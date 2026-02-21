---
layout: post
title: "Metering Chain Phase 4: Settlement and Economic Finality"
tags: [Rust, Blockchain, DePIN]
---

[Phase 1](/2026/01/24/metering-chain-deterministic-billing.html) was about accounting. [Phase 2](/2026/02/02/metering-chain-phase2-deterministic-auth.html) locked down authorization. [Phase 3](/2026/02/07/metering-chain-phase3-delegation.html) added delegation.  
Phase 4 is where money movement finally stops being "we think this is right" and becomes a process we can replay and defend.

<div style="text-align:center; margin: 2rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-02-21-metering-chain-phase4-settlement-finality/ezekiel-see-GnBjJyh0cz4-unsplash.jpg"
       alt="Digital multimeter: metering starts with measurement"
       style="max-width:90%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    Metering starts with measurement, but Phase 4 is about proving payout decisions with replayable evidence.
  </div>
  <div style="color: var(--text-secondary); font-size: 0.8em; margin-top: .15rem;">
    Photo by <a href="https://unsplash.com/@ezekiel_see?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Ezekiel See</a> on <a href="https://unsplash.com/photos/a-person-holding-a-multimeter-in-their-hand-GnBjJyh0cz4?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Unsplash</a>
  </div>
</div>

---

## Where Phase 4 hurts (in a good way)

The earlier phases answer "can we accept this usage?"  
The uncomfortable question is: "when payout is challenged three weeks later, can we still explain exactly why this number is correct?"

That is what this phase adds:

- settlement records that bound payout strictly (no over-claim / no double-pay)  
- disputes that can actually pause payout  
- a replay/evidence gate before a dispute resolution is accepted

---

## What actually changed in the state machine

We added four tx kinds in the same append-only log: `ProposeSettlement`, `FinalizeSettlement`, `SubmitClaim`, `PayClaim`, plus dispute txs `OpenDispute` and `ResolveDispute`.

At the model level, a settlement now carries explicit economics:

- `gross_spent`  
- `operator_share`  
- `protocol_fee`  
- `reserve_locked`

And we enforce the boring-but-critical checks:

- one settlement per `(owner, service_id, window_id)`  
- `gross_spent = operator_share + protocol_fee + reserve_locked`  
- claim/payment cannot exceed finalized payable amount

The practical behavior is simple: once `OpenDispute` succeeds, payout for that settlement is frozen until resolution.

`ResolveDispute` is not just a yes/no verdict. It passes through `apply_with_replay_verifier`, which checks that the submitted evidence bundle and replay output still match the settlement window before state is mutated.

## Why hook-first (design decision)

I originally considered a deeper refactor before Phase 4, but the safer path for this repo was **hook-first extension**:

- keep the existing apply pipeline stable
- add settlement/dispute as new tx kinds
- intercept at explicit extension points (policy resolve, replay verify, payout gate)
- avoid deep wrapper chains and avoid touching proven Phase 1-3 behavior

This fits the current codebase better because domain boundaries are already clear (auth, metering, state transition invariants). So instead of rewriting the core execution path, we attach new domain checks at known points and keep replay behavior unchanged.

### Execution gates (how I shipped this without breaking Phase 1-3)

- `G0 Refactor Ready` - done: interface split, validation cleanup, evidence/replay service extraction, regression baseline.
- `G1 Settlement Ready` - done: propose/finalize + claim/pay invariants.
- `G2 Dispute Ready` - done: dispute open/freeze + resolve path.
- `G3 Policy Ready` - done: versioned policy + effective-time resolution + bound policy snapshot.
- `G4 Evidence Finality` - harden: stricter verifier + better evidence ergonomics.

### Why hook over heavy refactor

- lower regression risk: fewer cross-cut changes in hot paths  
- easier audit diff: new logic appears as additive guards  
- better rollback surface: hook points can be disabled or narrowed without undoing architecture-wide edits

In short: Phase 4 is delivered as a domain capability layered on top of stable execution primitives, not a rewrite project.

## Three implementation frictions we had to pin down

### 1) Policy precedence is easy on slides, annoying in code

Resolution order is:

1. exact `OwnerService`
2. fallback `Owner`
3. fallback `Global`

Inside the same scope we choose the latest policy with `effective_from_tx_id <= propose_tx_id`.  
If two policy records collide on same scope + same `effective_from_tx_id`, we reject at write time (instead of silently picking one), because replay tie-breakers are where audits go to die.

Also important: the resolved policy is snapshotted onto the settlement at propose time. Finalize/dispute checks use that snapshot, not current config.

### 2) Settlement windows needed canonicalization rules

Window boundaries are computed in UTC with half-open intervals `[start, end)`, where:

- `start = floor(event_ts / window_size) * window_size`
- `end = start + window_size`

If an event timestamp is missing, we fallback to ingest timestamp and mark the row as derived-time in audit output.  
We also keep a small drift tolerance (currently 90s) when ingest time and event time disagree; outside the tolerance, the event is assigned strictly by canonical `event_ts`.

