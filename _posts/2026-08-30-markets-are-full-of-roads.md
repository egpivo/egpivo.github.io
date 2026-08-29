---
layout: post
title: "Markets Are Full of Roads. That Doesn't Mean Capital Takes Them."
date: 2026-08-30
tags: [Market Structure, RWA, Solana, DeFi, Finance]
image: /assets/2026-08-30-liquidity-migration/hero.png
---

*Five Solana wrappers on one company, one issuer-designated conversion route, and nine weeks of swap-level flow through it. Public data only, no position taken.*

*I first looked at SpaceX [before the listing]({{ site.baseurl }}/2026/05/26/spacex-trade-watch-the-tape.html), when access arrived before the stock. A [listing-day follow-up]({{ site.baseurl }}/2026/06/21/where-rwa-exchange-risk-actually-sits.html) mapped how similar tickers led to different claims and records. This time I follow the on-chain wrappers after the event.*

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-08-30-liquidity-migration/hero.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-08-30-liquidity-migration/hero.png"
         alt="How one shock moved through five SpaceX wrappers: shock, markets react, can capital move, can we see the path, and the different endings"
         style="max-width:96%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem; line-height: 1.55;">
    <strong>Overview.</strong> The questions used to trace the SpaceX wrappers after the IPO. Schematic; no data.
  </div>
</div>

---

Something large appears in a market. The immediate story is that money moved toward it.

That reflex is common in "record volume" headlines. We can see that one market got quieter and another got busier. Whether the second got busier **because of** the first is the migration claim, and it is difficult to verify.

Two episodes made me distrust it.

**USDC, March 2023.** Circle disclosed $3.3bn of reserves stuck at Silicon Valley Bank; USDC traded to roughly $0.88. The next day Curve printed the highest daily volume in its history, about $6.03bn. Read as activity, a record day. Read as liquidity, the opposite: USDT drained toward a single-digit share of the 3pool while USDC and DAI ballooned past 46%. The busiest pool was the exit—and it reversed.

**Terra, May 2022.** Roughly $50bn of UST and LUNA went to zero in a week. Badev and Watsky, covering 44 blockchains for the Federal Reserve, found the reverse of a walk to safety: chains sharing **more** bridges with Terra were **less** likely to gain relative TVL share over the next six weeks, the odds of losing share rising roughly 40% per shared bridge. The bridges worked as transmission channels, not reallocation infrastructure.

---

## What the Evidence Must Show

Reallocation needs a source, a destination, and a path between them. Two markets moving in opposite directions establish only the first two. Without linked transactions, the migration claim remains an inference.

A visible path shows only that reallocation is possible—Terra shows that the same path can carry a shock instead. Volume is not depth either: volume counts events, while depth determines what can be executed. Curve had record volume with a deteriorating pool on the same day. Holder counts can mislead for the same reason; a market can add holders while its book thins.

---

## A Visible Path Through Five Wrappers

On 12 June 2026 SpaceX began trading on Nasdaq—priced at $135, opened at $150, and closed at $160.95. For four months beforehand, claims on the same exposure were already trading on Solana. The plumbing is public: every wrapper is a mint address with issuer-controlled metadata, every swap a transaction. If migration is measurable rather than inferred, it should be measurable here.

It is messier than the ticker suggests. Nine Solana mints carry a SpaceX-like symbol and **four are squats**—including three named "SpaceX" reporting pool reserves of $454M to $1.25bn against five-figure daily volume. Identifying the substitute set already requires information the ticker does not carry. I froze the canonical-mint list before comparing the post-IPO outcomes; inclusion required issuer-attributable on-chain metadata or issuer documentation, not a volume cutoff.

The five canonical wrappers do not form one market:

- **`SPACEX` (PreStocks)** is pre-IPO economic exposure through an SPV. The holder can swap into `SPCXx` or any other token, but must act before 12 March 2027. Unconverted tokens expire worthless.
- **`tSpaceX` (Tessera)** is a loan participation right, not a security. Redemption waits for the SPV to divest the underlying exposure; the holder cannot trigger it.
- **`SPCX` (Backpack Securities)** represents a real share held 1:1 in regulated custody. The holder can reach the actual share through ACATS/DTCC.
- **`SPCXx` (Backed)** and **`SPCXon` (Ondo)** both use issuer primary markets, but access differs sharply. Backed requires KYC and a $5,000 minimum. Ondo starts at $1 and excludes US holders.

