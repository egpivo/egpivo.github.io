---
layout: post
title: "What Can a Landed Solana Transaction Actually Prove About DeFi Execution?"
date: 2026-08-28
tags: [Solana, DeFi, Market Structure, Blockchain, Finance]
image: /assets/2026-08-28-what-can-a-landed-solana-transaction-prove/hero.png
---

### TL;DR

- I reconstructed execution provenance for all **6,695** successfully landed rows in a frozen SPYx × OKX router candidate set. Under the pre-frozen conservative registry, **4,677 of 6,695 rows (69.86%)** received a registry-supported route/source classification.
- All **2,018** remaining transaction records were retrieved; those rows abstained because the conservative registry lacked a venue-role mapping. The blocker is venue attribution, not retrieval.
- Swap in an expanded registry and the same transactions reach **100%** coverage — but part of that mapping layer was learned from this dataset. **The chain evidence did not change. The interpretation layer did.**
- Provenance inside the frozen table is uneven: the mapping appearing on the most attributed rows carries only a partial-independence, medium-confidence grade. Anything downstream that separates public-pool from proprietary liquidity inherits that, not just the headline rate. This note estimates none of those quantities; it measures the input they would start from.
- **Scope:** four observed clock-hours in two disjoint collection bursts, success-conditioned. Not all SPYx activity, not all OKX router activity, not a continuous market window.

---

An incomplete registry producing incomplete classification is obvious. The measurement here is how much attribution survives when the registry is frozen before reconstruction, and how that coverage changes when mappings learned from the target sample are allowed back in.

