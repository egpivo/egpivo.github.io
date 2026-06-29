---
layout: post
title: "When the Quote Becomes Calldata. The Fork Tests Whether It Holds."
date: 2026-06-30
tags: [DeFi, RWA, Ethereum, Blockchain, Web3]
---

*A note on turning a Uniswap quote into API-native calldata, then replaying that transaction against pinned mainnet state.*

---

[Part I]({{ site.baseurl }}/2026/06/28/the-price-moves-first-route-frays-before-exit.html) stopped at the quote layer: route legs, output amounts, API-reported `priceImpact`, and `blockNumber`. It recorded what the router proposed. At larger sizes, that proposal became a spread of pools and intermediate hops, not a single price.

A desk sizing an exit acts on that quote; so does a risk pipeline that reads `priceImpact` as a risk number. On a centralized venue, a mistake there usually stays inside an operator's scope: an order cancelled, a fill refunded, a replacement issued. Once the quote becomes calldata, there is no venue operator between the user and pool execution, and the failure boundary moves from router proposal to encoded constraints. The quote alone cannot tell whether the next problem is invalid transaction construction, wallet authorization, gas estimation, state drift, ordering, or the final fill.

Part I sliced the quote layer; this post slices one execution layer: build the transaction from the quote, replay it against pinned mainnet state, and check whether the proposal survives, and where the route's complexity ends up. A valid quote does not mean valid calldata; a successful same-state replay does not mean a mined receipt.

---

## Readable quote, executable calldata

A `/quote` response can show expected output, `minimumAmount`, route structure, and `blockNumber`, but none of those fields execute by themselves. The trade becomes executable only when `/swap` returns a `TransactionRequest`: `to`, `data`, `value`, `gasLimit`, and encoded router instructions.

The chain enforces only what the transaction encodes—most importantly the minimum output condition. Expected output and `priceImpact` are display fields, not the bytes the Universal Router will run.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-06-30-when-the-quote-becomes-a-transaction/quote_becomes_transaction_fork_replay.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-06-30-when-the-quote-becomes-a-transaction/quote_becomes_transaction_fork_replay.png"
         alt="Quote evidence, swap calldata, and controlled fork replay with live mainnet ordering and MEV outside the measurement boundary"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 1.</strong> Quote evidence vs transaction evidence. The quote records what the router proposed; `/swap` materializes calldata; fork replay tests that calldata against pinned state. Ordering, MEV, fee payment, and inclusion sit outside this article.
  </div>
</div>

The replay is a same-state execution check for the `/swap` artifact, not a live fill. Fork setup and measured fields are in the run section below.

Uniswap's Trading API exposes this directly by separating [`/quote`](https://developers.uniswap.org/docs/api-reference/aggregator_quote) from [`/swap`](https://developers.uniswap.org/docs/api-reference/create_swap_transaction):

```text
POST /quote
  → POST /swap with the returned quote
  → save TransactionRequest
  → fork at quote.blockNumber
  → seed wallet balance and approvals
  → send API-native calldata
  → measure output-token delta, minimumAmount, and gas
```

