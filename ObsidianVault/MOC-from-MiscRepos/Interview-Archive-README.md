# Interview-Archive (operator copy into vault)

_Copy this file into your Obsidian vault as e.g. `Interview-Archive/README.md` (or keep as a note at vault root). It is **not** mirrored from `Harness/`._

## Purpose

- **`OG-Snapshot-*.md`** — immutable markdown exports from **OpenGrimoire** (via [`export_opengrimoire_to_vault.py`](../../local-proto/scripts/export_opengrimoire_to_vault.py) or manual paste). **Do not edit** snapshot bodies as SSOT; OG remains canonical.
- **`REVOKED-<responseId>.md`** — tombstones when OG marks a response revoked (written by the bridge when the [revoked-ids API](../../../OpenGrimoire/docs/agent/ELICITATION_EXPORT_CONTRACT.md) or manual list is available).
- **`Notes-*.md`** — your overlays, wikilinks, and clarifications. On multi-device sync, **Obsidian / sync tool wins**; resolve duplicate conflict files manually if they appear.

## Naming

- Snapshots: `OG-Snapshot-<UTC>-<responseOrSessionId>.md` (example: `OG-Snapshot-2026-04-15T143022Z-abc123.md`).
- One tombstone per id: `REVOKED-<responseId>.md`.

## Links

- Operator protocol: [INTENT_ELICITATION_AND_OG.md](../agent/INTENT_ELICITATION_AND_OG.md) (MiscRepos).
- Harness mirror (automation state): `[[Harness/Handoff-Latest]]` or path links after [sync](../../local-proto/scripts/sync_harness_to_vault.ps1).

## Hygiene

- **Single machine** runs the export bridge; other devices consume this folder via **cloud sync**.
- **Retention:** keep snapshots unless you must delete for legal reasons; tombstones document OG-side revocation without silently erasing history.
