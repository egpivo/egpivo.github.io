---
layout: post
title: "The AI Agent Can Act On-Chain. Who Defines Its Authority?"
date: 2026-07-07
tags: [DeFi, RWA, Governance, AI Agent, Ethereum, Blockchain, Web3]
---

The hard question is not whether an AI agent can write to a chain. It is who defines the scope of that write authority, how contracts enforce it, and who can withdraw it when the agent or policy fails.

By mandate, I mean a specification that a contract can check: which contracts, functions, assets, counterparties, and limits an agent may use, plus who can revoke that permission.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-07-07-the-agent-can-act-who-defines-its-authority/hero.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-07-07-the-agent-can-act-who-defines-its-authority/hero.png"
         alt="Proposed DAO agent authorization architecture"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 1.</strong> Proposed authorization boundary. DAO policy defines scope, limits, and revocation; contracts enforce those constraints on state-changing actions. Issuers, custodians, transfer agents, and legal claims remain outside DAO authority. The diagram describes a target authorization path, not a deployed system found in the protocols reviewed.
  </div>
</div>

This framing matters because many agent discussions stop at capability: can the agent monitor, recommend, prepare a transaction, or execute one? Capability is not authority. Once the agent can submit a state-changing transaction without per-action human approval, the relevant artifact is no longer the prompt or model output. It is the enforceable permission surface around the agent.

DAO governance is one possible way to define that surface. It is not needed for every system. It matters when multiple parties share economic risk and no single operator is supposed to redefine authority unilaterally.

---

## Why Governance Still Matters

DAO speculation faded. The control machinery remained. In the Binance USDT spot cohort used here—UNI, AAVE, and COMP—trading activity peaked in May 2021 and by 2026 had fallen to roughly 5–10% of that level. In the on-chain Governor sample, Aave, Compound, and Uniswap executions rose from 18 in 2021-Q2 to 111 in 2024-Q3, before declining in the later cohort series.

The measurement is narrow. It does not show that DAO governance became healthy, representative, or valuable. It only shows that the token-trading proxy and the execution proxy diverged.

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-07-07-the-agent-can-act-who-defines-its-authority/fig1_dao_hype_governance.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-07-07-the-agent-can-act-who-defines-its-authority/fig1_dao_hype_governance.png"
         alt="Token volume fell while on-chain Governor execution stayed active, 2021–2026"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 2.</strong> Token volume fell while on-chain Governor execution stayed active in the audited window. Panel A indexes average daily Binance USDT spot volume for UNI, AAVE, and COMP to the May 2021 peak; LDO is a supplementary dashed series from its first listed month. Panel B counts verified <code>ProposalExecuted</code> events for Aave, Compound, and Uniswap; ENS and Arbitrum are supplementary overlays. The dashed vertical line marks Q2 2021, when all three fixed-cohort governors were active. The figure compares market-attention and execution proxies only and does not imply governance quality, participation, or economic value. <a href="https://gist.github.com/egpivo/29319ae4bb20a7e7b0178936fced35e8" target="_blank" rel="noopener noreferrer">Reproduction script</a>; Panel A from Binance Vision, Panel B from on-chain RPC.
  </div>
</div>

Uniswap governance executed UNIfication in December 2025, combining a 100 million UNI burn with fee-switch implementation. Sky governance continued voting on RWA vault parameters, including collateral ratios and counterparty authorizations. Those votes changed protocol state or asset exposure.

The market can lose interest in the governance token while the protocol still uses governance to decide who may change parameters, move assets, or trigger upgrades.

What remained beneath the DAO label was not a social slogan. It was a practical access-control stack: delegates, voting power, councils, timelocks, emergency paths, and execution permissions.

Aave proposals pass through timelocks—one day or seven days depending on proposal type. Aave also separates a 4-of-7 Protocol Emergency Guardian from a 5-of-9 Governance Emergency Guardian, with different powers assigned to each. Arbitrum's 12-member Security Council can execute emergency upgrades without a governance vote; a 9-of-12 supermajority can bypass normal voting phases even outside emergencies.

---

