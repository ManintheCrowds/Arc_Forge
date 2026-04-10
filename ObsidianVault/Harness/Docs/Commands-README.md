---
title: "Frequently Used Commands"
tags: ["type/harness-doc", "status/mirror", "domain/harness"]
---

# Frequently Used Commands

Commands and scripts used ~90% of the time. Run from repo root (`D:\portfolio-harness` or `portfolio-harness`).

**PowerShell:** Use `;` not `&&` to chain. Example: `cd D:\portfolio-harness; python .cursor/scripts/sanitize_input.py handoff_latest.md`

---

## Slash Commands (Chat)

| Command | When |
|---------|------|
| `/cl4r1t4s` | Apply CL4R1T4S patterns (frontier-ops, tech-lead, dialectic); bounded retries, convention-first, verify before done |
| `/escalate` | Stop retrying; ask user for direction after multiple failed attempts |

---

## Handoff and Session Flow

| Command | When |
|---------|------|
| `python .cursor/scripts/write_handoff.py --file path\\to\\body.md` | **Preferred:** archive existing handoff, write `handoff_latest.md`, update checksum |
| `python .cursor/scripts/archive_handoff_latest.py` | Archive only (before manual edit); `--dry-run` to preview path |
| `python .cursor/scripts/verify_handoff_staged_archive.py` | Pre-commit: staged handoff vs `HEAD` requires matching staged archive (run via hook) |
| `.\\.cursor\\scripts\\copy_continue_prompt.ps1` | After handoff, before new chat |
| `.\\.cursor\\scripts\\copy_session_start_prompt.ps1` | New chat with declared focus |
| `.\\.cursor\\scripts\\copy_session_start_prompt_flywheel.ps1` | Flywheel mode: propose Next from pending_tasks; await human approval before handoff |
| `.\\.cursor\\scripts\\copy_daggr_deploy_prompt.ps1` | New chat: deploy Daggr visualizations for most important functionality |
| `.\\.cursor\\scripts\\copy_summarize_today_prompt.ps1` | End of day or "summarize today" |
| `.\\.cursor\\scripts\\show_next_goals.ps1` | New session orientation; `-Fallback` infers from handoff |

**Docs:** [docs/agent/HANDOFF_COMPACTION.md](../../docs/agent/HANDOFF_COMPACTION.md) (trim handoff before LLM steps) · [docs/agent/CALLER_SIDE_LLM_BUDGETS.md](../../docs/agent/CALLER_SIDE_LLM_BUDGETS.md) (orchestrator / Ollama env vars and caps).

---

## OWASP / Security (Pre-commit)

**First-time setup:** `pip install pre-commit` (or `pip install -r requirements-dev.txt`), then `pre-commit install` to enable hooks. Hooks run only when relevant paths are staged.

| Command | Purpose |
|---------|---------|
| `pre-commit run --all-files` | Manual run all hooks (CI or before commit) |
| `python .cursor/scripts/verify_handoff_staged_archive.py` | Manual check: staged handoff vs HEAD requires staged archive (same as hook) |
| `python .cursor/scripts/sanitize_input.py handoff_latest.md` | Scan for prompt injection before writing handoff |
| `python .cursor/scripts/sanitize_input.py --check "text"` | Scan inline text |
| `python .cursor/scripts/validate_output.py .cursor/state` | Scan for credential leaks in state (CLI: state dirs; scp_validate_output = MCP for content injection) |
| `python .cursor/scripts/mask_secrets.py --check handoff_latest.md` | Detect secrets before commit |
| `python .cursor/scripts/checksum_integrity.py` | Report rules/skills/org-intent checksums |
| `python .cursor/scripts/checksum_integrity.py --verify --strict` | Verify before rules/skills commit |
| `python .cursor/scripts/checksum_integrity.py --update` | Update baseline after human review |
| `python .cursor/scripts/validate_skill_frontmatter.py` | Optional: warn on skill YAML issues; tiered skills must include handoff fields (`--strict` fails on warnings) |
| (Run [AGENT_INTEGRITY_PRE_ENGAGEMENT_RUNBOOK.md](AGENT_INTEGRITY_PRE_ENGAGEMENT_RUNBOOK.md)) | Before important codebase: SCP red-team, intent, containment |
| (doc) | AI-Trends ingest + SCP analyze + optional summarize: [AI_TRENDS_SCP_PIPELINE.md](AI_TRENDS_SCP_PIPELINE.md) (MCP-operational) |

