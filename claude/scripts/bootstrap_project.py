#!/usr/bin/env python3
"""Bootstrap a new project working directory with a canonical research layout.

Creates the directory tree + .gitkeep files + manifest.json + git init, then
renders the bootstrap templates with the adopter's identity.

Reproducibility: the bootstrap script itself is a reproducible artifact. We
record into the project's `manifest.json`:
  - bootstrap_script_version (SemVer 2.0.0)
  - bootstrap_script_git_head (git SHA of ~/.claude at bootstrap time)
  - python_version pin (--python-version flag, or a sane default range)
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

Filename rule: all generated subdirs follow the canonical research layout. ADR
files emitted by /adr-new follow ADR-NNNN-slug.md.

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

_SCRIPT_VERSION = "0.2.0"  # SemVer 2.0.0; bump on template or layout change
# 0.2.0: R2-B2 — added template rendering
# 0.1.0: R2-B1 — initial CLI + dir tree + manifest

# Bootstrap template source dir (relative to this script)
_TEMPLATE_DIR = Path(__file__).resolve().parent / "bootstrap_templates"
# Shared template dir (used by R1-C, R1-D, etc.)
_SHARED_TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"

# Subdirs created for all --kind variants. Canonical research layout
# (data lake -> analysis-ready pipeline, docs, artifacts, logs).
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
    "runs",                      # some tooling hard-codes a top-level runs/;
                                 # emit both it and artifacts/runs/
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
    "generic": (),
}

# Mapping --kind -> activating ~/.claude/rules/*.md (informational; the rules
# are cwd-glob activated by ~/.claude/CLAUDE.md, not by the bootstrap)
_KIND_RULES = {
    "quant": "rules/quant-project.md",
    "epi": "rules/population-health.md",
    "generic": None,
}

# Bootstrap identity config. Gitignored; an adopter copies config.example.toml
# -> config.toml and sets these once so generated projects carry their own
# identity, not the template author's.
_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.toml"
_IDENTITY_DEFAULTS = {
    "author": "Your Name",
    "email": "",
    "github_user": "your-github-handle",
}

# Subprocess timeout for git commands. 30s margin covers a cold object cache.
_SUBPROCESS_TIMEOUT_SEC = 30


def run(cmd: list[str], cwd: Path | None = None,
        check: bool = False, capture: bool = True,
        timeout: int = _SUBPROCESS_TIMEOUT_SEC) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd, cwd=cwd, capture_output=capture, text=True,
        check=check, timeout=timeout,
    )


def resolve_python_version() -> str:
    """Default Python version pin; override per project with --python-version.

    justify: 3.11 floor matches the stdlib features this tooling relies on
    (e.g. tomllib); the <3.13 ceiling reflects wheel availability for the
    common scientific stack. Any project can override via --python-version.
    """
    return ">=3.11,<3.13"


def load_identity(cli_author: str | None = None,
                  cli_email: str | None = None,
                  cli_github_user: str | None = None) -> dict[str, str]:
    """Resolve bootstrap identity for emitted projects.

    Precedence (highest first): CLI flag > environment var > config.toml >
    interactive prompt (TTY only) > placeholder default. config.toml is
    gitignored; copy config.example.toml and set your values once.
    """
    vals = dict(_IDENTITY_DEFAULTS)
    if _CONFIG_PATH.exists():
        try:
            import tomllib
            data = tomllib.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
            for k in vals:
                v = data.get(k)
                if isinstance(v, str) and v.strip():
                    vals[k] = v.strip()
        except (OSError, tomllib.TOMLDecodeError):
            pass
    for k in vals:                       # env override (CI / ephemeral machines)
        env = os.environ.get(k.upper())
        if env:
            vals[k] = env
    if cli_author:
        vals["author"] = cli_author
    if cli_email:
        vals["email"] = cli_email
    if cli_github_user:
        vals["github_user"] = cli_github_user
    if sys.stdin.isatty():               # first-run prompt while still default
        if vals["author"] == _IDENTITY_DEFAULTS["author"]:
            r = input("Author name (for pyproject + git) [skip]: ").strip()
            if r:
                vals["author"] = r
        if not vals["email"]:
            r = input("Commit email (local git config, optional) [skip]: ").strip()
            if r:
                vals["email"] = r
    return vals


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


def render_template(
    template_path: Path,
    ctx: dict[str, str],
) -> str:
    """Substitute <<KEY>> placeholders with ctx[KEY]. Unknown placeholders
    pass through unchanged (preserves <<TODO: ...>> guidance markers in
    rendered bodies)."""
    text = template_path.read_text(encoding="utf-8")
    for key, val in ctx.items():
        text = text.replace(f"<<{key}>>", val)
    return text


def template_files_for(kind: str) -> list[tuple[str, str]]:
    """Return list of (template_name, target_relative_path) for the kind.

    Always-emitted (8 files) plus kind-specific extras (1-2 files).
    """
    always = [
        ("CLAUDE.md.tmpl", "CLAUDE.md"),
        ("README.md.tmpl", "README.md"),
        ("CHANGELOG.md.tmpl", "CHANGELOG.md"),
        ("LICENSE.tmpl", "LICENSE"),
        (".gitignore.tmpl", ".gitignore"),
        (".gitattributes.tmpl", ".gitattributes"),
        ("pyproject.toml.tmpl", "pyproject.toml"),
        (".pre-commit-config.yaml.tmpl", ".pre-commit-config.yaml"),
    ]
    if kind == "quant":
        always.append(("hypothesis_backlog.md.tmpl", "hypothesis_backlog.md"))
    elif kind == "epi":
        always.append(("protocol_v0.md.tmpl", "docs/protocol/protocol_v0.md"))
    return always


def render_all_templates(
    project_root: Path,
    kind: str,
    name: str,
    python_version: str,
    author: str,
    description: str = "",
) -> dict[str, str]:
    """Render every template; write to target path; return {target: sha256}.

    Skips files that already exist (preserves user edits across re-runs).
    Returns the SHA-256 map for the manifest's `files` field.
    """
    head = script_git_head()
    date = dt.date.today().isoformat()
    year = str(dt.date.today().year)
    rules_file = _KIND_RULES[kind] or "(none — generic kind)"
    license_id = "MIT"  # default SPDX license

    scope_text = {
        "quant": "Quant research project. Hypothesis-driven; pre-registered design.md per hypothesis; "
                 "walk-forward backtest with purge + embargo; Hansen SPA gate over the strategy family.",
        "epi": "Population-health research project. STROBE/CONSORT/STARD/TRIPOD reporting per study "
               "design; DAG-driven adjustment-set selection; E-value sensitivity per primary causal estimate.",
        "generic": "Generic research/scratch project. No kind-specific rules activate; user-global "
                   "rules from ~/.claude/CLAUDE.md still apply.",
    }[kind]

    reporting_standard = {
        "epi": "STROBE",  # user can change in protocol_v0.md
    }.get(kind, "")

    ctx = {
        "NAME": name,
        "DESCRIPTION": description or f"{name} ({kind} project bootstrapped from dotfiles)",
        "KIND": kind,
        "DATE": date,
        "YEAR": year,
        "RULES_FILE": rules_file,
        "PYTHON_VERSION": python_version,
        "BOOTSTRAP_SCRIPT_HEAD": head[:12] if head != "unknown" else "unknown",
        "LICENSE": license_id,
        "AUTHOR": author,
        "SCOPE_DESCRIPTION": scope_text,
        "REPORTING_STANDARD": reporting_standard,
        "DOTFILES": str(Path.home() / ".claude").replace("\\", "/"),
        "HYPOTHESIS_ROWS": "| H001 | 1 | <<TODO>> | designed | <<DOI>> | seed hypothesis |",
    }

    file_shas: dict[str, str] = {}
    for tmpl_name, target_rel in template_files_for(kind):
        # Resolve template source (bootstrap_templates/ first; fall back to shared templates/)
        src = _TEMPLATE_DIR / tmpl_name
        if not src.exists():
            src = _SHARED_TEMPLATE_DIR / tmpl_name.removesuffix(".tmpl")
        if not src.exists():
            print(f"WARN: template not found: {tmpl_name}", file=sys.stderr)
            continue

        target = project_root / target_rel
        if target.exists():
            # Preserve user edits; record current SHA but do not overwrite
            file_shas[target_rel] = hashlib.sha256(target.read_bytes()).hexdigest()
            continue

        rendered = render_template(src, ctx)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
        file_shas[target_rel] = hashlib.sha256(rendered.encode("utf-8")).hexdigest()

    return file_shas


def build_manifest(
    project_root: Path,
    kind: str,
    python_version: str,
    venv_created: bool,
    subdirs: list[str],
    file_shas: dict[str, str] | None = None,
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
        "files": file_shas or {},
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
                        user_email: str | None = None,
                        user_name: str | None = None) -> str:
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
    if user_name:
        run(["git", "config", "--local", "user.name", user_name],
            cwd=project_root)

    # Identity check: a commit will fail without user.email + user.name.
    email_r = run(["git", "-C", str(project_root), "config", "user.email"])
    name_r = run(["git", "-C", str(project_root), "config", "user.name"])
    if email_r.returncode != 0 or not email_r.stdout.strip() \
            or name_r.returncode != 0 or not name_r.stdout.strip():
        print("WARN: git user.email / user.name not configured. Initial commit "
              "skipped.", file=sys.stderr)
        print("  Configure with:", file=sys.stderr)
        print(f"    git -C {project_root} config --local user.email <your-email>",
              file=sys.stderr)
        print(f"    git -C {project_root} config --local user.name '<Your Name>'",
              file=sys.stderr)
        print("  Then run:", file=sys.stderr)
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
                   help="Python version pin (default: >=3.11,<3.13)")
    p.add_argument("--venv", action="store_true",
                   help="Run `uv venv` after dir tree creation")
    p.add_argument("--author", default=None,
                   help="Author name for pyproject + git (default: config.toml, else prompt)")
    p.add_argument("--github-user", default=None,
                   help="GitHub handle (default: config.toml)")
    p.add_argument("--user-email", default=None,
                   help="Set local git config user.email in the new repo")
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

    identity = load_identity(args.author, args.user_email, args.github_user)

    # Build
    project_root.mkdir(parents=True, exist_ok=True)
    try:
        subdirs = build_dir_tree(project_root, args.kind, dry_run=False)
        venv_created = False
        if args.venv:
            venv_created = maybe_run_uv_venv(project_root, python_version)

        # R2-B2: render templates
        file_shas = render_all_templates(
            project_root=project_root,
            kind=args.kind,
            name=args.name,
            python_version=python_version,
            author=identity["author"],
        )

        manifest = build_manifest(
            project_root=project_root,
            kind=args.kind,
            python_version=python_version,
            venv_created=venv_created,
            subdirs=subdirs,
            file_shas=file_shas,
        )
        atomic_write_json(project_root / "manifest.json", manifest)

        commit_status = git_init_and_commit(
            project_root, args.kind, script_head,
            user_email=identity["email"] or None,
            user_name=(identity["author"]
                       if identity["author"] != _IDENTITY_DEFAULTS["author"]
                       else None),
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
    print(f"  manifest: {project_root}/manifest.json "
          f"({len(manifest['files'])} tracked file(s))")
    print(f"  bootstrap_script_git_head: {script_head[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
