---
layout: post
title: "Pay-As-You-Go Protocol: From Services to Composable Pools"
tags: [Solidity, Blockchain, Web3]
---

Today, pay‑as‑you‑go services are everywhere.

Writers sell subscriptions. Venues sell access. Equipment providers rent assets. APIs sell usage.

In all these cases, users aren’t buying a single provider — they’re buying **one product delivered by many providers**.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2025-12-28-payg-pool-protocol-composition-layer/hero_image.png?v=1" target="_blank">
    <img src="{{ site.baseurl }}/assets/2025-12-28-payg-pool-protocol-composition-layer/hero_image.png?v=1" alt="One product, multiple providers" style="max-width:100%; height:auto; cursor: pointer;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">One product. One payment. Many payees.</div>
</div>

On-chain, this breaks down fast:

- each provider registers a service
- each service charges independently
- but the user wants **a single checkout**

That’s not a pricing problem. It’s a **composition** problem.

## Pool as a protocol primitive

A **Pool** is a purchasable unit that does exactly three things:

- **Access:** grants time‑based (or permanent) entitlement
- **Settlement:** splits revenue deterministically across providers
- **Membership:** defines the supply‑side alliance and its weights

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

## Membership is directional

In this article, **pool members** always mean providers/services (supply side). Users can buy access, but they are never members.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2025-12-28-payg-pool-protocol-composition-layer/membership_direction.png?v=1" target="_blank">
    <img src="{{ site.baseurl }}/assets/2025-12-28-payg-pool-protocol-composition-layer/membership_direction.png?v=1" alt="Membership Direction Diagram" style="max-width:100%; height:auto; cursor: pointer;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">Membership is directional: payers buy access; payees are members who share revenue.</div>
</div>

## A compact, real example (articles + rentals)

Assume we already have two modules, each exposing the same registry interface:

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
shares[0] = 2;
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
    <img src="{{ site.baseurl }}/assets/2025-12-28-payg-pool-protocol-composition-layer/composition_layer.png?v=1" alt="Pool as Composition Layer" style="max-width:100%; height:auto; cursor: pointer;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">Pool composes services via IServiceRegistry without coupling modules.</div>
</div>

### 3) User purchases once; providers get credited

```solidity
pool.purchasePool{value: 1 ether}(42, address(0));
```

Settlement is **ledger credits**, not inline transfers:

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2025-12-28-payg-pool-protocol-composition-layer/money_flow.png?v=1" target="_blank">
    <img src="{{ site.baseurl }}/assets/2025-12-28-payg-pool-protocol-composition-layer/money_flow.png?v=1" alt="Money Flow + Settlement Diagram" style="max-width:100%; height:auto; cursor: pointer;" />
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
    <img src="{{ site.baseurl }}/assets/2025-12-28-payg-pool-protocol-composition-layer/state_transition.png?v=1" alt="State Transition Diagram" style="max-width:100%; height:auto; cursor: pointer;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">A single purchase updates access + earnings atomically; usage stays module-owned.</div>
</div>

## Why this layout works

- **Pool handles purchase + settlement + access.**
- **Modules handle domain rules.** (availability, usage semantics, lifecycle)

That boundary is what keeps Pool a protocol primitive instead of “yet another bundle contract”.

**Code:** https://github.com/egpivo/payg-service-contracts
