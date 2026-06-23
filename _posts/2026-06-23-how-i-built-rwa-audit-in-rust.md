---
layout: post
title: "From RWA Evidence Collectors to a Rust Audit Toolkit"
date: 2026-06-23
tags: [RWA, Rust, Blockchain, Web3, Software]
---

*One CLI, three contracts, versioned evidence bundles.*

---

Tokenized real-world assets create a blockchain audit problem, not just a market-data problem. A token may reference gold, Treasuries, or equities, but the observable evidence is split across contract registries, ERC-20 transfers, DEX pools, aggregator quotes, transaction receipts, and exchange-side files. The hard part is not only collecting those surfaces. It is preserving what each surface can and cannot prove.

The first three RWA articles extended the same Rust repository in different directions.

[Part I]({{ site.baseurl }}/2026/06/07/if-everything-can-be-tokenized-what-should-we-audit.html) added registry and activity collectors. [Part II]({{ site.baseurl }}/2026/06/14/where-rwa-trades-and-exits-actually-clear.html) added pool panels, quote sweeps, and transaction reconstruction. [Part III]({{ site.baseurl }}/2026/06/21/where-rwa-exchange-risk-actually-sits.html) added an exchange freeze path, xStocks evidence files, and a manifest.

The collectors worked, but each article added its own command and output convention. API configuration, caching, provenance, live versus publish data, file inventories, and promotion were spread across the codebase. The refactor collected those concerns into three contracts: modules define how an audit runs, sources define how observations enter the system, and publish bundles define what may leave it.

---

## Three collectors, one repeated problem

The repository was already written mainly in Rust, with Python used for figures. The problem was not a language migration. It was the repository shape.

Part I wrote registry and activity outputs. Part II kept flow snapshots under `data/flow/`. Part III introduced `rwa-exchange-freeze`, `artifacts/data/manifest.json`, and an article-specific publish set. Each pipeline was usable, but adding another audit meant deciding again how to configure sources, name outputs, separate live data, and package evidence.

The repeated question was not "how should every collector look the same?" Registry logs, ParaSwap quotes, and xStocks reference files should remain different. The useful question was narrower: which boundaries must every collector declare?

---

## High-level structure

Within the main Rust crate, the refactor added a unified CLI and explicit module, source, and publication boundaries around the existing collectors.

```
rwa-audit/
 ├─ crates/rwa-audit/src/
 │   ├─ bin/        ← CLI entry points
 │   ├─ audit/      ← module contract + dispatcher
 │   ├─ core/       ← manifest + publish bundles
 │   ├─ sources/    ← adapters + cache + transport
 │   ├─ tools/      ← analysis primitives
 │   ├─ exchange/   ← xStocks evidence collector
 │   └─ flow/       ← pool, quote, and tx collectors
 ├─ config/         ← asset and source settings
 ├─ artifacts/      ← versioned publish bundles
 └─ data/           ← collector output and live staging
```

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-06-23-how-i-built-rwa-audit-in-rust/architecture.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-06-23-how-i-built-rwa-audit-in-rust/architecture.png"
         alt="rwa-audit architecture: CLI dispatches audit modules; modules use source adapters and analysis tools; validated evidence is promoted through the publish contract into versioned audit bundles."
         style="max-width:96%; height:auto; border: 1px solid #ddd; border-radius: 6px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <em><strong>Fig. 1.</strong> Collection and publication are separate paths. A module can write evidence without qualifying it for promotion.</em>
  </div>
</div>

## What Rust actually gave

Rust did not decide what counts as evidence. It made the evidence boundary harder to blur in code.

Four choices mattered:

- enums keep run modes and HTTP outcomes as distinct states;
- trait objects make module and publication obligations visible at dispatch boundaries;
- generics let one provenance envelope wrap different response payloads;
- `serde` and typed errors keep configuration, evidence, manifests, and failures consistent across the pipeline.

The run-mode distinction is small but concrete:

```rust
pub enum RunMode {
    Live,
    Frozen { snapshot_date: Option<String> },
}
```

