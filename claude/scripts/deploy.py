#!/usr/bin/env python3
"""Deploy ~/dotfiles/claude/ → ~/.claude/ on any machine (Windows / macOS / Linux).

Idempotent. Backs up anything it would overwrite to ~/.claude/backups/{YYYY-MM-DDTHHMMSS}/.
Managed directories are mirrored (orphans removed). Never touches machine-local state:
settings.local.json, .credentials.json, sessions/, projects/, memory/, ide/, plugins/,
shell-snapshots/, statsig/, telemetry/, todos/, debug/, file-history/, backups/.

settings.json is deployed with shell-agnostic {{CLAUDE_HOME}} placeholders rewritten
to the absolute deployed path (fixes Windows cmd/PowerShell $HOME expansion failures).

Usage:
    python deploy.py            # copy (safe default)
    python deploy.py --symlink  # symlink (requires Windows Developer Mode or admin)
    python deploy.py --check    # diff-only, no changes
    python deploy.py --init-local  # scaffold settings.local.json if missing
"""
from __future__ import annotations

import argparse
import datetime as dt
import filecmp
import json
import os
import platform
import shutil
import sys
import tempfile
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent  # ~/dotfiles/claude
DEST = Path.home() / ".claude"

MANAGED_DIRS = ["agents", "skills", "commands", "rules", "hooks", "workflows"]
MANAGED_FILES = ["CLAUDE.md"]  # settings.json handled specially
SPECIAL_FILES = ["settings.json"]

PROTECTED = {
    ".credentials.json", "settings.local.json", "sessions", "projects",
    "ide", "shell-snapshots", "statsig", "telemetry", "stats-cache.json",
    "mcp-needs-auth-cache.json", "file-history", "debug", "backups", "todos",
    "plugins", "memory",
}

LOCAL_TEMPLATE = {
    "env": {},
    "_comment": (
        "Machine-local overrides. Not tracked in dotfiles. "
        "Configure apiKeyHelper here pointing to an OS-keychain script; "
        "never put API keys directly in env. "
        "Add a 'permissions' key only if you need to override the user-level allow/deny/ask lists — "
        "scaffolding it empty silently replaces the global lists."
    ),
}


def backup(path: Path, stamp: str) -> None:
    if not path.exists():
        return
    dest = DEST / "backups" / stamp / path.relative_to(DEST)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if path.is_dir() and not path.is_symlink():
        shutil.copytree(path, dest, dirs_exist_ok=True, symlinks=True)
    else:
        shutil.copy2(path, dest, follow_symlinks=False)


def dirs_differ(a: Path, b: Path) -> tuple[bool, list[str]]:
    a_files = {str(p.relative_to(a)): p for p in a.rglob("*") if p.is_file()}
    b_files = {str(p.relative_to(b)): p for p in b.rglob("*") if p.is_file()}
    added = sorted(set(a_files) - set(b_files))
    removed = sorted(set(b_files) - set(a_files))
    modified = [
        rel for rel in a_files if rel in b_files and not filecmp.cmp(a_files[rel], b_files[rel], shallow=False)
    ]
    diff_summary = []
    if added:
        diff_summary.append(f"+{len(added)}")
    if removed:
        diff_summary.append(f"-{len(removed)}")
    if modified:
        diff_summary.append(f"~{len(modified)}")
    return bool(added or removed or modified), diff_summary


def try_symlink(src: Path, dst: Path) -> bool:
    """Return True if symlink succeeded. Windows needs Developer Mode or admin."""
    try:
        dst.symlink_to(src, target_is_directory=src.is_dir())
        return True
    except OSError:
        return False


def preflight_symlink() -> bool:
    with tempfile.TemporaryDirectory() as td:
        tgt = Path(td) / "tgt"
        tgt.write_text("x")
        link = Path(td) / "link"
        try:
            link.symlink_to(tgt)
            return True
        except OSError:
            return False


def deploy_dir(src: Path, dst: Path, mode: str, stamp: str, check: bool) -> tuple[bool, str, bool, list[str]]:
    """Returns (changed, diff_summary, symlink_fell_back, removed_files)."""
    changed = True
    diff = ""
    removed_files: list[str] = []
    fell_back = False
    if dst.exists() and not dst.is_symlink():
        different, parts = dirs_differ(src, dst)
        changed = different
        diff = ",".join(parts) if parts else ""
        a_files = {str(p.relative_to(src)) for p in src.rglob("*") if p.is_file()}
        b_files = {str(p.relative_to(dst)) for p in dst.rglob("*") if p.is_file()}
        removed_files = sorted(b_files - a_files)
    elif dst.is_symlink():
        changed = dst.resolve() != src.resolve()
    if not changed or check:
        return changed, diff, fell_back, removed_files
    backup(dst, stamp)
    if dst.is_symlink():
        dst.unlink()
    elif dst.exists():
        shutil.rmtree(dst)
    if mode == "symlink" and try_symlink(src, dst):
        return True, diff, False, removed_files
    if mode == "symlink":
        fell_back = True
    shutil.copytree(src, dst)
    return True, diff, fell_back, removed_files


