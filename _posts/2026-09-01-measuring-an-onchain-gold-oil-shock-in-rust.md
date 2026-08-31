---
layout: post
title: "Measuring a Commodity Shock in Tokenized Markets with a Rust CLI"
date: 2026-09-01
tags: [RWA, Market Structure, DeFi, Ethereum, Finance]
image: /assets/2026-09-01-measuring-an-onchain-gold-shock-in-rust/hero.png
---

On 8 July 2026, renewed U.S.–Iran escalation coincided with opposite moves in two commodity benchmarks: spot gold fell 0.52%, while front-month WTI settled 4.4% higher. The [same Reuters market report](https://www.investing.com/news/economy-news/oil-jumps-and-bonds-dip-as-us-strikes-iran-4780549) carried both numbers.

The benchmarks moved. The open question was whether the tokenized markets moved with them—by how much, and whether those responses stuck.

Shocktrace is the tool for that question. It freezes a shock case—identities, windows, on-chain marks, and reference returns—then returns typed measurements with the cutoffs needed to read them. This piece runs one case through it.

Four checks:

1. Same direction as the paired commodity benchmark?
2. Unusual relative to the token's own baseline?
3. Persist or reverse after the event close?
4. Unusually large gap between the two tokens?

*[Markets Are Full of Roads]({{ site.baseurl }}/2026/08/30/markets-are-full-of-roads.html) followed a visible SpaceX route. The distinction still matters here: market response is observable; capital moving between PAXG and WTIC is not.*

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-09-01-measuring-an-onchain-gold-shock-in-rust/hero.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-09-01-measuring-an-onchain-gold-shock-in-rust/hero.png"
         alt="Shocktrace architecture from frozen observations through validation and measurement to typed evidence and provenance"
         style="max-width:100%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem; line-height: 1.55;">
    <strong>Overview.</strong> A project freezes identities, windows, observations, and evidence boundaries. Shocktrace validates those inputs and returns each measurement with the assumptions needed to read it.
  </div>
</div>

---

## The Missing Comparison Was a Response Gap

The first Shocktrace build could standardize a token return, trace its later path, and compare two tokens. It could not keep an external commodity move and the token response inside one measurement object.

Putting a news percentage beside an engine result would make the comparison in prose. I wanted it in the measurement contract:

```text
frozen reference return + same-date token return
                         ↓
                   response gap
                         ↓
           direction + magnitude + cutoff boundary
```

The response branch now exposes four measurements—`response-gap`, `shock`, `horizon`, and `divergence`. Linked flow remains a separate evidence path.

This is a same-date comparison, not a causal transmission model. `response-gap` computes one descriptive quantity:

```text
response gap = token return - reference return
```

---

## Configure a Case, Extend a Metric

Shocktrace separates two kinds of work:

- A **new shock case** adds a project directory, frozen observations, and a TOML contract.
- A **new measurement** adds Rust accounting code that any project can call.

Each case is a `project.toml` plus frozen response and reference inputs. The excerpt below shows the schema shape; the full project also freezes the baseline/event windows and the WTIC asset block.

```toml
[event]
id = "us_iran_renewed_escalation_2026_07_08"
timestamp = "2026-07-08T00:00:00Z"

[[assets]]
key = "PAXG"
chain = "ethereum"
erc20 = "0x45804880de22913dafe09f4980848ece6ecbaf78"
session_calendar = "continuous"

[response]
baseline_window = "baseline"

[inputs]
response = "data/response_daily.csv"
references = "data/reference_returns.csv"
```

`00:00Z` anchors the project date; it is not an event-time synchronization point. The shared `asset_key` joins `response_daily.csv` to `reference_returns.csv`.

```bash
shocktrace validate projects/paxg_wtic_reference_2026_07_08
```

Validation catches undeclared assets, missing inputs, duplicate observations, and invalid windows. After that, the same project drives `response-gap`, `shock`, and `divergence`. For a new event, I change the project inputs and reuse the same accounting code.

The load-bearing line is deliberately plain:

```rust
let response_gap =
    token_return.map(|value| value - reference.reference_return);
```

`Option::map` keeps a missing token return as `None`; the summary carries source, cutoff, direction match, and the evidence boundary.

---

## Freeze the Shock and the Tokens

The frozen reference file holds two event-day observations:

- `GOLD_SPOT`: −0.52%, paired with PAXG.
- `WTI_FRONT_MONTH`: +4.40%, paired with WTIC.

For WTIC, `WTI_FRONT_MONTH` is the commodity benchmark chosen for this comparison—not a claim that the token tracks or redeems against that futures series.

These are same-date comparison points, not synchronized clocks. Reuters' spot-gold observation and WTI settlement are not aligned to the UTC on-chain candles, so the engine reports a response gap—not beta or tracking error.

The measured markets:

- **PAXG:** Paxos Gold on Ethereum, [`0x45804880de22913dafe09f4980848ece6ecbaf78`](https://etherscan.io/address/0x45804880de22913dafe09f4980848ece6ecbaf78).
- **WTIC:** WTI Coin on Ethereum, [`0x709ab533D18e652eCd56423d71c0241A0ee56a3b`](https://etherscan.io/address/0x709ab533D18e652eCd56423d71c0241A0ee56a3b).

PAXG price is a daily USD VWAP across twenty frozen Ethereum pools quoted in USDC, USDT, or DAI. WTIC uses the only eligible pre-event Uniswap v3 WTIC/USDC pool. Both series use UTC candle dates.

---

## Question 1 — Did the Tokens Register the Shock?

The same project commands reproduce the tables below.

```bash
shocktrace measure response-gap projects/paxg_wtic_reference_2026_07_08 \
  --asset PAXG --reference GOLD_SPOT

shocktrace measure response-gap projects/paxg_wtic_reference_2026_07_08 \
  --asset WTIC --reference WTI_FRONT_MONTH
```

| Benchmark | Benchmark return | Token | Token return | Gap | Direction |
|---|---:|---|---:|---:|---|
| Gold spot | −0.52% | PAXG | −0.92% | −0.40 pp | same |
| WTI | +4.40% | WTIC | +3.89% | −0.51 pp | same |

Direction matched on both legs. PAXG fell 0.40 percentage points more than the reported spot-gold move; WTIC rose 0.51 points less than the reported WTI move.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-09-01-measuring-an-onchain-gold-shock-in-rust/fig01_response_gap.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-09-01-measuring-an-onchain-gold-shock-in-rust/fig01_response_gap.png"
         alt="Event-day returns for paired commodity benchmarks and tokens, with token-minus-benchmark gaps"
         style="max-width:100%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem; line-height: 1.55;">
    <strong>Fig. 1.</strong> Source-reported commodity benchmark returns and same-date on-chain token returns on 8 July. Gap means token minus paired benchmark. The observations have different market cutoffs, so this is not a synchronized tracking-error estimate.
  </div>
</div>

Without the retained cutoff, `−0.40 pp` would look more precise than the clocks allow.

---

## Question 2 — Was the Token Move Unusual?

Direction match does not say whether the token itself had an extreme day. Shocktrace compares each event return with that token's own frozen baseline distribution.

| Token | Raw return | Standardized return | Baseline returns |
|---|---:|---:|---:|
| PAXG | −0.92% | −0.63σ | 90 |
| WTIC | +3.89% | +1.61σ | 48 |

PAXG tracked the negative gold direction, but the move was ordinary against its 90-return baseline. WTIC's rise was larger against its own 48-return baseline—+1.61 standard deviations.

The benchmark moves were visually clear. The token-level standardized results were more restrained. Those are different claims.

---

## Question 3 — Did the Response Persist?

Event-day response and persistence are separate outputs. The shock score uses the event-day return. Horizons stay anchored at the event close and count later priced observations.

| Priced observations after event | PAXG | WTIC |
|---:|---:|---:|
| +1 | +1.27% | −2.42% |
| +3 | +0.79% | +6.94% |
| +5 | −1.75% | +10.61% |
| +20 | −1.14% | unavailable |

PAXG reversed the event-day decline on the next observation, then moved below the event close again by its fifth priced observation. WTIC gave back part of its rise first; its fifth priced observation did not arrive until 20 July, and by then it was 10.61% above the event close.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-09-01-measuring-an-onchain-gold-shock-in-rust/fig01_onchain_paths.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-09-01-measuring-an-onchain-gold-shock-in-rust/fig01_onchain_paths.png"
         alt="PAXG and WTIC public-pool price paths indexed to the last pre-event observation"
         style="max-width:100%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem; line-height: 1.55;">
    <strong>Fig. 2.</strong> Frozen PAXG and WTIC public-pool marks, indexed to 100 at the last priced observation before 8 July. Missing WTIC dust days are not forward-filled. The path measures persistence; it does not establish capital flow.
  </div>
</div>

---

## Question 4 — Did the Token Markets Diverge Unusually?

The last check drops the commodity benchmarks and compares the two token returns directly.

```bash
shocktrace measure divergence projects/paxg_wtic_reference_2026_07_08 \
  --asset-a PAXG --asset-b WTIC
```

| Metric | Value |
|---|---:|
| Event gap | −4.8087 pp |
| Matched baseline | 48 return gaps |
| Divergence score | −1.6335 |

Opposite-signed token moves produced a wide raw gap. Against the matched baseline, it was 1.63 standard deviations below the mean—noticeable, but less unusual than the raw contrast suggests.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-09-01-measuring-an-onchain-gold-shock-in-rust/fig03_standardized.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-09-01-measuring-an-onchain-gold-shock-in-rust/fig03_standardized.png"
         alt="PAXG and WTIC event-day z-scores and their matched cross-token divergence score"
         style="max-width:100%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem; line-height: 1.55;">
    <strong>Fig. 3.</strong> Event-day PAXG and WTIC returns relative to their own baselines, plus the PAXG−WTIC gap relative to matched return dates. These are descriptive z-scores, not significance tests.
  </div>
</div>

---

## The Oil Leg Was Thin

WTIC met the case's eligibility rule, but its public market was narrow:

- one eligible pre-event pool;
- about $3,500 of event-day public-pool volume;
- 23 of 113 surface days below the $100 pricing threshold.

That does not erase the observed response. It limits how strongly I interpret it.

The engine forms a daily return only when adjacent UTC calendar days both have prices; it never relabels a bridged multi-day move as daily. That leaves 48 WTIC baseline returns. Across $0, $50, $100, and $250 thresholds, WTIC stayed at +1.56 to +1.61 standard deviations and the paired divergence at −1.57 to −1.63, so the qualitative result was stable.

WTIC's claimed one-barrel backing also remains an issuer claim unless a named attestation is attached. The measurement establishes that a token and public pool responded. It does not establish reserve quality or a canonical tokenized-WTI market.

---

## Freeze the Number

Before a number reaches the article, both input classes pass through the same engine output and claim gate.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-09-01-measuring-an-onchain-gold-shock-in-rust/fig04_freeze_pipeline.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-09-01-measuring-an-onchain-gold-shock-in-rust/fig04_freeze_pipeline.png"
         alt="On-chain pool observations and event-day reference returns merge into engine JSON, claim gate, then article"
         style="max-width:100%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem; line-height: 1.55;">
    <strong>Fig. 4.</strong> Two frozen input classes join one path: engine JSON → claim gate → article. Schematic of the provenance boundary, not a runtime topology.
  </div>
</div>

Reference rows retain source and cutoff. The on-chain freeze retains contracts, pool universes, UTC dates, and the dust rule. Regression tests enforce adjacent-day returns, priced-observation horizons, response-gap subtraction, matched-date divergence, and missing values.

---

## Closing

Direction matched on both legs. The standardized sizes and later paths did not.

PAXG's event-day move was ordinary against its own baseline and reversed quickly. WTIC's standardized move was larger, although it came from a thin and discontinuous public-pool surface; no linked flow between the two markets was measured.

Shocktrace was not for making a z-score faster. It was for asking the next shock question without changing the accounting underneath it.

The next useful input is a synchronized reference series. Until then, the reference-to-token response gap remains a same-date comparison—useful, but deliberately bounded.

---

## Appendix

- Repository: [`egpivo/shock-to-migration`](https://github.com/egpivo/shock-to-migration)
- PAXG: [`0x45804880de22913dafe09f4980848ece6ecbaf78`](https://etherscan.io/address/0x45804880de22913dafe09f4980848ece6ecbaf78)
- WTIC: [`0x709ab533D18e652eCd56423d71c0241A0ee56a3b`](https://etherscan.io/address/0x709ab533D18e652eCd56423d71c0241A0ee56a3b)
