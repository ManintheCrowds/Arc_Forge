---
title: "Scheduled tasks (MiscRepos + local-proto)"
tags: ["type/harness-doc", "status/mirror", "domain/harness"]
---

# Scheduled tasks (MiscRepos + local-proto)

Single source of truth for **what to run on a schedule**, **where logs go**, and **how to wire the OS or GitHub**. Cursor agents are **not** started by these jobs; see [.cursor/docs/GOVERNANCE_RITUAL.md](../../.cursor/docs/GOVERNANCE_RITUAL.md) for the same rule on governance.

## Scripts (run from repo root unless noted)

| Job | Script | Purpose | Default log location |
|-----|--------|---------|----------------------|
| Daily ops | `local-proto/scripts/daily_ops.ps1` | Precheck, MCP warmup, tiered smoke, optional OpenHarness bundle verify | Console; see [OPS_BOOTSTRAP_OPEN_GRIMOIRE.md](OPS_BOOTSTRAP_OPEN_GRIMOIRE.md) |
| Weekly governance | `.cursor/scripts/scheduled_governance.ps1` | Meta-review + GUI wave prompts | `.cursor/state/governance_runs/` |
| Code review (periodic) | `.cursor/scripts/scheduled_code_review.ps1` | `pytest local-proto/tests` + meta-review prompt log | `.cursor/state/code_review_runs/` |
| Context / token baseline | `local-proto/scripts/scheduled_perf_context_bundle.ps1` | Runs [measure_context_bundle.py](../scripts/measure_context_bundle.py) | `.cursor/state/perf_bundle_runs/` |
| Dependency report (local) | `local-proto/scripts/report_outdated_dependencies.ps1` | `pip list --outdated` (no upgrades) | `local-proto/logs/dependency_reports/` |

### PowerShell examples

```powershell
# Code review (tests + meta-review log)
powershell -ExecutionPolicy Bypass -File .cursor/scripts/scheduled_code_review.ps1

# Token bundle (add -OrchestratorEstimate for orchestrator chat estimate)
powershell -ExecutionPolicy Bypass -File local-proto/scripts/scheduled_perf_context_bundle.ps1

# Outdated packages report only
powershell -ExecutionPolicy Bypass -File local-proto/scripts/report_outdated_dependencies.ps1
```

### Cron (Linux/macOS) examples

Use the machine’s local timezone or UTC consistently.

| Intent | Cron | Command |
|--------|------|---------|
| Code review twice daily | `0 12,20 * * *` | `cd /path/to/MiscRepos && powershell -ExecutionPolicy Bypass -File .cursor/scripts/scheduled_code_review.ps1` |
| Token bundle hourly | `0 * * * *` | `cd /path/to/MiscRepos && powershell -ExecutionPolicy Bypass -File local-proto/scripts/scheduled_perf_context_bundle.ps1 -Quiet` |
| Weekly outdated report (Sunday 00:00) | `0 0 * * 0` | `cd /path/to/MiscRepos && powershell -ExecutionPolicy Bypass -File local-proto/scripts/report_outdated_dependencies.ps1` |

**Note:** `*/1 * * * *` runs **every minute**, not hourly. For hourly use `0 * * * *`.

### Windows Task Scheduler

Canonical click-by-click steps for recurring tasks: [.cursor/docs/GOVERNANCE_RITUAL.md](../../.cursor/docs/GOVERNANCE_RITUAL.md) (Scheduled task section). Create one task per script or combine triggers (e.g. bi-daily code review: two daily triggers at 12:00 and 20:00, or weekdays only).

## GitHub (remote)

| Mechanism | Location | Purpose |
|-----------|----------|---------|
| Dependabot | [.github/dependabot.yml](../../.github/dependabot.yml) | Weekly pip PRs for `local-proto/` |
| Scheduled workflow | [.github/workflows/scheduled_harness_checks.yml](../../.github/workflows/scheduled_harness_checks.yml) | ~Twice-weekly `pytest` on `local-proto/tests` + manual `workflow_dispatch` |

**Merge protection:** Enable required checks on `main` for the workflow and/or your primary CI when you adopt them; optional CodeQL and other scanners are outside this doc.

## Interpretation: “performance” here

[CONTEXT_TOKEN_BENCHMARK.md](CONTEXT_TOKEN_BENCHMARK.md) defines **context/token** measurement for the Cursor bundle. `scheduled_perf_context_bundle.ps1` tracks that baseline over time. Application APM (latency, CPU) is not part of these scripts; add separate tooling if needed.

## Related

- [CAPABILITY_INDEX.md](CAPABILITY_INDEX.md) — index entry for this page
- [REPO_BOUNDARY_INDEX.md](REPO_BOUNDARY_INDEX.md) — which flows live where
