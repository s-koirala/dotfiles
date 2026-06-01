---
title: Audit trail — R2-A (/commit-with-provenance)
date: 2026-05-15
type: audit_trail
subject: R2-A from implementation_plan_dotfiles_additions_2026-05-15.md
loop: per-item audit-remediate-loop
auditor: quant-auditor (round 1 + remediation)
rounds_completed: 1
rounds_cap: 3
exit_reason: 1 major + 3 minor remediated in-round; gates re-verified clean
---

# R2-A build record

## Files created
- `~/.claude/scripts/commit_with_provenance.py` (~270 lines after remediation)
- `~/.claude/commands/commit-with-provenance.md`

## Pre-audit gates (5 passed end-to-end)
1. Rejects no-staged-changes (exit 1)
2. Rejects non-Conventional-Commits subject (exit 1)
3. `--dry-run` with `--no-repro` composes correct trailer message
4. Real commit with `--no-repro` works
5. Real commit with full ReproLog path — 13 fields populated, dataset_checksums from R1-E manifest, content-addressed trailer matches on-disk log SHA

## Quant-auditor findings + disposition

| ID | Severity | Issue | Disposition |
|---|---|---|---|
| P2A-1-1 | **major** | `compute_pip_freeze` used `text=True` in subprocess and re-encoded to UTF-8; on Windows this decodes via cp1252 then re-encodes, producing different bytes than the raw pip stdout for non-ASCII content. Breaks byte-identity SHA-256 claim. | **fixed**: removed `compute_pip_freeze` entirely; delegated to `emit_repro_log._pip_freeze_bytes()` which already uses raw bytes (no text=True). Added `venv_available()` precheck function for fail-hard branch. |
| P2A-1-2 | minor | `cwd_is_publishing` used substring match for the `project-pub` token, which would false-positive on `my-project-pub/`, `old-project-pub-archive/`, etc. Rule glob is `**/project-pub/**` (exact segment, no wildcards). | **fixed**: split into `_PUBLISHING_EXACT = ('project-pub',)` (exact segment) and `_PUBLISHING_SUBSTRING = ('publication','manuscript')` (rule uses `*foo*`); separate checks for each. Verified on 6 path test cases. |
| P2A-1-3 | minor | Duplicate pip-freeze invocation — wrapper called once, `repro.capture` internally called again. The wrapper's `freeze_sha`/`freeze_rel` were dead variables; also risked write-then-overwrite with divergent bytes. | **fixed**: wrapper no longer invokes pip freeze; only `venv_available()` precheck. Single subprocess call inside `repro.capture` is canonical. |
| P2A-1-4 | minor | Hardcoded `hypothesis_id='n/a'`, `rng_seed=0` without `# justify:` neighbor per CLAUDE.md magic-numbers policy. | **fixed**: added inline `# justify:` comments explaining each sentinel choice. |

## Post-remediation gates (all re-verified)
- End-to-end fresh-venv commit: PASS (3 trailers, 13-field ReproLog, dataset_checksums populated)
- Content-addressing tamper-detection: PASS (log SHA == trailer SHA)
- Publishing-cwd detection: PASS on 6/6 edge cases including `my-project-pub/` correctly NOT matching

## Residual risk (auditor's flag)
Tamper-evidence is content-addressed against an **on-disk** ReproLog file that is itself NOT in the commit. An actor with working-tree write access can rewrite the ReproLog post-commit without git seeing it. Auto-staging the ReproLog would create a chicken-and-egg (trailer references its own SHA, but SHA depends on commit contents). **Accepted limitation**; documented in command body. Mitigation would require either (a) writing the log AFTER commit with a `git notes` annotation, or (b) staging the log AND emitting the trailer via a two-commit pattern. Both exceed plan scope; revisit in a future ADR.

## R2-A PASS. Proceeding to R2-B1.
