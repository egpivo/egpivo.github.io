---
layout: post
title: "Before the Result Could Count, the Benchmark Had to Freeze"
date: 2026-08-11
tags: [DeFi, DEX, Ethereum, Machine Learning, Finance]
image: /assets/2026-08-11-closed-loop-execution-benchmark/hero.png
---

*[The previous post]({{ site.baseurl }}/2026/08/09/a-large-order-pays-a-path-not-a-price.html) reported the execution result. This companion documents the evaluation contract behind it.*

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-08-11-closed-loop-execution-benchmark/hero.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-08-11-closed-loop-execution-benchmark/hero.png"
         alt="Closed-loop Rust execution environment: shared state and action space, pool mechanics, market-response operators, and step transition order"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem; line-height: 1.55;">
    <strong>Overview.</strong> The single closed-loop Rust environment shared by every policy in the execution study. Schedule baselines, tuned lookahead, planners, and the DQN all act through the same state, action space, pool mechanics, market-response operators, and completion accounting. Within each step: agent trade → noise routing → arbitrage → oracle advance → fee update → next state. The schematic uses agent-first ordering; the headline block uses agent-last (noise and arbitrage before the agent trade). The fee-closure block produces the next-state fees after oracle advance. Schematic only—not live-chain telemetry.
  </div>
</div>

***

Beating time-weighted average price (TWAP) was not enough. The two-hidden-layer DQN, which maps sixteen market-state features to eight execution actions, also had to beat tuned one-step control without future leakage, unfinished inventory, or feedback from the final seeds.

