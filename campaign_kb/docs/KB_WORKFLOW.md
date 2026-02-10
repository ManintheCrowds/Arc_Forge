<!--
# PURPOSE: Describe the KB ingest/search/merge workflow for campaign prep.
# DEPENDENCIES: None
# MODIFICATION NOTES: Initial KB workflow guide.
-->

# KB Workflow

## Ingest
1) PDFs: `POST /ingest/pdfs`
2) Seed docs: `POST /ingest/seeds`
3) DoD site: `POST /ingest/dod`
4) Local docs: `POST /ingest/docs`
5) Repos: `POST /ingest/repos`

## Search
Use `GET /search` during prep to find mechanics, lore, and hooks.

Example queries:
- `tier 2 requisition`
- `psychic corruption`
- `faction influence`
- `hive world hazards`

## Merge
Run `POST /merge` to generate a baseline merged seed doc at:
`D:/wrath_and_glory/output/campaign_seed_merged.md`

## Session Prep Loop
1) Pick next scene or mission
2) Search the KB for relevant rules/lore
3) Draft or update the related campaign files
4) Add citations to the section you used
