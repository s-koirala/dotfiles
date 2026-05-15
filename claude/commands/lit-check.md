---
description: Spawn the literature-check agent on the current artifact.
argument-hint: "[file/glob] (default: most recently modified .md/.ipynb/.py)"
---

Spawn `literature-check` on $ARGUMENTS (default: most recently modified .md / .ipynb / .py files in current project).

Return the JSON verdict. Block merge/publication on any `critical` or `major` finding.
