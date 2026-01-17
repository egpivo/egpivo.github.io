---
layout: post
title: "Learning Consensus Algorithms: A Hands-On Comparison with Rust"
tags: [Rust, Blockchain, Consensus]
---

I conceptually implemented five consensus algorithms in Rust to compare PBFT, Gossip, Eventual Consistency, Quorum-less, and Flexible Paxos. The project is [rust-market-ledger](https://github.com/egpivo/rust-market-ledger). Everything runs on a single machine with simulated consensus logic and SQLite storage. Some scaling solutions like sharding require real distributed systems, which I don't have here.

For metrics, I used [Aliyu et al. (2025)](https://arxiv.org/pdf/2505.03768) because they break down scalability into measurable constructs like throughput and latency. Some metrics (geographic diversity, hash power distribution) don't apply to a simulated environment, so I skipped those.

The [demo page](https://egpivo.github.io/rust-market-ledger/) shows the results.

## The Scalability Problem

As a blockchain network grows, developers face a fundamental scaling challenge: **more nodes increase decentralization (measured by the [Nakamoto coefficient](https://nakaflow.io/)), but reduce throughput**.

<div style="text-align:center; margin: 2rem 0;">
  <a href="https://nakaflow.io/" target="_blank">
    <img src="{{ site.baseurl }}/assets/2026-01-17-learning-consensus-algorithms/nakameot_coef.png?v=1" alt="Nakamoto Coefficient: Real-time decentralization metrics for Proof-of-Stake Networks" style="max-width:90%; height:auto; border: 1px solid #ddd; border-radius: 8px; cursor: pointer;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">Nakamoto coefficient: real-time decentralization metrics for Proof-of-Stake networks (2026-01-17 from <a href="https://nakaflow.io/" target="_blank">nakaflow.io</a>)</div>
</div>

Why? Every validating node must process all transactions, communicate with peers, and participate in consensus to finalize blocks. This creates a bottleneck. As the network scales, coordination overhead grows.

Ethereum processes ~20 TPS (Sharma, 2024). Solana achieves ~3,000 TPS by innovating consensus (Proof of History + PBFT). Newer chains like Aptos and Sui target even higher throughput through parallel processing.

The core tension: **decentralization requires more nodes, but more nodes mean slower consensus**. Consensus algorithms shape this trade-off. Some optimize for security (PBFT), others for speed (Gossip). Understanding these choices requires measuring the trilemma: decentralization, security, and scalability.

## The Blockchain Trilemma

I initially found the trilemma concept abstract, but after implementing these algorithms, the trade-offs became concrete. The blockchain trilemma says three desirable properties—decentralization, security, and scalability—are difficult to maintain simultaneously. As a network evolves, one trait usually dominates, and enhancing the others may weaken the dominant one.

More nodes increase decentralization but reduce scalability: every node must process transactions and participate in consensus, which slows down the network. Security also becomes more challenging with more participants (more attack surface).

Following [Aliyu et al. (2025)](https://arxiv.org/pdf/2505.03768), a blockchain system consists of:

- **Transaction Originators** (m nodes): External entities that submit transactions
- **Validating Nodes** (n nodes): Core processing units with Interface, Consensus Protocol, and optional State Machine Replica
- **Three phases**: Entry & Propagation → Consensus & Ordering → State Execution & Replication

<div style="text-align:center; margin: 2rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-01-17-learning-consensus-algorithms/Aliyu_2025_fig_1.png?v=1" alt="Blockchain System Model" style="max-width:90%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">Blockchain system model (from Aliyu et al., 2025)</div>
</div>

### Measuring the Trilemma

According to Aliyu et al., measuring Decentralization (DoD) is notoriously difficult because constructs like "Block Proposal Randomness" are easy to simulate, but "Wealth Distribution" depends on user behavior which I had to mock with randomized data. The measurement framework follows: **Concept** → **Subconcepts** → **Constructs** → **Metrics**.

I focused on metrics I could actually implement:

- **DoD (Decentralization)**: Nakamoto coefficient, Gini coefficient. The challenge: lacks social factors (node ownership, collusion risks), which are hard to simulate
- **Scalability**: Throughput (blocks/sec), confirmation latency. This is the most mature area—I could directly measure these in my Rust benchmarks. In this simulation, each block represents a transaction batch, so blocks/sec approximates TPS
- **Security**: Cost of attack, fault tolerance, stale block rate. No single metric captures all aspects, so I combined multiple indicators

<div style="text-align:center; margin: 2rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-01-17-learning-consensus-algorithms/Aliyu_2025_fig_2.png?v=1" alt="Trilemma Measurement Framework" style="max-width:90%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">Trilemma measurement framework (from Aliyu et al., 2025)</div>
</div>

**Trade-offs:**

- **DoD vs. Scalability**: More nodes → higher DoD but reduced throughput (more coordination overhead)
- **DoD vs. Security**: Geographic distribution reduces collusion but increases latency (weakens security assumptions)
- **Scalability vs. Security**: Fewer nodes → better performance but concentrates attack surface

### Scaling Solutions: Layer-1 vs Layer-2

Addressing scalability involves choosing between Layer-1 (protocol-level) and Layer-2 (off-chain) solutions:

**Layer-1 solutions** modify the blockchain's core protocol:
- **Sharding**: Divide the network into parallel shards, each processing a subset of transactions (e.g., Ethereum 2.0)
- **Consensus innovation**: Optimize consensus mechanisms (e.g., Solana's Proof of History, Aptos/Sui's parallel processing)
- **Parallel processing**: Process transactions simultaneously within blocks instead of sequentially

**Layer-2 solutions** build on top of existing chains:
- **Sidechains**: Separate blockchains with faster rules, assets flow between main chain and sidechain
- **Rollups**: Execute transactions off-chain, store compressed proofs on-chain (Optimistic rollups like Arbitrum, ZK rollups like PLONK)

Each solution makes different trade-offs. Consensus algorithm choice is a fundamental Layer-1 decision that affects all scalability efforts. Our comparison focuses on consensus algorithms—the foundation that determines baseline performance before Layer-2 optimizations.

## Implementation Examples

We implement five consensus algorithms for comparison. Brief overviews:

- **PBFT (Practical Byzantine Fault Tolerance)**: Classic Byzantine fault-tolerant consensus for distributed systems. Requires 3f+1 nodes to tolerate f Byzantine faults. Reference: [Castro & Liskov (1999)](https://css.csail.mit.edu/6.824/2014/papers/castro-practicalbft.pdf).

- **Gossip Protocol**: Decentralized communication protocol based on epidemic propagation model. Nodes spread messages to random peers without voting. Reference: [Demers et al. (1987)](http://disi.unitn.it/~montreso/ds/papers/montresor17.pdf).

- **Eventual Consistency**: Provides eventual consistency guarantees—replicas converge after updates stop. Common in distributed databases. Reference: [Terry et al. (1995)](https://people.eecs.berkeley.edu/~brewer/cs262b/update-conflicts.pdf).

- **Flexible Paxos**: Variant of Paxos that addresses majority voting constraints by allowing different quorum sizes for different phases, relaxing the strict intersection requirement. Reference: [Howard et al. (2016)](https://ar5iv.labs.arxiv.org/html/1608.06696).

- **Quorum-less Consensus**: Consensus mechanisms that don't rely on traditional quorum intersections, common in permissionless networks. Reference: [Nano consensus (2020)](https://dl.acm.org/doi/pdf/10.1145/3772052.3772268).

See references for detailed algorithms and correctness proofs. We show implementation examples for PBFT and Gossip below.

### PBFT: Three-Phase Byzantine Fault Tolerance

PBFT requires 3f+1 nodes to tolerate f Byzantine faults. Implementing PBFT's three phases in Rust was tricky. Handling the state transitions required wrapping the consensus state in an `Arc<RwLock>`, which heavily impacted the code structure compared to the simplistic Gossip implementation. Every block goes through three phases:

```rust
async fn propose(&self, block: &Block) -> Result<ConsensusResult, Box<dyn Error>> {
    let sequence = block.index;
    
    // Phase 1: Pre-Prepare (primary proposes)
    if self.pbft.is_primary(sequence) {
        let pre_prepare_msg = self.pbft.create_pre_prepare(
            &block.hash, &block_json, sequence
        );
        broadcast_message(&pre_prepare_msg, &self.node_addresses, self.port).await;
        self.pbft.handle_pre_prepare(&pre_prepare_msg);
    }
    
    tokio::time::sleep(Duration::from_millis(500)).await;
    
    // Phase 2: Prepare (nodes vote)
    let prepare_msg = self.pbft.create_prepare(&block.hash, sequence);
    broadcast_message(&prepare_msg, &self.node_addresses, self.port).await;
    self.pbft.handle_prepare(&prepare_msg);
    
    tokio::time::sleep(Duration::from_millis(500)).await;
    
    // Phase 3: Commit (finalize after 2f+1 votes)
    let commit_msg = self.pbft.create_commit(&block.hash, sequence);
    broadcast_message(&commit_msg, &self.node_addresses, self.port).await;
    self.pbft.handle_commit(&commit_msg);
    
    // Check if committed (requires 2f+1 commits)
    let state = self.pbft.state.read();
    if state.committed_blocks.contains(&sequence) {
        Ok(ConsensusResult::Committed(block.clone()))
    } else {
        Ok(ConsensusResult::Pending)
    }
}
```

In this simulation, PBFT averages 1500ms ± 50ms because it requires three sequential phases, each waiting for 2f+1 votes. The 500ms delays between phases are my simulation's network round-trip estimates—in reality, these would depend on actual network latency. This ensures safety with Byzantine faults but costs latency.

### Gossip: Epidemic Propagation

Gossip doesn't require voting—nodes spread messages to random peers (fanout=2). I realized this makes the Rust implementation much simpler: no `Arc<RwLock>` hell, just a `HashMap` tracking which nodes have seen each block. Consensus emerges when enough nodes have seen the block:

```rust
async fn propose(&self, block: &Block) -> Result<ConsensusResult, Box<dyn Error>> {
    // Track which nodes have seen this block
    {
        let mut state = self.state.write();
        let gossip_state = state.entry(block.index).or_insert_with(|| GossipState {
            block_index: block.index,
            block_hash: block.hash.clone(),
            received_from: HashSet::new(),
            timestamp: Self::get_timestamp(),
        });
        gossip_state.received_from.insert(self.node_id);
    }
    
    // Gossip rounds: spread to random peers
    for _ in 0..self.gossip_rounds {
        tokio::time::sleep(Duration::from_millis(100)).await;
        let mut state = self.state.write();
        if let Some(gossip_state) = state.get_mut(&block.index) {
            for _ in 0..self.fanout {
                gossip_state.received_from.insert(self.node_id);
            }
        }
    }
    
    // Commit when enough nodes have seen it (no majority required)
    let state = self.state.read();
    if let Some(gossip_state) = state.get(&block.index) {
        if gossip_state.received_from.len() >= self.gossip_rounds {
            self.committed.write().insert(block.index);
            return Ok(ConsensusResult::Committed(block.clone()));
        }
    }
    
    Ok(ConsensusResult::Pending)
}
```

Notice there's no voting logic here. This makes the propose function incredibly fast—just updating a HashMap and firing network requests. In this simulation, Gossip is 5x faster than PBFT (300ms vs 1500ms) because there's no voting or quorum requirement. However, it sacrifices Byzantine fault tolerance: no mechanism to verify message authenticity, so nodes have no idea if the peer they're talking to is lying.

## Simulation

With the trilemma framework in mind, here's how I set up the simulation to measure consensus algorithms:

- **Number of nodes**: 4 nodes total (n=4). For PBFT, this means f=1 (tolerates 1 Byzantine fault, requires 3f+1=4 nodes)
- **Network model**: Fixed latency delays between phases. PBFT uses 500ms per phase (simulating network round-trips), Gossip uses 100ms per round
- **Block generation**: 100 test blocks with simulated BTC price data. All algorithms process the same blocks for fair comparison
- **Trials**: 5 rounds per algorithm. Reported latency and throughput are means with standard deviation (±)
- **Trilemma scores (1-5)**: These are qualitative assessments based on algorithm characteristics. PBFT gets 5.0/5.0 for security because it tolerates Byzantine faults; Gossip gets 5.0/5.0 for scalability because it doesn't require voting. They're not derived from metrics—they reflect the algorithm design trade-offs
- **Throughput**: Measured as blocks per second. In this simulation, each block represents a single transaction batch, so blocks/sec ≈ TPS
- **Latency**: Includes algorithmic delays (phases, rounds) and simulated network communication. The artificial sleeps (500ms for PBFT, 100ms for Gossip) model network round-trips
- **Storage**: SQLite database on a single machine. No actual distributed network—consensus logic is simulated

### Result

I generated 100 test blocks with simulated BTC price data and ran each algorithm on the same blocks. Results averaged over 5 rounds (mean ± standard deviation):

<div style="text-align:center; margin: 2rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-01-17-learning-consensus-algorithms/sample-blocks-table.png?v=1" alt="Sample Blocks Table" style="max-width:90%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">Sample blocks: simulated BTC price data (10-block sample shown)</div>
</div>

<div style="text-align:center; margin: 2rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-01-17-learning-consensus-algorithms/btc-price-timeseries.png?v=1" alt="BTC Price Time Series" style="max-width:90%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">BTC price time series (simulated data)</div>
</div>

<div style="text-align:center; margin: 2rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-01-17-learning-consensus-algorithms/trilemma_score.png?v=1" alt="Trilemma Scores Comparison" style="max-width:90%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">Trilemma scores: decentralization, security, and scalability comparison across algorithms</div>
</div>

**Summary Comparison:**

<table style="width:100%; border-collapse: collapse;">
<thead>
<tr style="border-bottom: 2px solid #ddd;">
<th style="text-align:left; padding: 8px;">Algorithm</th>
<th style="text-align:center; padding: 8px;">Decentralization</th>
<th style="text-align:center; padding: 8px;">Security</th>
<th style="text-align:center; padding: 8px;">Scalability</th>
<th style="text-align:center; padding: 8px;">Latency (ms)</th>
<th style="text-align:center; padding: 8px;">Throughput (blocks/sec)</th>
</tr>
</thead>
<tbody>
<tr style="border-bottom: 1px solid #eee;">
<td style="padding: 8px;"><strong>PBFT</strong></td>
<td style="text-align:center; padding: 8px;">4.0/5.0</td>
<td style="text-align:center; padding: 8px; background-color: #d4edda;"><strong>5.0/5.0</strong></td>
<td style="text-align:center; padding: 8px; background-color: #f8d7da;">2.0/5.0</td>
<td style="text-align:center; padding: 8px; background-color: #f8d7da;">1500 ± 50</td>
<td style="text-align:center; padding: 8px;">66.67</td>
</tr>
<tr style="border-bottom: 1px solid #eee;">
<td style="padding: 8px;"><strong>Gossip</strong></td>
<td style="text-align:center; padding: 8px; background-color: #d4edda;"><strong>5.0/5.0</strong></td>
<td style="text-align:center; padding: 8px;">3.0/5.0</td>
<td style="text-align:center; padding: 8px; background-color: #d4edda;"><strong>5.0/5.0</strong></td>
<td style="text-align:center; padding: 8px;">300 ± 10</td>
<td style="text-align:center; padding: 8px;">333.33</td>
</tr>
<tr style="border-bottom: 1px solid #eee;">
<td style="padding: 8px;"><strong>Eventual</strong></td>
<td style="text-align:center; padding: 8px;">4.0/5.0</td>
<td style="text-align:center; padding: 8px; background-color: #f8d7da;">2.0/5.0</td>
<td style="text-align:center; padding: 8px;">4.0/5.0</td>
<td style="text-align:center; padding: 8px;">500 ± 5</td>
<td style="text-align:center; padding: 8px;">200.0</td>
</tr>
<tr style="border-bottom: 1px solid #eee;">
<td style="padding: 8px;"><strong>Quorum-less</strong></td>
<td style="text-align:center; padding: 8px;">4.0/5.0</td>
<td style="text-align:center; padding: 8px;">3.5/5.0</td>
<td style="text-align:center; padding: 8px;">4.5/5.0</td>
<td style="text-align:center; padding: 8px; background-color: #d4edda;"><strong>0.5 ± 0.1</strong></td>
<td style="text-align:center; padding: 8px; background-color: #d4edda;"><strong>2000.0</strong></td>
</tr>
<tr>
<td style="padding: 8px;"><strong>Flexible Paxos</strong></td>
<td style="text-align:center; padding: 8px;">4.0/5.0</td>
<td style="text-align:center; padding: 8px;">4.5/5.0</td>
<td style="text-align:center; padding: 8px;">3.0/5.0</td>
<td style="text-align:center; padding: 8px;">800 ± 30</td>
<td style="text-align:center; padding: 8px;">125.0</td>
</tr>
</tbody>
</table>

*Highlighted: <span style="background-color: #d4edda; padding: 2px 4px;">green = best</span>, <span style="background-color: #f8d7da; padding: 2px 4px;">red = worst</span>. For full interactive comparison, see the [live demo](https://egpivo.github.io/rust-market-ledger/).*

**Detailed Metrics:**

**Scalability - 3 Metrics:**

<table style="width:100%; border-collapse: collapse;">
<thead>
<tr style="border-bottom: 2px solid #ddd;">
<th style="text-align:left; padding: 8px;">Strategy</th>
<th style="text-align:center; padding: 8px;">Availability (%)</th>
<th style="text-align:center; padding: 8px;">Confirmation Latency (ms)</th>
<th style="text-align:center; padding: 8px;">Max Throughput (blocks/sec)</th>
</tr>
</thead>
<tbody>
<tr style="border-bottom: 1px solid #eee;">
<td style="padding: 8px;"><strong>PBFT</strong></td>
<td style="text-align:center; padding: 8px;">100.0</td>
<td style="text-align:center; padding: 8px; background-color: #f8d7da;">1500.0</td>
<td style="text-align:center; padding: 8px;">66.67</td>
</tr>
<tr style="border-bottom: 1px solid #eee;">
<td style="padding: 8px;"><strong>Gossip</strong></td>
<td style="text-align:center; padding: 8px;">100.0</td>
<td style="text-align:center; padding: 8px;">300.0</td>
<td style="text-align:center; padding: 8px;">333.33</td>
</tr>
<tr style="border-bottom: 1px solid #eee;">
<td style="padding: 8px;"><strong>Eventual</strong></td>
<td style="text-align:center; padding: 8px;">100.0</td>
<td style="text-align:center; padding: 8px;">500.0</td>
<td style="text-align:center; padding: 8px;">200.0</td>
</tr>
<tr style="border-bottom: 1px solid #eee;">
<td style="padding: 8px;"><strong>Quorum-less</strong></td>
<td style="text-align:center; padding: 8px;">100.0</td>
<td style="text-align:center; padding: 8px; background-color: #d4edda;"><strong>0.5</strong></td>
<td style="text-align:center; padding: 8px; background-color: #d4edda;"><strong>2000.0</strong></td>
</tr>
<tr>
<td style="padding: 8px;"><strong>Flexible Paxos</strong></td>
<td style="text-align:center; padding: 8px;">100.0</td>
<td style="text-align:center; padding: 8px;">800.0</td>
<td style="text-align:center; padding: 8px;">125.0</td>
</tr>
</tbody>
</table>

**Security - 4 Metrics:**

<table style="width:100%; border-collapse: collapse;">
<thead>
<tr style="border-bottom: 2px solid #ddd;">
<th style="text-align:left; padding: 8px;">Strategy</th>
<th style="text-align:center; padding: 8px;">Cost of Attack</th>
<th style="text-align:center; padding: 8px;">Fault Tolerance</th>
<th style="text-align:center; padding: 8px;">Reliability (%)</th>
<th style="text-align:center; padding: 8px;">Stale Block Rate (%)</th>
</tr>
</thead>
<tbody>
<tr style="border-bottom: 1px solid #eee;">
<td style="padding: 8px;"><strong>PBFT</strong></td>
<td style="text-align:center; padding: 8px; background-color: #d4edda;"><strong>0.75</strong></td>
<td style="text-align:center; padding: 8px; background-color: #d4edda;"><strong>0.25</strong></td>
<td style="text-align:center; padding: 8px;">100.0</td>
<td style="text-align:center; padding: 8px;">0.0</td>
</tr>
<tr style="border-bottom: 1px solid #eee;">
<td style="padding: 8px;"><strong>Gossip</strong></td>
<td style="text-align:center; padding: 8px;">0.30</td>
<td style="text-align:center; padding: 8px;">0.10</td>
<td style="text-align:center; padding: 8px;">100.0</td>
<td style="text-align:center; padding: 8px;">0.0</td>
</tr>
<tr style="border-bottom: 1px solid #eee;">
<td style="padding: 8px;"><strong>Eventual</strong></td>
<td style="text-align:center; padding: 8px;">0.30</td>
<td style="text-align:center; padding: 8px;">0.10</td>
<td style="text-align:center; padding: 8px;">100.0</td>
<td style="text-align:center; padding: 8px;">0.0</td>
</tr>
<tr style="border-bottom: 1px solid #eee;">
<td style="padding: 8px;"><strong>Quorum-less</strong></td>
<td style="text-align:center; padding: 8px;">0.30</td>
<td style="text-align:center; padding: 8px;">0.10</td>
<td style="text-align:center; padding: 8px;">100.0</td>
<td style="text-align:center; padding: 8px;">0.0</td>
</tr>
<tr>
<td style="padding: 8px;"><strong>Flexible Paxos</strong></td>
<td style="text-align:center; padding: 8px; background-color: #d4edda;"><strong>0.75</strong></td>
<td style="text-align:center; padding: 8px; background-color: #d4edda;"><strong>0.25</strong></td>
<td style="text-align:center; padding: 8px;">100.0</td>
<td style="text-align:center; padding: 8px;">0.0</td>
</tr>
</tbody>
</table>

**Key takeaways:**

PBFT pays a 400% latency tax for its security (1500ms vs Gossip's 300ms) in this simulation. Gossip maximizes scalability (333.33 blocks/sec) but sacrifices security (cost of attack: 0.30). Quorum-less achieves 2000 blocks/sec with 0.5ms latency, but its low cost of attack (0.30) would be vulnerable in a real adversarial network. No algorithm scores 5.0/5.0 on all three dimensions—that's the trilemma.

The [demo page](https://egpivo.github.io/rust-market-ledger/) shows interactive comparison. To run locally:

```bash
git clone https://github.com/egpivo/rust-market-ledger.git
cd rust-market-ledger
cargo run --example trilemma_comparison
```

---

**Explore the Project:**

- **Demo Page:** [Consensus Algorithm Comparison](https://egpivo.github.io/rust-market-ledger/)
- **GitHub Repository:** [rust-market-ledger](https://github.com/egpivo/rust-market-ledger)

**References:**

- Aliyu et al. (2025). "[From Concept to Measurement: A Survey of How the Blockchain Trilemma Is Analyzed](https://arxiv.org/pdf/2505.03768)"
- Sharma (2024). *Rust for Blockchain Application Development*. Packt Publishing.
