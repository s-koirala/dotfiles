---
description: Commit staged changes with a Conventional-Commits subject plus reproducibility provenance trailers (Repro-Log-Path + Repro-Log-SHA256). Recomputes pip freeze inline; never reads the truncated SessionStart cache.
argument-hint: "<subject> [--scope-strict] [--no-repro <justification>] [--dry-run]"
---

Run the wrapper script with $ARGUMENTS:

    python ~/.claude/scripts/commit_with_provenance.py $ARGUMENTS

Behavior summary:
1. Reject if no staged changes.
2. Validate subject matches Conventional Commits 1.0.0 regex (feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert).
3. Recompute pip freeze inline via project venv (`.venv/Scripts/python.exe` on Windows or `.venv/bin/python` on POSIX). Falls back to `uv pip freeze` if `uv.lock` present. **Never reads `~/.claude/cache/deps_*.json`** — that cache stores only a 12-hex truncated digest, insufficient for the 64-hex SHA-256 the ReproLog schema requires.
4. Write freeze text to `logs/reproducibility/env/<sha256>.txt` (project-local).
5. Read `data/_manifest.json` for `dataset_checksums` map; pass to `emit-repro-log`.
6. Emit ReproLog at `logs/reproducibility/repro_log_<run_id>.json`.
7. Compose Conventional Commits subject + trailers:
   - `Repro-Log-Path: <relative path>`
   - `Repro-Log-SHA256: <64-hex of log content>` (content-addressed; tamper-detectable)
8. `git commit -F <message-file>`.

Fail-hard conditions:
- No staged changes → exit 1.
- Non-Conventional-Commits subject → exit 1.
- No project Python venv detected AND `--no-repro` not set → exit 2; hint to run `bootstrap-project --venv`.

The `Co-Authored-By:` trailer is auto-added by Claude Code (`settings.json::includeCoAuthoredBy: true`). This script does NOT double-add it. **Note:** raw `git commit` outside Claude Code does NOT auto-add Co-Authored-By; use this command consistently within Claude sessions, or add via a global git template if invoking from a shell.

Hand-off:
- Consumes [emit-repro-log](../skills/emit-repro-log/SKILL.md) (R1-A).
- Consumes `data/_manifest.json` from [scripts/build_data_manifest.py](../scripts/build_data_manifest.py) (R1-E).
- Used by every subsequent build item from R2-B onward.
