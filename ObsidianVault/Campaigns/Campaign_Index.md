<!--
# PURPOSE: Index of campaigns and their key notes.
# DEPENDENCIES: Dataview plugin (optional) for auto-listing.
# MODIFICATION NOTES: Initial campaign index.
-->

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
