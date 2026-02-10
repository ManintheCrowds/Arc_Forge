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
