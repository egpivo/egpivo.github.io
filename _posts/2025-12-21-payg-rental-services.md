---
layout: post
title: "Designing Rental Services on a Pay-As-You-Go Protocol"
tags: [Solidity, Blockchain]
---

This is not a rental dApp tutorial. It's a protocol design exercise under real-world constraints.

## From Articles to Rentals: Why This Extension Matters

Payments are easy, until you try to ship a rental product. The first bug is never in payment logic. Every real rental bug is an exclusivity bug.

What turns out to be hard is everything *around* the payment: availability, exclusivity, and time.

In the [previous article]({{ site.baseurl }}/2025/12/16/payg-service-contracts-article-contracts.html), we built an article subscription system on top of a generic Pay-As-You-Go (PAYG) core. Article subscriptions never had this problem. Hundreds of readers can read the same article at the same time.

Rentals break that assumption immediately.

Repo: https://github.com/egpivo/payg-service-contracts

A space can already be occupied. A car can only be driven by one person. A venue might be unavailable for maintenance. This means access is no longer binary — it is *time- and state-dependent*.

With rentals, we can no longer assume "access after payment". We need to track who is using what, until when, and whether concurrent access is even possible.

<div style="text-align:center; margin: 1rem 0;">
  <a href="{{ site.baseurl }}/assets/2025-12-21-payg-rental-services/article_vs_rental.svg?v=1" target="_blank">
    <img src="{{ site.baseurl }}/assets/2025-12-21-payg-rental-services/article_vs_rental.svg?v=1" alt="Article vs Rental: The Fundamental Difference" style="max-width:100%; height:auto; cursor: pointer;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">Why rentals are harder than subscriptions: exclusive access requires state management</div>
</div>

The hard part of rentals is not payment, it's conflict. Figure 1 shows why rentals cannot reuse subscription logic directly: the problem is not charging users, but preventing concurrent access.

Rental failures are rarely payment failures — they are coordination failures. Double bookings, unclear availability, and delayed refunds are product problems, not UI problems.

To support this, we introduce a domain layer for rentals that sits between the PAYG core and concrete service implementations.

<div style="text-align:center; margin: 1rem 0;">
  <a href="{{ site.baseurl }}/assets/2025-12-21-payg-rental-services/payg_rental_arch.svg?v=4" target="_blank">
    <img src="{{ site.baseurl }}/assets/2025-12-21-payg-rental-services/payg_rental_arch.svg?v=4" alt="Rental services: Domain layer on top of PAYG payment core" style="max-width:100%; height:auto; cursor: pointer;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">How rentals build on PAYG core: domain layer adds availability and exclusivity</div>
</div>

All rental variants delegate payment settlement to the same PAYG core. The domain layer only decides whether access is allowed. Figure 2 shows where we draw the boundary: no calendar logic, no future booking — just immediate availability and exclusivity enforcement.

## Why We Needed a Rental Domain Layer

If we embed availability checks directly into payment contracts, every new rental product reimplements the same fragile logic — and every bug becomes a double-booking incident.

Instead of building payment logic repeatedly for each rental type, we isolate settlement into a single, auditable core. `RentalBase.sol` is the domain layer between the payment core and service-specific implementations.

RentalBase defines what is being rented, whether it's exclusive, and whether it's currently available. It does not define payment patterns, duration rules, or renewal logic.

**RentalBase answers what and who, not how long or how much.**

## Exclusivity Is the Real Problem

Exclusivity is the biggest difference between articles and rentals. We model it with simple state tracking:

- `currentRenter`: who is using the rental right now (if exclusive)
- `exclusiveUntil`: timestamp when exclusivity ends
- If `exclusiveUntil > block.timestamp`, the rental is blocked

Two rental modes: non-exclusive (digital equipment, shared resources) and exclusive (venues, vehicles, physical spaces).

**What we intentionally avoid:**

We deliberately chose not to build a full on-chain booking system. Calendar UX doesn't belong on-chain — users expect availability calendars, advance reservations, cancellations, and rescheduling. These interactions are too complex and gas-intensive for on-chain execution.

