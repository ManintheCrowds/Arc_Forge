# Workflow Write Contract

This document defines write targets and templates for workflow automations.

## Paths and naming

- Daily summary:
  - Path: `Workflows/Daily/<YYYY-MM-DD>.md`
  - Example: `Workflows/Daily/2026-02-07.md`
- Session log:
  - Path: `Workflows/Sessions/<Session_ID>.md`
  - Example: `Workflows/Sessions/Session_12.md`
- Incident report:
  - Path: `Workflows/Incidents/<INC-YYYY-MM-DD-NNN>.md`
  - Example: `Workflows/Incidents/INC-2026-02-07-001.md`

## Required sections (create on first write)

### Daily summary

- Title: `# Daily Summary - <YYYY-MM-DD>`
- Sections:
  - `## Highlights`
  - `## Blockers`
  - `## Next Steps`
  - `## Links`

### Session log

- Title: `# Session Log - <Session_ID>`
- Sections:
  - `## Agenda`
  - `## Decisions`
  - `## Action Items`
  - `## Links`

### Incident report

- Title: `# Incident Report - <INC-ID>`
- Sections:
  - `## Summary`
  - `## Impact`
  - `## Timeline`
  - `## Root Cause`
  - `## Resolution`
  - `## Follow-ups`

## Allowed operations

- Append-only for existing notes (adds a timestamped entry block).
- Create new note if missing using the required sections.
- No destructive replacements unless explicitly approved via `apply_patch`.
