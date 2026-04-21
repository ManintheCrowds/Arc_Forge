---
title: "Cursor skills vs OpenClaw / ClawHub"
tags: ["type/harness-doc", "status/mirror", "domain/harness"]
group: harness-docs
color: blue
cssclasses:
  - vault-grp-harness-docs
  - vault-col-blue
---

# Cursor skills vs OpenClaw / ClawHub

ClawHub bundles (e.g. Ghost Publishing Pro, Brain Map Visualizer) target **OpenClaw**, not Cursor’s `.cursor/skills/**/SKILL.md` format. Treating a downloaded zip as a drop-in Cursor skill will mis-load tools and blur credential boundaries.

## Repo stance (pick one primary)

| Mode | Description | When |
|------|-------------|------|
| **B — OpenClaw sidecar (default)** | Run OpenClaw on a host you control; install ClawHub skills there; keep Ghost Admin JSON and Telegram/Slack tokens in OpenClaw’s credential layout. Cursor edits **MiscRepos + vault**; OpenClaw runs publishing/graph workflows. | You want Voelbel’s bundles with minimal porting and clear separation of trust domains. |
| **A — Port patterns to Cursor** | Re-implement **small** flows (e.g. Ghost Admin JWT, one idempotent “upsert post” path) as **new** repo-native `SKILL.md` files with **your** instructions—**not** a verbatim paste of upstream `SKILL.md`. | You need Ghost or graph steps inside Cursor-only automation. |

**Current default for this workspace:** **Mode B** unless you explicitly commit to maintaining Mode A skills and audits.

## Security before Mode A

If you copy **any** instruction text from Ghost Publishing Pro or other marketplace bundles:

1. Load and apply [.cursor/skills/security-audit-rules/SKILL.md](../../.cursor/skills/security-audit-rules/SKILL.md) (override phrases, shell/env manipulation, remote fetch, hidden Unicode).
2. Prefer **structure-only** reuse; rewrite prose yourself (same skill §Steps).
3. Optional: append a redacted summary to `.cursor/private/audit-findings.md` per that skill.

## OpenClaw skill install order (operator)

When running the full Voelbel-style stack, use this order (risk and dependency aware):

1. **Brain Map Visualizer** — read-mostly; fix parser issues noted on ClawHub before unattended loops.
2. **Ghost Publishing Pro** — only after a **scoped Ghost Admin integration** key exists (not a full staff user).
3. **Second Brain Visualizer** — only with **localhost** LLM gateway and least-privilege bots; verify install docs vs code paths.
4. **Library of Babel** — last, after **manual** code and documentation review (hub flagged doc/code mismatch).

## Memory layers vs Brain Map (topology)

Per Voelbel’s [Brain Map article](https://josephvoelbel.com/the-brain-map-visualizer/): keep **searchable memory lists** (files, ledgers, SOUL/MEMORY/USER-style layers) **separate** from the **topology graph** (what connects to what). Lists answer “where is it?”; the graph answers “how does attention cluster?” Do not collapse both into one artifact.

## See also

- [joseph-voelbel-openclaw-clawhub.md](joseph-voelbel-openclaw-clawhub.md) — catalog, links, SCP summary.
- [GHOST1_RUNBOOK.md](../GHOST1_RUNBOOK.md) — Ghost site task.
- [PKM_ATTENTION_POCKETS_AND_BRAIN_MAP.md](../PKM_ATTENTION_POCKETS_AND_BRAIN_MAP.md) — vault-side parity without OpenClaw.
- [INTEGRATION_ROLLOUT_OPERATOR_CHECKLIST.md](../operations/INTEGRATION_ROLLOUT_OPERATOR_CHECKLIST.md) — phased operator checklist (Ghost → runtime → OpenClaw → PKM).
- [OPENCLAW_CLAWHUB_INSTALL_CHECKLIST.md](../operations/OPENCLAW_CLAWHUB_INSTALL_CHECKLIST.md) — ClawHub install order table.
