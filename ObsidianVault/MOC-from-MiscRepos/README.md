# Vault MOC templates (operator copy)

These files are **not** synced into `Harness/` automatically. They are **templates** for your Obsidian or Foam vault.

## How to use

1. Copy the desired `.md` file into your vault root (or `Notes/`, `MOC/`, etc.).
2. After [sync_harness_to_vault.ps1](../../local-proto/scripts/sync_harness_to_vault.ps1), adjust wikilinks so they resolve in your vault (paths differ per machine).
3. Prefer keeping MOC notes **outside** paths that agents overwrite on every sync. See [OBSIDIAN_VAULT_INTEGRATION.md](../../.cursor/docs/OBSIDIAN_VAULT_INTEGRATION.md) § Graph and organization.

## Files

| Template | Purpose |
|----------|---------|
| [MOC_Bitcoin_Agents.md](MOC_Bitcoin_Agents.md) | Hub for Bitcoin + agent publishing stack (Voelbel, Ghost, harness mirror). |
| [MOC_People.md](MOC_People.md) | Short people / collaborators index; link out to repo docs or `Harness/Docs/`. |
| [Interview-Archive-README.md](Interview-Archive-README.md) | Copy into vault **`Interview-Archive/`** (outside `Harness/`): OG snapshot exports, `REVOKED-*.md` tombstones, human `Notes-*.md`. See [INTENT_ELICITATION_AND_OG.md](../agent/INTENT_ELICITATION_AND_OG.md). |
