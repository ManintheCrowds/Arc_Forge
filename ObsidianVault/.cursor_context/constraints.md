# Arc_Forge / Obsidian Vault Constraints

Claw.md-style constraint document for AI agents working in this vault. Every line should earn its place.

## Musts

- Run pytest before marking Daggr changes done.
- Use workflows.md paths and naming for workflow outputs.

## Must-nots

- Do not modify campaign_kb ingest schema without approval.
- Do not replace existing notes destructively unless explicitly approved via apply_patch.

## Preferences

- Prefer PowerShell on Windows.
- Prefer append-only for existing notes (add timestamped entry blocks).

## Escalation triggers

- Before changing auth or RAG pipeline.
- Before modifying .cursor_context structure.
