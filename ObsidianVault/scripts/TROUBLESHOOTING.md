# PDF Ingestion System Troubleshooting Guide

## Quick Diagnostics

### Run Diagnostic Mode
```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "watch_ingest.ps1" -Diagnostic
```

This will:
- Show console output with color-coded messages
- Create/update `ingest_diagnostic.log` with structured JSON logs
- Display decision points and ingestion triggers

### Check System Status
```powershell
# Check scheduled task
schtasks /Query /TN "ObsidianVault-Ingest-Watcher" /FO LIST /V

# Check state file
Get-Content ingest_state.json

# Check diagnostic logs
Get-Content ingest_diagnostic.log -Tail 10
```

## Common Issues

### Issue: ContainsKey Error
**Symptom:** `Method invocation failed because [System.Management.Automation.PSCustomObject] does not contain a method named 'ContainsKey'`

**Solution:** Use `-NoProfile` flag to bypass cached PowerShell modules:
```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "watch_ingest.ps1"
```

### Issue: Ingestion Not Triggering
**Symptom:** No new notes created even with new PDFs

**Diagnosis:**
1. Check if PDFs are newer than last run:
   ```powershell
   Get-Content ingest_state.json
   Get-ChildItem pdf -Filter *.pdf -Recurse | Sort-Object LastWriteTime -Descending | Select-Object -First 1
   ```

2. Clear state to force ingestion:
   ```powershell
   Remove-Item ingest_state.json
   ```

3. Run with diagnostic mode to see decision logic

### Issue: Scheduled Task Not Running
**Symptom:** Task exists but doesn't execute

**Solutions:**
1. Verify task is enabled:
   ```powershell
   schtasks /Query /TN "ObsidianVault-Ingest-Watcher" /FO LIST
   ```

2. Test manual execution:
   ```powershell
   schtasks /Run /TN "ObsidianVault-Ingest-Watcher"
   ```

3. Check task history in Task Scheduler GUI

### Issue: Python Script Errors
**Symptom:** Ingestion fails with Python errors

**Diagnosis:**
1. Check Python version:
   ```powershell
   python --version
   ```

2. Check dependencies:
   ```powershell
   python scripts\check_deps.py
   ```

3. Run ingestion manually:
   ```powershell
   python scripts\ingest_pdfs.py
   ```

### Issue: Missing Source Notes
**Symptom:** PDFs exist but no source notes created

**Diagnosis:**
1. Verify templates exist:
   ```powershell
   Test-Path "Templates\source_note.md"
   Test-Path "Templates\entity_note.md"
   ```

2. Check vault paths in `ingest_config.json`

3. Verify write permissions on vault directory

### Issue: KeyError 'source' when running RAG pipeline with query
**Symptom:** `KeyError: 'source'` at `run_pipeline` line ~1412 when calling `python rag_pipeline.py --config ingest_config.json --query "orks"` (or any query).

**Cause:** `retrieve_context()` returns different schemas depending on which backend is used:
- **KB search** (campaign_kb DB): returns `section_id`, `document_id`, `section_title`, `text`, `score` — no `source`
- **DocumentIndex / text scan fallback**: returns `source`, `score`, `text`

`run_pipeline()` expects `item["source"]` for all results. When `use_kb_search` is True and the campaign_kb DB has matching sections, the KB path is used and the consumer fails.

**Fix:** Normalize `retrieve_context()` so all return paths include a `source` key (e.g. derive from `document_id` or document path for KB results). See [known-issues.md](D:\CodeRepositories\.cursor\state\known-issues.md) for details. For architecture and improvement roadmap: [docs/ERROR_MONITORING_AND_KNOWN_ISSUES.md](docs/ERROR_MONITORING_AND_KNOWN_ISSUES.md).

### Issue: ChromaDB tests fail (PermissionError at teardown, Strict Canon assertion)
**Symptom:** `test_chroma_retriever_build_and_retrieve` fails with `AssertionError: assert 'doc_dnd' in ('doc_wg_1', 'doc_wg_2')` and/or `PermissionError: [WinError 32]` when deleting temp dir.

**Cause (assertion):** `extract_chunk_tags` checks `doc_key` only for D&D; key `doc_dnd` does not contain "d&d" or "dragon", so it gets `system="W&G"` from defaults. Strict Canon filter cannot exclude it.

**Cause (teardown):** ChromaDB holds file locks on `data_level0.bin`; Windows cannot delete files in use.

**Fix:** See [known-issues.md](D:\CodeRepositories\.cursor\state\known-issues.md) (Arc_Forge / ChromaDB tests). Use doc key like `d&d_rules` for D&D content; use `chroma_tmp_path` fixture under `.pytest-tmp` to avoid teardown cleanup.

### Issue: Index Not Updating
**Symptom:** Source_Index.md is outdated

**Solution:** Rebuild index manually:
```powershell
python scripts\build_index.py --overwrite
```

## Manual Operations

### Force Full Ingestion
```powershell
# Clear state and run
Remove-Item ingest_state.json
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "watch_ingest.ps1"
```

### Rebuild Index
```powershell
python scripts\build_index.py --overwrite
```

### Check Diagnostic Logs
```powershell
# View recent logs
Get-Content ingest_diagnostic.log -Tail 20

# Parse JSON logs
Get-Content ingest_diagnostic.log | ConvertFrom-Json | Where-Object { $_.level -eq "ERROR" }
```

## Scheduled Task Management

### View Task Details
```powershell
Get-ScheduledTask -TaskName "ObsidianVault-Ingest-Watcher" | Format-List
```

### Run Task Manually
```powershell
schtasks /Run /TN "ObsidianVault-Ingest-Watcher"
```

### Disable Task
```powershell
schtasks /Change /TN "ObsidianVault-Ingest-Watcher" /DISABLE
```

### Enable Task
```powershell
schtasks /Change /TN "ObsidianVault-Ingest-Watcher" /ENABLE
```

## System Components

- **watch_ingest.ps1** - Watcher script with diagnostic mode
- **ingest_pdfs.py** - Python ingestion engine
- **build_index.py** - Index builder
- **ingest_config.json** - Configuration
- **ingest_state.json** - Last run state
- **ingest_diagnostic.log** - Diagnostic logs

## Getting Help

1. Run diagnostic mode first
2. Check diagnostic logs for detailed information
3. Verify all components are accessible
4. Check file permissions
5. Review configuration paths
