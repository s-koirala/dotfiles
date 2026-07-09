---
description: Run the audit-remediate loop on the current deliverable (up to 3 rounds).
argument-hint: "[target file/glob] (default: most recently modified non-test files in git diff)"
---

Invoke the `audit-remediate-loop` skill with:
- Target: $ARGUMENTS (if empty, infer the most recently modified non-test file set from git diff)
- Acceptance criteria: inherit from the task spec in the current conversation.
- Execution mechanism: per the skill — Workflow engine (`workflows/audit-remediate.js`) when the Workflow tool is available; parallel-Agent fallback otherwise.
- Auditor selection: defer to the skill's routing table (extensions + cwd globs + flags); do not hardcode a default set.
- Exit on zero critical+major findings surviving the refute gate OR after round 3.
- Emit the audit trail to `docs/audits/`.
