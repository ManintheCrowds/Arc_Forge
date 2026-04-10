---
title: "Gemma 4, TurboQuant, OpenClaw field run, Karpathy LLM Wiki — archive & stack brainstorm"
tags: ["type/research", "status/draft", "domain/ai", "domain/openclaw", "domain/local-llm"]
date: 2026-04-10
---

# Gemma 4, TurboQuant, OpenClaw field run, Karpathy LLM Wiki — archive & stack brainstorm

Vault archive of four primary sources (two YouTube transcripts summarized from public metadata, one Google Research blog, Unsloth Gemma 4 docs). **Purpose:** compound knowledge for **local AI**, **OpenClaw**, and **Obsidian**-aligned workflows — not a vendor runbook.

---

## Sources

| Source | URL |
|--------|-----|
| Video — *I Sent an AI Spy Into a Social Network for Robots \| OpenClaw* (gptars) | https://youtu.be/xj27uGjAKwA |
| Video — *Karpathy's LLM Wiki: What It Means & How to Build One* (Onchain AI Garage) | https://youtu.be/zVEb19AwkqM |
| Article — *TurboQuant: Redefining AI efficiency with extreme compression* (Google Research) | https://research.google/blog/turboquant-redefining-ai-efficiency-with-extreme-compression/ |
| Docs — *Gemma 4 — How to Run Locally* (Unsloth) | https://unsloth.ai/docs/models/gemma-4 |

