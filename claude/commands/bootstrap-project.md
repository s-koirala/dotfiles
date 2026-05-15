---
description: Scaffold a new project directory with SKIE-canonical layout (R2-B1 phase = dir tree + manifest + git init; R2-B2 will add templated CLAUDE.md/README.md/etc). Use whenever starting a new research project.
argument-hint: "<name> --kind={quant|epi|publishing|generic} [--path=<parent>] [--python-version=X.Y] [--venv] [--user-email=<pseudonym>] [--dry-run] [--rollback-on-fail]"
---

Run the bootstrap script with $ARGUMENTS:

    python ~/.claude/scripts/bootstrap_project.py $ARGUMENTS

R2-B1 phase (current): creates the directory tree and writes `manifest.json`. Top-level files (CLAUDE.md, README.md, CHANGELOG.md, CITATION.cff, etc.) are NOT yet templated — that is R2-B2.

Behavior:
- Creates `<path>/<name>/` with ~24 base subdirs + kind-conditional extras (e.g. `research/01_hypothesis_register/` for quant, `docs/protocol/` for epi, `manuscript/` for publishing). Both `runs/` AND `artifacts/runs/` are emitted (SKIE-Universe has both as siblings).
- Writes `manifest.json` at project root: `bootstrap_script_version`, `bootstrap_script_git_head`, `kind`, `rules_file`, `python_version`, `venv_created`, `timestamp_utc`, `subdirs`, `subdir_listing_sha256`, `files: {}`.
- Resolves `python_version` from SKIE-Universe `pyproject.toml::[project].requires-python` (gh api, cached at `~/.claude/cache/skie_python_version.txt`). Overridable via `--python-version`.
- If `--venv`: runs `uv venv` in the project root.
- Calls `git init -b main` and an initial Conventional Commits `chore: bootstrap` commit.

Idempotency:
- Re-running on an existing project root with matching `kind` + matching `bootstrap_script_git_head` + matching `subdir_listing_sha256` exits `in-sync` with no writes.
- If the dotfiles HEAD has drifted since last bootstrap (template source changed), exits non-zero with a `--migrate` hint. **`--migrate` is not yet implemented** (R2-B2 follow-up).
- If subdirs are missing, recreates them and updates the manifest.

Identity hygiene:
- For `--kind=publishing`, pass `--user-email <SKIE-pseudonym-email>`. The script writes it to the new repo's local git config; does NOT modify global git config.
- Per [rules/publishing.md](../rules/publishing.md), never auto-set the real-name email anywhere.

Rollback:
- With `--rollback-on-fail`, if any exception fires AFTER `mkdir` but BEFORE successful completion, the script `shutil.rmtree`s the newly-created project directory. Only operates on a directory created in the current invocation; never deletes a pre-existing tree.

Reproducibility:
- The bootstrap manifest records the dotfiles HEAD at bootstrap time, so any future audit can reproduce the layout by checking out that SHA of `s-koirala/dotfiles` and re-running.
- After R2-B2 lands, every templated file will additionally have its rendered SHA-256 in `manifest.files`.

Hand-off:
- After bootstrap, the user can invoke [/adr-new](adr-new.md) to seed `docs/decisions/ADR-0001.md`.
- For quant kind: use [/hypothesis-new](hypothesis-new.md) when R3-1 lands.
- All subsequent commits in the bootstrapped project should use [/commit-with-provenance](commit-with-provenance.md).