## Decision Is Not Execution

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-07-07-the-agent-can-act-who-defines-its-authority/fig2_agent_maturity.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-07-07-the-agent-can-act-who-defines-its-authority/fig2_agent_maturity.png"
         alt="Most agent activity stops before autonomous on-chain execution"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 3.</strong> Illustrative maturity map across four operational levels. The dashed line marks the boundary between human-approval-required work and autonomous on-chain write authority. Placements follow documented cases; NEAR AI delegate work is shown as planned, not verified live execution. Sources: protocol governance documentation; risk-service providers' public materials; NEAR Foundation communications, 2025.
  </div>
</div>

Most visible agent activity still stops before signature authority: monitoring, summaries, risk recommendations, and transaction preparation. Execution begins only when an agent can submit a state-changing transaction without per-action human approval. At that boundary, permission has to become contract-checkable and revocable.

---

## Pieces Without a Mandate

<div style="text-align:center; margin: 2rem 0;">
  <a href="{{ site.baseurl }}/assets/2026-07-07-the-agent-can-act-who-defines-its-authority/fig3_gap_map.png" target="_blank" rel="noopener noreferrer">
    <img src="{{ site.baseurl }}/assets/2026-07-07-the-agent-can-act-who-defines-its-authority/fig3_gap_map.png"
         alt="Authorization primitives exist but governance-ratified mandate layer is missing"
         style="max-width:92%; height:auto; border: 1px solid #ddd; border-radius: 8px;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">
    <strong>Fig. 4.</strong> Identity registries, smart accounts, and scoped permission tools exist as separate building blocks; audit trails and fast revocation are only partially connected. A governance-ratified mandate framework binding these components was not found in the protocols reviewed. The diagram is an evidence synthesis, not a quantitative deployment count.
  </div>
</div>

*Identity.* ERC-8004, a draft ERC proposed in August 2025, defines registries for agent identity, reputation, and validation. It answers "who is this agent"—not what the agent may do.

*Execution and scope.* ERC-4337, EIP-7702, and ERC-7579 provide infrastructure for programmable account execution. Scoped session keys and spending limits are implemented by particular wallets and modules; the standards define the capability, not the mandate.

*Audit, revocation, and legal interface.* Transactions are visible on-chain; decision rationale usually is not. Emergency revocation faster than a governance timelock requires a pre-authorized fast-path multisig—the same design as Aave's Emergency Guardians, applied to agent keys. DeFi governance still lacks a clear process for assigning responsibility when an agent acts on tokenized real-world assets.

What is missing is not another primitive, but a governance process that composes these pieces into one bounded and revocable authorization path. In the major protocols reviewed—Aave, Arbitrum, Sky, and Lido—I did not find a public process that does so.

---

## RWA Exposes the Boundary

Tokenized real-world assets make the permission boundary easier to see. The token is not the whole asset.

The Aave Horizon case makes the limits explicit. Aave DAO governs protocol parameters and risk exposure. Horizon leaves issuer-side access control to the issuers themselves: onboarding, verification, and allowlists are set per issuer rather than by the DAO. An agent authorized to deposit a tokenized Treasury fund as collateral controls the token operation—not the issuer's redemption process, not the T-bill custodian, not the legal documents defining what happens if the issuer cannot honor redemption.

A DAO can govern exposure to a tokenized asset. The underlying custody and redemption process remain outside its contracts.

For agent design, that distinction matters more than the asset label. The contract can reject an out-of-scope deposit; it cannot make an off-chain issuer redeem.

---

## A Minimal Authorization Layer

The proposed layer in Fig. 1 is not a deployed system found in the protocols reviewed. It assembles existing components into a narrow authorization path.

**Explicit scope.** Every agent under a DAO-governed protocol needs a machine-readable permission specification: target contracts, allowed functions, permitted assets, counterparty whitelist, amount limits. The governance system ratifies the policy; a delegated risk council can approve individual low-risk agents within it. A configuration file controlled only by the agent operator is not enough. Governance cannot inspect it reliably, and contracts cannot enforce it.

**Hard limits enforced by contracts.** The enforcement layer should reject anything outside authorized scope, independent of the agent's behavior. If the agent is compromised, the contracts limit how much damage it can cause. Scope-checking and aggregate consumption must update atomically in the same transaction—not in a view-only call that can be satisfied twice before state is written.

