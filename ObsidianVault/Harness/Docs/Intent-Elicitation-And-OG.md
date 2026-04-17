---
title: "Intent elicitation, OpenGrimoire, and Obsidian vault"
tags: ["type/harness-doc", "status/mirror", "domain/harness"]
---

# Intent elicitation, OpenGrimoire, and Obsidian vault

**Audience:** Operator + Cursor agents working across **MiscRepos**, **OpenGrimoire**, and an **Obsidian** vault.

**Plan source:** Operator decisions from the Interview + OG + vault integration plan (brainstorming rounds 1–5).

## Goals

- Run a **large initial interview** in **OpenGrimoire** (UI / survey), then **async** prompts and human-gate Q&A in OG—not a “10-minute install fixes everything” workflow.
- Keep **canonical answers in OpenGrimoire**; keep **readable history** in the vault under **`Interview-Archive/`** (outside `Harness/`); keep **git-safe pointers** in MiscRepos handoff and session snapshot fields.
- Avoid **employer-confidential or PII** in **public git** (`handoff_latest.md` is often ignored locally but treat policy as if it could be committed elsewhere—use **pointers only** in durable excerpts).

## Canonical order (first run)

1. Complete the **big interview** in OpenGrimoire.
2. Run the **export bridge** ([`export_opengrimoire_to_vault.py`](../../local-proto/scripts/export_opengrimoire_to_vault.py)) — human-gated or Task Scheduler; writes immutable **`OG-Snapshot-*.md`** and per-id **`REVOKED-*.md`** when applicable.
3. Refresh the **non-sensitive excerpt** file (see [Og intent excerpt](#og-intent-excerpt-stale-cache) below).
4. Update **handoff** / session start with OG **IDs**, **URLs**, **last elicitation** metadata, and clear any **`STALE`** banner when OG is healthy.

## Five elicitation layers (interview content)

Use these headings in OG survey design or in vault `Notes-*.md` overlays:

1. **Operating rhythms** — real daily / weekly / monthly cadence (not only calendar fiction).
2. **Recurring decisions** — easy calls vs hard judgment calls.
3. **Inputs and data sources** — dashboards, sites, metrics you actually use.
4. **Dependencies** — who you need handoffs from and what “done” means per handoff.
5. **Friction points** — recurring annoyances (highest ROI for agents).

**Time budget:** treat **45+ minutes** of focused elicitation as normal for the initial interview, not a failure mode.

**Sync Session + interviewing (full script):** OpenGrimoire [SYNC_SESSION_HANDOFF.md](../../../OpenGrimoire/docs/agent/SYNC_SESSION_HANDOFF.md) — dual-track operator + model elicitation, cadences, paste blocks, harness field mapping, and agent-native notes. This MiscRepos doc stays the **bridge / vault / env** operator contract.

## Markdown “OS” vs MiscRepos harness

Video / community framing (`soul.md`, `identity.md`, etc.) maps to this repo without renaming files:

| Concept | MiscRepos / harness analogue |
|--------|------------------------------|
| `soul.md` | Mission + boundaries: `org-intent-spec` JSON, `.cursorrules`, `decision-log.md` patterns |
| `identity.md` | Voice / persona: `docs/collaborators/*`, `AGENTS.md` operating style |
| `user.md` | `.cursor/state/preferences` (or JSON), `session_brief.md` |
| `heartbeat.md` | `pending_tasks.md`, [SCHEDULED_TASKS.md](../../local-proto/docs/SCHEDULED_TASKS.md), governance ritual |
| `memory.md` | `AGENTS.md` learned facts, `decision-log.md`, vault `.cursor_context` (when used) |

## Storage contract

| Store | Holds | SSOT? |
|-------|--------|--------|
| **OpenGrimoire** | All interview + async answers | **Yes** (canonical) |
| **Vault `Interview-Archive/`** | `OG-Snapshot-*.md` (immutable exports), `REVOKED-*.md`, optional human `Notes-*.md` | Human-readable **copy** + overlays |
| **MiscRepos git** | Protocols, contracts, scripts; **non-sensitive** pointers in templates | **No** for full narrative |
| **`Harness/`** in vault | Mirror from [sync_harness_to_vault.ps1](../../local-proto/scripts/sync_harness_to_vault.ps1) | **Mirror only** — see [HARNESS_VAULT_WRITE_CONTRACT.md](../../local-proto/docs/HARNESS_VAULT_WRITE_CONTRACT.md) |

### Vault file naming

- **`OG-Snapshot-<UTC>-<responseOrSessionId>.md`** — one new file per successful export; **never overwrite** prior snapshots.
- **`REVOKED-<responseId>.md`** — one tombstone per revoked id when OG (or manual list) reports revocation.
- **`Notes-*.md`** — your wikilinks and clarifications; **Obsidian / sync tool wins** on multi-device conflicts.

### Multi-machine

- **One machine** runs the bridge; vault is **cloud-synced** so other devices read `Interview-Archive/`.
- Do not run two bridge writers into the same folder without coordination.

## OG intent excerpt (stale cache)

**Path (local, gitignored):** `.cursor/state/og_intent_excerpt.md`

**Purpose:** Small **non-sensitive** summary for Cursor when OG is down or to avoid loading the vault. Must include a **`STALE`** / `OG_UNAVAILABLE` banner when the last health check failed.

**Refresh rule:** On **intent-related handoff**, agents should **ping OG** (e.g. `GET /api/capabilities`) and refresh this excerpt when healthy. The [export bridge](#export-bridge) updates timestamps when run successfully.

## Environment variables

Documented in [ENV_STANDARD.md](../../local-proto/docs/ENV_STANDARD.md) — see **OpenGrimoire (operator sync)** row.

| Variable | Purpose |
|----------|---------|
| `OPENGRIMOIRE_BASE_URL` | Primary OG origin (no trailing slash preferred). |
| `OPENGRIMOIRE_FALLBACK_URL` | Optional second origin if primary fails (same token assumptions). |
| `OPENGRIMOIRE_API_TOKEN` | Bearer or survey token as required by your OG deployment (never commit). |
| `OBSIDIAN_VAULT_ROOT` | Vault root; bridge writes `Interview-Archive/` under it. |
| `OPENGRIMOIRE_EXPORT_JSON` | Optional path to operator-supplied JSON dump for offline snapshot generation until OG exposes a full export API. |
| `OPENGRIMOIRE_REVOKED_IDS` | Optional comma-separated revoked response ids for tombstones. |
| `OPENGRIMOIRE_REVOKED_MANUAL_FILE` | Optional path to newline-separated revoked ids (defaults next to excerpt; see script `--help`). |

## Export bridge

**Script:** [`local-proto/scripts/export_opengrimoire_to_vault.py`](../../local-proto/scripts/export_opengrimoire_to_vault.py) — if the file is missing from your clone, copy from [EXPORT_BRIDGE_IMPLEMENTATION.md](./EXPORT_BRIDGE_IMPLEMENTATION.md) (embedded source).

- **Human gate:** agents run it only after **explicit operator approval** for the session when using production tokens.
- **Backoff:** exponential backoff on HTTP failures; non-zero exit on final failure (Task Scheduler visibility).
- **Revocations:** design target is OG **`GET` list of revoked ids** (Phase 2 in OpenGrimoire). Until then: env or manual file.

## OpenGrimoire Phase 2 (API)

Contract sketch and backlog: [OpenGrimoire docs/agent/ELICITATION_EXPORT_CONTRACT.md](../../../OpenGrimoire/docs/agent/ELICITATION_EXPORT_CONTRACT.md) (sibling clone).

## Related

- [FIRST_RUN_INTENT_CHECKLIST.md](./FIRST_RUN_INTENT_CHECKLIST.md)
- [SESSION_SNAPSHOT_TEMPLATE.md](./SESSION_SNAPSHOT_TEMPLATE.md)
- [SESSION_MESSAGE_TEMPLATE.md](../../.cursor/docs/SESSION_MESSAGE_TEMPLATE.md)
- [OBSIDIAN_VAULT_INTEGRATION.md](../../.cursor/docs/OBSIDIAN_VAULT_INTEGRATION.md)
- [SYNC_SESSION_HANDOFF.md](../../../OpenGrimoire/docs/agent/SYNC_SESSION_HANDOFF.md)
