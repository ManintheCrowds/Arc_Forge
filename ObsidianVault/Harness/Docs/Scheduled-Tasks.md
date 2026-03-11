# Scheduled Tasks (Harness and Local-Proto)

Central documentation for harness and local-proto scheduled automation. Use Windows Task Scheduler (schtasks) on Windows; see Appendix for cron equivalents on Linux/macOS.

**Replace `D:\portfolio-harness` with your repo path** (or set `HARNESS_ROOT` and use `%HARNESS_ROOT%` in commands).

---

## Prerequisites

- **Repo path:** Set `HARNESS_ROOT` env var or replace paths in commands
- **Python** in PATH (for orchestrator, Python scripts)
- **PowerShell** for .ps1 scripts
- **Working directory:** Run from harness root (`D:\portfolio-harness`) unless noted

---

## Task Registry

| Task | Schedule | Script | Purpose |
|------|----------|--------|---------|
| LocalProto-Orchestrator | On logon | orchestrator.py | Handoff watcher; reacts to handoff changes |
| Harness-DriftAnalysis | Weekly Sun 9 AM | analyze_drift.ps1 -Days 7 | Governance drift; exit 1 = review needed |
| Harness-MetaReviewPrompt | Weekly Mon 8 AM | run_meta_review.ps1 | Generate meta-review prompt for new chat |
| Harness-IntentChecksum | Weekly Sun 8 AM | check_intent_checksum.ps1 | Verify org-intent unchanged |
| Harness-PreCommitSecurity | Daily 6 AM | sanitize_input, validate_output, mask_secrets | State file hygiene |
| Harness-AuditRotation | Weekly Sun 2 AM | rotate_audit_logs.ps1 | Archive old audit log entries |
| Harness-VaultSync | Optional (manual or daily) | sync_harness_to_vault.ps1 | Mirror handoff, pending_tasks, decision-log, daily, docs to Obsidian Harness/ |
| Harness-DaggrRegistry | Weekly Sat 8 AM | run_daggr_registry.ps1 | Update Daggr workflow registry for monitoring |
| VehicleRecovery-* | Per [SCHEDULE_VEHICLE_RECOVERY.md](SCHEDULE_VEHICLE_RECOVERY.md) | run_vehicle_recovery_scheduled.ps1 | NICB + marketplace scraper |

---

## schtasks Commands

### LocalProto-Orchestrator (start on logon)

Keeps handoff watcher running. Restart manually if it exits.

```powershell
schtasks /create /tn "LocalProto-Orchestrator" /tr "python D:\portfolio-harness\.cursor\scripts\orchestrator.py" /sc onlogon /ru "%USERNAME%" /rl HIGHEST
```

**Start in:** `D:\portfolio-harness` (set via Task Scheduler GUI: Properties → General → "Run with highest privileges" if needed; configure "Start in" under Actions → Edit)

**Remove:**
```powershell
schtasks /delete /tn "LocalProto-Orchestrator" /f
```

---

### Harness-DriftAnalysis (weekly)

Exit 1 means drift detected; check Task Scheduler history for exit code.

```powershell
schtasks /create /tn "Harness-DriftAnalysis" /tr "powershell.exe -NoProfile -ExecutionPolicy Bypass -File \"D:\portfolio-harness\.cursor\scripts\analyze_drift.ps1\" -Days 7" /sc weekly /d SUN /st 09:00 /ru "%USERNAME%"
```

**Remove:**
```powershell
schtasks /delete /tn "Harness-DriftAnalysis" /f
```

---

### Harness-MetaReviewPrompt (weekly)

Output goes to task log. Copy prompt from output and paste into new Cursor chat.

```powershell
schtasks /create /tn "Harness-MetaReviewPrompt" /tr "powershell.exe -NoProfile -ExecutionPolicy Bypass -File \"D:\portfolio-harness\.cursor\scripts\run_meta_review.ps1\"" /sc weekly /d MON /st 08:00 /ru "%USERNAME%"
```

**Remove:**
```powershell
schtasks /delete /tn "Harness-MetaReviewPrompt" /f
```

---

### Harness-IntentChecksum (weekly)

Verifies org-intent JSON unchanged. Exit 1 if hash mismatch.

```powershell
schtasks /create /tn "Harness-IntentChecksum" /tr "powershell.exe -NoProfile -ExecutionPolicy Bypass -File \"D:\portfolio-harness\local-proto\scripts\check_intent_checksum.ps1\"" /sc weekly /d SUN /st 08:00 /ru "%USERNAME%"
```

**Remove:**
```powershell
schtasks /delete /tn "Harness-IntentChecksum" /f
```

---

### Harness-PreCommitSecurity (daily)

Scans state for credential leaks and prompt injection. Non-blocking; logs findings.

```powershell
schtasks /create /tn "Harness-PreCommitSecurity" /tr "powershell.exe -NoProfile -ExecutionPolicy Bypass -Command \"cd D:\portfolio-harness; python .cursor/scripts/sanitize_input.py .cursor/state/handoff_latest.md 2>&1; python .cursor/scripts/validate_output.py .cursor/state 2>&1; python .cursor/scripts/mask_secrets.py --check .cursor/state/handoff_latest.md 2>&1\"" /sc daily /st 06:00 /ru "%USERNAME%"
```

