---
layout: post
title: "The Stablecoin Map: What Crypto's Cash Rails Depend On"
date: 2026-05-31
categories: [web3, stablecoins, defi]
tags: [DeFi, Stablecoins, Blockchain, Web3, Ethereum]
excerpt: "Stablecoins are becoming crypto's cash layer. The question is not only what they are pegged to, but what they depend on."
---

*USDC is a dollar token. XSGD is a Singapore dollar token. EURC is a euro token. The peg label answers one question. A stablecoin rail also depends on backing, issuer controls, chain deployments, transfer activity, pool counterparts, bridges, and redemption paths outside the chain.*

*This follows [USDC Shows Why Stablecoin Risk Analysis Is Not One Signal]({{ site.baseurl }}/2026/05/17/usdc-looks-like-one-token.html) and [Local Pegs, Dollar Rails]({{ site.baseurl }}/2026/05/24/local-pegs-dollar-rails-geo-stablecoin-audit.html): separate the token label from the accounting and liquidity surfaces, then ask where the cash layer concentrates.*

---

The stablecoin map looks diverse. USD, EUR, SGD, JPY, and BRL show up across chains and issuers. That diversity is real at the label layer. It is much thinner once you ask what each rail actually runs on: reserves, issuer controls, deployment choice, transfer activity, pool counterparts, bridges, and redemption paths that mostly sit outside the chain.

I started this line of work from a narrower worry. Geographic stablecoins are often discussed as national or regional cash on chain. Blockchain data let me ask a harder question. If stress hits one rail through a pool drain, bridge delay, or collateral markdown, how fast does it move through a system with no lender of last resort on chain? Stablecoin depegs do not unwind like slow macro headlines. They propagate through shared quote assets, lending books, and bridge queues at block speed.

This post is not country adoption and not reserve adequacy. It maps dependencies you can partially see on chain: footprint, transfer activity, and DEX pool structure.

---

## The cash layer

Stablecoins settle trades, collateralize loans, bridge chains, and sit on the cash leg of tokenized asset products. When a market quotes in USDT, borrows against USDC, or routes through a USDC pool, the stablecoin is part of the system's cash layer. It is not just another token.

Stablecoins also depend on the chain's gas layer. A USDC or EURC transfer may be dollar- or euro-denominated, but it still needs a native fee asset to move—ETH on Ethereum and many L2s, POL on Polygon, TRX on Tron, SOL on Solana, and so on. The token may be stable; the rail it moves on is not free.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-05-31-stablecoin-map-local-pegs-dollar-rails/stakeholder.gif" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-05-31-stablecoin-map-local-pegs-dollar-rails/stakeholder.gif"
         alt="Conceptual stablecoin cash layer: backing outside the chain, chain deployments and pools, opaque CEX and redemption paths"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Conceptual bridge.</strong> Fiat backing and issuer control sit partly outside the chain; deployments, DEX pools, and some bridge activity leave chain traces; CEX venues and redemption paths stay more opaque. Conceptual diagram only.
  </div>
</div>

What matters for infrastructure risk is overlap: how many apps, pools, and bridges touch the same quote asset before anyone checks reserves or redemption capacity.

---

## Footprint by peg anchor

Stablecoins are usually grouped by peg currency: USD, EUR, SGD, JPY, and BRL. A footprint map asks which rails exist, what they track, and how large their supply or market cap proxy is.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-05-31-stablecoin-map-local-pegs-dollar-rails/global_stablecoin_footprint_map_v1.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-05-31-stablecoin-map-local-pegs-dollar-rails/global_stablecoin_footprint_map_v1.png"
         alt="Representative stablecoin footprint by peg currency or issuer anchor"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 1.</strong> Representative footprint by peg currency or issuer/currency anchor. Bubble size uses circulating supply or market cap where reliable. This is not country adoption, user geography, or country level transaction volume.
  </div>
</div>

Large footprint can coexist with thin activity or thin pools. The map is an inventory read, not a usage read.

---

## Footprint is not transfer activity

Circulating supply measures how large a rail is. Transfer volume measures how much value moved through supported chain rails in a window. USDC and USDT dominate supported token transfer volume from **2026-04-28 → 2026-05-27**. EURC shows up; XSGD and BRLA are far smaller.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-05-31-stablecoin-map-local-pegs-dollar-rails/stablecoin_transfer_volume_selected_rails_v1.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-05-31-stablecoin-map-local-pegs-dollar-rails/stablecoin_transfer_volume_selected_rails_v1.png"
         alt="Artemis adjusted stablecoin transfer volume for supported tokens, 2026-04-28 to 2026-05-27"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 2.</strong> Artemis adjusted stablecoin transfer volume for supported tokens, 2026-04-28 to 2026-05-27. Transfer activity on chain only. This is not user geography, CEX internal ledger activity, OTC flow, or actual routing.
  </div>
</div>

Footprint, transfer activity, and pool structure can all disagree. That is the point: one label hides several dependency surfaces.

---

## DEX pool counterparts

On a DEX, the question is what sits on the other side of the pool. I call this the pool counterpart. In the **2026-05-29** DexScreener snapshot, selected local currency deployments lean heavily on USDC in observed pool liquidity.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-05-31-stablecoin-map-local-pegs-dollar-rails/stablecoin_pair_share_local_only_v1.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-05-31-stablecoin-map-local-pegs-dollar-rails/stablecoin_pair_share_local_only_v1.png"
         alt="DEX pool counterpart shares for selected local currency stablecoin deployments"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 3.</strong> DEX pool counterpart shares for selected local currency deployments. DexScreener snapshot, 2026-05-29.
  </div>
