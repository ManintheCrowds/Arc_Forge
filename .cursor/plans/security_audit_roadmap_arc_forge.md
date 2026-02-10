# Security Audit Roadmap — Arc Forge

## Repository
- **Path:** D:/arc_forge
- **Primary stack:** Python, docs, Obsidian vault assets
- **Data tier (initial):** internal
- **Notes:** Contains campaign_kb and workflow_ui; has GitHub workflow for tests only.

## Phased roadmap (0–5)
### Phase0_TriageAndScope
- **Goal:** Run initial scan focused on code paths (campaign_kb/workflow_ui).
- **Effort:** 0.5–1 day
- **Blast radius:** low

### Phase1_MetadataAndPolicy_Soft
- **Goal:** Add `project-metadata.yml` per subproject and non-blocking checks.
- **Effort:** 1–2 days
- **Blast radius:** low-medium

### Phase2_SecretsAndDependabot
- **Goal:** Add secrets scanning + Dependabot for Python deps.
- **Effort:** 1–2 days
- **Blast radius:** medium

### Phase3_CodeQL
- **Goal:** Enable CodeQL for Python.
- **Effort:** 1–2 days
- **Blast radius:** medium

### Phase4_RemediationSprint
- **Goal:** Clean up true positives and sensitive config in workflows.
- **Effort:** 2–5 days
- **Blast radius:** medium

### Phase5_GovernanceHardening
- **Goal:** Enforce blocking checks for main merges.
- **Effort:** 1 day
- **Blast radius:** medium