Registry and flow modules are live collectors. The exchange module also has a frozen path that reads the committed publish fixtures. Its live mode writes to `data/exchange-live/`; it cannot be promoted through the normal exchange publish path.

Enums also keep audit states from collapsing into loosely related flags. `RunMode::Frozen` carries its optional snapshot date, while `HttpGetResult` keeps a valid response, rate limit, and semantic client error distinct. When code branches on those enums, pattern matching makes the states explicit. In the quote path, that means a provider's "no route" response can remain different from a transport failure.

A Python or Go implementation could enforce the same design. Rust helped because the project had accumulated enough modes, sources, and output paths that conventions alone were becoming difficult to review.

---

## Boundary 1 — Modules declare their audit contract

The unified CLI dispatches `registry`, `activity`, `article1`, `flow-panel`, `flow-quotes`, `flow-tx`, and `exchange`. Their procedures differ, but they implement one interface:

```rust
pub trait AuditModule: Send + Sync {
    fn name(&self) -> &'static str;
    fn method(&self) -> AuditMethod;
    fn required_sources(&self) -> Vec<SourceId>;
    fn run(
        &self,
        ctx: &AuditContext,
        mode: RunMode,
        extra: &RunExtra,
    ) -> Result<EvidenceBundle>;

    fn publish_bundle(&self) -> Option<&'static dyn PublishBundle> { None }
    fn data_write_lock_id(&self) -> Option<&'static str> { None }
}
```

This contract answers four questions before dispatch: which audit is running, which sources it requires, whether it has a publish path, and which writers must share a filesystem lock.

The returned `EvidenceBundle` is deliberately provisional. It records files written, run mode, panel date, and a summary. It does not by itself declare those files publishable. That decision belongs to the publish contract.

The toolkit uses trait objects where implementations differ in behavior. The CLI resolves audit modules and publish bundles at runtime, so `dyn AuditModule` and `dyn PublishBundle` fit those boundaries. Provenance has a different shape: the envelope stays fixed while the response payload changes, so `write_json_with_provenance<T: Serialize>` uses a generic payload. The choice follows the variation in the code—dynamic dispatch for different procedures, generics for one structure over different data types.

The lock hook addresses a concrete overlap. `registry`, `activity`, and `article1` write to the same `data/` directory, so they use the same lock id. Rust cannot prove that separate implementations chose the same string; the code centralizes the id in `REGISTRY_BUNDLE`. This is a convention I would strengthen if the number of shared write paths grows.

---

## Boundary 2 — Publish bundles separate claims from non-claims

A publish bundle is more than a directory copy. It declares the required data and figure files, prepares or generates a manifest, and applies article-specific promotion checks.

The manifest is the claim boundary:

```rust
pub struct AuditManifest {
    pub audit_id: Option<String>,
    pub version: Option<String>,
    pub title: String,
    pub reference_url: String,
    pub frozen_at: String,
    pub panel_date: String,
    pub methods: Vec<AuditMethod>,
    pub claims: Vec<ManifestClaim>,
    pub do_not_claim: Vec<String>,
}
```

Each claim points to an evidence file and carries its display value, source URL, caveat, and status. The exchange manifest also records nearby interpretations that the evidence does not support:

```rust
do_not_claim: vec![
    "Platform transfer ≠ CEX trading volume".into(),
    "Bridged value ≠ transfer volume".into(),
    "Jupiter quote ≠ executed trade or exit capacity".into(),
],
```

This list is not a generic disclaimer. It encodes mistakes that appeared plausible while comparing the Part III surfaces. The analysis tools can calculate cross-surface metrics, but the manifest preserves the non-equivalence.

Promotion leaves the public bundle unchanged until a complete replacement exists. Under an exclusive cross-process lock, it builds a hidden staging tree, materializes the manifest, and validates the required data, figures, and claim evidence paths.

The manifest, sorted data files, and figures are hashed with SHA-256; the first 16 hex characters name the directory under `artifacts/audits/versions/`. If that content-addressed version already exists and validates, promotion reuses it. Otherwise, the new version is installed and the public path `artifacts/audits/{id}` is updated atomically on Unix. A failed promotion removes the staging tree and leaves the previous public bundle untouched. Live exchange evidence and mismatched publish dates are rejected before activation.

