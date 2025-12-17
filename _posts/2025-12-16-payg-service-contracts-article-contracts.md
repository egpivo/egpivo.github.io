---
layout: post
title: "Building Article Subscription Contracts in Solidity"
tags: [Solidity, Blockchain]
---


The goal of this post is to design the *on-chain payment and settlement layer* for such a product, not a full dApp. We focus on how different article payment models map to Solidity contracts, and how those contracts can be tested and evolved safely.

This post explores a small dApp idea: the frontend only offers a few payment choices, and each choice simply calls a different smart contract. The contract — not the platform — decides how payments are settled to writers.

In this prototype, there are three concrete routes:
- **Pay‑per‑read**: pay each time you read, with funds going directly to a single author (p2p)
- **Subscription**: pay once, then read multiple times within an access window (p2p)
- **Bundle**: pay once for multiple articles or authors, with the contract splitting revenue across providers (p2p → split)

<div style="text-align:center; margin: 1rem 0;">
  <a href="{{ site.baseurl }}/assets/2025-12-16-payg-article-modes/payg_article_fig1_paths.svg?v=2" target="_blank">
    <img src="{{ site.baseurl }}/assets/2025-12-16-payg-article-modes/payg_article_fig1_paths.svg?v=2" alt="Three payment UX paths share the same on-chain settlement" style="max-width:100%; height:auto; cursor: pointer;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">Figure 1. Pay-per-read / Subscription / Bundle routes all settle through the same PAYG core</div>
</div>

Figure 1 summarizes this idea. The UI’s role is deliberately minimal: it only decides which contract to call. All payment logic and settlement rules live on‑chain. In other words, the platform is no longer the center of payments or user data — it’s just a UI.

Repo: https://github.com/egpivo/payg-service-contracts

To avoid reinventing wheels, we lean on a few open-source pieces:
- [OpenZeppelin](https://www.openzeppelin.com/): `Ownable` and `ReentrancyGuard` for basic access control and safety.
- Foundry + forge-std for tests (unit, fuzz, invariant) and scripts.

## Implementing the three payment models

### 1) Pay‑per‑read (stateless)
Users pay every time they read. The contract avoids per‑user writes; reads are tracked via events.

```solidity
// publish: sets price + provider
publishArticle(articleId, price, title, contentHash);

// read: pay each time
readArticle{value: price}(articleId);
```

### 2) Subscription (time‑limited or permanent)
Users purchase once and can read multiple times until expiry. `duration = 0` means permanent access.

```solidity
publishArticle(articleId, price, title, contentHash, duration);

purchaseArticle{value: price}(articleId);   // sets/extends accessExpiry
readArticle(articleId);                    // requires valid access
```

### 3) Bundle (one payment for multiple articles)
Users buy a bundle (a list of article IDs) with one payment. Revenue is split equally across providers (remainder goes to the first article).

```solidity
createBundle(bundleId, articleIds, bundlePrice, duration);

purchaseBundle{value: bundlePrice}(bundleId);  // splits revenue + updates bundleAccessExpiry
```


<div style="text-align:center; margin: 1rem 0;">
  <a href="{{ site.baseurl }}/assets/2025-12-16-payg-article-modes/payg_article_fig2_arch.svg?v=2" target="_blank">
    <img src="{{ site.baseurl }}/assets/2025-12-16-payg-article-modes/payg_article_fig2_arch.svg?v=2" alt="Dependencies: models use PayAsYouGoBase; Subscription/Bundle use AccessLib; Bundle uses IArticleRegistry; extension point for new services" style="max-width:100%; height:auto; cursor: pointer;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">Figure 2. Dependencies + extension point (new services call PayAsYouGoBase; optional registry-style interface)</div>
</div>


Once the payment flows were clear, the next step was structuring the contracts so that new payment models could be added without rewriting core logic. Figure 2 shows how all three models reuse a shared payment core and add only the minimum logic needed for their specific access rules.

## How we test these contracts

Once the contracts compile and basic flows work, most of the real risk is no longer in syntax errors—it’s in edge cases and state interactions. Payments, expiry, and repeated calls tend to fail in ways that aren’t obvious from a single happy-path test.

We structure tests around *what can go wrong*, not just around individual functions:

The main things we care about are:

- **Accounting invariants**: earnings, refunds, and contract balance must always stay consistent.
- **Time invariants**: expiry logic must behave correctly at boundaries.
- **Sequence safety**: repeated actions should never corrupt state.

We use a small number of unit tests to lock down expected behavior, then rely mostly on **fuzz tests and invariant tests** to stress the system with random inputs and call sequences. In practice, invariants around accounting and expiry caught far more issues than writing additional scenario-specific tests.

## A note on gas costs

While building these contracts, one recurring theme was that *small design choices compound quickly* when a function is called many times. This is especially visible in subscription renewals and bundle purchases, where a single transaction may touch multiple storage slots or multiple providers.

One concrete example is error handling. All contracts use **custom errors** instead of string-based `require(...)` messages. The reason is simple: custom errors are significantly cheaper, especially on revert paths.

At a high level:

- `require(condition, "long revert string")` stores and copies a dynamic string.
- `error SomeError(uint256 id, uint256 expected, uint256 actual);` only encodes a selector and arguments.

In Foundry tests, this difference consistently shows up as **lower gas usage on failure paths**, which matters for:
- bundle validation (checking many articles/providers),
- access checks on expired subscriptions,
- and refund logic when users overpay.

We don’t try to micro-optimize every opcode, but replacing revert strings with custom errors is a *low-effort, high-signal* improvement that keeps contracts cheaper and cleaner as they grow.

To make this concrete, here’s the rough *relative* gas profile of the main user actions (happy paths) across the three models:

<div style="text-align:center; margin: 1rem 0;">
  <a href="{{ site.baseurl }}/assets/2025-12-16-payg-article-modes/payg_article_gas.png?v=1" target="_blank">
    <img src="{{ site.baseurl }}/assets/2025-12-16-payg-article-modes/payg_article_gas.png?v=1" alt="Relative gas (happy paths)" style="max-width:100%; height:auto; cursor: pointer;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">Relative gas (happy paths)</div>
</div>

We treat this as a directional signal (not an exact benchmark), but it matches the intuition: `bundle/subscription` spend more gas upfront because they write more state (expiry tracking, splits), while pay-per-read keeps reads minimal.

CI reference: Foundry Tests run (Dec 16, 2025) — [GitHub Actions log](https://github.com/egpivo/payg-service-contracts/actions/runs/20286279112/job/58260580186).
