---
layout: post
title: "Building an Interactive P2P Attack Gym in Rust"
date: 2026-06-16
tags: [Rust, Blockchain, Cybersecurity, Web3]
---

*Slot pressure, fake state, and poisoned discovery on `127.0.0.1`.*

The [previous gym post]({{ site.baseurl }}/2026/06/09/building-blockchain-p2p-security-gym-rust.html) gave me terminal metrics: `occupancy`, `honest_peers`, `state_diverged`, and `cross_peers_remaining`. Those numbers were enough to compare runs, but not enough to see the sequence.

That sequence matters. A Sybil run can apply pressure without filling every slot. An Eclipse run can receive a fake `Tip` without diverging. A poisoned seed can bias the first peer list before the victim has formed a useful table.

This post adds `p2p-viz`, the interactive half of the gym in [**rust-p2p-protocol-lab**](https://github.com/egpivo/rust-p2p-protocol-lab). Pick a scenario, set the parameters, and run it from the left panel. The center graph replays the same `p2p-env` simulation: nodes appear, edges draw, peer slots fill. Result Summary on the right still prints the CLI metrics. No new protocol.

---

## `p2p-viz` in the workspace

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-06-16-making-p2p-attack-metrics-visible/fig1_crate_architecture.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-06-16-making-p2p-attack-metrics-visible/fig1_crate_architecture.png"
         alt="Four-crate layout: p2p-core, p2p-node, p2p-lab, and p2p-env, with p2p-viz as the browser layer"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 1.</strong> `p2p-viz` sits above `p2p-env`; it is presentation, not a second simulator.
  </div>
</div>

```bash
cargo run -p p2p-viz
# browser: http://127.0.0.1:3000/
```

The layout follows the gym: scenario buttons and parameter inputs on the left, a D3 topology in the center, Result Summary and Event Log on the right. Clicking a scenario posts your params to `p2p-env` and streams `SimEvent`s over SSE; the graph updates step by step rather than jumping to the final screenshot.

The replay format is intentionally small: nodes, edges, packets, drops, and one terminal summary string.

The Rust boundary is the important part. The browser does not infer attack state from animation timing; it renders typed events emitted by the runner.

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type", rename_all = "snake_case")]
pub enum SimEvent {
    NodeSpawned { id: String, addr: String, role: String },
    ConnectionEstablished { from: String, to: String },
    ConnectionDropped { from: String, to: String },
    PacketSent { from: String, to: String, data: String },
    PeerSlotsFull { node: String },
    ScenarioComplete { scenario: String },
    ScenarioReset,
}
```

That boundary matters for the screenshots. If the replay shows a surviving honest edge, it came from the same run that produced the terminal metric.

---

## Replay 1: Sybil pressure is not capture

The GIF uses the Article preset with Defense on and ten Sybil identities.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-06-16-making-p2p-attack-metrics-visible/fig8_sybil_viz.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-06-16-making-p2p-attack-metrics-visible/fig8_sybil_viz.png"
         alt="Sybil attack visualization: peer slot bar, graph, and result summary showing 62.5% occupancy"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 2.</strong> Terminal state: 5/8 slots Sybil, 62.5% occupancy, `Success: false`.
  </div>
</div>

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-06-16-making-p2p-attack-metrics-visible/sybil.gif" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-06-16-making-p2p-attack-metrics-visible/sybil.gif"
         alt="Sybil attack replay: honest peers connect first, then Sybil identities race for peer slots"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 3.</strong> Replay: honest peers arrive during `reset()`, then Sybil identities compete for slots.
  </div>
</div>

The CLI said `Success: false`. The slot bar explains the result: three honest slots survived. This is still useful pressure, but it is not full capture.

---

## Replay 2: Fake state is not enough

Eclipse adds state to the Sybil story. The GIF uses the Article preset with Defense off and twenty attackers. The attacker sends `attacker_tip_FAKE`; the metric only flips if the victim also loses every honest path.

```text
state_diverged = fake_tip_received && honest_peers == 0
```

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-06-16-making-p2p-attack-metrics-visible/fig10_eclipse_viz.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-06-16-making-p2p-attack-metrics-visible/fig10_eclipse_viz.png"
         alt="Eclipse visualization showing fake Tip delivery with honest peers still connected"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 4.</strong> Terminal state: fake `Tip` received; `honest_peers=3`; `state_diverged=false`.
  </div>
</div>

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-06-16-making-p2p-attack-metrics-visible/eclipse.gif" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-06-16-making-p2p-attack-metrics-visible/eclipse.gif"
         alt="Eclipse attack replay: fake Tip arrives while honest edges stay connected"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 5.</strong> Replay: fake `Tip` lands, but the surviving honest edges remain visible.
  </div>
</div>

This is the point the UI should make: receiving bad state is not the same as being eclipsed. In this lab, Eclipse needs `honest_peers == 0`.

---

## Replay 3: Bad discovery comes first

Nodes do not start with a full peer table. They first need a peer list from seeds, discovery tables, or another bootstrap path.

That first list is already a security boundary. If it is Sybil-heavy, the node starts from a biased network view before normal peer table competition begins.

Bootstrap Poisoning moves the same cheap identity problem earlier. The Bootstrap panel uses eight Sybil identities. The GIF walks through the seed handshake: the victim asks a seed for peers and receives only Sybil addresses.

The metric is not slot occupancy. It is the first peer list:

```text
bootstrap_sybil_ratio = sybil_peers / total_bootstrap_peers
```

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-06-16-making-p2p-attack-metrics-visible/fig16_bootstrap_viz.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-06-16-making-p2p-attack-metrics-visible/fig16_bootstrap_viz.png"
         alt="Bootstrap poisoning visualization: poisoned seed, GetPeers handshake, and 100% sybil ratio on first peer list"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 6.</strong> Terminal state: 8/8 Sybil in the first peer list, `bootstrap_sybil_ratio=100%`.
  </div>
</div>

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-06-16-making-p2p-attack-metrics-visible/bootstrap.gif" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-06-16-making-p2p-attack-metrics-visible/bootstrap.gif"
         alt="Bootstrap poisoning replay: GetPeers handshake and sybil peers accepted on first peer list"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 7.</strong> Replay: `Hello`, `GetPeers`, then poisoned `Peers`.
  </div>
</div>

```bash
cargo run -p p2p-env -- --honest 4 --attack bootstrap --sybil 8
# bootstrap_sybil_ratio: 100.0
# sybil_peers: 8.0
# honest_peers: 0.0
# total_bootstrap_peers: 8.0
```

This run is successful under the lab rule: `bootstrap_sybil_ratio >= 50%`.

---

## Other panels in the gym

The left panel also exposes scenarios I am not treating as the three main replays:

- **Partition**: `cross_peers_remaining=0` when two groups stop advertising each other.
- **TLS MITM Attack**: Mallory remains in the path; `verified_peer=false`; session intercepted.
- **Noise Handshake Defense**: the relay attempt fails on remote key mismatch; the final session is direct and verified.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-06-16-making-p2p-attack-metrics-visible/fig11_partition_viz.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-06-16-making-p2p-attack-metrics-visible/fig11_partition_viz.png"
         alt="Partition visualization showing two isolated node groups"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 8.</strong> Partition terminal state.
  </div>
</div>

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-06-16-making-p2p-attack-metrics-visible/fig12_noise_viz.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-06-16-making-p2p-attack-metrics-visible/fig12_noise_viz.png"
         alt="Noise handshake defense: MITM detected via remote key mismatch"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 9.</strong> Noise is a defense panel, not an attack panel.
  </div>
</div>

**Note:** Noise solves a different problem from Sybil or Bootstrap Poisoning. It can authenticate the remote transport key. It does not make identities expensive, diversify seed responses, or prevent peer table flooding.

---

## Closing

The metrics did not change. The failure conditions became easier to inspect.

- Sybil pressure is visible as slot churn.
- Eclipse failure is visible as surviving honest edges.
- Bootstrap Poisoning is visible before the victim has a clean peer list.

That is the useful boundary for this UI. It does not prove real world exploitability. It shows which local condition made each lab metric flip, or why it did not.

---

## Appendix

```bash
git clone https://github.com/egpivo/rust-p2p-protocol-lab.git
cd rust-p2p-protocol-lab
cargo run -p p2p-viz
# browser: http://127.0.0.1:3000/
```

The runs bind to `127.0.0.1`. Real world references and the original CLI gym are in the [previous post]({{ site.baseurl }}/2026/06/09/building-blockchain-p2p-security-gym-rust.html).
