---
layout: post
title: "Can a Solana Transaction Prove the Router?"
date: 2026-08-18
tags: [Solana, Rust, Blockchain, DeFi, Web3]
image: /assets/2026-08-18-the-interface-says-dflow-can-the-transaction-prove-it/hero.png
---

*[Part I]({{ site.baseurl }}/2026/08/16/different-apps-same-router.html) — **DFlow Shows Where Solana Trading Is Going. Retail Pricing Still Happens at the App.** — measures the retail price effect. This article opens one unsigned transaction and follows its program and account lineage with Rust.*

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-08-18-the-interface-says-dflow-can-the-transaction-prove-it/hero.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-08-18-the-interface-says-dflow-can-the-transaction-prove-it/hero.png"
         alt="JTX quote with route DFlow compiling into an unsigned Solana transaction where DF1ow4 program ID appears twice"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem; line-height: 1.55;">
    <strong>Overview.</strong> The quote names DFlow; the unsigned transaction recovers the aggregator program ID twice. Schematic of the encoding finding—not a fill.
  </div>
</div>

---

## One Quote, One Transaction Artifact

A Rust decoder opened one live JTX unsigned Solana v0 transaction, resolved the exact accounts loaded through three address lookup tables, and found that two of five compiled instructions directly target DFlow Aggregator v4. The transaction did not preserve a readable JTX identity, downstream venue path, delivery receipt, or settlement result.

The JTX interface displayed “Route via DFlow” on a plain USDC→SOL quote. The browser saw JTX and wallet-service hosts, not a DFlow hostname. That absence cannot exclude a server-side DFlow call. The unsigned transaction is the first artifact in this workflow that can test router attribution directly.

Public docs place DFlow deeper than a quote label: named integration, quote API, ready-to-sign construction, submission tooling, streaming, and agent-facing interfaces. This piece opens one live capture at the ready-to-sign step—not a census of integrators, and not a submitted fill.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-08-18-the-interface-says-dflow-can-the-transaction-prove-it/figure_integration_depth.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-08-18-the-interface-says-dflow-can-the-transaction-prove-it/figure_integration_depth.png"
         alt="Documented DFlow integration depth ladder with ready-to-sign transaction highlighted as the step opened in this article"
         style="max-width:94%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem; line-height: 1.55;">
    <strong>Fig. 1.</strong> Documented integration depth from public DFlow / partner surfaces. Step 3 is where this capture sits: an unsigned ready-to-sign transaction. Distribution counts and named apps are company-reported or docs claims; they are not proven by the decode below. Adoption and retail pricing belong to <a href="{{ site.baseurl }}/2026/08/16/different-apps-same-router.html">Part I</a>.
  </div>
</div>

One live quote returned that unsigned transaction. It was retained, sanitized, hashed, and decoded. It was never signed or submitted. The app returns quote metadata and an unsigned transaction; the wallet authorizes it; delivery and Solana execution occur later. Why DFlow is economically material enough to study as wholesale execution infrastructure is [Part I]({{ site.baseurl }}/2026/08/16/different-apps-same-router.html)—not this piece.

**RESULT**

| Field | Value |
|---|---|
| transaction type | Solana v0 unsigned transaction |
| address lookup tables | 3 |
| compiled instructions | 5 |
| instructions targeting DFlow Aggregator v4 | 2 |
| addresses available across referenced tables | 759 |
| addresses actually loaded | 22 |
| candidate integrator marker | 1, unconfirmed |
| Jito tip-account matches | 0 |
| settlement | not submitted |
| sample size | n = 1 |

---

## Decoding the Transaction with Rust

The previous article’s quote panel kept the `transaction` field out of scope on purpose—those runs measured price. The field was there in the response; this piece opens it.

Rust is the practical choice: the Solana SDK provides the canonical representations (`VersionedTransaction`, `MessageAddressTableLookup`, `AddressLookupTable`). Malformed input can fail at `bincode`; semantic mistakes—such as incorrect ALT ordering—can still produce a plausible but false account map. Typed deserialization makes structural failures visible; it does not prevent a confident wrong map.

Each stage is a library function with a CLI subcommand over it, so a capture can be re-decoded months later without a browser. The pipeline is read-only end to end—no key material, no signing path, nothing that could submit.

```rust
let raw = STANDARD
    .decode(b64.trim())
    .context("invalid base64 transaction")?;
let vtx: VersionedTransaction =
    bincode::deserialize(&raw).context("failed to deserialize as VersionedTransaction")?;

let message = &vtx.message;
let static_keys: Vec<String> = message
    .static_account_keys()
    .iter()
    .map(|k| k.to_string())
    .collect();

let alt_refs = message.address_table_lookups().unwrap_or_default();
let transaction_type = if alt_refs.is_empty() {
    "legacy_or_v0_no_alt"
} else {
    "v0_with_alt"
};
```

This capture is `v0_with_alt`, with three address-table lookups. Static keys alone are incomplete—indexes into shared tables still have to be resolved before any instruction account can be named.

---

## Why Address Lookup Tables Are the Hard Part

