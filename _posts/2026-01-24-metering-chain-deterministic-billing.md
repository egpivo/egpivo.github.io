---
layout: post
title: "Metering Chain: Deterministic Billing"
tags: [Rust, Blockchain, DePIN]
---

I started working on Metering Chain after yet another “we have the logs, but the bill still feels wrong” incident in a usage-based system.
On paper, everyone had telemetry: operators, indexers, dashboards, even a couple of CSV exports.
In practice, each of them told a slightly different story, and there was no obvious way to say: “if we all replay the same history, we will all land on the same number.”

That’s the itch this project is trying to scratch.

<div style="text-align:center; margin: 2rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-01-24-metering-chain/metering.png"
       alt="Row of analog electricity meters"
       style="max-width:90%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    Real-world metering: deterministic, auditable, and independent of who is paying whom (https://solarnrg.ph/blog/how-does-net-metering-work/).
  </div>
</div>

---

## Metering is not new

The concept of metering is as old as utility services themselves. Whether it’s an electricity meter outside your home or a gas meter, the core idea remains constant: a transparent, verifiable, and immutable record of consumption that both provider and consumer can trust. This physical analogy is the mental model I keep coming back to: a source of truth that is undeniable and independently auditable.

<div style="text-align:center; margin: 2rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-01-24-metering-chain/DePIN_infra.png"
       alt="DePIN architecture flow with Metering Chain as the billing layer"
       style="max-width:70%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    Where Metering Chain sits in a typical DePIN stack: between physical services and L1/L2 settlement, turning usage into a deterministic bill.
  </div>
</div>

---

## What Metering Chain actually is

I ended up thinking about Metering Chain as a kind of **billing kernel**, i.e., not a service, not a platform, but something you embed when you need billing to be boring and correct.

Under the hood it’s a small Rust state machine.
You feed it signed transactions like `Mint`, `OpenMeter`, `Consume`, and `CloseMeter`; it walks through them in order and you get back accounts, meters, and reports.
There is no hidden clock, no background job, no extra data source, the whole point is that anyone who replays the same history lands on the same balances.

---

## A real DePIN example: replaying on-chain rewards

The most interesting part of Metering Chain for me is this:  
**it can run directly on real on-chain history, not just toy data.**

DIMO is a DePIN project where vehicles earn token rewards based on data contributions.

In `examples/depin/` there’s a full demo that uses the SIM Dune Activity API to read real reward distributions (e.g. DIMO), map them into `Consume` transactions, and push them through Metering Chain.
The code and scripts there are closer to “real life” than a toy example: they pull on-chain transfers, normalise decimals, and then just treat the result as usage.

---

## From local story to real DePIN demo

If you just want to kick the tires and see a bill show up on your own machine, I’d start small and then immediately jump to real data.
Run the minimal “Alice uses storage” story in `examples/tx/` to see how `Mint`, `OpenMeter`, `Consume`, and `CloseMeter` fit together, then head straight to `examples/depin/` and follow the README.
That second step is the real point of the project for me: take a slice of on-chain activity, replay it as `Consume` transactions, and check that you and I both end up with the same numbers.

For the DIMO run that produced the screenshots in this post, I sampled the last 100 transfers from the DIMO token contract on Polygon and ended up with 74 usable transfers.
After scaling 18‑decimal token amounts down to 6 decimals, that worked out to 20,648,615,899 reward units, priced at a unit price of 1.
Replaying those 74 transfers as `Consume` events against a single `dimo-rewards` meter gave me exactly what I hoped for: one account, one meter, and one report that I can throw away and recompute any time from nothing but `tx.log`.

<div style="text-align:center; margin: 1.5rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-01-24-metering-chain/demo_results/sim_demo_analysis.png"
       alt="SIM Dune DIMO transfer analysis for the sampled window"
       style="max-width:90%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    How the sampled DIMO window actually looks: transfers per day, total units, top senders, and size distribution before turning everything into <code>Consume</code> events.
  </div>
</div>

<div style="text-align:center; margin: 1.5rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-01-24-metering-chain/demo_results/sim_demo_result.png"
       alt="SIM Dune DIMO rewards replayed through Metering Chain"
       style="max-width:90%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    One concrete run of the SIM Dune DIMO rewards demo: 74 transfers, 20,648,615,899 units, and a deterministic bill that anyone can replay from <code>tx.log</code>.
  </div>
</div>

If you want to see every command that produced that result, they’re all in `examples/depin/`: the point of the blog post is just to show that the whole thing reduces to “indexer output in, reproducible bill out.”

---

## If you want to dig into the repo

To reproduce anything in this post, you don’t need more documentation. You just need the repo.
The minimal “Alice uses storage” story lives in `examples/tx/`, the DIMO / SIM Dune demo lives in `examples/depin/`, and the copy I drafted against while writing this article was checked out under GitHub repo [`egpivo/metering-chain`](https://github.com/egpivo/metering-chain).

Under the hood, the design is deliberately small: pure data types and pure transactions (`Mint`, `OpenMeter`, `Consume`, `CloseMeter`) on one side, and a thin storage/CLI layer on the other.
Storage is just an append-only `tx.log` plus occasional `state.bin` snapshots; on restart you load the latest snapshot (or genesis) and replay `tx.log[snapshot_tx_id+1..]` to get back to the exact same state.
That’s what makes the DIMO demo work: all the SIM / Dune / plotting code lives outside, and the core just sees a sequence of signed `Consume` calls.

<div style="text-align:center; margin: 1.5rem 0;">
  <img src="{{ site.baseurl }}/assets/2026-01-24-metering-chain/arch.gif"
       alt="Internal architecture of Metering Chain: domain state machine over an append-only log"
       style="max-width:90%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    The repo’s core architecture: a pure billing state machine over an append-only log and snapshots, wired up to a thin CLI and storage layer.
  </div>
</div>

The end-to-end tests in `tests/basic_flow.rs` are basically “does replay really give me the same bill?” scenarios: snapshot part-way through, append more txs, restart, and assert the reconstructed `State` matches.
As long as you keep `tx.log` and one snapshot (or genesis), you can always recompute balances, meters, and receipts, which is exactly the property you want for DePIN and other usage-based systems.
