#!/usr/bin/env python3
"""SessionEnd hook: append a session summary under docs/audits/ in the project.

Captures session_id, reason (clear|logout|prompt_input_exit|other), cwd,
timestamp, git HEAD. Does not capture transcript content (that's in sessions/).
Creates docs/audits/ if the project already has a docs/ dir; silently skips
projects without docs/.

Concurrent same-day sessions append to the same file via text-mode 'a' open —
relies on OS append atomicity for entries < PIPE_BUF (each entry here is ~100
bytes, well under the 4KB POSIX and Windows thresholds).

Fail-open. Never blocks session shutdown.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], cwd: Path) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, timeout=5)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}

    proj = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
    docs = proj / "docs"
    if not docs.is_dir():
        return 0
    audits = docs / "audits"
    audits.mkdir(parents=True, exist_ok=True)

    now = dt.datetime.now()
    day = now.strftime("%Y-%m-%d")
    fname = audits / f"session_trail_{day}.md"

    head = run(["git", "rev-parse", "HEAD"], cwd=proj) or "(not a git repo)"
    entry = (
        f"- {now.isoformat(timespec='seconds')} | "
        f"session={str(payload.get('session_id', 'unknown'))[:12]} | "
        f"reason={payload.get('reason', 'unknown')} | "
        f"cwd={proj} | "
        f"git={head[:12]}\n"
    )
    try:
        with fname.open("a", encoding="utf-8") as f:
            f.write(entry)
    except Exception as e:
        print(f"session_end_audit_log: write failed: {e}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"session_end_audit_log: unhandled error: {e}", file=sys.stderr)
        sys.exit(0)
