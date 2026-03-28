---
layout: post
title: "Metering Chain: QA That Follows Business Logic"
tags: [Rust, Blockchain, DePIN, "Protocol Design", Web3, QA]
---

Phases 1-4 defined the guarantees Metering Chain is supposed to provide.
This article is about testing the failure modes that can quietly break those guarantees.

In DePIN, those failures are not abstract correctness issues. They change payout, delegated action, dispute cost, and operator trust.

A useful reference point is a product like Hivemapper: contributors submit road data, downstream systems turn it into reward-relevant outputs, and payout depends on how that contribution is interpreted, deduplicated, and preserved across product versions ([PANews coverage](https://www.panewslab.com/en/articles/5kc6zhxq)). In that kind of system, QA is not only about whether a code path runs. It is about making sure the same contribution is not counted twice, mislabeled, or reinterpreted after an upgrade.

That pattern is broader than Hivemapper. The same problem shows up in DePIN systems for wireless coverage, map data, and compute supply.

<figure class="post-figure" style="text-align:center;">
  <a href="/assets/2026-03-27-metering-chain-qa-business-logic/hero_image.png" target="_blank" rel="noopener noreferrer">
    <img src="/assets/2026-03-27-metering-chain-qa-business-logic/hero_image.png" alt="Same contribution, different payout story diagram contrasting wrong payout drift versus fail-closed deterministic payout handling" style="max-width:100%; height:auto;" />
  </a>
  <figcaption><em>Same contribution, different payout story: why fail-closed QA matters for payout correctness.</em> <strong>Source:</strong> ChatGPT.</figcaption>
</figure>

The diagram below uses a Hivemapper-style flow as the running example, but the same logic applies to any DePIN system where device output eventually becomes payout-relevant input.

<figure class="post-figure" style="text-align:center;">
  <a href="/assets/2026-03-27-metering-chain-qa-business-logic/depin-contribution-payout-risk-map.svg" target="_blank" rel="noopener noreferrer">
    <img src="/assets/2026-03-27-metering-chain-qa-business-logic/depin-contribution-payout-risk-map.svg" alt="DePIN contribution-to-payout flow diagram showing risk and guarantee checkpoints from contribution logs to settlement and version handoff" style="max-width:100%; height:auto;" />
  </a>
  <figcaption><em>Contribution-to-payout risk map: where DePIN systems fail, and which guarantees keep payout meaning stable.</em> <strong>Source:</strong> Author diagram based on current Metering Chain guarantee and fail-closed model.</figcaption>
</figure>

## 1) From Deterministic Billing to Production Confidence

Across the series, the questions changed, but the business problem stayed the same:
can multiple parties trust the same usage history enough to settle money against it?

The phase breakdown was:

- Phase 1: how usage is accounted.
- Phase 2: who is allowed to submit.
- Phase 3: who can act on behalf of whom.
- Phase 4: how accepted usage becomes settlement.

## 2) In DePIN, Valid Submission Is Only the Beginning

In a multi-operator DePIN system, valid authorization is necessary, but it is not enough to guarantee correct economics.

Even with valid signatures and valid delegation, you can still end up with:

- Replayed usage interpreted as new usage.
- Delegated actions accounted incorrectly.
- Accepted usage flowing into invalid settlement.
- Artifacts corrupted or misread across versions.

Those are expensive failures because they do not just change system state. They change who gets paid and why.

In practice, a contribution only becomes reward-relevant when authorship, deduplication, and downstream interpretation all line up. The risk is not just "bad data in." It is the same contribution being replayed, misclassified, or carried forward into a different payout story.

## 3) The Failures We Most Want to Prevent

### 3.1 Replayed or duplicated economic events

This is not about consensus-level double spend. It is about application-level duplication: the same usage, claim, or settlement being counted twice.

In a payout system, that is not a minor accounting bug. It directly changes who owes what and who gets paid.

### 3.2 Silent accounting drift

The worst outcome is often apparent success with the wrong meaning: balances, meter totals, fee splits, or reserve semantics drifting without an obvious failure.

That is especially dangerous in DePIN, where incentives depend on the assumption that the same usage history leads to the same payout logic.

### 3.3 Invalid settlement looking final

After Phase 4, this becomes critical. A wrong settlement window, wrong policy precedence, dispute that does not freeze payout, or invalid evidence path can all produce a result that looks final when it should not.

Once settlement appears final, the cost of correction goes up fast. Operators expect payout, disputes become harder to unwind, and trust is harder to recover.

### 3.4 Corrupted or incompatible artifact acceptance

Examples here include truncated `tx.log`, corrupted snapshot state, schema mismatch, replay protocol mismatch, or an inconsistent snapshot cursor.

A loud failure is inconvenient. A quiet reinterpretation is worse, because different parties can walk away with different payout narratives from the same history.

### 3.5 Version handoff changing meaning silently

The worst upgrade failure is not an explicit reject. It is an apparently successful handoff that changes the economic meaning of old artifacts.

In a multi-operator system, version handoff is not only an upgrade problem. It is a continuity-of-trust problem.

## 4) QA Should Follow Guarantees, Not Generic Test Buckets

QA gets clearer once guarantees are translated into contracts.

In this case, the contracts are safeguards around payout meaning: who may claim, what counts as a valid contribution, when settlement can be trusted, and how upgrades are stopped from quietly rewriting old history.

That is why I think it is better to start from guarantees than from generic test categories. In DePIN, the business contract comes first, so the test strategy should follow it.

From Phase 1:
- deterministic replay (`same log, same balances`).

From Phase 2:
- signer/owner binding and nonce anti-replay discipline.

From Phase 3:
- delegation proof validity, scope enforcement, revocation handling.

From Phase 4:
- settlement uniqueness, dispute/evidence constraints, payout freeze until resolution.

The usual test buckets still matter. They just come after this mapping, not before it.

### Guarantee -> Failure -> Test Mapping

Sources: [invariant_test_matrix.md](https://github.com/egpivo/metering-chain/blob/main/docs/invariant_test_matrix.md), [version_compatibility_matrix.md](https://github.com/egpivo/metering-chain/blob/main/docs/version_compatibility_matrix.md)
Each guarantee below protects a business expectation, not just a technical property.

| Guarantee | Failure to prevent | Test/contract surface |
|---|---|---|
| Authorization + delegation correctness | Wrong actor can submit/claim | `tests/security_abuse.rs`, `tests/cli_smoke.rs` |
| Replay/nonce discipline | Duplicate economic events counted twice | `tests/property_invariants.rs` |
| Deterministic accounting/replay | Same history yields different payout meaning | `tests/property_invariants.rs`, `tests/replay_recovery.rs` |
| Settlement/dispute semantics | Invalid settlement appears final | Recovery/compatibility + interface flow tests |
| Version/interface compatibility | Upgrades silently reinterpret artifacts | `tests/compatibility.rs`, interface contract tests |

## 5) What We Tested First

We started with the areas most likely to distort economic meaning:

- Invariant tests for deterministic/accounting behavior.
- Recovery tests for replay/restart correctness.
- Compatibility tests at schema/protocol/version boundaries.
- Interface tests for CLI/frontend contract surfaces.

That ordering was deliberate. The goal was not to maximize category coverage; it was to protect business meaning first.

By this point, the work had already moved beyond unit tests into recovery, compatibility, interface-contract, and product-facing smoke coverage.

Implemented test layers (current):

| Layer | Business risk protected | Representative coverage |
|---|---|---|
| Security / abuse | Forged or misbound actor actions | `security_abuse.rs`, `cli_smoke.rs` |
| Property / invariants | Drift in balances, meter totals, fee semantics | `property_invariants.rs` |
| Recovery + compatibility | Corrupted artifacts or version mismatch accepted | `replay_recovery.rs`, `compatibility.rs` |
| Interface contracts | CLI/frontend behavior silently diverges from engine guarantees | `frontend/src/pages/*.test.tsx`, adapters, `cli_smoke.rs` |
| Perf visibility | Regressions that erode operator confidence over time | `perf_smoke.rs`, adapter perf tests |

So the first wave of QA focused on payout correctness, replay trust, and operator-facing stability: stopping duplicate claims, preserving replay meaning, and making version boundaries visible before they turned into payout bugs.

The work also moved below the page layer. Snapshot adapters now have explicit contract tests for non-200 responses, malformed payloads, and anomaly mapping such as `disputed` and `replay_gap`.

## 6) Why Fail-Closed Matters in DePIN

In this kind of system, a loud reject is often safer than a quiet reinterpretation.

When failures affect payout, delegated action, and dispute handling, fail-closed behavior is not just a safety preference. It is part of the business safeguard.

Compatibility here is not best-effort parsing. It is explicit acceptance or explicit deterministic rejection.

> **Compatibility / Fail-Closed Policy (condensed)**  
> Source: [version_compatibility_matrix.md](https://github.com/egpivo/metering-chain/blob/main/docs/version_compatibility_matrix.md)  
> - No silent reinterpretation of persisted artifacts.  
> - Explicit accept or explicit deterministic reject (no "best-effort" parse).  
> - Schema/version mismatches must return stable machine-readable errors (for example: `UNSUPPORTED_SCHEMA_VERSION`, `REPLAY_PROTOCOL_MISMATCH`, `STATE_ERROR`).  
> - Interface contracts (CLI/frontend) are additive-only in v1; renames/removals/type/semantic changes are breaking.  
> - Version handoff is considered safe only when replay meaning is preserved, not just when parsing succeeds.

Concrete fail-closed examples from current tests:

| Failure case | Deterministic signal | Prevented outcome |
|---|---|---|
| Tampered signed payload | `SIGNATURE_VERIFICATION_FAILED` | Forged charge attempts rejected |
| Wrong signer/audience binding | `DELEGATION_AUDIENCE_SIGNER_MISMATCH` | Wrong actor blocked from acting on another party's behalf |
| Snapshot cursor > tx log tip | `STATE_ERROR` | Inconsistent replay basis for payout rejected |
| Stale nonce | `Invalid transaction: Nonce mismatch` | Duplicate/reordered economic action blocked |

Evidence:
- `security_abuse.rs` -> `test_security_abuse_tampered_signed_payload_rejected`
- `security_abuse.rs` -> `test_security_abuse_wrong_signer_audience_binding_rejected`
- `replay_recovery.rs` -> `test_recovery_mismatched_snapshot_cursor_vs_log_returns_state_error`
- `cli_smoke.rs` -> `test_cli_smoke_failure_stale_nonce_rejected`

Across all four cases, the contract is the same: explicit deterministic reject, stable operator-facing signal, and no silent payout drift.

Sample test code (trimmed) showing compatibility boundary behavior:
Legacy fixtures are still accepted within explicit compatibility boundaries; the critical guard is that unsupported schema versions must reject deterministically with stable error codes.

```rust
#[test]
fn test_compat_unsupported_schema_error_code_stable() {
    let mut bundle: EvidenceBundle = load_fixture_bundle_v1();
    bundle.schema_version = 999;
    let err = bundle.validate_shape().expect_err("must reject unsupported schema");
    assert!(matches!(err, Error::UnsupportedSchemaVersion));
    assert_eq!(err.error_code(), "UNSUPPORTED_SCHEMA_VERSION");
}
```

Recent product-facing frontend defects fixed in this cycle:

- `DisputesPage` detail-fetch failure path previously degraded into `No open disputes` plus unhandled rejection; now it resolves to deterministic `ErrorBanner` behavior.
- `SettlementDetailPage` evidence error-object path now degrades safely: no crash, no invalid "Evidence & Replay" rendering, while integrity status remains consistent.

One useful outcome of this cycle was that the `DisputesPage` tests found a real product bug rather than just adding coverage. A detail-fetch failure could collapse into a misleading `No open disputes` state plus an unhandled rejection. The fix turned that path into a deterministic error surface.

The same pattern showed up in `SettlementDetailPage`: not-found and evidence error-object cases now degrade deterministically instead of rendering a misleading "Evidence & Replay" success state.

In a dispute-heavy system, that is not cosmetic. It changes how operators interpret whether money is blocked, payable, or contested.

Frontend contract tests also assert deterministic UI degradation paths (for example, dispute detail fetch failure must surface a stable error banner instead of collapsing into misleading fallback state).

## 7) What Still Remains

Current high-value gaps:

- Broader adversarial coverage around evidence/dispute-resolution paths, because this is where payout trust is directly challenged.
- Fuller invariant closure, because business guarantees should not depend on partial coverage.
- Older-binary-produced artifacts (not hand-authored fixtures only), because real upgrades happen with old data, not fresh fixtures.
- Diagnostics treated as a tested contract, because operators need stable explanations, not only stable failures.

On performance, we finished a first-pass variance review and kept CI perf checks as warning-only for now. Hard-gate promotion can come later, after broader cross-day and cross-machine sampling.

Performance coverage also expanded beyond the backend. Frontend snapshot mode now has reporting-only visibility into first-load, cached-load, and adapter-path cost, even though it is not yet a release gate.

### Perf baseline snapshot (first pass)

Source: [benchmark_baseline.md](https://github.com/egpivo/metering-chain/blob/main/docs/benchmark_baseline.md)

| Dataset | Replay ms (median) | Recompute ms (median) | Gate mode |
|---|---:|---:|---|
| Small | 0 | 1 | Warning-only |
| Medium | 2 | 5 | Warning-only |
| Large | 5 | 12 | Warning-only (hard-gate candidate later) |

<figure class="post-figure" style="text-align:center;">
  <a href="/assets/2026-03-27-metering-chain-qa-business-logic/perf_latency.svg" target="_blank" rel="noopener noreferrer">
    <img src="/assets/2026-03-27-metering-chain-qa-business-logic/perf_latency.svg" alt="Perf latency medians chart comparing replay and recompute across small, medium, and large datasets" style="max-width:100%; height:auto;" />
  </a>
  <figcaption><em>Replay and recompute latency medians from the first-pass variance review.</em> <strong>Source:</strong> <a href="https://github.com/egpivo/metering-chain/blob/main/docs/benchmark_baseline.md">benchmark_baseline.md</a>.</figcaption>
</figure>

## 8) Closing

Seen this way, systems like Hivemapper sit at the application layer of DePIN metering: they decide how contribution, deduplication, and payout logic show up for users and operators. Metering Chain sits one layer below, making replay, authorization, settlement, and compatibility guarantees explicit enough to test.

In a multi-operator DePIN system, QA is not mainly about test count. It is about stopping the system from quietly changing who can act, what usage means, how settlement resolves, and ultimately who gets paid.

That is why Metering Chain treats replay safety, fail-closed compatibility, and interface contracts as business guarantees rather than just engineering hygiene. The goal is not to collect test categories. It is to turn those guarantees into invariant checks, reject paths, recovery behavior, and interface contracts.

## References

- Metering Chain source repository: [github.com/egpivo/metering-chain](https://github.com/egpivo/metering-chain)
- [Phase 1 (Deterministic Billing)]({{ site.baseurl }}/2026/01/24/metering-chain-deterministic-billing.html)
- [Phase 2 (Deterministic Auth)]({{ site.baseurl }}/2026/02/02/metering-chain-phase2-deterministic-auth.html)
- [Phase 3 (Delegation)]({{ site.baseurl }}/2026/02/07/metering-chain-phase3-delegation.html)
- [Phase 4 (Settlement Finality)]({{ site.baseurl }}/2026/02/21/metering-chain-phase4-settlement-finality.html)
- QA matrices: [invariant_test_matrix.md](https://github.com/egpivo/metering-chain/blob/main/docs/invariant_test_matrix.md), [version_compatibility_matrix.md](https://github.com/egpivo/metering-chain/blob/main/docs/version_compatibility_matrix.md)
- Perf baseline: [benchmark_baseline.md](https://github.com/egpivo/metering-chain/blob/main/docs/benchmark_baseline.md)
- Hivemapper context: [PANews coverage](https://www.panewslab.com/en/articles/5kc6zhxq)
