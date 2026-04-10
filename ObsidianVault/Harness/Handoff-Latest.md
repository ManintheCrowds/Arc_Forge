---
title: "Handoff #5: AGA GPU archive lands in local-proto"
tags: ["type/harness-state", "status/mirror", "domain/harness"]
---

# Handoff #5: AGA GPU archive lands in local-proto

decision_id: handoff-2026-04-09-aga-gpu-archive
supersedes: handoff-2026-04-09-obsidian-github-gap-analysis
Updated: 2026-04-09T12:00:00Z
Session: local-proto AGA GPU documentation

## Context

Prior thread analyzed [Dell KB 000178406](https://www.dell.com/support/kbdoc/en-us/000178406/alienware-graphics-amplifier-supported-graphics-card-list) for Alienware Graphics Amplifier GPU tiers; this session archived that analysis into the repo and wired Obsidian/private mirror paths.

## Done

- Added **`local-proto/docs/AGA_GPU_UPGRADE_ARCHIVE.md`** — Dell link, AGA size/power limits, NVIDIA/AMD tiers, ideal picks (2080 Ti / 2070–2080 / 1080 Ti / RX 580), local inference tie-in, changelog, mirroring instructions.
- Linked from **`local-proto/docs/HARDWARE.md`** (Alpha R2 + AGA bullet) and **`local-proto/docs/ALPHA_R2_AGA_SETUP.md`** (references).
- Extended **`local-proto/scripts/sync_harness_to_vault.ps1`** — maps archive → **`Harness/Docs/AGA-GPU-Upgrade-Archive.md`** in the Obsidian vault when sync runs.
- **`MiscRepos/.gitignore`** — `local-proto/docs/private/` for optional git-ignored copies/symlinks.

## Next

**Operator:** Run harness→vault sync so Obsidian picks up the new doc (and other mapped files):

```powershell
cd <MiscRepos>
$env:OBSIDIAN_VAULT_ROOT = "D:\Arc_Forge\ObsidianVault"  # adjust; must sit under VAULT_SYNC_SAFE_BASE unless overridden
.\local-proto\scripts\sync_harness_to_vault.ps1
```

Optional: create `local-proto/docs/private/` and copy or symlink `AGA_GPU_UPGRADE_ARCHIVE.md` there for a non-committed duplicate.

## Paths / artifacts

| Path | Role |
|------|------|
| `local-proto/docs/AGA_GPU_UPGRADE_ARCHIVE.md` | Canonical archive |
| `local-proto/docs/HARDWARE.md` | Link under Alpha R2 + AGA |
| `local-proto/docs/ALPHA_R2_AGA_SETUP.md` | GPU selection reference |
| `local-proto/scripts/sync_harness_to_vault.ps1` | `docMappings` entry for AGA doc |
| `MiscRepos/.gitignore` | `local-proto/docs/private/` |

## dependency_links

- `local-proto/docs/AGA_GPU_UPGRADE_ARCHIVE.md`
- `local-proto/docs/OBSIDIAN_GITHUB_GAP_ANALYSIS.md` (related vault/GitHub context if continuing Obsidian work)

## open_risks

- Vault sync requires `OBSIDIAN_VAULT_ROOT` and path under safe base; script errors if unset.
- Newer GPUs (RTX 30/40) are not on Dell’s list — noted in archive; operator risk if experimenting.

## Decisions / gotchas

- **`/brainstorm` Cursor command** is deprecated; prefer superpowers brainstorming skill for structured ideation (mentioned in prior thread only — not codified in repo).

## Verification

- **Session type:** documentation and config only. **Tests/build:** not run (no code change requiring CI).

## Assumptions

- Repo root for scripts is **`MiscRepos`** (parent of `local-proto`).
## Vault navigation

**Daily log:** [[Harness/Daily/2026-04-09]]
**Handoff chain:** [[Harness/MOC_Harness_State]]
**Decision index:** [[Harness/Decision-Index]]
**Supersedes:** [[Harness/Handoff-archive/20260409-231452.md]]