A v0 transaction carries static keys plus indexes into shared on-chain tables. Fetching a table and reading its hundreds of addresses tells you what the table contains—not what the transaction uses. Shared tables are infrastructure; a single swap message borrows a thin slice of them.

The first implementation treated table membership as transaction use and produced a complete, plausible, false account map. Two eye-catching addresses—DFlow’s referral program, and a vanity address spelling marketing copy—sat in a referenced table but were never loaded. Their indexes are never requested. Being one of 251 addresses in a shared table is not evidence about this transaction.

The decoder must apply the transaction’s writable and readonly indexes and concatenate them in Solana’s order: writable across all tables first, then readonly.

```rust
for writable_pass in [true, false] {
    for alt in &decoded.address_lookup_table_references {
        let table = resolved_tables.get(&alt.lookup_table_account)?;
        let indexes = if writable_pass {
            &alt.writable_indexes
        } else {
            &alt.readonly_indexes
        };
        for &table_index in indexes {
            let address = table.get(table_index as usize)?;
            vector.push(LoadedAddress {
                account_vector_index: vector.len(),
                address: address.clone(),
                writable: writable_pass,
                lookup_table_index: Some(table_index),
                ..Default::default()
            });
        }
    }
}
```

Get that order wrong and every instruction’s account indexes resolve to the wrong addresses—silently. The output still looks complete. False marker candidates from whole-table attribution disappeared once exact indexes were applied.

Two guards catch the failure. Unit tests build a synthetic transaction whose tables contain far more addresses than the transaction loads, then assert the vector is exactly `[static…, writable…, readonly…]` and that an index past the end of a table errors rather than skips. Externally, the Associated Token Account instruction resolves to the canonical layout—funder, token account, owner, mint, System Program, SPL Token—in the slots the ATA program requires. Wrong ordering would scatter System Program and SPL Token out of those slots.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-08-18-the-interface-says-dflow-can-the-transaction-prove-it/figure1_account_vector.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-08-18-the-interface-says-dflow-can-the-transaction-prove-it/figure1_account_vector.png"
         alt="Table membership is not transaction use: 759 addresses available; exact indexes load 22; Solana ordering yields 32-entry account vector"
         style="max-width:94%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 2.</strong> A v0 transaction stores indexes, not an account list. The three referenced lookup tables hold 759 addresses; this transaction loads 22 via <code>writable_indexes</code> and <code>readonly_indexes</code>, concatenated after the static keys. Reading a whole table instead of applying its indexes yields a complete, plausible, false account map.
  </div>
</div>

On this capture: 759 addresses available across the three tables; 22 loaded; final account vector 32 entries (10 static + 22 loaded, split 7 writable / 15 readonly). Every loaded address is referenced by at least one compiled instruction.

---

## Mapping Five Compiled Instructions

With the account vector built, mapping an instruction is mechanical: resolve its program by index, then resolve each account index against the same vector.

```rust
for ix in &decoded.instructions {
    let program_slot = vector.get(ix.program_id_index as usize)?;
    let mut accounts = Vec::new();

    for (pos, &acct_index) in ix.account_indexes.iter().enumerate() {
        let slot = vector.get(acct_index as usize)?;
        accounts.push(InstructionAccountRef {
            position_in_instruction: pos,
            account_vector_index: acct_index as usize,
            address: slot.address.clone(),
            writable: slot.writable,
            label: slot.label.clone(),
        });
    }

    instructions.push(MappedInstruction {
        instruction_index: ix.index,
        program_id: program_slot.address.clone(),
        program_label: program_slot.label.clone(),
        accounts,
    });
}
```

