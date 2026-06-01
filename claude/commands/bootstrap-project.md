---
description: Scaffold a new project directory with a canonical research layout (dir tree + manifest + git init + templated top-level files). Use whenever starting a new research project.
argument-hint: "<name> --kind={quant|epi|generic} [--path=<parent>] [--python-version=X.Y] [--venv] [--author=<name>] [--user-email=<email>] [--dry-run] [--rollback-on-fail]"
---

Run the bootstrap script with $ARGUMENTS:

    python ~/.claude/scripts/bootstrap_project.py $ARGUMENTS

Renders the directory tree, writes `manifest.json`, and renders the top-level files from templates: `CLAUDE.md`, `README.md`, `CHANGELOG.md`, `LICENSE`, `pyproject.toml`, `.gitignore`, `.gitattributes`, `.pre-commit-config.yaml`, plus kind-specific (`hypothesis_backlog.md` for quant; `docs/protocol/protocol_v0.md` for epi).

Behavior:
- Creates `<path>/<name>/` with ~24 base subdirs + kind-conditional extras (e.g. `research/01_hypothesis_register/` for quant, `docs/protocol/` for epi). Both `runs/` AND `artifacts/runs/` are emitted (some tooling hard-codes a top-level `runs/`).
- Writes `manifest.json` at project root: `bootstrap_script_version`, `bootstrap_script_git_head`, `kind`, `rules_file`, `python_version`, `venv_created`, `timestamp_utc`, `subdirs`, `subdir_listing_sha256`, `files: {}`.
- Defaults `python_version` to `>=3.11,<3.13`; override via `--python-version`.
- Identity (`author` / `email` / `github_user`) is read from `config.toml` (copy `config.example.toml`), overridable via `--author` / `--user-email` / `--github-user` flags.
- If `--venv`: runs `uv venv` in the project root.
- Calls `git init -b main` and an initial Conventional Commits `chore: bootstrap` commit.

Idempotency:
- Re-running on an existing project root with matching `kind` + matching `bootstrap_script_git_head` + matching `subdir_listing_sha256` exits `in-sync` with no writes.
- If the dotfiles HEAD has drifted since last bootstrap (template source changed), exits non-zero with a `--migrate` hint. **`--migrate` is not yet implemented** (R2-B2 follow-up).
- If subdirs are missing, recreates them and updates the manifest.

Identity hygiene:
- `--user-email` (or `email` in `config.toml`) sets the new repo's LOCAL git config only; the script never modifies global git config.
- Avoid auto-setting an unwanted real-name email anywhere; prefer the GitHub no-reply form.

Rollback:
- With `--rollback-on-fail`, if any exception fires AFTER `mkdir` but BEFORE successful completion, the script `shutil.rmtree`s the newly-created project directory. Only operates on a directory created in the current invocation; never deletes a pre-existing tree.

Reproducibility:
- The bootstrap manifest records the dotfiles HEAD at bootstrap time, so any future audit can reproduce the layout by checking out that SHA of `s-koirala/dotfiles` and re-running.
- After R2-B2 lands, every templated file will additionally have its rendered SHA-256 in `manifest.files`.

Hand-off:
- After bootstrap, the user can invoke [/adr-new](adr-new.md) to seed `docs/decisions/ADR-0001.md`.
- For quant kind: use [/hypothesis-new](hypothesis-new.md) when R3-1 lands.
- All subsequent commits in the bootstrapped project should use [/commit-with-provenance](commit-with-provenance.md).