Shell references: [`quote_to_swap.sh`](https://gist.github.com/egpivo/72f6c99f39bfc1b27238283e438db632#file-quote_to_swap-sh) and [`replay_swap.sh`](https://gist.github.com/egpivo/0e1ee51092d60ee0587ede159bde569a#file-replay_swap-sh).

---

## The fork replay run

**Run ID:** `20260619Tpart2v1`

I collected nine cells: USDC → WETH, AAVE, and MKR at $100, $10k, and $1M. Routing was Uniswap classic (`CLASSIC`); protocols V2/V3/V4 via `BEST_PRICE`; UniswapX excluded.

For each cell I POSTed `/quote`, then POSTed `/swap` with the returned quote object and archived both responses. `/swap` used allowance-based calldata from the Trading API—not SDK reconstruction from route JSON. API `simulateTransaction` succeeded on all nine cells.

Each cell was replayed on a fresh Anvil mainnet fork at that cell's `quote.blockNumber` (blocks 25,350,126–25,350,128), with archive RPC state. I seeded a fixed test wallet with ETH for gas, USDC via `anvil_setStorageAt`, and `USDC → Permit2 → Universal Router` approvals. Replay sent exact API-native `/swap` calldata to the router at `0x66a989…8Af`.

A signed-permit collection (`20260619Tpart2v0`) failed fork replay when permit `sigDeadline` preceded the pinned quote-block timestamp. That comparison run is archived; the primary evidence is the allowance path above.

Measured per row: `fork_status`, `fork_output_amount`, `fork_vs_quote_bps`, `fork_meets_minimum`, `fork_gas_used`, and `api_simulation_status`.

---

## What the grid shows

All nine cells replayed at pinned state, cleared `minimumAmount`, and matched the quote at 0 bps: the expected baseline for same block, same pool state, same calldata.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-06-30-when-the-quote-becomes-a-transaction/fig2_9cell_fork_replay_panel.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-06-30-when-the-quote-becomes-a-transaction/fig2_9cell_fork_replay_panel.png"
         alt="Nine-cell fork replay panel for WETH, AAVE, and MKR at 100, 10k, and 1M USDC input sizes"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 2.</strong> Fork replay panel: WETH / AAVE / MKR × $100 / $10k / $1M. Each cell reports fork status, fork vs quote (bps), `minimumAmount` pass/fail, and gas used. Run `20260619Tpart2v1`; same-state replay matched the quote at 0 bps.
  </div>
</div>

**WETH $100** routed through a single V3 hop. Fork gas was 140,975—the simple control.

**MKR $1M** showed quote-layer output deterioration in Part I. Its seven-hop transaction still replayed at 0 bps and cleared the minimum.

---

## AAVE $1M: fragmented route, same-state pass

Part I flagged AAVE for route fragmentation and summary-field ambiguity. At $1M the quote carried **13 pool legs across five parallel paths** (V2/V3/V4 mix). `/swap` returned 14,366 bytes of calldata. Fork gas was 2,386,700—roughly 17× the WETH $100 control.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-06-30-when-the-quote-becomes-a-transaction/fig3_aave_1m_route_stress.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-06-30-when-the-quote-becomes-a-transaction/fig3_aave_1m_route_stress.png"
         alt="AAVE one-million-dollar quote route dependency graph with five parallel paths and thirteen pool legs"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 3.</strong> USDC → AAVE at $1M: five parallel paths, 13 pool legs, V2/V3/V4 mix. Side panel: quote block 25,350,127, quoted output, `minimumAmount`, fork status. The route looked fragmented at quote time; it did not become a deterministic same-state failure.
  </div>
</div>

---

## Pilot panel: what route stress becomes

The nine-cell replay is a controlled check, but it is too small to say much about route stress more generally. I therefore ran a pilot panel over 28 snapshot labels, 10 assets, and five input sizes: 1,400 intended cells. This was a pipeline pilot, not a historical backtest.

The pilot produced 977 successful `/quote` + `/swap` rows. The strongest pattern was payload size: hop count versus calldata bytes had a Pearson correlation of 0.935; path count versus calldata bytes was 0.917.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-06-30-when-the-quote-becomes-a-transaction/fig_panel_b_complexity_scatter.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-06-30-when-the-quote-becomes-a-transaction/fig_panel_b_complexity_scatter.png"
         alt="Pilot panel scatter plot showing route hop count against calldata bytes, with marker size indicating USDC input size"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 4.</strong> Pilot panel: 1,400 intended cells; 977 successful `/quote` + `/swap` rows plotted. Hop count versus calldata bytes (Pearson <em>r</em> = 0.935). Marker size is USDC input size; descriptive, not causal.
  </div>
</div>

From that panel I selected 118 stress rows for fork replay. Ninety replayed successfully at pinned state. The remaining 28—all high-complexity SHIB rows—stopped at `eth_estimateGas`.

Three of those I direct-sent on fresh pinned forks with a 12M gas cap; all three executed at roughly 7M gas and cleared `minimumAmount`. The timeout was an estimator artifact, not an EVM failure—but that check covers only 3 rows. The remaining 25 still need the same follow-up.

---

## What a fork replay result actually means

The first all-green table raised a scope question: was this evidence, or only a same-state sanity check? Treating replay as one test stopped working once the non-receipts came from different layers.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-06-30-when-the-quote-becomes-a-transaction/fig5.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-06-30-when-the-quote-becomes-a-transaction/fig5.png"
         alt="Where the evidence stopped: CRV at configuration, COMP/LDO at quote availability, signed-permit at wallet authorization, SHIB at gas estimation then direct-send success, AAVE at same-state EVM fork execution"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 5.</strong> Where the evidence stopped across 118 selected stress-row replays. CRV stopped at configuration, COMP/LDO at quote availability, the signed-permit path at wallet authorization, SHIB at gas estimation before direct-send replay, and AAVE at same-state EVM fork execution. A single pass/fail column would erase those distinctions.
  </div>
</div>

A non-receipt is not one failure class. Configuration, authorization, estimation, and EVM execution fail at different boundaries.

---

## Closing

Part I stopped at the quote. Here, same-state replay held, route complexity showed up in calldata size, and three SHIB estimator timeouts became roughly 7M-gas executions on bounded forks.

The harder part is keeping the labels straight: estimator timeout, authorization failure, configuration error, and EVM execution are different boundaries, even when all of them produce no mined receipt.

The next falsifiable check is narrow: direct-send the remaining 25 SHIB rows with bounded gas on pinned forks. Inclusion, ordering, MEV, state drift, and realized fill still need receipt-level evidence.

---

## Appendix

- **Reproduce:** [`quote_to_swap.sh`](https://gist.github.com/egpivo/72f6c99f39bfc1b27238283e438db632) (collect `/quote` + `/swap`) and [`replay_swap.sh`](https://gist.github.com/egpivo/0e1ee51092d60ee0587ede159bde569a) (fork replay).
  - **Requires:** `curl`, `jq`, Foundry (`cast`, `anvil`), Uniswap API key, archive Ethereum RPC.
  - **Replay:** fork at `quote.blockNumber` → seed wallet → send saved calldata → check output, `minimumAmount`, gas.
  - **Estimator check:** `SKIP_ESTIMATE=1` with a bounded gas cap if `eth_estimateGas` times out.

- **Part I ladder:** [The Price Moves First. DEX Routes Fray Before the Exit.]({{ site.baseurl }}/2026/06/28/the-price-moves-first-route-frays-before-exit.html) — quote-layer route fraying; collection `20260617T134419Z`.
- **RWA exchange-risk context:** [Where RWA Exchange Risk Actually Sits]({{ site.baseurl }}/2026/06/21/where-rwa-exchange-risk-actually-sits.html). Centralized venues can cancel, refund, or issue replacement objects; a DEX route has no default operator at execution time.
- **API references:** [POST /quote](https://developers.uniswap.org/docs/api-reference/aggregator_quote), [POST /swap](https://developers.uniswap.org/docs/api-reference/create_swap_transaction), [swapping integration guide](https://developers.uniswap.org/docs/trading/swapping-api/integration-guide).
- **Pre-execution tooling:** [MetaMask security alerts](https://support.metamask.io/configure/wallet/security-alerts/) (transaction simulation before signing); [Tenderly single simulations](https://docs.tenderly.co/simulations/single-simulations) and [virtual environments](https://docs.tenderly.co/virtual-environments/overview) (fork simulation).