Two of the five compiled instructions target [`DF1ow4…`](https://explorer.solana.com/address/DF1ow4tspfHX9JwWJsAb9epbkA8hmpSEAtxXy1V27QBH?cluster=mainnet-beta). The full program address [`DF1ow4tspfHX9JwWJsAb9epbkA8hmpSEAtxXy1V27QBH`](https://explorer.solana.com/address/DF1ow4tspfHX9JwWJsAb9epbkA8hmpSEAtxXy1V27QBH?cluster=mainnet-beta) sits in the static account keys and stores no name. The decoder first returned it as unknown; “DFlow Aggregator v4” comes from outside the transaction—[Solana Explorer](https://explorer.solana.com/address/DF1ow4tspfHX9JwWJsAb9epbkA8hmpSEAtxXy1V27QBH?cluster=mainnet-beta) and [Solana Compass](https://solanacompass.com/analytics/programs/DF1ow4tspfHX9JwWJsAb9epbkA8hmpSEAtxXy1V27QBH). The address is evidence in the unsigned message; the human-readable name is external attribution. Nothing was signed or submitted, so there is no landed transaction hash on Explorer.

The five instructions divide plainly: one Associated Token Account `CreateIdempotent`; two Compute Budget calls (limit 324,189 CU; price 50,000 micro-lamports per CU); two DFlow instructions (36 accounts / 134 bytes, then a 3-account follow-up). No top-level SPL Token transfer. If signed and landed unchanged, Solana would dispatch two instructions to that program. Downstream venue, runtime CPI, and settlement remain unresolved. A priority-fee compute-budget instruction is present; the Jito tip-account check returned zero hits.

---

## What Survived Compilation?

Compilation is selective. Some quote-JSON fields never become readable transaction fields. Others only exist at runtime or settlement and were never present to erase.

**Survived directly.** DFlow program address; instruction structure; static accounts; exact ALT references and the 22 loaded addresses; compute-budget parameters.

**External attribution.** The label “DFlow Aggregator v4”; ownership and executability labels from read-only RPC on 2026-07-29.

**Did not survive as readable metadata.** Request ID; `routePlan` JSON; venue labels such as “DFlow JIT Router”; app name; displayed fee label. The string “DFlow JIT Router” appears nowhere in the compiled bytes. What survives is a program address that a registry happens to name.

**Opaque.** The 134-byte DFlow payload may encode amounts, limits, or route parameters. Without a verified layout, this analysis records length and hash only. Static decode therefore cannot place the displayed fee inside the instruction, the routed amount, or a later CPI transfer.

**Requires runtime.** Downstream CPI venue path; fee transfers and balance effects; Jito bundle delivery; settlement. Those are not compilation losses.

One result moved the other way. The ATA-owner slot of `CreateIdempotent` references [`Cb1uxfFv…`](https://explorer.solana.com/address/Cb1uxfFv5TG3LRtdALitazALcLMhogbcDbXcz6vTQAyN?cluster=mainnet-beta), owned by executable program [`JTXJTX…`](https://explorer.solana.com/address/JTXJTXfr1wVRMEzqiPhXUr69zJtfGuLh5qEiXG772Zj?cluster=mainnet-beta). That vanity prefix belongs to the owner program, not to an address the transaction names as an instruction program. Classify it only as a **candidate integrator-associated owner program**—not proven app origin, not a confirmed fee account.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-08-18-the-interface-says-dflow-can-the-transaction-prove-it/figure2_evidence_matrix.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-08-18-the-interface-says-dflow-can-the-transaction-prove-it/figure2_evidence_matrix.png"
         alt="Evidence matrix: quote/API versus compiled transaction"
         style="max-width:94%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 3.</strong> Quote versus compiled transaction. Router label, program address <a href="https://explorer.solana.com/address/DF1ow4tspfHX9JwWJsAb9epbkA8hmpSEAtxXy1V27QBH?cluster=mainnet-beta" target="_blank" rel="noopener noreferrer"><code>DF1ow4…</code></a>, and registry name stay on separate rows. Runtime and settlement are out of scope here. One capture, n=1.
  </div>
</div>

Part I measures the displayed fee as a retail pricing object at quote stage. Here that fee does not reappear as a readable top-level transfer. That is a provenance boundary, not a redo of the fee decomposition.

---

## Closing

The interface named the router. Rust found the same router program inside the compiled transaction. The transaction did not preserve a readable app identity, and it could not reveal a runtime path, delivery channel, or settlement result that did not yet exist.

Transaction transparency begins after some execution decisions have already been made—and ends before others occur.

---

## Appendix

- Part I: [DFlow Shows Where Solana Trading Is Going. Retail Pricing Still Happens at the App.]({{ site.baseurl }}/2026/08/16/different-apps-same-router.html)
- Decoder: [`egpivo/dflow-transaction-lineage`](https://github.com/egpivo/dflow-transaction-lineage) @ [`0e79e1f`](https://github.com/egpivo/dflow-transaction-lineage/commit/0e79e1f015b1a9c31be3b7bdbfb4957591f2b98a) — capture 2026-07-29T13:20:14Z · USDC→SOL · 1,000 USDC · unsigned v0 · SHA-256 of serialized bytes `87a4fa3b06dbdad18825004f2a2446d8e05d5893c819e2f9f6a3f478a60b5c3a` · n = 1 · not signed or submitted
- Program ID [`DF1ow4…`](https://explorer.solana.com/address/DF1ow4tspfHX9JwWJsAb9epbkA8hmpSEAtxXy1V27QBH?cluster=mainnet-beta): [Explorer](https://explorer.solana.com/address/DF1ow4tspfHX9JwWJsAb9epbkA8hmpSEAtxXy1V27QBH?cluster=mainnet-beta) · [Compass](https://solanacompass.com/analytics/programs/DF1ow4tspfHX9JwWJsAb9epbkA8hmpSEAtxXy1V27QBH)
- Candidate owner program [`JTXJTX…`](https://explorer.solana.com/address/JTXJTXfr1wVRMEzqiPhXUr69zJtfGuLh5qEiXG772Zj?cluster=mainnet-beta); owned account [`Cb1uxfFv…`](https://explorer.solana.com/address/Cb1uxfFv5TG3LRtdALitazALcLMhogbcDbXcz6vTQAyN?cluster=mainnet-beta)
- Jito tip accounts: [on-chain addresses](https://jito-foundation.gitbook.io/mev/mev-payment-and-distribution/on-chain-addresses)
