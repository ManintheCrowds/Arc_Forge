---
title: "GHOST1 — Ghost personal or project site"
tags: ["type/harness-doc", "status/mirror", "domain/harness"]
---

# GHOST1 — Ghost personal or project site

Runbook for standing up a **Ghost** site aligned with task **GHOST1** (see `software/.cursor/state/pending_tasks.md` on hosts that track that repo, and MiscRepos harness docs here).

**Operator checklist (phased):** [docs/operations/INTEGRATION_ROLLOUT_OPERATOR_CHECKLIST.md](operations/INTEGRATION_ROLLOUT_OPERATOR_CHECKLIST.md). **After §Verification:** [docs/operations/GHOST1_CLOSEOUT.md](operations/GHOST1_CLOSEOUT.md).

## Outcomes

- A running Ghost instance (self-host or Ghost(Pro)-style managed—your choice).
- A **scoped Admin API integration** (custom integration in Ghost Admin) for any automation (OpenClaw Ghost Publishing Pro or a future thin Cursor skill).
- Optional theme based on [highnoonoffice/ghost-theme](https://github.com/highnoonoffice/ghost-theme).

## Steps

### 1. Provision Ghost

- Example local Docker stack (Ghost + MySQL + mkcert TLS): sibling **`ghost-local`** repo next to this checkout (for example `Documents/GitHub/ghost-local`).
- Choose install path: official Docker image, bare metal, or managed Ghost.
- Set site URL, mail (for newsletters/password reset), and TLS.
- Complete first-run admin user in the web UI.

### 2. Theme evaluation

- Clone or submodule [github.com/highnoonoffice/ghost-theme](https://github.com/highnoonoffice/ghost-theme).
- Upload zip in Ghost Admin **Settings → Design** or deploy as a custom theme per Ghost docs.
- Confirm contrast, typography, and post/card templates match your publishing style (Voelbel’s site is a minimal reference: [josephvoelbel.com](https://josephvoelbel.com)).

### 3. Integration key (before any agent writes)

- Ghost Admin → **Integrations** → add custom integration.
- Grant **only** the capabilities you need (posts, tags, images—not full admin if avoidable).
- Store `Admin API Key` and `API URL` in the automation runtime’s secret store (OpenClaw: `~/.openclaw/credentials/ghost-admin.json` per [joseph-voelbel-openclaw-clawhub.md](collaborators/joseph-voelbel-openclaw-clawhub.md)—never commit keys).

### 4. Content migration (if applicable)

- Use [Installing OpenClaw: Meet Magnus](https://josephvoelbel.com/installing-openclaw-meet-magnus/) as a **narrative checklist** for large migrations (e.g. 200+ posts): slugs, redirects, image assets, internal links.
- Ghost’s built-in import tools plus manual QA for edge cases.

### 5. Publishing automation (after 1–3)

- **Option A (default alignment):** [Ghost Publishing Pro on ClawHub](https://clawhub.ai/highnoonoffice/ghost-publishing-pro) inside **OpenClaw** (see [CURSOR_OPENCLAW_INTEGRATION.md](collaborators/CURSOR_OPENCLAW_INTEGRATION.md)).
- **Option B:** Port minimal flows into Cursor-native skills only after [security-audit-rules](../.cursor/skills/security-audit-rules/SKILL.md) on any copied instructions.

## Verification

- [ ] Public homepage loads over HTTPS.
- [ ] Create/edit/publish one test post in Admin.
- [ ] Integration key can create a draft post via Admin API (curl or ClawHub workflow) and you can delete the draft.
- [ ] Backups scheduled (DB + `content/`).

## Cross-references

- Voelbel primer: [joseph-voelbel-openclaw-clawhub.md](collaborators/joseph-voelbel-openclaw-clawhub.md)
- Cursor vs OpenClaw: [CURSOR_OPENCLAW_INTEGRATION.md](collaborators/CURSOR_OPENCLAW_INTEGRATION.md)
