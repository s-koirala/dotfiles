---
title: Implementation plan — ~/.claude additions (R0 through R3)
date: 2026-05-15
type: implementation_plan
status: ready-for-implementation (plan-compile loop exited at round 2; 0 critical + 0 major residuals)
scope: ~/.claude config additions for github.com/s-koirala/dotfiles
upstream_memo: docs/audits/research_memo_dotfiles_additions_2026-05-15.md
upstream_audit_trail: docs/audits/audit_trail_dotfiles_additions_2026-05-15.md
plan_audit_trail: docs/audits/audit_trail_implementation_plan_2026-05-15.md
git_head_at_authoring: (untracked — R0 establishes; this is the round-1 prerequisite)
pip_freeze_sha256: n/a (planning artifact)
dataset_checksums: n/a (re-uses upstream-library source references hashed in upstream audit_trail)
rng_seed: n/a
model_commit: n/a
ai_assistance: claude-opus-4-7 (planning subagent + remediation pass; per ICMJE 2026)
reporting_standard: implementation plan
items_total: 21 sub-items (R0 + 5 R1 + 4 R2-subitems + 11 R3-subitems; maps to 13 memo-NEEDED items + 2 pillars + R0 + R1-E + R3-4 inline, with R2-B split into B1/B2 and R3-2 split into 2a/2b; memo #19 Sharpe-CI dropped per user directive)
audit_loop_per_item: yes (cap=3, per skills/audit-remediate-loop/SKILL.md)
remediation_round: 1
remediated_findings: 6 critical + 20 major + 9 minor from plan-audit round 1
---

# Implementation plan — dotfiles additions

## Plan-level conventions (apply to every item)

- **Filename rule.** Artifact-producing items obey `{type}_{description}_{YYYY-MM-DD}.{ext}`.
- **Reproducibility envelope.** Every artifact-producing item emits an R1-A ReproLog. The five CLAUDE.md fields (git HEAD, pip freeze SHA-256, dataset checksum, RNG seed, model commit) are mandatory; additional schema fields are derived once and documented.
- **SessionStart cache is non-authoritative.** `hooks/session_start_provenance.py` stores a 12-hex truncated digest as a SessionStart-only optimization. R2-A and ReproLog emitters re-compute the full 64-hex SHA-256 inline. The cache is never read for ReproLog content.
- **Per-item audit-remediate-loop.** Each build emits `audit_trail_{item-id}_{YYYY-MM-DD}.md` under `~/.claude/docs/audits/`; quant-auditor + literature-check + reproducibility-verifier in parallel; 3-round cap.
- **Identity hygiene.** R1-C, R2-B, R2-C, R3-2, R3-9 touch publishing-adjacent artifacts. Pre-commit gate: `git config user.email` matches the author's publishing identity; no `kernelspec.display_name` with real name; no `git config user.name` value embedded in templates.
- **Magic-numbers policy.** Every numeric in every template/skill has either inline `# justify:` neighbor or upstream empirical selection. Fixture/example numerics in this plan are annotated `# justify: fixture-only, not default`.

---

## 0. Pre-flight — R0

### R0 — Git-init `~/.claude` + remote bind

1. **Files to create.** `~/.claude/.git/` (via `git init`); `~/.claude/.gitignore`.
2. **Files to modify.** None.
3. **.gitignore enumeration** (verified against `Glob *` at `~/.claude/` 2026-05-15 — include every runtime-state or sensitive path):
   - **Sensitive (highest priority):** `.credentials.json`, `mcp-needs-auth-cache.json`, `settings.local.json`
   - **Runtime state:** `cache/`, `sessions/`, `projects/`, `telemetry/`, `statsig/`, `shell-snapshots/`, `ide/`, `file-history/`, `todos/`, `session-env/`, `stats-cache.json`, `backups/`, `debug/`, `scheduled_tasks.lock`, `plugins/`, `.last-cleanup`, `.claude/`
   - **Allow-list (do NOT ignore):** `mcp.json` (R1-B target; commit this)
4. **Build steps.**
   1. Write `.gitignore` per §3.
   2. `git init -b main` in `~/.claude/`.
   3. `git config user.email` precheck — must match the author's publishing identity before any commit.
   4. `git remote add origin <s-koirala/dotfiles URL>` (https or ssh per user environment).
   5. `git add -A && git commit -m "chore: initial commit of ~/.claude tracked state"`.
   6. `git fetch origin && git status` — surface any divergence from remote; do not auto-merge.
5. **Dependencies.** None.
6. **Verification gate** (all runnable, unattended-able):
   - `git -C ~/.claude rev-parse HEAD` → SHA.
   - `git -C ~/.claude remote -v` → `origin → s-koirala/dotfiles.git`.
   - `git -C ~/.claude ls-files | grep -E '\.credentials|token|secret'` → 0 lines (no sensitive files tracked).
   - `git -C ~/.claude ls-files mcp.json` → returns `mcp.json` once R1-B lands (post-condition for R1-B's own gate).
   - With `CLAUDE_PROJECT_DIR=~/.claude` set, `python ~/.claude/hooks/session_start_provenance.py < /dev/null` emits `git: <sha12> (main)` for `~/.claude`. (Note: other-project sessions correctly continue to report their own project's git — this is intended.)
7. **Rollback.** `rm -rf ~/.claude/.git ~/.claude/.gitignore`. Untracked state restored.
8. **Risk surface.** First commit captures sensitive runtime data if .gitignore is incomplete → mitigated by §3 enumeration with sensitive-first ordering.
9. **Effort.** XS (<30 min).

---

## 1. Round 1 — Foundations

### R1-A — `skills/emit-repro-log` (memo #25)

1. **Files to create.**
   - `~/.claude/skills/emit-repro-log/SKILL.md`
   - `~/.claude/skills/emit-repro-log/assets/repro_log_schema.json`
   - `~/.claude/skills/emit-repro-log/assets/emit_repro_log.py`
2. **Schema fields (frozen).** Source-of-truth: the upstream library's reproducibility module (`utils/reproducibility.py`). The schema must enumerate exactly the upstream library's dataclass fields, with the content hash of that source file embedded in the schema's `$comment`. Per CLAUDE.md the five mandatory fields are git_head, pip_freeze_sha256, dataset_checksums, rng_seed, model_hash. The rest derive automatically:
   - `run_id` (str), `phase` (enum: bootstrap|backtest|inference|validation|deliver), `hypothesis_id` (str|null), `timestamp_utc` (ISO 8601 str), `git_head` (40-hex), `pip_freeze_sha256` (64-hex of full freeze text — NOT the truncated cache digest), `pip_freeze_path` (str — project-local path to text file, see R2-A), `dataset_checksums` (object, additionalProperties=str, populated from `data/_manifest.json` per R1-E), `rng_seed` (int|null), `model_hash` (str|null), `config_resolved_sha256` (str|null), `host` (object: `os` str, `python` = `platform.python_version()` like `"3.12.1"` (version only, not interpreter path), `hostname` str). **`env_id` dropped from round-1 schema** — `host` + `pip_freeze_sha256` already pin environment.
3. **Atomic write — explicit pseudocode** (Windows-safe; required to satisfy byte-identity for SHA-256 verification):
   ```python
   from tempfile import NamedTemporaryFile
   import os
   from pathlib import Path
   payload_bytes = json.dumps(record, sort_keys=True, indent=2).encode("utf-8")
   with NamedTemporaryFile(
       mode="wb", delete=False,
       dir=path.parent, prefix=path.stem + ".", suffix=".tmp"
   ) as tf:
       tf.write(payload_bytes)
       tf.flush()
       os.fsync(tf.fileno())
       tmp = Path(tf.name)
   os.replace(tmp, path)
   ```
   Same-volume placement (`dir=path.parent`) is mandatory; `os.replace` is atomic only within a single filesystem. `delete=False` is mandatory on Windows.
4. **Dependencies.** R0.
5. **Verification gate.**
   - `python -c "import json, jsonschema; s=json.load(open('.../repro_log_schema.json')); jsonschema.Draft202012Validator.check_schema(s)"` exits 0.
   - `--selftest` flag on `emit_repro_log.py`: build fixture from env, write, read back, validate against schema, exit 0.
   - Schema field set matches the upstream library's dataclass field set (set-equality assertion; embedded source-file content hash validated).
   - Byte-identity round-trip: write a fixture from Linux fixture data on Windows, hash bytes; replay on Linux from the same source; assert identical SHA-256.
6. **Rollback.** Delete `skills/emit-repro-log/`.
7. **Risk surface.** Schema drift vs the upstream library → mitigated by embedded source-file content hash + build-time assertion.
8. **Effort.** S (1–2 hr).

### R1-B — `~/.claude/mcp.json` (memo #12)

1. **Files to create.** `~/.claude/mcp.json`.
2. **Content sketch.** `{ "mcpServers": { arxiv, crossref, zenodo } }` with `uvx`-based commands. Tokens read from keychain-referenced files, never inlined. Zotero excluded pending §5 Q5 — leave a commented placeholder.
3. **Dependencies.** R0.
4. **Verification gate** (all runnable in CI without user enable):
   - `python -c "import json; json.load(open('~/.claude/mcp.json'))"` exits 0 (parses).
   - `uvx --help` exits 0 (uvx available; precondition for any server launch).
   - `claude mcp list` shows three servers (state may be `disabled` until user enable).
   - **Deferred follow-up gate** (post user-enable): `claude mcp call arxiv list_tools` returns non-empty array. Documented as a follow-up validation, not a build gate.
5. **Rollback.** Delete `mcp.json`.
6. **Risk surface.** Package-name drift; mitigated by `uvx --help` precheck.
7. **Effort.** XS.

### R1-C — CITATION.cff template + precommit hook (memo #3)

1. **Files to create.**
   - `~/.claude/templates/CITATION.cff.tmpl`
   - `~/.claude/hooks/precommit_citation_cff.py`
   - `~/.claude/commands/cite-add.md`
2. **Content sketch.**
   - `CITATION.cff.tmpl`: CFF v1.2.0. Required fields per §A.2 of memo. Placeholders use **`<<KEY>>`** double-angle-bracket syntax (not `{{KEY}}` Jinja-style) to avoid YAML-flow-mapping parse failures during validation.
   - `precommit_citation_cff.py`: read CITATION.cff from argv[1]; substitute placeholders with sentinel strings (`<<TITLE>>` → `"title_placeholder"`, etc.); YAML parse; required-keys check against CFF v1.2.0 spec; non-zero on missing. If `cffconvert` available, also run `cffconvert --validate`. Fail-open if `cffconvert` absent and YAML well-formed.
   - `cite-add.md`: `argument-hint: "<DOI|URL>"`. Call CrossRef MCP `lookup` on `$ARGUMENTS`, parse author/title/year/venue, append `references: -` block.
3. **Dependencies.** R0; R1-B (CrossRef MCP).
4. **Verification gate.**
   - Placeholder substitution: `python -c "import yaml, pathlib, re; src=pathlib.Path('CITATION.cff.tmpl').read_text(); s=re.sub(r'<<(\w+)>>', r'placeholder_\1', src); yaml.safe_load(s)"` round-trips.
   - Fixture: CITATION.cff missing `version` → hook exits 1; complete fixture → exits 0.
   - If `cffconvert` installed: agreement with hook verdict on both fixtures.
5. **Rollback.** Delete three files.
6. **Risk surface.** CFF v1.3.0 drift; pin to 1.2.0.
7. **Effort.** S.

### R1-D — ADR scaffold (memo #10)

1. **Files to create.**
   - `~/.claude/templates/adr_TEMPLATE.md`
   - `~/.claude/commands/adr-new.md`
2. **Content sketch.** Nygard/MADR; sections per memo §C.1; auto-numbering by scanning `docs/decisions/ADR-*.md`.
3. **Dependencies.** R0.
4. **Verification gate.** Fixture with empty `docs/decisions/` → `/adr-new "Sample"` creates `ADR-0001-sample.md` with all 5 sections.
5. **Rollback.** Delete two files.
6. **Risk surface.** Auto-numbering race on concurrent invocation — solo workflow, low risk; doc-note.
7. **Effort.** XS.

### R1-E — Dataset manifest writer (NEW — closes critical R-1-3)

1. **Files to create.**
   - `~/.claude/scripts/build_data_manifest.py`
   - `~/.claude/templates/data_manifest_schema.json`
2. **Content sketch.**
   - `data_manifest_schema.json`: JSON Schema 2020-12. Required fields per `validate-data` SKILL.md §1: `source_uri`, `retrieval_timestamp` (ISO 8601), `retriever_script` (path), `retriever_git_head` (40-hex), `sha256` (64-hex), `license`, `snapshot_date`. Object keyed by relative path under `data/`.
   - `build_data_manifest.py`: walks `data/raw/`, `data/interim/`, `data/processed/`, `data/external/`; computes per-file SHA-256; writes `data/_manifest.json` atomically (same atomic-write idiom as R1-A); preserves existing entries' `source_uri`/`license`/`snapshot_date` if previously declared. CLI: `--check` (no-write verification) and default rebuild mode.
3. **Dependencies.** R0, R1-A (atomic-write idiom).
4. **Verification gate.**
   - Schema validates against itself: `jsonschema.Draft202012Validator.check_schema(json.load(open('data_manifest_schema.json')))`.
   - Fixture project with 3 files under `data/raw/` → `--check` produces `data/_manifest.json` with 3 entries, each 64-hex SHA.
   - Re-run `--check` exits 0 (idempotent).
   - Mutate one file → `--check` exits non-zero, indicates the drifted file.
5. **Rollback.** Delete two files.
6. **Risk surface.** Walking large `data/` trees is slow → document `--max-files` flag for very large datasets; not in scope this round.
7. **Effort.** S.

---

## 2. Round 2 — Wrappers (consume R1)

### R2-A — `/commit-with-provenance` (memo #11 + #22)

1. **Files to create.** `~/.claude/commands/commit-with-provenance.md` + `~/.claude/scripts/commit_with_provenance.py` (Python implementation; command file is a thin shell-out wrapper).
2. **Content sketch.** `argument-hint: "<subject> --role={idea|code|prose|audit|multi} [--scope-strict] [--no-repro <justification>]"`.
   - `--role` enum **mandatory** in publishing-cwd; ICMJE 2026 requires specific role.
   - `--no-repro` requires a free-text justification recorded in commit body; emits non-trailer audit note for downstream inspection.
   - Workflow:
     1. Verify staged changes exist; reject empty commits.
     2. **Inline pip freeze** (not from cache):
        - `py = find_project_python(cwd)` (re-use `session_start_provenance.find_project_python`).
        - `freeze = subprocess.run([py, '-m', 'pip', 'freeze'], capture=True).stdout` (or `uv pip freeze` fallback).
        - Write to project `logs/reproducibility/pip_freeze_{run_id}.txt`.
        - `pip_freeze_sha256 = sha256(freeze.encode('utf-8'))` (full 64-hex).
        - On missing project Python interpreter → fail hard with message: "No project venv detected. Run `bootstrap-project --venv` or invoke with `--no-repro <reason>` to override."
     3. Read `data/_manifest.json` (produced by R1-E) for `dataset_checksums`.
     4. Emit R1-A ReproLog at `logs/reproducibility/repro_log_{run_id}.json` with all fields populated.
     5. Compose trailers via `git interpret-trailers`:
        - `Repro-Log-Path: logs/reproducibility/repro_log_{run_id}.json`
        - `Repro-Log-SHA256: <64-hex of the log file content>`
        - `AI-Assistance: claude-opus-4-7 (role=<from --role>)` per ICMJE 2026
     6. Co-Authored-By: skip — already auto-injected by Claude Code per `settings.json::includeCoAuthoredBy: true`. **Note: outside Claude Code, raw `git commit` does not auto-add Co-Authored-By; users running this script outside Claude must add via global git template.**
     7. Subject validated against Conventional Commits 1.0.0 regex; reject malformed.
   - `--scope-strict` flag: if set, require staged changes to touch `artifacts/` OR `logs/` OR `research/`; else default = always trailer.
3. **Dependencies.** R1-A, R1-C (identity hygiene checkpoint), R1-E (data manifest source).
4. **Verification gate.**
   - Fixture repo, fixture project venv: stage a change, run `--role=code "feat: x"`. `git log -1 --format=%B` shows subject + `Repro-Log-Path:` + `Repro-Log-SHA256:` + `AI-Assistance:` trailers.
   - `git interpret-trailers --parse` round-trips.
   - Non-conventional subject (`xyz: bad`) → exit non-zero with reason.
   - Missing project Python → exit non-zero with `bootstrap-project --venv` hint UNLESS `--no-repro` set.
   - SHA verification: `sha256sum logs/reproducibility/repro_log_<id>.json` matches `Repro-Log-SHA256:` trailer.
   - Mutate the repro_log post-commit → re-verify trailer SHA mismatch (proves content-addressing works).
5. **Rollback.** Delete command + script. Existing commits untouched.
6. **Risk surface.** Trailer-key collisions with downstream tools (Gerrit). Solo single-author workflow unaffected.
7. **Effort.** M (half day) — full pip-freeze emission path adds complexity vs cache read.

### R2-B — `/bootstrap-project` (pillar A)

**Split into two phases for tractable audit-loop scoping:**

#### R2-B1 — bootstrap CLI + dir tree (no templates)
1. **Files to create.**
   - `~/.claude/commands/bootstrap-project.md`
   - `~/.claude/scripts/bootstrap_project.py`
2. **Content sketch.** CLI argparse; resolve `python_version` from the upstream library's `pyproject.toml::[project].requires-python`; create dir tree per memo §A.3 (always-subdirs + kind-conditionals); emit BOTH `runs/` AND `artifacts/runs/`; **idempotency mechanism explicit**:
   - On run, compute per-file SHA-256 of every existing target path.
   - Read `manifest.json` if present.
   - If `manifest.json` exists AND every target's current SHA matches its manifest entry AND `bootstrap_script_git_head` in manifest matches current `~/.claude` HEAD → exit 0 `in sync`.
   - If files missing → write missing ones; update manifest.
   - If template-source SHA drift detected (bootstrap_script_git_head differs from manifest) → exit non-zero with `--migrate` hint; never silent overwrite.
3. **Dependencies.** R0.
4. **Verification gate.**
   - `--dry-run` produces diff plan, no FS write.
   - First run creates dir tree; `manifest.json` exists; SHAs match re-walk.
   - Idempotent re-run: exits `in sync`, no writes.
   - Mutate one template SHA in `~/.claude/scripts/bootstrap_templates/`; re-run; exits non-zero with `--migrate` hint.
5. **Rollback (R2-B1 only).** Delete command + script. **Caveat: any projects already bootstrapped retain their manifest.json referencing the deleted `bootstrap_script_git_head` — downstream auditors recomputing template SHAs will fail.** Mitigation: before rollback, inventory bootstrapped projects via `find . -name manifest.json -exec grep -l bootstrap_script_version`; either freeze their manifests to a tarball or document the breakage and require user opt-in.
6. **Risk surface.** Drift management deferred to a separate `migrate-project` command (out of scope this round).
7. **Effort.** M.

#### R2-B2 — bootstrap templates (~25 .tmpl files)
1. **Files to create.** `~/.claude/scripts/bootstrap_templates/` containing ~25 `.tmpl` files using Python `str.format_map` placeholders (no Jinja dep). Names per memo §A.3.
2. **Content sketch.** Each template ports the relevant upstream-library artifact, parametrized for kind. Inline `# justify:` comments retained as source-only documentation (matplotlib-style ignored at runtime). Pre-commit chain in `.pre-commit-config.yaml.tmpl` registers `precommit_seed_guard.py` + `precommit_citation_cff.py` (R1-C).
3. **Dependencies.** R2-B1, R1-A (manifest format), R1-C (CITATION.cff template), R1-D (ADR-0001 seeded into `docs/decisions/`), R1-E (data manifest schema referenced from `validate-data` skill body).
4. **Verification gate.** Each template renders for each applicable kind; rendered output passes the format-specific validator (YAML for `.yaml`, TOML for `pyproject.toml`, etc.); fixture project bootstraps end-to-end with `session_start_provenance.py` emitting non-empty additionalContext.
5. **Rollback.** Delete `bootstrap_templates/`; same caveat re bootstrapped projects as R2-B1.
6. **Risk surface.** Template drift vs the upstream library — frozen template SHA in manifest.json; ~25 templates × audit-loop = significant per-template review surface.
7. **Effort.** L (2–4 days) — templates dominate the total work.

**Combined R2-B effort: XL (3–5 days).**

### R2-C — `skills/deliver-results` (pillar B)

1. **Files to create.**
   - `~/.claude/skills/deliver-results/SKILL.md`
   - `~/.claude/skills/deliver-results/assets/publication.mplstyle`
   - `~/.claude/skills/deliver-results/assets/save_figure.py`
   - `~/.claude/skills/deliver-results/assets/workbook_skeleton.py`
   - `~/.claude/skills/deliver-results/assets/report_card_quant.md`
   - `~/.claude/skills/deliver-results/assets/report_card_epi.md`
2. **Content sketch.** As in earlier draft. Critical compliance pin: `report_card_quant.md` lists Sharpe as a single KPI row alongside survival-first KPIs (terminal-wealth-q05, Calmar, profit-factor, R-multiple, MaxDD, Sortino). **No decision tree for Sharpe-CI selection.**
3. **Dependencies.** R1-A, R1-C, R2-B (consumes bootstrap manifest format).
4. **Verification gate.**
   - Figure pipeline: `plt.style.use(publication.mplstyle); save_figure(fig, 'test', target='single_col')` → png/svg/pdf at correct size and 300 dpi.
   - `pdffonts test.pdf` shows all fonts `emb`+`sub`.
   - `workbook_skeleton.py --selftest` creates xlsx with all 7 mandatory sheets.
   - **Sharpe-correction grep gate:** `grep -i "sharpe.*decision\|decision.*sharpe" report_card_quant.md` returns 0 matches; `grep -c "Sharpe" report_card_quant.md` returns exactly 1 (the KPI row).
   - Workbook README sheet metadata fields map 1:1 to R1-A ReproLog schema keys (no orphan fields).
5. **Rollback.** Delete `skills/deliver-results/`.
6. **Risk surface.** matplotlib/xlsxwriter API drift — pin in per-project pyproject.toml.
7. **Effort.** L.

---

## 3. Round 3 — Specialized

(memo #19 Sharpe-CI dropped per user directive 2026-05-15. R3-4 covers memo #18 + #21 only.)

### R3-1 — `/hypothesis-new` (memo #9)

1. **Files to create.** `~/.claude/commands/hypothesis-new.md`.
2. **Content sketch.** As in earlier draft. HID format regex taken from the upstream library's `hypothesis_backlog.md`.
3. **Dependencies.** R1-A (ReproLog), R1-B (CrossRef MCP), R2-A (commit-with-provenance), R2-B (template creates backlog).
4. **Verification gate.** Fixture empty backlog → `/hypothesis-new "Test"` creates HID-001 row; emits R1-A ReproLog for the registry mutation.
5. **Rollback.** Delete command.
6. **Risk surface.** HID format drift vs the upstream library.
7. **Effort.** S.

### R3-2 — `skills/pre-register-hypothesis` + `/preregister` (memo #5)

**Split for OSF optionality:**

#### R3-2a — internal-only pre-registration
1. **Files to create.**
   - `~/.claude/skills/pre-register-hypothesis/SKILL.md`
   - `~/.claude/skills/pre-register-hypothesis/assets/hypothesis_design_TEMPLATE.md`
   - `~/.claude/commands/preregister.md`
2. **Content sketch.** 11-section frozen-design template port from the upstream library. Freeze procedure: write → SHA-256 → emit R1-A ReproLog with `config_resolved_sha256` = design.md SHA → commit via R2-A. R2-A trailers therefore embed the pre-reg SHA via `config_resolved_sha256` (already in R1-A schema — no new trailer key needed).
3. **Dependencies.** R1-A, R2-A, R3-1.
4. **Verification gate.** `/preregister HID-001` produces `research/01_hypothesis_register/HID-001/design.md` with all 11 sections; R1-A ReproLog at `logs/reproducibility/repro_log_<run_id>.json` with `config_resolved_sha256` matching design.md content SHA.
5. **Rollback.** Delete skill dir + command.
6. **Risk surface.** Template drift vs the upstream library.
7. **Effort.** M.

#### R3-2b — OSF API integration (deferred; depends on §5 Q6 decision)
1. **Files to create.** Add `osf` server to R1-B `mcp.json`; thin OSF-upload step in `preregister.md`.
2. **Dependencies.** R3-2a, R1-B, §5 Q6 resolved to `OSF`.
3. **Effort.** S, blocked on Q6.

### R3-3 — `skills/power-analysis` (memo #7)

1. **Files to create.** `~/.claude/skills/power-analysis/SKILL.md`.
2. **Content sketch.** Gate-position diagram: pre-register (R3-2) → power-analysis (R3-3) → validate-data → statistical-analysis. Cohen 1988 effect sizes; statsmodels.stats.power; Hoenig & Heisey 2001 retrospective-power-forbidden. Output: `research/01_hypothesis_register/<HID>/power_analysis_{YYYY-MM-DD}.md` with grid search over n for fixed (effect_size, alpha, power_target). **`# justify:` enforcement is documentation-only this round** — no new hook. SKILL.md instructs user to add `# justify:` neighbors; verification by audit-remediate-loop quant-auditor at use-time, not by a pre-write hook.
3. **Dependencies.** R3-2a, R1-A.
4. **Verification gate.**
   - Fixture: `(test_type=two-sample, effect=Cohen-d=0.5  # justify: fixture-only, not default, alpha=0.05  # justify: fixture-only, power=0.8  # justify: fixture-only)` → output md contains analytical n ≈ 64/group matching `tt_ind_solve_power` within tolerance ±1.
   - Output md has sibling `repro_log_<run_id>.json` validating against R1-A schema.
5. **Rollback.** Delete skill file.
6. **Risk surface.** Fixture defaults misread as recommended; `# justify: fixture-only` annotation visible in skill doc.
7. **Effort.** S.

### R3-4 — inline updates to `skills/statistical-analysis/SKILL.md` (memo #18, #21)

1. **Files to create.** None.
2. **Files to modify.** `~/.claude/skills/statistical-analysis/SKILL.md` — append under §3:
   - `Autocorrelation, HAC SE → Newey-West 1994 data-driven bandwidth OR Andrews 1991 plug-in. statsmodels.stats.sandwich_covariance.cov_hac.`
   - `Time-series resample → stationary bootstrap (Politis-Romano 1994) with auto block length per Politis-White 2004. arch.bootstrap.StationaryBootstrap.`
   Add the two references at the file's References section. **Explicitly add no Sharpe-specific block** — Sharpe-CI methodology stays in [`rules/quant-project.md`](../../rules/quant-project.md) per user directive.
3. **Dependencies.** None (doc edit).
4. **Verification gate.** Grep both methods + citations; literature-check re-run returns 0 critical/major; `grep -i sharpe ~/.claude/skills/statistical-analysis/SKILL.md` returns 0 matches.
5. **Rollback.** `git revert` the edit commit.
6. **Risk surface.** Minimal.
7. **Effort.** XS.

### R3-5 — `skills/pit-canary` (memo #20)

1. **Files to create.** `~/.claude/skills/pit-canary/SKILL.md`.
2. **Content sketch.** Pattern port from the upstream library's leak-canary module (`backtest/leak_canaries.py`). **Test statistic explicit**: inject a known future-knowing feature with a fixture effect size; run model fit; compute permutation-test p-value (n_perm=1000 # justify: upstream-library default) for the future-feature's marginal contribution. Canary FAILS if p > 0.01 # justify: upstream-library default (i.e., the future feature does NOT dominate — implies pipeline already has a leak). Invoked by existing `quant-auditor`; no new agent.
3. **Dependencies.** R1-A, R0; existing `quant-auditor`.
4. **Verification gate.**
   - Fixture with deliberately-leaked feature → canary p ≥ 0.01 → FAIL.
   - Clean fixture → canary p < 0.01 → PASS.
   - Each run emits R1-A ReproLog with `rng_seed` for the permutation test.
5. **Rollback.** Delete skill file.
6. **Risk surface.** Threshold mismatch with future upstream-library updates; documented via inline annotation.
7. **Effort.** S.

### R3-6 — `skills/multipletest-gate` + template (memo #17)

1. **Files to create.**
   - `~/.claude/skills/multipletest-gate/SKILL.md`
   - `~/.claude/templates/multipletest_family_TEMPLATE.yaml`
2. **Content sketch.** Hansen SPA / White Reality Check / BH FDR / Holm. Method selection per `multipletest_family.yaml::correction_method`. Project's raw p-values supplied by the user's actual inference run (NOT by R3-4, which is doc-only).
3. **Dependencies.** R1-A, R3-1 (HIDs feed registry). **No dep on R3-4** — R3-4 is doc-only, doesn't produce p-values.
4. **Verification gate.** Fixture: replay Hansen 2005 Table 1 (10 forecasters, IID resample) → adjusted thresholds match published values to 3 decimal places. Refuses to add 11th test without registry update. Emits R1-A ReproLog with `rng_seed` for bootstrap.
5. **Rollback.** Delete skill dir + template.
6. **Risk surface.** Family-boundary definition is project-specific; doc-note in skill body.
7. **Effort.** S.

### R3-7 — `agents/dag-drafter` + DAG template (memo #6)

1. **Files to create.**
   - `~/.claude/agents/dag-drafter.md`
   - `~/.claude/templates/dag_TEMPLATE.dag`
2. **Content sketch.** As in earlier draft. dagitty syntax; back-door criterion (Pearl 2009); cwd-scoped to `rules/population-health.md` glob.
3. **Dependencies.** R1-A, R2-B2 (epi-kind bootstrap creates `docs/protocol/`).
4. **Verification gate.** Fixture research question → valid dagitty file; parser accepts; back-door adjustment set printed; sibling R1-A ReproLog emitted with `config_resolved_sha256` = DAG file SHA + `dataset_checksums` field including the research-question prompt SHA.
5. **Rollback.** Delete two files.
6. **Risk surface.** dagitty syntax breaking changes rare.
7. **Effort.** S.

### R3-8 — DUA/IRB tracker + PHI guard (memo #14)

1. **Files to create.**
   - `~/.claude/templates/compliance/dua_TEMPLATE.md`
   - `~/.claude/hooks/pre_write_phi_guard.py`
2. **Files to modify.** `~/.claude/settings.json` — **explicit insertion: append a second object** `{"type": "command", "command": "python \"~/.claude/hooks/pre_write_phi_guard.py\""}` to the **existing** `hooks` array under the existing `PreToolUse` matcher `Write|Edit|MultiEdit|NotebookEdit`. Both hooks run; an `ask` decision from either prompts the user (PreToolUse short-circuits on first `deny` but not on `ask`).
3. **Content sketch.** Template: 45 CFR §46.111 checklist + DUA fields. Hook: HIPAA Safe Harbor 18 identifiers regex; cwd-scoped to `rules/population-health.md` glob; `permissionDecision: ask` (not deny); fail-open; excludes `tests/`/`fixtures/` paths (mirror `pre_write_seed_guard.py`).
4. **Dependencies.** R0.
5. **Verification gate.**
   - Fixture epi-cwd: write containing `123-45-6789  # justify: fixture-only synthetic SSN` → hook returns `ask` with SSN-pattern reason.
   - Non-epi cwd: same write → no prompt.
   - Synthetic SSN in `tests/` path → no prompt.
6. **Rollback.** Delete template; revert settings.json insertion (`git diff` shows the appended hook block removed); delete hook file.
7. **Risk surface.** False positives on synthetic IDs in non-excluded paths.
8. **Effort.** M.

### R3-9 — manuscript templates (memo #4)

**Status: materially blocked on §5 Q1 + Q2 + Q3 + Q4. Effort estimate conditional on decisions.**

1. **Files to create** (once unblocked):
   - `~/.claude/templates/manuscript_strobe_TEMPLATE.qmd` (or `.md` if Q4=raw markdown)
   - `~/.claude/templates/manuscript_consort_TEMPLATE.qmd`
   - `~/.claude/templates/manuscript_tripod_TEMPLATE.qmd`
   - `~/.claude/templates/manuscript_ssrn_TEMPLATE.qmd`
2. **Content sketch.** Per memo §B.7-B.8. STROBE 22 items / CONSORT 25 / TRIPOD+AI 27 / SSRN abstract schema as HTML comments. Identity-hygiene checklist at file top. AI-assistance section per ICMJE 2026.
3. **Dependencies.** R1-C (CITATION.cff authoritative author record), R2-A (commits). **§5 Q1–Q4 must resolve before build.**
4. **Verification gate** (once unblocked). `quarto render manuscript_strobe_TEMPLATE.qmd --to html` succeeds; no real-name strings; reporting-standard items 1–22 referenced.
5. **Rollback.** Delete four templates.
6. **Risk surface.** Quarto installation cost; PDF engine cost (Q3).
7. **Effort.** L (conditional on Q1+Q2+Q3+Q4 resolved; ~25-item STROBE × 4 standards = significant content).

### R3-10 — `agents/epi-auditor` (memo #24)

1. **Files to create.** `~/.claude/agents/epi-auditor.md`.
2. **Content sketch.** As in earlier draft. E-value (VanderWeele & Ding 2017) mandatory for primary causal estimates; cwd-scoped to `rules/population-health.md` glob.
3. **Dependencies.** R3-7 (DAG agent output is a hard input for adjustment-set verification). **Soft dep on R3-9** (STROBE-checklist coverage tags improve audit quality but not required — agent functions with reduced coverage if templates absent). E-value source = project's `statistical-analysis` output JSON (existing infra, not new dep).
4. **Verification gate.** Fixture epi analysis lacking E-value → `critical` finding. With E-value → `accept`. Output JSON schema matches `quant-auditor` schema.
5. **Rollback.** Delete agent file.
6. **Risk surface.** Agent inventory bloat — tight cwd scoping.
7. **Effort.** S.

---

## 4. Cross-cutting concerns

- **JSON Schema utility.** Pin `jsonschema>=4.18` (Draft 2020-12) in `pyproject.toml.tmpl` dev-deps (R2-B2).
- **Per-item audit-remediate-loop.** Each build emits structured audit_trail per skill spec; 3-round cap; output to `~/.claude/docs/audits/`.
- **Provenance trailers.** Items pre-R2-A (R0, R1-A, R1-B, R1-C, R1-D, R1-E) committed manually with plain Conventional Commits subjects; trailer-only commits begin from R2-B onward via `/commit-with-provenance`.
- **Identity hygiene checkpoints.** R1-C, R2-B, R2-C, R3-2, R3-9 enforce publishing-identity + no-real-name checks.
- **Magic-numbers policy.** Every fixture numeric in this plan is annotated `# justify: fixture-only`. Project-level defaults derive from pre-registration `design.md` (R3-2a), not from these fixtures.
- **Filename rule.** `{type}_{description}_{YYYY-MM-DD}.{ext}` for all generated artifacts.

---

## 5. Open decisions gating specific items

| Memo Q | Topic | Gates | Default if unresolved |
|---|---|---|---|
| Q1 | `[build-system]` in pyproject template | R2-B2 | Defer (upstream-library pattern) |
| Q2 | Docs-site renderer | R2-B2, R3-9 | Quarto for manuscripts (R3-9), none for docs site (R2-B2) |
| Q3 | PDF engine | R3-9 | tectonic |
| Q4 | Quarto vs raw markdown longform | R3-9 | Quarto (stacks on Q1/Q2) |
| Q5 | Zotero MCP | R1-B | Drop (placeholder comment) |
| Q6 | OSF vs arXiv pre-reg target | R3-2b | OSF if token available; else R3-2a internal-only |
| Q7 | commit-with-provenance scope | R2-A | Always-add trailers |

**Materially blocked:** only R3-9 (Q1+Q2+Q3+Q4 stack). All other items have defaults that allow build to proceed.

---

## 6. Build sequence — dependency graph

**ASCII tree below shows topological build order; authoritative dependencies are the cross-check table after the tree. If the two disagree, the table wins.**

```
R0
├── R1-A ──┬─► R1-E
│         │
│         ├─► R2-A ──┬─► R2-B1 ──► R2-B2 ──► R2-C
│         │         │                          ├─► R3-1 ──► R3-2a ──► R3-2b (blocked: Q6)
│         │         │                          │              │
│         │         │                          │              ├─► R3-3 (deps R3-2a, R1-A)
│         │         │                          │              └─► R3-6 (deps R1-A, R3-1; NOT R3-4)
│         │         │                          │
│         │         │                          ├─► R3-4 (deps none, but ordered after R2-C for clean review)
│         │         │                          │
│         │         │                          ├─► R3-5 (deps R1-A, R0; existing quant-auditor)
│         │         │                          │
│         │         │                          └─► R3-7 (deps R1-A, R2-B2 for docs/protocol/)
│         │         │                                    │
│         │         │                                    └─► R3-10 (deps R3-7; soft dep R3-9)
│         │         │
│         │         └─► R3-8 (deps R0)
│         │
│         └─► (R1-A consumed by every artifact-producing item)
│
├── R1-B ──┬─► R1-C ──► (consumed by R2-A, R2-B2, R3-9)
│         │
│         └─► R3-2b (blocked on Q6)
│
├── R1-D ──► R2-B2 (ADR-0001 seeded into bootstrap)
│
└── R3-9 (deps R1-C, R2-A; BLOCKED on Q1+Q2+Q3+Q4)
```

Dependency-level cross-check (item ID → declared deps):
- R0: ∅
- R1-A: R0
- R1-B: R0
- R1-C: R0, R1-B
- R1-D: R0
- R1-E: R0, R1-A
- R2-A: R1-A, R1-C, R1-E
- R2-B1: R0
- R2-B2: R2-B1, R1-A, R1-C, R1-D, R1-E
- R2-C: R1-A, R1-C, R2-B (i.e., R2-B2)
- R3-1: R1-A, R1-B, R2-A, R2-B2
- R3-2a: R1-A, R2-A, R3-1
- R3-2b: R3-2a, R1-B
- R3-3: R3-2a, R1-A
- R3-4: ∅ (doc edit; ordered after R2-C for review continuity)
- R3-5: R1-A, R0, existing quant-auditor
- R3-6: R1-A, R3-1 (no dep on R3-4)
- R3-7: R1-A, R2-B2
- R3-8: R0
- R3-9: R1-C, R2-A; BLOCKED on Q1+Q2+Q3+Q4
- R3-10: R3-7; soft R3-9

**Total: 21 sub-items** (R0 + 5 R1 + 4 R2-subitems + 11 R3-subitems). Memo mapping: 13 NEEDED items + 2 pillars + R0 + R1-E + R3-4 inline = 18 plan rows, expanded to 21 sub-items by splitting R2-B → B1/B2 and R3-2 → 2a/2b for tractable audit scoping.

---

## 7. Estimated total effort

| Item | Effort |
|---|---|
| R0 | XS |
| R1-A | S |
| R1-B | XS |
| R1-C | S |
| R1-D | XS |
| R1-E | S |
| R2-A | M |
| R2-B1 | M |
| R2-B2 | L (2–4 days; ~25 templates × audit-loop) |
| R2-C | L |
| R3-1 | S |
| R3-2a | M |
| R3-2b | S (blocked on Q6) |
| R3-3 | S |
| R3-4 | XS |
| R3-5 | S |
| R3-6 | S |
| R3-7 | S |
| R3-8 | M |
| R3-9 | L (blocked on Q1–Q4) |
| R3-10 | S |

**Rough sum:** R0–R1 (~1 day), R2 (~5 days), R3 unblocked (~3 days), R3 blocked (~3 days when decisions land). **Total ~12 days** of focused work, distributed across audit-loops per item.
