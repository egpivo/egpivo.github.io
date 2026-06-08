---
layout: post
title: "Three Classic Blockchain P2P Attacks, Rebuilt in a Rust Local Lab"
tags: [Rust, Blockchain, P2P, Security, Web3]
---

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-06-09-building-blockchain-p2p-security-gym-rust/hero.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-06-09-building-blockchain-p2p-security-gym-rust/hero.png"
         alt="Rust P2P Security Gym: Sybil, Eclipse, and Partition local lab on 127.0.0.1 with cargo attack commands and honest, Sybil, and victim peer topology"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
</div>

*Sybil, Eclipse, and Network Partition — from real incidents to local simulations*

I wanted one local Rust lab where I could run three classic blockchain P2P failure modes with one CLI: Sybil, Eclipse, and network partition. The goal was not to attack a live network. The goal was to make each failure mode observable: which peers entered the table, which state message arrived, and whether the victim still had an honest peer to compare against.

Everything runs on `127.0.0.1` in [**rust-p2p-protocol-lab**](https://github.com/egpivo/rust-p2p-protocol-lab).

---

## Overview: why these three attacks?

The three modes, in the order I ran them:

- **Sybil**: one actor creates many identities. Cheap wallets in airdrops, cheap `NodeId`s in P2P; I track `sybil_peers / total_peers` to see how many peer slots one operator can fill.
- **Eclipse**: those identities try to control what a victim sees. Real concern is attacker-controlled state; in the lab I check `state_diverged`—whether bad state sticks when honest peers remain.
- **Partition**: two groups stop seeing each other. Real chain splits show why split views matter; locally I count `cross_peers_remaining` to see whether Group A still advertises Group B.

---

## Lab setup: one Rust workspace, three scenarios

Four crates, one runner:

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-06-09-building-blockchain-p2p-security-gym-rust/architecture.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-06-09-building-blockchain-p2p-security-gym-rust/architecture.png"
         alt="Four-crate layout: p2p-core, p2p-node, p2p-lab, and p2p-env"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 1.</strong> `p2p-core` → `p2p-node` / `p2p-lab` → `p2p-env`.
  </div>
</div>

- **`p2p-core`**: `NodeId`, `Message`
- **`p2p-node`**: honest node behavior, peer table (`MAX_PEERS = 8`)
- **`p2p-lab`**: crawler and attack tools
- **`p2p-env`**: scenario runner (`cargo run -p p2p-env -- ...`)

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-06-09-building-blockchain-p2p-security-gym-rust/01_workspace.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-06-09-building-blockchain-p2p-security-gym-rust/01_workspace.png"
         alt="cargo check success in the rust-p2p-protocol-lab workspace"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 2.</strong> Workspace build.
  </div>
</div>

Protocol is small on purpose:

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-06-09-building-blockchain-p2p-security-gym-rust/handshake-flow.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-06-09-building-blockchain-p2p-security-gym-rust/handshake-flow.png"
         alt="Handshake, keepalive, peer query, and Tip message sequence"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 3.</strong> `Hello`, `Ping`/`Pong`, `GetPeers`/`Peers`, `Tip`.
  </div>
</div>

```rust
pub enum Message {
    Hello {
        node_id: NodeId,
        listen_addr: SocketAddr,
        peers: Vec<SocketAddr>,
    },
    Ping,
    Pong,
    GetPeers,
    Peers(Vec<SocketAddr>),
    Tip {
        height: u64,
        hash: String,
    },
}
```

- **`Hello`**: identity + listen address + known peers
- **`Ping` / `Pong`**: keepalive
- **`GetPeers` / `Peers`**: what the gym queries after each run
- **`Tip`**: a loggable state string so I can see which hash the victim picked up

`Tip` is not a validated block header. It exists so the Eclipse scenario has something to push besides peer-table entries.

---

## Attack 1 — Sybil: many identities, limited peer slots

### Real case

In May 2022, [Optimism removed more than 17,000 Sybil addresses](https://www.optimism.io/blog/let-the-claims-begin) from OP Airdrop #1—wallet farming that had slipped through initial filters. [The Block](https://www.theblock.co/post/148417/optimism-cracks-down-on-airdrop-farmers) reported the same enforcement. That is application-layer abuse, not a P2P attack. The contested resource was token eligibility, not peer slots.

The lab tests the same pressure with a different object: one operator, many cheap `NodeId`s, eight peer slots. Wallet farming and peer-table flooding are not the same mechanism. They share one question: how much can one actor gain by multiplying identities?

### Local model

In my lab, Sybil identities are local nodes with different `NodeId`s. The victim has `MAX_PEERS = 8`. I launched 10 Sybil identities and measured how many peer slots they occupied.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-06-09-building-blockchain-p2p-security-gym-rust/sybil-occupancy.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-06-09-building-blockchain-p2p-security-gym-rust/sybil-occupancy.png"
         alt="Sybil identities occupying slots in a victim peer table"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 4.</strong> Eight slots; many identities compete to hold them open.
  </div>
</div>

```rust
let occupancy = sybil_peers as f64 / peers.len().max(1) as f64 * 100.0;
```

```bash
cargo run -p p2p-env -- --honest 4 --attack sybil --sybil 10
```

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-06-09-building-blockchain-p2p-security-gym-rust/02_sybil.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-06-09-building-blockchain-p2p-security-gym-rust/02_sybil.png"
         alt="Sybil run: 62.5% occupancy, 5 of 8 peers Sybil, Success false"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 5.</strong> 5/8 slots Sybil; `occupancy: 62.5`, `Success: false`.
  </div>
</div>

I expected full capture when I outnumbered the table. I got 5 of 8 slots instead. Honest nodes connected during `reset()` before every Sybil session landed.

This was not Sybil success. It was **62.5% malicious occupancy**, i.e., real pressure on the peer table, but three honest slots still held.

---

## Attack 2 — Eclipse: fake state is not enough

### Real case

[Marcus et al.'s "False Friends" work](https://arxiv.org/abs/1908.10141) showed an Ethereum node could be isolated by flooding its discovery table with attacker-controlled peers, then feeding that victim a filtered chain view. The attack targets peer selection and connection management—not consensus math. The paper reports that countermeasures were incorporated into Geth v1.9.0.

I am not reproducing that attack. It is the reference for why Eclipse sits next to Sybil: Sybil fills slots; Eclipse cuts honest cross-checks.

### Local model

The lab strips that down to one check: attacker peers send a fake `Tip`—does the victim lose every honest peer?

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-06-09-building-blockchain-p2p-security-gym-rust/eclipse-flow.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-06-09-building-blockchain-p2p-security-gym-rust/eclipse-flow.png"
         alt="Eclipse flow: connect, send fake Tip, check peer mix"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 6.</strong> Eclipse path: connect, send fake `Tip`, check peer mix.
  </div>
</div>

```rust
let state_diverged = victim_tip != honest_tip && honest_peers == 0;
```

```bash
cargo run -p p2p-env -- --honest 4 --attack eclipse --sybil 20
```

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-06-09-building-blockchain-p2p-security-gym-rust/03_eclipse.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-06-09-building-blockchain-p2p-security-gym-rust/03_eclipse.png"
         alt="Eclipse run: fake tip logged, 5 honest peers remain, Success false"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 7.</strong> `attacker_tip_FAKE` logged; 3/8 Sybil, 5 honest; `state_diverged=false`.
  </div>
</div>

This was the most useful failed run. The fake state arrived, but the victim still had honest peers. I stopped treating Sybil and Eclipse as the same thing after this run. Sybil gave me peer pressure. Eclipse required removing the honest path.

In this lab, Eclipse requires `honest_peers == 0` before `state_diverged` can flip true.

---

## Attack 3 — Network partition: when groups stop seeing each other

### Real case

In August 2021, [a Geth bug](https://github.com/ethereum/go-ethereum/blob/master/docs/postmortems/2021-08-22-split-postmortem.md) led some unpatched nodes onto a minority chain—a brief split until operators patched. Bitcoin had an earlier version of the same failure mode: [BIP 50](https://bips.dev/50/) documents a March 2013 fork where Bitcoin 0.8 accepted a block that pre-0.8 nodes rejected.

Neither incident used my blocklist model. Both show what happens when two groups stop sharing the same view: recovery becomes a client rollout and coordination problem, not just a consensus rule.

Partition is also the setup people often cite for double-spending scenarios: broadcast conflicting transactions to two isolated groups. That requires a transaction layer, which this lab does not have. Here I only check whether cross-group peers disappear.

### Local model

Six local nodes, Group A `[0,1,2]` and Group B `[3,4,5]`, symmetric blocklists inside the process. Metric: does Group A's peer table still list any Group B port?

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-06-09-building-blockchain-p2p-security-gym-rust/network-partition.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-06-09-building-blockchain-p2p-security-gym-rust/network-partition.png"
         alt="Network partition with symmetric blocklists"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 8.</strong> Symmetric blocklists; metric is `cross_peers_remaining`.
  </div>
</div>

```rust
let cross_peers = a_peers
    .iter()
    .filter(|p| addrs_b.iter().any(|b| b.port() == p.port()))
    .count();
```

```bash
cargo run -p p2p-env -- --honest 6 --attack partition
```

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-06-09-building-blockchain-p2p-security-gym-rust/04_partition.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-06-09-building-blockchain-p2p-security-gym-rust/04_partition.png"
         alt="Partition run: cross_peers_remaining 0, Success true"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 9.</strong> Group A `[0,1,2]` / Group B `[3,4,5]`; `cross_peers_remaining: 0`, `Success: true`.
  </div>
</div>

This is an application-layer local simulation, not BGP routing and not a real Internet partition.

---

## Closing

The most useful result was not the clean partition success. It was the failed Eclipse run. I could deliver fake state, but I could not make that fake state become the victim's only view while honest peers remained. That gap is the real design space: peer replacement, anchor peers, diversity rules, identity cost, and monitoring.

Next knobs I want to turn in the same lab:

- signed `NodeId` or another identity-cost mechanism
- peer diversity policy (subnet / operator bucketing)
- anchor peers that eviction cannot drop
- different peer eviction rules under slot pressure
- IDS scoring on peer-table concentration
- rerun all three modes and compare `occupancy`, `honest_peers`, and `cross_peers_remaining`

---

## Appendix
### Reproduce

```bash
git clone https://github.com/egpivo/rust-p2p-protocol-lab.git
cd rust-p2p-protocol-lab
cargo run -p p2p-env -- --honest 4 --attack sybil --sybil 10
cargo run -p p2p-env -- --honest 4 --attack eclipse --sybil 20
cargo run -p p2p-env -- --honest 6 --attack partition
```



### References

Sources cited for the real-world case introductions:

- Optimism, [Let the Claims Begin](https://www.optimism.io/blog/let-the-claims-begin) (May 2022): OP Airdrop #1 launch; removal of 17,000+ Sybil addresses.
- The Block, [Optimism Cracks Down on Airdrop Farmers](https://www.theblock.co/post/148417/optimism-cracks-down-on-airdrop-farmers) (May 2022): press coverage of the same sybil filtering.
- Marcus et al., [Eclipsing Ethereum Peers with False Friends](https://arxiv.org/abs/1908.10141) (arXiv, 2019): Ethereum eclipse attack via peer-table flooding; paper reports Geth v1.9.0 countermeasures.
- Go-Ethereum, [Minority Split Postmortem](https://github.com/ethereum/go-ethereum/blob/master/docs/postmortems/2021-08-22-split-postmortem.md) (August 2021): August 2021 chain split affecting unpatched Geth nodes.
- [BIP 50: March 2013 Chain Fork Post-Mortem](https://bips.dev/50/): Bitcoin 0.8 vs pre-0.8 block acceptance mismatch.