On a screen, these are five ways to own SpaceX. In the plumbing, one can expire, one waits on the issuer, one reaches the real share, and two depend on primary-market access.

These differences existed before the IPO. The event made their consequences easier to observe.

---

## The Designated Path Carried 3.5% of Supply

PreStocks names the conversion target itself—`SPCXx`, by mint address—with a deadline of 12 March 2027, after which unconverted tokens expire worthless. Conversion happens "through normal trading," so the route is a public swap venue, and a pool for exactly that pair appeared at 16:23 UTC on listing day.

Here the path is visible, and net flow through it was small.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-08-30-liquidity-migration/fig02_visible_path_conduit.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-08-30-liquidity-migration/fig02_visible_path_conduit.png"
         alt="Daily gross flow in both directions through the SPACEX/SPCXx pair, and the wandering cumulative net which ends near 3.5% of supply"
         style="max-width:100%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem; line-height: 1.55;">
    <strong>Fig. 1.</strong> All <code>SPACEX</code>↔<code>SPCXx</code> swaps on Solana, matched on the mint pair rather than a single pool, measured on the <code>SPACEX</code> leg in tokens. Panel B cumulates the net over 12 June – 14 August; the right axis expresses it against total <code>SPACEX</code> supply of 8,742.6 tokens. A swap in this pair accomplishes what the conversion terms require, but the pool is not issuer-operated and some flow is ordinary trading or arbitrage. Neither gross nor net flow identifies one-way conversion. Source: Dune <code>dex_solana.trades</code>; mint-pair flow frozen 12 June – 14 August 2026.
  </div>
</div>

Gross flow into `SPCXx` over nine weeks: 1,586 tokens. Gross flow back: 1,283. **Net: 303 tokens, or 3.5% of supply.**

Four-fifths of the traffic on the conversion route was offset by flow in the other direction. The cumulative line goes negative on four days, peaks at 5.1% of supply on 12 July, then drifts back to 3.5%. A cumulative total that falls is not a one-way conversion queue; the route also carried two-way trading.

**Possible explanation, not verified here:** traders may have been trading around the lockup discount. PreStocks discloses that underlying shares unlock in tranches over six months and that the token trades at a market-priced discount until they do. The swaps do not identify trader intent.

Gross volume counts both directions, so I do not treat it as one-way reallocation.

Supply says something separate, and the two numbers should not be netted against each other. `SPACEX` cumulative net mint-minus-burn was 5,623.03 tokens on 11 June and 5,622.76 on 14 August—**−0.27 tokens** across the whole post-IPO period. Whatever trading occurred, it was not accompanied by a material contraction in observed net issuance.

That is not the same as "97% unconverted." Holders were free to swap into anything else, and those exits appear in neither figure. The evidence supports two separate facts: small net flow along the designated path, and almost no change in observed net issuance.

The designated route never carried most of the flow either: `SPCXx` was 11.3% of all `SPACEX` selling in the event week, 43.2% during settling, 15.8% recently. The issuer's "or any other token" is doing real work.

Nor was it where post-IPO trading concentrated. In the event week, Backpack's `SPCX`—the only one redeemable into an actual share—traded **$23.47M against `SPCXx`'s $3.28M**. That says where activity gathered, not where `SPACEX` holders went. The two measurements should remain separate.

---

## The IPO Did Not Empty the Neighbourhood

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-08-30-liquidity-migration/fig01_one_ipo_two_market_families.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-08-30-liquidity-migration/fig01_one_ipo_two_market_families.png"
         alt="Two panels of normalized daily DEX volume around 12 June 2026; the PreStocks pre-IPO tokens collapse together while Backed xStock controls stay flat"
         style="max-width:100%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem; line-height: 1.55;">
    <strong>Fig. 2.</strong> In this sample, issuer family lines up with the post-event pattern better than SpaceX exposure does. Daily DEX swap volume per token, divided by each token's own median over 12 Feb – 30 Apr 2026, log scale, trailing 7-day median. Dashed line is the first Nasdaq trade; dotted lines are the IPO pricing date and the 7 Aug unlock. Panel B groups are medians across tokens. Volume is an activity measure and is not depth; quoted depth could not be reconstructed historically. Source: Dune <code>dex_solana.trades</code>, canonical mints only; frozen 1 February – 14 August 2026. Window medians are true medians.
  </div>
