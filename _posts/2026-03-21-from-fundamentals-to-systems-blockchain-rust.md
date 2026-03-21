---
layout: post
title: "Blockchain in 2026: Trust, State, and Why Rust Fits"
tags: [Rust, Blockchain, Web3, Cryptography, Consensus]
---

What pushed me to write this was simple: digital finance still relies too much on centralized operators.
Banks can freeze accounts. Platforms can change rules overnight. Cross-border settlement can still take days.

Even after a trade is matched, real settlement in traditional markets can lag (for example, T+1 in major U.S. equities since 2024, and often longer in other asset classes or cross-border flows).

Public data still shows meaningful frictions in legacy rails (see **References** below):
> Global remittance costs remain around 6.49% on average (World Bank), and cross-border payment speed can vary from minutes to multiple days depending on route and beneficiary processing (BIS/SWIFT gpi).

Events like the FTX collapse also reminded many people of counterparty risk in custodial exchange models, where users rely on internal controls they cannot independently verify (as alleged by the SEC complaint/press release).
More broadly, controversies around large exchanges made me more skeptical of the transparency and governance of custodial systems.

What keeps me interested in blockchain is not the idea of "zero trust," but reducing where blind trust is required.
From the book notes I took, the stack is clear:
Some framing below follows the textbook model directly, with current references added where useful.

- Cryptography gives integrity and authentication.
- Game theory aligns incentives.
- Computer science gives data structures and network rules that actually run at scale.

I am also learning Rust in parallel because secure protocol ideas are useless if implementation code is full of race conditions and memory bugs.

<figure style="text-align:center;">
  <img src="/assets/2026-03-21-beyond-the-boss-rust-blockchain-trust/hero-image.jpg" alt="Decentralized trust network visualization for blockchain infrastructure" style="max-width:90%; height:auto; border-radius:8px;" />
  <figcaption><em>Why this topic matters to me: moving trust from institutions toward verifiable systems. Source: <a href="https://www.pexels.com/zh-tw/@pixabay/">Pixabay on Pexels</a>.</em></figcaption>
</figure>

## 0) What Clicked First: Transaction vs. Settlement

A point from Chapter I changed how I read the rest:
> In blockchain systems, transaction execution and settlement are more tightly coupled on-chain, though practical finality still depends on the consensus model.

In conventional finance, trade execution and final settlement are separate steps, with intermediaries and reconciliation in between.
In blockchain, state transition and settlement happen as one committed event on a shared ledger.

That does not mean "free" or "instant in all cases."
It means fewer reconciliation layers and a different trust model.

Performance became a more concrete issue for me when I compared Bitcoin and Ethereum side by side.
Bitcoin keeps scripting intentionally constrained, while Ethereum opens a much larger execution surface through the EVM.
That flexibility is powerful for developers, but it also raises the bar on execution safety and system performance.

## 1) Cryptography: What I Had to Re-learn

A correction I had to make early:
password storage is a hashing problem, not an encryption problem.

- Encryption is reversible if the key leaks.
- Password verification should be one-way via a password KDF: `kdf(password, salt)` (e.g., Argon2id).
- In practice, use slow KDFs (Argon2id, bcrypt, scrypt), not plain SHA-256.

I used to mix up these terms in casual conversation. Writing it down forced me to separate confidentiality from integrity.

```rust
struct User {
    username: String,
    // Store derived password hash, never plaintext.
    password_hash: String,
    // Unique per-user salt (stored, not secret).
    salt: String,
}
```

**Salting:** each user gets a unique, random salt stored alongside the derived hash (the salt is not a secret, but it must be unpredictable when created). Two users with the same password still produce different stored hashes, so attackers cannot reuse one precomputed table (a rainbow table) across the whole database.

<figure class="post-figure post-figure--compact" style="text-align:center;">
  <img src="/assets/2026-03-21-beyond-the-boss-rust-blockchain-trust/salting.png" alt="Salting: same password with different salts yields different hashes" style="max-width:min(640px, 90%); height:auto; border-radius:8px;" />
  <figcaption><em>Conceptual illustration of salting: identical passwords with different salts map to different hashes, undermining rainbow-table attacks. Source: Generated with <a href="https://chatgpt.com/">ChatGPT</a>, edited by author.</em></figcaption>
</figure>

Another concept I had been underestimating is Kerckhoffs's principle:

> A system should remain secure even when attackers know the algorithm; only the key must stay secret.

That principle explains why open-source crypto systems can still be secure.

<figure style="text-align:center;">
  <img src="/assets/2026-03-21-beyond-the-boss-rust-blockchain-trust/colored_block1.jpg" alt="Single red block among blue blocks illustrating avalanche effect" style="max-width:90%; height:auto; border-radius:8px;" />
  <figcaption><em>One-bit input changes should heavily alter hash output (avalanche effect). Source: <a href="https://www.pexels.com/zh-tw/@ds-stories/">DS Stories on Pexels</a>.</em></figcaption>
