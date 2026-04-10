---
title: "Chaos-to-Bitcoin Mapping"
tags: ["type/harness-doc", "status/mirror", "domain/harness"]
---

# Chaos-to-Bitcoin Mapping

Side-by-side analysis of Agents of Chaos failures, Bitcoin design patterns, agent mitigations, and Fedimint/ACE/PentAGI implementation.

**Source:** [Agents of Chaos](https://arxiv.org/abs/2602.20021) — red-teaming study of autonomous AI agents (Northeastern, MIT, Harvard, Bau Lab). [Project site](https://agentsofchaos.baulab.info/).

**See also:** [bitcoin_chaos_convergence plan](D:\software\plans\bitcoin_chaos_convergence_a219e7b9.plan.md), [PENTAGI_FEDIMINT_ACE_ROADMAP.md](D:\portfolio-harness\docs\PENTAGI_FEDIMINT_ACE_ROADMAP.md), [AUTHORITY_MODEL_TAXONOMY.md](AUTHORITY_MODEL_TAXONOMY.md), [2026-03-10-bitdevs-mpls-seminar-36.md](bitcoin_observations/2026-03-10-bitdevs-mpls-seminar-36.md).

---

| Chaos Failure                             | Bitcoin Solution                                        | Agent Mitigation                                       | Fedimint/ACE/PentAGI Implementation                                        |
| ----------------------------------------- | ------------------------------------------------------- | ------------------------------------------------------ | -------------------------------------------------------------------------- |
| Authority conversational (CS2, CS8, CS11) | Private key = proof of ownership; no display names      | Cryptographic owner binding; signed identity           | Fedimint AuthModule capability tokens; agent identity = Fedimint pubkey    |
| Reframing bypasses semantic guards (CS3)  | Protocol is deterministic; wording irrelevant           | Intent checksum; action-level verification             | Action-level verification; capability scope enforced by consensus          |
| Indirect injection via URLs (CS10)        | Don't trust external sources; verify on-chain           | Document provenance; no trust for user-controlled URLs  | Document provenance; no trust for user-controlled URLs; LogEvent for audit  |
| Multi-agent amplification (CS10, CS11)    | Each node validates independently; no blind propagation | Owner-only channels; explicit opt-in for non-owners    | Fedimint BFT; each guardian validates; no blind propagation               |
| Provider values invisible (CS6)           | Open protocol; no silent truncation                     | Local models or transparent provider; audit            | Federation constitution (org-intent) anchored on Fedimint/Bitcoin           |
| Values conflict without resolution (CS1)  | Longest chain wins; clear rules                         | Escalate to human; no unilateral resolution            | ACE Aspirational layer; escalate to human; no unilateral resolution        |
| Infinite loops (CS4, CS5)                 | Fee market; block size limits                           | Resource caps; termination conditions                  | Resource caps; termination conditions; reputation tier gating              |
| Payment gatekeeper lock-in (ACP, x402, AP2) | Bitcoin: no KYC; no single trusted party; no chargebacks; open rails | Prefer open payment methods; Moneydevkit, L402 | Fedimint as payment rail; AuthModule capability tokens for agent spend |
| Authority model (FIPS contrast) | Private key = proof | Nostr identity + social routing; coordination without crypto proof | Cryptographic owner binding for spend/PII; human gates for low-stakes coordination per [AUTHORITY_MODEL_TAXONOMY](AUTHORITY_MODEL_TAXONOMY.md) |
