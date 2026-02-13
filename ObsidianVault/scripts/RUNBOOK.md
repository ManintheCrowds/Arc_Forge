# PDF Ingestion System Runbook

## System Overview

Automated PDF ingestion system that:
- Watches `pdf/` directory for new/updated PDFs
- Creates source notes in `Sources/` with metadata
- Extracts text and creates atomic notes (NPCs, Factions, etc.)
- Maintains searchable index
- Runs automatically via Windows Scheduled Task (every 10 minutes)

## Daily Operations

### Normal Operation
System runs automatically. No intervention needed.

### Verify System Health
```powershell
# Check scheduled task status
schtasks /Query /TN "ObsidianVault-Ingest-Watcher" /FO LIST

# Check last run time in state file
Get-Content scripts\ingest_state.json

# View recent diagnostic logs
Get-Content scripts\ingest_diagnostic.log -Tail 10
```

## Adding New PDFs

1. Place PDF in `pdf/` directory (or subdirectory)
2. System will detect within 10 minutes (or trigger manually)
3. Source note created in `Sources/`
4. Index updated (run manually: `python scripts\build_index.py --overwrite`)

## Manual Operations

### Force Ingestion
```powershell
cd D:\Arc_Forge\ObsidianVault\scripts
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "watch_ingest.ps1" -Diagnostic
```

### Rebuild Index
```powershell
cd D:\Arc_Forge\ObsidianVault\scripts
python build_index.py --overwrite
```

### Check System Status
```powershell
# PDF count
(Get-ChildItem "D:\Arc_Forge\ObsidianVault\pdf" -Filter *.pdf -Recurse).Count

# Source note count
(Get-ChildItem "D:\Arc_Forge\ObsidianVault\Sources" -Filter *.md -Recurse).Count

# Latest PDF
Get-ChildItem "D:\Arc_Forge\ObsidianVault\pdf" -Filter *.pdf -Recurse | Sort-Object LastWriteTime -Descending | Select-Object -First 1
```

## Scheduled Task

**Task Name:** `ObsidianVault-Ingest-Watcher`

**Schedule:** Every 10 minutes

**Command:**
```
powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File "D:\Arc_Forge\ObsidianVault\scripts\watch_ingest.ps1"
```

**Management:**
- View: `schtasks /Query /TN "ObsidianVault-Ingest-Watcher" /FO LIST /V`
- Run: `schtasks /Run /TN "ObsidianVault-Ingest-Watcher"`
- Disable: `schtasks /Change /TN "ObsidianVault-Ingest-Watcher" /DISABLE`
- Enable: `schtasks /Change /TN "ObsidianVault-Ingest-Watcher" /ENABLE`

## Configuration

**Config File:** `scripts\ingest_config.json`

Key settings:
- `vault_root` - Obsidian vault root
- `pdf_root` - PDF source directory
- `source_notes_dir` - Where source notes are created
- `diagnostic.log_path` - Diagnostic log location

## Diagnostic Mode

Enable diagnostic logging:
```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "watch_ingest.ps1" -Diagnostic
```

Or with custom log path:
```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "watch_ingest.ps1" -Diagnostic -LogPath "custom.log"
```

## Maintenance

### Weekly
- Review diagnostic logs for errors
- Verify index is up to date
- Check scheduled task is running

### Monthly
- Rebuild index: `python scripts\build_index.py --overwrite`
- Review source notes organization
- Clean up old diagnostic logs if needed

## Troubleshooting

See `TROUBLESHOOTING.md` for detailed troubleshooting guide.

## Support

1. Run diagnostic mode first
2. Check logs in `ingest_diagnostic.log`
3. Verify all paths in `ingest_config.json`
4. Test components individually
