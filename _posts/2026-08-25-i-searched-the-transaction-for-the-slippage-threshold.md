---
layout: post
title: "I Searched the Transaction for the Slippage Threshold. I Found the Quote Instead."
date: 2026-08-25
tags: [Solana, DeFi, Market Structure, Rust, Finance]
image: /assets/2026-08-25-i-searched-the-transaction-for-the-slippage-threshold/hero.png
---

*Thirty read-only DFlow `/order` responses, ten A1/T/A2 brackets, and a byte search for the minimum-output threshold inside unsigned Solana transactions. No private key, nothing signed, nothing submitted.*

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-08-25-i-searched-the-transaction-for-the-slippage-threshold/hero.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-08-25-i-searched-the-transaction-for-the-slippage-threshold/hero.png"
         alt="DFlow order response quantities Q and M against an unsigned Solana instruction: Q matches at offset 99 as a numeric candidate; M is not recovered as a literal"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem; line-height: 1.55;">
    <strong>Overview.</strong> The response names both the quote and the minimum-output threshold. Inside the unsigned transaction, a quote-valued literal recurs at ix 2 / offset 99; the threshold is not recovered as a literal. Schematic of the encoding finding—not a fill.
  </div>
</div>

---

## Slippage Moved. So Did the Transaction.

The setup is small. USDC→SOL orders to DFlow’s developer `/order` endpoint, 100 USDC in, platform fee at zero, one field varied: `slippageBps`. Each response returned a quote and an unsigned versioned Solana transaction.

`slippageBps` enters the returned minimum-output threshold mechanically. The observed relation was exact; the formula is below. Each request also returned a different transaction. A quote is JSON with named fields. An instruction payload here is 111 bytes with no field names. Which response quantities stay legible after that gap?

[Part II]({{ site.baseurl }}/2026/08/18/the-interface-says-dflow-can-the-transaction-prove-it.html) asked what one unsigned capture preserves about the router. This piece asks what a controlled parameter change preserves as a literal inside the compiled bytes.

## Why a Raw Diff Is Not Enough

The tempting move is to diff two unsigned transactions, treat the changed bytes as slippage encoding, and stop.

In one otherwise clean bracket, exactly one instruction payload changed between a 50 bps request and a 100 bps request. Seventy of its 111 bytes differed. That is not a self-identifying slippage field. The diff shows the payload moved. It does not say which bytes belong to slippage.

Two live router calls are not two draws from a fixed system. Between any pair the router can reprice, reroute, or pick a different market on the same venue. Diff two routes and you mostly measure the route change.

## Ten A1/T/A2 Brackets

Each batch is three requests:

```text
A1  50 bps   (anchor)
T   10 or 100 bps   (treatment)
A2  50 bps   (anchor)
```

Ten batches, thirty requests, alternating 10 bps and 100 bps treatments. The anchors share the same setting so they can catch route drift around the treatment. I kept the bracket short on purpose: longer windows would invite more mid-bracket reroutes, and the question here is byte recoverability, not long-horizon market dynamics.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-08-25-i-searched-the-transaction-for-the-slippage-threshold/fig1_bracket.svg" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-08-25-i-searched-the-transaction-for-the-slippage-threshold/fig1_bracket.png"
         alt="Bracket 6: the two 50 bps anchor requests both returned the Tessera V route on fingerprint 78e349e7, while the 10 bps treatment request between them returned BisonFi on fingerprint dea0ce94"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem; line-height: 1.55;">
    <strong>Fig. 1.</strong> Batch 6: both anchors on Tessera V (<code>78e349e7</code>); the 10 bps treatment on BisonFi (<code>dea0ce94</code>). The bracket is excluded—anchor agreement is necessary for a usable comparison, not sufficient to attribute what differs.
  </div>
</div>

## Route and Topology Eligibility

Each response route is hashed into a fingerprint. Writing r<sub>i</sub> for that fingerprint and τ<sub>i</sub> for the decoded transaction topology, the eligibility rule for a bracket is:

<p style="text-align:center; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; line-height: 1.7; margin: 1.25rem 0;">
  E<sub>b</sub> = 1{ r<sub>A1</sub> = r<sub>T</sub> = r<sub>A2</sub> } × 1{ τ<sub>A1</sub> = τ<sub>T</sub> = τ<sub>A2</sub> }
</p>

r covers venue, market key, mint pair, leg order and allocation; τ covers the program set, account and lookup-table topology, and the instruction layout. Both definitions were frozen in code before any live results were inspected. Compare byte-for-byte only when E<sub>b</sub> = 1.

