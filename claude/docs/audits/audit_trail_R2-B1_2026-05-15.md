---
title: Audit trail — R2-B1 (/bootstrap-project CLI + dir tree)
date: 2026-05-15
type: audit_trail
subject: R2-B1 from implementation_plan_dotfiles_additions_2026-05-15.md
loop: per-item audit-remediate-loop
auditor: gate-only (behavioral verification across kinds + idempotency)
rounds_completed: 0
exit_reason: 8 behavioral gates passed; 2 bugs caught + fixed during gate verification (in-tree review counts as round 0)
---

# R2-B1 build record

## Files created
- `~/.claude/scripts/bootstrap_project.py` (~340 lines)
- `~/.claude/commands/bootstrap-project.md`

## Scope
R2-B1 ships the CLI + directory tree + manifest emission only. Template rendering (~25 `.tmpl` files for CLAUDE.md, README.md, CITATION.cff, pyproject.toml, etc.) is R2-B2, a separate item.

## Bugs found and fixed during gate verification

| Bug | Detection | Fix |
|---|---|---|
| `sha256_dir_listing` included `.git/` content, which changes after `git init`, breaking idempotency check on second invocation | Gate 5 returned "Bootstrap OK" instead of "in-sync" on re-run | Excluded `.git/`, `.venv/`, `venv/`, `__pycache__/`, `*.pyc`, `manifest.json` from the listing scan |
| `git commit` silently failed when global `git config user.email` was unset (environment edge case); `--user-email` flag was optional in the CLI | Gate 6 showed "your current branch 'main' does not have any commits yet" | Added explicit identity precheck in `git_init_and_commit`; prints clear instructions if email/name absent; returns status string consumed by main output line |

## Verification gates — all passed after fixes

| Gate | Check | Result |
|---|---|---|
| 1 | `--dry-run` lists 28 subdirs for quant kind without writing | ✓ |
| 2 | Real bootstrap quant creates 28 subdirs with `.gitkeep` sentinels + `manifest.json` | ✓ |
| 3 | Tree structure matches expected (base + quant extras: `config/instruments`, `research/00_literature_review`, `research/01_hypothesis_register`, `logs/promotions`) | ✓ |
| 4 | `manifest.json` contains 11 expected keys with correct types | ✓ |
| 5 | Idempotent re-run reports `in-sync: ... matches manifest; no writes.` | ✓ |
| 6 | Initial git commit lands with Conventional Commits subject and `bootstrap_script_git_head[:12]` reference | ✓ (`41f9c2c chore: bootstrap test_quant_v2 (quant) --- bootstrap-script 5c52abf93817`) |
| 7 | Publishing kind creates `manuscript/`, `manuscript/figures/`, `manuscript/supplement/`, `submissions/` | ✓ |
| 8 | `--user-email` writes to local git config; never modifies global | ✓ (verified via `git config --local user.email`) |

## Idempotency mechanism
1. Read existing `manifest.json` (kind + bootstrap_script_git_head + subdir_listing_sha256).
2. If kind mismatch → "script-drift" exit 3 with clear error.
3. If dotfiles HEAD changed since last bootstrap → "script-drift" exit 3 with `--migrate` hint.
4. If subdir listing SHA matches → "in-sync" exit 0; no writes.
5. If subdirs missing → recreate them, update manifest.

## Identity-hygiene
- `--user-email` is OPTIONAL but strongly recommended for publishing-kind.
- If neither global git config nor `--user-email` provides identity, the script SKIPS the initial commit with clear remediation instructions. Never makes up a default email.
- For `~/.claude/` itself (this repo), commits continue to use the no-reply email set in R0.

## Risks / deferred
- `--migrate` flag is not yet implemented. If bootstrap_script_git_head changes, user must manually delete `manifest.json` to force rebuild. R2-B2 follow-up.
- `--venv` was not exercised end-to-end (uv venv works in fixture; tested implicitly via R2-A R2-A Gate 5 earlier).
- Templates (CLAUDE.md, README.md, CITATION.cff, etc.) not yet rendered — R2-B2.

## R2-B1 PASS. Proceeding to R2-B2.
