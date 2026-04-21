---
title: "Integration rollout — operator checklist"
tags: ["type/harness-doc", "status/mirror", "domain/harness"]
group: harness-docs
color: blue
cssclasses:
  - vault-grp-harness-docs
  - vault-col-blue
---

# Integration rollout — operator checklist

Executable checklist for the **Integration action rollout** plan (`integration_action_rollout_0da4cc44` in workspace `.cursor/plans/`). **Human / infra work** with pointers to repo SSOT.

## Phase 1 — Ghost (GHOST1)

Use [GHOST1_RUNBOOK.md](../GHOST1_RUNBOOK.md) as the canonical procedure.

- [ ] **§1 Provision** — Docker, bare metal, or managed; canonical URL; mail; TLS; first admin user.
- [ ] **§2 Theme** — Evaluate or deploy [highnoonoffice/ghost-theme](https://github.com/highnoonoffice/ghost-theme); confirm design fit vs [josephvoelbel.com](https://josephvoelbel.com).
- [ ] **§3 Integration key** — Custom integration, minimal Admin API scopes; secrets only in automation store (never git). OpenClaw path: see [joseph-voelbel-openclaw-clawhub.md](../collaborators/joseph-voelbel-openclaw-clawhub.md).
- [ ] **§4 Migration** (if applicable) — [Meet Magnus](https://josephvoelbel.com/installing-openclaw-meet-magnus/) checklist: redirects, slugs, images, internal links.
- [ ] **§Verification** — All items in GHOST1_RUNBOOK §Verification checked on a **real** instance (HTTPS, test post, API draft lifecycle, backups).

When §Verification is complete, follow [GHOST1_CLOSEOUT.md](GHOST1_CLOSEOUT.md) to mark **GHOST1** done in the software repo.

## Phase 2 — Agent runtime (Mode B vs A)

- [ ] **Decision** — [CURSOR_OPENCLAW_INTEGRATION.md](../collaborators/CURSOR_OPENCLAW_INTEGRATION.md): default **Mode B** (OpenClaw sidecar + ClawHub). Use **Mode A** only if Cursor-native Ghost is required; then apply [security-audit-rules](../../.cursor/skills/security-audit-rules/SKILL.md) before merging any ported `SKILL.md` text.
- [ ] If you **change** primary mode from B to A (or back), append one line to [MiscRepos/.cursor/state/decision-log.md](../../.cursor/state/decision-log.md).

## Phase 3 — OpenClaw / ClawHub (if Mode B and stack in use)

Ordered checklist: [OPENCLAW_CLAWHUB_INSTALL_CHECKLIST.md](OPENCLAW_CLAWHUB_INSTALL_CHECKLIST.md).

## Phase 4 — PKM / vault

- [ ] Copy [vault-templates/README.md](../vault-templates/README.md) templates into your vault; fix wikilinks. _(Rollout 2026-04-16: on one configured host, copies were placed under vault `MOC-from-MiscRepos/` beside `Harness/` — repeat or relocate for your layout.)_
- [ ] Run `sync_harness_to_vault.ps1` from MiscRepos root per [.cursor/docs/OBSIDIAN_VAULT_INTEGRATION.md](../../.cursor/docs/OBSIDIAN_VAULT_INTEGRATION.md) (`OBSIDIAN_VAULT_ROOT` / safe base). _(Same rollout: sync executed successfully to `Harness/Docs/` including this checklist’s mirrors.)_
- [ ] **Automation — int-vault-resync:** After `write_handoff.py`, the repo runs [int-vault-resync.ps1](../../local-proto/scripts/int-vault-resync.ps1) (`-Trigger Handoff`). For markdown churn, enable [`.githooks/README.md`](../../.githooks/README.md) (`git config core.hooksPath .githooks`). Optional daily Task Scheduler **Harness-IntVaultResync** — [SCHEDULED_TASKS.md § Harness-IntVaultResync](../../local-proto/docs/SCHEDULED_TASKS.md). **Health:** `.cursor/state/int_vault_resync.log`; if vault env is wrong, fix `OBSIDIAN_VAULT_ROOT` / `VAULT_SYNC_SAFE_BASE`, then `int-vault-resync.ps1 -Force` or `Show-VaultSyncContext.ps1`. **Escalation:** third consecutive handoff-triggered sync failure returns non-zero from `write_handoff.py` (handoff file still on disk).
- [ ] **Optional:** `pocket/*` tags, Dataview, local graph — [PKM_ATTENTION_POCKETS_AND_BRAIN_MAP.md](../PKM_ATTENTION_POCKETS_AND_BRAIN_MAP.md).
- [ ] **Optional:** Read-only `brain-map-graph.json` snapshot into vault (not SSOT).
- [ ] **Policy:** One ledger markdown; no bulk vault/ledger to **remote** LLM gateways.
