---
layout: post
title: "Who Owns Execution on Solana?"
date: 2026-08-23
tags: [Solana, DeFi, Market Structure, Blockchain, Finance]
image: /assets/2026-08-23-who-owns-execution-on-solana/hero.png
math: true
math_numbered: false
---

*[Part I]({{ site.baseurl }}/2026/08/16/different-apps-same-router.html) measured retail pricing at the app. [Part II]({{ site.baseurl }}/2026/08/18/the-interface-says-dflow-can-the-transaction-prove-it.html) opened one unsigned transaction for router attribution. This piece is a seven-day probe of Jupiter’s managed `/order` path: selected-router incidence stays dispersed, but the large leave-one-out gaps sit in a few pair×size×state corners—not across the router layer as a whole.*

<div style="text-align:center; margin: 1.5rem 0 2rem;">
  <a href="{{ site.baseurl }}/assets/2026-08-23-who-owns-execution-on-solana/hero.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-08-23-who-owns-execution-on-solana/hero.png"
         alt="One leading interface; router selection stays dispersed below"
         style="max-width:96%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem; line-height: 1.55;">
    <strong>Overview.</strong> One leading interface. Router selection stays dispersed below. Selected-router incidence in a fixed production <code>/order</code> probe—not transaction volume, notional share, or landed fills.
  </div>
</div>

<!-- FINAL FREEZE: b0x_20260803. -->

---

## One Interface, Many Execution Sources

Solana liquidity sits across AMMs, books, and market makers. Most traders never see that stack. They enter through a small number of swap interfaces.

Jupiter was the largest DefiLlama-attributed Solana aggregator series in **15/15** months from May 2025 through July 2026. Those adapter series are not a mutually exclusive partition of execution flow, so they enter here only as persistent interface-level attribution—not as market share.

Jupiter is also not a single router. Its managed Meta-Aggregator `/order` path (Ultra during this collection lineage) runs a selection layer containing Metis, JupiterZ, DFlow, and OKX, and returns which label was selected. Interface adoption and selected-router incidence are different objects.

This is a fixed pair×size×time probe grid, not a draw from Jupiter’s production order flow. Each tested intent counts once regardless of notional. The router percentages below are incidence inside this experiment—not production flow share, notional share, or landed execution share.

An app can also buy execution outside that managed race. Parts I–II retain one unsigned JTX→DFlow Aggregator v4 transaction—an alternate wiring, not evidence that any one source dominates Jupiter’s internal selection.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-08-23-who-owns-execution-on-solana/figure1_execution_stack.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-08-23-who-owns-execution-on-solana/figure1_execution_stack.png"
         alt="Control layers: managed execution, router selection, venues, delivery, settlement"
         style="max-width:96%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem; line-height: 1.55;">
    <strong>Fig. 1.</strong> Where control can sit. Left: direct / embed path (measured JTX→DFlow example). Right: Jupiter managed execution layer with router selection under <code>/order</code>. Schematic only—arrows are not volume.
  </div>
</div>

---

## Jupiter Runs the Managed Execution Layer

Panel B0-extended measured selected-router incidence across **21** UTC windows (2026-08-03→08-09). Selected-router HHI stayed between **0.28 and 0.35**, with overall HHI **0.298** (effective number of routers about **3.35**). No single router label took half or more of the tested intents.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-08-23-who-owns-execution-on-solana/figure2_provider_share_over_time.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-08-23-who-owns-execution-on-solana/figure2_provider_share_over_time.png"
         alt="DefiLlama-attributed Jupiter series versus selected-router HHI"
         style="max-width:96%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem; line-height: 1.55;">
    <strong>Fig. 2.</strong> Left: DefiLlama-attributed Jupiter series (not market share). Right: selected-router HHI by probe window; dashed line = overall 0.298. Panel B is label dispersion in the fixed probe—not volume-weighted share, and not evidence of replaceability.
  </div>
</div>

The managed `/order` path decides eligibility (`excludeRouters`), compares offers, and returns amounts plus a transaction when build succeeds. This probe stops at the order stage, so the stored responses do not support router-level buildability or landing comparisons.

JupiterZ is Jupiter-operated. Metis is treated separately: Jupiter formally separated Metis v7 from the Jupiter umbrella in late 2025 while still listing Metis as a 2026 Meta-Aggregator engine. Jupiter-operated selected incidence is therefore a bound—**31.7%–55.3%**—depending on how Metis is classified.

