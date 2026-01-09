---
layout: post
title: "Wrapping Up PAYG with a Web UI Demo"
tags: [Solidity, Blockchain, Web3, Demo]
---

After weeks of diving into article registries and rental modules, I finally reached the stage every developer craves: making it all visible. It's one thing to see `0x...` addresses in a terminal; it's another to see a "Private Gallery" package actually work on a UI.

## The Journey So Far

This post is the grand finale of my series on building a Pay-As-You-Go (PAYG) ecosystem. If you're joining just now, here's how we got here:

[Transitioning to Web3](https://egpivo.github.io/2025/12/11/practicing-solidity-transitioning-to-web3.html) — My initial shift from traditional development to Solidity.

[Article Registries](https://egpivo.github.io/2025/12/16/payg-service-contracts-article-contracts.html) — Building the foundation for on-chain content services.

[Rental Services](https://egpivo.github.io/2025/12/21/payg-rental-services.html) — Extending the protocol to handle time-based infrastructure.

[The Composition Layer](https://egpivo.github.io/2025/12/28/payg-pool-protocol-composition-layer.html) — Creating the Pool Protocol to bundle multiple services together.

Today, I'm excited to share a [live demo](https://egpivo.github.io/payg-service-contracts/) that ties everything together. I chose a Private Gallery as the use case because it perfectly illustrates the messiness of real-world collaboration: you have content (art), a venue (hotel), and security. Normally, that's three separate contracts and a lot of trust. With the Pool Protocol, it's just one transaction.

## The Problem We've All Faced

We've all been there: trying to bundle different services but ending up with a nightmare of multiple invoices and manual splits. In Web3, we can do better than just "sending tokens"; we can program the revenue logic directly into the purchase.

I wanted to show that on-chain composition isn't just about technical feasibility—it's about solving real coordination problems. When I started building this demo, I kept asking myself: "What if a user wants to buy access to multiple services from different providers, but pay once? What if those providers need to split revenue automatically?"

The answer became Pool #42: a Private Gallery Access package that bundles an art collection, a hotel space, and security services. One payment. Three providers. Automatic settlement.

## Connecting the Dots: How a Gallery Becomes a Pool

When I was designing this, I kept picturing that high-end gala scene from *Mission: Impossible — Fallout* at the Grand Palais. What if we could bring that kind of complex setup directly on-chain?

For me, this framework isn't just a technical showcase. The real challenge is: can we translate all those messy coordination and trust costs from the physical world into decentralized services? Whether it's an individual or a premium client, they shouldn't have to deal with three suppliers, sign three contracts, and make three separate payments. Through this Pool, content, venue, and security get bundled into one simple PAYG product. At its core, it's about bringing Web3 back to basics: one purchase, automatic settlement, instant delivery.

On-chain, this maps to services from different registries. The art collection lives in an `ArticleRegistry`, while the hotel space and security come from a `RentalRegistry`. The Pool Protocol composes them into a single purchasable product.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-01-09-payg-private-gallery-demo/composition.png?v=1" target="_blank">
    <img src="{{ site.baseurl }}/assets/2026-01-09-payg-private-gallery-demo/composition.png?v=1" alt="Composition: Registries → Pool #42" style="max-width:90%; height:auto; cursor: pointer;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">Services from different registries bundle into Pool #42</div>
</div>

Pool #42 is configured with a 3:2:1 revenue split. The art collection provider gets 50% (3 shares), the hotel space provider gets 33.3% (2 shares), and security gets 16.7% (1 share). The operator takes a 2% fee, transparent and upfront. This wasn't arbitrary—the art collection is the main draw, so it gets the largest share.

## The "Magic" Moment: One Transaction, Three Receivers

The moment I saw this work in the UI was when I realized the protocol was actually solving a real problem. Here's what happens when someone buys Pool #42:

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-01-09-payg-private-gallery-demo/user_flow.png?v=1" target="_blank">
    <img src="{{ site.baseurl }}/assets/2026-01-09-payg-private-gallery-demo/user_flow.png?v=1" alt="User Flow: Select → Create → Purchase → Settlement" style="max-width:90%; height:auto; cursor: pointer;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">The complete flow: from selection to settlement</div>
</div>

The user selects the "Private Gallery Access" package, creates the pool (if it doesn't exist), and purchases it. In one transaction, three things happen atomically: the user gets 7 days of access, the operator receives their 2% fee, and all three providers get credited in their ledgers.

No manual reconciliation. No trust required between providers. The smart contract handles it all.

This is my favorite part of the demo—watching the transaction confirm and seeing the revenue split visualization update in real-time. It's the difference between "here's how it could work" and "here's how it actually works."

## Follow the Money (The Transparent Way)

When a user pays 1 ETH for Pool #42, here's exactly where it goes:

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-01-09-payg-private-gallery-demo/money_flow.png?v=1" target="_blank">
    <img src="{{ site.baseurl }}/assets/2026-01-09-payg-private-gallery-demo/money_flow.png?v=1" alt="Money Flow: Payment → Fee/Net → Providers" style="max-width:90%; height:auto; cursor: pointer;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">Revenue flows transparently from one payment to multiple providers</div>
</div>

The 1 ETH splits into 0.02 ETH for the operator (2%) and 0.98 ETH net revenue. That 0.98 ETH then distributes by shares: 0.49 ETH to the art collection provider, 0.327 ETH to the hotel space provider, and 0.163 ETH to security.

The demo UI shows this breakdown visually. I added this because transparency matters—users and providers should see exactly where the money goes. No hidden fees. No surprises.

## What I Learned Building This

Building this demo forced me to make some hard decisions. I originally wanted to show more complex scenarios—dynamic membership, usage gating, renewal behavior. But I realized that for a demo to be effective, it needs to be simple enough to understand in one sitting.

I also had to decide between showing the "perfect" implementation and showing something that actually works. I chose the latter. The demo currently supports two modes: local (with a real Anvil node) and mock (for GitHub Pages). The mock mode doesn't connect to a blockchain, but it shows the UI flow and makes the concept accessible to anyone.

This limitation is actually a feature. It shows that the protocol works conceptually, and the UI demonstrates the user experience. For production, you'd deploy to a real network, but for understanding the concept, the mock mode is perfect.

## Try It Yourself

The [Service Marketplace demo](https://egpivo.github.io/payg-service-contracts/) is live and interactive. You can select the Private Gallery Access package, see how services compose, and watch the revenue split happen.

If you want to run it locally, the setup is straightforward:

```bash
make demo
```

Connect MetaMask to `localhost:8545` and you'll have a full on-chain experience. The Pool #42 configuration is pre-filled, so you can immediately see how cross-registry composition works.

Here's what the local setup looks like in action—running on Anvil with real smart contract deployment:

<div style="text-align:center; margin: 2rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-01-09-payg-private-gallery-demo/demo.gif" alt="Demo: Local implementation with Anvil - wallet connection, contract deployment, and settlement" style="max-width:90%; height:auto; border-radius: 8px;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">Local demo running on Anvil: wallet connection → contract deployment → pool creation → purchase → revenue settlement</div>
</div>

This GIF shows the complete flow in a local environment. The contracts are deployed to Anvil, transactions are real (even if on a local chain), and you can see exactly how the protocol handles multi-provider settlement atomically.

## Why This Matters

After building article registries, rental services, and now the composition layer, I've come to see that Web3 payment protocols don't have to be complicated. They just need to solve real problems.

The core value of this framework lies in turning a "physical event" into a "purchasable combination of decentralized services." Whether it's for an individual enthusiast, a small group, or a premium client, the protocol allows them to access a complete, multi-provider experience through a simple PAYG model.

This isn't just about technology—it's about making on-chain services usable. When users can buy a "gallery access package" instead of managing three separate contracts, we're moving in the right direction.

The demo is live, the code is open source, and the concept is proven. Now it's time to see what people build with it.

---

**Previous Posts in This Series:**
- [Practicing Solidity: Transitioning to Web3]({{ site.baseurl }}/2025/12/11/practicing-solidity-transitioning-to-web3.html)
- [PAYG Service Contracts: Article Contracts]({{ site.baseurl }}/2025/12/16/payg-service-contracts-article-contracts.html)
- [PAYG Rental Services]({{ site.baseurl }}/2025/12/21/payg-rental-services.html)
- [From Services to Products: Composing Multi-Provider Checkout On-Chain]({{ site.baseurl }}/2025/12/28/payg-pool-protocol-composition-layer.html)

**Code:** https://github.com/egpivo/payg-service-contracts  
**Live Demo (Mock Wallet):** [Service Marketplace](https://egpivo.github.io/payg-service-contracts/)  
**Demo Source:** [Web UI Demo](https://github.com/egpivo/payg-service-contracts/tree/main/demo/web)
