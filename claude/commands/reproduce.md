---
description: Spawn the reproducibility-verifier agent against the current project.
argument-hint: "[project root] (default: current cwd)"
---

Spawn the `reproducibility-verifier` agent against $ARGUMENTS (default: current project root).

Brief it with:
- Project root path
- Any declared entrypoint (Makefile, nox, Justfile, package.json scripts)
- The expected runtime (quick smoke vs full reproduction)

Return its JSON verdict verbatim, then propose remediation commits for any `fail` or `partial` checks.