---

## Who Gets Selected Is Not Who Matters Most

The probe: six USDC pairs × four sizes × three UTC windows/day for seven days, leave-one-out for Metis, JupiterZ, DFlow, and OKX. **21/21** windows completed; **941** stable matched sets of **1008** attempted.

**Sign convention.** Leave-one-out bps:

$$\mathrm{LOO}_r = 10{,}000 \times \left( \frac{q^{\mathrm{all}}}{q^{-r}} - 1 \right),$$

where $q^{\mathrm{all}}$ is the midpoint of the bracketing all-router quotes (`out_all_ref`) and $q^{-r}$ is the exclude-$r$ quote (`out_exclude_r`). Positive means excluding $r$ worsened measured output.

Leave-one-out estimates are conditional on brackets whose all-router endpoint drift stayed below **5** bps; high-drift brackets were dropped. On the stable sets, median $\lvert\Delta_{AA}\rvert$ is about **0.26** bps (P95 about **2.75**). Among brackets with both endpoints observable, pre-gate $\mathrm{P}(\lvert\Delta_{AA}\rvert > 5\,\mathrm{bp})$ is about **4.8%**. Stable-set $\mathrm{P}(\lvert\Delta_{AA}\rvert > 5\,\mathrm{bp})$ is censored by the gate—not a tail benchmark.

JupiterZ selection also rises in those high-drift brackets after accounting for pair composition (pair-standardized expected share about **49%**, observed about **65%**). The stable-bracket results therefore miss some states where JupiterZ is selected more often.

Across successful all-router responses (A1 and A2 pooled; n = **2014**), OKX was selected in **36.8%** of tested intents, JupiterZ **31.7%**, Metis **23.6%**, DFlow **7.8%**.

Aggregate leave-one-out medians sit near that resolution: Metis and DFlow about **0** bps, OKX about **0.1**, JupiterZ about **0.3**. Hard coverage failure was almost absent—another routing source usually returned a valid quote. A valid fallback is not always an economically close substitute. Most stable brackets have a replacement path and aggregate median effects near probe resolution. The large gaps sit in specific pair×size×fallback×state cells.

**Exclusion scope.** Docs keep Metis eligible when `excludeRouters=jupiterz`, and separately state that JupiterZ V2 MM liquidity is integrated into Metis as hops. Stored Metis `routePlan` labels never expose a `JupiterZ` hop—under either the all-router or exclude-JupiterZ arm—so the schema does not show whether embedded inventory is also disabled. No bias direction is assigned. The exclude-JupiterZ arm identifies execution-path dependence, not a clean standalone-router valuation.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-08-23-who-owns-execution-on-solana/figure3_router_wins_and_loo.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-08-23-who-owns-execution-on-solana/figure3_router_wins_and_loo.png"
         alt="Selected-router incidence versus median leave-one-out effect"
         style="max-width:96%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem; line-height: 1.55;">
    <strong>Fig. 3.</strong> Panel A: selected-router incidence on A1+A2 all-router responses (n=2014); whiskers are window-clustered bootstrap 95% intervals. Panel B: median leave-one-out effect (bps) with IQR on stable sets (n=941). Aggregate medians sit near probe resolution.
  </div>
</div>

---

## Dependence Is Concentrated by Pair, Size, and Path

Large exclude-JupiterZ effects are not a general property of the probe. They occur in two pairs: AAPLX and BONK. In the other four pairs, no stable set exceeds **5** bps.

On stable sets, exclude-JupiterZ LOO exceeds 5 bps in **60.4%** of AAPLX sets (n = 144; median **21.5** bps) and **34.2%** of BONK sets (n = 146). BONK’s median is small (~**0.7** bps), but roughly one-third of its stable sets still clear 5 bps. For SOL, USDT, JITOSOL, and CBBTC the >5 bp rate is **0%**.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-08-23-who-owns-execution-on-solana/figure4_pair_jz_exceedance.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-08-23-who-owns-execution-on-solana/figure4_pair_jz_exceedance.png"
         alt="Share of sets with exclude-JupiterZ LOO above 5 bp by pair"
         style="max-width:96%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem; line-height: 1.55;">
    <strong>Fig. 4.</strong> Large exclude-JupiterZ effects are concentrated by pair. Share of stable sets with LOO &gt; 5 bp under <code>excludeRouters=jupiterz</code>.
  </div>