**Related (not primary):** [Gemma 4 — Google blog](https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/) · [TurboQuant paper arXiv:2504.19874](https://arxiv.org/abs/2504.19874) · community [turboquant-kv](https://github.com/hackimov/turboquant-kv) (PyTorch KV quantization; verify before production).

---

## 1. Video A — OpenClaw “spy” on Moltbook (transcript themes)

**Setup:** OpenClaw agent (“Larry”) on a **~$55 Raspberry Pi**, deployed to **Moltbook** (AI-only social network; creator describes ~millions of agents). **14 days**, **~35,000 words** of field reports, **cover identity** + **mission** + **SOUL**-style document. Periodic prompts to resume the spy role.

**Themes useful for our stack:**

- **Long-horizon agents** need explicit **cadence** (heartbeat, scheduled re-grounding) so mission drift does not become silent failure.
- **Volume of artifacts** (35k words) argues for **structured logging** → vault / effectiveness logs / handoff files — not raw chat only.
- **Handler not always listening** mirrors real OpenClaw ops: design for **async summaries** and **durable queue** of “reports” even when human is offline.
- **Karpathy-adjacent quote** (sci-fi / “dumpster fire”): excitement + chaos → **blast radius**, separate chat/profile for experiments, governance (aligns with local-proto OpenClaw runbooks).
- **Edge deployment** proves OpenClaw-class stacks can run **low-power**; pair with **small local models** for offline summarization when cloud is undesirable.

---

## 2. Video B — Karpathy “LLM Wiki” (transcript themes)

**Core idea:** Move from **one-shot RAG** (retrieve chunks per question, no memory) to an **LLM-maintained, persistent, interlinked wiki** so knowledge **compounds** across sessions.

**Architecture (as presented):**

- **Layer 1 — Raw sources:** originals (papers, repos, notes).
- **Layer 2 — Wiki:** markdown-style pages, cross-links, incremental updates by the LM.
- **Layer 3 — Schema / structure:** categories, indices, lint rules so the wiki stays navigable.

**Operations:** **Ingest** (add/update pages from sources), **Query** (read/navigate), **Lint** (consistency, broken links, duplication).

**Why it matters here:**

- **Obsidian** is a natural **Layer 2** surface; harness sync and `Harness/` already mirror repo state — extend with **wiki-first** conventions (MOCs, evergreen notes) for research like this file.
- **OpenClaw** can run **ingest/lint** jobs on a schedule (Task Scheduler / cron) with **human approval** on destructive merges — matches [[AGENT_NATIVE_PARITY_CHECKLIST]] style parity (agent does the loop; human approves gates).

---

## 3. TurboQuant (Google Research blog digest)

**Problem:** High-dimensional vectors and **KV cache** dominate memory; classical VQ often adds **per-block overhead** (extra bits), partly negating savings.

**Method:**

1. **PolarQuant:** Random rotation → simpler geometry → strong per-coordinate quantization; polar-style parameterization to reduce **normalization overhead**.
2. **QJL (Quantized Johnson–Lindenstrauss):** ~**1 bit** on residual error; **low overhead** attention scoring.

**Claims (benchmark framing):** Strong **long-context** results (LongBench, needle-in-haystack, etc.); **~6× KV memory reduction** in discussed settings; **up to ~8×** speedup on **attention logits** vs described JAX baseline on **H100** at some bitwidths; **3-bit KV** without training/fine-tuning in reported Gemma/Mistral experiments. Also positioned for **vector search** (recall vs PQ-style baselines).

**Stack implications:**

- **Local inference:** Watch **llama.cpp / vLLM / Ollama** release notes for **KV cache quantization** paths (community ports exist; validate quality on **your** models before defaults).
- **OpenClaw + long context:** If gateway uses long histories or big tool transcripts, **KV compression** is directly tied to **cost and tail latency** — track TurboQuant-class options when backends support them.
- **Semantic search / RAG:** Same math applies to **embedding index** size and build time; useful when we scale **vault RAG** or local vector stores.

---

## 4. Gemma 4 — Unsloth local run (digest)

**Family:** E2B, E4B, **26B-A4B** (MoE), **31B** (dense); **Apache-2.0**; up to **256K** context (128K on smaller variants per doc).

**Fit:**

- **E2B/E4B:** Multimodal (**image + audio** on small variants); **edge / laptop** RAM bands (see Unsloth tables).
- **26B-A4B:** **4B active** MoE — good **speed/quality** tradeoff for desktop GPUs.
- **31B:** Strongest quality, heavier VRAM.

**Operational sharp edges (must not ignore):**

- **Do not use CUDA 13.2 runtime** with Gemma 4 GGUFs — **poor outputs** (Unsloth warning).
- **Default sampling:** `temperature=1.0`, `top_p=0.95`, `top_k=64`; start **~32K context** locally then raise.
- **Thinking mode:** `<|think|>` at start of **system** prompt; use `--chat-template-kwargs '{"enable_thinking":false}'` on **llama-server** when reasoning channel should be off; **strip thought blocks** from **multi-turn history** (only ship final visible answer forward).
- **EOS:** `<turn|>` (Unsloth).
- **Multimodal ordering:** **Image/audio before text**; OCR/doc use high visual token budget (**560** or **1120**); audio **≤30s**; video **≤60s** at ~1 fps — design OpenClaw tools to respect these limits when wrapping Gemma 4.

---

## Brainstorm — concrete improvements (local AI + OpenClaw)

| Area | Idea |
|------|------|
| **Model lineup** | Add **Gemma 4 E4B / 26B-A4B** to the local roster for **tool-heavy** and **long-context** experiments; pin **CUDA** stack to avoid **13.2** for GGUF runs. |
| **Chat templates** | Centralize **thinking on/off** and **history stripping** in any gateway that talks to Gemma 4 / llama-server (same pattern as Unsloth warns). |
| **KV / RAM** | Track **TurboQuant** and **turboquant-kv**-class integrations; benchmark **context length** vs VRAM before promising “256K local.” |
| **Obsidian** | Treat vault as **LLM wiki layer:** ingest scripts that create/update **research/** notes with **sources table + dated filenames** (this file); add **lint** (link check, duplicate titles) in CI or weekly agent job. |
| **OpenClaw** | From Video A: **heartbeat + mission re-grounding** in SOUL/HEARTBEAT; **durable field reports** even when handler is away; **separate experimental profile** to limit Moltbook-style blast radius. |
| **Knowledge** | From Video B: prefer **incremental wiki updates** over **only** ad-hoc RAG for recurring domains (trading, infra, OpenClaw effectiveness). |
| **Docs** | Keep **Unsloth Gemma 4** + **TurboQuant** pointers here; link outward papers for deep dives. |

---

## Cross-links

- Harness / OpenClaw docs in repo: `OPENCLAW_READINESS.md`, `OPENCLAW_STACK_RECOMMENDATIONS.md`, `OPENCLAW_PRACTICE_RUNBOOK.md` (MiscRepos `local-proto/docs/`).
- Vault integration overview: MiscRepos `.cursor/docs/OBSIDIAN_VAULT_INTEGRATION.md`.

---

*Archived 2026-04-10. Transcript content for YouTube items summarized from public video metadata and search snippets — no video files downloaded.*
