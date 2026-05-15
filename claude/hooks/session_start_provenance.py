#!/usr/bin/env python3
"""SessionStart hook: emit git/env/data provenance into additionalContext.

Uses the project's venv interpreter (not the one running this hook) so reported
deps match what the project will actually run. Skips pip freeze entirely if no
Python project markers are present. Caches deps-sha per-day in
~/.claude/cache/deps_{sha1(project_path)}_{YYYY-MM-DD} to avoid repeated
pip-freeze cost on the same day.

Fails open — never blocks a session on hook error.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
from pathlib import Path

CACHE_DIR = Path.home() / ".claude" / "cache"
PROJECT_MARKERS = ("pyproject.toml", "requirements.txt", "uv.lock", "poetry.lock", "Pipfile.lock")


def run(cmd: list[str], cwd: Path | None = None, timeout: int = 5) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, timeout=timeout)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


def short_digest(text: str, n: int = 12) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:n] if text else ""


def find_project_python(proj: Path) -> str | None:
    if platform.system() == "Windows":
        cand = [proj / ".venv" / "Scripts" / "python.exe", proj / "venv" / "Scripts" / "python.exe"]
    else:
        cand = [proj / ".venv" / "bin" / "python", proj / "venv" / "bin" / "python"]
    for p in cand:
        if p.exists():
            return str(p)
    return None


def is_python_project(proj: Path) -> bool:
    return any((proj / m).exists() for m in PROJECT_MARKERS)


def deps_sha(proj: Path) -> tuple[str, int] | None:
    """Return (sha, n_pkgs) for the project's deps. Cache keyed on lockfile mtimes
    so `uv add` / `pip install` invalidates the cache immediately."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    lock_sig_parts: list[str] = []
    for m in PROJECT_MARKERS:
        p = proj / m
        if p.exists():
            try:
                lock_sig_parts.append(f"{m}:{p.stat().st_mtime_ns}")
            except Exception:
                pass
    lock_sig = "|".join(lock_sig_parts) or "no-lock"
    key = hashlib.sha1((str(proj.resolve()) + "::" + lock_sig).encode()).hexdigest()[:16]
    cache_file = CACHE_DIR / f"deps_{key}.json"
    if cache_file.exists():
        try:
            d = json.loads(cache_file.read_text())
            return d["sha"], d["n"]
        except Exception:
            pass

    py = find_project_python(proj)
    if py:
        freeze = run([py, "-m", "pip", "freeze"], timeout=15)
    elif (proj / "uv.lock").exists() and os.environ.get("PATH"):
        freeze = run(["uv", "pip", "freeze"], cwd=proj, timeout=15)
    else:
        return None
    if not freeze:
        return None
    sha = short_digest(freeze)
    n = freeze.count("\n") + 1
    try:
        cache_file.write_text(json.dumps({"sha": sha, "n": n}))
    except Exception:
        pass
    return sha, n


def main() -> int:
    proj = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
    parts: list[str] = []

    head = run(["git", "rev-parse", "HEAD"], cwd=proj)
    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=proj)
    dirty = run(["git", "status", "--porcelain"], cwd=proj)
    if head:
        parts.append(f"git: {head[:12]} ({branch}){' [DIRTY]' if dirty else ''}")

    if is_python_project(proj):
        res = deps_sha(proj)
        if res:
            parts.append(f"deps-sha: {res[0]} ({res[1]} pkgs)")

    data_dir = proj / "data"
    if data_dir.is_dir():
        files = sorted(p for p in data_dir.rglob("*") if p.is_file())[:50]
        if files:
            h = hashlib.sha256()
            for f in files:
                try:
                    h.update(f.name.encode())
                    h.update(str(f.stat().st_size).encode())
                except Exception:
                    pass
            parts.append(f"data/: {len(files)} files, manifest-sha: {h.hexdigest()[:12]}")

    if not parts:
        return 0

    ctx = "PROVENANCE | " + " | ".join(parts)
    print(
        json.dumps(
            {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": ctx}}
        )
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"session_start_provenance: unhandled error: {e}", file=sys.stderr)
        sys.exit(0)
