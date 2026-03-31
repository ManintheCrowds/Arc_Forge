# Primitives vs workflows (workflow_ui)

| Kind | Examples | Notes |
|------|------------|--------|
| **Primitive** | `GET /api/modules/.../file`, `GET /api/arc/.../tree`, `GET /api/kb/search`, `GET /api/status`, `GET /openapi.json` | Thin read/list/search; composable. |
| **Workflow** | `POST /api/run/stage1`–`stage5`, `POST /api/session/archivist`, `POST /api/session/foreshadow` | Multi-step storyboard/session pipelines. |
| **Hybrid** | `POST /api/workbench/chat` | LLM call with optional file context + structured fields. |

Refactors that split shared file I/O into a small module are optional; this table is the source of truth for v1.