That raw ledger data underdetermines economic meaning is established prior art: [DeFiRanger](https://arxiv.org/abs/2104.15068) names the gap and introduces *semantic lifting*, [GraphSense](https://arxiv.org/abs/2102.13613) versions attribution tags with provenance, and [Disentangling DeFi Compositions](https://arxiv.org/abs/2111.11933) depends on a hand-built protocol set that is not onchain. What this adds is a measured coverage rate for one router, with the abstention rule and the registry's provenance both stated.

---

## One transaction, end to end

Signature [`2LU6WK48…EQYXL5JX`](https://explorer.solana.com/tx/2LU6WK48r9vtM3H9SkbYahArgUZ7PdUFh62KSoqYiUxCMNP9eN28KY9tqrbPDK6vKGwvHuQuz9gS37ikEQYXL5JX). Landed, successful, two venue legs. Relevant excerpts from the same log stream — non-contiguous, taken from lines 8, 21, 23, 37 and 39 of 63:

```
Program proVF4pMXVaYqmy4NjniPh4pqKNfMmsihgd4wdkCX3u invoke [1]
...
Program log: Dex::AlphaQ amount_in: 328735290, offset: 0
Program ALPHAQmeA7bjrVuccPsYPiCvsi428SNwte66Srvs4pHA invoke [2]
...
Program log: Dex::Tessera amount_in: 201482921, offset: 15
Program TessVdML9pBGgG9yGks7o4HewRaXVAMuoVj4x83GLQH invoke [2]
```

Both legs are structurally identical: a router-emitted `Dex::` name, then a depth-2 CPI into the venue program. Registry membership is what separates them.

```
Dex::AlphaQ  → ALPHAQme… → conservative registry hit  → proprietary source
Dex::Tessera → TessVdML… → conservative registry miss → no economic role
                                                      → ABSTAIN on route class
```

The "conservative registry" is nothing exotic. It is a hand-maintained lookup table, frozen before reconstruction, mapping the router's venue names to an economic role — this is the whole thing:

```python
CONSERVATIVE_DEX_EVENTS = {
    "RaydiumClmmSwapV2": ("Raydium_CLMM",   "pooled_amm"),
    "WhirlpoolV2":       ("Orca_Whirlpool", "pooled_amm"),
    "RaydiumCPMMSwap":   ("Raydium_CPMM",   "pooled_amm"),
    "AlphaQ":            ("AlphaQ",         "prop_amm"),
    "SolfiV2WithSig":    ("SolFi_v2",       "prop_amm"),
}
block_route_on_unknown_dex = True   # an unmapped name abstains rather than guesses
```

`pooled_amm` means a public pool; `prop_amm` means a proprietary liquidity source. `AlphaQ` is in the table, so that leg resolves. `Tessera` is not, so it does not — the program identity `TessVdML…` is fully visible in the record, and the binding from that identity to an economic role is what the table lacks.

Here, "registry-supported" means the classification follows from the pre-frozen registry under the declared parser rule. It does not imply that every mapping carries identical evidence strength or full independence from the target census; those are separate dimensions, reported per mapping in the provenance manifest shipped with the [reproduction gist](https://gist.github.com/egpivo/9f38443647c676cb5b2362d4a0ae6361):

| entry | role | source | independent | confidence | tier |
|---|---|---|---|---|---|
| `WhirlpoolV2` | pooled_amm | public gist, OKX router event name | yes | high | conservative |
| `AlphaQ` | prop_amm | gist + venue registry (OKX log observation) | partial | medium | conservative |
| `Tessera` | prop_amm | frequency-mined from this census | no | low | expanded |

The grades are assigned from the source of each mapping: **yes** where the binding comes from the public gist that predates this census, **partial** where the role label draws on a third-party venue registry together with observation of OKX router logs, and **no** where the mapping was frequency-mined from this census's own swap events. The manifest covers every conservative mapping that fires on an attributed row. `RaydiumCPMMSwap` did not appear in this census and contributes nothing to the 69.86%; the remaining audited rows document selected expanded mappings.

That grade needs unpacking, because two different bindings sit behind it. The **event-to-program** association is directly observed in the router transaction: `Dex::AlphaQ` is followed by a CPI into `ALPHAQme…`, in the log excerpt above. The **venue-to-role** claim — that this program is a proprietary rather than public-pool liquidity source — rests on the registry evidence recorded in the manifest, and it is that role evidence which carries the partial-independence, medium-confidence grade. Seeing the CPI does not by itself establish the economic role.

The unevenness is not incidental. `AlphaQ` appears on 2,612 of the 4,677 attributed rows, more than any other venue, while carrying one of the two weaker grades in the conservative tier. The mapping bearing the most weight is not the one with the strongest evidence. A single coverage rate hides that; the manifest is where it becomes visible.

The landed record used here does not supply that economic-role binding. A program ID identifies the program; it does not by itself say whether the venue is a public pool or a proprietary liquidity source. In practice, indexers, explorers, and analytics pipelines that assign economic labels need some equivalent mapping layer, and those mappings can differ.

Similar semantic-mapping problems appear elsewhere in DeFi; [McLaughlin et al. (2023)](https://www.usenix.org/conference/usenixsecurity23/presentation/mclaughlin) note that venue-specific swap events on Ethereum require manual, application-specific interpretation. Here the economic distinction cannot be recovered from token movement alone, because the route class depends on whether the counterparty is a public pool or a proprietary source.

That gap decides the row. On the AlphaQ leg alone the route reconstructs as proprietary-only, but an unmapped venue could be a pooled AMM, making the route hybrid. The parser cannot rule that out, so it abstains. AlphaQ is therefore registry-supported, not independently identified from the landed record; its partial-independence grade is disclosed in the manifest. The census's own published label here also reads proprietary-only, and it changes nothing: agreement with an external label is not independent evidence.

Resolving account indices, lookup-table addresses, and the inner CPI tree is established tooling — Solana ships a [transaction introspection library](https://solana.com/docs/core/transactions/transaction-introspection) for it. The question is what economic claims survive once that decoded structure is available.

**On label leakage.** Published route labels enter only after the independent reconstruction decision, to subdivide abstained rows for diagnostic reporting. They do not map programs, assign economic roles, identify pools, or alter whether a row reconstructs.

---

## What the frozen universe covers

The candidate set was built by paging `getSignaturesForAddress` backwards from the most recent signature, over the SPYx mint and seven canonical SPYx pool addresses, deduplicating by signature and keeping transactions that touch both SPYx and the OKX router. Two collection runs produced 7,000 deduplicated candidates. Both terminated on a match cap rather than by exhausting a date range.

That cap is why the frozen data occupies **four clock-hours in two disjoint bursts** — 2026-06-21T22:00–23:59Z (1,584 rows) and 2026-06-23T23:00–2026-06-24T00:59Z (5,111 rows) — with no coverage in the ~47 hours between them. The two bursts are the two runs. Read this as two captures of OKX-routed SPYx flow, not a continuous window.

From 7,000 candidates: 6,962 landed without a program error (`meta.err == null`), 6,707 of those carried an executed USDC notional, and **6,695** fell in the primary size window, capped at $10,000 with no included row above $5,000. The 38 dropped rows landed and then errored; none were retrieval failures. N = 6,695 is complete relative to that candidate set and to nothing wider — not all SPYx activity, not all OKX router activity, not any calendar period.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-08-28-what-can-a-landed-solana-transaction-prove/figure1_field_level_recoverability.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-08-28-what-can-a-landed-solana-transaction-prove/figure1_field_level_recoverability.png"
         alt="Stacked bar chart of field-level recoverability: settlement, route or source class, public pool provenance, and routing decision"
         style="max-width:94%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem; line-height: 1.55;">
    <strong>Fig. 1.</strong> Field-level recoverability under the frozen conservative registry. The pool row runs on a different denominator — 4,687 applicable transactions, excluding 2,008 registry-supported proprietary-only paths with no public pool to name — and its candidate-set segment records account presence, which does not establish fill participation. Routing-decision fields sit outside the landed evidence set rather than measuring 0%.
  </div>
</div>

Router presence and token-balance settlement evidence were recovered for all 6,695 rows. Because the universe is success-conditioned, that 100% is a pipeline sanity check: it does not mean all attempted trades landed, and it does not imply execution economics were reconstructed. Retrieval failure contributes nothing to the reconstruction residual.

The 30.14% residual splits 21.33% / 8.81% in the frozen outputs. That split tracks whether an external published label happened to exist, not any difference in the onchain evidence, so read the residual as one category.

Under the pre-frozen conservative registry, 30.14% of rows contain at least one venue event outside the registry and therefore abstain from whole-route economic classification. All 2,018 carry such an event — partly definitional, since an unrecognised event is what triggers abstention. Its value is the decomposition: retrieval contributes zero to the residual, attribution all of it. A targeted adversarial sample re-checked the parser's reading of the same records and found 27/27 mapping-blocked rows with genuine onchain swap legs, 10/10 unclassified rows likewise, and no false positives in 13/13 attributed controls. That audit was independent of the published label and of the parser's verdict, working from the same transactions.

---

## Same evidence, different registry

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-08-28-what-can-a-landed-solana-transaction-prove/figure2_registry_sensitivity.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-08-28-what-can-a-landed-solana-transaction-prove/figure2_registry_sensitivity.png"
         alt="Two horizontal bars on a shared base: conservative table at 69.86 percent route attribution, expanded table at 100 percent with the added 30.14 percentage points hatched and marked mixed-provenance sensitivity"
         style="max-width:94%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem; line-height: 1.55;">
    <strong>Fig. 2.</strong> Registry sensitivity on identical landed evidence. The conservative table above yields 69.86% route attribution. An expanded table reaches 100% *coverage* — not 100% independently sourced attribution: the added entries have mixed provenance and include census-derived tail mappings, so it is robustness evidence rather than an independent population estimate.
  </div>
</div>

The conservative table is the main specification because it was frozen before reconstruction and excludes mappings learned from this census's published labels or event frequencies. Its entries have heterogeneous provenance and independence grades, recorded in the manifest. The expanded table is reported only as sensitivity, and its added coverage is mixed — Tessera, Manifest and GoonFi have independent external support, while tail entries such as `ByrealClmm`, `ZeroFi`, `Quantum` and `Scorch` came from this census's own swap-event frequency. No frozen artifact splits the added 30.14 percentage points into externally sourced versus census-derived shares, so neither the figure nor this text does.

Fitting part of a measurement instrument on the sample being measured is circular validation. The 69.86% rate is registry-conditioned. The discipline that survives is narrower than "use good mappings": freeze the registry before reconstruction, exclude anything learned from the target sample, and report each mapping's provenance and independence alongside the coverage rate rather than behind it.

Some bindings absent from the conservative table are available in OKX's offchain material. Absence from the frozen registry is therefore different from absence from the public world, and both differ from absence from the landed record.

---

## Pool provenance: point versus candidate set

The pool rule intersects the **full resolved account set** — static message account keys plus every address resolved through lookup tables, with no filtering to execution-relevant accounts — against a fixed list of seven canonical SPYx pool addresses. Exactly one candidate yields point identification. Two or more leaves a narrowed candidate set, because presence in a declared account list does not establish which pool supplied a fill.

Among the 4,687 applicable trades, 2,038 name exactly one canonical pool — **43.48% point identified** — and a further 1,934, or **41.26%**, name two to five (1,492 name two, 352 three, 87 four, 3 five). Point-or-candidate-set coverage reaches 84.75%, carrying that same caveat. 1,906 of those 1,934 also show two or more distinct mapped venue events, consistent with multi-venue routing.

The distinction matters downstream. Route class answers composition questions; pool-level work needs pool identity — liquidity concentration, fee-tier attribution, pool-specific price impact, LP analysis, some MEV attribution, reproducible execution-cost studies. A transaction can be route-class identified and still insufficient for a pool-level question, and counting single-venue fills as attributed while dropping multi-venue splits can bias concentration estimates toward venues that route alone.

---

## What the gaps imply

Retrieval, attribution, resolution, and route selection are different engineering problems. RPC retrieval is complete within the frozen set. Route attribution depends on the venue registry. Pool attribution is limited by using the resolved account set rather than leg-level account participation. And unselected route alternatives are outside the landed transaction evidence used here. The last two are implementation questions rather than claims that Solana itself lacks information.

The reason pool attribution stops where it does is Solana-specific: [the resolved account set](https://solana.com/docs/core/transactions/transaction-structure) is a declaration of accounts available to the transaction, not a record of which account supplied each fill.

Route selection bounds a different class of question. Landed transactions support realized-execution claims; best-execution and route-choice estimands need a separate quote, intent, or counterfactual source — which is why [Bachu, Wan & Moallemi (2024)](https://arxiv.org/abs/2405.00537) construct a counterfactual baseline rather than reading one off the chain.

That distinction is not only descriptive. A lending protocol assessing collateral liquidation risk may want to distinguish liquidity that is publicly observable and permissionlessly LP-funded from liquidity supplied by a private market maker — [liquidation being a forced sale of collateral at a discount](https://arxiv.org/abs/2106.06389). How either source should be treated under stress is a separate modelling question, and this audit says nothing about it. The point is narrower: if a liquidation-capacity estimate, collateral haircut, or liquidity score is built using that distinction, it inherits the attribution assumptions used to construct it.

[Zhu et al. (2024)](https://arxiv.org/abs/2410.19107) illustrate why analyses of DEX liquidity may separate internalized order flow from publicly pooled liquidity. Their setting and definitions are not the same as this audit's, but the comparison is the reason to report the provenance of any venue-role classification rather than treat it as given.

This note estimates none of those quantities. It identifies an input they would depend on.

Because downstream measurements can depend on the distinction, the measured ambiguity becomes an application-layer question rather than only a parsing one. One way to frame it for Solana applications: a small attribution feature surface, exposing enough metadata to make venue role and execution-leg provenance independently auditable, without asking the runtime to interpret economic meaning.

| Measured gap | Possible application feature |
|---|---|
| 30.14% route abstention; 69.86% → 100% on a registry swap | versioned venue-role metadata with explicit provenance |
| 43.48% pool point ID, a further 41.26% candidate-set only | explicit leg → pool/market metadata |
| route alternatives off-record | optional route/quote commitment — a design question, not a measured defect |

These are not proposed protocol requirements. They are candidate application features that would make specific economic claims easier to audit from the same transaction evidence. The literature reviewed here does not settle who should own these bindings or what the minimal surface should contain — they are maintained as engineering practice, via the [Program Metadata Program](https://solana.com/developers/guides/advanced/idls), [TagPacks](https://arxiv.org/abs/2102.13613), and vendor label sets. That makes them useful questions for builders rather than claims this audit has already answered.

The OKX-routed transactions studied here already emit venue names such as `Dex::AlphaQ` and `Dex::Tessera`. The open question is what the smallest additional machine-readable binding would be that makes the economic role independently auditable.

---

## Scope and next steps

**Scope.** One asset, one router, two capped collection bursts spanning four observed clock-hours, 155 signers, trades under $10,000, one registry version, success-conditioned throughout.

**Next steps.** The obvious replications are SOL/USDC through OKX, SPYx through another router such as Jupiter, and a continuous collection window. I expect the 69.86% rate to move; the more interesting question is whether the dependence on registry provenance survives those changes.

**Reproducibility.** The [reproduction gist](https://gist.github.com/egpivo/9f38443647c676cb5b2362d4a0ae6361) includes the frozen registry, the provenance-reconstruction pipeline, the aggregate outputs behind every rate quoted here, and the manual-audit material. The [worked transaction](https://explorer.solana.com/tx/2LU6WK48r9vtM3H9SkbYahArgUZ7PdUFh62KSoqYiUxCMNP9eN28KY9tqrbPDK6vKGwvHuQuz9gS37ikEQYXL5JX) resolves on any archive RPC.

---

Onchain execution data does not arrive with a single recoverability rate. That rate is conditional on the semantic registry used to turn execution evidence into economic claims — which makes registry provenance part of the result, not a footnote to it.

---

## References

- [DeFiRanger](https://arxiv.org/abs/2104.15068) — Wu et al., IEEE TDSC 2023
- [GraphSense](https://arxiv.org/abs/2102.13613) — Haslhofer et al., ARES 2021
- [A Large Scale Study of the Ethereum Arbitrage Ecosystem](https://www.usenix.org/conference/usenixsecurity23/presentation/mclaughlin) — McLaughlin et al., USENIX Security 2023
- [Disentangling DeFi Compositions](https://arxiv.org/abs/2111.11933) — Kitzler et al., WWW 2022
- [Quantifying Price Improvement in Order Flow Auctions](https://arxiv.org/abs/2405.00537) — Bachu et al., FC 2025
- [What Drives Liquidity on Decentralized Exchanges?](https://arxiv.org/abs/2410.19107) — Zhu et al., 2024
- [An Empirical Study of DeFi Liquidations](https://arxiv.org/abs/2106.06389) — Qin et al., AFT 2021
- Solana docs: [transactions](https://solana.com/docs/core/transactions/transaction-structure), [introspection](https://solana.com/docs/core/transactions/transaction-introspection), [IDLs](https://solana.com/developers/guides/advanced/idls)

---

## Questions for builders

If Solana applications were to expose an attribution feature for routed execution, what is the smallest useful surface?

If you maintain an indexer, router, explorer, or venue integration: should the program-ID → economic-role binding come from the venue, be published by the router, or stay an indexer-maintained registry?

For pool attribution, is walking the CPI and account structure enough, or would an explicit leg → pool/market binding be worth emitting?

And would you want that metadata to carry only a role label, or also its source, version, and provenance state? The audit above is the argument for the second: a role label alone cannot tell you that the mapping carrying the most weight has only partial independence and medium-confidence support.