</div>

XSGD Polygon is the extreme case: SGD on the label, USDC on almost every observed pool edge.

**Interpretation:** this is not FX diversity at the liquidity layer. In this selected DEX slice, the map looks multicurrency, but the visible pools behave much closer to a shared dollar rail system.

---

## One hop neighborhoods

The stacked bar shows proportions; the one hop graph shows shape. XSGD Polygon is almost entirely connected to USDC. XSGD Base and EURC Base carry WETH/native exposure, but USDC remains the largest observed edge. EURC Ethereum has a wider neighborhood; USDC is still the largest counterpart class.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-05-31-stablecoin-map-local-pegs-dollar-rails/stablecoin_dependency_graph_simplified_v1.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-05-31-stablecoin-map-local-pegs-dollar-rails/stablecoin_dependency_graph_simplified_v1.png"
         alt="One hop liquidity neighborhoods for selected local currency stablecoin deployments"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 4.</strong> One hop liquidity neighborhoods for the same deployments and DexScreener snapshot. Edges summarize observed pool counterparts, not actual swap paths.
  </div>
</div>

Local pegs are not floating in isolated SGD or EUR liquidity zones. In this pool graph, they sit next to USDC.

---

## What remains outside the chain

Reserves, redemption queues, CEX order books, OTC flows, legal claims, issuer mint policy, and actual swap routing need different evidence.

Tether on Omni is an early instance of the same split. The token moved on-chain; balances counted; markets quoted it as a dollar substitute. The harder question sat off-ledger: what backed it, who verified it, and what redemption looked like when confidence broke. Transfer and pool maps cannot answer that. A stablecoin is an on-chain balance and an off-chain claim.

Macro pressure, reserve politics, admin controls, and contract halt rights also sit outside the chain.

The map does not stop at DEX pools. Tokenized funds, synthetics, and pre-IPO products still settle through a cash leg. That leg is often a stablecoin rail. In [The SpaceX Trade Exists. Now Watch the Tape.]({{ site.baseurl }}/2026/05/26/spacex-trade-watch-the-tape.html), the evidence was CEX APIs, not pool liquidity: pre-IPO perps settled in USDT, with real volume and open interest, no equity claim behind the contract.

**My conjectures:** local currency stablecoins may be less about building standalone national liquidity on chain and more about keeping a local unit visible on a settlement rail that still clears through dollar inventory. I cannot test issuer motive or macro causality from a DexScreener pull. I can inspect whether nominally different pegs still share the same pool edge. That shared edge is where a liquidity problem in one token can start to look like a shared rail problem.

---

## Closing

The first stablecoin question is what it is pegged to. The infrastructure question is what gives it liquidity, and what else breaks when that liquidity moves.

This snapshot shows local pegs sitting near USDC in observed DEX pools. That pattern alone does not forecast a crash. It does suggest a mismatch worth taking seriously: currency labels multiply faster than independent liquidity rails.

The next check I would run is swap path data against the pool graph. If execution routes through USDC as often as pool inventory implies, the single rail read gets stronger. If not, the graph overstates concentration. The footprint map would still look diverse while execution stayed entangled.

Either way, the dependency question comes before the peg question when you care about speed. Cash on chain has no quiet weekend to absorb bad news.

---

## Appendix: sources

- **Footprint:** [DefiLlama stablecoins API](https://stablecoins.llama.fi/stablecoins?includePrices=true); regenerated as `global_stablecoin_inventory_v1.csv` via [`stablecoin-map-package`](https://github.com/egpivo/stablecoin-audit#blog-evidence) (below).
- **Transfer activity:** [Artemis `ARTEMIS_STABLECOIN_TRANSFER_VOLUME`](https://data-svc.artemisxyz.com/data/api/ARTEMIS_STABLECOIN_TRANSFER_VOLUME), window **2026-04-28 → 2026-05-27**; regenerated as `stablecoin_transfer_volume_selected_rails_v1.csv`. Excludes CEX internal ledger flow, OTC flow, and issuer desk activity.
- **DEX liquidity:** DexScreener pool snapshot (**2026-05-29**); repo artifacts [`stablecoin_liquidity_pairs.csv`](https://github.com/egpivo/stablecoin-audit/blob/main/data/benchmarks/stablecoin_liquidity_pairs.csv), [`stablecoin_pair_dependence_summary.csv`](https://github.com/egpivo/stablecoin-audit/blob/main/data/benchmarks/stablecoin_pair_dependence_summary.csv). Excludes CEX depth and redemption queues.
- **Claim map:** [docs/evidence/blog_evidence_links_v1.md](https://github.com/egpivo/stablecoin-audit/blob/main/docs/evidence/blog_evidence_links_v1.md) in [stablecoin-audit](https://github.com/egpivo/stablecoin-audit).

## Appendix: reproduction

Map-package CSVs for footprint, transfer volume, and DEX dependency rows can be regenerated from [stablecoin-audit](https://github.com/egpivo/stablecoin-audit):

```bash
cargo run -- stablecoin-map-package
# local only dependency CSVs, no DefiLlama/Artemis calls:
cargo run -- stablecoin-map-package --skip-network
```
