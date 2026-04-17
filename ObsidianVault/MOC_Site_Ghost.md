---
title: MOC — Site (self-hosted Ghost)
tags:
  - pocket/publishing
  - type/moc
---

# MOC — Site (self-hosted Ghost)

**Recorded in MiscRepos:** `.cursor/state/decision-log.md` (2026-04-17) — Ghost = **self-hosted**; PKM = **Obsidian** for now.

## Harness mirror (run `sync_harness_to_vault.ps1` so these stay current)

- [[GHOST1-Runbook]] — Docker/VM, HTTPS, transactional mail, scoped integration, §Verification.
- [[GHOST1-Closeout]] — After verification: mark **GHOST1** `done` in `software/.cursor/state/pending_tasks.md`.
- [[Joseph-Voelbel-OpenClaw-Clawhub]] — ClawHub links; OpenClaw credential path for `ghost-admin.json` (not git).
- [[Cursor-OpenClaw-Integration]] — Mode B sidecar vs thin Cursor skills.

## Operator order (short)

1. Stand up Ghost + **HTTPS** + **SMTP** (invites / password reset).
2. Ghost Admin → **Integrations** → custom integration, **minimal** scopes; store secrets outside git.
3. Complete runbook **§Verification**, then follow **[[GHOST1-Closeout]]**.

PKM stays **Obsidian**; this note is only for **site** discoverability.
