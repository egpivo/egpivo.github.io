---
layout: post
title: "Before MEV, I Built a Rust AMM Lab to Measure Pool State"
date: 2026-07-14
tags: [DeFi, Rust, DEX, Blockchain, RWA, Web3]
image: /assets/2026-07-14-before-mev-build-the-pool/hero.jpg
---

*Part I asked whether a public-pool surface formed. This piece opens the pool and runs its state forward.*

<div style="margin: 1.5rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-07-14-before-mev-build-the-pool/hero.jpg"
       alt=""
       aria-label="LP, Trader, Arbitrageur, AMM Pool, External reference price"
       style="width:100%; height:auto; border-radius: 8px;" />
</div>

---

[Part I]({{ site.baseurl }}/2026/07/12/the-same-token-is-not-the-same-market.html) compared canonical SPYx on Solana and Ethereum. Raydium and Orca showed substantial June volume; the one discovered Ethereum canonical pool returned **13** decoded swaps and **$43.49** in USDC notional over June 1–21. Canonical deployment was present. Executable public-pool liquidity was not observed at the same scale.

That gap was measured from the outside: venue bars, swap counts, and route classes. It did not reconstruct reserves, fee accrual, arbitrage behavior, or what an LP would have held after external repricing.

So I built a smaller [Rust lab](https://github.com/egpivo/amm-lab) and stopped before MEV. The first question was not who could sandwich a trade. It was what the pool had to expose first: reserves, fee logic, slippage guards, arbitrage, and LP accounting.

---

## How I run the lab

Each run is a TOML scenario: typed commands executed in sequence against `u128` pool state. Fee-on-input, no floating point in reserves. Each command writes the next state; each scenario writes JSON and CSV to [`data/processed/`](https://github.com/egpivo/amm-lab/tree/main/data/processed).

Two blocks share the same CPMM rules. The deterministic block has four TOML scenarios, each a point event. The stochastic block has one seeded price path. Both write artifacts to [`data/processed/`](https://github.com/egpivo/amm-lab/tree/main/data/processed); claims map via [`research/evidence_ledger.csv`](https://github.com/egpivo/amm-lab/blob/main/research/evidence_ledger.csv) (C1–C11).

```bash
cargo test --all
scripts/run_all_scenarios.sh
cargo run --release -- scenario run scenarios/<name>.toml
```

[`scripts/run_all_scenarios.sh`](https://github.com/egpivo/amm-lab/blob/main/scripts/run_all_scenarios.sh) runs all four deterministic scenarios. Scenario format: [`scenarios/README.md`](https://github.com/egpivo/amm-lab/blob/main/scenarios/README.md).

Fee-on-input ordering in [`src/swap.rs`](https://github.com/egpivo/amm-lab/blob/main/src/swap.rs) is what makes the measured cost separable from the curve:

```rust
let fee = amount_in * fee_bps as u128 / 10_000;
let amount_in_after_fee = amount_in - fee;
let amount_out = amount_in_after_fee * reserve_out
    / (reserve_in + amount_in_after_fee);
```

A slippage guard checks `amount_out >= min_out` before any state is committed.

---

I use four terms narrowly:

- **Execution drag** is the single-swap cost relative to the pre-trade pool spot: fee plus curve effect paid by the trader.
- **LP-vs-hold** is withdrawal value versus holding the original deposit through a deterministic shock.
- **Tracking error / LVR** is the path-level loss measure used in the Campbell-style run: the cost of passive liquidity while the external mark moves.
- **Hedged PnL** is fee revenue minus tracking error in the Campbell-style run.

---

## Deterministic scenarios

Four files live in [`scenarios/`](https://github.com/egpivo/amm-lab/tree/main/scenarios). Same runner, same `u128` pool. Each run fixes an input state, executes typed commands, and writes an artifact. Part I measured activity from the outside; these scenarios isolate pool-side mechanisms one at a time. They are not calibrated to SPYx.

### Trade size sets execution drag: [`price_impact_ladder.toml`](https://github.com/egpivo/amm-lab/blob/main/scenarios/price_impact_ladder.toml)

- **Input.** One 1T / 1T pool at spot 1.0. Six `SwapExactIn` runs from 100M to 250B base units (0.01% → 25% of reserves).

- **Method.** `SwapExactIn` with 30 bps fee-on-input. I call the measured quantity *execution drag*: fee plus curve effect, not slippage.

`execution_drag_pct = (execution price − pre-trade spot) / pre-trade spot`

- **Output.** [`price_impact_ladder_swaps.csv`](https://github.com/egpivo/amm-lab/blob/main/data/processed/price_impact_ladder_swaps.csv). Drag runs **0.31%** at the smallest trade to **25.30%** at 25% of pool, more than 80× the 30 bps fee floor (C1).

### Same spot, different executable depth: [`same_price_different_depth.toml`](https://github.com/egpivo/amm-lab/blob/main/scenarios/same_price_different_depth.toml)

- **Input.** Three pools, all at spot 1.0: 100B, 1T, and 10T reserves. Same trade every time: 10B base units of X.

- **Method.** Same `SwapExactIn`. Only reserves change.

- **Output.** [`same_price_different_depth_swaps.csv`](https://github.com/egpivo/amm-lab/blob/main/data/processed/same_price_different_depth_swaps.csv). Drag is **10.30%** on the shallow pool, **1.30%** on 1T, **0.40%** on 10T (C2). Part I noted that nominal and executable liquidity diverge; this run holds the trade fixed and changes only reserves.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-07-14-before-mev-build-the-pool/fig2_execution_drag.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-07-14-before-mev-build-the-pool/fig2_execution_drag.png"
         alt="Panel A: execution drag vs trade size on a 1T pool. Panel B: same 10B trade across three pool depths."
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 1.</strong> Execution drag in synthetic constant-product pools. Panel A shows the fee floor disappearing as trade size grows; Panel B shows why the same spot price can hide very different executable depth. Looking only at nominal liquidity would miss that difference. Sources: <a href="https://github.com/egpivo/amm-lab/blob/main/data/processed/price_impact_ladder_swaps.csv"><code>price_impact_ladder_swaps.csv</code></a>, <a href="https://github.com/egpivo/amm-lab/blob/main/data/processed/same_price_different_depth_swaps.csv"><code>same_price_different_depth_swaps.csv</code></a>.
  </div>
</div>

### External repricing leaves a fee-limited gap: [`arbitrage_repricing.toml`](https://github.com/egpivo/amm-lab/blob/main/scenarios/arbitrage_repricing.toml)

Part I treated arbitrage as correction against stale inventory, not theft from the pool. This run makes the correction explicit.

- **Input.** 1T / 1T pool at 1.0. `ExternalPriceMove` sets reference to **1.5**. Pool price stays at 1.0 until someone trades.

- **Method.** `ArbitrageUntilNoProfit` uses ternary search on input size, because profit is unimodal. Too small and fees eat it; too large and the curve overshoots.

- **Output.** [`arbitrage_repricing_arbitrage.csv`](https://github.com/egpivo/amm-lab/blob/main/data/processed/arbitrage_repricing_arbitrage.csv). Pool reprices to **1.496**, not 1.500. Residual gap: **0.00368**. It is below the fee threshold, so no rational actor closes it (C3, C4). The oracle did not update the pool. A trade did.

### Fees accrued; hold still won: [`lp_vs_hold.toml`](https://github.com/egpivo/amm-lab/blob/main/scenarios/lp_vs_hold.toml)

Part I asked whether fees compensate adverse selection when fundamental flow is thin. This run answers one controlled version. It is not `0xafdd…4575`; it is a synthetic 1T / 1T pool under a 50% external move.

- **Input.** LP deposits 500B X and 500B Y into a 1T / 1T pool. Three swaps run. External price moves to 1.5. Arbitrageur reprices once.

- **Method.** `LpPerformance` reports withdrawal value vs passive hold, with fee income separated. Display: 1 unit = 1,000,000 base units.

- **Output.** [`lp_vs_hold.json`](https://github.com/egpivo/amm-lab/blob/main/data/processed/lp_vs_hold.json). Hold **1,250,000 Y**. LP withdrawal **1,225,150 Y**. Fee income **+410 Y**. Net LP-vs-hold **−24,850 Y**. Fee income covered about **1/61** of the loss (C6, C7).

```bash
cargo run --release -- scenario run scenarios/lp_vs_hold.toml
```

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-07-14-before-mev-build-the-pool/fig3_lp_performance.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-07-14-before-mev-build-the-pool/fig3_lp_performance.png"
         alt="Hold vs LP withdrawal; fee income vs net LP-vs-hold loss"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 2.</strong> LP-vs-hold after one 50% external move, three swaps, and one arbitrage pass. Fee income is positive, but the LP still loses versus hold. Source: <a href="https://github.com/egpivo/amm-lab/blob/main/data/processed/lp_vs_hold.json"><code>lp_vs_hold.json</code></a>.
  </div>
</div>

Under this setting: fee income positive, LP-vs-hold negative. One shock, three swaps, one arb pass.

---

## Stochastic scenarios

The deterministic block stops at point events. That is enough to see how size, depth, repricing, and a single LP shock behave. Part I's passive-liquidity question is path-dependent.

Part I cited [Campbell et al. (2025)](https://arxiv.org/pdf/2508.08152) on loss-versus-rebalancing: the cost of passively providing liquidity while the external mark moves. The paper's object is not one 50% jump. It asks whether fee revenue accumulates faster than LVR when arbitrageurs and fundamental flow trade against the pool step by step. Part I could name that tradeoff; it could not run it.

[`lp_vs_hold.toml`](https://github.com/egpivo/amm-lab/blob/main/scenarios/lp_vs_hold.toml) made the single-shock version concrete: fees **+410 Y**, net LP-vs-hold **−24,850 Y**. The stochastic block keeps the pool economics and changes the input: a seeded GBM price path, routed buy/sell demand each step, and cumulative fee vs tracking error over 1,440 steps. Implementation follows Campbell et al.'s reduced-form CEX + DEX model; the draw is fixed by `seed = 42`.

### Fee revenue vs LVR over a path: [`campbell_sim.toml`](https://github.com/egpivo/amm-lab/blob/main/scenarios/campbell_sim.toml)

- **Input.** GBM CEX price (sigma = 0.04, seed = 42). 1M X / 500 Y reserves. 100 Y buy and sell demand per step. 1,440 steps.

- **Method.** Separate binary ([`src/bin/campbell_sim.rs`](https://github.com/egpivo/amm-lab/blob/main/src/bin/campbell_sim.rs)). `f64` pool, three agents per step (arb → buy → sell). Not the TOML scenario runner.

```bash
cargo run --bin campbell_sim scenarios/campbell_sim.toml
# -> data/processed/campbell_sim.json
```

- **Output.** Fee revenue **390.78 Y** (C9). Tracking error **337.16 Y** (C10). Hedged PnL **+53.62 Y** (C11). Under this seeded path, fees outpaced LVR. The single-shock LP run had the opposite sign (C7). LP economics depend on path and flow intensity, not just whether fees are positive on one event.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-07-14-before-mev-build-the-pool/fig4_campbell_path.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-07-14-before-mev-build-the-pool/fig4_campbell_path.png"
         alt="Fee revenue vs tracking error on default Campbell path; hedged PnL plus 53.6 Y"
         style="max-width:65%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 3.</strong> Fee revenue vs tracking error (LVR) on the default seeded path, seed = 42 (C9–C11). Fees exceed tracking error on this draw; this is not a general result. Source: <a href="https://github.com/egpivo/amm-lab/blob/main/data/processed/campbell_sim.json"><code>campbell_sim.json</code></a>.
  </div>
</div>

---

## Closing

The deterministic block made four pool-layer quantities visible: execution drag, depth, arbitrage residual, and LP-vs-hold. The stochastic block added one path-level quantity: whether fees accumulated faster than tracking error on a seeded Campbell-style run.

Those results are not a live-pool return model. They use synthetic reserves, one seeded path, and simplified flow. The next version should vary depth, fee tier, seeds, and flow assumptions before adding mempool ordering.

That is the boundary of this article: before modeling who captures a trade, the pool layer itself has to be specified and measured.

---

## Appendix

- **Repo:** [egpivo/amm-lab](https://github.com/egpivo/amm-lab)
- **Deterministic:** [`price_impact_ladder.toml`](https://github.com/egpivo/amm-lab/blob/main/scenarios/price_impact_ladder.toml), [`same_price_different_depth.toml`](https://github.com/egpivo/amm-lab/blob/main/scenarios/same_price_different_depth.toml), [`arbitrage_repricing.toml`](https://github.com/egpivo/amm-lab/blob/main/scenarios/arbitrage_repricing.toml), [`lp_vs_hold.toml`](https://github.com/egpivo/amm-lab/blob/main/scenarios/lp_vs_hold.toml)
- **Stochastic:** [`campbell_sim.toml`](https://github.com/egpivo/amm-lab/blob/main/scenarios/campbell_sim.toml)
- **Campbell:** Campbell, J., Bergault, P., Milionis, J., and Nutz, M. (2025). *Optimal Fees for Liquidity Provision in Automated Market Makers.* [arXiv:2508.08152](https://arxiv.org/pdf/2508.08152).
- **Evidence ledger:** [`research/evidence_ledger.csv`](https://github.com/egpivo/amm-lab/blob/main/research/evidence_ledger.csv) (C1–C11)
- **Part I:** [The token appeared twice. The AMM market formed once.]({{ site.baseurl }}/2026/07/12/the-same-token-is-not-the-same-market.html)
