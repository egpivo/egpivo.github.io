---
layout: post
title: "When the Fee Switch Turns On, Does Liquidity Walk Away?"
date: 2026-08-02
tags: [DeFi, DEX, Ethereum, Blockchain, Web3, Statistics]
image: /assets/2026-08-02-protocol-fee-liquidity/hero.png
math: true
math_numbered: false
---

*[The pool series]({{ site.baseurl }}/2026/07/14/before-mev-build-the-pool.html) measured one layer at a time; [dynamic-fee simulations]({{ site.baseurl }}/2026/07/21/dynamic-fees-amm-signal-matters.html) asked whether state can price toxic flow. **Part V** tests a different margin: what happens to liquidity when the protocol—not the trader—gets a larger share of the fee.*

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-08-02-protocol-fee-liquidity/hero.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-08-02-protocol-fee-liquidity/hero.png"
         alt="Schematic: trader pays unchanged posted fee; fee income splits between LP take-rate and protocol treasury after UNIfication"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Overview.</strong> The trader-facing swap fee stays fixed; the fee split changes. LP take-rate falls from ρ to 1 − κ, while the protocol keeps the rest. Schematic only—not measured flows.
  </div>
</div>

***

Uniswap's UNIfication package turned a long governance debate into an on-chain take-rate cut. After the December 2025 vote, part of swap fees routed away from LPs into a protocol-fee system tied to UNI burns. Traders still paid the posted tier. LPs kept a smaller share.

The finance question is simple:

**If you cut LPs' take, does their capital leave?**

Formally, it is whether LP capital tolerates a new protocol claim on its fee income—the liquidity-supply margin this paper measures.

Most AMM fee debates mix at least four channels: fee revenue, adverse-selection loss (loss-versus-rebalancing, LVR), routing response, and whether LPs add or withdraw capital. Simulator papers often freeze the last channel and optimize the first three. Fixed-fee Uniswap v3 history cannot separate them either—the posted swap fee does not move within a pool, and public logs do not reveal counterparty types or the router's full choice set.

For measurement, the fee switch is a relatively clean shock on the LP side. Executed after governance on **2025-12-28**, it carved a protocol fee out of LP fee income on a large set of v3 pools—**1/4** of LP fees on 1 bp and 5 bp tiers, **1/6** on 30 bp and 100 bp tiers—while leaving **trader-facing swap fees unchanged**. That is a take-rate cut, not a spread change.

