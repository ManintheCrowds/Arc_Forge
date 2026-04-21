---
title: "First run — OpenGrimoire intent + vault (operator checklist)"
tags: ["type/harness-doc", "status/mirror", "domain/harness"]
group: harness-docs
color: blue
cssclasses:
  - vault-grp-harness-docs
  - vault-col-blue
---

# First run — OpenGrimoire intent + vault (operator checklist)

Use this once per machine (or after resetting env). Canon: [INTENT_ELICITATION_AND_OG.md](./INTENT_ELICITATION_AND_OG.md).

1. **Set env** — [ENV_STANDARD.md](../../local-proto/docs/ENV_STANDARD.md): `OBSIDIAN_VAULT_ROOT`, `OPENGRIMOIRE_BASE_URL`, optional `OPENGRIMOIRE_FALLBACK_URL`, `OPENGRIMOIRE_API_TOKEN` (never commit).
2. **Complete the big interview** in the OpenGrimoire UI (survey / wizard).
3. **Run the bridge** — from MiscRepos root: `python local-proto/scripts/export_opengrimoire_to_vault.py --dry-run` then without `--dry-run`. Optional: set `OPENGRIMOIRE_EXPORT_JSON` to a JSON file for the first `OG-Snapshot-*.md` body.
4. **Copy vault template** — [Interview-Archive-README.md](../vault-templates/Interview-Archive-README.md) into your vault under `Interview-Archive/README.md` if missing.
5. **Handoff / session** — paste OG pointers (`survey_response_id`, URL, `last_elicitation_utc`) per [SESSION_MESSAGE_TEMPLATE.md](../../.cursor/docs/SESSION_MESSAGE_TEMPLATE.md); confirm `.cursor/state/og_intent_excerpt.md` exists and `stale: false` after a healthy run.
6. **Sync harness mirror** — `local-proto/scripts/sync_harness_to_vault.ps1` so `Harness/Docs/Intent-Elicitation-And-OG.md` appears in Obsidian.