def deploy_file(src: Path, dst: Path, mode: str, stamp: str, check: bool) -> tuple[bool, bool]:
    changed = not dst.exists() or not filecmp.cmp(src, dst, shallow=False)
    fell_back = False
    if not changed or check:
        return changed, fell_back
    backup(dst, stamp)
    if dst.exists() or dst.is_symlink():
        dst.unlink()
    if mode == "symlink" and try_symlink(src, dst):
        return True, False
    if mode == "symlink":
        fell_back = True
    atomic_write(dst, src.read_text(encoding="utf-8"))
    return True, fell_back


def atomic_write(dst: Path, content: str) -> None:
    """Write content to dst atomically (write+fsync tmp, then os.replace)."""
    tmp = dst.with_suffix(dst.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as f:
        f.write(content)
        f.flush()
        try:
            os.fsync(f.fileno())
        except OSError:
            pass
    os.replace(tmp, dst)


def deploy_settings(src: Path, dst: Path, stamp: str, check: bool) -> bool:
    """Rewrite {{CLAUDE_HOME}} → absolute DEST path, atomically deploy."""
    rewritten = src.read_text(encoding="utf-8").replace(
        "{{CLAUDE_HOME}}", str(DEST).replace("\\", "/")
    )
    changed = not dst.exists() or dst.read_text(encoding="utf-8") != rewritten
    if not changed or check:
        return changed
    backup(dst, stamp)
    atomic_write(dst, rewritten)
    return True


def assert_no_managed_in_protected() -> None:
    for name in MANAGED_DIRS + MANAGED_FILES + SPECIAL_FILES:
        if name in PROTECTED:
            raise SystemExit(f"config error: {name} is both managed and protected")


def maybe_init_local() -> bool:
    local = DEST / "settings.local.json"
    if local.exists():
        print("settings.local.json already exists — left untouched")
        return False
    local.write_text(json.dumps(LOCAL_TEMPLATE, indent=2) + "\n", encoding="utf-8")
    print(f"scaffolded {local}")
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--symlink", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--init-local", action="store_true")
    args = ap.parse_args()

    if not SRC.exists():
        print(f"Source not found: {SRC}", file=sys.stderr)
        return 2

    assert_no_managed_in_protected()
    DEST.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y-%m-%dT%H%M%S")
    mode = "symlink" if args.symlink else "copy"

    if args.symlink and platform.system() == "Windows" and not preflight_symlink():
        print(
            "Windows: symlinks unavailable (enable Developer Mode or run as Admin). "
            "Falling back to copy mode.",
            file=sys.stderr,
        )
        mode = "copy"

    any_changed = False
    fallbacks = 0

    for d in MANAGED_DIRS:
        src = SRC / d
        if not src.exists():
            continue
        dst = DEST / d
        ch, diff, fb, removed = deploy_dir(src, dst, mode, stamp, args.check)
        if ch:
            any_changed = True
            print(f"{'DIFF' if args.check else 'SYNC'} {d}/" + (f" ({diff})" if diff else ""))
            for r in removed:
                print(f"    removed: {d}/{r}")
        if fb:
            fallbacks += 1

    for f in MANAGED_FILES:
        src = SRC / f
        if not src.exists():
            continue
        dst = DEST / f
        ch, fb = deploy_file(src, dst, mode, stamp, args.check)
        if ch:
            any_changed = True
            print(f"{'DIFF' if args.check else 'SYNC'} {f}")
        if fb:
            fallbacks += 1

    for f in SPECIAL_FILES:
        src = SRC / f
        if not src.exists():
            continue
        dst = DEST / f
        ch = deploy_settings(src, dst, stamp, args.check)
        if ch:
            any_changed = True
            print(f"{'DIFF' if args.check else 'SYNC'} {f} (path-substituted)")

    if args.init_local:
        maybe_init_local()

    if args.check:
        print("changes pending" if any_changed else "in sync")
        return 1 if any_changed else 0

    summary = f"deployed ({mode})"
    if fallbacks:
        summary += f"; {fallbacks} items copied because symlinks unavailable"
    if any_changed:
        summary += f" — backups in {DEST/'backups'/stamp}"
    else:
        summary += " — no changes"
    print(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
