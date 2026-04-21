---
title: "Handoff #25: Ghost canonical publishing backlog + vault Harness sync (HARNESS_ROOT)"
tags: ["type/harness-state", "status/mirror", "domain/harness"]
group: harness-archive
color: slate
cssclasses:
  - vault-grp-harness-archive
  - vault-col-slate
---

# Handoff #25: Ghost canonical publishing backlog + vault Harness sync (HARNESS_ROOT)

decision_id: handoff-2026-04-18-pub-ghost-harness-sync
supersedes: handoff-2026-04-18-og-gui-wave10-audit-vault
Updated: 2026-04-18T19:29:13Z

## Done

- **`pending_tasks.md`:** New Contents theme + **`## PENDING_GHOST_CANONICAL_PUBLISHING (corpus, RAID archive, distribution)`** — **PUB-0 … PUB-14**; principle **Ghost = canonical** for all published work; other channels = syndication only. Cross-refs GWS, WS-PRIV, vault sync note.
- **`sync_harness_to_vault.ps1`:** Ran from `e:\local-proto\workspace\scripts\` — default **Harness root** resolved to **`E:\local-proto`** → state/doc copies **`[SKIP]`** (sources missing). **Re-ran** with **`-HarnessRoot "C:\Users\Dell\Documents\GitHub\MiscRepos"`** → **`[OK]`** on **`Harness/Pending-Tasks.md`** and full mirror under **`Arc_Forge/ObsidianVault/Harness`**.

## Next

- **`HARNESS_ROOT` habit:** When MiscRepos is SSOT for `.cursor/state`, set **`HARNESS_ROOT=C:\Users\Dell\Documents\GitHub\MiscRepos`** or always pass **`-HarnessRoot`** to `sync_harness_to_vault.ps1` so the vault mirror does not silently skip.
- **`PUB-*` execution:** Start **PUB-0** charter or **PUB-1** manifest schema; **PUB-5** (Steemit identity matrix) in parallel with **PUB-3/4** (Dropbox / Google Drive inventory).
- **Handoff #24 carryover** (if still open): **AN1 + OGAN**, **OGSEC/OG-AUDIT/OG-DV** triage; **`npm run vault:sync`** when env is set — this session refreshed **Pending-Tasks** via explicit **`-HarnessRoot`** run.

## Paths / artifacts

| Area | Path |
|------|------|
| New backlog section | `MiscRepos/.cursor/state/pending_tasks.md` § **PENDING_GHOST_CANONICAL_PUBLISHING** |
| Sync script | `e:\local-proto\workspace\scripts\sync_harness_to_vault.ps1` (param **`-HarnessRoot`**) |
| Vault mirror | `Arc_Forge/ObsidianVault/Harness/Pending-Tasks.md` (and sibling Harness files) |

## dependency_links

- [pending_tasks.md](Harness/Pending-Tasks.md)

## open_risks

- Default harness root **`E:\local-proto`** ≠ MiscRepos → vault sync can **look** successful while state files were **skipped**.

## Decisions / gotchas

- Operator policy: **Ghost = canonical home** for published work; **PUB-*** rows encode syndication-only elsewhere.
- **Handoff SSOT:** `MiscRepos/.cursor/state/handoff_latest.md`; Obsidian **Harness/Handoff-Latest.md** is mirror after sync / int-vault-resync.

## Verification

- `powershell -NoProfile -ExecutionPolicy Bypass -File "e:\local-proto\workspace\scripts\sync_harness_to_vault.ps1" -HarnessRoot "C:\Users\Dell\Documents\GitHub\MiscRepos"` → **`[OK] …\Harness\Pending-Tasks.md`**
- Obsidian: **Harness/Pending-Tasks.md** includes **PENDING_GHOST_CANONICAL_PUBLISHING**.
