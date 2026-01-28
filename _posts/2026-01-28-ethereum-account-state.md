---
layout: post
title: "Ethereum Account State: A Minimal Token with Reconstructible State"
tags: [Smart Contracts, Blockchain, Ethereum, Solidity, Web3]
---

I built this project to answer a simple question: can you reconstruct a token's entire state just from events, without ever reading storage?

I got it wrong the first time. I processed both `Burn` and `Transfer(to=address(0))` and ended up double-counting supply. The fix is straightforward but easy to miss: treat `Transfer(..., address(0), ...)` as the canonical burn signal and ignore `Burn` events from the same transaction.

This matters because event-based reconstruction is the foundation for indexers, audit tools, and historical state queries. If you can't reliably rebuild state from events, you're stuck reading storage directly, which works for current state but fails for historical queries and verification.

This post walks through the implementation: a deliberately small Solidity token, a TypeScript domain model that mirrors the on-chain state machine, and a React frontend that demonstrates event-based reconstruction. The code is in [`egpivo/ethereum-account-state`](https://github.com/egpivo/ethereum-account-state).

<div style="text-align:center; margin: 2rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-01-28-ethereum-account-state/wallet_hero.png"
       alt="Ethereum wallet and tokens illustration"
       style="max-width:80%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    Ethereum token and wallet — the minimal demo this post walks through.
  </div>
</div>

---

## On-chain state machine design

The contract (`contracts/src/Token.sol`) is intentionally tiny: three functions (`mint`, `transfer`, `burn`) and three events (`Mint`, `Transfer`, `Burn`). I kept it minimal so the state transitions are obvious:

- **Mint**: `totalSupply += amount`, `balances[to] += amount`
- **Transfer**: `balances[from] -= amount`, `balances[to] += amount` (supply unchanged)
- **Burn**: `totalSupply -= amount`, `balances[from] -= amount`

I used Solidity's user-defined value types (0.8.8+; this repo uses 0.8.28) for type safety: `type Balance is uint256`, with a `BalanceLib` for `add()`, `sub()`, `gte()`, and `zero()`. It prevents mixing balances with unrelated `uint256` values and compiles down to zero-cost `wrap/unwrap` conversions.

The invariant `sum(balances) == totalSupply` can't be checked on-chain because mappings aren't enumerable. It's guaranteed by construction. Off-chain, we can actually check it by summing a `Map<address, Balance>`.

### Event design and burn semantics

When `burn()` is called, the contract emits two events:

```solidity
emit Burn(from, amount);
emit Transfer(from, address(0), amount); // ERC20 canonical supply reduction
```

Both events describe the same burn. They even have different `logIndex` values, which makes naive reconstruction extra risky. The rule I follow: **use `Transfer(..., address(0), ...)` as the canonical burn and skip `Burn` events from the same transaction**. That matches ERC20's burn semantics. (ERC20 also uses `Transfer(from=address(0), ...)` for mints; this token uses a separate `Mint` event, so reconstruction follows the contract's events, not full ERC20 event semantics.)

---

## Off-chain domain and validation

The TypeScript domain layer (`domain/`) mirrors the on-chain state machine so the rules are enforced in both places:

- `domain/entities/Token.ts` holds `totalSupply` and a `Map<address, Balance>`, with `mint()`, `transfer()`, and `burn()`.
- `domain/value-objects/` wraps `Address` and `Balance` to avoid mixing raw strings or numbers with domain values.
- `domain/services/StateTransition.ts` validates the same conditions the contract reverts on (zero address, zero amount, insufficient balance).

`WalletService` (`application/services/WalletService.ts`) uses those checks before sending a transaction:

1. Reconstruct current state from events.
2. Validate the transition (`StateTransition.validate*()`).
3. Encode and send the transaction via `ethers.Interface`.

If validation passes off-chain but reverts on-chain, it's likely a domain bug or stale/off-chain state (e.g., a new block, reorg, missing events, or mempool race between reconstruction and execution).

---

## State querying and event reconstruction

`StateQueryService` (`application/services/StateQueryService.ts`) supports two ways to read state:

- **Storage reads**: `getTokenBalance()` and `getTotalSupply()` use `eth_call`.
- **Event reconstruction**: `reconstructStateFromEvents()` rebuilds state from `Mint`, `Transfer`, and `Burn` events.

The reconstruction logic is simple but strict:

1. Sort all events by `(blockNumber, txIndex, logIndex)` so ordering is well-defined (logs are ordered within a tx by `logIndex`, but merging multiple event queries can scramble order otherwise).
2. Group events by transaction hash.
3. If a tx includes any `Transfer(..., address(0), ...)`, mark it as a burn tx.
4. Skip `Burn` events for burn txs.
5. Apply events in that order: `Mint` increases supply, `Transfer(to != address(0))` moves tokens, `Transfer(to == address(0))` decreases supply.

This avoids double-counting and keeps the invariant intact.

`compareState()` reads storage state and compares it to reconstructed state. In production this is best-effort only: event reconstruction can be incomplete (pagination limits, missing history, chain reorganizations), so mismatches are logged as warnings rather than hard errors.

### Why event reconstruction matters (and when it doesn't)

It's slower than storage reads and less reliable if you don't have full history. But it enables things storage can't:

- Historical state queries without archive storage.
- Indexer validation and audit trails.
- Tests that verify invariants using just events.

---

## Infrastructure layer

The infrastructure layer (`infrastructure/ethereum/`) wires everything to Ethereum:

- `EthereumProvider` wraps `ethers.Provider` with connection handling.
- `ContractRepository` implements `ITokenRepository` using event reconstruction, and compares to storage as a diagnostic check.

The repository intentionally favors reconstructed state even if diagnostics warn, because this is more of an educational/verification tool than a production indexer.