The result is narrow but useful: a collector can succeed without silently replacing the published audit state.

---

## Boundary 3 — Sources are adapters, not assumptions

An Ethereum log query, GeckoTerminal pool response, Jupiter quote, and manual RWA.xyz file do not share one economic meaning. The source layer does not try to make them equivalent. It standardizes how they are configured, fetched, cached, and recorded.

`SourceContext` combines a source registry, transport, cache, and typed helpers. `config/sources.yaml` keeps endpoints and rate-limit settings out of collector code. Live collection uses a short cache TTL and bypasses volatile head-dependent RPC calls; force refresh disables the cache.

For exchange evidence, saved API responses carry a provenance envelope:

```json
{
  "provenance": {
    "source": "geckoterminal",
    "fetched_at": "2026-06-12T08:14:03Z",
    "request_url": "https://api.geckoterminal.com/...",
    "response_sha256": "...",
    "live": true
  },
  "data": { }
}
```

Transport errors also preserve distinctions that matter to interpretation. A semantic 4xx from an aggregator can be returned as `ClientError` rather than collapsed into a generic failure. The caller can record "no route returned" without turning it into "no exit exists."

The source contract therefore standardizes mechanics, not meaning. The evidence keeps its original surface; the manifest limits the claim made from it.

---

## End-to-end: `run exchange`

The frozen exchange path shows how the three contracts meet:

```bash
cargo run --bin rwa-audit -- run exchange
```

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-06-23-how-i-built-rwa-audit-in-rust/cli_run_exchange.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-06-23-how-i-built-rwa-audit-in-rust/cli_run_exchange.png"
         alt="Terminal output of rwa-audit run exchange: loading frozen reference data, validating eight claims, and promoting a versioned audit bundle."
         style="max-width:96%; height:auto; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <em><strong>Fig. 2.</strong> The frozen exchange run checks eight manifest targets before activating the public audit path for <code>article3-xstocks-2026-06-12</code>.</em>
  </div>
</div>

`ExchangeModule` selects the manual-import, GeckoTerminal, and Jupiter sources. Frozen mode loads the committed reference files, rebuilds the panel and manifest, and checks the Part III target values. The publish bundle then validates the date, file inventory, and claim evidence paths before installing a version.

The terminal output is useful to the operator. The versioned bundle is the object another reader can inspect.

---

## One design decision I would revisit

The module interface still carries a catch-all:

```rust
pub struct RunExtra {
    pub tx_hashes: Vec<String>,
    pub exchange: ExchangeRunArgs,
    pub promote_bundle: bool,
}
```

This preserves dynamic `AuditModule` dispatch, but every module receives fields it does not use. With seven modules, the unused surface remains visible. At twenty, I would reconsider the dispatch model rather than keep extending `RunExtra`.

---

## Closing

The refactor did not make registry logs, pool snapshots, quotes, and exchange files equivalent. It gave them three shared boundaries: modules declare how evidence is produced, sources retain where it came from, and publish bundles state what can be claimed from it.

That is the useful role Rust played here. It did not verify the underlying RWA. It made the software's evidence and publication rules harder to leave implicit.

The next step is a diff-aware promotion check. Before installing a new version, it should compare claim statuses with the prior manifest and flag changes. That would turn the bundle directory into a timestamped evidence log rather than a sequence of isolated snapshots.

---

## Appendix: codebase and series

**GitHub.** [rwa-audit](https://github.com/egpivo/rwa-audit): the Rust toolkit built across this series.

**Series.**

- [Part I: When Real-World Assets Move On-Chain, What Becomes Visible?]({{ site.baseurl }}/2026/06/07/if-everything-can-be-tokenized-what-should-we-audit.html)
- [Part II: Where RWA Flow Leaves Traces]({{ site.baseurl }}/2026/06/14/where-rwa-trades-and-exits-actually-clear.html)
- [Part III: Where RWA Exchange Risk Actually Sits]({{ site.baseurl }}/2026/06/21/where-rwa-exchange-risk-actually-sits.html)
