---
title: "GHOST1 — close out task in software repo"
tags: ["type/harness-doc", "status/mirror", "domain/harness"]
group: harness-docs
color: blue
cssclasses:
  - vault-grp-harness-docs
  - vault-col-blue
---

# GHOST1 — close out task in software repo

Run this **only after** [GHOST1_RUNBOOK.md](../GHOST1_RUNBOOK.md) **§Verification** is satisfied on a real Ghost instance.

## 1. Edit software pending tasks

File: `software/.cursor/state/pending_tasks.md` (path relative to your `software` clone).

1. Set **Last updated** to today’s date (header under `# Pending Tasks`).
2. In the GHOST1 row, change `in_progress` to `done` in the **Status** column.

Example (adjust spacing to match the table):

```markdown
| GHOST1 | done | Stand up a **Ghost-powered** personal or project site | ... |
```

Keep the **Notes** column as-is (links remain useful).

## 2. Optional

- If you track the same task in MiscRepos `.cursor/state/pending_tasks.md`, add or update a row there only if you use that file for site work; GHOST1 SSOT for the software clone is `software/.cursor/state/pending_tasks.md`.

## 3. Do not

- Mark **done** before HTTPS + test post + API draft create/delete + backups are verified.
- Commit Ghost Admin keys or `.env` secrets.
