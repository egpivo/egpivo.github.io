---
layout: post
title: "From Services to Products: Composing Multi-Provider Checkout On-Chain"
tags: [Solidity, Blockchain, Web3]
---

Imagine a mobile library. Readers don’t pay per book. They pay to enter the library for a period of time. Inside the library:

- books come from different authors  
- authors join and leave over time  
- revenue needs to be split across contributors

On-chain, each book would be a separate service. But the product people buy is the library itself.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2025-12-28-payg-pool-protocol-composition-layer/miroslav-denkov-KVS95WFbe5U-unsplash.jpg?v=1" target="_blank">
    <img src="{{ site.baseurl }}/assets/2025-12-28-payg-pool-protocol-composition-layer/miroslav-denkov-KVS95WFbe5U-unsplash.jpg?v=1" alt="One product, multiple providers" style="max-width:500px; width:100%; height:auto; cursor: pointer;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">One product. One payment. Many payees.</div>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    Photo by
    <a href="https://unsplash.com/@mdenkov?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText"
       target="_blank" rel="noopener noreferrer">
       Miroslav Denkov
    </a>
    on
    <a href="https://unsplash.com/photos/a-yellow-truck-parked-next-to-a-bookshelf-filled-with-books-KVS95WFbe5U?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText"
       target="_blank" rel="noopener noreferrer">
       Unsplash
    </a>
  </div>
</div>

In this post, the "books" are articles, the mobile vehicle is rental services, and the "library pass" is a Pool that sells access and settles revenue.

On-chain, this breaks down fast.

- **Creator platform:** readers want one 30‑day membership across multiple writers. If each writer is a separate contract, the user ends up with multiple transactions and mismatched expiry windows.
- **Co‑working + gear:** a customer wants “room + projector” as one booking. Without composition, they pay (and manage terms) separately.

**Pools make multi-provider products purchasable in one atomic transaction.**

> Providers are modeled as services.
> The pool turns many services into one checkout.

That’s not a pricing problem. It’s a **composition** problem.

## Pool: turning services into a product

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2025-12-28-payg-pool-protocol-composition-layer/hero_image.png?v=1" target="_blank">
    <img src="{{ site.baseurl }}/assets/2025-12-28-payg-pool-protocol-composition-layer/hero_image.png?v=1" alt="Pool Architecture" style="max-width:90%; height:auto; cursor: pointer;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    Pool as a protocol primitive: composition without domain coupling.
  </div>
</div>

A **Pool** is a purchasable unit that does exactly three things:

1. **Access:** grants time‑based (or permanent) entitlement
2. **Settlement:** splits revenue deterministically
3. **Membership:** defines members + weights

> **One payment, multiple providers, deterministic settlement.**

## Interfaces

Pools compose services through two minimal interfaces:

```solidity
interface IServiceRegistry {
    function getService(uint256 serviceId)
        external view
        returns (uint256 price, address provider, bool exists);
}

interface IPoolAccess {
    function hasPoolAccess(address user, uint256 poolId)
        external view
        returns (bool);
}
```

Pool queries services via `IServiceRegistry`. Modules can gate usage via `IPoolAccess`. No domain logic crosses these boundaries.

## Design constraints

Three constraints shaped these interfaces:

- **Atomicity:** Purchase, settlement, and access updates happen in one transaction  
- **Deterministic splits:** Shares define weights; remainder goes to the first member
- **Minimal coupling:** Pool never imports domain logic; modules query Pool via interface  

## Membership is directional

In this article, **pool members** always mean providers/services (supply side). Users can buy access, but they are never members.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2025-12-28-payg-pool-protocol-composition-layer/membership_direction.png?v=1" target="_blank">
    <img src="{{ site.baseurl }}/assets/2025-12-28-payg-pool-protocol-composition-layer/membership_direction.png?v=1" alt="Membership Direction Diagram" style="max-width:90%; height:auto; cursor: pointer;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">Membership is directional: payers buy access; payees are members who share revenue.</div>
