---
title: Audit trail — public-anonymization refactor
date: 2026-06-01
type: audit_trail
scope: anonymize repo for public reuse (strip pseudonym + private-project coupling)
rounds: 1
verdict: exit-loop (0 critical, 0 major)
---

# Audit trail — public-anonymization refactor

Audit-remediate loop (`skills/audit-remediate-loop`) over the anonymization
change on branch `claude/lucid-thompson-RhXrf`. Four specialist auditors ran in
parallel against checkpoint `a9e95ba`. The calculations branch (quant/epi method
fidelity) was N/A — no statistical methods changed.

## Round 1

**Result: 0 critical, 0 major, 14 minor.** Exit condition met (only minor
findings remain, each fixed or accepted with rationale); no Round 2 required.

### format-auditor

| ID | Sev | Finding | Disposition |
|---|---|---|---|
| FA-1 | minor | Dead ctx keys `MODEL_ID`/`MODEL_VERSION`/`ROLE` in `bootstrap_project.py` after the `--role`/CITATION strip; carried a stale hard-coded model-version string. | **Fixed** — removed the three ctx entries. |
| FA-2 | minor | `docs/audits/` historical records still narrate the removed publishing apparatus. | **Accepted** — historical trail, kept-and-anonymized per the agreed decision; no identity leakage. |

Verified clean: zero `SKIE`/`skie_ninja`/`SKIE-Universe`/`project-skie`/`skie.mplstyle`
tokens anywhere; all inventory counts match the filesystem (skills 14, agents 7,
commands 8, hooks 7, rules 2, scripts 4, templates 5, bootstrap_templates 10);
`publication.mplstyle` rename fully propagated; template substitution complete;
`config.toml` confirmed gitignored.

### code-reviewer

| ID | Sev | Finding | Disposition |
|---|---|---|---|
| CR-1 | minor | Dead ctx keys (same as FA-1). | **Fixed** (with FA-1). |
| CR-2 | minor | `load_identity` docstring claimed `CLI > config > env` but code applies `config → env → CLI` (env over config). | **Fixed** — corrected docstring to `CLI > env > config > prompt > default`. |
| CR-3 | minor | `license_id` inline comment "override per project" misleading after the CC-BY/publishing path was removed (LICENSE now unconditional MIT). | **Fixed** — simplified comment. |
| CR-4 | minor | F541: two `print(f"…")` with no placeholders in the `git_init_and_commit` no-identity block. | **Fixed** — dropped the `f` prefix. |
| CR-5 | minor | F401: unused `field` import in `emit_repro_log.py`. | **Fixed** — removed from import. |
| CR-6 | minor | `_SHARED_TEMPLATE_DIR` fallback now a no-op for the current template set. | **Accepted** — valid safety net, still referenced; not dead. |

Validated by execution: `--help`/`--dry-run` succeed with no network; `--dry-run`
returns before `load_identity`, so the interactive prompt never fires in dry-run;
the `"Your Name"` placeholder cannot leak into a committed `git user.name`;
`commit_with_provenance.py` has no residual references to the removed
`cwd_is_publishing`/`_ROLE_ENUM`/`_PUBLISHING_*`/`args.role`/AI-Assistance symbols
(prior `_PUBLISHING_GLOBS` NameError path also gone); `emit_repro_log` env-var
rename consistent and `--selftest` passes.

### literature-check (21 citations checked)

| ID | Sev | Finding | Disposition |
|---|---|---|---|
| LC-1 | minor | Orphaned in-text citation `van der Walt & Smith 2015` in `deliver-results/SKILL.md` (no References entry). **Pre-existing** (predates this commit). | **Fixed** — added the SciPy 2015 viridis reference. |
| LC-2 | minor | `pit-canary` cites AFML "§8.3" for permutation importance; most precise anchor is §8.2–8.3. **Pre-existing**, unchanged by refactor. | **Accepted** — correct at chapter level. |
| LC-3 | minor | Three statistics-textbook page anchors not page-verified (web confirmed the load-bearing AFML §7 / ISBN / Politis-Romano claims). | **Accepted** — section-level attribution coherent. |

Confirmed the four reframed provenance claims are factually correct — notably the
"13-field ReproLog is a superset of the 5-field `CLAUDE.md` mandate" claim matches
`CLAUDE.md §Reproducibility` exactly, and no citation was orphaned *by* the refactor.

### reproducibility-verifier

| ID | Sev | Finding | Disposition |
|---|---|---|---|
| RV-1 | minor | Stale "(12 .tmpl files)" changelog comment in `bootstrap_project.py`. | **Fixed** — dropped the count. |
| RV-2 | minor | `repro_log_schema.json` `$id` omits the `/assets/` path segment. **Pre-existing**; `$id` is a non-dereferenced identifier. | **Accepted** — out of scope. |

Confirmed: zero dangling references to the 11 deleted files or the renamed
`skie.mplstyle` in active config; hook/registration integrity intact (settings.json,
both pre-commit configs); `deploy.py` MANAGED_DIRS correct and the renamed style
deploys. The 9 broken relative links found are all out of scope — six to
`memory/` (PROTECTED, machine-local, gitignored), one literal `[path](path)` doc
example, one historical `[LICENSE]` record in an audit trail.

## Residual risk (accepted)

Low. Intentionally left as-is:
- `docs/audits/` historical narration of the removed apparatus (kept-and-anonymized
  per decision; no identity leakage).
- `memory/feedback_*.md` references (per-user gitignored pattern; empty on a fresh
  clone — an adopter populates them, or they remain inert).
- Two pre-existing E702 semicolons (`bootstrap_project.py:239`, a compact
  write/flush/fsync idiom); the schema `$id` `/assets/` path; the `pit-canary` §8.3
  anchor.

None of these defeats the anonymization goal. Identity hygiene, dangling-reference
integrity, Python correctness, and citation integrity all pass.