On rounding: we never sum floats. Unit price is converted to minor units first, each row cost is integer-rounded once, then window totals are integer sums. We hit a 1-cent replay mismatch once. That was enough to ban floats from totals permanently.

### 3) `evidence_hash` had to be versioned from day one

In `ev1`, hash input is canonical JSON (sorted keys, stable field order) over:

- settlement identity (`owner`, `service_id`, `window_id`)
- tx slice (`from_tx_id`, `to_tx_id`)
- normalized totals
- policy snapshot hash
- replay summary

Then we hash bytes with BLAKE3 and store as `ev1:<hex>`.

Why the prefix matters: future formats (for example Merkleized evidence sets) can be added as `ev2:*` without breaking old disputes. The verifier first checks prefix, then runs the matching preimage builder.

---

## The end-to-end arc now

`authorized usage -> accounted usage -> settlement window -> payout attempt -> dispute (optional) -> replay-gated resolution`

That is the first version where the system can explain not only why a tx was accepted, but also why money did or did not move.

---

## Two architecture diagrams (system + decision flow)

**System context** (where everything lives) and **settlement decision flow** (propose → finalize or blocked).

<div style="text-align:center; margin: 2rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-02-21-metering-chain-phase4-settlement-finality/metering_chain_architecture.png"
       alt="Metering Chain system context: data and UI/CLI → Metering; Policy Snapshot bound at ProposeSettlement; Settlement and Dispute domains; Replay Guard; Payout/Claim Execution; Audit Output"
       style="max-width:100%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    System context: data and UI/CLI → Metering; Hook builds settlement windows; Policy Snapshot bound at ProposeSettlement; Replay Guard gates finality; Audit Output exposes evidence_hash, replay_hash, replay_summary, error_code.
  </div>
</div>

**Settlement decision flow**

<div style="text-align:center; margin: 2rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-02-21-metering-chain-phase4-settlement-finality/settlement_decision_flow.png"
       alt="Settlement decision flow: ProposeSettlement → Bind Policy → claim/pay → Evidence/Replay Check → Finalized/Payout or Blocked; OpenDispute → frozen; deterministic error codes"
       style="max-width:100%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    Happy path: ProposeSettlement → Bind Policy → claim/pay → Evidence/Replay Check → Finalized + Payout. Dispute path: OpenDispute ⇒ payout frozen; ResolveDispute can Block. Deterministic error codes: EVIDENCE_NOT_FOUND, REPLAY_MISMATCH, DISPUTE_OPEN_PAYOUT_BLOCKED, POLICY_NOT_EFFECTIVE.
  </div>
</div>

---

## Examples (UI)

