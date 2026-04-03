# Workspace MCP registry (stub)

**Owning repo:** Arc_Forge (portfolio / campaign workbench).  
**Purpose:** Phase **P1.2** — single place that points to **which MCP servers** this multi-root workspace expects and where the **canonical capability map** lives in the sibling **MiscRepos** clone.

This file is **not** a generated inventory of your live Cursor `mcp.json`. Update it when you intentionally add or remove a server family from the workspace.

## Canonical capability map

| Resource | Path (sibling repos under your GitHub folder) |
|----------|-----------------------------------------------|
| MCP tools × harness scripts | [`../../MiscRepos/.cursor/docs/MCP_CAPABILITY_MAP.md`](../../MiscRepos/.cursor/docs/MCP_CAPABILITY_MAP.md) |
| OpenGrimoire HTTP + MCP tiers (unified manifest) | [`../../OpenGrimoire/docs/AGENT_TOOL_MANIFEST.md`](../../OpenGrimoire/docs/AGENT_TOOL_MANIFEST.md) |

If **MiscRepos** or **OpenGrimoire** are not cloned next to Arc_Forge, clone them or adjust paths in your editor; links above assume `Documents/GitHub/{Arc_Forge,MiscRepos,OpenGrimoire}` (legacy folder name `OpenGrimoire` still works until you rename).

## Enabled servers (example set)

Replace with your actual `mcp.json` names. Typical families in this workspace:

| Server (example) | Role |
|------------------|------|
| `project-1-MiscRepos-*` | Git, Docker, SQLite, Playwright, Daggr, etc. (see map) |
| Cursor bundled | `cursor-ide-browser`, filesystem, codebase tools |

**Policy:** Enable **least privilege** — only servers needed for the current workflow ([MiscRepos MCP_CAPABILITY_MAP.md](../../MiscRepos/.cursor/docs/MCP_CAPABILITY_MAP.md) § maintenance).

## Related

- OpenGrimoire integration entry: [`../../OpenGrimoire/docs/AGENT_INTEGRATION.md`](../../OpenGrimoire/docs/AGENT_INTEGRATION.md)
- Canonical naming: [OpenGrimoire `docs/engineering/OPENGRIMOIRE_NAMING_AND_URLS.md`](../../OpenGrimoire/docs/engineering/OPENGRIMOIRE_NAMING_AND_URLS.md)
