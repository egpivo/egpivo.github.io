---
layout: post
title: "Before SNARKs: Building a Mini ZK-Rollup Verifier in Rust"
tags: [Rust, Blockchain, Web3, Zero-Knowledge, Cryptography]
---

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-05-03-rust-zkp-learning-demo/hero.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-05-03-rust-zkp-learning-demo/hero.png"
         alt="Before SNARKs: mini ZK-rollup verifier in Rust—toy verifier workflow from tx and witness through Rust checks to updated Merkle state root"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Hero image:</strong> ChatGPT generated.
  </div>
</div>

Most ZK-rollup explanations start where the machinery is already compressed: SNARKs, polynomial commitments, circuits, recursion. That is useful **if you already know what is being proved**.

I did not.

Before I wanted a shorter proof, I wanted to understand the ordinary verifier: what it is allowed to see, what stays private, and what predicate must hold for a state change to count.

In the usual notation, **x** is the **public statement** (facts everyone agrees on), **w** is the **private witness** (secret inputs the prover uses), and **R(x, w)** is the **relation** (the check that should return true). The verifier should accept the transition **without** learning **w**.

So I wrote a **small Rust learning repo**, [**rust-zkp**](https://egpivo.github.io/rust-zkp/), not to hand-roll a **SNARK** (*Succinct Non-interactive Argument of Knowledge*: one short proof checked quickly), but to wire up the **same checks a rollup verifier cares about** (signatures, balances, roots, binding) in plain Rust first.

The point is not performance. The point is to see those checks **before** anything bundles them into one succinct object.

Scope-wise, this post is about **toy per-transaction validity checks** you can read in Rust—not the **succinct batch validity proof** many people picture when they hear “ZK rollup.”

## 1. Why I did not start with SNARKs

A SNARK does **not** prove "a blockchain" by itself. It proves a **relation**. If the first tool you meet is a proving-system API, it is easy to memorize names without knowing which balances, nonces, roots, and signatures actually sit inside that relation.

So I started with small primes, explicit Rust checks, and classical building blocks - the boring side of the story - on purpose.

The part I kept getting wrong at first was the line between **checking** a transaction and **proving** one in the SNARK sense. Either way, someone still has to evaluate a **concrete predicate** before mutating state. A proof system mainly changes **how that predicate is packaged**, not whether it exists.

## 2. What the verifier has to believe

The useful mental shift was this: a rollup proof is not proving "a rollup" in the abstract. It is proving a **strict state transition**. In production you would arithmetize that and hand it to a prover; in a learning repo you keep the checks **readable** in code. Concretely, before I trust a transition I want:

- the transaction was signed by the sender;
- the sender had enough balance and a fresh nonce;
- account state lines up with a Merkle root you trust as the "previous world";
- applying the transition yields the new root you publish;
- the proof or transcript is **bound to this exact transaction**, not a reusable blob.

That list is what I wanted to **pin down in code** before asking any framework to shrink it.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-05-03-rust-zkp-learning-demo/new-flow.gif" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-05-03-rust-zkp-learning-demo/new-flow.gif"
         alt="Animated: prover private zone with witness and relation; proof to verifier; Verify with public input only"
         style="max-width:96%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .35rem;">
    <strong>Figure 1.</strong> Who holds what: witness, relation, one message to the verifier, public input only on the check.
  </div>
</div>

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-05-03-rust-zkp-learning-demo/simple_flow.gif" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-05-03-rust-zkp-learning-demo/simple_flow.gif"
         alt="Animated abstract pipeline toward verification without prover or verifier labels"
         style="max-width:96%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .35rem;">
    <strong>Figure 2.</strong> The same idea as a pipeline: constraints and checks, without casting roles yet.
  </div>
</div>

## 3. What I hand-rolled first

In [**rust-zkp**](https://github.com/egpivo/rust-zkp) the cryptographic core is explicit. In scan order:

- **Pedersen commitments**: what it means to hide a value while keeping enough algebraic structure to combine commitments honestly.
- **Sigma + Fiat-Shamir**: how challenge-response proofs become **transcript-bound** checks. In the repo, [**`transcript.rs`**](https://github.com/egpivo/rust-zkp/blob/main/src/transaction.rs) handles length-prefixed, domain-separated hashing;[**`sigma.rs`**](https://github.com/egpivo/rust-zkp/blob/main/src/sigma.rs) wires the proof shape.
- **Merkle membership**: how a verifier checks that an account (or leaf) belongs to a **published state root** without carrying the whole state on-chain.
- **Bit-level constraints**: a small step toward how **range-style** checks are represented from bits upward, including a **toy Schnorr-style OR proof** for bit-like claims in [**`bits.rs`**](https://github.com/egpivo/rust-zkp/blob/main/src/bits.rs) (playground demos make that concrete).
- **Transaction binding**: why a proof must be tied to **this exact** sender, amount, nonce, and message hash, not a reusable blob.
- **WASM / native split**: how the **same Rust** can power browser demos and a toy **Axum** API without forking the protocol logic.

None of that is a SNARK. It is the vocabulary around the verifier.

Before diving into files, this is the shape of `apply_tx`-style checks the repo is trying to make obvious (not copy-pasted from production - labels only):

```rust
// Mindset sketch - not the real API: "would I accept this transition?"
fn accept_if_verifier_happy(tx: &Tx, prev_state: &State) -> Option<State> {
    if !verify_signature(tx.sender, tx.message_hash(), &tx.proof) { return None; }
    if balance_of(prev_state, tx.sender) < tx.amount { return None; }
    if nonce_of(prev_state, tx.sender) != tx.nonce { return None; }
    if !root_coherent(prev_state, tx.from_leaf_proof) { return None; }
    let mut next = prev_state.clone();
    apply_balance_move(&mut next, tx);
    Some(next)
}
```

**How to read it:** signature checks **who**; balance and nonce check **rules**; "root coherent" stands in for Merkle / state inclusion; `apply_balance_move` is the transparent transition you could later arithmetize. The real crate binds Fiat–Shamir to the **serialized transaction fields** similarly (against a `Proof { r, z }` and a transaction-scoped challenge), not necessarily the same helper names as this sketch.

## 4. How the mini rollup composes it

One **layered** picture keeps repeating in the project: the same crypto runs in the browser for demos and beside an Axum server for a real (toy-param) API.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-05-03-rust-zkp-learning-demo/wasm-http-axum-layers.svg" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-05-03-rust-zkp-learning-demo/wasm-http-axum-layers.svg"
         alt="Three columns: Browser WASM sign and prove, HTTP JSON POST tx, native Axum server with mempool batch sled and state root"
         style="max-width:96%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .35rem;">
    <strong>Figure 3.</strong> Same transaction shape: WASM demos on the left, JSON <code>POST /tx</code> in the middle, toy Axum stack on the right (mempool → batch → <strong>sled</strong>).
  </div>
</div>

On top of the primitives sits a tiny rollup: accounts, `State::apply_tx`, a Merkle **state root**, a bounded mempool, a background task that batches and persists to **sled**, and a WebSocket line when a batch closes. It **echoes** the **accept → queue → batch → persist → broadcast** spine you see in larger systems, but this is still a toy: per-transaction checks in Rust, not one succinct batch proof, and none of the production-scale state or economics.

**How to read Figure 4 (dense map):** go **row by row**. Left = "what statement you want," middle = "which module implements it in this repo," right = "how it feeds the mini rollup box." You do not need every cell on the first pass: start with "discrete log -> sigma" and "Merkle -> merkle.rs," then skim the rest.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-05-03-rust-zkp-learning-demo/zk-claims-map.svg" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-05-03-rust-zkp-learning-demo/zk-claims-map.svg"
         alt="Claims mapped to Rust modules composing into mini rollup"
         style="max-width:96%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .35rem;">
    <strong>Figure 4.</strong> Claims in the left column, modules in the middle, composed rollup on the right - including the honest label that this composition is still **not** a SNARK batch proof.
  </div>
</div>

## 5. Where this project stops

It does **not** produce one succinct proof for a whole batch. It does not use a production curve or replace serious stacks: for example **circuit-style frameworks** (Halo2, Plonky2) and **zkVM / end-to-end proving systems** (RISC Zero, SP1) live in a different layer than this repo. The toy parameters are intentional: they keep the checks small enough to inspect.

**rust-zkp** sits below those stacks, but it mirrors the **same checks** they would eventually wrap: signatures, balances, nonces, published roots, and transcript or proof material bound to a **specific** transaction hash.

That boundary is not embarrassment; it is the **point**. The repo stops where a real ZK system picks up: at the door of a prover that would **encode the same checks** and output one short proof object. Getting there still means reworking the predicate for a circuit or AIR (or choosing a zkVM host) - it is not a literal copy-paste of the Rust binary.

I keep a higher-level ZK mental map in the project notes: [ZK mental map](https://egpivo.github.io/rust-zkp/notes/zk_high_level/).

## 6. What comes next

The natural next step is to take the checks you can already read in `apply_tx`, roots, and transcripts, and express a small part of that predicate in a real proving pipeline: a circuit, an AIR trace, or a zkVM program.

I would probably start with one branch of `apply_tx`: signature binding, nonce freshness, or a small Merkle membership check. That is enough to feel the encoding cost without pretending the toy Rust verifier can be copied directly into a production proof system.

For me, the useful lesson was that ZK systems are not only about proving abstract math. They are also about binding proofs to messages, enforcing nonces, checking roots, and keeping transitions auditable in code.

SNARKs stop feeling like a black box when they become "the thing that shrinks this bundle of checks" instead of "the magic layer that proves a rollup."

## 7. Links and try it

[Playground](https://egpivo.github.io/rust-zkp/demos/) · [Notes](https://egpivo.github.io/rust-zkp/notes/) · [Home](https://egpivo.github.io/rust-zkp/) · [GitHub](https://github.com/egpivo/rust-zkp)

If you want to poke it locally, these are the commands I use from the **repo root** (first time: `cd web && npm install`; then `make dev-web`, which wraps `build-wasm` and `npm run dev` inside `web/`):

```bash
cargo run --bin zkp
cargo run --bin cli -- send --from 1 --to 2 --amount 30 --nonce 1 --secret 12345
make dev-web
cargo test
```

The `send` line is a **demo** transfer (toy secret); do not reuse that pattern on a real chain. Alternative dev path: `make build-wasm && cd web && npm run dev`. CI-style checks from root: `make check`. Optional hosted API: [health](https://rust-zkp.onrender.com/health).

## References

A few references I found useful:

- Ethereum.org, [Zero-knowledge rollups](https://ethereum.org/en/developers/docs/scaling/zk-rollups/): standard vocabulary for batches, state roots, and how validity proofs sit on L1.
- Aztec, [ZK-ZK-Rollup: behind the crypto curtain](https://aztec.network/blog/aztecs-zk-zk-rollup-looking-behind-the-cryptocurtain): useful context for how production rollup circuits add **recursion** and heavier proving machinery (not a literal map of this toy repo).
- Vitalik Buterin, [An approximate introduction to how zk-SNARKs are possible](https://vitalik.eth.limo/general/2021/01/26/snarks.html): a helpful bridge from "what is being checked" to why succinct proofs require a different encoding.