That required one transition engine, common completion accounting, tuned baselines, role-separated seeds, and frozen checkpoints. The implementation, manifest, and per-seed outputs live in [egpivo/amm-lab](https://github.com/egpivo/amm-lab) under [`data/rl_equilibrium/`](https://github.com/egpivo/amm-lab/tree/main/data/rl_equilibrium). The simulator and result are in [the previous post]({{ site.baseurl }}/2026/08/09/a-large-order-pays-a-path-not-a-price.html); this post covers the five checks behind them.

***

## One transition engine

The learner and baselines must face the same transition law, and the observation cannot contain future information.

Market physics live in one Rust execution environment ([`ExecEnv`](https://github.com/egpivo/amm-lab/blob/main/src/sim/env.rs)). Python never reimplements the step. The DQN calls the same binary over a JSON-lines bridge; every heuristic and planner calls the same step function.

Decision-time fees are snapshotted before any leg runs. Fees update only after the oracle advances. **Intra-step priority**—whether the agent's trade runs before or after noise flow and arbitrage within the step—is a declared parameter, not an implementation accident.

A cargo test whitelists every field on the observation vector. Add a field without review and the test fails. Same seed → identical episode outcome. Drift + slippage-ex-fee + fee + gas + terminal term must equal reported implementation shortfall to 1e-6.

The learner also sees *less* than the tuned baseline: heuristics read the full observation struct; the DQN reads sixteen scaled features. The information asymmetry runs against the learner.

### Why Rust and Python

- **Rust world model:** pools, noise flow, arbitrage, fee updates, completion accounting, baselines, planners, and tabular Monte Carlo.
- **Python learner:** PyTorch DQN, replay buffer, hyperparameter sweeps, and checkpoint selection.

Rust keeps simulation deterministic and semantically single. Python keeps network, optimizer, reward-scaling, and exploration changes cheap.

The PyTorch path is [`rl_equilibrium_bridge`](https://github.com/egpivo/amm-lab/blob/main/src/bin/rl_equilibrium_bridge.rs) → [`gym_env.py`](https://github.com/egpivo/amm-lab/blob/main/scripts/rl_equilibrium/gym_env.py) → [`dqn_train.py`](https://github.com/egpivo/amm-lab/blob/main/scripts/rl_equilibrium/dqn_train.py). Tabular Monte Carlo stays in Rust, where thousands of episodes finish in seconds. Rewriting [`ExecEnv`](https://github.com/egpivo/amm-lab/blob/main/src/sim/env.rs) or [`src/sim/`](https://github.com/egpivo/amm-lab/tree/main/src/sim) in Python would duplicate the transition law and create another place for train/evaluation drift.

[`rl_equilibrium_bridge`](https://github.com/egpivo/amm-lab/blob/main/src/bin/rl_equilibrium_bridge.rs) is a thin stdin/stdout JSON layer. Rust holds state and computes reward; Python sends `reset` and `step`, then reads observation, reward, and completion. Tabular runs never cross the bridge.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-08-11-closed-loop-execution-benchmark/fig03_policy_behavior.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-08-11-closed-loop-execution-benchmark/fig03_policy_behavior.png"
         alt="Wait share vs oracle gap; routing vs buy-fee gap for DQN and lookahead on development seeds"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 1.</strong> Development diagnostic. Waiting varies with the oracle gap; routing varies with the buy-fee gap. Not the headline block.
  </div>
</div>

The behavior is economically legible, though this diagnostic does not establish optimality.

***

## A baseline worth beating

TWAP, myopic routing, and an untuned heuristic are weak comparison points.

The bar is **tuned one-step lookahead**. It rebuilds exact quote curves and scores each action using immediate execution premium plus a carry for unfinished inventory. The carry multiplier is selected on validation seeds; the frozen value is 16. Immediate liquidation and myopic routing are still reported.

On the final block under agent-first ordering, paired differences relative to lookahead are **+10.8 bps** for two-step expectimax, **+1.6** for three-step expectimax, **+0.1** for stochastic rollout, and **−14.9** for the DQN ([`final_ladder.csv`](https://github.com/egpivo/amm-lab/blob/main/data/rl_equilibrium/final_ladder.csv), [`m3r_stochastic_planner_final.csv`](https://github.com/egpivo/amm-lab/blob/main/data/rl_equilibrium/m3r_stochastic_planner_final.csv)). Positive values are worse; negative values are better. Stochastic rollout ties lookahead, while the DQN reduces shortfall. Realized fee and quote variation may contribute, but the experiment cannot separate that mechanism from shallow search and heuristic continuation.

The learner rung also includes model-free tabular Monte Carlo control at two discretizations. The fine table ties tuned lookahead; the coarse table does not. That comparison is consistent with a discretization bottleneck in the coarse learner rather than an absence of sequential structure.

Hindsight coordinate descent over full action sequences provides an achieved reference only. It consumes realized future shocks and is never a deployable policy.

***

## Strict completion

An execution policy should not win by leaving inventory unfinished.

Under forced terminal completion—the headline setting—any inventory left after the agent's final action is executed at the terminal state. Completion is **1.0** for every policy. No controller wins by leaving the book open.

Reward is the negative normalized execution premium: maximizing undiscounted return is identical to minimizing reported implementation shortfall. The terminal term is part of the same accounting identity: a penalty under the standard rule, and actual forced execution cost under the headline rule. It is never removed from reported shortfall or added as a post-hoc correction.

***

## Freeze the seed blocks

Seeds used for training, selection, diagnostics, and the headline need distinct roles.

Training, development, fresh-check, and final headline blocks are isolated by seed range. Learner validation (`20,000–20,049`) is declared upfront as a nested subset of the broader baseline-validation block (`20,000–20,199`):

- **Train** — episode index `1,000,000 + ep` (fresh path per episode)
- **Baseline validation** — seeds `20,000–20,199` (lookahead urgency weight; planner grid)
- **Learner validation** — seeds `20,000–20,049` (DQN checkpoint pick at episode 11,000—not the final epoch)
- **Development test** — seeds `30,000–30,499` (ladder figures, behavior diagnostics)
- **Fresh check** — seeds `40,000–40,499` (one-shot reproduction)
- **Final headline** — seeds `90,000–90,999` (all frozen policies; paired confidence intervals vs lookahead)


<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-08-11-closed-loop-execution-benchmark/fig02_seed_freeze_pipeline.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-08-11-closed-loop-execution-benchmark/fig02_seed_freeze_pipeline.png"
         alt="Role-separated seed blocks and freeze pipeline from training through final headline evaluation"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem; line-height: 1.55;">
    <strong>Fig. 2.</strong> Seed roles from training through final evaluation. The headline block is read only after design and checkpoint freeze.
  </div>
</div>

The completed manifest at [`data/rl_equilibrium/m3r_run_manifest.json`](https://github.com/egpivo/amm-lab/blob/main/data/rl_equilibrium/m3r_run_manifest.json) records Python/torch/rustc versions, [`Cargo.lock`](https://github.com/egpivo/amm-lab/blob/main/Cargo.lock) hash, git commit, command list, the pre-final design choices, and sha256 of every checkpoint and result CSV. Because it hashes final-result CSVs, the manifest is assembled after those files are produced. The policies and evaluation choices it records were frozen before the final block. [`make -C scripts/rl_equilibrium verify`](https://github.com/egpivo/amm-lab/blob/main/scripts/rl_equilibrium/Makefile) runs [`verify_paper_artifacts.py`](https://github.com/egpivo/amm-lab/blob/main/scripts/rl_equilibrium/verify_paper_artifacts.py) against the recorded contract.

**Headline (final block only):** forced completion, agent trade after noise and arbitrage, n = 1,000 — DQN **100.3 bps** vs lookahead **113.6 bps**, paired **−13.29 bps** [−14.22, −12.32]. Agent trade before noise and arbitrage: **−14.9 bps**. Randomized intra-step ordering is the smallest edge: **−5.62 bps** [−7.03, −4.18].

That ordering spread has a loose analogue in recent centralized-exchange–DEX (CEX–DEX) work on priority fees and stochastic settlement delays ([Bergault, Hafsi & Sánchez-Betancourt, arXiv:2602.10798](https://arxiv.org/abs/2602.10798)): execution speed, uncertainty, and cost trade off. It is not the same model as the simulator's trade-ordering parameter; the basis-point numbers are ours. The paper helps motivate treating intra-step priority as a finance parameter rather than a bookkeeping detail.

***

## Transfer is not re-solving

Retraining under a perturbation does not show that the original checkpoint generalized.

Perturbations change the transition law. The protocol separates:

- **Frozen transfer** — evaluate the frozen checkpoint under the perturbed environment without retraining
- **Re-solving** — retrain under the perturbed environment on the pre-specified set (fee mode, intra-step priority)

On development seeds, moving an agent-first checkpoint to agent-last execution shrinks its paired edge from **−15.5** to **−6.3 bps** ([`m3r_priority.csv`](https://github.com/egpivo/amm-lab/blob/main/data/rl_equilibrium/m3r_priority.csv)). After retraining under agent-last ordering, the final-block edge is **−13.3 bps** against matched lookahead ([`m3r_final_paper_seeds.csv`](https://github.com/egpivo/amm-lab/blob/main/data/rl_equilibrium/m3r_final_paper_seeds.csv)). The first comparison measures transfer; the second re-solves the changed environment.

Scalar nuisance perturbations—gas level, arbitrage speed, noise scale, fee coefficients—are transfer-only. None flip the ranking on the frozen checkpoint.

**Fee-mode re-solving (a 300-seed subset of the development-test block, default bridge ordering—agent trade before noise and arbitrage):** when trained and evaluated under constant fees, the paired DQN–lookahead estimate is **+1.2 bps** (means round to 116.1 and 115.0 bps), a near tie rather than evidence of an advantage. Dynamic monopoly: **−23.2 bps**. Dynamic duopoly: **−14.7 bps**. Each row pairs the retrained DQN against tuned lookahead in the same fee environment ([`m3r_dynamic_fee_ablation.csv`](https://github.com/egpivo/amm-lab/blob/main/data/rl_equilibrium/m3r_dynamic_fee_ablation.csv)). The edge concentrates in dynamic-fee environments. These are ablation results, not final-block headline estimates.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-08-11-closed-loop-execution-benchmark/fig01_priority_retrain.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-08-11-closed-loop-execution-benchmark/fig01_priority_retrain.png"
         alt="Priority retraining heatmap: DQN shortfall and paired edge vs lookahead by train and eval ordering"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 3.</strong> Priority transfer and retraining on development seeds. Diagonal cells use matched train/evaluation ordering; off-diagonal cells test transfer. Source: <a href="https://github.com/egpivo/amm-lab/blob/main/data/rl_equilibrium/m3r_priority.csv"><code>m3r_priority.csv</code></a>.
  </div>
</div>

Two optional sensitivity layers default off in the headline freeze. On separate 500-seed blocks, neither layer flips the DQN–lookahead ranking at baseline or weak stress ([`m4_lp_adaptation.csv`](https://github.com/egpivo/amm-lab/blob/main/data/rl_equilibrium/m4_lp_adaptation.csv), [`m4_jit_mev.csv`](https://github.com/egpivo/amm-lab/blob/main/data/rl_equilibrium/m4_jit_mev.csv)). Aggressive threshold-based sandwich-searcher stress raises shortfall for both policies but leaves the gap intact.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-08-11-closed-loop-execution-benchmark/fig04_sensitivity_layers.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-08-11-closed-loop-execution-benchmark/fig04_sensitivity_layers.png"
         alt="M4 sensitivity: DQN vs tuned lookahead under LP depth adaptation and threshold-based sandwich-searcher stress"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem; line-height: 1.55;">
    <strong>Fig. 4.</strong> Optional appendix layers on 500-seed sensitivity blocks (LP: 95,000–95,499; JIT: 96,000–96,499), not the 90,000–90,999 headline block. Left: liquidity-provider depth adaptation. Right: threshold-based sandwich-searcher stress. Sources: <a href="https://github.com/egpivo/amm-lab/blob/main/data/rl_equilibrium/m4_lp_adaptation.csv"><code>m4_lp_adaptation.csv</code></a>, <a href="https://github.com/egpivo/amm-lab/blob/main/data/rl_equilibrium/m4_jit_mev.csv"><code>m4_jit_mev.csv</code></a>. Both are explicit stress models, not claims about live LP or searcher behavior.
  </div>
</div>

***

## What the contract does not certify

The contract supports a model-conditioned comparison with tuned one-step routing under forced completion. It does not establish live profitability, actual mempool ordering, adaptive liquidity-provider behavior, or equilibrium of the fee rule.

If I rebuilt this study next, resolving intra-step priority and adaptive liquidity-provider response would take priority over network width.

***

## Closing

The result counted only after the transition law, completion rule, baseline, checkpoint, and final seed block stopped moving. The next test is a richer transition law with mempool ordering and adaptive liquidity-provider repositioning before adding network capacity.

***

## Appendix: sources and reproducibility

- **Paper:** Wang, Wen-Ting (2026), [Reinforcement Learning for Execution under Dynamic Fees in a Closed-Loop DEX Simulator](https://arxiv.org/abs/2607.10960).
- **Execution study:** [A Large DEX Order Is a Sequential Control Problem.]({{ site.baseurl }}/2026/08/09/a-large-order-pays-a-path-not-a-price.html)
- **Code, manifest, and artifacts:** [egpivo/amm-lab](https://github.com/egpivo/amm-lab). Simulator: [`src/sim/`](https://github.com/egpivo/amm-lab/tree/main/src/sim). Training and evaluation: [`scripts/rl_equilibrium/`](https://github.com/egpivo/amm-lab/tree/main/scripts/rl_equilibrium) ([`gym_env.py`](https://github.com/egpivo/amm-lab/blob/main/scripts/rl_equilibrium/gym_env.py), [`dqn_train.py`](https://github.com/egpivo/amm-lab/blob/main/scripts/rl_equilibrium/dqn_train.py), [`verify_paper_artifacts.py`](https://github.com/egpivo/amm-lab/blob/main/scripts/rl_equilibrium/verify_paper_artifacts.py)). Frozen outputs: [`data/rl_equilibrium/`](https://github.com/egpivo/amm-lab/tree/main/data/rl_equilibrium) ([`m3r_run_manifest.json`](https://github.com/egpivo/amm-lab/blob/main/data/rl_equilibrium/m3r_run_manifest.json)).
- **External reference:** Bergault, Hafsi & Sánchez-Betancourt (2026), [Trading in CEXs and DEXs with Priority Fees and Stochastic Delays](https://arxiv.org/abs/2602.10798)
