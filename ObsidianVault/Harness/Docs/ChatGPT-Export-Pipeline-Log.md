---
title: "ChatGPT export pipeline — vault log"
tags: ["type/harness-doc", "status/mirror", "domain/harness"]
group: harness-docs
color: blue
cssclasses:
  - vault-grp-harness-docs
  - vault-col-blue
---

# ChatGPT export pipeline — vault log

**Repo SSOT (edit here, then sync):** `MiscRepos/local-proto/docs/chatgpt-derived/`  
**Harness mirror (this file):** `Harness/Docs/ChatGPT-Export-Pipeline-Log.md` via `local-proto/scripts/sync_harness_to_vault.ps1`

## What shipped

- **Ingest + buckets:** `business` / `personal` / `life_ops` / `ambiguous` → `MiscRepos/.cursor/state/adhoc/chatgpt_export_2026-04-20_*` (gitignored).
- **Overrides:** `business_overrides.json` (force ambiguous → business on ingest).
- **Promoted excerpts:** same folder — scope, security checklist, Proxmox runbook, PEG/broadcast/Crestron/HELO/AJA refs, etc.; index in **`README.md`** (repo only unless you add more `docMappings`).
- **Handoff:** [[Handoff-Latest]] **#30** (`handoff-2026-04-21-chatgpt-export-pipeline`).

## Operator commands

```text
python local-proto/scripts/ingest_chatgpt_export.py --export-root "C:\Users\Dell\Downloads\ChatGPTExport04202026" --tag 2026-04-20
python local-proto/scripts/extract_chatgpt_threads_to_docs.py --export-root "C:\Users\Dell\Downloads\ChatGPTExport04202026"
powershell -File local-proto/scripts/sync_harness_to_vault.ps1 -HarnessRoot "C:\Users\Dell\Documents\GitHub\MiscRepos" -VaultRoot "C:\Users\Dell\Documents\GitHub\Arc_Forge\ObsidianVault"
```

(`VAULT_SYNC_SAFE_BASE` must prefix the vault path if you rely on env-based `-VaultRoot`.)

## Risks

- Classifier + overrides are **heuristic**; promoted MD may contain **PII** — scrub before sharing outside private vault.
