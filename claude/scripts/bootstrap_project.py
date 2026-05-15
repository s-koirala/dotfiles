#!/usr/bin/env python3
"""Bootstrap a new project working directory with SKIE-canonical layout.

R2-B1 phase (this commit): directory tree + .gitkeep files + manifest.json +
git init. Template rendering (~25 .tmpl files) lands in R2-B2.

Reproducibility: the bootstrap script itself is a reproducible artifact. We
record into the project's `manifest.json`:
  - bootstrap_script_version (SemVer 2.0.0)
  - bootstrap_script_git_head (git SHA of ~/.claude at bootstrap time)
  - python_version pin (resolved from SKIE-Universe pyproject.toml at first
    run; cached in ~/.claude/cache/skie_python_version.txt for offline reruns)
  - per-dir SHA-256 of the directory listing (recursive; for idempotency check)
  - per-file SHA-256 of every templated file (populated in R2-B2; empty here)
  - rules_file: which ~/.claude/rules/*.md activates for the chosen --kind
  - venv_created: bool
  - timestamp_utc

Idempotency mechanism:
  On second invocation, the script:
    1. Reads existing manifest.json.
    2. Recomputes the current per-dir SHAs.
    3. If all SHAs match AND bootstrap_script_git_head matches current
       ~/.claude HEAD -> exit 0 with "in sync"; no writes.
    4. If a target path is missing -> create it, update manifest.
    5. If bootstrap_script_git_head differs (template source drift) ->
       exit non-zero with --migrate hint; never silent overwrite.

Rollback: with --rollback-on-fail, any exception after the project directory
is created triggers shutil.rmtree on the newly-created directory. Never
touches an existing tree (idempotent re-run preserves user content).

Filename rule: all generated subdirs follow SKIE-Universe convention. ADR
files emitted by R1-D's /adr-new follow ADR-NNNN-slug.md.

Hard constraints:
- Python 3.11+ stdlib only (no jinja2; templates use str.format_map in R2-B2)
- All numeric thresholds documented inline with `# justify:` comments
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath

_SCRIPT_VERSION = "0.1.0"  # SemVer 2.0.0; bump on template or layout change

# Subdirs created for all --kind variants. Order matches docs/audits/
# implementation_plan_dotfiles_additions_2026-05-15.md §A.3 (memo) and
# SKIE-Universe layout verified via gh api.
_BASE_SUBDIRS = (
    "src",
    "tests",
    "scripts",
    "notebooks",
    "data/raw",
    "data/interim",
    "data/processed",
    "data/external",
    "docs/audits",
    "docs/decisions",
    "docs/literature",
    "docs/methodology",
    "docs/reports",
    "docs/research_notes",
    "docs/templates",
    "research",
    "reports",
    "artifacts/models",
    "artifacts/runs",
    "runs",                      # SKIE-Universe has BOTH artifacts/runs/ AND
                                 # top-level runs/ — emit both per plan audit F-1-3
    "config",
    "logs/reproducibility",
    "logs/reproducibility/env",  # for pip_freeze_<sha>.txt files
    "outputs",
)

# Kind-conditional extras
_KIND_EXTRAS = {
    "quant": (
        "config/instruments",
        "research/00_literature_review",
        "research/01_hypothesis_register",
        "logs/promotions",
    ),
    "epi": (
        "docs/protocol",
        "data/processed/_provenance",
        "logs/imputation",
    ),
    "publishing": (
        "manuscript",
        "manuscript/figures",
        "manuscript/supplement",
        "submissions",
    ),
    "generic": (),
}

# Mapping --kind -> activating ~/.claude/rules/*.md (informational; the rules
# are cwd-glob activated by ~/.claude/CLAUDE.md, not by the bootstrap)
_KIND_RULES = {
    "quant": "rules/quant-project.md",
    "epi": "rules/population-health.md",
    "publishing": "rules/publishing.md",
    "generic": None,
}

# Cache file for the SKIE-Universe Python version pin (gh api fetch); avoids
# network on every invocation.
_CACHE_DIR = Path.home() / ".claude" / "cache"
_PYTHON_VERSION_CACHE = _CACHE_DIR / "skie_python_version.txt"

# Subprocess timeout for gh api / git commands. Justify: gh api p99 < 5s on
# warm connection; 30s margin covers cold-start + 3xx redirects.
_SUBPROCESS_TIMEOUT_SEC = 30


def run(cmd: list[str], cwd: Path | None = None,
        check: bool = False, capture: bool = True,
        timeout: int = _SUBPROCESS_TIMEOUT_SEC) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd, cwd=cwd, capture_output=capture, text=True,
        check=check, timeout=timeout,
    )


def resolve_python_version() -> str:
    """Fetch SKIE-Universe pyproject.toml requires-python; cache result.

    Falls back to '3.11' (matches user's currently installed py launcher
    target) if gh api unavailable. Cache is invalidated by user manually
    removing the cache file; no TTL.
    """
    if _PYTHON_VERSION_CACHE.exists():
        try:
            return _PYTHON_VERSION_CACHE.read_text(encoding="utf-8").strip()
        except OSError:
            pass

    # Fetch from upstream
    try:
        r = run(["gh", "api",
                 "repos/s-koirala/SKIE-Universe/contents/pyproject.toml",
                 "--jq", ".content"], timeout=_SUBPROCESS_TIMEOUT_SEC)
        if r.returncode == 0 and r.stdout.strip():
            import base64
            content = base64.b64decode(r.stdout.strip()).decode("utf-8")
            # Parse requires-python from [project] section
            import re
            m = re.search(r'^\s*requires-python\s*=\s*"([^"]+)"', content, re.M)
            if m:
                version = m.group(1)
                _CACHE_DIR.mkdir(parents=True, exist_ok=True)
                _PYTHON_VERSION_CACHE.write_text(version, encoding="utf-8")
                return version
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass

    # Fallback. justify: matches the only Python interpreter currently
    # installed on the user's machine (py launcher 3.11.9 verified 2026-05-15);
    # safe default that any project can override with --python-version.
    return ">=3.11,<3.13"


def script_git_head() -> str:
    """git rev-parse HEAD for ~/.claude; 'unknown' on failure."""
    dotfiles = Path(__file__).resolve().parent.parent
    r = run(["git", "-C", str(dotfiles), "rev-parse", "HEAD"])
    return r.stdout.strip() if r.returncode == 0 else "unknown"


def sha256_dir_listing(path: Path) -> str:
    """SHA-256 of the sorted POSIX-relative listing of files/dirs under `path`.

    Used for idempotency check: bootstrap-generated tree should match its
    manifest's per-dir SHA after re-run.

    Excludes:
      - `.git/` and contents (changes after `git init`; would break idempotency)
      - `.venv/` and contents (uv venv populates this with hundreds of files)
      - `__pycache__/`, `*.pyc` (Python bytecode cache)
      - `manifest.json` itself (its own SHA would chicken-and-egg)
    """
    if not path.is_dir():
        return ""
    excluded_prefixes = (".git/", ".venv/", "venv/", "__pycache__/")
    excluded_names = ("manifest.json",)
    entries = []
    for p in path.rglob("*"):
        rel = str(PurePosixPath(*p.relative_to(path).parts))
        if any(rel.startswith(pref) or f"/{pref}" in f"/{rel}/"
               for pref in excluded_prefixes):
            continue
        if p.name in excluded_names:
            continue
        if p.suffix == ".pyc":
            continue
        entries.append(f"{rel}\t{'d' if p.is_dir() else 'f'}")
    payload = "\n".join(sorted(entries)).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def atomic_write_json(path: Path, payload: dict) -> Path:
    """Same atomic-write idiom as R1-A emit_repro_log.py."""
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False).encode("utf-8")
    tmp = tempfile.NamedTemporaryFile(
        mode="wb", dir=str(path.parent),
        prefix=f".{path.name}.", suffix=".tmp", delete=False,
    )
    tmp_path = Path(tmp.name)
    try:
        try:
            tmp.write(data); tmp.flush(); os.fsync(tmp.fileno())
        finally:
            tmp.close()
        os.replace(tmp_path, path)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise
    return path


def build_dir_tree(project_root: Path, kind: str, dry_run: bool = False) -> list[str]:
    """Create base + kind-extra subdirs with .gitkeep sentinels. Returns the
    list of subdir paths (POSIX-relative) that exist after the call."""
    subdirs = list(_BASE_SUBDIRS) + list(_KIND_EXTRAS[kind])
    created: list[str] = []
    for sub in subdirs:
        d = project_root / sub
        if not d.exists():
            if not dry_run:
                d.mkdir(parents=True, exist_ok=True)
            created.append(sub)
        gitkeep = d / ".gitkeep"
        if not gitkeep.exists() and not dry_run:
            gitkeep.touch()
    return subdirs


def build_manifest(
    project_root: Path,
    kind: str,
    python_version: str,
    venv_created: bool,
    subdirs: list[str],
) -> dict:
    """Compose the manifest.json payload."""
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    head = script_git_head()
    return {
        "bootstrap_script_version": _SCRIPT_VERSION,
        "bootstrap_script_git_head": head,
        "kind": kind,
        "rules_file": _KIND_RULES[kind],
        "python_version": python_version,
        "venv_created": venv_created,
        "timestamp_utc": now,
        "subdirs": sorted(subdirs),
        "subdir_listing_sha256": sha256_dir_listing(project_root),
        "files": {},  # populated in R2-B2 with per-template SHA-256
    }


def idempotency_check(project_root: Path, expected_kind: str) -> tuple[str, str]:
    """Compare current state to existing manifest. Returns (status, detail).

    Status one of:
      - 'in-sync'      : everything matches; no writes needed
      - 'missing-paths': some subdirs/files don't exist; will be created
      - 'script-drift' : bootstrap_script_git_head differs; bail with --migrate hint
      - 'fresh'        : no manifest; this is a first bootstrap
    """
    mp = project_root / "manifest.json"
    if not mp.exists():
        return "fresh", ""
    try:
        m = json.loads(mp.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return "fresh", f"existing manifest unreadable: {e}"

    if m.get("kind") != expected_kind:
        return "script-drift", (
            f"manifest kind '{m.get('kind')}' != requested '{expected_kind}'. "
            "Refusing to mutate."
        )

    expected_head = script_git_head()
    if m.get("bootstrap_script_git_head") not in (expected_head, "unknown") \
            and expected_head != "unknown":
        return "script-drift", (
            f"bootstrap_script_git_head changed: manifest "
            f"{m.get('bootstrap_script_git_head','?')[:12]} != current "
            f"{expected_head[:12]}. Run with --migrate (not yet implemented) "
            "or remove manifest.json to force re-bootstrap."
        )

    current_sha = sha256_dir_listing(project_root)
    if m.get("subdir_listing_sha256") != current_sha:
        return "missing-paths", "subdir listing has drifted (paths added or removed)"

    return "in-sync", ""


def maybe_run_uv_venv(project_root: Path, python_version: str) -> bool:
    """Create .venv via `uv venv` if uv is on PATH. Returns True on success."""
    if run(["uv", "--version"]).returncode != 0:
        print("WARN: uv not on PATH; skipping venv creation. "
              "Run `uv venv && uv sync` manually after bootstrap.", file=sys.stderr)
        return False
    # uv venv accepts "3.11" or ">=3.11,<3.13" depending on version
    py_arg = python_version.split(",")[0].lstrip(">=<! ")
    if not py_arg:
        py_arg = "3.11"
    r = run(["uv", "venv", "--python", py_arg], cwd=project_root, timeout=60)
    if r.returncode != 0:
        print(f"WARN: uv venv failed (returncode {r.returncode}); "
              f"stderr: {r.stderr.strip()}", file=sys.stderr)
        return False
    return True


def git_init_and_commit(project_root: Path, kind: str, script_head: str,
                        user_email: str | None = None) -> str:
    """git init + initial Conventional Commits commit. Returns a status string.

    Returns one of:
      - 'committed'        : initial commit landed
      - 'already-initialized': .git/ already exists; commit skipped
      - 'no-identity'      : user.email/user.name unset; commit skipped with
                             instructions printed
      - 'commit-failed'    : git commit returned non-zero for another reason
    """
    if (project_root / ".git").exists():
        return "already-initialized"
    run(["git", "init", "-b", "main"], cwd=project_root, check=False)
    if user_email:
        run(["git", "config", "--local", "user.email", user_email],
            cwd=project_root)
        # If user_email provided, also set user.name to match
        run(["git", "config", "--local", "user.name",
             user_email.split("@")[0]], cwd=project_root)

    # Identity check: a commit will fail without user.email + user.name.
    email_r = run(["git", "-C", str(project_root), "config", "user.email"])
    name_r = run(["git", "-C", str(project_root), "config", "user.name"])
    if email_r.returncode != 0 or not email_r.stdout.strip() \
            or name_r.returncode != 0 or not name_r.stdout.strip():
        print("WARN: git user.email / user.name not configured. Initial commit "
              "skipped.", file=sys.stderr)
        print(f"  Configure with:", file=sys.stderr)
        print(f"    git -C {project_root} config --local user.email <your-email>",
              file=sys.stderr)
        print(f"    git -C {project_root} config --local user.name '<Your Name>'",
              file=sys.stderr)
        print(f"  Then run:", file=sys.stderr)
        print(f"    git -C {project_root} add . && git -C {project_root} commit "
              f"-m 'chore: bootstrap {project_root.name} ({kind})'",
              file=sys.stderr)
        return "no-identity"

    run(["git", "add", "."], cwd=project_root)
    msg = (f"chore: bootstrap {project_root.name} ({kind}) "
           f"--- bootstrap-script {script_head[:12]}")
    r = run(["git", "commit", "-m", msg], cwd=project_root)
    return "committed" if r.returncode == 0 else "commit-failed"


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("name", help="Project name (becomes the directory name "
                                "if --path not given)")
    p.add_argument("--kind", choices=sorted(_KIND_EXTRAS.keys()), required=True,
                   help="Project kind; selects extra subdirs and informs rule activation")
    p.add_argument("--path", type=Path, default=None,
                   help="Parent directory (default: cwd); project created at <path>/<name>")
    p.add_argument("--python-version", default=None,
                   help="Python version pin (overrides SKIE-Universe lookup)")
    p.add_argument("--venv", action="store_true",
                   help="Run `uv venv` after dir tree creation")
    p.add_argument("--user-email", default=None,
                   help="Set local git config user.email in the new repo "
                        "(use SKIE pseudonym for publishing-kind)")
    p.add_argument("--dry-run", action="store_true",
                   help="Show what would be created; no writes")
    p.add_argument("--rollback-on-fail", action="store_true",
                   help="shutil.rmtree the newly-created dir on any exception "
                        "(only if newly-created in THIS invocation)")
    args = p.parse_args(argv)

    parent = (args.path or Path.cwd()).resolve()
    project_root = (parent / args.name).resolve()

    python_version = args.python_version or resolve_python_version()
    script_head = script_git_head()
    newly_created = not project_root.exists()

    # Idempotency check
    if project_root.exists():
        status, detail = idempotency_check(project_root, args.kind)
        if status == "in-sync":
            print(f"in-sync: {project_root} matches manifest; no writes.")
            return 0
        if status == "script-drift":
            print(f"ERROR: {detail}", file=sys.stderr)
            return 3
        # status in ('missing-paths', 'fresh') -> proceed to (re)build

    if args.dry_run:
        print("=== DRY RUN ===")
        print(f"project_root: {project_root}")
        print(f"kind: {args.kind}")
        print(f"python_version: {python_version}")
        print(f"bootstrap_script_git_head: {script_head[:12]}")
        print(f"newly_created: {newly_created}")
        all_subs = list(_BASE_SUBDIRS) + list(_KIND_EXTRAS[args.kind])
        print(f"subdirs ({len(all_subs)}):")
        for s in all_subs:
            print(f"  {s}/")
        return 0

    # Build
    project_root.mkdir(parents=True, exist_ok=True)
    try:
        subdirs = build_dir_tree(project_root, args.kind, dry_run=False)
        venv_created = False
        if args.venv:
            venv_created = maybe_run_uv_venv(project_root, python_version)

        manifest = build_manifest(
            project_root=project_root,
            kind=args.kind,
            python_version=python_version,
            venv_created=venv_created,
            subdirs=subdirs,
        )
        atomic_write_json(project_root / "manifest.json", manifest)

        commit_status = git_init_and_commit(
            project_root, args.kind, script_head,
            user_email=args.user_email,
        )

    except Exception as e:
        if args.rollback_on_fail and newly_created:
            print(f"ERROR during bootstrap: {e}", file=sys.stderr)
            print(f"  Rolling back: removing {project_root}", file=sys.stderr)
            shutil.rmtree(project_root, ignore_errors=True)
        else:
            print(f"ERROR during bootstrap (NO rollback; tree left at "
                  f"{project_root}): {e}", file=sys.stderr)
        return 4

    print(f"Bootstrap OK: {project_root}")
    print(f"  kind={args.kind}, python={python_version}, "
          f"venv={'created' if venv_created else 'skipped'}, "
          f"commit={commit_status}")
    print(f"  manifest: {project_root}/manifest.json")
    print(f"  bootstrap_script_git_head: {script_head[:12]}")
    print(f"  R2-B2 (template rendering) is a separate item; this build "
          f"creates dir tree + manifest only.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
