---
layout: post
title: "Metering Chain Phase 2: Deterministic Authorization for Multi-Operator DePIN"
tags: [Rust, Blockchain, DePIN]
---

In [the first post](/2026/01/24/metering-chain-deterministic-billing.html), Metering Chain showed that usage can be replayed into deterministic balances: same history, same bill. That part worked. What kept nagging me was the more dangerous question:

> **Who is allowed to submit usage?**

Without signatures, anyone can impersonate a user or operator. Phase 2 adds cryptographic authorization so the system stays deterministic and becomes permissioned.

The easiest way to think about Phase 2 is as an access-control gate. Operators don't "submit usage" just because they can. They present a signed message, and only messages that pass verification are admitted into the log. The append-only property holds because invalid entries never enter the state machine in the first place.

<div style="text-align:center; margin: 2rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-02-02-metering-chain-phase2/signer.png"
       alt="Signature verification: valid data passes, invalid data rejected (X)"
       style="max-width:90%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    Signature verified: only valid inputs (✓) proceed; invalid or unsigned data (✗) is rejected.
  </div>
</div>

Phase 1 proved reproducibility: feed transactions, replay, same balances. But it didn't solve who can create those transactions. An unsigned `Consume` could be fabricated. An unsigned `Mint` could inflate supply. In a multi-operator DePIN (many hotspots, many reward events), you need to know that usage comes from the right actor.

Phase 2 makes every transaction signed and verified before it hits domain logic.

- **Domain layer**: invariants only — signer must match owner (or minter for `Mint`), nonces must increment.
- **Infrastructure layer**: wallet creation, signing, verification.

Changes under the hood, in plain terms:

