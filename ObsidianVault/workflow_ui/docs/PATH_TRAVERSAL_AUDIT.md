# Path-traversal audit: `/api/arc/<id>/file/<subpath>`

## Scope

- **Route**: `GET /api/arc/<arc_id>/file/<path:subpath>` in [app.py](../app.py) (`api_arc_file`).
- **Purpose**: Serve file contents under `Campaigns/<arc_id>/` so the UI can display task_decomposition, feedback, encounter drafts, etc.

## Current controls

1. **arc_id**: Sanitized with `werkzeug.utils.secure_filename(arc_id)`; if result is empty, fallback to `"first_arc"`. This prevents using `arc_id` to inject path segments (e.g. `../../../etc/passwd` is stripped to empty and becomes `first_arc`).

2. **subpath** (literal check): Rejected with 400 if it contains `..`, or starts with `/`, or contains `\`. So direct traversal and absolute or Windows-style segments are blocked before path resolution.

3. **Resolution and containment**: `full = (base / subpath).resolve()` and `base_res = base.resolve()`. Response is 404 if `not full.is_file()` or `base_res not in full.parents`. So even if some bypass of the literal check were possible, the resolved path must be a file under the arc directory.

## Risks considered

| Risk | Mitigation | Residual |
|------|------------|----------|
| URL-encoded traversal (e.g. `%2e%2e/`) | Flask/Werkzeug decode the URL before the view; the decoded `subpath` is what we check. So `%2e%2e/` becomes `../` and is rejected by the `".." in subpath` check. | None if framework decoding is always applied; test with encoded traversal to lock behavior. |
| arc_id as traversal | `secure_filename` removes path separators and dangerous segments; empty falls back to `first_arc`. | None for path traversal via arc_id. |
| Symlinks under CAMPAIGNS | `Path.resolve()` follows symlinks. A file under `Campaigns/arc_a/` that is a symlink to a file outside CAMPAIGNS can yield `full` outside `base_res`. Our check `base_res not in full.parents` uses resolved paths: if the symlink target is outside the arc, `full.parents` does not contain `base_res`, so we return 404. So we do not serve content outside the resolved arc root. However, a symlink *inside* the arc that points to another file *inside* the arc is allowed (normal). A symlink inside the arc pointing *outside*: resolved path would be outside, so `base_res not in full.parents` → 404. So current logic is safe. | Acceptable: we do not follow symlinks to serve content outside the arc. If the deployment requires no symlinks under CAMPAIGNS at all, document that or add an explicit “no symlink” walk. |
| Redundant segments (e.g. `foo/../foo.md`) | Allowed; resolved to a file under the arc. No security issue. | None. |

## Conclusion

- Path traversal via `subpath` or `arc_id` is blocked by literal checks and containment after resolution.
- URL-encoded `..` is decoded by the framework and then rejected; add a test to lock this.
- Symlinks: resolved path must remain under the arc; otherwise 404. No change required unless policy is to disallow any symlinks under CAMPAIGNS.

## Related

- `/api/session/file/<path:subpath>` uses a different strategy: only the final path component (filename) is used via `secure_filename(Path(subpath).name)`, and the file must be under `Campaigns/_session_memory`. So traversal there is not possible.

---

## Workbench chat `context_path`

### Scope

- **Route**: `POST /api/workbench/chat` in [app.py](../app.py) (`api_workbench_chat`).
- **Purpose**: Send a message to the LLM (Ollama) with optional file context. `context_path` is a path relative to CAMPAIGNS (e.g. `first_arc/module/note.md`).

### Current controls

1. **Literal check**: If `context_path` contains `..`, starts with `/`, or contains `\`, it is rejected by skipping the file read entirely. `context_text` stays empty; the chat proceeds without that file.

2. **Containment**: After resolving, `base_res = CAMPAIGNS.resolve()` and `full = (base_res / context_path).resolve()`. We only read if `base_res in full.parents or full == base_res` and `full.is_file()`.

3. **Result**: Traversal attempts (e.g. `../leak.txt`) result in no file being read; the prompt is built from the message only. No error is returned; the chat succeeds.

### Tests

- `test_workbench_chat_context_path_traversal_rejected`: POST with `context_path="../leak.txt"` where `leak.txt` exists outside CAMPAIGNS. Asserts 200, and that the prompt sent to Ollama does not contain the leaked content.

---

## Workbench create-module

### Scope

- **Route**: `POST /api/workbench/create-module` in [app.py](../app.py) (`api_workbench_create_module`).
- **Purpose**: Create `Campaigns/{campaign}/{module}/` with stub files.

### Current controls

1. **Input sanitization**: `campaign` and `module` are passed through `secure_filename()`; names starting with `_` are rejected with 400.

2. **Containment**: Before `root.mkdir()`, we call `root.resolve().relative_to(CAMPAIGNS.resolve())`. If `ValueError` (path outside CAMPAIGNS), return 400.

3. **Result**: Traversal via `campaign=".."` or `module=".."` is neutralized by `secure_filename` (which strips path separators and dangerous segments; `..` becomes empty). Empty campaign/module fails the required-field check. Any remaining edge case would fail the `relative_to` check.

### Tests

- `test_workbench_create_module_traversal_rejected`: POST with `campaign=".."`, `module="x"` → 400.
- `test_workbench_create_module_path_containment`: POST with valid `campaign="safe"`, `module="mod"` → 200, directory created under CAMPAIGNS.