</div>

A 3.5% net flow is small but not zero. Did the IPO drain the market around it? `SPACEX` activity moved in that direction: 1.32× baseline during the anticipation window, 0.47× during IPO week, **0.02×** through late June and July, and 0.01× by August.

The control group breaks that explanation. **Anthropic's and xAI's pre-IPO tokens—companies that did not go public—fell to 0.02× over the same windows**, closely enough that Panel B shows two lines on top of each other. Five Backed xStocks held as controls finished at 1.10× baseline; the two xStock peers at 1.69×.

**Note:** `SPYx` reached 12.6× baseline in the event week, against a control median of 1.6×. A broad-index reaction to the IPO is plausible but not verified. The group result uses the median, so this observation does not determine it.

In this sample, the split followed **issuer families** more closely than exposure to SpaceX. One issuer's product line went quiet; tokenized equities on the same chain, venues, and token standard did not. The data do not identify why PreStocks went quiet.

**Possible explanation, not verified here:** one possibility is an issuer-level liquidity or distribution shock—for example, a market maker reducing inventory across several PreStocks products. I do not have historical LP attribution or issuer-side traffic data to test that mechanism.

The timing also disagrees with an immediate IPO effect. `SPACEX` was still above half its baseline during listing week; the larger decline came later. The untied wrapper followed another path: `tSpaceX` held 0.80× through the settling window, a **40×** gap against `SPACEX`, and only fell to 0.22× five weeks later.

A mechanism in which the SpaceX listing emptied its own substitutes cannot explain why Anthropic's pre-IPO token died at the same rate on the same schedule.

---

## What the Wrapper Terms Allowed

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-08-30-liquidity-migration/fig03_connected_vs_unconnected.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-08-30-liquidity-migration/fig03_connected_vs_unconnected.png"
         alt="Left panel: normalized volume for SPACEX and tSpaceX. Right panel: supply paths, with tSpaceX flat at 1,190 tokens throughout."
         style="max-width:100%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem; line-height: 1.55;">
    <strong>Fig. 3.</strong> Supporting figure. The wrapper with a holder-executable conversion route beside the one without. Panel B is cumulative net mint minus burn from 1 Feb 2026, so it is a change series rather than an absolute level. The figure does not attribute the activity difference in Panel A to the architectural difference—issuer is not held constant between the two, and the confound in Fig. 2 is unresolved.
  </div>
</div>

The cleanest fact in the exercise is the flat blue line. **`tSpaceX` was minted once, 1,190.0000 tokens on 9 February, and stood at 1,189.9971 on 14 August**—a decline of 0.003 tokens, or 0.0002%, spread across about two dozen dust-sized burns. No redemption of any economic size occurred, straight through the SpaceX IPO.

That is consistent with the architecture. Tessera's on-chain metadata describes a loan participation right held through a Cayman segregated portfolio, with redemption triggered by "divestment of the underlying exposure." The holder cannot initiate it. No divestment occurred, so no redemption occurred—the routes that were available and the routes that were used are the same set.

The terms tell us which exits holders could initiate, but they cannot by themselves explain why `SPACEX` and `tSpaceX` later traded differently; issuer and liquidity-provider effects remain mixed together.

The difference is not only legal. I recorded Jupiter quotes for four of the five wrappers every half hour for a week—311 captures—at $1,000, $10,000 and $50,000, in both directions. `SPCXon` is absent because its mint could not be confirmed against issuer-controlled metadata, so it never entered the frozen universe. At $50,000 the quoted buy impact ran from 14 bps on `SPCX` to **4,664 bps** on `SPACEX`: a 300-fold range across four claims on one company.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-08-30-liquidity-migration/fig04_depth_buy_vs_sell.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-08-30-liquidity-migration/fig04_depth_buy_vs_sell.png"
         alt="Panel A: quoted price impact at $50,000 by wrapper, buy versus sell. Panel B: share of captures with a routable quote; SPACEX sell is routable in 13 percent while the others are routable in 97 to 100 percent."
         style="max-width:100%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem; line-height: 1.55;">
    <strong>Fig. 4.</strong> Jupiter quotes for a $50,000 order, both directions, every ~32 minutes over 7–14 August 2026 (311 captures). Panel A is the median price impact <em>conditional on a routable quote existing</em>; Panel B is how often one did. Read together: <code>SPACEX</code>'s sell bar in Panel A looks cheaper than its buy bar only because it is measured on the 13% of captures where the sell was possible at all. Quoted depth, not executed trades.
  </div>