---

## Audits and Evals

| Command | Purpose |
|---------|---------|
| `.\\.cursor\\scripts\\audit_context_engineering.ps1 -Rubric` | Context integration audit |
| `.\\.cursor\\scripts\\run_ai_evals.ps1` | Run Daggr AI task evals |
| `.\\.cursor\\scripts\\run_meta_review.ps1` | Meta-review (agent performance, drift) |
| `.\\.cursor\\scripts\\scheduled_governance.ps1` | Weekly reminder: log stub + meta-review + **gui wave prompt** ([GOVERNANCE_RITUAL.md](GOVERNANCE_RITUAL.md)); `-SkipGuiWavePrompt` to omit wave block |
| `.\\.cursor\\scripts\\scheduled_code_review.ps1` | Periodic **code review** run: `pytest local-proto/tests` + meta-review log ([local-proto/docs/SCHEDULED_TASKS.md](../../local-proto/docs/SCHEDULED_TASKS.md)); `-SkipTests` / `-SkipMetaReviewPrompt` |
| `python .cursor/scripts/weekly_gui_wave_prompt.py` | Print weekly GUI wave + one agent-native principle (SSOT: [docs/audit/gui_wave_rollout.yaml](../../docs/audit/gui_wave_rollout.yaml)); `pip install -r requirements-dev.txt` for PyYAML. `scheduled_governance.ps1` uses `--append-log … --quiet` so the full prompt goes to the log only (avoid duplicating a long block in the console). **After** pasting output, add the fixed session contract from [docs/audit/GUI_WAVE_TWO_LAYER_CONTRACT.md](../../docs/audit/GUI_WAVE_TWO_LAYER_CONTRACT.md). |
| `python .cursor/scripts/weekly_gui_wave_prompt.py --config docs/audit/gui_wave_rollout_opengrimoire.yaml` | Same as above for **OpenGrimoire** ([`gui_wave_rollout_opengrimoire.yaml](../../docs/audit/gui_wave_rollout_opengrimoire.yaml)); default YAML stays moltbook_watchtower. |
| `python .cursor/scripts/parity_audit_delta.py` | **Action parity delta:** compare latest `.cursor/state/adhoc/action_parity_audit_*.md` to backtick tool names in [MCP_CAPABILITY_MAP.md](MCP_CAPABILITY_MAP.md); prints Markdown to stdout (human review only, not CI). |
| `python .cursor/scripts/check_agent_entry_index_links.py` | Relative link check for [AGENT_ENTRY_INDEX.md](AGENT_ENTRY_INDEX.md); missing targets printed (exit 0 unless `--strict`). |
| (doc) | New GUI surface onboarding: [docs/audit/NEW_GUI_SURFACE_CHECKLIST.md](../../docs/audit/NEW_GUI_SURFACE_CHECKLIST.md) — audit file → smoke test → link YAML → first PR listed files only. |
| `.\\.cursor\\scripts\\run_continual_learning_prompt.ps1` | Continual-learning (extract preferences/facts from transcripts to AGENTS.md) |
| `.\\.cursor\\scripts\\run_skills_improvement_prompt.ps1` | Skills self-improvement loop (use -Phase observe, learn, design, implement, verify, or full) |
| `.\\.cursor\\scripts\\run_daggr_tests.ps1` | Daggr workflow tests |
| `python daggr_workflows/scp_promptfoo_eval.py --standalone` | SCP red-team eval (16 prompts from reference.md) |
| `.\\.cursor\\scripts\\run_model_floor_evals.ps1 -TaskType retrieval` | Model-floor retrieval eval (jCodeMunch + model summarize) |
| `python .cursor/scripts/jcodemunch_benchmark.py` | Retrieval benchmark (separate; no LLM); output_chars, latency, correct |

---

## Credentials and Setup

| Command | Purpose |
|---------|---------|
| `python .cursor/scripts/setup_env.py local-proto` | Generate VAULT_KEY, copy .env.example |
| `python .cursor/scripts/setup_env.py` | General credential setup (PentAGI, Med-Vis, etc.) |
| `python .cursor/scripts/install_agency_agents.py --clone` | Install curated agency-agents to project (SCP-gated) |
| `.\\.cursor\\scripts\\verify_pentagi_protection.ps1` | Verify PentAGI protection setup |

## OpenRAG (Optional)

| Command | Purpose |
|---------|---------|
| `python .cursor/scripts/merge_mcp_openrag.py` | Merge OpenRAG MCP block into mcp.json; `--dry-run` to preview |
| `.\\.cursor\\scripts\\start_openrag.ps1` | Start OpenRAG and verify reachability |

## Fish Speech (Optional, Local)

| Command | Purpose |
|---------|---------|
| `.\\.cursor\\scripts\\start_fish_speech.ps1` | Start fish-speech Docker server and verify reachability |

---

## Observability / Environment Issues

| Command | Purpose |
|---------|---------|
| `python .cursor/scripts/report_environment_issue.py <category> <summary> [details]` | Report env issues (tool_unavailable, api_error, missing_dependency, etc.) per frontier-ops pattern; logs to environment_issues.jsonl |

---

## Agent Telemetry

| Command | Purpose |
|---------|---------|
| `python .cursor/scripts/log_agent_event.py handoff <decision_id> <handoff_number>` | Log handoff event |
| `python .cursor/scripts/log_agent_event.py skill_load <skill> <context>` | Log skill load |
| `python .cursor/scripts/log_agent_event.py critic_score <artifact> <pass> <intent> <safety> <correctness> <completeness> <minimality>` | Log critic score |
| `.\\.cursor\\scripts\\run_populate_agent_log_prompt.ps1` | Generate prompt to populate agent_log from session |

---

## Integrity and Handoff

| Command | Purpose |
|---------|---------|
| `python .cursor/scripts/validate_proposed_next.py [path]` | Validate Next section (1–2 sentences, paths or pending_tasks ID) before human approval; use when human_gate |
| `python .cursor/scripts/validate_pending_tasks_table.py [.cursor/state/pending_tasks.md]` | Check markdown tables in pending_tasks.md for consistent column counts per section |
| `python .cursor/scripts/check_handoff_integrity.py` | Verify handoff checksum (optional) |
| `.\local-proto\scripts\check_intent_checksum.ps1` | Verify org-intent unchanged (local-proto) |
| `.\local-proto\scripts\check_intent_checksum.ps1 -Update` | Accept new org-intent hash after review |
| `.\local-proto\scripts\check_intent_checksum.ps1 -IntentPath <path>` | If clone is not at default `D:/portfolio-harness`, point at your `org-intent.example.json` |

**Pitfalls:** Do not paste the script’s printed lines (e.g. `Updated checksum: …`) back into PowerShell as a command—they are status text, not cmdlets. Use a real date with AI Trends archive scripts (`--date 2026-03-20`), not the literal `YYYY-MM-DD`.

---

## Quick Reference: Pre-commit Checklist

**Before committing handoff or state:**
```powershell
python .cursor/scripts/sanitize_input.py .cursor/state/handoff_latest.md
python .cursor/scripts/validate_output.py .cursor/state
python .cursor/scripts/mask_secrets.py --check .cursor/state/handoff_latest.md
```

**Before committing rules/skills:**
```powershell
# Run security-audit-rules skill first
python .cursor/scripts/checksum_integrity.py --verify --strict
```

---

## See Also

- [AGENT_ENTRY_INDEX.md](AGENT_ENTRY_INDEX.md) — Full doc index
- [state/README.md](../state/README.md) — Memory scripts table
- [OWASP_LLM_PROTECTION_CHECKLIST.md](OWASP_LLM_PROTECTION_CHECKLIST.md) — Security checklist
- [CONTEXT_INTEGRATION_AUDIT.md](CONTEXT_INTEGRATION_AUDIT.md) — Audit scripts
