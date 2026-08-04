---
layout: post
title: "How I Turned AMM Logs Into a Causal Pipeline"
date: 2026-08-04
tags: [DeFi, Statistics, Rust, R]
image: /assets/2026-08-04-fee-switch-panel-design/hero.png
---

*[The previous post]({{ site.baseurl }}/2026/08/02/when-the-fee-switch-turns-on-do-lps-walk-away.html) reported the headline: no large short-run liquidity exit after UNIfication. This is the methods companion—how that reading was earned by freezing the empirical object before inference.*

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-08-04-fee-switch-panel-design/hero.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-08-04-fee-switch-panel-design/hero.png"
         alt="From automated market maker (AMM) logs to causal evidence: frozen unit list, pool-week panel, R event study, causal gate"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem; line-height: 1.55;">
    <strong>Overview.</strong> Match before outcomes; infer only after the gate. Schematic pipeline—not measured flows.
  </div>
</div>

***

UNIfication moved **liquidity provider (LP) take-rate** while trader-facing swap fees stayed fixed. Posted swap-fee tiers **cᵢ** on each pool did not change; what changed was the share LPs retain per unit of liquidity supplied.

A governance shock is still not a research design. Before any post-period outcome could be interpreted, the pipeline had to reconstruct treatment and event time from logs, freeze a matched unit list blind to post-activation liquidity, rebuild outcomes only for those units, and run every outcome through the same causal gate. The [paper](https://arxiv.org/pdf/2607.08525) and Rust implementation live in [egpivo/amm-lab](https://github.com/egpivo/amm-lab); the object that matters is the **frozen panel**—typed, hashed, and match-locked before R reads it.

Difference-in-differences (DiD) was the easy step. The discipline was freezing the design before any post-period coefficient could steer it.

***

## Freeze the empirical object

The first failure mode is **leakage**: letting post-period outcomes influence who enters the sample, who counts as control, or what the counterfactual is. The Rust data layer closes that off in a fixed order, most critically in **matching**, which runs on pre-period inputs only and never sees post-period liquidity.

An early draft still mixed the steps: matching on pre-period fee revenue, then sanity-checking balance with post-period active liquidity—the standardized mean difference (SMD) looked better than it should have. That was already leakage; the fix was to hard-separate matching from reconstruction and hash `panel_units.json` before the outcome pull.

**Treatment and event time from logs.** `SetFeeProtocol` events define activation indicator **Dᵢ**, protocol share **κᵢ** (1/4 on 1 basis point (bp) and 5 bp tiers; 1/6 on 30 bp and 100 bp), and activation week **t₀ᵢ** from the event block timestamp—not the governance calendar date. Fork pools are excluded from the primary control reservoir.

**What enters the matcher.** Each pool becomes a [`Unit`](https://github.com/egpivo/amm-lab/blob/main/src/causal/matching.rs): pool id, treated flag, selection variable **s** (log pre-period realized fee revenue, not volume), fee tier, pair class, and a `low_exposure` flag from the spillover map (same unordered pair as a treated pool → spillover; one shared major token → exposed; primary controls require exposure ≤ 0.25). Reservoir pools must also be census-age, fee-revenue-positive, USD-numeraire-covered, and on the canonical Uniswap v3 factory.

| Step | Module | Output | Purpose |
|---|---|---|---|
| 1 | `matching.rs` | `matched_pairs.json` | caliper match output |
| 2 | design metadata | `panel_units.json` | unit roles frozen here |
| 3 | `panel.rs` | `PoolWeek` schema | typed row contract |
| 4 | `reconstruct.rs` | `panel_weekly_rust.csv` | pool-week outcomes |
| 5 | `adapter.rs` | role ↔ match check | Rust/R consistency check |
| 6 | artifact manifest | SHA256 per file | integrity lock |

### How we wrote the match

The core function is `nn_caliper_match` in [`src/causal/matching.rs`](https://github.com/egpivo/amm-lab/blob/main/src/causal/matching.rs). It encodes the frozen primary rule: exact strata on **(fee tier, pair class)**, nearest-neighbour on **s**, caliper **0.5** log-points, **k ≤ 3**, with replacement. No outcome field exists on `Unit`—the matcher cannot leak post-period information because it has no access to it.

```rust
pub fn nn_caliper_match(units: &[Unit], caliper: f64, k: usize) -> MatchResult {
    let controls: Vec<&Unit> = units
        .iter()
        .filter(|u| !u.treated && u.low_exposure)
        .collect();

    for t in units.iter().filter(|u| u.treated) {
        let mut cand: Vec<(f64, &&Unit)> = controls
            .iter()
            .filter(|c| c.tier == t.tier && c.pair_class == t.pair_class)
            .map(|c| ((t.s - c.s).abs(), c))
            .filter(|(d, _)| *d <= caliper)
            .collect();
        cand.sort_by(|a, b| a.0.partial_cmp(&b.0).unwrap());
        // take up to k controls; unmatched if caliper empty
    }
}
```

Three design choices are easy to get wrong and are explicit in the return type:

1. **Strata are hard filters**, not regression controls. A control in the wrong tier or pair class never enters `cand`, even if it is close on fee revenue.
2. **Unmatched treated pools are first-class output** (`unmatched_treated`), not dropped silently. They carry no counterfactual and do not enter the primary average treatment effect on the treated (ATT).
3. **With-replacement multiplicity is tracked** in `control_freq: HashMap<String, usize>`—how many treated units each control was matched to. A plain set of used controls would drop this; the estimator would then under-weight controls that serve multiple treated pools.

The module ships unit tests that pin the contract: caliper and strata respected, unmatched when no control is in-band, wrong-tier and wrong-class controls rejected, exposed controls excluded. [`smd`](https://github.com/egpivo/amm-lab/blob/main/src/causal/matching.rs) on the same scale reports balance diagnostics (fee-revenue SMD **1.19 → 0.84** after match—support improves, covariate balance does not).

**786** of 868 treated-main pools find a match; **314** distinct controls are assigned; roles freeze in `panel_units.json` before the post-period pull. The pre-registered ±8-week event window then trims the primary sample to **779** treated pools and **303** controls—long enough for a weekly liquidity response to show up, short enough to avoid drifting into unrelated regime shifts. ±6 felt tight; ±12 opened more slow-confound risk. Not uniquely correct, but the least-bad compromise on those two margins.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-08-04-fee-switch-panel-design/fig_match_flow.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-08-04-fee-switch-panel-design/fig_match_flow.png"
         alt="Flow from treated pool through exposure filters and caliper match to frozen panel_units"
         style="max-width:88%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 1.</strong> Match closes on pre-period fee revenue. `panel_units.json` freezes unit roles before outcomes are rebuilt.
  </div>
</div>

### Panel rebuild

After the unit list freezes, [`reconstruct.rs`](https://github.com/egpivo/amm-lab/blob/main/src/data/reconstruct.rs) replays normalized Swap / Mint / Burn / Collect events per pool: tick-book seed → ordered replay → weekly time-weighted active liquidity, depth at ±1/2/5%, LP lifecycle fields. Each row is a typed [`PoolWeek`](https://github.com/egpivo/amm-lab/blob/main/src/data/panel.rs) with an explicit [`UnitRole`](https://github.com/egpivo/amm-lab/blob/main/src/data/panel.rs)—`matched_treated`, `matched_control`, `unmatched_treated`, `crossvenue_fork`—so primary controls are never defined as "treated == 0."

[`adapter.rs`](https://github.com/egpivo/amm-lab/blob/main/src/causal/adapter.rs) checks roles against the match: every `MatchedTreated` / `MatchedControl` label must agree with the `MatchResult`, and no matched unit may hide under a fork or unmatched role; `panel::compare()` then row-checks the reconstructed CSV against the golden artifact. Rust doesn't decide causal labels—its job is to make the frozen object typed, auditable, and drift-resistant before R reads it.

**Why Rust for the panel layer.** Not the match logic, which is a few dozen lines either way—the bottleneck is data handling at node-RPC scale: tens of millions of log rows from Ethereum JSON-RPC, a stateful tick book, `i128` liquidity deltas, and event ordering that has to survive a re-run six months later. Rust buys typed schemas, exact integer paths where Python would round, and parity tests that fail loudly when a reconstructed column drifts.

***

## What the frozen panel hands to inference

Data engineering ends when the pool-week table is frozen. Causal inference begins when R reads it. Each row is one **(pool, week)**—not a dashboard export, but a typed schema:

| Group | Field | Meaning |
|---|---|---|
| identity (time-invariant, absorbed by the pool FE) | `pool` | address |
| | `token_pair` | unordered pair id → `cluster_key` |
| | `fee_tier` | u32 |
| design (frozen before the post-period pull) | `unit_role` | `matched_treated` \| `matched_control` \| `unmatched_treated` \| `crossvenue_fork` |
| | `match_weight w` | f64, from `MatchResult.control_freq` — 1 for treated, multiplicity for controls |
| event_time | `week` | `"YYYY-WW"`, calendar week on the frozen grid |
| | `t0_week` | `"YYYY-WW"`, `SetFeeProtocol` activation week (treated only) |
| | `rel_week k` | i32, `week_index − t0_index`; reference `k = −1` |
| outcomes (dependent variables under the causal gate) | `twl_active_liquidity` | time-weighted active liquidity |
| | `depth_1pct`, `depth_2pct`, `depth_5pct` | depth bands |
| | `lp_entry_count`, `lp_exit_count`, `unique_lp_count` | LP participation |
| | `jit_share_same_block`, `position_duration_days` | JIT = just-in-time liquidity share; position duration |
| | `vol0`, `vol1`, `lp_fee_income_native1` | token-0 / token-1 volume; LP fee income |
| inference_keys | `pool_id` | → pool fixed effect |
| | `week_id` | → week fixed effect |
| | `cluster_key` | → token-pair cluster-robust standard errors (SE) |

Volume and native LP fee income sit in `outcomes`. They are not pushed into the main specification as controls—that would absorb the response the design is trying to measure.

***

## Run the gate in R

The second failure mode is **interpretation drift**: treating every coefficient from the same event-study regression as causal. **Reported inference comes from R.** Rust [`event_study.rs`](https://github.com/egpivo/amm-lab/blob/main/src/causal/event_study.rs) reproduces point estimates as a parity check; it does not assign labels.

Once the panel is frozen, the questions are econometric: absorbed fixed effects (FE) on 17k pool-weeks, token-pair clustering, a joint pre-trend Wald test, wild cluster bootstrap ([`fwildclusterboot`](https://cran.r-project.org/package=fwildclusterboot)), and Honest-DiD sensitivity bounds ([`HonestDiD`](https://cran.r-project.org/package=HonestDiD))—maintained estimators for the failure modes a DeFi panel actually hits, run via [`fixest`](https://cran.r-project.org/package=fixest) alongside the Rust panel in `amm-lab`.

**Matched overlap, not all activated pools.** Identification rests on dynamic parallel trends in untreated increments, not post-match covariate equality; unmatched high-revenue pools are reported separately from the primary ATT.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-08-04-fee-switch-panel-design/fig_balance_smd.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-08-04-fee-switch-panel-design/fig_balance_smd.png"
         alt="Love plot of standardized mean differences before and after matching"
         style="max-width:72%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 2.</strong> Support improves; balance does not. Residual imbalance stays on the fee-revenue selection margin.
  </div>
</div>

R reads `control_freq` from the match as frequency weights on controls; the ±8-week window leaves **17,598** pool-weeks across **1,013** token-pair clusters.

**Event-study DiD:**

```r
feols(
  yt ~ i(rel, treated, ref = "-1") | pool + week,
  data = d, weights = ~w, cluster = ~cluster_key
)
```

Pool fixed effects absorb time-invariant pool traits (pair, tier, posted **cᵢ**); week fixed effects absorb market-wide shocks. Token-pair clustering respects correlated shocks across pools sharing a pair, and frequency weights preserve with-replacement matching—the same `control_freq` object tracked in Rust.

**Outcome routing.** The gate does not search for significance. It decides whether a coefficient path is allowed to receive a causal label.

The same gate rule runs for every outcome:

| Gate step | Rule |
|---|---|
| `joint_pre_trend` | Wald test on all pre-period leads; reject at pre-specified α → pre-trend fail → descriptive |
| `post_path` | β_k confidence intervals (CIs) include zero throughout the post window |
| `honest_did` | relative-magnitude bounds on outcomes that pass pre-trends |
| `placebo_dates` | pre-period fake activations |
| `caliper_robustness` | 0.25 / 0.5 / 1.0 log-point support check |

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-08-04-fee-switch-panel-design/fig_causal_gate.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-08-04-fee-switch-panel-design/fig_causal_gate.png"
         alt="Causal gate routing: pre-trend test branches outcomes to descriptive or labeled estimates"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 3.</strong> Frozen gate logic in <code>analysis_es.R</code>: pre-trend failure routes an outcome to descriptive regardless of post-period significance. Outcome-by-outcome results are in <a href="{{ site.baseurl }}/2026/08/02/when-the-fee-switch-turns-on-do-lps-walk-away.html">the previous post's gate map</a>.
  </div>
</div>

**Active liquidity** passes (joint lead test **p = 0.91**). **Depth ±2%** passes (**p = 0.25**). The sensitivity checks do not turn these paths into precise effects; the interpretation remains an identified **non-detection** (no large effect found at this resolution). The main event-study paths for liquidity and depth are in [the previous post]({{ site.baseurl }}/2026/08/02/when-the-fee-switch-turns-on-do-lps-walk-away.html)—not repeated here.

**Token-1 volume** (joint lead test **p = 0.014**) and **native LP fee income** (**p = 0.007**) fail the pre-trend gate: post-period coefficients aren't sharply different from zero, but under the frozen rule they stay **descriptive**, not causal.

### When parallel trends fail on flow outcomes

Pre-period leads drift before activation on both flow outcomes (Fig. 4, Panel A)—a parallel-trends failure on the fee-revenue selection margin at this panel's weekly resolution.

[`fpca_diagnostic.R`](https://github.com/egpivo/amm-lab/blob/main/scripts/causality/fpca_diagnostic.R) ([`fdapace`](https://cran.r-project.org/package/fdapace)) runs a functional principal component analysis (FPCA) on centered pre-period token-1 volume trajectories: treated and matched controls separate on the leading score (permutation **p = 0**; Panel B). An auxiliary factor-model (`fect`) route failed validation. Flow and fee income stay **descriptive**: the shape split is documented, not rescued.

The liquidity nulls survive a gate that flow outcomes do not. The panel is pool-week, so intraweek routing and just-in-time (JIT) liquidity collapse into weekly sums—a resolution limit if flow timing matters, not proof that flow didn't move.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-08-04-fee-switch-panel-design/fig_pt_fpca_diagnostic.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-08-04-fee-switch-panel-design/fig_pt_fpca_diagnostic.png"
         alt="Failed parallel-trend leads and FPCA shape diagnostic for token-1 volume"
         style="max-width:96%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 4.</strong> Panel A — pre-period leads that reject parallel trends. Panel B — treated/control shape split the FPCA route does not reconcile.
  </div>
</div>

***

## What the stack refuses to identify

Public logs support a reduced-form read on **K_L**—the short-run liquidity-supply response when LP take-rate **ρ** moves and posted swap fee **cᵢ** stays fixed. They do **not** identify dynamic-fee protection, since **cᵢ** never varies within a pool here, and trader type, router choice sets, and the arbitrage-versus-flow split in fee income all stay latent. Where parallel trends fail and auxiliary factor routes don't recover identification, a descriptive read may reflect **limited temporal resolution** as much as a true zero effect.

If I rebuilt this panel in a year, temporal resolution would move before the estimator.

***

## Closing

The fee switch gave the shock; the frozen panel defined the empirical object; the matched design supplied the counterfactual; the R gate decided which outcomes could carry a causal label. [The previous post]({{ site.baseurl }}/2026/08/02/when-the-fee-switch-turns-on-do-lps-walk-away.html) reports what passed that bar on liquidity—this one is the stack underneath it.

The next build isn't a fancier estimator. It's a higher-resolution panel if flow timing matters, or a cross-venue read if reallocation happens outside the matched pool set.

***

## Appendix: sources and reproducibility

**Paper and code:** Wang, Wen-Ting (2026). *Causal Effects of Protocol-Fee Changes on Liquidity Provision in Automated Market Makers.* [arXiv:2607.08525](https://arxiv.org/pdf/2607.08525) — code and frozen panel, plus diagnostics [`fpca_diagnostic.R`](https://github.com/egpivo/amm-lab/blob/main/scripts/causality/fpca_diagnostic.R) and [`fect_vol1.R`](https://github.com/egpivo/amm-lab/blob/main/scripts/causality/fect_vol1.R), at [egpivo/amm-lab](https://github.com/egpivo/amm-lab).

**Methods references:** event-study DiD (Sun and Abraham, 2021, [doi:10.1093/restud/rdab034](https://doi.org/10.1093/restud/rdab034); Roth et al., 2023, [doi:10.1093/restud/rdad016](https://doi.org/10.1093/restud/rdad016)); Honest-DiD (Rambachan and Roth, 2023, [doi:10.1093/restud/rdad018](https://doi.org/10.1093/restud/rdad018), R package [`HonestDiD`](https://cran.r-project.org/package=HonestDiD)); wild cluster bootstrap (Roodman et al., 2019, [doi:10.1093/ectj/utz015](https://doi.org/10.1093/ectj/utz015), R package [`fwildclusterboot`](https://cran.r-project.org/package=fwildclusterboot)); interference/exposure (Aronow and Samii, 2017, [doi:10.1093/biomet/asx046](https://doi.org/10.1093/biomet/asx046)); asinh transform (Bellemare and Wichman, 2020, [doi:10.1017/psrm.2019.65](https://doi.org/10.1017/psrm.2019.65)). Event studies run on [`fixest`](https://cran.r-project.org/package=fixest); pre-period shape diagnostics on [`fdapace`](https://cran.r-project.org/package/fdapace).

**Series:** [Part II]({{ site.baseurl }}/2026/07/14/before-mev-build-the-pool.html) · [Part V]({{ site.baseurl }}/2026/08/02/when-the-fee-switch-turns-on-do-lps-walk-away.html) (results this post supports) · this post (methods companion)
