---
layout: post
title: "DFlow Shows Where Solana Trading Is Going. Retail Pricing Still Happens at the App."
date: 2026-08-16
tags: [Solana, DeFi, Market Structure, Blockchain, Finance]
image: /assets/2026-08-16-different-apps-same-router/hero.png
---

*As execution becomes an embedded wholesale service, synchronized JTX quotes show that app-level fees still shape the price offered before signing.*

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-08-16-different-apps-same-router/hero.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-08-16-different-apps-same-router/hero.png"
         alt="The emerging Solana trading stack: app layer, DFlow wholesale execution, liquidity venues, authorization, delivery, settlement"
         style="max-width:96%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem; line-height: 1.55;">
    <strong>Overview.</strong> DFlow represents an emerging wholesale execution layer between customer-facing products and Solana liquidity. The diagram shows the functional framework examined here, not measured market share or exclusive control.
  </div>
</div>

---

## DFlow as a Wholesale Execution Layer

Trading interfaces on Solana keep multiplying. Execution need not. An app, a wallet, or an agent can present the same swap while the routing and transaction construction underneath is one shared service. DFlow is the named case: one API for quoting, routing, and building the transaction, sitting behind many customer-facing surfaces ([docs](https://pond.dflow.net)).

Whether that arrangement is large enough to matter depends on which data universe you accept. Fig. 1 reconstructs DFlow’s share of Solana aggregator volume from DefiLlama, the public series available for this window. Read it as a within-source adoption index rather than a market-share estimate. What it shows is a rise, not a takeover, on numbers another source counts differently.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-08-16-different-apps-same-router/figure_solana_aggregator_share_over_time.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-08-16-different-apps-same-router/figure_solana_aggregator_share_over_time.png"
         alt="Monthly DFlow, Jupiter, Titan, OKX, and Other shares within a DefiLlama Solana aggregator reconstruction from May 2025 to July 2026, with MoonPay acquisition month shaded and JTX panel marked"
         style="max-width:96%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem; line-height: 1.55;">
    <strong>Fig. 1.</strong> DFlow share within a <a href="https://defillama.com/protocols/Aggregators" target="_blank" rel="noopener noreferrer">DefiLlama</a> Solana aggregator reconstruction (May 2025–Jul 2026); Blockworks’ public series and Dune were unavailable. Green column marks the MoonPay acquisition month (May 2026); dashed line marks the JTX quote panel (2026-07-28/29). Within this source, DFlow rises from near zero, peaks at 20.6% (Sep 2025) and 26.2% (May 2026), then retreats, while Jupiter remains majority throughout. These levels run materially above the Blockworks figures reported elsewhere: 9.75% in September 2025, roughly 5%–10% in the months before May 2026 (<a href="https://fortune.com/2026/05/05/moonpay-acquires-solana-100m-all-stock/" target="_blank" rel="noopener noreferrer">Fortune</a>). The two sources do not share a verified common denominator.
  </div>
</div>

Integration is a separate claim from share, and the numbers for it are company-reported. [MoonPay](https://www.moonpay.com/newsroom/dflow) reports more than **500** applications, roughly **10 million** monthly transactions, and Q1 2026 volume above **$12 billion**, across surfaces including Coinbase, Phantom, Solflare, and Kamino. The same interface covers quoting, signing, and submission for apps, wallets, and agents ([docs](https://pond.dflow.net/introduction); [Helius](https://www.helius.dev/docs/agents/skills/dflow)).

None of this makes DFlow Solana’s Uniswap, and it does not need to be. The wholesale-execution question only requires that an ordinary retail trade plausibly passes through a layer the trader never sees. Adoption is an architecture fact. Once execution becomes an abstract middle layer, the interesting question is a finance question: not who routes the order, but where the retail price is still formed.

---

## The JTX Test

JTX makes that question observable. It is a customer-facing Solana trading surface that labels DFlow as its router.

The measured object is pre-trade price dispersion: matched, standardized intents that receive different quoted outputs across interfaces. A difference sampled minutes apart is a difference between moments; a difference sampled inside a window of under two seconds is a difference between offers.

JTX’s quote is captured alongside Jupiter’s public quote in that window. Jupiter plays the role an outside option plays in the execution-quality literature: a contemporaneous alternative offer at decision time ([Schwarz et al., 2025](https://doi.org/10.1111/jofi.13467); [Bessembinder, 2003](https://www.acsu.buffalo.edu/~keechung/MGF743/Readings/Issues%20in%20assessing.pdf)). It is not the market’s latent true price, and a gap against it is not proof that best execution failed. Nor is this two DFlow-integrated apps compared: Jupiter is an independent public surface, and nothing here claims the two share a router.

Across five pairs and three displayed fee tiers, **29 observations** classify STRONG synchronization, the largest cross-surface gap being 1.842 seconds. **In 29 of 29, the JTX quote is lower than Jupiter’s.** Against DFlow’s own no-key developer endpoint, a sensitivity reference rather than a production path, the count is 28 of 29.

All of this is pre-trade. Nothing was signed or submitted, so the panel is silent on fills, markouts, network fees, slippage, MEV, delivery, and settlement. What it measures is the offer a retail trader is shown at the moment they are shown it, which is the number they actually act on.

---

## The App Fee Enters the Quote

The first place to look is the one cost the app does display, and JTX serves it from its own backend: a passive session returned `{"feeBps":2}` on a USDC→SOL quote that also displayed “Route via DFlow” and 0.02%. The schedule is pair-specific: **1 bp** on USDC→USDT, **2 bps** on USDC→SOL and USDC→WETH, **25 bps** on USDC→JUP and USDC→XAUt0.

In 28 of 29 captured responses, that fee arrives as an input-side deduction: the shortfall between the quote’s stated input and the input that actually reaches the route reproduces each pair’s displayed tier almost exactly (method in the Appendix). The fee is not appended after the route prices the trade, it is removed before, and a small proportional haircut on the input comes back as a comparably lower quoted output. The trader meets it as a smaller number.

Four questions hide inside the word *fee*: who sets it, how it enters the offer, who bears it at quote stage, and who receives the deducted value after settlement. This evidence answers the middle two. The app labels the fee, deducts it from the input, and the trader carries it as a lower quoted output. The first and last remain open: nothing here shows that DFlow sets the schedule, identifies a separate upstream router charge, or follows the deducted units after settlement. Mechanical burden in the offer is not equilibrium incidence, and it is not retained profit ([Tax Foundation, Tax Incidence](https://taxfoundation.org/taxedu/glossary/tax-incidence/)).

Taking each observation’s displayed tier as the fee component and the remainder as residual, the **median observed gap is 2.37 bps** against a **median displayed fee of 2.00 bps**, leaving a **median residual of 0.10 bps** (IQR −0.01 to 0.54). On an aggregate absolute-gap basis, **the displayed fee accounts for 89.2% of the observed quote disadvantage across the 29 observations**. That figure is a share of total absolute gap magnitude: not an R-squared, not variance explained, not a pass-through coefficient, and not a measure of what anyone kept. Tightening the synchronization filter does not overturn the result; see the robustness note in the Appendix.

One row resists the decomposition. A $10,000 USDC→SOL capture routed entirely through BisonFi shows no detectable input-side deduction, yet a gap in line with the other 2 bp rows. It is carried at the displayed tier as a labeled approximation and left unresolved.

The one number the app does show predicts most of the disadvantage it does not show. A trader who reads the fee line has already read most of the gap.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-08-16-different-apps-same-router/figure_pair_fee_gap_residual.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-08-16-different-apps-same-router/figure_pair_fee_gap_residual.png"
         alt="Displayed fee explains most of the observed quote gap across markets; residuals by pair"
         style="max-width:96%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem; line-height: 1.55;">
    <strong>Fig. 2.</strong> Pair-level medians: displayed app fee, quote gap against the synchronized Jupiter outside option, and what the fee does not explain. JUP holds the largest positive residual (median +2.13 bps); XAUt0 is the only negative median residual on the shared 25 bp tier. Panel medians, not a fitted model; the figure does not explain tier assignment.
  </div>
</div>

---

## Same Wholesale Layer, Different Retail Prices

Most is not all, and what remains is not spread evenly.

The tiers are already an act of pricing: a twenty-five-fold spread between the cheapest pair and the most expensive, inside a single app. Why a pair sits where it does, whether liquidity, route complexity, or willingness to pay, is not identified by quote data.

The sharper point is that pairs sharing a tier do not behave alike. USDC→JUP and USDC→XAUt0 both display 25 bps. JUP carries most of the residual mass in the panel, with individual residuals reaching **+12.81 bps**; XAUt0’s median residual is small and negative, near **−0.44 bps**. Same posted fee, different quoted cost against the outside option. A posted tier is not a sufficient statistic for the retail quote difference.

The residual is market-specific, and quote JSON cannot identify its source. Separating route composition, timing, liquidity, and quote construction needs transaction-level evidence.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-08-16-different-apps-same-router/figure2_retail_quote_comparison.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-08-16-different-apps-same-router/figure2_retail_quote_comparison.png"
         alt="Displayed app fee versus quote gap against outside option; residual by pair"
         style="max-width:96%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem; line-height: 1.55;">
    <strong>Fig. 3.</strong> Observation-level support for Fig. 2. Twenty-nine synchronized quotes, 2026-07-28 to 2026-07-29. Left: log–log displayed fee versus quote gap against a fee-only benchmark (dashed line: gap equals fee, not a fitted trend). Right: residual quote gap by pair; axis capped at 3.2 bps, with two USDC→JUP points above that range (+10.15, +12.81 bps) marked. Within the 2 bp tier, median residuals differ as well (SOL +0.08, WETH +0.36 bps; WETH n=3, so the contrast is directional).
  </div>
</div>

That heterogeneity is the market-structure result. One wholesale execution framework can sit underneath retail markets that still price differently, because the layer that sets and displays the fee is not the layer that finds the route.

---

## What This Changes for Competition and Accountability

Competition in this stack is layered. Apps compete on fees and on how a quote is presented, routers compete on execution quality, venues compete on liquidity. These are separate contests: a market can proliferate on the surface while consolidating underneath, so more customer-facing apps need not mean more independent execution systems. Nothing in this panel identifies a causal link from router concentration to retail fees.

Outsourcing execution therefore does not make the retail surface price-neutral. In the measured case the app kept the largest observable lever over the offer, the displayed fee, while presenting the routing as someone else’s service. An agent submitting standardized intent to a wholesale layer inherits that same policy, with less visibility than a screen provides.

Accountability is where this becomes uncomfortable. A residual quote disadvantage could reflect app policy, route construction, venue liquidity, timing, or settlement mechanics, and quote JSON cannot allocate it among them. The fee line predicts most of an otherwise invisible gap; the residual is the part no outside observer can assign.

---

## Closing

Execution is not being taken away from apps. Outsourcing the router does not erase pricing discretion; it relocates it, and relocates the evidence with it. The routing moves into a shared layer, while the number that shapes the offer stays on the app’s own screen.

As execution moves into shared infrastructure, a trader’s screen can explain less about how a price was built, not more. The execution layer may become harder to see. The fee that shapes the offered price will not.

---

## Appendix

- **Panel.** 29 synchronized observations, 2026-07-28/29; quote-stage JSON only, nothing signed or submitted, rules fixed before the final panel. USDC→SOL (14, $100 to $10,000, incl. same-tier liquidity check), USDC→JUP (6), USDC→USDT (3), USDC→XAUt0 (3, thin liquidity), USDC→WETH (3, same-tier liquidity check). Displayed tier served by JTX’s own backend at `GET /v1/fees/tier`; UI baseline from a passive session on 2026-07-25. Input-side deduction measured by summing route legs whose input asset matches the top-level input, then differencing against the quote’s stated total input. DFlow-dev exception (28 of 29): a thin-liquidity USDC→WETH row. [Reconciled rows and audit](https://gist.github.com/egpivo/ef02813e33bf869a230321599c6ebc52)
- **Route-component association.** Rows with no DFlow-labeled route component (8 of 29) hold a median residual near zero; the 21 that carry one hold both the overall median residual and the largest outlier. An association in what the quote discloses, not a causal DFlow effect; settling it needs transaction-level evidence
- **Robustness.** Near-zero-lag DFlow-dev vs. Jupiter dispersion (316 tick pairs) is material against a 2 bp fee signal on SOL and WETH, smaller at 1 bp and 25 bp, and reflects persistent cross-surface differences, not pure timing noise. The 13 of 29 rows with sync gap <= 1.0 s move the median gap-to-fee ratio from 1.17 to 1.02; subgroups unbalanced by pair. USDC→SOL at $100 / $1,000 / $10,000 shows no monotonic size trend in median residuals. Multi-hop counting under DefiLlama adapters (Fig. 1) remains unresolved
- Transaction-lineage companion: [Can a Solana Transaction Prove the Router?]({{ site.baseurl }}/2026/08/18/the-interface-says-dflow-can-the-transaction-prove-it.html) · [JTX: Moving Up the Stack](https://x.com/minnus/article/2076693316456865917) (minnus)