</div>

## A compact example: articles + rentals

Assume two registries already exist (same interface, different domains):

- `ArticleRegistry` (writers)  
- `RentalRegistry` (equipment)  

### 1) Providers register services (unchanged modules)

```solidity
// Article services
articleRegistry.registerService(101, 0.05 ether);
articleRegistry.registerService(102, 0.05 ether);

// Rental service
rentalRegistry.registerService(201, 0.20 ether);
```

### 2) Create a cross‑module pool

One pool composes services from **different registries** and defines the revenue weights.

```solidity
// Pool #42: 1 ETH for 7 days, operator fee 2%
// Members: Article(101) weight=2, Rental(201) weight=1

uint256[] memory ids = new uint256[](2);
ids[0] = 101;
ids[1] = 201;

address[] memory regs = new address[](2);
regs[0] = address(articleRegistry);
regs[1] = address(rentalRegistry);

uint256[] memory shares = new uint256[](2);
shares[0] = 2;  // weights, not percentages (remainder handled deterministically)
shares[1] = 1;

pool.createPool(
  42,
  ids,
  regs,
  shares,
  1 ether,
  7 days,
  200 // 2%
);
```

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2025-12-28-payg-pool-protocol-composition-layer/composition_layer.png?v=1" target="_blank">
    <img src="{{ site.baseurl }}/assets/2025-12-28-payg-pool-protocol-composition-layer/composition_layer.png?v=1" alt="Pool as Composition Layer" style="max-width:90%; height:auto; cursor: pointer;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">Pool composes services via IServiceRegistry without coupling modules.</div>
</div>

### 3) User purchases once; providers get credited

```solidity
pool.purchasePool{value: 1 ether}(42, address(0));
```

Settlement is **ledger credits** (providers withdraw later):

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2025-12-28-payg-pool-protocol-composition-layer/money_flow.png?v=1" target="_blank">
    <img src="{{ site.baseurl }}/assets/2025-12-28-payg-pool-protocol-composition-layer/money_flow.png?v=1" alt="Money Flow + Settlement Diagram" style="max-width:90%; height:auto; cursor: pointer;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">One payment → operator fee + provider earnings, computed on-chain.</div>
</div>

For intuition (not exact wei math):

- price = 1 ETH  
- fee = 2% → 0.02 ETH  
- net = 0.98 ETH  
- shares = [2, 1]  

So the article side gets ~0.653 ETH and the rental side gets ~0.327 ETH (remainder handled deterministically).

### 4) Usage stays inside the module (access gating)

Pool never calls rental logic. Rentals can optionally **gate usage** by checking pool access:

```solidity
function useWithPoolAccess(uint256 rentalServiceId, address pool, uint256 poolId) external {
    require(IPoolAccess(pool).hasPoolAccess(msg.sender, poolId), "no pool access");
    _useRental(rentalServiceId); // availability + state transitions live here
}
```

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2025-12-28-payg-pool-protocol-composition-layer/state_transition.png?v=1" target="_blank">
    <img src="{{ site.baseurl }}/assets/2025-12-28-payg-pool-protocol-composition-layer/state_transition.png?v=1" alt="State Transition Diagram" style="max-width:90%; height:auto; cursor: pointer;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">A single purchase updates access + earnings atomically; usage stays module-owned.</div>
</div>

## Why this layout works

- **Pool:** purchase + settlement + access
- **Modules:** availability + usage semantics + lifecycle

## Failure modes

A few edge cases are handled explicitly:

- **Member removed:** future purchases no longer credit that member
- **Bad registry / missing service:** pool creation rejects it (`exists == false`)
- **Expired access:** modules simply gate usage via `hasPoolAccess`

---

**Code:** https://github.com/egpivo/payg-service-contracts

Pools aren’t built for “articles” or “rentals”. They’re a composition primitive: **one checkout, many payees**.