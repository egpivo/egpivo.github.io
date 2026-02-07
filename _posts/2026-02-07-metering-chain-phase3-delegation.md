---
layout: post
title: "Metering Chain Phase 3: Capability-Driven Delegation"
tags: [Rust, Blockchain, DePIN, UCAN]
---

In DePIN, owners can't sign every event, and letting operators submit usage without proof opens a trust hole. Phase 3 adds delegation: the owner issues a signed capability proof; the delegate signs `Consume` and attaches it. Same usage, different outcome depending on authorization — no proof gets rejected, valid proof gets accepted, revoked proof gets rejected.

---

[Phase 1](/2026/01/24/metering-chain-deterministic-billing.html) proved deterministic accounting. [Phase 2](/2026/02/02/metering-chain-phase2-deterministic-auth.html) proved deterministic authorization. Phase 3 adds **delegation**: a delegate can submit `Consume` for an owner without using the owner's private key.

Core shift:

> Usage does not change; who is allowed to speak does.

---

## Why Phase 3 exists

<div style="text-align:center; margin: 2rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-02-07-metering-chain-phase3/analogy.png"
       alt="Access control reader with access card"
       style="max-width:90%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    Delegation analogy: owner-issued access card grants scoped access; revoked card is denied.
  </div>
  <div style="color: var(--text-secondary); font-size: 0.8em; margin-top: .15rem;">
    Image: <a href="https://www.pexels.com/zh-tw/photo/13657444/" rel="noopener">Pexels (free to use)</a>
  </div>
</div>

In real usage systems (DeWi, API billing, AI/compute), the owner cannot sign every event. But letting operators submit usage creates a trust problem:

- Who is authorized to charge?
- What service is in scope?
- How much can be charged?
- Can anyone audit and replay the result?

Phase 3 turns these into verifiable constraints in signed transaction input. Below, the flow: owner issues proof, delegate submits Consume(v2) with proof, validator applies and appends to tx.log.

<div style="text-align:center; margin: 2rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-02-07-metering-chain-phase3/delegated_consume_sequence.png"
       alt="Phase 3 delegation sequence: Owner → Delegate → Validator → State → tx.log"
       style="max-width:90%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    Delegation flow. <a href="{{ site.baseurl }}/assets/2026-02-07-metering-chain-phase3/delegated_consume_sequence.png" target="_blank" rel="noopener">Open full-size</a>
  </div>
</div>

---

## What changed in Phase 3

Delegated consume requires `payload_version=2` and owner-signed proof; no proof, no apply. Details:

- **Owner-nonce**: delegate consumes owner's nonce (`nonce_account=owner`), not their own.
- **Revocation**: `RevokeDelegation` adds `capability_id` to revoked set; reusing a revoked proof fails.
- **Proof format**: owner-signed canonical `bincode` (not JWT); issuer and audience bind to owner and signer.
- **Principal format**: `0x` hex or `did:key` (Ed25519).
- **Scope match**: must match the transaction's `service_id` (and optional `ability`).
- **Capability identity**: `capability_id = hash(proof_bytes)`, deterministic.
- **Caveat**: optional bounds like `max_units` or `max_cost` to limit delegated spend.
- **Replay time model**: `ValidationContext(Live/Replay)` — Live uses wall clock, Replay uses tx reference time, which keeps determinism.

<div style="text-align:center; margin: 1.5rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-02-07-metering-chain-phase3/validation_decision_tree.png"
       alt="Delegated Consume validation: owner path vs delegation path, accept/reject"
       style="max-width:90%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    Validation flowchart: owner path vs delegation path. <a href="{{ site.baseurl }}/assets/2026-02-07-metering-chain-phase3/validation_decision_tree.png" target="_blank" rel="noopener">Open full-size</a>
  </div>
</div>

---

## Demo: who can act on behalf of another?

Phase 3 answers one question: who can act on behalf of someone else? The demo runs four scenes. In Scenes 1–2, a delegate signs Consume without a proof — rejected. In Scene 3 the owner issues a delegation proof and the same Consume goes through. In Scene 4 we revoke the capability; sending Consume again with the same proof returns `Delegation revoked`. Same usage, same amount, different authorization outcome.

<div style="text-align:center; margin: 1.5rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-02-07-metering-chain-phase3/live_vs_replay.png"
       alt="Live vs Replay: ValidationContext time model"
       style="max-width:90%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    Live vs Replay time semantics.
  </div>
</div>

### Try it

```bash
# Run from egpivo/metering-chain repo root
./examples/phase3_demo/run_phase3_demo.sh
```