</figure>

## 2) Game Theory: Security Is Also an Incentive Design Problem

I used to treat consensus as mostly a cryptography topic.
After working through the notes, it is clearly also an economics problem.

Bitcoin works because honest behavior is often the best response:

- Attack costs are real (hardware + electricity + opportunity cost).
- Failed attacks burn capital.
- Even a "successful" attack can destroy confidence and asset value.

So the protocol does not need participants to be moral. It needs them to be rational under the payoff structure.

One subtle point from my notes: decentralization is multi-dimensional.
A system can be technically distributed but still politically centralized, or logically centralized around one shared state.
That helped me stop using "centralized vs decentralized" as a binary label.

## 3) Computer Science: Hash Pointers, Merkle Trees, and "Heaviest" Chain

A detail I used to gloss over: in Bitcoin, we should say *heaviest chain* (most accumulated work), not just *longest chain*.
That distinction matters when difficulty varies.

Two core structures:

- Hash pointers link each block header to the previous header hash.
- Merkle trees compress all block transactions into one root.

This gives a strong combination:

- If transaction data changes, Merkle root changes.
- If header changes, block hash changes.
- Then every following block reference breaks.

SPV wallets are where this becomes very concrete:
they can verify inclusion with a Merkle proof plus headers, without downloading full blocks.
But they cannot enforce full UTXO set validity like full nodes do.

The layered mental model from Chapter I also helped me:
application -> execution -> semantic rules -> propagation -> consensus.
Following that stack made protocol reading easier for me than treating "blockchain" as one giant black box.

<figure class="post-figure" style="text-align:center;">
  <img src="{{ '/assets/2026-03-21-beyond-the-boss-rust-blockchain-trust/protocol-stack-flow.svg' | relative_url }}" alt="Diagram: Application, Execution, Semantic rules, Propagation, Consensus in a left-to-right pipeline" width="920" height="118" style="max-width:100%; height:auto;" />
  <figcaption><em>Conceptual pipeline from app logic to network agreement (after <cite>Beginning Blockchain</cite>, Chapter I framing).</em></figcaption>
</figure>

<figure style="text-align:center;">
  <img src="/assets/2026-03-21-beyond-the-boss-rust-blockchain-trust/colored_block2.jpg" alt="Triangular block hierarchy illustrating a Merkle-tree-like structure" style="max-width:90%; height:auto; border-radius:8px;" />
  <figcaption><em>Merkle proofs reduce verification from full-data checks to logarithmic proof paths. Source: <a href="https://www.pexels.com/zh-tw/@ds-stories/">DS Stories on Pexels</a>.</em></figcaption>
</figure>

## 4) Double-Spend at Network Level vs. Rust Safety at Code Level

I now separate this into two defenses:

- Network layer: consensus resolves ordering and prevents global double-spend.
- Application layer: implementation safety prevents local state corruption.

Rust helps with the second part. The ownership model is strict enough to prevent many accidental shared-state bugs.

- `&T`: many readers.
- `&mut T`: one mutable borrower.

```rust
impl Wallet {
    // Exclusive mutable access, safe against underflow.
    fn spend_coin(&mut self, amount: u64) -> Result<(), &'static str> {
        self.balance = self
            .balance
            .checked_sub(amount)
            .ok_or("Insufficient funds")?;
        Ok(())
    }
}
```

Rust does not solve consensus, but it does shrink the bug surface in code that touches money.
That is the practical reason I keep investing time in it.

The practical bridge from my Rust notes is ownership:
RAII + move semantics + borrow checking make resource lifetimes explicit.
For systems code, that "explicit lifetime" discipline feels very aligned with blockchain's need for deterministic, auditable state transitions.

The reason this feels more urgent to me when I look at Ethereum is the stateless vs. stateful split.

Chapter I presents Bitcoin as a UTXO-based model with simpler validation semantics than account-based smart-contract execution: validating a spend is largely about checking which outputs exist and are authorized.
Ethereum is stateful (account/contract state): the chain carries a persistent memory of "who owns what" and "what contracts can do next."

That persistent state is powerful, but it turns execution into a dependency problem:
transactions that touch the same state pieces compete for the right ordering, and the system needs careful execution rules to avoid corrupting shared state or falling into race-like behaviors at runtime.

Gas works as practical resource metering:
because the EVM is Turing complete, programs can (in principle) run forever.
Ethereum's gas does not solve the halting problem in a theoretical sense, but it bounds execution in practice by charging for computation steps.
If a call runs out of gas, it reverts. So unbounded execution becomes economically and operationally bounded rather than a way to freeze the network.
This is also how Ethereum frames gas in its developer docs: metering computation to reduce spam risk and prevent infinite-loop style resource exhaustion.

