---
layout: post
title: "After Uniswap v4 Went Live. The Pool Is No Longer the Whole Market."
date: 2026-07-28
tags: [DeFi, DEX, Blockchain, Web3]
image: /assets/2026-07-28-pool-gets-options/hero.png
---

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-07-28-pool-gets-options/hero.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-07-28-pool-gets-options/hero.png"
         alt="Schematic: concentrated-liquidity pool core with optional hook modules for dynamic fees, TWAMM, hook fees, custom accounting, and limit-order-like behavior"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
  <strong>Overview.</strong> Schematic only. Hooks are opt-in modules around a concentrated-liquidity pool; simple pools can remain simple. Not measured from a live deployment.
  </div>
</div>

***

Uniswap v4 has been live long enough that the interesting question is no longer what hooks can do. The question is what changes when the pool is no longer the whole market object.

The deeper shift is not that pools gained features. It is that routes can now select rule ownership.

A v4 pool can still be simple. But once it opts into hooks, the router is no longer touching only liquidity and price. It is also touching an **authority graph**: which hook can run, when it can run, what it can write, which fees it can change, and which accounting assumptions it controls.

Put differently: the route is no longer just choosing liquidity. It may also be choosing who owns the rules.

That is the engineering shift. Programmability is not just flexibility. It makes the authority around the pool part of the thing being traded against.

***

## Why now?

Uniswap v4 is not new launch news anymore. That is exactly why the question is more interesting now.

At launch, hooks were mostly described as optional customization: dynamic fees, callbacks, custom accounting, new pool behavior. That was the design story. The post-launch question is different: once those rules move into hook contracts, who owns the rule, who audits it, and who pays when it fails?

