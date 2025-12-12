---
layout: post
title: "Practicing Solidity: Learning Notes from Building a Pay-as-You-Go Service"
tags: [Solidity, Blockchain]
---

I'm learning Solidity and wanted to apply some concepts to build a pay-as-you-go (PAYG) service contract as practice. I finished *The Complete Solidity Course – Zero to Advanced for Blockchain and Smart Contracts* on O'Reilly, and this is my first hands-on project.

Instead of just listing language features, I wanted to see how payment handling, state management, and inheritance work together in a reusable design.

- Repository: https://github.com/egpivo/payg-service-contracts  
- Course: https://learning.oreilly.com/course/the-complete-solidity/9781805122470/

## The PAYG Concept

Before getting into the code, here's the basic idea: users pay per use instead of subscriptions. The contract needs to handle payments, track what providers earn, and unlock access after payment.

Here's how it flows:

<div style="text-align:center;">
  <img src="{{ site.url }}/assets/2025-12-11-practicing-solidity-transitioning-to-web3/payg_concept.dot.svg" width="800" alt="PAYG Concept Flow">
  <figcaption>Fig. 1: PAYG Service Concept: High-Level Flow</figcaption>
</div>

Pretty straightforward: users pay, providers get credited, and access gets unlocked. 

### A Quick Note on Addresses

Contracts need to know who's calling functions. Solidity has `msg.sender`—a global variable that automatically contains the address of whoever called the function. In this PAYG system:

- When a user calls `useService()`, `msg.sender` is the user's address
- When a provider calls `withdraw()`, `msg.sender` is the provider's address

So the contract knows who's doing what without needing explicit address parameters.

## Contract Design: Base Contract with Inheritance

I learned about inheritance in the course, so I designed the PAYG system with a base contract that handles the core payment stuff. Then different service types can extend it.

Here's how the inheritance works:

<div style="text-align:center;">
  <img src="{{ site.url }}/assets/2025-12-11-practicing-solidity-transitioning-to-web3/contract_architecture.dot.svg" width="800" alt="Contract Architecture">
  <figcaption>Fig. 2: Contract Architecture: Inheritance Pattern</figcaption>
</div>

### PayAsYouGoBase: The Foundation

Here's how the base contract works:

#### State Variables

At a minimum, the contract needs to keep track of services and provider earnings:

```solidity
struct Service {
    uint id;
    uint price;
    address provider;
    uint usageCount;
    bool exists;
}
```
(similar to Python's `dataclass`).

The key state variables are:

- `services`: the source of truth for service pricing and ownership
- `earnings`: how much ETH each provider has earned but not yet withdrawn
- `serviceIds`: a simple way to enumerate registered services (mainly for debugging and demos)

Almost every action in the contract—registering a service, paying for usage, or withdrawing earnings—comes down to reading from or updating these variables. Thinking in terms of state transitions helped me reason about correctness and payment safety early on.

```solidity
mapping(uint => Service) public services;
mapping(address => uint) public earnings;
uint[] public serviceIds;
```

#### Registering a Service

Here's how providers register a service:

```solidity
    function registerService(uint _serviceId, uint _price) public virtual {
        require(_price > 0, "Price must be greater than 0");
        require(!services[_serviceId].exists, "Service ID already exists");
        
        services[_serviceId] = Service({
            id: _serviceId,
            price: _price,
            provider: msg.sender,
            usageCount: 0,
            exists: true
        });
        
        serviceIds.push(_serviceId);
        emit ServiceRegistered(_serviceId, msg.sender, _price);
    }
```

I use `msg.sender` here so providers don't need to pass their own address—the contract already knows who's calling.

#### Using a Service

When users want to use a service, they call this:

```solidity
    function useService(uint _serviceId) public virtual payable {
        Service storage service = services[_serviceId];
        require(service.exists, "Service does not exist");
        require(msg.value >= service.price, "Insufficient payment");
        
        service.usageCount += 1;
        earnings[service.provider] += service.price;
        
        // Refund excess payment if any
        if (msg.value > service.price) {
            payable(msg.sender).transfer(msg.value - service.price);
        }
        
        emit ServiceUsed(_serviceId, msg.sender, service.usageCount);
    }
```

I credit earnings using `service.price` instead of `msg.value` to handle cases where users overpay. The excess gets refunded immediately.

#### Withdrawing Earnings

Providers can withdraw what they've earned:

```solidity
    function withdraw() public virtual {
        uint amount = earnings[msg.sender];
        require(amount > 0, "No earnings to withdraw");
        
        earnings[msg.sender] = 0; // Reset before transfer (CEI pattern)
        payable(msg.sender).transfer(amount);
        
        emit Withdrawn(msg.sender, amount);
    }
}
```

I reset earnings to 0 before the transfer (CEI pattern). This way, if something goes wrong with the transfer, the state is already updated and can't be exploited.

### Extending for Different Service Types

I built an example implementation for article subscriptions. One thing I find interesting about this design: readers pay writers directly—no platform taking a cut in the middle. The payment goes straight from reader to writer through the contract.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./PayAsYouGoBase.sol";

contract ArticleSubscription is PayAsYouGoBase {
    struct Article {
        uint articleId;
        string title;
        bytes32 contentHash;
        uint publishDate;
    }
    
    mapping(uint => Article) public articles;
    mapping(address => mapping(uint => bool)) public hasRead;
    
    function publishArticle(
        uint _articleId,
        uint _price,
        string memory _title,
        bytes32 _contentHash
    ) external {
        // Use base contract's registerService
        registerService(_articleId, _price);
        
        // Add article-specific data
        articles[_articleId] = Article({
            articleId: _articleId,
            title: _title,
            contentHash: _contentHash,
            publishDate: block.timestamp
        });
        
        emit ArticlePublished(_articleId, _title, msg.sender);
    }
    
    function readArticle(uint _articleId) external payable {
        // Use base contract's useService
        useService(_articleId);
        
        // Mark article as read
        hasRead[msg.sender][_articleId] = true;
        emit ArticleRead(_articleId, msg.sender);
    }
}
```

This design lets us reuse the core payment logic while each service type adds what's specific to it (just like tracking which articles users have read). We can super easily create new service types (e.g., `VideoStreaming`, `APIAccess`) by inheriting from the base. It's a pattern I see a lot in production Solidity code.

## Other ideas

### Design by Contract with `require`

I use `require()` throughout the contract to validate inputs and state. Reading other contracts online, I see this pattern frequently, enforcing preconditions before executing logic. I later found out this pattern is often called "design by contract," and it seems like a standard practice in Solidity, so I adopted it.

```solidity
require(_price > 0, "Price must be greater than 0");
require(service.exists, "Service does not exist");
require(msg.value >= service.price, "Insufficient payment");
```

If any `require()` fails, the transaction reverts. Basically, state what you expect upfront, and fail early if it's not met.

### Modifiers

I haven't used modifiers in this contract yet, but I'm learning about them. They add reusable checks to functions, which helps prevent unauthorized access and scams.

For example, to restrict functions to only the service provider:

```solidity
modifier onlyProvider(uint _serviceId) {
    require(services[_serviceId].provider == msg.sender, "Not the service provider");
    _;
}

function updateServicePrice(uint _serviceId, uint _newPrice) public onlyProvider(_serviceId) {
    // Only the provider can update the price
}
```

This prevents someone from modifying a service they don't own. Modifiers make access control explicit and reusable.

