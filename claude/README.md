# Claude Code Dotfiles (SKIE)

User-level Claude Code configuration synchronized across machines.

## Layout
- `CLAUDE.md` — user-level directives (communication, evidence hierarchy, parameter selection, verification).
- `settings.json` — permissions + hook registration. Machine-local overrides in `~/.claude/settings.local.json` (gitignored, not deployed).
- `agents/` — subagent definitions (`quant-auditor`, `literature-check`, `reproducibility-verifier`).
- `skills/` — procedural playbooks (`statistical-analysis`, `validate-data`, `audit-remediate-loop`).
- `commands/` — slash commands (`/audit-loop`, `/reproduce`, `/lit-check`).
- `rules/` — path-scoped rules (`quant-project.md`, `population-health.md`, `publishing.md`).
- `hooks/` — Python hook scripts (seed guard, bash safety, session-start provenance, notebook clean).
- `scripts/deploy.py` — idempotent deploy to `~/.claude/` (copy or symlink).

## Deploy

```bash
git clone https://github.com/s-koirala/dotfiles.git ~/dotfiles
python ~/dotfiles/claude/scripts/deploy.py          # copy (safe)
python ~/dotfiles/claude/scripts/deploy.py --symlink  # symlink (admin on Windows)
python ~/dotfiles/claude/scripts/deploy.py --check     # diff only
```

Deploy preserves: `sessions/`, `projects/`, `memory/`, `.credentials.json`, `settings.local.json`, `plugins/`, `ide/`, `shell-snapshots/`, `statsig/`, `telemetry/`.

## Secrets
- Never commit `settings.local.json` or `.credentials.json`.
- API keys: use `apiKeyHelper` in `settings.local.json` pointing to an OS-keychain script.

## Update
```bash
cd ~/dotfiles && git pull && python claude/scripts/deploy.py
```

## Empirical basis
See `CLAUDE.md` and skill/agent files for the citations that justify each directive.
