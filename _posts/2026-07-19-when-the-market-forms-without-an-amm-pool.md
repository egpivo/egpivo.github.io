---
layout: post
title: "Hyperliquid Shows What a Market Looks Like Without an AMM Pool"
date: 2026-07-19
tags: [DeFi, DEX, Blockchain, RWA, Web3]
image: /assets/2026-07-19-market-without-amm-pool/hero.png
---

*[Part I]({{ site.baseurl }}/2026/07/12/the-same-token-is-not-the-same-market.html) asked whether an AMM surface formed. [Part II]({{ site.baseurl }}/2026/07/14/before-mev-build-the-pool.html) opened the pool. This piece looks at the other state object: posted depth in a CLOB.*

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-07-19-market-without-amm-pool/hero.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-07-19-market-without-amm-pool/hero.png"
         alt="Schematic comparing AMM architecture (pool state x·y=k, LP deposits, arbitrage) and CLOB architecture (order book, maker quotes, margin and risk engine), with a legend for publicly observable vs non-reconstructible fields"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
  <strong>Overview.</strong> Two market-formation objects—AMM committed reserves vs CLOB posted depth. Schematic architecture and visibility map; not measured from a live pool or venue.
  </div>
</div>

***
[Hyperliquid](https://hyperliquid.xyz) became hard to ignore for more than one reason.

HYPE's price action helped draw attention. I do not treat token performance as market-structure evidence. Fees are the cleaner hook: in a 2026 H1 [DeFiLlama](https://defillama.com/) pull (Jan 1–Jun 30 UTC), Hyperliquid logged about **$419 million**, ahead of Aave and Uniswap in the same peer set.

[Reuters](https://www.reuters.com/legal/government/crypto-exchanges-gear-up-launch-us-perpetual-futures-ahead-rule-change-2026-04-22/), citing CryptoQuant, also named Hyperliquid among major offshore perp venues in a report on 2025 perp volume: **$61.7 trillion** globally, against **$18.6 trillion** in spot. I am not merging that headline figure with DeFiLlama daily fees; the scopes differ. It only explains why this is not a random venue pick.

The context is noisy. If marginal capital is crowding into AI, a few high-attention names, or leveraged venues, weak spot activity can look like an AMM problem before it is one. Fees make Hyperliquid worth inspecting. They do not decide the pool-versus-book question.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-07-19-market-without-amm-pool/fig0b_protocol_fee_attention.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-07-19-market-without-amm-pool/fig0b_protocol_fee_attention.png"
         alt="Bar chart of protocol fees in USD millions for 2026 H1 (DeFiLlama daily chart), Hyperliquid ranked first among selected DeFi protocols"
         style="max-width:88%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 1.</strong> Protocol fees by protocol for 2026 H1 (Jan 1–Jun 30 UTC). Bars sum DeFiLlama daily fee data; definitions differ across protocols, so this is an attention signal, not a mechanism comparison. Hyperliquid appears first in this peer sample at about $419M. Source: <a href="https://gist.github.com/egpivo/2da1db905a09cbf9e2b83840eee5fbf9" target="_blank" rel="noopener noreferrer">reproducibility gist</a>.
  </div>
</div>

When the market forms without a pool, what state object replaces it?

Hyperliquid is the case study because its public <code>info</code> API exposes enough book state to make that question answerable.

***

## This is not an AMM death claim

"AMM is dying" bundles too many claims—volume share, LP economics, launch patterns, trader attention. I am not adjudicating all of them.

The useful question is narrower: what market object fits the product?

Callable spot still maps to pools. Perps need margin, funding, liquidation, open interest, and position accounting—state a passive curve does not carry on its own. That split is old in TradFi. What is newer on-chain is inspectability: fee flow large enough to notice, plus public APIs that return book, funding, and OI fields.

For an AMM, the audit starts with reserves and swaps. For a CLOB, it starts with bids, asks, fills, funding, open interest, and whatever slices of the risk engine leak out. Fee rank does not settle that split.

When a non-AMM venue both collects real fees and publishes `l2Book`, the book stops being only a UI widget. It becomes a partial market object—imperfect, capped at 20 levels per side in Hyperliquid's case, but callable from outside.

***

## Callable inventory vs posted depth

An AMM and a CLOB fail differently.

An AMM exposes **callable inventory governed by a pricing curve**. A pool holds reserves and quotes through a rule such as `x * y = k`. A trader does not choose a counterparty. The pool is the counterparty. That is why [Part II]({{ site.baseurl }}/2026/07/14/before-mev-build-the-pool.html) could measure execution by running pool state forward—change trade size and execution drag changes; change reserves and executable depth changes; move the external price and arbitrage pushes the pool until the remaining gap is fee-limited.

A CLOB exposes **persistent book depth through price-level commitments**. There is no single reserve pair that defines the market. There are bids, asks, sizes, spreads, and depth around the mid. A taker consumes posted orders. A maker can cancel, repost, or move inventory elsewhere.

AMM liquidity is committed into a contract. CLOB liquidity is posted into a queue.

The advantage is not that a book clears what a pool cannot. The book's native fit is conditional liquidity: at this price, for this size, for now. A maker can tighten, widen, cancel, or hedge as inventory and risk change. Queue position and timing become part of the market.

A pool can make its defense layer more active through ranges, fees, and hooks, but it still exposes inventory through a rule. It does not become a native price-time queue.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-07-19-market-without-amm-pool/fig1_amm_curve_vs_clob_book.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-07-19-market-without-amm-pool/fig1_amm_curve_vs_clob_book.png"
         alt="Panel A: illustrative constant-product reserve curve; Panel B: Hyperliquid BTC perp L2 bid and ask levels from a public snapshot"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 2.</strong> AMM and CLOB markets expose different state objects. Panel A is an illustrative constant-product reserve curve (not measured from a live pool). Panel B is a Hyperliquid BTC perp L2 snapshot from <code>POST https://api.hyperliquid.xyz/info</code> with <code>{"type":"l2Book","coin":"BTC"}</code> at <strong>2026-06-30T02:09:33.700Z</strong>. The figure compares mechanism shapes only; it does not rank venue quality or liquidity.
  </div>
</div>

In the AMM panel, the visible state is compact: a reserve point plus a pricing rule. In the CLOB panel, the visible state is a ladder of price levels. Each level can contain one or more posted orders (`n` in the API response is order count at that level, not queue position). The book can change without a trade, because makers can cancel or replace orders.

***

## A small Hyperliquid snapshot

On **2026-06-30T02:09:33.700Z**, I pulled `l2Book` snapshots for four perps on the primary Hyperliquid dex and computed mid, spread, and visible notional depth within ±1% of mid. At snapshot time, spreads were tight—**0.17 bps** on BTC, **0.63** on ETH, **0.13** on SOL, **0.15** on HYPE—and visible depth within ±1% of mid ranged from sub-million on SOL to roughly **$18–23M** on ETH (see Fig. 3).

The public `l2Book` endpoint returns **at most 20 price levels per side**. For all four markets in this snapshot, every visible level fell inside the ±1% band—so ±5% depth equals ±1% depth in the processed file. That is a measurement cap, not evidence that depth is flat beyond 1%.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-07-19-market-without-amm-pool/fig2_clob_spread_depth_snapshot.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-07-19-market-without-amm-pool/fig2_clob_spread_depth_snapshot.png"
         alt="Bar chart of top-of-book spread in bps and visible notional depth within 1% of mid for BTC ETH SOL HYPE"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 3.</strong> Single-point CLOB snapshot across BTC, ETH, SOL, and HYPE at <strong>2026-07-02T05:40:43Z</strong>. Panel A: top-of-book spread in basis points. Panel B: visible notional depth within ±1% of mid (sum of <code>px × sz</code> per level; max 20 levels per side). Not a historical average.
  </div>
</div>

The snapshot is a point-in-time view of what the public book exposed when the probe ran—not a claim about permanent liquidity.

Depth here comes from posted levels around the mid, not from reserves on a curve. In [Part II]({{ site.baseurl }}/2026/07/14/before-mev-build-the-pool.html), depth came from the pool state. Here it comes from the book.

The same probe window also pulled funding and open interest from `metaAndAssetCtxs`—fields with no direct AMM analog. BTC at snapshot time: funding **0.0000125**, open interest **35,637** contracts (base units), 24h notional volume **$3.12B**; mark **60,652**, mid **60,652.50**, oracle **60,654** (premium **−0.000016**).

***

## What the book exposes — and what it does not

Each mechanism leaves the outsider a different audit problem.

A public CLOB feed can expose more immediate structure than an AMM pool:

- best bid and best ask (`l2Book`)
- spread and visible depth around mid (derived from `l2Book`)
- recent fills (`recentTrades` — short window; 10 trades returned for BTC in this probe)
- funding and open interest (`metaAndAssetCtxs`)
- 24h notional volume (`dayNtlVlm`)
- fee schedule (documented in API; not re-derived here)

The missing side is still important.

The book shows posted depth, not why it was posted, whether a maker intends to stay, or queue priority. On a perp venue, margin and risk-engine state sit alongside the ladder. Liquidation decision paths are only partly visible; the rest stays outside the artifact.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-07-19-market-without-amm-pool/fig3_observability_boundary.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-07-19-market-without-amm-pool/fig3_observability_boundary.png"
         alt="Three-column flow map: public API fields, metrics derived by an outsider, and state outside the artifact"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 4.</strong> What an outsider can reconstruct from the book. Left: fields returned by public Hyperliquid <code>info</code> endpoints in this probe. Center: metrics an outsider can derive (spread, visible depth, premium, fill window). Right: state that stays outside the artifact, including maker intent, queue priority, private inventory or hedging, liquidation paths, and account-specific terms.
  </div>
</div>

CLOB data is granular and incomplete at the same time.

***

## Dynamic fees change the AMM defense layer

AMMs are not standing still. [Uniswap v4 hooks](https://docs.uniswap.org/contracts/v4/overview) and dynamic-fee pools make that clear. The old pool design treated the fee as a mostly fixed parameter. The newer design space lets the pool react: a hook can update fees before a swap, add custom accounting, or alter behavior around the swap path. Official docs position v4 hooks as a way to customize pool behavior—not as a path to turn the pool into an order book.

That matters because many AMM failures land on the LP side. The pool offers inventory through a deterministic rule. If the outside price moves first, informed flow can trade against stale inventory. If liquidity is concentrated in the wrong range, the LP absorbs the repricing. If routing or MEV makes the flow toxic, the fee may not compensate the inventory risk. [Part II]({{ site.baseurl }}/2026/07/14/before-mev-build-the-pool.html) measured that tension through execution drag, arbitrage residual, and fee-versus-LVR.

Dynamic fees and hooks are one response—Part IV will run that defense layer in simulation. Here the point is narrower.

**Dynamic fees are not an AMM victory lap. They are evidence that the old fixed-fee pool was under-defended against toxic flow.**

They do not make the pool into a CLOB. They make the pool's defense layer more active.

On a CLOB, liquidity is already active—makers quote, cancel, repost, hedge, or leave. Failure shows up in stale quotes, queue games, and liquidation parameters more than in a passive curve being picked off.

Where loss lands depends on the mechanism. In an AMM, defense increasingly sits in fees, hooks, and LP strategy. In a CLOB, it sits in maker behavior, margin rules, and liquidation logic—and much of that is only partly visible from outside.

***

## The risk surface changes too

[Part II]({{ site.baseurl }}/2026/07/14/before-mev-build-the-pool.html) stayed inside AMM mechanics: whether fees cover passive inventory being repriced by arbitrage.

AMM failure tends to land on **LP inventory**—stale prices, LVR, range placement, toxic flow, sandwich and routing effects, and whether hooks or dynamic fees actually defend the pool.

CLOB failure tends to land on **active market making**—queue priority, cancellation latency, bad quotes, liquidation cascades, and risk-engine parameters. A perp CLOB adds funding, open interest, margin, and liquidation on top of the book.

Fixed-fee pools are fine for long-tail spot until volatility or toxic flow arrives. Dynamic fees help only if the oracle or proxy is right and the hook is not gamed. Books work when makers stay; they break when makers leave or the risk engine misfires.

**AMM and CLOB expose different slices of the market and lose money in different places.** Both leave something outside the artifact.

***

## Closing

A market can form without an AMM pool if there is posted depth, matching, and risk infrastructure behind the book. I would not read this probe as industry-wide migration. It shows what becomes visible when the forming object is book-shaped.

The book-shaped side is inspectable enough to audit—incomplete, but not hypothetical. That changes where loss lands and which failures stay inside the artifact.

The question I keep returning to: **where does the mechanism fail, who absorbs the loss, and what can an outsider verify?**

For an AMM, start with reserves and swaps, then fees and hooks. For a CLOB, start with the book and whatever funding/OI the API returns; assume maker intent and liquidation paths are partly missing.

The pool is not always the object. The audit problem remains.

***

## Appendix: source

- **Part I:** [The token appeared twice. The AMM market formed once.]({{ site.baseurl }}/2026/07/12/the-same-token-is-not-the-same-market.html)
- **Part II:** [Before MEV, I Built a Rust AMM Lab to Measure Pool State.]({{ site.baseurl }}/2026/07/14/before-mev-build-the-pool.html)
- [Reproducibility gist](https://gist.github.com/egpivo/2da1db905a09cbf9e2b83840eee5fbf9)
— DeFiLlama fees and Hyperliquid `info` probe.