When execution becomes more stateful and more dependency-heavy, I want implementation safety rails even more. Rust is one of the tools that helps me reduce the bug surface in the node and wallet code that processes those state transitions.

Where I think Rust is a strong fit for blockchain systems:

- Node/client implementations that must run long-lived networking + storage code safely.
- Concurrent mempool/state-processing code where data races are expensive to debug.
- Performance-sensitive paths where predictable memory behavior matters.

Where Rust is not a silver bullet:

- It does not guarantee protocol economics are incentive-compatible.
- It does not replace cryptographic design review, audits, or formal verification.
- It does not make unsafe architecture choices safe by default.

<figure style="text-align:center;">
  <img src="/assets/2026-03-21-beyond-the-boss-rust-blockchain-trust/pexels-i-rem-tuba-orhan-3247169-5603895.jpg" alt="Library shelves metaphor for strict rules and safe access" style="max-width:72%; height:auto; border-radius:8px;" />
  <figcaption><em>Rust borrowing rules reduce many runtime failure modes. Source: <a href="https://www.pexels.com/">Pexels</a>.</em></figcaption>
</figure>

## 5) Why I Am Watching [Monad](https://www.monad.xyz/)

From an adoption perspective, I keep seeing the same tension:

- EVM compatibility is valuable because teams can reuse tooling and contracts.
- Performance still matters because users feel latency immediately.

Monad is interesting to me because it tries to keep EVM portability while pushing execution performance.

The bottleneck here is not just "raw throughput."
It is the stateful execution model that the EVM inherited from the account-based world:
simple to develop, but difficult to scale when transactions must apply updates to shared state deterministically.

In a naive account model, execution is effectively sequential: transactions update shared balances and contract storage one-by-one to stay correct.
To scale, newer designs try to separate independent work from dependent work so more execution can happen in parallel without breaking determinism.

By 2026, this discussion is usually framed as a stack-level choice, not a single trick:
L1 execution improvements, L2 architectures, and ZK/rollup-based verification each optimize different parts of the bottleneck.
The common direction is to move expensive computation off the critical on-chain path while keeping settlement and verification on-chain.

If systems like Monad can keep EVM portability while improving how they handle state dependency and execution parallelism in production,
it could remove a common "portability vs UX" tradeoff for teams.

<figure style="text-align:center;">
  <img src="/assets/2026-03-21-beyond-the-boss-rust-blockchain-trust/pexels-grizzlybear-399636.jpg" alt="High-speed traffic lanes representing performance and throughput" style="max-width:90%; height:auto; border-radius:8px;" />
  <figcaption><em>Throughput and latency are product concerns, not just infrastructure metrics. Source: <a href="https://www.pexels.com/zh-tw/@grizzlybear/">grizzlybear on Pexels</a>.</em></figcaption>
</figure>

## 6) What I Think Matters Going Into 2026

My read right now is:
mainstream adoption will depend less on narratives and more on infrastructure quality.

Themes I keep tracking:

- Stablecoins in real payment flows.
- RWA tokenization pipelines.
- Better rollup/ZK UX and proof systems.
- High-performance execution with developer portability.
- Elastic scaling and parallel execution for stateful workloads.
- Off-chain computation with on-chain settlement and verification (to reduce the critical path).

At this point, I see correctness and performance as table stakes, not optional upgrades.

## References

- [World Bank — Remittance Prices Worldwide](https://remittanceprices.worldbank.org/) (global remittance cost averages and corridors)
- [BIS CPMI — SWIFT gpi and cross-border payment speed](https://www.bis.org/cpmi/publ/swift_gpi.pdf) (variability and beneficiary-leg delays)
- [FSB — G20 targets for cross-border payments](https://www.fsb.org/work-of-the-fsb/financial-innovation-and-structural-change/cross-border-payments-2/g20-targets-for-enhancing-cross-border-payments-2/) (cost, speed, access, transparency)
- [U.S. SEC — FTX press release (Dec 2022)](https://www.sec.gov/news/press-release/2022-219)
- [Ethereum.org — Gas and fees (developer overview)](https://ethereum.org/en/developers/docs/gas/)
- Singhal, Dhameja, Panda, *Beginning Blockchain: A Beginner's Guide to Building Blockchain Solutions* — [Amazon](https://www.amazon.com/-/zh_TW/Beginning-Blockchain-Beginners-Building-Solutions/dp/148423443X)
- Blandy, Orendorff, Tindall, *Programming Rust, 3rd Edition* — [O'Reilly Learning](https://learning.oreilly.com/library/view/programming-rust-3rd/9781098176228/)

## Conclusion

These notes changed how I frame blockchain work.
The hard part is getting cryptography, incentives, and systems engineering to hold at the same time.
