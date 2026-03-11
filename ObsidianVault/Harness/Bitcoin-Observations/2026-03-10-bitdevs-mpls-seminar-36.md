# BitDevs MPLS Socratic Seminar 36 — Notes

**Date:** 2026-03-10  
**Source:** [bitdevsmpls.org/2026-03-10-socratic-seminar-36](https://bitdevsmpls.org/2026-03-10-socratic-seminar-36)  
**Theme:** Vibe coding, OpenClaw, agentic payments

---

## What We're Documenting

Structured capture of seminar topics, references, and action items for Bitcoin-Chaos convergence, agent workflows, and future development.

---

## Topics Discussed

### 1. FIPS — Free Internetworking Peering System

- **Link:** [github.com/jmcorgan/fips](https://github.com/jmcorgan/fips)
- **Context:** Distributed mesh routing protocol; Nostr keypairs as node identities; no central authority.
- **Relevance:** Contextualizes *human authority without cryptographic certainty* — contrasts with our desire for cryptographic authority over AI systems. FIPS shows how mesh networks can operate with social/coordination authority when full crypto proof isn't available.
- **Status:** Reference for authority-model discussions.
- **Authority reference:** See [AUTHORITY_MODEL_TAXONOMY.md](../AUTHORITY_MODEL_TAXONOMY.md); FIPS = reference for low-stakes, coordination-heavy designs.

---

### 2. Model Escalation System

- **Idea:** Use the lightest model possible for execution; evaluate completion with a stronger but heavier model.
- **Action:** Document escalation system in workflows (light model → heavy model for verification).
- **Status:** Pending — add to AI_TASK_EVALS or similar.

---

### 3. Agent PR on BitDevs MPLS

- **Future:** Have agent submit a pull request to [bitdevsmpls.org](https://bitdevsmpls.org/2026-03-10-socratic-seminar-36) (source on GitHub).
- **Status:** Future workflow capability.

---

### 4. IronClaw — Privacy/Security-First AI Assistant (Rust)

- **Link:** [github.com/nearai/ironclaw](https://github.com/nearai/ironclaw)
- **Context:** OpenClaw-inspired Rust implementation; WASM sandbox; credential protection; prompt-injection defense.
- **Interest:** Prioritize privacy and security with Rust in future development; IronClaw could function as base.
- **Status:** Research / future dev path.

---

### 5. Bitcoin — No Chargebacks

- **Observation:** No chargebacks risk in Bitcoin; known advantage for agentic payments.
- **Cross-ref:** [CHAOS_BITCOIN_MAPPING.md](../CHAOS_BITCOIN_MAPPING.md) — payment gatekeeper row.

---

### 6. Fedimint CLI / Phoenix Phi

- **Action:** Research Fedimint CLI. Phoenix phi (?) running as daemon — spelling/name unclear; verify.
- **Status:** Research task.

---

### 7. MCP2CLI

- **Action:** Look into MCP2CLI as potential tool/integration.
- **Status:** Research task.

---

### 8. Word Clouds for Skills Audit

- **Idea:** Use word clouds to audit skills (JSON, Markdown) — surface words and their importance for prompt-injection risk.
- **Status:** Potential audit technique for RAG_PROMPT_INJECTION_MITIGATIONS or security-audit-rules skill.

---

### 9. Joseph Voelbel — AI-Built Website in BTC Community

- **Link:** [josephvoelbel.com](https://josephvoelbel.com)
- **Context:** Website made with AI; inside the Bitcoin community.
- **Status:** Reference / case study.

---

## Payment & Agentic Workflows (Explicit Workflow Integration)

### x402 — Payment Required (HTTP 402)

- **Link:** [x402.org](https://www.x402.org/)
- **Context:** Open standard for internet-native payments; natively supports USDC.
- **Audit note:** Seems suspect due to third-party risk. Appears KYC-related; bots cannot provide KYC.
- **Cross-ref:** [CHAOS_BITCOIN_MAPPING.md](../CHAOS_BITCOIN_MAPPING.md) — payment gatekeeper row; [org-intent.bitcoin-inspired.json](../../org-intent-spec/examples/org-intent.bitcoin-inspired.json) — prefer L402/Bitcoin over x402.
- **Status:** Audit; prefer L402 for agentic payments.

---

### L402 — Lightning HTTP 402 Protocol

- **Link:** [docs.lightning.engineering/.../l402](https://docs.lightning.engineering/the-lightning-network/l402)
- **Context:** Stateless verification; Macaroons; Lightning invoices; agentic commerce.
- **Status:** Preferred for agentic payments per org-intent.

---

### unhuman.domains

- **Link:** [unhuman.domains](https://unhuman.domains/)
- **Context:** Domain registrar for AI agents; search, register, manage via API; llms.txt.
- **Status:** Already in harness — [UNHUMAN_DEALS.md](../../.cursor/docs/UNHUMAN_DEALS.md); add unhuman.domains to workflow docs.

---

### Cloaked Wireless

- **Link:** [cloakedwireless.com](https://www.cloakedwireless.com/)
- **Context:** Private and secure wireless; Signal can use this.
- **Status:** Reference for secure messaging stack.

---

## E2EE Messaging — Marmot / White Noise

### NanoClaw — Marmot Channel PR

- **Link:** [github.com/qwibitai/nanoclaw/pull/858](https://github.com/qwibitai/nanoclaw/pull/858)
- **Context:** Marmot protocol support; MLS (RFC 9420) + Nostr; E2EE group messaging; White Noise compatible.
- **Status:** Track for OpenClaw/NanoClaw integration.

---

### White Noise — CLI PR (merged)

- **Link:** [github.com/marmot-protocol/whitenoise-rs/pull/537](https://github.com/marmot-protocol/whitenoise-rs/pull/537)
- **Context:** `wn` CLI and `wnd` daemon; identity, accounts, groups, chats, messages, follows, relays, settings.
- **Status:** Merged; reference for Marmot CLI usage.

---

## LLM Routing — LiteLLM, OpenRouter, Routstr

### LiteLLM

- **Link:** [github.com/BerriAI/litellm](https://github.com/BerriAI/litellm)
- **Context:** Python SDK + proxy; 100+ LLM APIs in OpenAI format; cost tracking, guardrails, load balancing.
- **Integration path:** Way to integrate [OpenRouter](https://openrouter.ai/) or [Routstr](https://routstr.com/).
- **Status:** Research — [OPENROUTER.md](../../.cursor/docs/OPENROUTER.md), [ROUTSTR.md](../../.cursor/docs/ROUTSTR.md).

---

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| Prefer L402 over x402 for agentic payments | x402 USDC path implies third-party/KYC; bots cannot provide KYC; L402 is Lightning-native, stateless |
| Add x402/L402/unhuman.domains to workflows | Explicit workflow integration per user request |
| Document model escalation (light → heavy) | Cost/latency optimization; stronger model for verification only |
| IronClaw as future Rust/privacy path | Aligns with security-first, WASM sandbox, credential protection |

---

## Open Questions

- Fedimint CLI vs Phoenix phi — exact naming and daemon usage?
- MCP2CLI — scope and integration path?
- Word-cloud audit — tooling and integration with skills JSON/MD?

---

## Next Steps

1. Add model-escalation pattern to AI_TASK_EVALS or similar.
2. Add x402/L402/unhuman.domains to workflow docs (AGENT_ENTRY_INDEX or PAYMENT_WORKFLOWS).
3. Research: Fedimint CLI, MCP2CLI, LiteLLM + Routstr/OpenRouter.
4. Future: Agent PR capability for bitdevsmpls.org.
5. Future: IronClaw evaluation for Rust-based privacy-first AI.
