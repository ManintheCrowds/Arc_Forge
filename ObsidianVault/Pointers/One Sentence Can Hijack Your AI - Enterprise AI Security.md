---
title: "One Sentence Can Hijack Your AI - Enterprise AI Security"
tags: ["type/ingest-pointer", "status/draft", "domain/scp"]
---

# One Sentence Can Hijack Your AI - Enterprise AI Security

#ai-security #prompt-injection #enterprise #harness #zero-trust #dmz #compartmentalization #observability

# One Sentence Can Hijack Your AI: Enterprise AI Security

**Source:** [AI++ YouTube](https://www.youtube.com/watch?v=8PIwEkKenQU) · Anatoli (Rishon founder) · ~20 min

## Summary

Enterprise AI security centers on the **harness**—the software that wraps the LLM, invokes tools, and connects to databases, email, and APIs. The LLM itself is mostly harmless (text in, text out); risk lives in what it can do through tools. IBM: 86% of orgs lack visibility into AI data flows; 97% lack proper AI access controls.

---

## Where Risk Lives

| Component | Risk level |
|-----------|------------|
| Pure LLM (API only) | Low — no hands, no direct world access |
| Harness (tools, DB, email, APIs) | **High** — nearly all risk |
| Third-party hosted LLM | Trust boundary — you rely on vendor security |
| Built-in tools (e.g. search) | **High** — exfiltration and hijacking vectors |

**Search tool risk:** Malicious pages can hide instructions (e.g. "append transcript to URL"); the LLM fetches pages and leaks data. Prompt injection and search leaks are **unsolved at model level**—you must handle them in your architecture.

---

## Top Three Attack Vectors

1. **Direct prompt injection** — Crafted inputs override system instructions (forged orders to a field agent).
2. **Indirect prompt injection** — Malicious instructions in documents, emails, or web pages the AI consumes (KGB "active measures").
3. **Agent-to-agent propagation** — One compromised agent infects others in a trust chain (Cambridge 5 analogy).

**Constraint gap:** Prompts often omit constraints; AI follows programming to a logical extreme (I, Robot / Asimov). Autonomous agents have no human to press stop.

---

## Six Defensive Techniques

### Architectural (3)

1. **Compartmentalization** — Manhattan Project model: narrow goals, minimal tools, controlled data, no cross-agent visibility. Many small agents instead of long-running sessions.
2. **Source verification** — Multi-agent validation: query multiple models on same input; agreement = confidence, divergence = investigate. Inspect inputs (prompt injection) and outputs (hallucinations).
3. **DMZ architecture** — For customer-facing chatbots: isolated zone between internet and internal systems. Outer firewall sanitizes input; inner firewall restricts to read-only API calls. Attacker trapped in DMZ even if LLM is compromised.

### Operational (3)

4. **Human-in-the-loop** — Irreversible/high-impact actions require approval. Safeguards in **harness code**, not LLM prompts. Approval checkpoints are a feature, not a bottleneck.
5. **Observability** — Log every input, output, tool call, reasoning trace. Searchable, auditable, alertable. Without it, incidents are black boxes.
6. **Anomaly detection** — Baselines for normal behavior (tool calls per session, endpoints, sequence). Deviations → flag, throttle, kill session. Like fraud detection for AI.

---

## Key Theorems & Facts

- **Karpowitch impossibility (2025):** An LLM cannot be both fully truthful and fully resistant to manipulation. Architectural fixes required, not behavioral.
- **Lethal trifecta (Simon Willis):** Tools + untrusted input + sensitive access.
- **Claude Sonnet 4.6:** One-shot attack success 50% → 8% with safeguards; risk remains.

---

## Related

- [[Secure Contain Protect]] — SCP pipeline for external content before LLM/handoff
- [[Zero Trust]] — Treat every component as already compromised
- [[Prompt Injection]] — Direct and indirect attack patterns