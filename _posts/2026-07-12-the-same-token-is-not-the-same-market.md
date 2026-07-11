---
layout: post
title: "The token appeared twice. The AMM market formed once"
date: 2026-07-12
tags: [DeFi, DEX, Solana, Ethereum, Blockchain, RWA]
---

*Canonical deployment tells you which contract is real. It does not tell you whether a callable public-pool trading surface formed around it.*

---

SPYx had verified canonical deployments on both Solana and Ethereum—same issuer, same underlying exposure—but that fact told me almost nothing about whether a substantial public-pool trading surface had formed on either chain.

From April 1 through June 21, observed Solana public-pool activity stayed low for much of April and May, then accelerated sharply into mid-June. On June 20 UTC, Raydium contributed about **$96.4 million** and Orca **$91.8 million**, with other discovered pools contributing **less than $200**.

Across the one canonical-SPYx pool I discovered on Ethereum, a June 1–21 query returned **13** decoded swaps and **$43.49** in executed USDC notional. No swaps occurred before June 6.

This is not a clean experiment in which only the chain changed. The Solana side uses observed public-pool venue aggregates over April 1–June 21; the Ethereum side uses decoded events from the one discovered canonical pool over June 1–21. Neither covers every execution channel. The result is an observed activity gap, not an identified chain effect.

> Canonical deployment was a poor proxy for whether a substantial public-pool trading surface had formed.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-07-12-the-same-token-is-not-the-same-market/fig1_same_asset_different_surface.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-07-12-the-same-token-is-not-the-same-market/fig1_same_asset_different_surface.png"
         alt="Panel A: observed Solana gross public-pool volume by venue from April 1 to June 21; Panel B: decoded swap events from the discovered canonical Ethereum Uniswap V3 pool on an independent scale"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 1.</strong> Canonical SPYx activity in discovered public pools. Panel A: observed Solana gross public-pool volume by venue (Raydium / Orca / Other), <strong>April 1–June 21 UTC</strong>. Panel B: decoded events from the discovered canonical Ethereum Uniswap V3 pool, <strong>June 1–21 UTC</strong>, on an independent scale. June 1–5 on the Ethereum panel reflect a queried and confirmed zero, not missing coverage. The comparison measures observed activity, not total market share or a causal chain effect.
  </div>
</div>

---

## How I built the comparison