Repo: [egpivo/metering-chain](https://github.com/egpivo/metering-chain). The script initializes a temporary data dir, creates three wallets (authority, owner, delegate), runs Mint and OpenMeter, then runs the four scenes above. Output lines like "Expected: rejected." or "Expected: accepted." indicate the expected outcome. Manual steps: [examples/phase3_demo/README.md](https://github.com/egpivo/metering-chain/blob/main/examples/phase3_demo/README.md).

### Demo outcomes (one run)

| Scene | Action | Expected | Result |
|-------|--------|----------|--------|
| 1–2 | Delegate signs Consume (no proof) | Reject | `Delegated Consume requires payload_version=2` |
| 3 | Owner issues proof → delegate signs same Consume | Accept | Transaction applied, Cost: 20 |
| 4 | Owner revokes → delegate retries with same proof | Reject | `Delegation revoked` |

Scene 3 success: after the delegate signs with a valid proof, the state shows the owner's updated balance and meter:

```
--- Scene 3: Owner issues proof, delegate signs (expected accept) ---
Created signed delegation proof: 254 bytes
Transaction applied successfully  Cost: 20
Expected: accepted.
AccountOutput { address: "0xc89176c9...", balance: 880, nonce: 2 }
MetersOutput { service_id: "storage", total_units: 10, total_spent: 20, active: true, locked_deposit: 100 }
```

[Full log]({{ site.baseurl }}/assets/2026-02-07-metering-chain-phase3/demo_log.txt)

### Phase 3 on real data

We ran the delegation demo on real Helium IOT transfers from Dune. Fetch, convert to Consume NDJSON, create one owner and N delegate wallets with N proofs, then run the four scenes. Without proof the batch is rejected; with proof it's accepted. Revoke one capability and re-apply: `Delegation revoked`. Replay the applied log in a fresh state and the owner report matches. Run from [egpivo/metering-chain](https://github.com/egpivo/metering-chain) repo root. Scripts live in [examples/phase3_dune_demo/](https://github.com/egpivo/metering-chain/tree/main/examples/phase3_dune_demo); [result_summary_template.md](https://github.com/egpivo/metering-chain/blob/main/examples/phase3_dune_demo/result_summary_template.md) for recording a run; [run_fetch_and_viz.sh](https://github.com/egpivo/metering-chain/blob/main/examples/phase3_dune_demo/run_fetch_and_viz.sh) spits out `helium_real_analysis.png`.

<div style="text-align:center; margin: 1.5rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-02-07-metering-chain-phase3/helium_real_analysis.png"
       alt="Helium IOT analysis: transfers, units, top-10 concentration, distribution"
       style="max-width:90%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    Four panels: transfers over time, units by operator, top-10 share (65.4%), distribution. One run: 200 consume lines, 68 delegates, 2.2T units.
  </div>
</div>

---

## Guarantees and boundaries

For accepted claims you get authorization validity (signature plus delegation proof), one-time semantics (nonce, anti-replay), deterministic replay (same log, same state), and auditability. What we don't do: Metering Chain doesn't prove physical-world truth. It won't tell you whether a hotspot actually forwarded traffic or a GPU actually did work. It validates accounting truth over accepted claims, not oracle truth. Key distribution and network/transport layer stay out of scope for Phase 3 v1.

---

## Why this matters beyond one app

This isn't Helium-only logic. Same authorization and accounting flow works for DeWi traffic metering, GPU inference billing, API usage charging, agent budget enforcement. Units and service names change; the rest stays.

<div style="text-align:center; margin: 1.5rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-02-07-metering-chain-phase3/lifecycle.gif"
       alt="Capability lifecycle: Issued → Active → Accumulating / Revoked / Expired"
       style="max-width:90%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    Capability lifecycle.
  </div>
</div>

---

## Summary

| Phase | Question answered |
|-------|-------------------|
| [1](/2026/01/24/metering-chain-deterministic-billing.html) | How is usage accounted? |
| [2](/2026/02/02/metering-chain-phase2-deterministic-auth.html) | Who can submit transactions? |
| 3 | Who can **act on behalf of another**? |

Phase 3 v1 ships as a deterministic delegation layer: UCAN-style capability verification in a protocol-grade state machine. We scoped it intentionally: validation and replay first, oracle and attestation later. Trust in actors gets replaced by verifiable constraints on actions.

Repo: [egpivo/metering-chain](https://github.com/egpivo/metering-chain). Run demos from repo root: [examples/phase3_demo/](https://github.com/egpivo/metering-chain/tree/main/examples/phase3_demo) (toy), [examples/phase3_dune_demo/](https://github.com/egpivo/metering-chain/tree/main/examples/phase3_dune_demo) (real Helium IOT).

---

## Terms

| Term | Meaning |
|------|---------|
| `payload_version` | v1 = legacy (no delegation); v2 = required for delegated Consume (proof, nonce_account, valid_at). |
| `nonce_account` | Which account’s nonce is consumed; for delegated Consume, must equal owner. |
| `capability_id` | Deterministic hash of proof bytes; used for revocation and caveat tracking. |
| `valid_at` | Reference time in the signed tx; used for expiry checks (Live: wall clock, Replay: this value). |
| `caveat` | Optional bound on a capability, e.g. `max_units` or `max_cost`, to limit delegated spend. |