The enforcement boundary constrains the actions the policy describes. A capable agent cannot bypass a correctly implemented check, but it may still find a route the permission model failed to cover.

**Fast revocation.** Granting permission can tolerate a governance timelock. Emergency revocation cannot. That requires a pre-authorized fast-path multisig—the same design pattern as Aave's Emergency Guardians, applied to agent keys. Comparable fast-path bodies already exist in Aave and Arbitrum. Their authority can extend beyond a narrow pause-and-revoke role, so the mandate must say exactly what the emergency path can do.

**A public authorization record.** The on-chain record of what each agent may do—under which governance policy and approval path, and with which expiry—is how governance knows which agents hold active permissions at any moment. Agent actions should emit on-chain events. For higher-risk actions, a pre-execution commitment to a decision artifact supports later forensic comparison: it can show a particular artifact existed before execution, not that it was complete or causally responsible for the outcome.

---

## Why Not Just Use a Multisig?

A single-operator system does not need this. A board, multisig, or conventional policy engine performs the same access-control functions faster and with clearer legal accountability.

The DAO case starts when the parties sharing the risk do not all trust the same operator. When Sky's governance votes on RWA vault parameters, the vote matters because one team is not supposed to silently redefine exposure for everyone else. If one operator can expand an agent's scope without recorded approval, the policy is only a label.

The strongest case for DAO-governed permissions is not automation. It is shared capital without a single accepted controller.

---

## What the Record Cannot Prove

The record can prove that an agent held a specific permission at the time it acted; that the action was within or outside that permission; that the authorization followed a recorded governance policy and approval path; and that the action was logged.

Those records do not establish whether the custodian's reserve attestation is accurate, whether the oracle's NAV feed reflects actual underlying value, whether the issuer will honor redemption, or whether the governance policy correctly interprets applicable law.

Suppose an agent is authorized to rebalance a vault within approved assets and limits. If it trades against a manipulated oracle, the authorization record can show that the action was permitted. It cannot establish that the policy or market signal was sound.

The authorization record—governance policy, approval path, on-chain permission specification, agent action log—may become evidence when regulators or courts identify who designed, approved, or operated the agent's authority. The SEC staff's January 28, 2026 statement treats tokenization as a change in representation or recordkeeping, not one that removes the underlying instrument from federal securities-law analysis. Making authorization explicit does not eliminate legal risk. It makes visible what governance contributed and what it did not.

---

## Closing

The contract bounds the agent. The DAO governs the bounds. Neither proves the off-chain asset or the legal claim.

The next useful artifact is concrete: a governance-ratified authorization policy, contract-recorded scopes, emitted action logs, and a revocation path that is faster than the ordinary proposal cycle. Once that exists, the audit question is no longer only "can the agent act?" It is "who approved this scope, what has it consumed, and can it be withdrawn now?"

---

## Appendix

- **Fig. 2:** [reproduction script](https://gist.github.com/egpivo/29319ae4bb20a7e7b0178936fced35e8) — Binance Vision (Panel A), on-chain `ProposalExecuted` via RPC (Panel B, June 2026).
- **Protocols cited:** [Aave governance](https://aave.com/docs/ecosystem/governance); [Aave Horizon](https://aave.com/blog/horizon-launch); [Uniswap UNIfication (93)](https://vote.uniswapfoundation.org/proposals/93); [Arbitrum Security Council](https://docs.arbitrum.foundation/concepts/security-council); [Lido Dual Governance](https://lido.fi/how-lido-works/governance-stack); [Sky governance](https://vote.sky.money/).
- **Standards cited:** [ERC-4337](https://eips.ethereum.org/EIPS/eip-4337); [EIP-7702](https://eips.ethereum.org/EIPS/eip-7702); [ERC-7579](https://eips.ethereum.org/EIPS/eip-7579); [ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) (draft, Aug 2025).
- **SEC statement on tokenized securities:** [January 28, 2026](https://www.sec.gov/newsroom/speeches-statements/corp-fin-statement-tokenized-securities-012826-statement-tokenized-securities).