That question is no longer theoretical. [Bunni](http://blog.bunni.xyz/) made it visible from the security side: custom logic can fail outside the core pool. Hyperliquid makes it visible from the market side: book-native venues can still attract flow, fees, and attention when traders care about execution, leverage, and speed. CoW makes it visible from the routing side: execution can move into signed intents and solver competition without becoming a CLOB.

So this piece is not a late introduction to Uniswap v4 hooks. It is a post-launch question about DEX direction. Are DEXs dying, drifting back toward CLOBs, or evolving into several execution surfaces at once?

My read is the third one. The pool is not disappearing. But the rules around the pool are becoming harder to ignore.

The launch story was programmability. The post-launch story is rule ownership: who gets to change execution, who prices that authority, and who finds the failure boundary first.

***

## The pool was simple by design

Uniswap's history reads less like a replacement story and more like a gradual widening of the control surface around the pool.

**v2** kept the surface small: reserves, a constant-product curve, a fixed swap fee, and arbitrage against callable inventory. Few moving parts meant a small audit object.

**v3** added LP range placement and concentrated liquidity. LP positions were commonly represented through NFT positions in the periphery; where inventory sat inside tick ranges became part of what you had to read. The core math was still pool mechanics inside ticks—not a price-time queue.

**v4** pushes further into lifecycle hooks, dynamic fees, custom accounting, and execution timing. Uniswap v4 does not hide every policy inside the core protocol; it lets application builders, hook authors, routers, and liquidity managers move specific behavior into explicit code—and with it, delegated authority around the pool. [Hooks](https://docs.uniswap.org/contracts/v4/concepts/hooks) are external contracts attached to individual pools, called at defined lifecycle points (`beforeSwap`, `afterSwap`, liquidity changes, initialization) to intercept and modify execution flow. State moves into a singleton [`PoolManager`](https://developers.uniswap.org/docs/protocols/v4/overview): shared accounting for all pools, not a centralized exchange backend.

Before routers and hooks, the basic AMM audit object was already the pool—reserves or ticks, fee parameters, swap logs. In v4, that object can include external authority around it.

***

## Hooks move control into the pool lifecycle

Hooks matter because they let a pool choose which rules become programmable: fee response, execution timing, accounting, hook fees, conditional execution, and liquidity behavior. The pool remains the base layer; the hook defines a permission map around it.

- **`beforeSwap` / `afterSwap`** — pre/post swap intervention; programmable steps around the core swap.
- **Dynamic fees** — LP fee response; volatility- or flow-sensitive fee schedule.
- **Hook fees** — separate fee layer; value capture outside the LP fee.
- **Custom accounting / delta-return** — swap-leg settlement; highest audit expansion (see AsyncSwap).
- **TWAMM-style** — large trade timing; time-sliced execution across blocks.
- **Limit-order-like** — conditional execution; functional analogy only—not a queue.

This is where v4 becomes more interesting than a feature list. A v3 pool can be wrong for an LP because the range is wrong, the fee is wrong, or the flow is toxic. A v4 hooked pool adds another question: which part of that defense moved into code outside the core pool? The pool did not disappear, but the thing a trader touches is no longer only the pool.

The important part is not that hooks can do many things. The important part is that each extra behavior grants authority somewhere.

If the fee changes with volatility, the hook has fee authority. If a hook returns deltas, it has accounting authority. If execution is delayed or sliced, it has timing authority. If a router prefers one hooked pool over another, it is not only choosing liquidity. It is choosing which hook authority comes with the route.

That is why a hooked pool is no longer just a pool with extra logic. It is a pool plus delegated authority.

CLOB comparisons are easy to overread. A hooked pool can mimic some *functions* of a book—conditional execution, time-sliced flow, fee schedules—but it is still not a price-time priority queue. TWAMM-style hooks spread execution over time; they do not create a hidden matching engine.

[**AsyncSwap**](https://developers.uniswap.org/docs/protocols/v4/guides/hooks/async-swap) is the path I would inspect first on a hooked deployment: delta-return permissions can move swap-leg accounting into the hook. Flash accounting in the `PoolManager` still requires deltas to settle by transaction end, but the audit trail no longer stops at the core swap.

A pool with `address(0)` hooks or minimal permissions still audits like a compact concentrated-liquidity object. Turn hooks on, and delegated authority around the pool becomes part of the market object.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-07-28-pool-gets-options/fig2_audit_object_shift.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-07-28-pool-gets-options/fig2_audit_object_shift.png"
         alt="Side-by-side schematic: v3 audit checklist vs v4 hooked pool checklist with additional hook address, callback path, dynamic fees, and custom accounting"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 1.</strong> Hooks change the audit object. v3: pool address, fee tier, tick/liquidity, LP positions, swap logs. v4 hooked pool: add <code>PoolManager</code>/<code>PoolId</code>, hook address, callback path, dynamic fees, hook fees, and custom accounting. Schematic checklist—not an exhaustive hook taxonomy.
  </div>
</div>

***

## The engineering question is authority

For an engineer, a hooked pool starts with a permission map.

Who selected this hook for the pool? Who controls the hook contract? If it is upgradeable, who can upgrade it? If it has admin parameters, who can change them? Can it be paused? Which caller does the hook trust? Does it assume the trader is `msg.sender`, or does it correctly account for the `PoolManager` and router path? Which balances are internal, which are pool balances, and which are external dependencies?

Those are not side questions. They define the market object—and map the authority graph around the pool. A pool with the same tokens and the same visible liquidity can behave differently if a different contract has fee authority, accounting authority, timing authority, or admin authority around it.

***

## When authority fails outside the core

On **2 September 2025**, [Bunni](http://blog.bunni.xyz/)—a liquidity layer built as a Uniswap v4 hook—lost **~$8.4M** in an exploit, per the team's [post-mortem](http://blog.bunni.xyz/posts/exploit-post-mortem/). I treat the post-mortem as the primary technical account; I did not independently re-audit the on-chain trace.

Bunni is not useful here as proof that hooks are broken. It is useful because it shows that failure can live in the authority delegated outside the core pool.

In this case, the relevant story was not Uniswap v4 core swap math. It was hook-side accounting. That is the new audit question: not only "is the pool safe?" but "which external authority did this pool opt into, and where can that authority break?"

***

## What the charts show—and what they do not

The figures below are a bounded read, not a full map of DEX activity. Panel A pulls DeFiLlama `summary/dexs` volume for six spot protocols (Uniswap, PancakeSwap, Aerodrome, Orca, Raydium, Curve), aggregates to monthly shares, and uses a trailing-thirty-day window for the headline numbers. Panel B charts Hyperliquid perp trading fees (`fees/hyperliquid-perps`) as a book-native attention signal—a different metric class from the six-protocol spot sample. Spot DEX volume, aggregator volume, perp volume, TVL, and protocol fees should not share one denominator; I do not rank them on a single chart.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-07-28-pool-gets-options/fig0_trading_surfaces_split.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-07-28-pool-gets-options/fig0_trading_surfaces_split.png"
         alt="Panel A: monthly spot DEX volume share among Uniswap PancakeSwap Aerodrome Orca Raydium Curve; Panel B: Hyperliquid perp trading fees from DeFiLlama"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 2.</strong> Trading surfaces split by mechanism (DeFiLlama pulls, accessed Jul 2026). <strong>Panel A:</strong> monthly spot DEX volume share across a six-protocol sample. <strong>Panel B:</strong> Hyperliquid perp trading fees (`fees/hyperliquid-perps`) as a book-native attention signal. These panels use different metric classes and are not a shared market-share denominator. Latest partial month omitted. CoW omitted because no clean reproducible series was available in this pull.
  </div>
</div>

In that six-protocol spot sample, trailing-thirty-day volume was about **$83B**; Uniswap was roughly **44%**. PancakeSwap and Aerodrome took most of the remainder. Pool-native execution is still large across chains.

[CoW Protocol](https://docs.cow.fi/cow-protocol/concepts/introduction/intents) is the solver-side example in prose: users sign intents for a desired outcome; solvers compete under batch-auction rules. I did not chart it here.

Hyperliquid perp trading fees over the same thirty days: about **$63M** (`fees/hyperliquid-perps`). Perp notional volume is much larger—about **$209B** on DeFiLlama's derivatives series in the 9 July 2026 check—but that dimension is not reproduced in the free API pull behind Panel B.

### v4 adoption is not the same as hook adoption

Version share and hook share are different measurements. A protocol can ship optional hooks long before hooked pools dominate volume.

DeFiLlama child slugs (`uniswap-v2`, `uniswap-v3`, `uniswap-v4`) give a reproducible spot-DEX version series (`python3 scripts/fetch_uniswap_version_share.py`). In the trailing thirty days of the 9 July 2026 API check, v4 was about **60%** of Uniswap spot DEX volume in the series, v3 about **39%**, v2 about **1%**.

Hook-enabled volume is not in that series. Hook adoption remains an open measurement lane at publication time.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-07-28-pool-gets-options/fig_left_uniswap_v2_v3_v4_share.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-07-28-pool-gets-options/fig_left_uniswap_v2_v3_v4_share.png"
         alt="Monthly spot DEX volume share among Uniswap v2, v3, and v4 from DeFiLlama"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 3.</strong> DeFiLlama spot-DEX volume by Uniswap version (v2 / v3 / v4), monthly share within Uniswap only. This is version share within Uniswap spot-DEX volume only; it does not measure hook-enabled volume. Child-slug series is a reproducible DeFiLlama classification, not an audited decomposition of every Uniswap-routed trade.
  </div>
</div>

v4 shows up clearly in the DeFiLlama version series. What share of that volume actually runs through hooked pools is still unresolved.

***

## Hyperliquid from the other side

[Hyperliquid](https://hyperliquid.xyz) matters here because it represents pressure from the other side. A venue that still attracts transactions, fees, and attention becomes hard to ignore, especially when traders care about execution, speed, leverage, and visible market activity.

I do not read Uniswap v4 as a path toward a CLOB. Moving toward a book is not only a technical choice. It pulls DeFi back toward venue-style market design: makers, queues, matching, margin, risk engines, and a stronger operator surface. That may be efficient. It is also a different philosophy from a callable pool.

That does not mean Uniswap should become Hyperliquid. A book-native venue that attracts flow, fees, and attention proves demand for a different authority allocation. It does not prove that the pool is obsolete. [CoW Protocol](https://docs.cow.fi/cow-protocol/concepts/introduction/intents) sits on yet another axis—solver competition over signed intents. None of these replace the others; they allocate authority differently.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-07-28-pool-gets-options/fig3_different_surfaces_cards.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-07-28-pool-gets-options/fig3_different_surfaces_cards.png"
         alt="Three metric cards: Uniswap spot sample share, Hyperliquid perp fees, Hyperliquid perp volume—different surfaces, different metrics"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 4.</strong> Different surfaces, different metrics—not a single ranking. Three independent 30d attention signals: Uniswap share within the six-protocol spot sample, Hyperliquid perp fees (`fees/hyperliquid-perps`), and Hyperliquid perp volume (DeFiLlama derivatives UI check—not in the free API pull).
  </div>
</div>

***

## Closing

Uniswap v4 is not a book. CoW is not a pool. Hyperliquid is not an AMM. They are different answers to the same pressure: users want better execution, but nobody wants to be the last person to discover where the risk was hidden.

The next DEX competition may not be pool versus book. It may be rule ownership versus rule ownership.

One system gives rule authority to hooks around a pool. One gives it to solvers over signed intents. One gives it to a book, makers, margin, funding, and a risk engine. Traders experience these as routes. LPs experience them as flow and risk. Builders experience them as product surfaces. Auditors experience them as failure boundaries.

That is why the pool is no longer the whole market. Liquidity still matters, but the route is no longer only asking "which pool has depth?" It is also asking "who owns the rules around this execution, and what can fail there?"

Liquidity still decides where a route can go. Rule ownership decides what the route is actually touching.

The next DEX question may not be which mechanism wins. It is whether traders, routers, LPs, and auditors can see who owns the rules before capital discovers the failure mode for them.

***

## Appendix: sources and reproducibility

- Uniswap v4: [overview](https://developers.uniswap.org/docs/protocols/v4/overview), [hooks](https://developers.uniswap.org/docs/get-started/concepts/hooks), [swap hooks](https://developers.uniswap.org/docs/protocols/v4/guides/hooks/swap-hooks), [dynamic fees](https://developers.uniswap.org/docs/protocols/v4/concepts/dynamic-fees), [AsyncSwap](https://developers.uniswap.org/docs/protocols/v4/guides/hooks/async-swap), [security](https://developers.uniswap.org/docs/protocols/v4/security)
- CoW Protocol: [intents](https://docs.cow.fi/cow-protocol/concepts/introduction/intents)
- Bunni: [exploit post-mortem](http://blog.bunni.xyz/posts/exploit-post-mortem/) (2 Sep 2025)
- Hyperliquid Perps: [DeFiLlama protocol page](https://defillama.com/protocol/hyperliquid-perps) (perp fees and 30d perp volume UI check)
- Data fetching scripts: [gist](https://gist.github.com/egpivo/044682f4743715602e2fd81682339095) (`fetch_trading_surfaces.py`, `fetch_uniswap_version_share.py`, `probe_v4_subgraph.py`)
