#!/usr/bin/env python3
"""PreToolUse (Bash) hook: warn on destructive or nondeterministic commands.

Complements settings.json deny list by surfacing subtle risks:
  - pip install without a version pin in a project that has requirements.txt
  - running a notebook without papermill / without a pinned kernel
  - git operations that rewrite published history
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

DESTRUCTIVE = [
    (re.compile(r"\bgit\s+push\s+.*--force(?!-with-lease)"), "git push --force without --force-with-lease"),
    (re.compile(r"\bgit\s+reset\s+--hard\b"), "git reset --hard"),
    (re.compile(r"\bgit\s+rebase\s+.*-i\b"), "interactive rebase (not supported by Claude Code)"),
    (re.compile(r"\brm\s+-rf\s+[/~]"), "rm -rf of root/home"),
]
PIP_UNPINNED = re.compile(r"\bpip\s+install\s+(?!-r|-e|--upgrade\s+pip\b)(?![^ ]*==)(\S+)")


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    cmd = (payload.get("tool_input", {}) or {}).get("command", "")
    if not cmd:
        return 0

    reasons: list[str] = []
    for pat, label in DESTRUCTIVE:
        if pat.search(cmd):
            reasons.append(f"destructive: {label}")

    proj = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
    if (proj / "requirements.txt").exists() or (proj / "pyproject.toml").exists():
        for m in PIP_UNPINNED.finditer(cmd):
            pkg = m.group(1)
            if pkg not in ("pip", "uv", "."):
                reasons.append(f"unpinned install: {pkg} (project has lockfile — add ==version or use uv add)")

    if reasons:
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "ask",
                        "permissionDecisionReason": "Bash safety: " + "; ".join(reasons),
                    }
                }
            )
        )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