Five of ten survived: batches 1, 2, 5, 8, and 9. The other half failed the route or topology gate. That cuts the usable sample in half before the search starts. Comparing byte offsets across different instruction layouts would be worse. Full table: [project site](https://egpivo.github.io/onchain-execution-lineage/#/explore/dflow-slippage/route).

Batch 3 shows why the fingerprint is stricter than a venue label. A1 and T both returned HumidiFi on `87aeaaaf`; A2 returned HumidiFi on `15921ffa`. Same venue name, different market key. A venue-only rule would have called that bracket stable and let a topology mismatch into the byte search.

### Route Stability Is Only a Filter

Route sits below both the parameter set and the market state that cannot be measured: S → R ← U. Keeping brackets whose route happened to repeat selects on that shared child. Nothing issued do(route = r).

The latent market state is neither observed nor held fixed. The anchors only screen for visible route drift around the treatment. An eligible bracket is narrower than it looks. Observed route and transaction topology stay stable, so byte offsets are comparable across the three requests. That is a forensic filter, not a controlled direct effect. Formally, the eligible comparison conditions on an observed route; it does not identify the form that would require intervening on route:

<p style="text-align:center; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; line-height: 1.7; margin: 1.25rem 0;">
  P(B | do(S), R = r)&nbsp;&nbsp;&nbsp;versus&nbsp;&nbsp;&nbsp;P(B | do(S), do(R = r))
</p>

Observing a stable route is not holding the route fixed.

<div style="text-align:center; margin: 1.5rem 0;">
  <a href="https://egpivo.github.io/onchain-execution-lineage/#/explore/dflow-slippage/identification" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-08-25-i-searched-the-transaction-for-the-slippage-threshold/fig2_identification_play.gif"
         alt="Animated walkthrough of the identification model: structural, intervention, route-stable selection, and evidence modes; routePlan is highlighted under selection"
         style="max-width:min(960px, 98%); height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem; line-height: 1.55;">
    <strong>Fig. 2.</strong> Working identification model. Interactive walkthrough: <a href="https://egpivo.github.io/onchain-execution-lineage/#/explore/dflow-slippage/identification" target="_blank" rel="noopener noreferrer">project site</a>. <code>routePlan</code> is a shared child of assigned <code>slippageBps</code> and unmeasured market state. Route-stable eligibility is selection, not <code>do(route = r)</code>; arrows are structural assumptions, not measured effects.
  </div>
</div>

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-08-25-i-searched-the-transaction-for-the-slippage-threshold/fig2_pipeline.svg" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-08-25-i-searched-the-transaction-for-the-slippage-threshold/fig2_pipeline.png"
         alt="Five stages: the request carries slippageBps; the response carries named fields outAmount and otherAmountThreshold with the threshold exact in 30 of 30; a route and topology gate admits 5 of 10 brackets; in the admitted transactions the quote is found at instruction 2 offset 99 in all 15 while the threshold is not recovered; settlement sits beyond the observation boundary with no observation"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem; line-height: 1.55;">
    <strong>Fig. 3.</strong> Named response fields become unnamed instruction bytes. The threshold is exact at the response; a quote-valued literal candidate appears at ix 2 / offset 99; settlement is never observed. The gate is a filter on an observed value, not an intervention.
  </div>
</div>

## The Exact Response Invariant

Before any byte search, one response-level relationship can be checked exactly. Across all thirty responses:

<p style="text-align:center; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; line-height: 1.7; margin: 1.25rem 0;">
  M<sub>i</sub> = ⌈ Q<sub>i</sub> × (10000 − S<sub>i</sub>) / 10000 ⌉
</p>

where S is the requested `slippageBps`, Q is the quoted `outAmount`, and M is `otherAmountThreshold`. Thirty of thirty, exact, in integer token base units. `minOutAmount` equalled `otherAmountThreshold` in every observation.

I also checked the floor form. It matches zero of thirty. These are `u64` base units, so the two rules differ by at most one unit. That one unit decides which side of the exact percentage boundary the returned minimum sits on.

This is exact within this experiment, on this endpoint, in this execution mode. It is not a claim about every DFlow path.

## The Formal Byte Search

For a payload B<sub>i</sub><sup>(k)</sup> (instruction k of request i) and a value v, define the search operator over a fixed encoding family F:

<p style="text-align:center; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; line-height: 1.7; margin: 1.25rem 0;">
  H<sub>F</sub>(B<sub>i</sub>, v) = { (k, p, e) : decode<sub>e</sub>( B<sub>i</sub><sup>(k)</sup>[p : p+|e|] ) = v, e ∈ F }
</p>

In words: the positions where v appears as a literal under one of the encodings actually tested. F here is only what the runner implements: 8- and 4-byte little- and big-endian integers. I therefore kept the encoding family fixed rather than expanding it after seeing the misses.

An empty H<sub>F</sub>(B, M) means the value was not recovered under this search. It does not prove the value is absent from the transaction.

Three values were searched per request: the threshold M, the quote Q, and their difference Q − M. The search covered every instruction payload of all fifteen transactions in the five eligible brackets, not only the payloads that changed.

## The Recurring Quote Candidate

The target was M. Its exact value is known from the response body, and S enters its response-level formula mechanically. If slippage were written into the instruction as an obvious literal, this is where it would appear.

It did not appear. Neither did the difference.

In all fifteen eligible-bracket transactions, H<sub>F</sub>(B, M) and H<sub>F</sub>(B, Q − M) were empty. Q matched uniquely at the same site every time: instruction 2, offset 99, 8-byte little-endian. Per-bracket rows are on the [byte search page](https://egpivo.github.io/onchain-execution-lineage/#/explore/dflow-slippage/bytes?batch=1).

Formally, for every eligible observation:

<p style="text-align:center; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; line-height: 1.7; margin: 1.25rem 0;">
  H<sub>F</sub>(B<sub>i</sub>, M<sub>i</sub>) = ∅&nbsp;&nbsp;&nbsp;H<sub>F</sub>(B<sub>i</sub>, Q<sub>i</sub> − M<sub>i</sub>) = ∅&nbsp;&nbsp;&nbsp;(2, 99) ∈ H<sub>F</sub>(B<sub>i</sub>, Q<sub>i</sub>)
</p>

The quote matched in all fifteen transactions, not only the five treatments. One position per transaction, always the same offset.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-08-25-i-searched-the-transaction-for-the-slippage-threshold/fig3_byte_search.svg" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-08-25-i-searched-the-transaction-for-the-slippage-threshold/fig3_byte_search.png"
         alt="Three quantities were searched for in the instruction payloads: the minimum-output threshold produced no match, the quoted outAmount matched at instruction 2 offset 99, and their difference produced no match"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem; line-height: 1.55;">
    <strong>Fig. 4.</strong> Search outcomes for M, Q, and Q − M. The shaded row is the target. A match at offset 99 is a recurring numeric coincidence, not a named protocol field.
  </div>
</div>

Every observed amount is below 2³², so the 8-byte little-endian form is the 4-byte form followed by four zero bytes: `5a 5a e7 51 00 00 00 00`. A 4-byte read of the same offset therefore also matches. One physical location, not two independent findings. The 8-byte form is reported because that is what the payload holds.

## A Same-Treatment Control

The recurring position might just be an artefact of the treatment contrast. The brackets already contain a test.

`A1` and `A2` carry the same 50 bps setting, so the slippage contrast between them is zero. The quote still drifted between them in all five eligible brackets; live market, seconds apart. With ΔS = 0 and route and topology identical, does the candidate position sit still, or does it follow the quote?

It followed the quote. In all five brackets the position carried each response’s own `outAmount`, with no change in slippage at all.

So the position is not written only when the treatment changes. With slippage fixed, it still moved with the quote. That says nothing about what the field means. Another quantity carrying the same value would look identical here.

## What the Experiment Identifies

At the response layer, slippage is fully explicit: a named field, an exact integer relation to the threshold, 30/30, floor rule excluded 0/30. One stage later, under the tested encoding family, that threshold is not recoverable as a literal in any of the fifteen eligible-bracket transactions. A quote-valued literal is recoverable in all fifteen, at one stable and unique offset.

Both readings stop at the same search boundary. A different encoding family, a scaling, or a packed representation could move the second result. I stopped at integer endianness because that is the family I froze before looking; I do not have an IDL or official decoder that would justify a wider hunt.

Offset 99 has no name here. What is in hand is a recurring, unique numeric coincidence between a response field and a payload slice. Calling it the `outAmount` field would need an IDL, an official decoder, or a protocol schema.

The threshold may still be in the transaction. All that can be said is that it was not recovered as an exact literal under the encoding family tested. Scaled, packed, or derived representations remain open. Where topology failed the stability rule, route differences stay unattributed. Nothing was signed or submitted, so nothing about landed fills or realized price follows.

---

## Closing

I knew which quantity was mechanically tied to the assigned slippage setting, knew its exact value from the response, and searched for it inside comparisons where the observed route and topology stayed stable. What kept matching, in every request including the ones with no treatment contrast at all, was the quote.

A transaction diff is evidence. It is not an attribution rule.

---

## Appendix

- Prior: [Part I]({{ site.baseurl }}/2026/08/16/different-apps-same-router.html) · [Part II]({{ site.baseurl }}/2026/08/18/the-interface-says-dflow-can-the-transaction-prove-it.html)
- Evidence and walkthroughs: [DFlow slippage case](https://egpivo.github.io/onchain-execution-lineage/#/explore/dflow-slippage) · reproduce: [`egpivo/onchain-execution-lineage`](https://github.com/egpivo/onchain-execution-lineage) (`./scripts/reproduce_slippage_article.sh`)
- Scope: 30 `/order` responses · 10 brackets · 5 eligible · USDC→SOL · 100 USDC · platform fee 0 · unsigned only; raw captures stay local