We focus on immediate availability and current usage. Higher-level applications can handle calendar logic off-chain.

Here's how exclusivity is enforced:

<div style="text-align:center; margin: 1rem 0;">
  <a href="{{ site.baseurl }}/assets/2025-12-21-payg-rental-services/rental_state_machine.svg?v=1" target="_blank">
    <img src="{{ site.baseurl }}/assets/2025-12-21-payg-rental-services/rental_state_machine.svg?v=1" alt="Exclusive Rental: State Machine" style="max-width:100%; height:auto; cursor: pointer;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">Exclusive rental state machine: rent() checks exclusivity, expiry auto-unlocks. No calendar, no future booking.</div>
</div>

This state machine is intentionally minimal. The protocol guarantees exclusivity now, not reservations later. Figure 3 shows the two-state protocol: Available and Occupied, with timestamp-based unlock.

## What We Actually Implemented (and Why)

We didn't design these to be exhaustive. Each one exists because payment logic alone was not enough — the product needed different ways to buy access.

- **SpacePayPerUse**: Pay each time you use a space (typically exclusive)
- **SpaceSubscription**: Rent once, use multiple times (with optional security deposits)
- **EquipmentPayPerUse**: Equipment that can be exclusive or non-exclusive
- **DigitalPayPerUse**: Quantity-based billing for digital resources
- **RentalBundle**: Bundled rentals with revenue sharing

Each implementation inherits from `RentalBase` and adds only the payment pattern and access duration logic it needs. Providers list services and withdraw earnings via the PAYG core.

<div style="text-align:center; margin: 1rem 0;">
  <a href="{{ site.baseurl }}/assets/2025-12-21-payg-rental-services/rental_sequence.svg?v=1" target="_blank">
    <img src="{{ site.baseurl }}/assets/2025-12-21-payg-rental-services/rental_sequence.svg?v=1" alt="Rental Flow: User to Provider" style="max-width:100%; height:auto; cursor: pointer;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">What the contract guarantees that Web2 systems struggle with: atomic rent + payment + exclusivity. No off-chain booking, no calendar.</div>
</div>

## How We Test Something That Must Never Break

In rental products, exclusivity bugs are catastrophic. If two users can rent the same space at the same time, the product is broken, no matter how correct the accounting is.

If fuzzing ever finds a state where two renters overlap, the protocol has already failed. At that point, no refund logic can save the product.

Concretely, our tests don't try to simulate realistic user flows. Instead, we let Foundry generate arbitrary interleavings of rent/use, time jumps, and withdraw calls. The goal is not coverage — it's call-order safety: no possible sequence should break exclusivity guarantees. If the invariants hold under random interleavings, we consider the core protocol safe.

That's why fuzzing and invariant tests matter more here than in article subscriptions. We stress-test exclusivity boundaries and concurrent access scenarios to ensure exclusive rentals block correctly and expired exclusivity auto-clears.

We also test accounting consistency (especially deposits), but exclusivity enforcement is the critical path.

## Trade-offs We Accepted

- **Exclusivity enforcement**: We enforce exclusivity at the protocol layer, but don't build scheduling. This keeps the core simple while allowing applications to add calendar features on top.
- **Deposits**: Subscription rentals can require security deposits, which are held in escrow. The contract ensures deposits can't be withdrawn by providers (true escrow behavior).
- **Gas considerations**: Pay-per-use rentals avoid storage writes for access expiry (similar to article pay-per-read), while subscription rentals write expiry to storage for on-chain enforcement.

---

## Where This Goes Next

This article builds on our [previous work on article subscription contracts]({{ site.baseurl }}/2025/12/16/payg-service-contracts-article-contracts.html), where we established the PAYG core protocol. The rental extension validates that the same payment foundation can handle stateful, exclusive access without becoming overly complex.

If you're interested in following the development of this protocol, check out the [repository](https://github.com/egpivo/payg-service-contracts) and stay tuned for future articles on protocol extensions and real-world applications.
