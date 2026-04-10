<!--
# PURPOSE: Index of campaigns and their key notes.
# DEPENDENCIES: Dataview plugin (optional) for auto-listing.
# MODIFICATION NOTES: Initial campaign index.
-->

---
title: "Campaign Index"
tags: ["type/campaign", "status/draft", "campaign/redacted_records"]
---

# Campaign Index

## Campaigns

```dataview
TABLE file.link AS Campaign, file.mtime AS Updated
FROM "Campaigns"
WHERE contains(tags, "type/campaign")
  AND file.name != "DM_Dashboard"
  AND file.name != "Campaign_Index"
SORT file.name ASC
```

## Quick Links

- [[DM_Dashboard]]
- [[Campaigns/README_workflow]] — storyboard → encounter pipeline (RAG output dir: `_rag_outputs/`)
- [[Campaigns/_rag_outputs/MOC_RAG_Outputs]] — index of frame/RAG generated notes (staging)
