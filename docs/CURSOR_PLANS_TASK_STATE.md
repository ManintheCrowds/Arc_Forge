# `.cursor/plans` — task state vs chat transcript

**Owning repo:** Arc_Forge (workspace-level); same convention applies in other roots that use Cursor Plans.  
**Purpose:** Phase **P4.2** — clarify what belongs under **`.cursor/plans/`** so agents and humans do not confuse **approved task specs** with **conversation logs**.

## Task state (plans)

Files under **`.cursor/plans/*.plan.md`** are **planning artifacts**: scoped work, acceptance hints, links to issues/PRs. They are **context for execution**, not a substitute for GitHub issues or ADRs.

- Treat them as **durable task memory** for a feature or phase.
- Prefer **one plan per initiative** or a small numbered series; avoid duplicating full chat transcripts.

## Conversation state (not plans)

Chat history, agent transcripts, and exploratory Q&A belong in **session tools**, **issue comments**, or **private scratch** — not as the authoritative plan file. If a plan file grows into a transcript, **split** the narrative out or archive it.

## Handoff docs (OpenHarness / MiscRepos)

For operator and harness handoff conventions (separate from Cursor UI), see sibling repos, e.g. OpenHarness `docs/` and MiscRepos `.cursor/scripts` / handoff prompts — cross-link from your runbook when this workspace includes those clones.

## Related

- Idempotency and agent retries (OpenGrimoire): [`../../OpenGrimoire/docs/agent/ADR_IDEMPOTENCY_AND_RETRY.md`](../../OpenGrimoire/docs/agent/ADR_IDEMPOTENCY_AND_RETRY.md)
- Plans that change **OpenGrimoire** code or contracts: run **`npm run verify`** from the **OpenGrimoire** sibling clone (see [Arc_Forge README](../README.md) — *Agent harness (Cursor workspace)* / *OpenGrimoire + harness verify*).
