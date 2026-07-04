---
layout: post
title: "When the Swap Actually Lands. What Can an Outsider Reconstruct?"
date: 2026-07-05
tags: [DeFi, RWA, Ethereum, Blockchain, Web3]
---

*A DEX receipt does not explain everything, but it gives outsiders a canonical place to start.*

---

In May 2026, [Ignas noted on X](https://x.com/DefiIgnas/status/2056401323256619180) that at least five high-profile Ethereum Foundation contributors had publicly announced their departures within a month. The post asked why; it did not establish a common reason. Still, the discussion revived a familiar refrain: Ethereum was finished.

I did not know whether the departures justified that conclusion, and I was not interested in treating organizational headlines as a protocol diagnosis. But the confidence narrative raised a more concrete question: what would a genuine rush for liquidity look like at the execution layer?

Quotes can age. Transactions compete for inclusion. Ordering changes execution. Liquidity moves, positions unwind, and some transactions revert after consuming gas.

What reassured me was not a price forecast, but that the Ethereum community's response remained technical: more execution capacity, stronger inclusion, faster confirmation, and better coordination across L1 and L2. That made the receipt layer a useful place to look—not because a receipt explains the whole event, but because it is the first canonical record of what actually landed.

> Which forms of market pressure can infrastructure reduce, and which failures remain problems of evidence and accountability?

The quote looked good. The calldata looked executable. But after the transaction was mined, what could an outsider independently verify?

A transaction receipt is not a complete explanation. It does not preserve the user's quote, reveal every internal call, or establish whether the execution was optimal. But it anchors the outcome to a shared, publicly inspectable state machine. From that anchor, the transaction input, execution trace, pool events, block context, and state changes can still be joined.

That makes a DEX receipt incomplete, but publicly anchored and partly reconstructible.

[Part I]({{ site.baseurl }}/2026/06/28/the-price-moves-first-route-frays-before-exit.html) asked what the interface proposed. [Part II]({{ site.baseurl }}/2026/06/30/when-the-quote-becomes-a-transaction.html) asked what the wallet submitted and whether it would execute under pinned state. Part III reaches the final record:

> What actually landed, and how much of the outcome can an outsider independently reconstruct?

This 300-block window is not a stress-event study. It is a baseline for identifying what the receipt layer preserves—and which questions would still require quote, trace, block-pressure, or market data during a genuine exit event.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-07-05-when-the-swap-actually-lands/dex_execution_boundary.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-07-05-when-the-swap-actually-lands/dex_execution_boundary.png"
         alt="DEX execution boundary from intent and calldata through ordering, EVM execution, and realized receipt"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 1.</strong> The DEX execution boundary from intent to realized receipt. The receipt anchors status, gas, and logs after execution; quote staleness, ordering, and failure cause require evidence from earlier or deeper layers. The infrastructure directions shown are architectural responses, not effects measured in this 300-block sample.
  </div>
</div>

---

## The mined outcome

I scanned Ethereum blocks 22,000,000 through 22,000,299 for transactions whose top-level `to` address was the deployed Universal Router, [`0x3fC91…7FAD`](https://etherscan.io/address/0x3fC91A3afd70395Cd496C647d5a6CC9D4B2b7FAD).

The fixed window contained 40 matching transactions: 30 successful receipts and 10 reverts. The decoder produced 109 ERC-20 Transfer events, 12 V2-compatible Swap events, and 26 V3-compatible Swap events. Among the successful receipts, 22 met the simple-candidate rule and 8 met the complex-candidate rule.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-07-05-when-the-swap-actually-lands/fig2_part3_sample_summary.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-07-05-when-the-swap-actually-lands/fig2_part3_sample_summary.png"
         alt="Transaction outcomes and decoded events in the 300-block receipt sample"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 2.</strong> Fixed-window receipt outcomes and decoded event counts. Simple and complex partition the 30 successful receipts; event counts are decoded log rows rather than transaction counts. The figure describes this 300-block sample and is not a market-wide execution-rate estimate.
  </div>
</div>

The labels are selection aids. A simple candidate has one decoded Swap event from one touched pool. A complex candidate has at least two decoded Swap events or at least two touched pools. Neither label reconstructs the full router path.

This window is also not a market-wide success-rate estimate. It is a reproducible sample with three useful kinds of landing: readable, heavier, and failed.

---

## Three landed outcomes

### A readable landing

Transaction [`0x1f7d…be70`](https://etherscan.io/tx/0x1f7da7a68150e8b9971d2682b11cf48a132079ade65bdcee1c2ca0fb29d0be70) landed in [block 22,000,120](https://etherscan.io/block/22000120) with `status=1`.

It used 131,680 gas and retained four logs. The decoder found two ERC-20 Transfer events and one V3-compatible Swap event from one pool.

The receipt proves that this transaction landed, completed without a top-level revert, used 131,680 gas, and retained four logs.

That sentence is deliberately limited. The receipt does not contain the quote shown to the user or the minimum-output constraint. It cannot say whether the pool was the best route. The emitted events make the landing readable; they do not explain why that path was selected.

### A heavier landing

Transaction [`0x114d…1e66`](https://etherscan.io/tx/0x114d412bd0eb6137cb5310af1ea13d8f222440a523b9e0b25993ca607c631e66) landed in [block 22,000,187](https://etherscan.io/block/22000187) with `status=1`.

It used 302,729 gas and retained eleven logs. Five were decoded ERC-20 Transfer events. Two were V2-compatible Swap events emitted by two pool contracts.

The first decoded V2-compatible event outputs to the second swap-emitting contract. This is consistent with a chained pool flow.

The transaction succeeded, retained eleven logs, and exposed two swap-emitting pools. Yet no receipt field records which alternative routes the router considered, why this path was selected, or whether a lower-cost route was available when the decision was made.

The receipt therefore identifies the realized footprint, not the decision set behind it. More emitted evidence does not necessarily make the routing decision identifiable.

### A failed landing

Transaction [`0xf8a3…9ce4`](https://etherscan.io/tx/0xf8a384e81fd359dc69440055e00375b0e5e317c18b9ab44d227033f044259ce4) landed in [block 22,000,182](https://etherscan.io/block/22000182) with `status=0`.

It used 304,322 gas and retained no logs.

The receipt proves that the transaction was included and reverted after consuming 304,322 gas. It does not prove that no internal calls or tentative state changes occurred before the revert; reverted state and logs do not survive in this receipt.

With `status=0` and no surviving logs, the receipt alone cannot distinguish a slippage failure from an allowance, token-transfer, pool, or router-command failure. A trace or revert payload is needed to separate those explanations.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-07-05-when-the-swap-actually-lands/fig3_part3_case_panel.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-07-05-when-the-swap-actually-lands/fig3_part3_case_panel.png"
         alt="Three receipt cases: single-pool success, multi-pool success, and reverted transaction"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 3.</strong> Three fixed cases from the 300-block sample. The single-pool case has a readable emitted footprint; the multi-pool case exposes more structure without complete route causality; the reverted transaction proves failure without its cause.
  </div>
</div>

---

## The receipt is not the explanation

The receipt proves the outcome, but not the decision path that produced it.

For a successful transaction, `status=1` does not mean best execution. For a reverted transaction, `status=0` does not identify the failed command. Logs support contract-local claims about emitted transfers and pool events, but receipt-log order is not a call graph.

The same boundary applies to market explanations. A transaction's position in a block does not by itself prove MEV. Gas use does not by itself prove congestion caused a bad result. A Swap event does not identify whether a router, pool, token, market move, or user-side constraint determined the outcome.

---

## Incomplete, but reconstructible

Evidence completeness and evidence reconstructibility are not the same thing.

A receipt is incomplete. It does not contain the original quote, full user intent, router command sequence, internal call hierarchy, or a causal MEV label. But the transaction hash joins the receipt to other public artifacts:

```text
receipt
  → transaction input
  → router commands and constraints
  → execution trace
  → pool and token state
  → block context and neighboring transactions
```

Operationally, the layers narrow different questions. With the receipt and calldata, an outsider can often recover the submitted router commands and encoded constraints. Adding a trace exposes the internal calls that actually executed.

Together, these artifacts recover much of the observable execution path, but not the counterfactual decision set: routes considered and rejected, alternative execution prices, or proof that the submitted route was optimal.

Not every join is free or easy. Archive access, tracing support, ABI coverage, token behavior, and off-chain quote retention still matter. Private order flow and user intent may remain unavailable.

The narrower point is that much of the missing execution explanation remains attached to a public, canonical state transition. Independent investigators can query the same transaction, decode the same input, inspect the same logs, and replay or trace the same chain state.

The receipt is therefore not valuable because it contains every answer. It is valuable because it supplies a canonical join key from which the audit can continue.

---

## What infrastructure can—and cannot—change

The infrastructure directions in Fig. 1 target different parts of the execution path. Execution scaling addresses capacity pressure. Fair ordering and inclusion address sequencing and censorship risk. Faster confirmation reduces the time available for quoted state to drift. L1/L2 interoperability reduces friction when liquidity and collateral move across execution domains.

These improvements can make the path more reliable, but they do not make a receipt self-explanatory. A faster or higher-capacity network still requires quote, calldata, trace, and state evidence to explain a particular outcome.

The roadmap can improve the environment in which a trade lands. It cannot replace the evidence needed to reconstruct why that trade succeeded, reverted, or received a particular execution.

---

## A comparison: when the venue owns the evidence

That property changes when the execution engine and the evidence issuer are the same private operator.

A centralized venue may expose order, fill, margin, liquidation, and account records, but there is no single public artifact from which an outsider can replay the complete decision path.

A liquidation record illustrates the gap. To independently reconstruct one decision, an outsider would need the index components, index price, mark price, collateral valuation, account equity, maintenance-margin rule, liquidation trigger, resulting order-book fills, any insurance-fund or auto-deleveraging action, and the final account ledger.

A venue may expose several outputs from that chain without exposing the internal state that connected them. The result can be visible while the decision remains externally non-replayable.

I previously examined how RWA products split authority across platform ledgers, token contracts, custodians, issuers, and redemption workflows in [Where RWA Exchange Risk Actually Sits]({{ site.baseurl }}/2026/06/21/where-rwa-exchange-risk-actually-sits.html). The execution question here is narrower: when a trade or liquidation completes, which parts of the decision can an outsider independently replay?

A DEX receipt records what a shared state machine accepted. A CEX record reports what the venue says its private state machine decided.

The DEX path is fragmented across transaction, receipt, logs, traces, blocks, and state, but much of it is publicly canonical and partly replayable. The CEX path may expose the order result, fill, liquidation notice, or account adjustment while keeping the matching sequence, risk-engine state, trigger calculation, and fallback behavior inside the venue.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-07-05-when-the-swap-actually-lands/dex_cex_comparison.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-07-05-when-the-swap-actually-lands/dex_cex_comparison.png"
         alt="DEX and CEX execution boundaries compared by evidence architecture"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 4.</strong> DEX and CEX execution records expose different reconstruction boundaries. A DEX receipt anchors the result to a shared state machine and can be joined to public transaction, trace, and state evidence. CEX records may expose the visible outcome while the matching and risk path remains venue-owned. This is an architectural comparison, not a finding that a particular venue record is incorrect.
  </div>
</div>

This comparison does not make every on-chain execution transparent. Quotes can be missing. Private order flow can remain private. Traces can be expensive to obtain, and protocol-specific interpretation can still fail.

That is the harder audit boundary: whether anyone outside the system can verify how the execution decision was made.

---

## Closing

[Part I]({{ site.baseurl }}/2026/06/28/the-price-moves-first-route-frays-before-exit.html) recorded the promise. [Part II]({{ site.baseurl }}/2026/06/30/when-the-quote-becomes-a-transaction.html) tested the submitted instruction under pinned state. Part III reached the mined outcome.

The receipt was not the whole explanation. It was the first canonical record from which the explanation could continue.

That may be the more important property of public execution. The evidence is fragmented across quotes, calldata, traces, logs, blocks, and state, but much of it can still be independently reconstructed.

Private exchanges expose a different boundary. Users may receive an order record, a fill, a liquidation notice, or a corrected balance while the state machine that produced those records remains internal to the venue.

The final question is therefore larger than whether a receipt exists:

> Can anyone outside the system verify how the execution decision was made?

---

## Appendix

- The public [`receipt_layer_sample.py`](https://gist.github.com/egpivo/5fe3d5d03945d08ac1a6687c8e17136a#file-receipt_layer_sample-py) contains the fixed-window scanner and reproduction instructions for blocks 22,000,000–22,000,299.

- Receipt and event semantics: [`eth_getTransactionReceipt`](https://ethereum.org/en/developers/docs/apis/json-rpc/#eth_gettransactionreceipt), [ERC-20](https://eips.ethereum.org/EIPS/eip-20), [Uniswap V2 events](https://github.com/Uniswap/v2-core/blob/master/contracts/interfaces/IUniswapV2Pair.sol), and [Uniswap V3 events](https://github.com/Uniswap/v3-core/blob/main/contracts/interfaces/pool/IUniswapV3PoolEvents.sol).

- Infrastructure context: [Ethereum scaling](https://ethereum.org/roadmap/scaling/), [inclusion and proposer-builder separation](https://ethereum.org/roadmap/pbs/), [single-slot finality](https://ethereum.org/roadmap/single-slot-finality/), and the Ethereum Foundation's [L1/L2 direction](https://blog.ethereum.org/2026/03/23/l1-l2-ethereum).

- Opening context: [Ignas on five publicly announced Ethereum Foundation departures](https://x.com/DefiIgnas/status/2056401323256619180), May 18, 2026. The post raised questions about their reasons; it did not establish a shared motive.