<div style="text-align:center; margin: 1.5rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-01-28-ethereum-account-state/arch.png"
       alt="Architecture & execution flow: frontend, off-chain SDK layer, on-chain contract, and RPC"
       style="max-width:95%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    Codebase architecture: the React UI talks to MetaMask, the SDK layer reconstructs/validates state, and the contract is the only source of truth (storage + logs).
  </div>
</div>

---

## Frontend integration

The React frontend (`frontend/src/App.tsx`) is a minimal demo of the contract interface:

- Connects via `ethers.BrowserProvider` and a MetaMask signer.
- Displays `balanceOf()` and `totalSupply()`.
- Sends `mint()`, `transfer()`, and `burn()` calls.
- Shows the last 20 events, deduplicating burns the same way as the backend (treat `Transfer(to=0)` as canonical).

<div style="text-align:center; margin: 1.5rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-01-28-ethereum-account-state/simple_sys.gif"
       alt="System flow: App.tsx → MetaMask → Ethereum RPC → Token.sol → logs"
       style="max-width:95%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    End-to-end user flow: click → sign → send → execute → emit events. Burns emit both <code>Burn</code> and <code>Transfer(to=0)</code>, but the UI/reconstructor treats <code>Transfer(to=0)</code> as canonical.
  </div>
</div>

The frontend doesn't use the domain layer or `WalletService`; it's intentionally direct.

---

## Demo steps

If you want to run the full demo locally:

<div style="text-align:center; margin: 1.5rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-01-28-ethereum-account-state/demo_flow.png"
       alt="Demo flow: anvil → deploy → frontend → MetaMask → load contract → mint/transfer/burn → view balance and events"
       style="max-width:85%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    Demo flow at a glance: start Anvil, deploy locally, connect MetaMask, load the contract, then run Mint/Transfer/Burn and watch balances and recent events update.
  </div>
</div>

1. **Start Anvil** (local Ethereum node):
   ```bash
   anvil
   ```

<div style="text-align:center; margin: 1.5rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-01-28-ethereum-account-state/anvil.png"
       alt="Anvil local node: default accounts and private keys"
       style="max-width:95%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    Local Anvil node with 10 pre-funded accounts and their private keys. Use one of these accounts in MetaMask for the demo.
  </div>
</div>

2. **Deploy the contract**:
   ```bash
   make deploy-local
   ```
   This deploys the Token contract to Anvil and prints the contract address.

<div style="text-align:center; margin: 1.5rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-01-28-ethereum-account-state/local_deploy_contract.png"
       alt="Local deployment output: token address on Anvil"
       style="max-width:95%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    Output of <code>make deploy-local</code>: the script connects to Anvil, deploys <code>Token.sol</code>, and prints the deployed contract address you will paste into the UI.
  </div>
</div>

3. **Install frontend dependencies**:
   ```bash
   make frontend-install
   ```

4. **Start the frontend dev server**:
   ```bash
   make frontend-dev
   ```

5. **Add Anvil network and account in MetaMask** (required for the demo):
   - In MetaMask, add a new network: **Network name** e.g., "Anvil Local", **RPC URL** `http://127.0.0.1:8545`, **Chain ID** `31337`. (MetaMask may warn that the name doesn't match the chain ID; that's fine for local use.)
   - Use one of Anvil's default accounts: when you run `anvil`, it prints private keys and addresses. Import one of those into MetaMask so you have test ETH and can receive tokens on the local chain.

<div style="display:flex; justify-content:center; gap:1.5rem; margin: 1.5rem 0; flex-wrap:wrap;">
  <div style="text-align:center; max-width:48%;">
    <img src="{{ site.baseurl }}/assets/2026-01-28-ethereum-account-state/anvil_local_config.png"
         alt="MetaMask: add Anvil Local network (RPC 127.0.0.1:8545, Chain ID 31337)"
         style="width:100%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
    <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
      Add the Anvil Local network in MetaMask so the demo can talk to your local node.
    </div>
  </div>
  <div style="text-align:center; max-width:48%;">
    <img src="{{ site.baseurl }}/assets/2026-01-28-ethereum-account-state/demo_account.png"
         alt="MetaMask: Anvil Local address for receiving tokens"
         style="width:100%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
    <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
      Use this Anvil Local account (or another Anvil default account) to receive tokens and run Mint/Transfer/Burn in the demo.
    </div>
  </div>
</div>

6. **Connect MetaMask in the app**:
   - Open the frontend in your browser, then click "Connect Wallet" and approve the connection. Ensure MetaMask is set to the Anvil Local network.

7. **Load the contract**:
   - Paste the deployed contract address into the "Token contract address" field.
   - Click "Load" to fetch balance and total supply.

8. **Test operations**:
   - **Mint**: Enter a recipient address and amount, click "Mint".
   - **Transfer**: Enter recipient and amount, click "Transfer".
   - **Burn**: Enter amount, click "Burn".
   - After each operation, click "Refresh" to see updated balances.

<div style="text-align:center; margin: 1.5rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-01-28-ethereum-account-state/demo_p_demo.gif"
       alt="UI demo: mint → transfer to self → burn, with Recent Events updating"
       style="max-width:95%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    One full demo run: mint tokens, transfer them to yourself, burn part of the balance, and watch the Recent Events table show Mint, Transfer, and canonical Burn (<code>Transfer(to=0)</code>) entries.
  </div>
</div>

9. **View events**:
   - The "Recent Events" section shows the last 20 events from the last 1000 blocks.
   - Burns appear as "Burn" type (from `Transfer(..., address(0), ...)`).
   - Click "View" to open the transaction on Etherscan (for Sepolia/mainnet) or see the hash (for local).

The full code is in [`egpivo/ethereum-account-state`](https://github.com/egpivo/ethereum-account-state).