**Remove:**
```powershell
schtasks /delete /tn "Harness-PreCommitSecurity" /f
```

---

### Harness-AuditRotation (weekly)

Archives audit log entries older than retention period. See [OBSERVABILITY_LAYER.md](OBSERVABILITY_LAYER.md).

```powershell
schtasks /create /tn "Harness-AuditRotation" /tr "powershell.exe -NoProfile -ExecutionPolicy Bypass -File \"D:\portfolio-harness\local-proto\scripts\rotate_audit_logs.ps1\"" /sc weekly /d SUN /st 02:00 /ru "%USERNAME%"
```

**Remove:**
```powershell
schtasks /delete /tn "Harness-AuditRotation" /f
```

---

### Harness-VaultSync (optional)

Mirrors handoff, pending_tasks, decision-log, daily summaries, and key docs to Obsidian vault `Harness/` for human review. See [OBSIDIAN_VAULT_INTEGRATION.md](../../.cursor/docs/OBSIDIAN_VAULT_INTEGRATION.md). Requires `OBSIDIAN_VAULT_ROOT` env or `-VaultRoot` param.

**Run manually:** After handoff or when you want to review harness state in Obsidian:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "D:\portfolio-harness\local-proto\scripts\sync_harness_to_vault.ps1"
```

**Optional daily:** Run at 7 AM to keep vault in sync:
```powershell
schtasks /create /tn "Harness-VaultSync" /tr "powershell.exe -NoProfile -ExecutionPolicy Bypass -File \"D:\portfolio-harness\local-proto\scripts\sync_harness_to_vault.ps1\"" /sc daily /st 07:00 /ru "%USERNAME%"
```

**Remove:**
```powershell
schtasks /delete /tn "Harness-VaultSync" /f
```

---

### Harness-DaggrRegistry (weekly)

Updates Daggr workflow registry at `%LOCALAPPDATA%\local-proto\daggr_registry\workflows.json`. Runs `verify_integration` for WatchTower and campaign_kb. Exit 1 if all stacks fail.

```powershell
schtasks /create /tn "Harness-DaggrRegistry" /tr "powershell.exe -NoProfile -ExecutionPolicy Bypass -File \"D:\portfolio-harness\local-proto\scripts\run_daggr_registry.ps1\"" /sc weekly /d SAT /st 08:00 /ru "%USERNAME%"
```

**Remove:**
```powershell
schtasks /delete /tn "Harness-DaggrRegistry" /f
```

---

## Maintenance

### List harness tasks

```powershell
schtasks /query /tn "Harness-*" /fo LIST
schtasks /query /tn "LocalProto-*" /fo LIST
```

### Disable a task

```powershell
schtasks /change /tn "Harness-DriftAnalysis" /disable
```

### Enable a task

```powershell
schtasks /change /tn "Harness-DriftAnalysis" /enable
```

### View task history

Open **Task Scheduler** (taskschd.msc) → Task Scheduler Library → select task → **History** tab.

### Logs and output

- **Audit dir:** `%LOCALAPPDATA%\local-proto\audit\`
- **Task output:** Configure task to save output: Actions → Edit → Add `>> D:\portfolio-harness\.cursor\state\adhoc\task_<name>_log.txt 2>&1` to command if desired
- **Drift exit 1:** Check task history; run `analyze_drift.ps1 -Days 7` manually to see report

---

## Cross-References

- [SCHEDULE_VEHICLE_RECOVERY.md](SCHEDULE_VEHICLE_RECOVERY.md) — Vehicle recovery tasks (NICB, marketplace)
- [OBSERVABILITY_LAYER.md](OBSERVABILITY_LAYER.md) — Audit log schema, drift monitoring
- [OBSIDIAN_VAULT_INTEGRATION.md](../../.cursor/docs/OBSIDIAN_VAULT_INTEGRATION.md) — Vault sync, Harness/ folder
- [COMMANDS_README.md](../../.cursor/docs/COMMANDS_README.md) — Full command reference
- [ORCHESTRATOR_CONFIG.md](ORCHESTRATOR_CONFIG.md) — Orchestrator config

---

## Appendix: Cron (Linux/macOS)

```bash
# Drift analysis — Sundays 9 AM
0 9 * * 0 cd /path/to/portfolio-harness && powershell -File .cursor/scripts/analyze_drift.ps1 -Days 7

# Meta-review prompt — Mondays 8 AM
0 8 * * 1 cd /path/to/portfolio-harness && powershell -File .cursor/scripts/run_meta_review.ps1

# Intent checksum — Sundays 8 AM
0 8 * * 0 cd /path/to/portfolio-harness && powershell -File local-proto/scripts/check_intent_checksum.ps1

# Audit rotation — Sundays 2 AM
0 2 * * 0 cd /path/to/portfolio-harness && powershell -File local-proto/scripts/rotate_audit_logs.ps1

# Daggr registry — Saturdays 8 AM
0 8 * * 6 cd /path/to/portfolio-harness && powershell -File local-proto/scripts/run_daggr_registry.ps1
```

Adjust paths and use `pwsh` if PowerShell Core is installed.