**Canonical identity.** I verified the issuer-listed canonical identifiers: Solana Token-2022 mint [`XsoCS1…DF2W`](https://solscan.io/token/XsoCS1TfEyfFhfvj8EtZ528L3CaKBDBRqRapnBbDF2W) and Ethereum ERC-20 contract [`0x90a2…dd48`](https://etherscan.io/address/0x90a2a4c76b5d8c0bc892a69ea28aa775a8f2dd48). Pools indexed under the same `SPYx` ticker but using different contracts were excluded.

**Solana.** The collector queried GeckoTerminal OHLCV for the verified canonical-SPYx pool registry (61 pools), preserved missing observations separately from reported zeros, and aggregated pool-level rows into daily Raydium / Orca / Other venue totals for **April 1–June 21**.

**Ethereum.** I queried `eth_getLogs` over a UTC-aligned block range covering June 1–21 ([blocks 25,218,798](https://etherscan.io/block/25218798)–[25,369,413](https://etherscan.io/block/25369413)) via `mainnet.gateway.tenderly.co` and decoded Uniswap V3 Swap events from the one discovered canonical SPYx/USDC pool ([`0xafdd…4575`](https://etherscan.io/address/0xafdd3bdc20a31652e48b56b73952ca324f544575)). The event table contains 13 rows with signed token amounts and exact USDC-side notional (run id: `spyx_202606_mtd_2026-06-21`; tx links in the [gist bundle](https://gist.github.com/egpivo/c867941c6c650fc1722db25650010c72)).

---

## What the contract did—and did not—deploy

A token contract defines balances and transfer rules. It can establish which SPYx is canonical and whether a transfer succeeded.

It cannot place quote inventory beside that token.

LPs can do that through a public AMM pool. They deposit SPYx and a quote asset, and the pool exposes that inventory through a callable pricing rule. The trader does not need another trader to submit a matching order at the same moment.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-07-12-the-same-token-is-not-the-same-market/fig2_amm_pool_availability.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-07-12-the-same-token-is-not-the-same-market/fig2_amm_pool_availability.png"
         alt="Schematic: liquidity providers deposit SPYx and quote assets into a public AMM pool; traders send quote assets in and receive SPYx out; fees accrue to active LP positions"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 2.</strong> The token contract defines transferability. Active liquidity makes inventory callable through the pool, while swap fees accrue to active LP positions.
  </div>
</div>

The distinction becomes sharper in concentrated-liquidity pools. Two pools can report similar nominal liquidity while offering very different executable depth if one places capital near the current price and the other does not. Capital outside the active range does not contribute liquidity at the current price and earns no fees until the price enters its range. Nominal liquidity and executable liquidity are not the same quantity.

### The passive liquidity trap

A dormant canonical pool also raises a harder question: why would passive liquidity form there in the first place?

Arbitrageurs do not steal from an AMM in the ordinary sense. They still have to trade through the pool. The problem is that they trade against stale inventory. If the external reference price moves before the pool price catches up, the pool can be offering the asset too cheaply or too expensively. Arbitrageurs correct that gap, but the correction changes what the LP is left holding.

For the LP, the question is not whether the pool collected fees. It is whether those fees covered the cost of being picked off while the pool price lagged the external mark. In AMM models this cost is often discussed as loss-versus-rebalancing, or LVR ([Campbell et al., 2025](https://arxiv.org/pdf/2508.08152)): the gap between passively providing liquidity and continuously rebalancing against the external price.

Fundamental demand matters because it can pay that bill. A deep ETH/USDC pool may see enough real two-sided flow for fees to offset part of the arbitrage cost. A thin RWA market is different. For SPYx, the dominant mark is offchain TradFi; if that mark moves while onchain fundamental demand is sparse, passive LPs may face the downside of repricing without enough fee income to make the position worthwhile. Capital may stay out, or sit in ranges too far from the mark to offer executable depth.

That does not prove why the Ethereum SPYx pool stayed quiet. This run does not reconstruct LP positions, fee tiers, active ranges, or mark-to-market LVR for `0xafdd…4575`. It cannot distinguish thin demand, inactive ranges, routing integration, fee economics, or simple lack of LP interest. The observed evidence is consistent with a passive-liquidity economics problem, but this run does not identify it. Swap count alone is not enough for the next measurement—the question is whether posted LP capital would have beaten holding after external repricing, and whether the fee schedule made it rational to keep executable inventory available.

The one discovered Ethereum canonical pool produced 13 small swaps during the 21-day query window; all occurred from June 6 onward. The contract was present, but substantial executed liquidity was not observed in this window.

---

## What the volume bars do—and do not—mean

The Solana bars are **gross venue-leg volume**, not unique originating-order notional. A routed order touching two pools contributes to both pools' counts. The current dataset also does not measure proprietary liquidity outside the indexed public pools—unavailable proprietary volume is not zero.

Across the April 1–June 21 observed window, activity concentrates in Raydium and Orca on active days, with smaller pools remaining a minor share of observed public-pool volume.

The Ethereum result is bounded by the one pool discovered and decoded. Zero decoded swaps on a given day in that pool is an exact result for that pool, not a claim about other contracts or offchain venues.

Those boundaries narrow the claim; they do not erase it.

The useful finding is not that Solana "won." It is that deploying the canonical token was only the first step in market formation. Inventory had to be positioned, active ranges maintained, venues integrated, and routers able to reach them.

---

## Pooled-only routing rose in the higher-size bucket

Once a public-pool surface exists, the next question is whether a router continues to use it when executed size increases. This is a separate validation window, not a transaction-level reconstruction of the June 20 surge.

I examine an OKX-routed canonical-SPYx sample from **2026-06-21 to 2026-06-24** and compare **3,253** transactions below $1,000 with **3,442** transactions between $1,000 and $10,000.

Candidate discovery takes the **union** of canonical-SPYx mint signatures and verified canonical-pool signatures, deduplicates them, and retains transactions in which canonical SPYx and the OKX router co-occur. Pool pagination supplements mint pagination; a retained transaction does not need to touch a public pool at execution time.

In the raw transaction sample, pooled-only routing increased from **25.9%** to **45.6%**. Proprietary-only routing fell from **35.3%** to **31.7%**, while hybrid routing fell from **25.1%** to **18.4%**.

I classify a transaction as **pooled-only** when the parsed venue set contains verified public-pool programs (for example Raydium or Orca) but no verified proprietary program; **proprietary-only** when it contains verified proprietary programs (for example AlphaQ or SolFi) but no public pool; and **hybrid** when both classes appear. Co-occurrence identifies a route class, not necessarily a parallel split.

Raw transaction counts were concentrated in repeated wallet, amount, and route combinations, so I recomputed the size-bucket difference using one-transaction-per-wallet-hour and a repeated-pattern-adjusted sample. The weighting checks narrow the interpretation: pooled-only routing is higher in the $1k–$10k bucket under all three weighting schemes (**+19.7 pp**, **+5.0 pp**, **+5.4 pp**). Proprietary-only routing decreases under all three (**-3.7 pp**, **-3.5 pp**, **-9.2 pp**). Hybrid routing is sensitive to weighting (raw negative, adjusted positive).

The durable result is therefore not that the higher-size bucket shifted toward proprietary makers. It is that public pools remained important and became more common as the sole classified execution source in the $1,000–$10,000 bucket of this OKX sample.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-07-12-the-same-token-is-not-the-same-market/fig3_route_shift_by_size.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-07-12-the-same-token-is-not-the-same-market/fig3_route_shift_by_size.png"
         alt="Route architecture in OKX-routed canonical-SPYx transactions: Panel A shows share of transactions by executed trade size; Panel B compares percentage-point changes under raw, wallet-hour, and repeated-pattern weighting"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 3.</strong> Route architecture across two executed-size buckets in OKX-routed canonical-SPYx transactions (OKX-router-specific), validation window <strong>2026-06-21 to 2026-06-24</strong>. Panel A reports route-class shares for below $1,000 (n=3,253) and $1,000–$10,000 (n=3,442), n=6,695 total in the plotted size window (decoded rows with blank executed notional excluded). Panel B reports percentage-point differences under three weighting schemes: raw transactions, one transaction per wallet-hour, and repeated-pattern adjustment. Pooled-only is positive across all schemes; proprietary-only is negative across all schemes; hybrid changes sign by weighting. The result is descriptive and does not identify a causal size effect.
  </div>
</div>

This is OKX-router-specific evidence from a bounded validation sample. It does not generalize to all Solana routers, all months, or trades above $10,000.

---

## What this dataset does not measure

This is observed public-pool activity (Solana April 1–June 21) plus an OKX-router validation sample, not a complete SPYx market census across all venues and months.

- Public-pool volume does not equal total SPYx execution volume.
- Gross venue-leg volume does not equal unique originating-order notional.
- Ethereum coverage is limited to one discovered canonical pool.
- The OKX sample is router- and window-specific, and does not identify causality.

**Interpretation:** June 20 UTC volume on Solana coincided with a U.S. holiday weekend context (Juneteenth on June 19, Saturday on June 20). That calendar annotation is descriptive. I do not treat it as a causal explanation for the surge.

---

## Closing

Canonical SPYx existed on both chains. In the observed public-pool panel through June 21, only Solana showed a substantial public-pool trading surface. In the separate OKX validation sample, higher-notional routing did not move away from pools: pooled-only routing became more common while proprietary-only did not increase.

Passive LPs are not obligated to form that surface. If fees do not compensate adverse selection and fundamental flow is thin, a canonical pool can remain callable in principle and thin in practice.

Before a router can search for a route, executable liquidity must exist somewhere. The SPYx comparison makes that first boundary visible:

> The same token can be deployed twice without the same market forming twice.

The next question is not whether SPYx exists onchain. It is which inventory a router can actually reach when size arrives—and whether the fee mechanism made posting that inventory rational.

---

## Appendix

- **Reproducibility package:** [gist bundle](https://gist.github.com/egpivo/c867941c6c650fc1722db25650010c72) — processed CSVs, collection and figure scripts, validation and reconciliation sheets (`spyx_blog_reproducibility.md` indexes the bundle).
- **RWA context:** [Where RWA Exchange Risk Actually Sits]({{ site.baseurl }}/2026/06/21/where-rwa-exchange-risk-actually-sits.html).
- **LVR / passive LP economics:** [Campbell et al., Optimal Fees for Liquidity Provision in Automated Market Makers](https://arxiv.org/pdf/2508.08152) (arXiv:2508.08152, 2025).
- **Downstream quote layer:** [The Price Moves First]({{ site.baseurl }}/2026/06/28/the-price-moves-first-route-frays-before-exit.html); [When the Quote Becomes a Transaction]({{ site.baseurl }}/2026/06/30/when-the-quote-becomes-a-transaction.html).