In a [new paper](https://arxiv.org/pdf/2607.08525) I estimate the short-run liquidity-supply response using a matched-overlap event-study difference-in-differences design on a frozen on-chain panel. The headline is a **non-detection**: no large average withdrawal of active liquidity or local depth in the ±8-week window after activation, and the more sharply estimated participation margins—LP entry, exit, unique-LP count, same-block JIT share—also show no detectable move. In plain terms: if LPs reacted, it was not at a scale this design can clearly see. That is not proof that LPs do not care. It is evidence that, at this resolution, a real protocol-wide take-rate cut did not empty the pools along the margin that fee-controller models often freeze.

***

## What the shock moved

Governance proposed the package in November 2025; the vote passed **2025-12-25**; execution followed the timelock on **2025-12-28**. On chain, activation appears as a burst of `SetFeeProtocol` events—**2,638** canonical Uniswap v3 pools in one batched burst starting **2025-12-27 20:51 UTC**, with tier-assigned intensity applied without exception inside the burst.

The empirical design treats each pool's **on-chain activation timestamp** as event time $t_0$, not the governance calendar date. Treatment $D_i$, intensity $\kappa_i \in \{1/4, 1/6\}$, and event week all come from those events. Fork pools emitting the same signature are excluded by a canonical-factory filter.

Coverage followed fee revenue, not raw volume alone. Some high-volume pools stayed untreated because inclusion tracked realized fee income at the list margin—a selection rule the design matches on rather than assumes away.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-08-02-protocol-fee-liquidity/fig01_activation_funnel.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-08-02-protocol-fee-liquidity/fig01_activation_funnel.png"
         alt="Funnel from 2,638 treated v3 pools through eligibility filters to 779-pool estimation sample"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 1.</strong> Sample funnel from on-chain <code>SetFeeProtocol</code> activation to the matched ±8-week estimation panel: 2,638 activated v3 pools → 779 treated pools, matched to 303 low-exposure controls. Filters were fixed before post-period estimation.
  </div>
</div>

The outcome panel is built from normalized Swap, Mint, Burn, and Collect logs, with pool state reconstructed from ordered events and depth measured in ±1%, ±2%, and ±5% bands around mid. Primary outcomes are **time-weighted active liquidity** and **local depth**; secondary outcomes track LP participation, composition, same-block JIT share, and collected amounts. Volume and native LP fee income are tested as feedback margins—they are never main-specification controls, because conditioning on them would absorb the response the design is trying to measure.

Before activation, the forecast was mostly model-driven: [Gauntlet's 2024 protocol-fee analysis](https://www.gauntlet.xyz/resources/uniswap-protocol-fee-report) framed a revenue–liquidity–volume tradeoff, and governance participants raised the same concern in plainer terms—if LP earnings are diluted, capital may migrate. After UNIfication, one part of that forecast became observable on the pools that mattered for fee revenue.

***

## Which channel the design identifies

LP welfare in any accounting period mixes fee revenue from arbitrage, fee revenue from ordinary flow, and LVR. Routing and liquidity supply act on those terms from outside. Many simulations improve LP welfare on paper. But if they hold liquidity fixed, they shut down the margin this paper measures.

Call the liquidity-supply response kernel **$K_L$**: the finite-horizon path of active liquidity, depth, and related LP-supply outcomes after a take-rate change. The protocol-fee switch identifies $K_L$ because $\rho_{it}$ moves while the posted trader-facing fee $c_i$ stays fixed. It does **not** identify trader-facing dynamic-fee protection—$c_i$ never varies, and trader types plus router decision sets are latent in public data.

The estimand is a matched-overlap average treatment effect on the treated (ATT) in event time, estimated as

$$
Y_{it} = \alpha_i + \delta_t + \sum_{k \neq -1} \beta_k \mathbf{1}[t - t_{0i} = k]\, D_i + \text{(pre-treatment baseline interactions)} + \varepsilon_{it},
$$

with pool and week fixed effects, reference week $k = -1$, and inference clustered at the token-pair level. Identification rests on **dynamic parallel trends in untreated increments** for matched low-exposure controls—not on level balance. Matching narrows the pre-period fee-revenue gap (standardized mean difference **1.19 → 0.84**) but leaves residual imbalance on the selection margin; credibility comes from pre-trend gates, placebo dates, Honest-DiD bounds, and caliper robustness, not from pretending treated and control pools looked identical before the switch.

***

## What the event study shows

In the primary ±8-week window, joint lead tests do not reject parallel pre-trends for active liquidity (**p = 0.91**) or local depth at the ±2% band (**p = 0.25**). Post-period coefficients stay inside confidence intervals that include zero throughout. Depth follows the same pattern: pooled post ATT **[−2.02, 1.27]** on the asinh scale. Inference clusters at the token-pair level (1,013 clusters); reference week is **k = −1**.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-08-02-protocol-fee-liquidity/fig03_main_event_paths.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-08-02-protocol-fee-liquidity/fig03_main_event_paths.png"
         alt="Event-study coefficients for time-weighted active liquidity with 95% confidence intervals; intervals include zero post-activation"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 2.</strong> Active-liquidity event-study path. Pre-trends pass cleanly (p = 0.91), and post-activation intervals include zero throughout. The pooled post ATT is [−1.11, 0.33] on the asinh scale—an identified non-detection, not a precise zero.
  </div>
</div>

Read the magnitudes carefully. On the asinh scale, the active-liquidity interval implies a multiplicative range of roughly **[0.33, 1.39]** against an 80% minimum detectable effect near **1.03**. Depth bands are wider (MDE near **2.35**). The design rules out only **very large** average short-run withdrawals; moderate reallocation could still be there. Participation outcomes are the sharper evidence: entry, exit, unique-LP, and JIT-share nulls carry MDEs near **0.1** asinh units (roughly ±10% multiplicatively).

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-08-02-protocol-fee-liquidity/fig04_precision_mde.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-08-02-protocol-fee-liquidity/fig04_precision_mde.png"
         alt="Aggregate post-period ATT intervals versus MDE80 for liquidity and participation outcomes"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 3.</strong> Precision split. Participation outcomes are sharply estimated; active liquidity and depth are much wider. The design rules out large short-run exits, not moderate reallocation.
  </div>
</div>

Not every outcome gets the same label. Token-1 volume (joint pre-trend **p = 0.014**) and native LP fee income (**p = 0.007**) **fail** the parallel-trends gate—unsurprising, since they sit on the fee-revenue selection margin the matching covariate targets. Their post CIs still include zero, but the causal label is void under the pre-specified gate. A pre-registered auxiliary factor-model route for volume also failed validation. The fee-income-per-active-liquidity ratio is degenerate in the reconstructed panel.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-08-02-protocol-fee-liquidity/fig05_outcome_gate_map.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-08-02-protocol-fee-liquidity/fig05_outcome_gate_map.png"
         alt="Identification gate map routing outcomes to identified-null versus descriptive dispositions"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 4.</strong> Outcome routing by the pre-specified gate. Liquidity, depth, and participation pass and receive an identified-null reading; token-1 volume and native LP fee income fail pre-trends and remain descriptive.
  </div>
</div>

***

## What on-chain data can—and cannot—settle

The credible part of the claim is **replayability**. Treatment indicators, intensities, event times, unit roles, and outcomes are deterministic functions of raw logs and fixed reconstruction rules, checked into a frozen panel with hash manifests before estimation. That matters in DeFi: the design is only as strong as the objects entering it.

The boundary is equally important. Public swap receipts show **landed** routes, not the router's full choice set. Swap counterparties are addresses, not labeled arbitrageurs versus noise traders. Fee-revenue attribution into arbitrage versus fundamental flow is not identified from logs alone—and neither is any counterfactual **dynamic fee** rule that would move $c_i$ within a pool. The switch estimates one real channel ($K_L$) and marks the rest as model-conditioned or non-estimand.

For fee-controller evaluation, the implication is narrow but concrete. Papers that freeze liquidity supply while optimizing fees or LVR assume away a margin that **can** be measured when governance moves take-rates. The December switch does not tell you whether dynamic fees would have protected LPs better. It does tell you that a protocol-wide LP pay cut, on the pools that mattered for fee revenue, did not trigger a large short-run liquidity exit at the depth bands traders actually hit.

***

## Closing

The fee switch was a value-accrual experiment, but the measurable object here is narrower: the short-run liquidity-supply response **$K_L$** to a take-rate cut with posted swap fees held fixed.

Under this ±8-week window and these depth bands, the result is an identified non-detection—not a proof that LPs are indifferent. Participation margins are sharply null; active liquidity and depth are wide enough to miss moderate reallocation. Volume and native LP fee income fail the pre-trend gate and stay descriptive.

The next observables are longer horizons, cross-venue reallocation, and staged rollout waves on L2s and v4—not reasons to over-read a short-window null. If capital does eventually migrate, the first place to look is whether depth moved on competing venues for the same token pairs, not whether one aggregate ATT happened to cross zero by week eight.

***

## Appendix: sources and reproducibility

**Paper and code:** Wang, Wen-Ting (2026). *Causal Effects of Protocol-Fee Changes on Liquidity Provision in Automated Market Makers.* [arXiv:2607.08525](https://arxiv.org/pdf/2607.08525) — code and frozen panel at [egpivo/amm-lab](https://github.com/egpivo/amm-lab).

**Primary sources:** [UNIfication governance proposal](https://gov.uniswap.org/t/unification-proposal/25881); on-chain `SetFeeProtocol` events (Dec 2025 activation burst); [protocol fee docs](https://docs.uniswap.org/contracts/v3/reference/deployments/ethereum-deployments#protocol-fees); pre-activation forecast: [Gauntlet, 2024](https://www.gauntlet.xyz/resources/uniswap-protocol-fee-report).

**Background reading:** LVR (Milionis, Moallemi, and Roughgarden, 2022, [arXiv:2208.06046](https://arxiv.org/abs/2208.06046)); dynamic-fee theory not identified here (Campbell, Bergault, Milionis, and Nutz, 2026, [arXiv:2606.21769](https://arxiv.org/abs/2606.21769); Baggiani, Herdegen, and Sánchez-Betancourt, 2026, [arXiv:2603.09669](https://arxiv.org/abs/2603.09669)); event-study DiD method (Sun and Abraham, 2021, [doi:10.1093/restud/rdab034](https://doi.org/10.1093/restud/rdab034); Roth, 2023, [doi:10.1093/restud/rdad016](https://doi.org/10.1093/restud/rdad016)).

**Series:** [Part I]({{ site.baseurl }}/2026/07/12/the-same-token-is-not-the-same-market.html) · [Part II]({{ site.baseurl }}/2026/07/14/before-mev-build-the-pool.html) · [Part III]({{ site.baseurl }}/2026/07/19/when-the-market-forms-without-an-amm-pool.html) · [Part IV]({{ site.baseurl }}/2026/07/21/dynamic-fees-amm-signal-matters.html) · Part V (this post) · [related: The Cheapest Trade Is Not Always the Safe Equilibrium]({{ site.baseurl }}/2026/08/02/the-cheapest-trade-is-not-always-the-safe-equilibrium.html)
