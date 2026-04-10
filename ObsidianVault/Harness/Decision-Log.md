---
title: "Decision Log"
tags: ["type/harness-state", "status/mirror", "domain/harness"]
---

# Decision Log

- 2026-04-03 | Area: Repo naming / portfolio layout | Decision: Completed cross-repo replacement of legacy **OpenAtlas** strings and folder names with **OpenGrimoire**; **portfolio-harness/OpenGrimoire** is a junction to the OpenGrimoire repo; MiscRepos uses **OpenGrimoire/** for CI path filters. | Rationale: single product name in docs and tooling; remote GitHub rename remains a separate step. (handoff: handoff-2026-04-03-opengrimoire-naming-migration)
- 2026-03-24 | Area: OpenGrimoire naming (OG-1) | Decision: Initiative name **OpenGrimoire** (one word) in operator docs; **OpenCompass** remains literal for upstream framework, CSV artifacts, and MCP/tool ids. | Rationale: avoids conflating the portfolio pipeline with the third-party eval project; see `OpenGrimoire/docs/OPEN_GRIMOIRE_LOCAL_FIRST_INTEGRATION.md` and `.cursor/state/og1_opencompass_opengrimoire_audit.md`.
- 2026-03-23 | Area: Ops bootstrap/OpenGrimoire | Decision: Use `local-proto` as execution control-plane and OpenHarness as canonical governance bundle source; keep OpenGrimoire integration local-first via optional metadata extensions. | Rationale: preserves existing workflows, reduces token cost via local routing, and avoids breaking current graph/API contracts.
