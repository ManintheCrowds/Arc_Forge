---
title: "OpenClaw / ClawHub — ordered install checklist"
tags: ["type/harness-doc", "status/mirror", "domain/harness"]
group: harness-docs
color: blue
cssclasses:
  - vault-grp-harness-docs
  - vault-col-blue
---

# OpenClaw / ClawHub — ordered install checklist

Use when running **Mode B** ([CURSOR_OPENCLAW_INTEGRATION.md](../collaborators/CURSOR_OPENCLAW_INTEGRATION.md)): OpenClaw hosts ClawHub skills; Cursor does not treat zips as `SKILL.md` drop-ins.

**Prereq:** Ghost scoped Admin integration exists if you will use Ghost Publishing Pro — [GHOST1_RUNBOOK.md](../GHOST1_RUNBOOK.md) §3.

| Order | Skill | Operator actions |
|-------|-------|------------------|
| 1 | [Brain Map Visualizer](https://clawhub.ai/highnoonoffice/brain-map-visualizer) | Install; fix ClawHub-noted **parser** issues before unattended automation. |
| 2 | [Ghost Publishing Pro](https://clawhub.ai/highnoonoffice/ghost-publishing-pro) | Install only after Ghost integration key is scoped; credentials under OpenClaw layout (see [joseph-voelbel-openclaw-clawhub.md](../collaborators/joseph-voelbel-openclaw-clawhub.md)). |
| 3 | [Second Brain Visualizer](https://clawhub.ai/highnoonoffice/second-brain-visualizer) | **Localhost** LLM gateway only; reconcile `install.md` vs `cluster.js` paths before trusting. |
| 4 | [Library of Babel](https://clawhub.ai/highnoonoffice/library-of-babel) | **Last:** manual doc vs code review (hub flagged mismatch); do not loop agents on it until reconciled. |

**Structure:** Keep **memory layers** (searchable lists) separate from **Brain Map** topology — [Voelbel: The Brain Map Visualizer](https://josephvoelbel.com/the-brain-map-visualizer/).

**Security context:** ClawHub scan summaries and SCP notes: [joseph-voelbel-openclaw-clawhub.md](../collaborators/joseph-voelbel-openclaw-clawhub.md) §ClawHub platform security scans.
