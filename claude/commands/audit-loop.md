---
description: Run the audit-remediate loop on the current deliverable (up to 3 rounds).
argument-hint: "[target file/glob] (default: most recently modified non-test files in git diff)"
---

Invoke the `audit-remediate-loop` skill with:
- Target: $ARGUMENTS (if empty, infer the most recently modified non-test file set from git diff)
- Acceptance criteria: inherit from the task spec in the current conversation.
- Auditor selection: default to running `quant-auditor`, `literature-check`, and `reproducibility-verifier` in parallel on round 1.
- Exit on zero critical+major findings OR after round 3.
- Emit the audit trail to `docs/audits/`.
