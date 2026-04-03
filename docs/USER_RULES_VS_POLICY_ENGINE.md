# User rules vs automated policy (workspace reminder)

**Purpose:** Phase **P2.2** — short note so contributors do not assume **Cursor user rules** or **agent-intent** copy alone enforce security or correctness.

## What user rules are

**User rules** (and similar editor-injected instructions) shape **model behavior** in-session. They are **not** a substitute for:

- CI (`npm run verify`, linters, tests)
- Pre-commit hooks (checksum, sanitization) in **MiscRepos**
- Repository **branch protection** and **code review**

## Where enforcement actually lives

| Concern | Typical location |
|---------|------------------|
| OpenGrimoire API contract | [CONTRIBUTING.md](../../OpenGrimoire/CONTRIBUTING.md), `verify:capabilities` |
| Harness scripts / rules integrity | MiscRepos `.cursor/scripts`, `checksum_integrity` |
| Intent and escalation policy | [MiscRepos `.cursor/rules/agent-intent.mdc`](../../MiscRepos/.cursor/rules/agent-intent.mdc) (conceptual; still not automated law) |

## Takeaway

**Rules in the prompt reduce drift; they do not replace verification.** For agent-harness work, align PRs with [OpenGrimoire CONTRIBUTING — agent harness](../../OpenGrimoire/CONTRIBUTING.md) and the improvement program linked there.
