---
layout: post
title: "Dynamic Fees in AMMs: When the Signal Matters"
date: 2026-07-21
tags: [DeFi, Rust, DEX, Blockchain, Web3]
image: /assets/2026-07-21-dynamic-fees-amm-signal-matters/hero.png
---

*[Part I]({{ site.baseurl }}/2026/07/12/the-same-token-is-not-the-same-market.html) asked whether an AMM surface formed. [Part II]({{ site.baseurl }}/2026/07/14/before-mev-build-the-pool.html) ran pool state forward. [Part III]({{ site.baseurl }}/2026/07/19/when-the-market-forms-without-an-amm-pool.html) contrasted reserves with book depth. This piece runs the AMM defense layer: fixed fee vs state-responsive fee.*

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-07-21-dynamic-fees-amm-signal-matters/hero.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-07-21-dynamic-fees-amm-signal-matters/hero.png"
         alt="GBM price path with oracle-gap fee response overlaid on a constant-product pool"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
  <strong>Overview.</strong> Campbell-style CPMM simulation with interchangeable fee policies. Illustrative parameters; not calibrated to a live pool.
  </div>
</div>

***
[Part III]({{ site.baseurl }}/2026/07/19/when-the-market-forms-without-an-amm-pool.html) ended on dynamic fees as evidence that the fixed-fee pool was under-defended—not as proof that hooks beat a book. [Uniswap v4 dynamic fees](https://docs.uniswap.org/contracts/v4/concepts/dynamic-fees) make the defense layer callable: a hook can read pool state and set the fee per swap.

The design question is narrower than "can the hook observe more fields?" Under this constant-function market maker (CFMM) setup—specifically a constant-product market maker (CPMM)—does an extra field add information, or only rescale a response the invariant already implies?

I put [Campbell *et al.* (2025)](https://arxiv.org/abs/2508.08152) and [Baggiani *et al.* (2025)](https://arxiv.org/abs/2506.02869) into the same [Rust lab](https://github.com/egpivo/amm-lab). Campbell *et al.* supply the fixed-fee LP objective and the routing mechanism: when CEX trading is costly, a stale AMM can still attract fundamental flow by charging a low enough fee. Baggiani *et al.* supply the policy question—whether observation-based fees can beat a static optimum. Four policies share one `FeePolicy` interface and the same Monte Carlo paths: fixed 6 bps, fixed 10 bps, oracle-gap, and inventory-gap.

The bridge is market-making control. Campbell *et al.* define what the pool is trying to protect: fee revenue net of stale-price loss. Baggiani *et al.* change the fee from a scalar parameter into a policy over market state. A CLOB maker does this through spreads, size, cancels, and exposure limits when flow turns toxic. A programmable AMM cannot reproduce the whole book, but fee is its smallest spread-like defense.

***

## The Campbell baseline

This is a baseline check, not a fee-design breakthrough. A CEX or oracle reference moves before the pool price does. Arbitrage closes the gap; the LP absorbs LVR. Campbell *et al.* formalize that setting with arbitrageurs, fundamental traders, and a passive LP. Hedged PnL is fee revenue minus tracking error.

In the lab, `oracle_gap_bps` is pool price vs CEX price in bps—the exposure window before arb trades. `arb_delta` closes the gap each step; `hedged_pnl` records what the LP kept net of LVR.

With a 10 bps CEX fee, the optimum AMM fee lands near **6 bps**. Higher fees extract more per arb trade but widen the no-trade band and lose fundamental flow. I reproduced the sweep in Rust—1 to 100 bps on one GBM path, then 500-path Monte Carlo.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-07-21-dynamic-fees-amm-signal-matters/fig1_fee_sweep.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-07-21-dynamic-fees-amm-signal-matters/fig1_fee_sweep.png"
         alt="Panel A: hedged PnL vs AMM fee on a single GBM path. Panel B: Monte Carlo mean with shaded ±1 std band, zoomed to 1–30 bps."
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 1.</strong> The fixed-fee optimum stays near 6 bps under this setup. Going below it leaves LVR uncovered; going above it prices out flow. Panel A: one GBM path. Panel B: 500-path mean (±1 std, 1–30 bps). Source: <a href="https://github.com/egpivo/amm-lab"><code>amm-lab</code></a>.
  </div>
</div>

Below 6 bps, arb keeps trading but the fee does not cover LVR. Above 6 bps, the pool keeps some arb revenue but loses fundamental flow to the CEX.

***

## Fee as a policy

Dynamic fees are control laws over observations. Production hooks override the fee in `beforeSwap` or via `updateDynamicLPFee`. The simulation uses the same surface: observe state, choose fee, run arb and fundamental trades.

```rust
pub trait FeePolicy {
    fn name(&self) -> &'static str;
    fn fee(&mut self, obs: &FeeObservation) -> f64;
}
```

`FeeObservation` carries oracle gap (bps), inventory skew, and recent realized volatility. In this comparison, realized volatility is recorded but not used in the fee rule. Each step calls `policy.fee(&obs)` before trades execute.

`FixedFeePolicy` reproduces the Campbell baseline. In these runs, fee is stored as a fraction (`1 bps = 0.0001`, so `base_fee = 0.0006`). The two dynamic policies are:

- **OracleGapFeePolicy:** `fee = base_fee + 0.04 × |oracle_gap_bps| / 10 000`, clamped to [1, 20] bps
- **InventoryGapFeePolicy:** `fee = base_fee + 0.01 × |inventory_skew|`, clamped to [1, 20] bps

Oracle-gap charges more when the pool has drifted from the CEX. Inventory-gap charges more when reserve composition is imbalanced. Same interface; different stated signal.

***

## Oracle-gap beats fixed 6 bps on every path

Across 500 paired Monte Carlo paths, oracle-gap beat fixed 6 bps on **every path**: mean Δ hedged PnL **+15.2**, minimum **+8**.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-07-21-dynamic-fees-amm-signal-matters/fig2_policy_comparison.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-07-21-dynamic-fees-amm-signal-matters/fig2_policy_comparison.png"
         alt="Dot-interval chart showing hedged PnL p05–mean–p95 for four policies across 500 paths."
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 2.</strong> Fixed 10 bps underperforms for the same reason as Fig. 1: it overcharges and loses flow. Both dynamic policies beat fixed 6 bps, but only oracle-gap delivers material lift (p05–mean–p95, 500 paths).
  </div>
</div>

Each policy runs against the same price path and the same demand draws. The market did not get easier or harder for one policy. Statistically, Fig. 3 asks how much PnL changed when only the fee rule changed.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-07-21-dynamic-fees-amm-signal-matters/fig3_paired_delta.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-07-21-dynamic-fees-amm-signal-matters/fig3_paired_delta.png"
         alt="Histograms of per-path delta hedged PnL vs fixed 6 bps for oracle-gap and inventory-gap policies."
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 3.</strong> Same sign, different magnitude: oracle-gap adds +8 to +22 per path; inventory-gap adds +0.5 to +2.5 (500 seeds). The policy ranking is not close.
  </div>
</div>

Inventory-gap also beat fixed 6 bps on every path, but mean gain was only **+1.8**—roughly one-eighth of oracle-gap's advantage.

***

## Inventory skew collapses into oracle gap

Inventory skew is not a new signal here. In a CPMM, both fields are monotone functions of the same quantity—deviation between AMM and CEX price:

```rust
let oracle_gap_bps  = (P_amm − P_cex) / P_cex × 10 000;
let inventory_skew  = (P_amm − P_cex) / (P_amm + P_cex);
```

When arb keeps the pool near the CEX price, `P_amm ≈ P_cex` and the skew denominator is approximately `2 × P_cex`:

```
inventory_skew ≈ oracle_gap_bps / 20 000
```

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-07-21-dynamic-fees-amm-signal-matters/fig4_signal_collinearity.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-07-21-dynamic-fees-amm-signal-matters/fig4_signal_collinearity.png"
         alt="Scatter plot of oracle gap (bps) vs inventory skew × 10 000, showing near-perfect linear relationship."
         style="max-width:72%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 4.</strong> These variables are effectively the same coordinate in this model. Near-linear fit (slope ≈ 0.5, Pearson r = 1.000 to four decimals) shows inventory-skew policy is mostly oracle-gap policy with lower gain.
  </div>
</div>

`InventoryGapFeePolicy` applies the same signal at lower gain—the step-level audit in the repo shows why. The +1.8 mean gain is amplitude, not a different signal.

This is specific to constant-product pools where arb continuously aligns pool price with the external reference. In pegged-pool designs, reserve imbalance can move while marginal price stays near peg, so inventory can carry information not captured by current oracle gap. Curve's `offpeg_fee_multiplier` is aimed at that regime, not at CPMM-style rescaling.

***

## What a hook should test next

If the feature is reserve-derived in CPMM, assume redundancy until shown otherwise. Current oracle gap is the primitive; inventory skew, reserve ratio, and pool price are functions of it. Adding them does not expand the information set. It rescales the response.

The next candidate is not another reserve-derived field. It is path-derived or external:

- **Realized volatility**: not recoverable from instantaneous CPMM state
- **Order-flow imbalance**: directional pressure within a block, visible before the swap executes
- **Oracle latency**: time since last reliable external update
- **Toxic-flow proxy**: share of recent volume from arb vs fundamental demand

These break collinearity because the invariant does not encode them. The test: does the feature add information beyond current oracle gap under the same path and demand assumptions?

***

## Closing

[Part II]({{ site.baseurl }}/2026/07/14/before-mev-build-the-pool.html) ran two settings: a seeded path where fees beat LVR, and a deterministic shock where LP-vs-hold stayed negative. The policy layer matters here: oracle-gap dynamic fees beat fixed 6 bps on every sampled path, while inventory-gap adds only a small lift because the two signals are nearly collinear.

That does not prove dynamic fees rescue LP economics in production. The run uses illustrative parameters (σ = 4%, μ = 0, 100 Y fundamental demand per step, CEX fee = 10 bps). The gain still depends on multiplier, demand, and volatility regime, even if the signal relationship is structurally redundant under the CPMM invariant.

Production should be stricter than simulation. This reduced-form world has no gas auction, block latency, queue dynamics, or LP repositioning cost. A hook that freely explores fee settings with LP capital can become statistical gambling once those frictions enter. The safer version starts from a champion rule, deviates only when edge clears cost and uncertainty, and can abstain.

Under CPMM, most fee innovation is control law, not information. The next test is strict: add a path-derived feature (realized volatility or order-flow proxy), check orthogonality to oracle gap on the same paths, then keep it only if paired PnL improves at matched risk.

***

## Appendix: source

- **Part I:** [The token appeared twice. The AMM market formed once.]({{ site.baseurl }}/2026/07/12/the-same-token-is-not-the-same-market.html)
- **Part II:** [Before MEV, I Built a Rust AMM Lab to Measure Pool State.]({{ site.baseurl }}/2026/07/14/before-mev-build-the-pool.html)
- **Part III:** [Hyperliquid Shows What a Market Looks Like Without an AMM Pool.]({{ site.baseurl }}/2026/07/19/when-the-market-forms-without-an-amm-pool.html)
- **GitHub Repo:** [amm-lab](https://github.com/egpivo/amm-lab), Campbell simulation and dynamic-fee policy runs
- **Campbell:** Campbell, S., Bergault, P., Milionis, J., and Nutz, M. (2025). [arXiv:2508.08152](https://arxiv.org/abs/2508.08152).
- **Baggiani:** Baggiani, L., Herdegen, M., and Sánchez-Betancourt, L. (2025). [arXiv:2506.02869](https://arxiv.org/abs/2506.02869).
