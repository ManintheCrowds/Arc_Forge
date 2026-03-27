# Multi-repo GUI audit — master index

**Date:** 2026-03-26  
**Playbook:** Multi-repo end-to-end GUI audit (Arc_Forge planning artifact; do not confuse with this index path).

This index links each repository’s primary GUI audit artifact. Full methodology (prompt template, tools, decomposition, severity rubric) lives in the playbook you used to kick off this pass.

## Artifacts by repository

| Repository | Scope | Artifact |
|------------|--------|----------|
| OpenAtlas | Next.js app (OpenGrimoire) | [gui-2026-03-26.md](../../../OpenAtlas/docs/audit/gui-2026-03-26.md) |
| Arc_Forge | `ObsidianVault/workflow_ui` (Flask + JS + Gradio) | [gui-workflow_ui-2026-03-26.md](./gui-workflow_ui-2026-03-26.md) |
| moltbook_watchtower | Generated static dashboard | [gui-2026-03-26.md](../../../moltbook_watchtower/docs/audit/gui-2026-03-26.md) |
| OpenHarness | No product GUI | [gui-2026-03-26.md](../../../OpenHarness/docs/audit/gui-2026-03-26.md) |
| SCP | MCP server (non-browser) | [gui-2026-03-26.md](../../../SCP/docs/audit/gui-2026-03-26.md) |
| VibeLedger | Docs-only repo | [gui-2026-03-26.md](../../../VibeLedger/docs/audit/gui-2026-03-26.md) |
| Planswithinplans | Plans archive | [gui-2026-03-26.md](../../../Planswithinplans/docs/audit/gui-2026-03-26.md) |
| software | Plans-heavy; no app root | [gui-2026-03-26.md](../../../software/docs/audit/gui-2026-03-26.md) |
| MiscRepos | No `package.json` at root; scan result | [gui-2026-03-26.md](../../../MiscRepos/docs/audit/gui-2026-03-26.md) |

**Note:** Links are relative to this file (`Arc_Forge/docs/audit/GUI_AUDIT_INDEX.md`) with sibling repos under the same parent directory.

## Triage queue (cross-repo)

Priority is **P0 = do next** for shipped surfaces; **P3 = backlog / optional**.

| P | Repository | Next action | Notes |
|---|------------|-------------|--------|
| P0 | **OpenAtlas** | Keep `npm run test:e2e` green in CI | Smoke nav flake fixed (2026-03-26): `waitForURL` + `click` in parallel in `e2e/smoke.spec.ts`. |
| P1 | **OpenAtlas** | Security follow-ups from [agent_native_review Appendix B](../../../OpenAtlas/docs/audit/agent_native_review_2026-03-26.md) | Split alignment vs survey-read keys; review `NEXT_PUBLIC_BRAIN_MAP_SECRET`. |
| P1 | **Arc_Forge** | Run `ObsidianVault/workflow_ui` Playwright from vault root with env | `tests/e2e/test_workflow_ui_playwright_smoke.py`; Gradio/KB redirects need services. |
| P2 | **moltbook_watchtower** | One manual open of generated `exports/dashboard.html` + console check | No E2E yet; generator is `scripts/generate_dashboard_html.py`. |
| P2 | **MiscRepos** | Optional deep GUI audit: `WatchTower_main/WatchTower_main/app/templates/` or `docs/demo/*.html` | See [MiscRepos gui audit](../../../MiscRepos/docs/audit/gui-2026-03-26.md). |
| P3 | **OpenHarness** | No GUI; refresh docs links if browser-review-protocol moves | N/A stubs only unless adding a viewer. |
| P3 | **SCP** | README/tool ergonomics when MCP schema changes | N/A for browser. |
| P3 | **VibeLedger / Planswithinplans / software** | No app tree; skip until a subfolder app exists | Point future audits at sibling repos with `package.json` / Flask. |

**Agent-native / harness:** OpenAtlas report [agent_native_review_2026-03-26.md](../../../OpenAtlas/docs/audit/agent_native_review_2026-03-26.md) — lead with **Axis A** scorecard when asking “are agents unblocked?”

## Optional follow-ups

- Run full OpenAtlas `npm run test:e2e` after substantive routing or layout changes.
- Run Arc_Forge `workflow_ui` Playwright tests with a live Flask fixture when the vault path and env are configured.