</div>

The AAPLX cell is the maximum of 24 pair×router medians; it was identified post hoc. The **21.5** bp AAPLX median sits far above its **0.05** bp local drift median—roughly six times the pair-specific P95 full-bracket drift (**3.39** bps). Leave-one-day-out medians stay in **16.6–30.6** bps.

The AAPLX gap is strongly size-dependent. Medians: about **0** bps at \$100 (n = 39); **19** bps at \$1k (n = 41); **185** bps at \$10k (n = 36); about **16,800** bps at \$100k (n = 28). The \$100k cell is also where the extreme-value audit concentrates.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-08-23-who-owns-execution-on-solana/figure5_aaplx_size_gradient.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-08-23-who-owns-execution-on-solana/figure5_aaplx_size_gradient.png"
         alt="AAPLX exclude-JupiterZ median LOO by tested order size"
         style="max-width:96%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem; line-height: 1.55;">
    <strong>Fig. 5.</strong> AAPLX dependence rises with tested order size. Median exclude-JupiterZ LOO (bps, log scale) versus local $\lvert\Delta_{AA}\rvert$ median; n = 39 / 41 / 36 / 28 by size.
  </div>
</div>

Hard coverage and replacement quality are different objects. Among stable sets where JupiterZ won A1, Metis and OKX fallbacks typically preserve the all-router reference (median remaining output ~ **1.00**). The extreme AAPLX tail concentrates in the rare JupiterZ→DFlow fallback (n = 18), where the median fallback returned about **one-fifth** of the all-router reference (median remaining-output ratio ~ **0.20**). The leave-one-out result measures the quality of the available replacement path—not a standalone price tag on JupiterZ.

The sharper calendar contrast is weekday versus weekend, not U.S. hours alone: weekday U.S.-hours overlap median **24.4** bps (n = 30); weekday off-hours **54.2** bps (n = 68); weekend **0.01** bps (n = 46), though roughly **28%** of weekend observations still exceed 5 bps. Onchain xStocks are documented as 24/7 tradable; no depth or market-closure mechanism is claimed here.

---

## Closing

In this fixed `/order` probe, Jupiter controls the managed entry and comparison layer. Selected-router frequency is a poor proxy for economic dependence: most single-source exclusions have aggregate medians near within-bracket resolution, and a valid fallback quote usually exists.

The large gaps sit in corners of the test grid. Under `excludeRouters=jupiterz`, only AAPLX and BONK produce >5 bp events. On AAPLX, the effect rises sharply with tested order size and differs between weekday and weekend observations. The extreme tail also depends on which fallback path remains available.

Because that exclusion may not isolate a clean standalone router, these results identify execution-path dependence rather than a standalone valuation of JupiterZ. They are order-stage selection and quote-sensitivity results from a fixed probe—not production-volume shares or landed fills.

---

## Appendix

- **Sample.** Production Meta-Aggregator `/order`, `b0x_20260803` (2026-08-03→08-09). Matched set = A1 + 4 randomised LOO + A2. **1008** attempted → **941** stable ($\lvert\mathrm{A1}-\mathrm{A2}\rvert$ < **5.0** bps; span ≤ **20** s). Pre-gate high-drift rate ~**4.8%**.
- **Resolution.** Stable $\lvert\Delta_{AA}\rvert$: median ~0.26 bps, P95 ~2.75. Pre-gate (n=1006): median ~0.29, P95 ~4.39. Stable $\mathrm{P}({>}5)/\mathrm{P}({>}10)$ are gate-censored.
- **Denominators.** Incidence pools A1+A2 (n=**2014**). Substitution counts use the A1 winner on each stable set (n=**941**).
- **Scope.** Metis affiliation unresolved (Jupiter-operated bound **31.7%–55.3%**). JupiterZ exclusion semantics unresolved. No landed fills; no production-volume read. Diagnostics: [empirical package](https://gist.github.com/egpivo/c36f32551f25a94ebaf97a134f7571fb).
- Part I: [Different Apps, Same Router]({{ site.baseurl }}/2026/08/16/different-apps-same-router.html) · Part II: [Can a Solana Transaction Prove the Router?]({{ site.baseurl }}/2026/08/18/the-interface-says-dflow-can-the-transaction-prove-it.html) · [Jupiter `/order`](https://developers.jup.ag/docs/swap/order-and-execute)