- `SignedTx` now carries an [Ed25519](https://en.wikipedia.org/wiki/EdDSA#Ed225519) signature over a canonical payload.
- `apply` verifies signatures before it validates domain rules.
- Unsigned tx are rejected by default; legacy replay can use a flag `--allow-unsigned` if you really need it.

Flow: `wallet create` → build kind-only JSON → `wallet sign --address <signer> --file kind.json` → pipe to `apply`. Signing uses the current nonce from state, so tx must be applied in order.

<div style="text-align:center; margin: 1.5rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-02-02-metering-chain-phase2/phase2.gif"
       alt="Phase 2 architecture: CLI, wallet/signer, verify signature, validate, apply, tx.log"
       style="max-width:90%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    Phase 2 architecture: wallet signs tx (Ed25519) → verify → validate → apply → append-only tx.log.
  </div>
</div>

<div style="text-align:center; margin: 1.5rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-02-02-metering-chain-phase2/signer_flow.png"
       alt="Metering Chain interaction flow: Init, wallets, Mint, OpenMeter, Consume loop, Report"
       style="max-width:90%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    Signed flow: Init → Auth & User wallets → Mint (AUTH) → OpenMeter (USER) → Consume loop (USER signs each line from <code>consume.ndjson</code>) → Report. Full script: <a href="https://github.com/egpivo/metering-chain/blob/main/examples/signed/run_signed_demo.sh">run_signed_demo.sh</a>.
  </div>
</div>

### Wallet / signer

Signing builds the canonical message and attaches an Ed25519 signature; verification runs before apply. I kept the domain rules boring and strict, and pushed the “who signed this” decision to the boundary.

```rust
// sign_transaction (wallet.rs)
pub fn sign_transaction(&self, nonce: u64, kind: Transaction) -> Result<SignedTx> {
    let tx = SignedTx::new(self.address.clone(), nonce, kind);
    let message = tx.message_to_sign()?;
    let signature = self.sign_bytes(&message);
    Ok(SignedTx { signature: Some(signature), ..tx })
}
```

Note: code snippet from [src/wallet.rs](https://github.com/egpivo/metering-chain/blob/main/src/wallet.rs)


### Data format & replay

Deterministic replay depends on byte-level stability, so the details are a bit pedantic here. Address = `0x` + hex(32-byte Ed25519 pubkey). Canonical signing payload = bincode of `SignablePayload { signer, nonce, kind }` (no signature included in the bytes being signed). `tx.log` continues to be bincode; replay verifies signatures when present and accepts the legacy layout (no sig) for backward compatibility.

```rust
// message_to_sign (tx/transaction.rs)
pub fn message_to_sign(&self) -> Result<Vec<u8>> {
    let payload = SignablePayload { signer, nonce, kind };
    bincode::serialize(&payload)
}
```

Note: code snippet from [src/tx/transaction.rs](https://github.com/egpivo/metering-chain/blob/main/src/tx/transaction.rs)

---

## Helium IOT: 17k rows, 1.5k operators

DePIN is inherently multi-operator, so I wanted a dataset that is public, messy, and real. Helium IOT transfers fit that well. We pull from [Dune Analytics](https://dune.com) `tokens_solana.transfers`, Helium IOT mint `iotEVVZLEywoTn1QdwNPddxPWszn3zFhEot3MfL9fns`, treat each `to_owner` as an operator (hotspot), aggregate by operator, and map into `Consume`.

**Data source:** Dune Analytics, `tokens_solana.transfers`, Helium IOT token. **Window:** 2026-01-01 → 2026-01-31.

| Metric | Value |
|--------|-------|
| Rows | 17,820 |
| Distinct operators | 1,561 |
| Total units | 659,978,351,356,954 |

Pipeline (4 steps):
1. Fetch Helium IOT transfers from Dune → `helium_rewards.csv`
2. Analyze with `analyze_rewards.py` → charts + `helium_jan_summary.json`
3. Convert CSV to Consume NDJSON with `helium_rewards_to_consume.py` → `consume.ndjson`
4. Signed apply — init, Mint, OpenMeter, then sign-and-apply each line

Full scripts live in [examples/multi_operator](https://github.com/egpivo/metering-chain/tree/main/examples/multi_operator).

---

## When top 10 hold 70%

The Helium Jan dataset is highly concentrated. A small set of operators has outsized influence:

| Metric | Value |
|--------|-------|
| Top-10 share | 70.6% |
| HHI | 0.116 |
| Gini | 0.958 |

This isn't just a pretty plot. If the top 10 operators control most rewards, authorization isn't optional:  it's the only way to keep the ledger honest.

<div style="text-align:center; margin: 1.5rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-02-02-metering-chain-phase2/helium_jan_analysis.png"
       alt="Helium Jan 2026 IOT transfer analysis: concentration and distribution"
       style="max-width:90%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    Helium IOT analysis: Lorenz curve (Gini), concentration metrics (HHI, Top-10 share). Full Jan dataset: 17,820 rows, 1,561 operators.
  </div>
</div>

The Lorenz curve (blue) is cumulative operators vs. cumulative units earned; the diagonal would be perfect equality. Gini, HHI, and Top-10 share are different angles on the same skew. That’s why Phase 2 focuses on who signs, not just how much.

---

## One run, one report

I ran the demo with real Helium IOT data (500 rows from Dune, 92 distinct operators aggregated) and captured the output below. Same pipeline as above: fetch → convert → signed apply. The reassuring part: replaying the same signed `tx.log` reproduces the exact numbers.

<div style="text-align:center; margin: 1.5rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-02-02-metering-chain-phase2/demo_result.png"
       alt="Phase 2 demo: report, account, meters output from real Helium data run"
       style="max-width:90%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    Real run: 500 Helium IOT transfers, 92 operators, 24.3T units consumed. One account, one meter, one report — anyone who replays the same signed <code>tx.log</code> gets the same numbers.
  </div>
</div>

**Numbers from this run:**
- **Account:** balance 5,659,623,953,113, nonce 93
- **Report:** `helium-rewards` meter, 24,340,376,045,887 units consumed, unit price 1.0
- **Meters:** one active meter, deposit 1,000 locked

---

## Auditability, non-repudiation, delegation

Same inputs → same outputs; replay the log, same balances. Only the right actor can produce valid inputs: `Consume` signed by the meter owner, `Mint` by the authorized minter. No signature, no apply. That gives you auditability (who did what, verifiable from signatures), non-repudiation (the signer can’t deny it), and a path to delegation (Phase 3: UCAN/ReCaps so operators can act on behalf of accounts without sharing keys).

## Delegation (Phase 3, out of scope)

Phase 2 deliberately stops at authorization. Delegation is the next layer:

- **UCAN / ReCaps**: scoped operator rights — “this hotspot can Consume on behalf of account X for service Y” without handing over the root key.
- **Device attestation**: TPM/WebAuthn for hardware-backed operator identity.
- **Optional MetaMask / EIP-712**: familiar wallet UX for account owners.

The repo lives at [`egpivo/metering-chain`](https://github.com/egpivo/metering-chain). Phase 1 demo: `examples/depin/`. Phase 2 signed demo: `examples/signed/` and `examples/multi_operator/`.
