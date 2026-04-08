---
layout: post
title: "Ethereum Account State: QA Pipeline for a Minimal Token"
tags: [Smart Contracts, Blockchain, Ethereum, Solidity, Web3, QA]
---

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-04-08-ethereum-account-state-qa/hero_image.jpg" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-04-08-ethereum-account-state-qa/hero_image.jpg"
         alt="QA dashboard monitoring smart contract state"
         style="max-width:80%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
</div>

The [previous post]({{ site.baseurl }}/2026/01/28/ethereum-account-state.html) walked through an end-to-end implementation: a minimal token contract, off-chain state reconstruction, and a React frontend — all the way from `mint()` to MetaMask. This post picks up where that left off: how do you QA something like this?

I'm not a blockchain engineer (yet) — but QA patterns port well across domains, and borrowing what already works elsewhere is how I learn fastest.

The contract only does three things — `mint`, `transfer`, and `burn` — but even that is enough to practice the full QA toolchain: static analysis, mutation testing, gas profiling, formal verification.

The code is in [`egpivo/ethereum-account-state`](https://github.com/egpivo/ethereum-account-state).

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-04-08-ethereum-account-state-qa/qa_flow.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-04-08-ethereum-account-state-qa/qa_flow.png"
         alt="Blockchain QA Pyramid: from static analysis at the base to formal verification at the top"
         style="max-width:40%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
</div>

---

## What we started with

Before adding anything new, the project already had:

- **21 Foundry unit tests** covering each state transition (success, revert on illegal input, event emission)
- **3 invariant tests** via a `TokenHandler` that runs random sequences of `mint`/`transfer`/`burn` on 10 actors (128k calls each)
- **Fuzz tests** checking `sum(balances) == totalSupply` for random amounts
- **TypeScript domain tests** (Vitest) mirroring the on-chain state machine
- **CI**: compile, test, lint (Prettier + solhint)

All tests passed. Coverage looked fine. So why bother with more?

Because "all tests pass" does not mean "all bugs are caught." 100% line coverage can still miss a real bug if no assertion checks the right thing.

---

## Phase 1: Smart contract static analysis and coverage

### Slither

[Slither](https://github.com/crytic/slither) (Trail of Bits) catches issues that are invisible to tests: reentrancy, unchecked return values, interface mismatches.

```bash
./scripts/run-qa.sh slither
```

Result: **1 Medium finding** — `erc20-interface`: `transfer()` doesn't return `bool`.

This is expected. The contract is intentionally not a full ERC20 — it is an educational state machine. But the finding is not academic: USDT's `transfer()` famously does not return `bool` either, and that non-compliance has caused [real integration failures](https://bugblow.com/blog/erc20-integration-hell) in DeFi protocols that assumed standard ERC20 behavior. If someone later imports this token into a protocol expecting ERC20, the interface mismatch would silently fail. Slither flags it now so the decision is conscious.

### Coverage

```bash
./scripts/run-qa.sh coverage
```

| Metric | Token.sol |
|---|---|
| Lines | 96.15% (50/52) |
| Statements | 93.10% (54/58) |
| Branches | 100% (7/7) |
| Functions | 91.67% (11/12) |

One uncovered function: `BalanceLib.gt()`. We will come back to this.

<div style="text-align:center; margin: 1.5rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-04-08-ethereum-account-state-qa/coverage2.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-04-08-ethereum-account-state-qa/coverage2.png"
         alt="forge coverage output: 24 tests passed, Token.sol coverage table"
         style="max-width:95%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <code>forge coverage</code> output: 24 tests passed, Token.sol at 96% lines / 100% branches / 91.67% functions.
  </div>
</div>

### Gas snapshots

```bash
./scripts/run-qa.sh gas
```

Baseline gas costs for the three operations:

| Operation | Gas |
|---|---|
| `mint` | ~59k |
| `transfer` | ~88k |
| `burn` | ~64k |

On subsequent runs, `forge snapshot --diff` compares against the baseline. A 20% gas regression in `transfer()` is a real cost to every user — catching it before merge is cheap.

---

## Phase 2: Mutation testing and formal verification

### Mutation testing (Gambit)

This is where things got interesting. [Gambit](https://github.com/Certora/gambit) (Certora) generates *mutants* — copies of `Token.sol` with small deliberate bugs (`+=` to `-=`, `>=` to `>`, conditions negated). The pipeline runs the full test suite against each mutant. If a mutant survives (all tests still pass), that is a concrete test gap.

```bash
./scripts/run-qa.sh mutation
```

Result: **97.0% mutation score** — 32 killed, 1 survived out of 33 mutants.

Gambit's output log shows each mutant and what it changed. A few examples:

```
Generated mutant #7: BinaryOpMutation — Token.sol:168
  totalSupply = totalSupply.add(amountBalance)  →  totalSupply = totalSupply.sub(amountBalance)
  KILLED by test_Mint_Success

Generated mutant #19: RelationalOpMutation — Token.sol:196
  if (!fromBalance.gte(amountBalance))  →  if (fromBalance.gte(amountBalance))
  KILLED by test_Transfer_Success

Generated mutant #28: SwapArgumentsMutation — Token.sol:81
  return Balance.unwrap(a) > Balance.unwrap(b)  →  return Balance.unwrap(b) > Balance.unwrap(a)
  SURVIVED ← no test caught this
```

<div style="text-align:center; margin: 1.5rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-04-08-ethereum-account-state-qa/mutation_test.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-04-08-ethereum-account-state-qa/mutation_test.png"
         alt="Gambit mutation testing: 32 killed, 1 survived, mutation score 97.0%"
         style="max-width:95%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    Gambit results: 33 mutants tested, one survivor — <code>[13] SwapArgumentsOperatorMutation</code> on <code>BalanceLib.gt()</code>.
  </div>
</div>

The surviving mutant swapped `a > b` to `b > a` in `BalanceLib.gt()`. No test caught it — because `gt()` is **dead code**. It is never called anywhere in `Token.sol`.

Coverage flagged 91.67% functions but could not explain the gap. Mutation testing did: `gt()` is dead code, nothing calls it, and nobody would notice if it were wrong.

Dead or unprotected code in smart contracts has real precedent. In 2017, an unprotected `initWallet()` function in the Parity multisig library was called by an outside user, who then triggered `kill()` — [permanently freezing over $150M](https://threatpost.com/hundreds-of-millions-in-digital-currency-remains-frozen/128821/) across 500+ wallets. The function was not intended to be callable, but nobody tested that assumption. Our `gt()` is harmless by comparison, but the pattern is the same: code that exists but is never exercised is code that nobody is watching.

### Formal verification (Halmos)

[Halmos](https://github.com/a16z/halmos) (a16z) reasons about *all possible inputs* symbolically. Where fuzz tests sample random values and hope to hit edge cases, Halmos proves properties exhaustively.

```bash
./scripts/run-qa.sh halmos
```

Result: **9/9 symbolic tests pass** — all properties proven for all inputs.

Properties verified:

| Property | Result |
|---|---|
| `mint` increases `totalSupply` by exactly `amount` | Proven |
| `mint` increases recipient balance by exactly `amount` | Proven |
| `transfer` preserves `totalSupply` | Proven |
| `burn` decreases `totalSupply` by exactly `amount` | Proven |
| `mint(address(0), ...)` always reverts | Proven |
| `mint(..., 0)` always reverts | Proven |
| `transfer` with insufficient balance always reverts | Proven |
| `BalanceLib.add` — no overflow (within uint128) | Proven |
| `BalanceLib.sub` — correct when `a >= b` | Proven |

One practical note: Halmos 0.3.3 does not support `vm.expectRevert()`, so I could not write revert tests the normal Foundry way. The workaround is a try/catch pattern — if the call succeeds when it should revert, `assert(false)` fails the proof:

```solidity
function check_mint_reverts_on_zero_address(uint256 amount) public {
    vm.assume(amount > 0);
    try token.mint(address(0), amount) {
        assert(false); // should not reach here
    } catch {
        // expected revert — Halmos proves this path is always taken
    }
}
```

Not the prettiest, but it works — Halmos still proves the property for all inputs. This is the kind of thing you only find out by actually running the tool.

For context on why formal verification matters: the 2016 DAO hack exploited a reentrancy pattern that [drained ~$60M and led to Ethereum's hard fork](https://www.nadcab.com/blog/famous-smart-contract-hacks-complete-guide). The vulnerability was in the code, reviewable by anyone, but no tool or test caught it before deployment. Symbolic provers like Halmos exist precisely to close that gap — they do not sample; they exhaust the input space.

<div style="text-align:center; margin: 1.5rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-04-08-ethereum-account-state-qa/halmost_test.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-04-08-ethereum-account-state-qa/halmost_test.png"
         alt="Halmos output: 9 tests passed, 0 failed, symbolic test results"
         style="max-width:95%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    Halmos symbolic test results: 9 passed, 0 failed — all properties proven for all inputs.
  </div>
</div>

The test file is [`contracts/test/Token.halmos.t.sol`](https://github.com/egpivo/ethereum-account-state/blob/main/contracts/test/Token.halmos.t.sol).

---

## Phase 3: Cross-layer property testing

The first post's architecture has a TypeScript domain layer that mirrors the on-chain state machine. This phase tests whether the two actually agree.

### Property-based testing with fast-check

I added [fast-check](https://github.com/dubzzz/fast-check) property tests for the TypeScript domain layer, mirroring what Foundry's fuzzer does for Solidity:

```bash
npm test -- tests/unit/property.test.ts
```

Result: **9/9 property tests pass** — after fixing a real bug.

Properties tested:

- `Balance`: commutativity, associativity, identity, inverse, comparison consistency
- `Token`: invariant `sum(balances) == totalSupply` under random operation sequences (200 runs, 50 ops each)
- `Token`: `totalSupply` non-negative after random sequences
- `mint` always succeeds for valid inputs
- `transfer` preserves `totalSupply`

### The bug fast-check found

fast-check found a real cross-layer consistency bug in `Token.ts` `transfer()`. The shrunk counterexample was immediately clear:

```
Property failed after 3 tests
Shrunk 2 time(s)
Counterexample: transfer(from=0xaaa..., to=0xaaa..., amount=1n)
  → from == to (self-transfer)
  → verifyInvariant() returned false
```

Self-transfer (`from == to`) broke the `sum(balances) == totalSupply` invariant. `toBalance` was read *before* `fromBalance` was updated, so when `from == to`, the stale value overwrote the deduction:

```typescript
// Before (buggy)
const fromBalance = this.getBalance(from);
const toBalance = this.getBalance(to);      // ← stale when from == to

this.accounts.set(from.getValue(), fromBalance.subtract(amount));
this.accounts.set(to.getValue(), toBalance.add(amount));  // ← overwrites the subtraction
```

Fix: read `toBalance` after writing `fromBalance`, matching Solidity's storage semantics:

```typescript
// After (fixed)
const fromBalance = this.getBalance(from);
this.accounts.set(from.getValue(), fromBalance.subtract(amount));

const toBalance = this.getBalance(to);      // ← now reads updated value
this.accounts.set(to.getValue(), toBalance.add(amount));
```

The Solidity contract was **not** affected — it re-reads storage after each write. But the TypeScript mirror had a subtle ordering dependency that no existing unit test covered.

Cross-layer mismatches at larger scale have been catastrophic. The 2022 [Wormhole bridge hack ($320M)](https://techcrunch.com/2023/07/27/wormhole-new-security-320m-hack/) exploited a gap between off-chain guardian validation and on-chain verification — the two layers disagreed on what constituted a valid signature, and the attacker walked through the gap. Our self-transfer bug would not have lost anyone money, but the failure mode is structurally the same: two layers that are supposed to agree, don't.

---

## Pitfalls hit along the way

Running QA tools on an existing project is never just "install and run." A few things broke before they worked:

- **0% coverage because `foundry.toml` had no test path**: The first `forge coverage` run returned 0% across the board. Turns out `foundry.toml` did not specify `test = "contracts/test"` or `script = "contracts/script"`, so Forge was not discovering any tests. The coverage command succeeded silently — it just had nothing to cover. This was the most misleading failure: a green run with no useful output.
- **`InvariantTest` import gone in forge-std v1.14.0**: `Invariant.t.sol` imported `InvariantTest` from `forge-std`, which was removed in a recent release. Compilation failed with an opaque "symbol not found" error. The fix was to drop the import — `Test` alone is sufficient for Foundry's invariant testing now.
- **`uint256(token.totalSupply())` vs `Balance.unwrap()`**: Tests were using an explicit cast to extract the underlying `uint256` from the user-defined `Balance` type. It compiled, but it is the wrong idiom — `Balance.unwrap(token.totalSupply())` is what the UDVT system is designed for. Applied across `Token.t.sol`, `Invariant.t.sol`, and `DeploySepolia.s.sol`.

---

## Pipeline design

Everything runs through two scripts:

- [`scripts/setup-qa-tools.sh`](https://github.com/egpivo/ethereum-account-state/blob/main/scripts/setup-qa-tools.sh) — installs Slither, Halmos, Gambit (idempotent)
- [`scripts/run-qa.sh`](https://github.com/egpivo/ethereum-account-state/blob/main/scripts/run-qa.sh) — runs checks, saves timestamped results to `.local/qa-results/`

```bash
./scripts/run-qa.sh slither gas        # just static analysis + gas
./scripts/run-qa.sh mutation           # just mutation testing
./scripts/run-qa.sh all                # everything
```

Not every check is fast. Slither and coverage run on every commit. Mutation testing and Halmos are slower — better suited for weekly or pre-release runs.

---

## Summary

<div style="text-align:center; margin: 1.5rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-04-08-ethereum-account-state-qa/qa_layers.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-04-08-ethereum-account-state-qa/qa_layers.png"
         alt="Blockchain QA Toolchain: what each layer catches — from static analysis to cross-layer property testing"
         style="max-width:95%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    Five QA layers, each catching a different class of problem.
  </div>
</div>

| Layer | Question answered | What we found |
|---|---|---|
| Static analysis (Slither) | Structural vulnerabilities tests can't see? | 1 Medium: `transfer()` missing ERC20 `bool` return (intentional) |
| Coverage (Forge) | Code paths no test reaches? | 96% lines, 100% branches, 1 uncovered function |
| Gas snapshots | Did a refactor regress gas? | Baseline: mint ~59k, transfer ~88k, burn ~64k |
| Mutation testing (Gambit) | Are assertions strong enough? | 97% score — 1 survivor = dead code (`BalanceLib.gt()`) |
| Formal verification (Halmos) | Does it hold for *all* inputs? | 9/9 properties proven |
| Property testing (fast-check) | Does off-chain match on-chain? | Found self-transfer bug in `Token.ts` |

Gambit and fast-check gave the most actionable results in this round.

---

## CI pipeline

The QA checks are now wired into GitHub Actions as a six-stage pipeline:

<div style="text-align:center; margin: 1.5rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-04-08-ethereum-account-state-qa/ci_pipeline.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-04-08-ethereum-account-state-qa/ci_pipeline.png"
         alt="CI Pipeline: Build & Lint fans out to Test, Coverage, Gas, Slither, and Audit stages"
         style="max-width:55%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    GitHub Actions pipeline: Build & Lint gates all downstream stages.
  </div>
</div>

| Stage | What it does | Gate |
|---|---|---|
| Build & Lint | Compile Solidity + TypeScript, run Prettier + solhint | Fail on error |
| Test | Foundry tests (unit + invariant + fuzz) + Vitest (unit + property) | Fail on error |
| Coverage | `forge coverage` + LCOV, check Token.sol branch coverage | Fail if < 95% |
| Gas | `forge snapshot --diff --tolerance 5` against baseline | Fail if > 5% regression |
| Slither | Static analysis, `--fail-on high` | Fail on High findings |
| Audit | `npm audit --audit-level=high` | Warning only |

Mutation testing and Halmos are not in CI yet — they are slower and better suited for pre-release runs.

## References

- Ethereum Account State source: [github.com/egpivo/ethereum-account-state](https://github.com/egpivo/ethereum-account-state)
- [Previous post: Ethereum Account State]({{ site.baseurl }}/2026/01/28/ethereum-account-state.html)
- Slither: [github.com/crytic/slither](https://github.com/crytic/slither)
- Gambit: [github.com/Certora/gambit](https://github.com/Certora/gambit)
- Halmos: [github.com/a16z/halmos](https://github.com/a16z/halmos)
- fast-check: [github.com/dubzzz/fast-check](https://github.com/dubzzz/fast-check)
- Foundry: [getfoundry.sh](https://getfoundry.sh)
