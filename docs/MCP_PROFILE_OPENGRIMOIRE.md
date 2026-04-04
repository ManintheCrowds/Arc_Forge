# Minimal MCP profile — OpenGrimoire work

**Owning repo:** Arc_Forge (workspace documentation).  
**Purpose:** Phase **P8.1** — smallest useful MCP server set when **primary work** is OpenGrimoire (REST contract, Next.js app, `npm run verify`), versus a **full portfolio** workspace with Daggr, Fish Speech, etc.

**Normative inventories:** Unified HTTP + MCP tiers — [OpenGrimoire `docs/AGENT_TOOL_MANIFEST.md`](../../OpenGrimoire/docs/AGENT_TOOL_MANIFEST.md). Per-tool harness detail — [MiscRepos `.cursor/docs/MCP_CAPABILITY_MAP.md`](../../MiscRepos/.cursor/docs/MCP_CAPABILITY_MAP.md). Enabled-server stub — [WORKSPACE_MCP_REGISTRY.md](./WORKSPACE_MCP_REGISTRY.md).

## Include (typical)

| Server / tool family | Rationale |
|---------------------|-----------|
| **Cursor defaults** (filesystem, codebase search, built-in terminal guidance) | Read and edit OpenGrimoire sources without extra MCP. |
| **Git** (`project-1-MiscRepos-git` or equivalent) | Optional but useful for status/diff/log when not using only IDE UI. |
| **Playwright** | Only when running or debugging **E2E** (`npm run verify:e2e` / Playwright flows). |

## Exclude unless needed

| Server / tool family | Rationale |
|---------------------|-----------|
| **Docker** | Only if the task changes `Dockerfile` / `docker-compose` or container debugging. |
| **SQLite / Daggr / Scrapling / …** | Portfolio harness servers; add back when the task touches those domains ([MCP_CAPABILITY_MAP.md](../../MiscRepos/.cursor/docs/MCP_CAPABILITY_MAP.md) § maintenance / least privilege). |
| **Extra browser / crawl MCP** | Prefer Cursor browser or repo scripts unless integrating a specific external stack. |

**Policy:** Optional OpenGrimoire MCP servers (if you add any) must remain **thin wrappers** over existing HTTP/CLI — see [OpenGrimoire `docs/AGENT_INTEGRATION.md`](../../OpenGrimoire/docs/AGENT_INTEGRATION.md) § Harness integration paths and optional thin MCP.
