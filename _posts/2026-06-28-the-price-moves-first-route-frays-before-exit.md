---
layout: post
title: "The Price Moves First. DEX Routes Fray Before the Exit."
date: 2026-06-28
tags: [DeFi, RWA, Ethereum, Blockchain, Web3]
---

*A quote is the first place where exit risk becomes observable—not as a failed trade yet, but as route fragmentation, output deterioration, and summary-field ambiguity.*

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-06-28-the-price-moves-first-route-frays-before-exit/hero.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-06-28-the-price-moves-first-route-frays-before-exit/hero.png"
         alt="One price, many routes: a price mark enters a DEX quote with output, pool hops, and API price impact; proposed routes branch from one to twelve hops while execution success or revert remains outside the article's measurement"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
</div>

---

Most users read a DEX quote as a number. I read it as an evidence object: pool hops, split paths, output rate, API `priceImpact`, block state, and the transaction boundary ahead.

[Solana Data’s recent comparison of blockchain metrics across providers](https://x.com/vibhu/status/2069099097139581149?s=20) makes a broader measurement problem visible: a shared label does not guarantee a shared construction path. A DEX quote has the same problem one layer lower: one output number can compress different pools, fee tiers, intermediate tokens, and split routes.

DEX exit risk does not begin at transaction failure. In this run, it began when the quote stopped looking like a single price and started looking like a route map—before any swap was sent.

Price marks the position. After it moves, the loss can still take different forms: an execution haircut, a failed swap, a delayed redemption, or a withdrawal that cannot clear. Those outcomes do not share one measurement. This post asks what the **quote layer** exposes before execution.

I swept Uniswap classic routes from **$100** to **$1M** (USDC → WETH, LINK, AAVE, MKR) on June 17, 2026. At larger sizes, several quotes drew on more pools and intermediate hops. One pair also showed a sign disagreement between the API `priceImpact` field and the output-rate direction.

Market stress makes exit capacity worth asking about. The useful parallel from the [SpaceX access episode]({{ site.baseurl }}/2026/06/21/where-rwa-exchange-risk-actually-sits.html) is narrower: centralized venues can cancel, refund, or issue replacement objects when an upstream allocation fails. A DEX route has no default actor who can create the replacement object. Once the quote becomes a transaction, failure moves to pool state, transaction constraints, token controls, and execution outcomes.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-06-28-the-price-moves-first-route-frays-before-exit/fig1_macro_volatility_backdrop.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-06-28-the-price-moves-first-route-frays-before-exit/fig1_macro_volatility_backdrop.png"
         alt="Rolling seven-day volatility for BTC, ETH, and WTI oil with pre-shock, escalation, and de-escalation context windows"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 1.</strong> Macro backdrop for the exit question—context for the collection window.
  </div>
</div>

---

## The ladder run

I requested Uniswap classic routes on Ethereum mainnet for:

- USDC → WETH, LINK, AAVE, and MKR
- $100, $1k, $10k, $100k, and $1M input sizes
- 50 bps slippage tolerance
- V2, V3, and V4 routes; UniswapX excluded

The collection run was `2026-06-17T134419Z`. Each saved response included proposed output, route plan, API-reported `priceImpact`, gas estimate, and block. The dataset contains no signed transactions, mempool observations, or receipts.

One limitation: successful responses span blocks `25337645`–`25337664`, so the ladder mixes size changes with modest live-state drift. It is not a same-block counterfactual.

I also pinned one block, `25337659`, and replayed WETH, AAVE, and MKR with a local [Smart Order Router](https://github.com/Uniswap/smart-order-router). The local router is not the Trading API, so I keep it separate. But the pattern survived the stricter setup: with block state fixed, pool-hop counts still changed with size.

The routing API returns a proposed output and path under state at request time. It does not lock that state. I used Uniswap's [`POST /quote` API reference](https://developers.uniswap.org/docs/api-reference/aggregator_quote). The user still signs with a minimum output, deadline, and gas; if state moves against the quote, the swap can revert ([swaps concepts](https://developers.uniswap.org/docs/get-started/concepts/traders/swaps)).

---

## At $1M, the quote became a route map

In this ladder, the first visible change was the quote object becoming a route map.

At $100, the quote can look like one number. At $1M, the routing structure is harder to ignore.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-06-28-the-price-moves-first-route-frays-before-exit/fig2_route_complexity.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-06-28-the-price-moves-first-route-frays-before-exit/fig2_route_complexity.png"
         alt="Routing pool-hop count across Uniswap classic quote sizes for WETH, LINK, AAVE, and MKR"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 2.</strong> Total pool hops across the proposed split routes, by USDC input size. Uniswap classic route plans at quote time.
  </div>
</div>

The router may split a larger input across parallel paths, fee tiers, and intermediate tokens. I count pool hops across those proposed routes—the routing structure behind one output number.

In this run:

- WETH reached **7** pool hops at $1M.
- LINK reached **6**.
- AAVE moved from **1** hop at $100 to **12** at $1M.
- MKR reached **7** at $1M.

AAVE is the sharp contrast: twelve hops at $1M, assembled across several pools and intermediate tokens.

---

## Route structure and output deterioration are different axes

Pool hops and quoted output deterioration pull apart in this ladder:

- **WETH:** modest impact at $1M (**0.30%**), but **7** pool hops.
- **LINK:** **6** hops at $1M without a large impact field.
- **MKR:** aligned deterioration at $1M—API **46.11%**, output-rate benchmark **~45.96%**.
- **AAVE:** **12** hops plus cross-benchmark sign disagreement at $100k and $1M.

Read route composition and output-rate movement separately.

---

## Cross-benchmark check: AAVE diverges, MKR aligns

I also compared API-reported `priceImpact` with output-rate deterioration from the returned output. At large size, even the quote summary can become part of the audit problem.

Let out(*S*) be `response.quote.output.amount` converted into human-readable output tokens for input size *S*. I define the ladder's output-rate deterioration as:

```text
output-rate deterioration(S)
= 1 - [(out(S) / S) / (out(100) / 100)]
```

The $100 quote is an internal reference within the same ladder.

The two metrics answer different questions, so I do not expect numerical agreement. I use sign agreement only as a basic cross-field sanity check: whether the API summary and output-per-USDC movement point in the same direction.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-06-28-the-price-moves-first-route-frays-before-exit/fig3_quote_object_inspection.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-06-28-the-price-moves-first-route-frays-before-exit/fig3_quote_object_inspection.png"
         alt="Comparison of one-million-dollar Uniswap classic WETH and AAVE quote objects, including route legs and API versus output-rate impact"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 3.</strong> Two $1M quote objects. WETH's API impact and output-rate comparison remained close. AAVE returned 12 pool hops and a negative API impact while output per USDC deteriorated relative to its $100 quote.
  </div>
</div>

WETH stayed aligned: **0.30%** API impact at $1M versus about **0.34%** output-rate deterioration. MKR also stayed aligned: **46.11%** API impact versus about **45.96%** output-rate deterioration.

AAVE did not. The $1M response reported **−34.11%** price impact while output per USDC was about **6.13%** worse than at $100; at $100k the sign disagreed as well. I kept AAVE in the route figure and flagged its $100k and $1M points in the impact chart for cross-benchmark sign disagreement.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-06-28-the-price-moves-first-route-frays-before-exit/fig4_price_impact_filtered.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-06-28-the-price-moves-first-route-frays-before-exit/fig4_price_impact_filtered.png"
         alt="Filtered Uniswap API-reported price impact across trade sizes for WETH, LINK, AAVE, and MKR"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 4.</strong> Uniswap API-reported price impact by size. AAVE at $100k and $1M appear as open markers, flagged for cross-benchmark sign disagreement with the ladder output-rate metric. MKR $1M stays on the main series; both measures point to roughly 46% deterioration.
  </div>
</div>

I checked the AAVE rows against the saved Uniswap JSON and the normalized ladder. The negative API `priceImpact` values appear in the raw responses; the output-rate calculation reproduces from raw amounts, and WETH and MKR pass the same pipeline with matching signs. Under this setting, AAVE is a cross-benchmark discrepancy that survives the data-pipeline audit.

The remaining question is router-level: how the Trading API defines `priceImpact` when a route is split across multiple pools, fee tiers, and intermediate tokens. The saved artifact is enough to audit the mismatch, but not enough to attribute it to a specific aggregation rule.

---

## What this ladder does not measure

This is quote-layer evidence: saved route plans, outputs, blocks, and API summary fields. It contains no signed transactions, mempool observations, or receipts. Every pair returned a $1M quote in this window, but quote success is not exit capacity.

Pool-hop counts describe routing structure, not pool depth or fill outcome. Gas, inclusion, ordering, private flow, state changes, and MEV belong to a later layer after broadcast. The macro backdrop and SpaceX comparison motivate the exit question; they do not explain the AAVE or MKR rows. The AAVE discrepancy survives basic parsing and decimal checks, but its router-level cause remains unresolved.

---

## Closing

Before signing, I would ask four quote-layer questions from this run:

1. How many pool hops does the router need to assemble this size?
2. Does output per USDC deteriorate versus a smaller quote in the same ladder?
3. Does the API `priceImpact` summary agree in sign with that output-rate movement?
4. Where does the evidence stop—quote JSON, or receipt?

The next test is fork execution: replay the quoted swaps under controlled state changes and check whether `amountOutMinimum` still holds. Reverts and output gaps would move the evidence from **route fraying** toward **exit breakage**.

---

## Appendix: sources

- **Main ladder:** Uniswap [`POST /quote` API](https://developers.uniswap.org/docs/api-reference/aggregator_quote) on Ethereum mainnet, collection run `2026-06-17T134419Z` (June 17, 2026). USDC → WETH, LINK, AAVE, MKR; $100–$1M; 50 bps; V2/V3/V4 classic routes.
- **Output-rate audit:** [minimal sanity check gist](https://gist.github.com/egpivo/fe9bc7774c2d08a04ee960b66082f825). It compares raw `response.quote.priceImpact` to cross-quote output-rate math on saved Uniswap JSON and does not fetch quotes.
- **RWA context:** [Where RWA Exchange Risk Actually Sits]({{ site.baseurl }}/2026/06/21/where-rwa-exchange-risk-actually-sits.html). The SpaceX episode separates subscription claims, refunds, replacement tokens, perps, wallet tokens, and brokerage shares into different audit objects.
- **Macro backdrop (Fig. 1):** public BTC, ETH, and WTI daily prices; shaded windows are context only.
- **Fixed-block check:** local [Smart Order Router](https://github.com/Uniswap/smart-order-router) replay at block `25337659` for WETH, AAVE, and MKR. This check is kept separate from the Trading API ladder.
