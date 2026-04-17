---
title: "Joseph Voelbel — OpenClaw stack, ClawHub skills, collaboration primer"
tags: ["type/harness-doc", "status/mirror", "domain/harness"]
---

# Joseph Voelbel — OpenClaw stack, ClawHub skills, collaboration primer

**Purpose:** Single place to learn what Voelbel is shipping in the agent/Ghost space, how it maps to **highnoonoffice** on ClawHub, and how to fold it into **your** knowledge bases (Obsidian/Foam, Cursor skills, OpenClaw vault) without surprise risk.

**Meat-space collaboration:** Treat this as *intel*, not endorsement. Review skill source before installing; use dedicated Ghost integration keys and least-privilege bots (see SCP + ClawHub assessments below).

---

## Who / narrative

| Axis | Detail |
|------|--------|
| **Identity** | Joseph Voelbel — writer, “AI Learning Experience Designer,” Bitcoin-facing author (*Pay Attention to Bitcoin*, *Nineteen Stories*). |
| **Public site** | [josephvoelbel.com](https://josephvoelbel.com) — Ghost, minimal URL-first design. |
| **Agent persona** | “Magnus” — his OpenClaw instance; co-authored workflows and memory layout described in long-form posts. |
| **Org (code + skills)** | [github.com/highnoonoffice](https://github.com/highnoonoffice) — `hno-skills`, `ghost-theme`, `library-of-babel`, etc. |

**Essays to read first (primary citations):**

- [The Brain Map Visualizer](https://josephvoelbel.com/the-brain-map-visualizer/) — motivation, graph semantics, link to ClawHub + GitHub.
- [Installing OpenClaw: Meet Magnus](https://josephvoelbel.com/installing-openclaw-meet-magnus/) — setup pain, SOUL/MEMORY/USER files, Ghost migration Squarespace → Ghost, first-week build list (Ghost API, Kanban pipeline, Telegram, Protonmail ingest).

**Secondary:**

- [Once Bitten #523 — Pay Attention To Bitcoin](https://anchor.fm/daniel-prince6/episodes/Pay-Attention-To-Bitcoin--JosephVoelbel-523-e2udjjn) (podcast).
- Internal seminar cross-ref: [BitDevs MPLS 36 §9](../bitcoin_observations/2026-03-10-bitdevs-mpls-seminar-36.md) (short case study link).

---

## ClawHub skills (@highnoonoffice) — catalog

Canonical listing pages (same skills; `clawhub.ai` is the current UI path you shared):

| Skill | URL | Version (as captured) | One-line role |
|-------|-----|----------------------|---------------|
| **Ghost Publishing Pro** | [clawhub.ai/.../ghost-publishing-pro](https://clawhub.ai/highnoonoffice/ghost-publishing-pro) | v1.7.7 | Headless Ghost Admin API — write, audit, batch, migrations, newsletters, images (~16 workflows). |
| **Brain Map Visualizer** | [clawhub.ai/.../brain-map-visualizer](https://clawhub.ai/highnoonoffice/brain-map-visualizer) | v3.2.1 | Force-directed graph from vault Markdown + session journals → local JSON + D3/React. |
| **Library of Babel** | [clawhub.ai/.../library-of-babel](https://clawhub.ai/highnoonoffice/library-of-babel) | v0.1.1 | Borges-style deterministic page/address engine (+ demos). |
| **Second Brain Visualizer** | [clawhub.ai/.../second-brain-visualizer](https://clawhub.ai/highnoonoffice/second-brain-visualizer) | v1.5.0 | Markdown “ledger” → optional Slack/Telegram ingest → **local OpenClaw gateway** LLM → clustering → frontend. |

**Legacy / alternate hub URL (still cited in his article):** [clawhub.com/skills/oc-brain-map](https://clawhub.com/skills/oc-brain-map) — same **Brain Map Visualizer** lineage (slug evolved).

---

## ClawHub platform security scans (summarized)

These are **ClawHub’s** automated assessments, not a substitute for reading `SKILL.md` and scripts in the zip.

| Skill | VirusTotal | OpenClaw scan | Capability / notes |
|-------|------------|---------------|---------------------|
| Ghost Publishing Pro | Benign | Benign | **OAuth / posts externally** — needs Ghost Admin integration JSON under `~/.openclaw/credentials/ghost-admin.json`; rate-limit and key hygiene critical. |
| Brain Map Visualizer | Benign | Benign | **“Can make purchases”** label on hub (capability signal); locally reads vault/journals, writes graph JSON; do not expose graph API publicly without intent. Hub notes a **parser regex bug** (`pattern.run`) — fix before trusting automation. |
| Library of Babel | Benign | **Suspicious** | Flagged for **doc/code mismatch** (claims “no storage / no randomness” vs `codex.json` + PRNG in demos). Likely benign for math demo; **human review** before install. |
| Second Brain Visualizer | Benign | Benign | Optional **Slack/Telegram** read; **gateway host** must stay localhost or corpus leaves machine; install.md vs `cluster.js` credential path — **trust the code**, align config. |

---

## Secure Contain Protect (SCP) — what we ran

**Method:** Aggregated neutral summaries of the four skills (versions, capabilities, credential paths) and the bare `clawhub.ai/...` URLs; ran `scp.scp_utils.inspect(..., context="tool_output")` and `run_pipeline(..., sink="llm_context")` from `E:\local-proto\workspace` (Python `scp` package).

**Results:**

- **Inspect:** `tier: clean`, `risk_score: 0.0`, no override/power-word/encoding-block findings on both the summary blob and the URL-only blob.
- **Pipeline:** `blocked: false`; contained output with markdown fence for LLM-safe replay.

**Interpretation (SCP skill alignment):**

- Third-party **marketplace descriptions** did not trip text-tier injection/reversal heuristics.
- **Operational risk** still lives in *behavior*: Ghost API keys, Telegram/Slack tokens, gateway URLs, and running unaudited scripts — that is **credential + provenance** hygiene ([secure-contain-protect SKILL](../../.cursor/skills/secure-contain-protect/SKILL.md) § mask secrets, DMZ, human review), not something `scp_inspect` replaces.
- **Library of Babel:** treat ClawHub “suspicious” as **provenance / honesty-of-docs** signal → review before merge into any automated agent loop.

---

## Integration playbook (your knowledge bases)

**Expanded in-repo:** [CURSOR_OPENCLAW_INTEGRATION.md](CURSOR_OPENCLAW_INTEGRATION.md) (Cursor vs OpenClaw default **sidecar**), [PKM_ATTENTION_POCKETS_AND_BRAIN_MAP.md](../PKM_ATTENTION_POCKETS_AND_BRAIN_MAP.md) (attention pockets + optional graph JSON snapshot), [GHOST1_RUNBOOK.md](../GHOST1_RUNBOOK.md) (Ghost stand-up), [vault-templates/README.md](../vault-templates/README.md) (copy-paste MOC notes for Obsidian/Foam). **Operator phased checklist:** [INTEGRATION_ROLLOUT_OPERATOR_CHECKLIST.md](../operations/INTEGRATION_ROLLOUT_OPERATOR_CHECKLIST.md).

### 1. Obsidian / Foam (human PKM)

- Link this file from your people or Bitcoin research MOC (see [bitcoin_observations/README.md](../bitcoin_observations/README.md) **Research MOC** and [vault-templates/MOC_Bitcoin_Agents.md](../vault-templates/MOC_Bitcoin_Agents.md)).
- If you adopt **Brain Map** ideas without OpenClaw: replicate the *concept* (co-access graph, MOCs by “attention pocket”) with Dataview, Juggl, or Foam graph — no install required.
- If you use **Second Brain** patterns: keep a single **ledger** markdown convention and avoid sending vault text to a **remote** LLM gateway.

### 2. Cursor (`.cursor/skills`)

- Voelbel’s artifacts are **OpenClaw / ClawHub** bundles, not Cursor `SKILL.md` drop-ins. To “integrate,” either:
  - **Port patterns** (Ghost Admin JWT flow, journal parse → JSON graph) into your own repo-native skills, or
  - Run **OpenClaw** beside Cursor and treat ClawHub skills as **that** runtime’s extensions.
- Before porting **Ghost Publishing Pro**, run **security-audit-rules** on any copied instruction file (prompt-injection surface in long `SKILL.md`). Checklist: [.cursor/skills/security-audit-rules/SKILL.md](../../.cursor/skills/security-audit-rules/SKILL.md).

### 3. OpenClaw vault (if you run it)

- Install order suggestion: **Brain Map** (read-only-ish) → **Ghost Publishing Pro** (after integration key scoped in Ghost) → **Second Brain** (only with localhost gateway + scoped bots) → **Library of Babel** last, after manual code read. (Same sequence in [CURSOR_OPENCLAW_INTEGRATION.md](CURSOR_OPENCLAW_INTEGRATION.md).)
- Mirror Voelbel’s split: **Memory layers** (searchable file list) vs **Brain Map** (high-level topology) — described in his Brain Map article.

### 4. Ghost site (aligned with your pending task GHOST1)

- Reference theme: [highnoonoffice/ghost-theme](https://github.com/highnoonoffice/ghost-theme).
- Publishing automation: **Ghost Publishing Pro** on ClawHub + his essay on Magnus migrating 200+ posts. Step-by-step: [GHOST1_RUNBOOK.md](../GHOST1_RUNBOOK.md).

---

## Link roll (copy-friendly)

**Person & writing**

- https://josephvoelbel.com/
- https://josephvoelbel.com/the-brain-map-visualizer/
- https://josephvoelbel.com/installing-openclaw-meet-magnus/
- https://twitter.com/josephvoelbel

**GitHub org**

- https://github.com/highnoonoffice
- https://github.com/highnoonoffice/hno-skills
- https://github.com/highnoonoffice/ghost-theme

**ClawHub (skills you asked about)**

- https://clawhub.ai/highnoonoffice/ghost-publishing-pro
- https://clawhub.ai/highnoonoffice/brain-map-visualizer
- https://clawhub.ai/highnoonoffice/library-of-babel
- https://clawhub.ai/highnoonoffice/second-brain-visualizer

**Hub / ecosystem**

- https://clawhub.com/skills/oc-brain-map (legacy slug for brain map)

---

## Changelog

| Date | Change |
|------|--------|
| 2026-04-14 | Initial doc: ClawHub quartet, SCP inspect+pipeline on aggregates, integration hooks, full link roll. |