</div>

| Wrapper | Issuer | $10k buy | $50k buy | $50k **sell** |
|---|---|---|---|---|
| `SPCX` | Backpack Securities | 5 bps | 14 bps | 17 bps |
| `SPCXx` | Backed | 18 bps | 75 bps | 29 bps |
| `tSpaceX` | Tessera | 21 bps | 115 bps | 117 bps |
| `SPACEX` | PreStocks | 788 bps | 4,664 bps | 1,456 bps, **routable in 13% of captures** |

Jupiter returned a routable $50,000 buy quote for `SPACEX` in every one of the 311 captures. It returned a routable $50,000 *sell* quote in 13% of them, and returned none for a $10,000 sell in 19% of them. A quote to buy into the expiring wrapper was always available; a quote to get out at size usually was not.

That asymmetry is the part a single-direction measurement hides, and it matters here more than the headline basis points, because the trade this wrapper's holders face before March 2027 is the sell. The three wrappers with a working exit route quote both directions at comparable cost. The one with a deadline does not.

*(These quotes are the 7–14 August book; historical quotes cannot be reconstructed.)*

---

## Where the Evidence Stops

The route was visible, sanctioned by the issuer, and open on a public venue for nine weeks. Net flow through it remained small, and observed net issuance barely changed. Meanwhile, wrappers with no IPO also lost activity. These observations do not support a simple migration story; they do not identify the mechanism behind the wider decline.

The public trail stops in three places.

- **Depth during the event.** Jupiter quotes are live-only, so historical executable depth cannot be reconstructed after the fact. The charts measure activity, participation, or supply. The basis-point comparison is the 7–14 August book, not the June book; that week was recorded prospectively for exactly this reason, and the recording continues for the next event.
- **Activity outside Solana DEXs.** `SPCXx` also trades on Kraken and Bybit; Backpack's token trades on its own exchange. The direction of the resulting coverage bias is unknown.
- **Why PreStocks went quiet.** The control group isolates the mismatch. It does not explain it.

The window is also incomplete. `tSpaceX` was still falling in the last interval, and net flow on the designated route was still drifting down in August.

---

## Closing

These wrappers were easier to put on one screen than to treat as one market. They differed in who could redeem, what redemption delivered, when it could happen, what a fixed-size trade cost—and whether it could be routed at all. The issuer-designated pair made one exit visible, but most of its gross flow was offset in the other direction.

A route tells us what holders can do, not what they did. If one market loses activity while another gains it, I would call that an activity shift until transactions connect the source to the destination.

---

## Appendix: Sources

- **Market data:** Dune `dex_solana.trades` and `tokens_solana.transfers`; live Jupiter quotes captured every ~32 minutes from 7–14 August 2026 (311 captures). The [data-processing Gist](https://gist.github.com/egpivo/657162cecaee71daac5abec45c209a25) contains the frozen universe configuration, Dune SQL, the depth collector, the transformation scripts, and the processed CSVs behind every figure. Plotting code is not included.
- **Wrapper terms:** [PreStocks](https://prestocks.com/spacex), [Tessera `tSpaceX` metadata](https://cdn.tesseralab.co/tessera/t-spacex.json), and [Backpack on `SPCX`](https://learn.backpack.exchange/articles/how-to-hold-spcx).
- **SpaceX IPO:** [CoinDesk](https://www.coindesk.com/tech/2026/06/10/spacex-stock-is-coming-to-solana-on-the-same-day-it-lists-on-nasdaq) and [CNBC](https://www.cnbc.com/2026/06/12/spacex-ipo-spcx-live-updates.html).
- **Comparison cases:** Federal Reserve, [*Interconnected DeFi: Ripple Effects from the Terra Collapse*](https://www.federalreserve.gov/econres/feds/files/2023044pap.pdf); CoinDesk, [*Curve's $500M stablecoin pool hammered as traders flee USDC*](https://www.coindesk.com/business/2023/03/10/defi-protocol-curves-500m-stablecoin-pool-hammered-as-traders-flee-usdc).