The [demo site](https://egpivo.github.io/metering-chain) runs the same flow. These screenshots show the full closing loop: data is metered, transformed into settlement windows, and then constrained by replay/evidence gates before finality.

**1. Overview (Start Here)**

<div style="text-align:center; margin: 1.5rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-02-21-metering-chain-phase4-settlement-finality/01_overview_start_here.png"
       alt="Metering Chain Overview: Start Here defines product flow Metering → Settlement → Dispute/Finality with snapshot data source"
       style="max-width:100%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    Start Here defines the product flow in one screen: Metering → Settlement → Dispute/Finality, with transparent snapshot data source and generation metadata.
  </div>
</div>

**2. Metering main view**

<div style="text-align:center; margin: 1.5rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-02-21-metering-chain-phase4-settlement-finality/02_metering_counters_timeline.png"
       alt="Metering page: date-scoped counters, anomaly rail, usage timeline, top operators, settlement-window preview"
       style="max-width:100%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    The Metering page turns raw transfer snapshots into operational context: date-scoped counters, anomaly rail, usage timeline, top operators, and settlement-window preview.
  </div>
</div>

**3. Top operators**

<div style="text-align:center; margin: 1.5rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-02-21-metering-chain-phase4-settlement-finality/03_metering_top_operators.png"
       alt="Top Operators: owner-service pairs ranked by metered cost"
       style="max-width:100%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    Top Operators ranks owner-service pairs by metered cost, showing where usage concentration comes from before settlement decisions.
  </div>
</div>

**4. Window preview**

<div style="text-align:center; margin: 1.5rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-02-21-metering-chain-phase4-settlement-finality/04_metering_window_preview.png"
       alt="Window Preview: windows produced by filters, handoff to Settlements"
       style="max-width:100%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    Window Preview shows the exact windows produced by current filters and provides a direct handoff to Settlements, connecting metering output to settlement input.
  </div>
</div>

**5. Settlements list**

<div style="text-align:center; margin: 1.5rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-02-21-metering-chain-phase4-settlement-finality/05_settlements_list.png"
       alt="Settlements: window-level economics and lifecycle states"
       style="max-width:100%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    Settlements displays window-level economics and lifecycle states (Proposed / Finalized / Disputed), not just analytics aggregates.
  </div>
</div>

**6. Settlement detail**

<div style="text-align:center; margin: 1.5rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-02-21-metering-chain-phase4-settlement-finality/06_dispute_or_detail_execution_gate.png"
       alt="Settlement detail: lifecycle, economics, integrity fields for auditable finality"
       style="max-width:100%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    Settlement detail exposes lifecycle status, economics, and integrity fields (evidence hash, replay hash, tx range) needed for auditable finality decisions.
  </div>
</div>

**7. Explorer with evidence gate**

<div style="text-align:center; margin: 1.5rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-02-21-metering-chain-phase4-settlement-finality/07_explorer_blocked_missing_or_mismatch.png"
       alt="Flow explorer: Recorded vs Replay comparison gates execution; MISMATCH blocks resolve"
       style="max-width:100%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    In the flow explorer, Recorded vs Replay comparison drives execution gating: MISMATCH blocks resolve/payout and surfaces explicit failure behavior.
  </div>
</div>

**8. Audit output and rule summary**

<div style="text-align:center; margin: 1.5rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-02-21-metering-chain-phase4-settlement-finality/08_audit_output_rule_summary.png"
       alt="Audit output and rule summary: policy snapshot, recorded vs replay, rule that blocks resolve when totals mismatch"
       style="max-width:100%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    Audit output and rule summary: policy snapshot, recorded vs replay, and the rule that blocks resolve when totals do not match (example shown: mismatch).
  </div>
</div>

---

## Examples (CLI: propose → finalize → claim → pay)

Like [Phase 2](/2026/02/02/metering-chain-phase2-deterministic-auth.html) and [Phase 3](/2026/02/07/metering-chain-phase3-delegation.html), Phase 4 is runnable from the repo. From the [metering-chain](https://github.com/egpivo/metering-chain) README:

```bash
# From repo root
cargo run --example settlement_demo
```

The example runs Mint → OpenMeter → Consume, then ProposeSettlement → FinalizeSettlement → SubmitClaim → PayClaim (in-memory; for persistent state use the binary with `init` and `apply`). For disputes, policy, and evidence-backed resolve use the CLI settlement/dispute/policy flows or the frontend. Same sequence replayed from `tx.log` yields the same state; over-claim or double-settlement attempts get explicit error codes (e.g. `CLAIM_AMOUNT_EXCEEDS_PAYABLE`, `DUPLICATE_SETTLEMENT_WINDOW`).

**CLI run**

<div style="text-align:center; margin: 1.5rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-02-21-metering-chain-phase4-settlement-finality/cli_demo.png"
       alt="Terminal run of settlement demo: propose → finalize → claim → pay"
       style="max-width:100%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    Terminal output of <code>cargo run --example settlement_demo</code>: Mint → OpenMeter → Consume → Propose → Finalize → SubmitClaim → PayClaim.
  </div>
</div>

---

## What “finality” means here (and what it does not)

**In v1:**

- Replaying the same tx log yields identical settlement and dispute outcomes.  
- Payout safety is enforced by domain invariants.  
- Every reject maps to an explicit error code.  
- Evidence artifacts are queryable for audit.

**Not in scope for v1:**

- No multi-node consensus protocol.  
- No oracle truth for physical-world events.  
- No full on-chain settlement execution engine.

Phase 4 finality is **single-node replayable finality**, aligned with the current architecture.

---

## Why this matters for real systems

In DePIN, API billing, or compute marketplaces, trust often breaks at payout boundaries. The technical win of Phase 4 is not a new screen or command; it is making payout decisions **reproducible**, **challengeable**, and **explainable from evidence**. The point is: three weeks later, we can replay the same tx slice and get the same number - or refuse to pay with a deterministic reason.

---

## Summary

| Phase | Question answered |
|-------|-------------------|
| [1](/2026/01/24/metering-chain-deterministic-billing.html) | How is usage accounted? |
| [2](/2026/02/02/metering-chain-phase2-deterministic-auth.html) | Who can submit transactions? |
| [3](/2026/02/07/metering-chain-phase3-delegation.html) | Who can act on behalf of another? |
| [4](/2026/02/21/metering-chain-phase4-settlement-finality.html) | How does accepted usage become **settled, disputable, and final**? |

Phase 4 is where Metering Chain stops being only a transaction validator and becomes a replayable **economic system**: same log, same settlement and dispute results, and evidence-backed resolution.

Repo: [egpivo/metering-chain](https://github.com/egpivo/metering-chain). CLI: `cargo run --example settlement_demo`. Demo site: [egpivo.github.io/metering-chain](https://egpivo.github.io/metering-chain) — Overview → Metering → Settlements → Disputes (optional: `/demo/phase4` advanced explorer).

---

## Quick term notes

- **Settlement window**: billing interval keyed by `(owner, service_id, window_id)`.  
- **Bound policy**: policy snapshot attached at propose time; later checks do not read latest config.  
- **Replay summary**: deterministic replay output for a tx slice (`from_tx_id`, `to_tx_id`, totals).  
- **`apply_with_replay_verifier`**: required entry point for `ResolveDispute`; blocks apply on evidence/replay mismatch.  
