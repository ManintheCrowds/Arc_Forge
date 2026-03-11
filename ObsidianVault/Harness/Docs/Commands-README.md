# Frequently Used Commands

Commands and scripts used ~90% of the time. Run from repo root (`D:\portfolio-harness` or `portfolio-harness`).

**PowerShell:** Use `;` not `&&` to chain. Example: `cd D:\portfolio-harness; python .cursor/scripts/sanitize_input.py handoff_latest.md`

---

## Handoff and Session Flow

| Command | When |
|---------|------|
| `.\\.cursor\\scripts\\copy_continue_prompt.ps1` | After handoff, before new chat |
| `.\\.cursor\\scripts\\copy_session_start_prompt.ps1` | New chat with declared focus |
| `.\\.cursor\\scripts\\copy_session_start_prompt_flywheel.ps1` | Flywheel mode: propose Next from pending_tasks; await human approval before handoff |
| `.\\.cursor\\scripts\\copy_daggr_deploy_prompt.ps1` | New chat: deploy Daggr visualizations for most important functionality |
| `.\\.cursor\\scripts\\copy_summarize_today_prompt.ps1` | End of day or "summarize today" |
| `.\\.cursor\\scripts\\show_next_goals.ps1` | New session orientation; `-Fallback` infers from handoff |

---

## OWASP / Security (Pre-commit)

| Command | Purpose |
|---------|---------|
| `python .cursor/scripts/sanitize_input.py handoff_latest.md` | Scan for prompt injection before writing handoff |
| `python .cursor/scripts/sanitize_input.py --check "text"` | Scan inline text |
| `python .cursor/scripts/validate_output.py .cursor/state` | Scan for credential leaks in state |
| `python .cursor/scripts/mask_secrets.py --check handoff_latest.md` | Detect secrets before commit |
| `python .cursor/scripts/checksum_integrity.py` | Report rules/skills/org-intent checksums |
| `python .cursor/scripts/checksum_integrity.py --verify --strict` | Verify before rules/skills commit |
| `python .cursor/scripts/checksum_integrity.py --update` | Update baseline after human review |

---

## Audits and Evals

| Command | Purpose |
|---------|---------|
| `.\\.cursor\\scripts\\audit_context_engineering.ps1 -Rubric` | Context integration audit |
| `.\\.cursor\\scripts\\run_ai_evals.ps1` | Run Daggr AI task evals |
| `.\\.cursor\\scripts\\run_meta_review.ps1` | Meta-review (agent performance, drift) |
| `.\\.cursor\\scripts\\run_continual_learning_prompt.ps1` | Continual-learning (extract preferences/facts from transcripts to AGENTS.md) |
| `.\\.cursor\\scripts\\run_skills_improvement_prompt.ps1` | Skills self-improvement loop (use -Phase observe, learn, design, implement, verify, or full) |
| `.\\.cursor\\scripts\\run_daggr_tests.ps1` | Daggr workflow tests |
| `.\\.cursor\\scripts\\run_model_floor_evals.ps1 -TaskType retrieval` | Model-floor retrieval eval (jCodeMunch + model summarize) |
| `python .cursor/scripts/jcodemunch_benchmark.py` | Retrieval benchmark (separate; no LLM); output_chars, latency, correct |

---

## Credentials and Setup

| Command | Purpose |
|---------|---------|
| `python .cursor/scripts/setup_env.py local-proto` | Generate VAULT_KEY, copy .env.example |
| `python .cursor/scripts/setup_env.py` | General credential setup (PentAGI, Med-Vis, etc.) |
| `.\\.cursor\\scripts\\verify_pentagi_protection.ps1` | Verify PentAGI protection setup |

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
| `python .cursor/scripts/check_handoff_integrity.py` | Verify handoff checksum (optional) |
| `.\local-proto\scripts\check_intent_checksum.ps1` | Verify org-intent unchanged (local-proto) |
| `.\local-proto\scripts\check_intent_checksum.ps1 -Update` | Accept new org-intent hash after review |

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
