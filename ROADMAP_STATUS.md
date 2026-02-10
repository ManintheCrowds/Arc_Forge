# Roadmap and verification status

**Updated:** 2025-02-10 (after Arc Forge rename, root .gitignore, README updates; repo folder relabel: use **Arc_Forge**; rename `wrath_and_glory` → `Arc_Forge` on disk if needed)

## Last test run

Unified test run from repo root (`.\scripts\run_tests.ps1`):

| Suite              | Result              | Notes   |
|--------------------|---------------------|--------|
| campaign_kb        | 12 passed           | 7 deprecation warnings |
| workflow_ui        | 45 passed, 1 skipped| OK     |
| ObsidianVault scripts | 273 passed, 9 skipped | OK  |

**Overall:** All suites passed. Prerequisites: pytest, Python 3.x; run from `arc_forge` root.

## Grading (plan rubric)

| Area                   | Pass? | Notes |
|------------------------|-------|--------|
| A. Product clarity      | Yes   | README: Arc Forge, purpose, "what this is" |
| B. IP hygiene          | Yes   | Root .gitignore: PDFs, PCs/, temp_pdfs/, ObsidianVault/pdf/, Sources/_summaries/, Sources/_extracted_text/ |
| C. Feature completeness| Yes   | Wave A/B/C done; S1–S5 pipeline, RAG, Archivist/Foreshadow |
| D. Quality and ops     | Yes   | Three test suites run; README links to testing, manual I/O checklist, /docs |
| E. Improvements backlog| Yes   | DEVELOPMENT_PLAN_REMAINING.md with "Done when" |

**Target:** Shareable (A–E pass). Next: P2 improvements (in-context help, checklist alignment) or P3 (E2E, path traversal, rate-limit docs) as needed.

## Next

- Optional: Apply P2 from plan (in-context help on S1–S5 panels, manual I/O checklist alignment).
- Re-run tests after env or code changes and update this file.
