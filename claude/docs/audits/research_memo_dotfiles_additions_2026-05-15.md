---
title: Dotfiles additions — scaffolding, results-delivery, gap analysis
date: 2026-05-15
type: research_memo
status: round-1-final (audit-remediate-loop round 1 complete; exit conditions met — see audit_trail)
author: the author's publishing identity
scope: ~/.claude config additions for github.com/s-koirala/dotfiles
git_head_at_authoring: (untracked — ~/.claude is not yet a git repo; see pillar A round-0 prerequisite)
pip_freeze_sha256: n/a (memo authoring; no code execution)
dataset_checksums: upstream-library layout/source references (hashed at audit-trail emission, see audit_trail_dotfiles_additions_2026-05-15.md)
rng_seed: n/a (no sampling)
model_commit: n/a (no model)
ai_assistance: claude-opus-4-7 (3 parallel research subagents + main-session synthesis + literature-check + quant-auditor audit round 1; per ICMJE 2026 [^31])
reporting_standard: research memo (no STROBE/CONSORT/etc. applies)
reproducibility_log: docs/audits/audit_trail_dotfiles_additions_2026-05-15.md
---

# Research memo — proposed additions to ~/.claude

## 0. Executive summary

Three coordinated additions are recommended for `~/.claude` (mirror: `s-koirala/dotfiles`). All are additive — no existing skill, agent, hook, rule, or settings file requires modification.

| Pillar | Artifact class | Count | Headline path |
|---|---|---|---|
| A. Scaffolding | 1 slash command + 1 script + ~25 templates | 1+1+25 | `~/.claude/commands/bootstrap-project.md` |
| B. Results delivery | 1 skill + 4 assets | 1+4 | `~/.claude/skills/deliver-results/SKILL.md` |
| C. Gap fills | 5 priority items + 13 lower-priority | 18 | mixed (skills/commands/agents/hooks/templates) |

**Implementation order:** see §6, which is the single source of truth. Round-1 foundations (no internal deps): emit-repro-log, MCP config, CITATION.cff scaffolding, ADR scaffold. Round-2 (consumes round-1): commit-with-provenance, bootstrap-project, deliver-results. Round-3 (specialized): hypothesis-new, pre-register, power-analysis, statistical-analysis inline updates, pit-canary, multipletest-gate, dag-drafter, IRB/DUA, manuscript templates, E-value enforcement.

**Cap on novel parameters.** The only numeric literals introduced are (a) slide dimensions cited from Microsoft Office documentation [^19], (b) journal DPI cited from Nature artwork guide [^13], and (c) the prompt-reuse threshold quoted verbatim from the user's CLAUDE.md (`>5 times`). No magic numbers introduced.

---

## 1. Pillar A — Project scaffolding

### A.1 Decision: slash command, not skill

Justification per Anthropic docs [^1][^2]: slash commands are explicit user-initiated procedures with `$ARGUMENTS`; skills are model-invoked capabilities triggered by `description:` matching. Bootstrap is always user-initiated. The user's existing pattern already follows this split — [`audit-loop.md`](../../commands/audit-loop.md), [`lit-check.md`](../../commands/lit-check.md), [`reproduce.md`](../../commands/reproduce.md) are command thin-wrappers around the heavy skills.

### A.2 Files to create

| Path | Role |
|---|---|
| [`~/.claude/commands/bootstrap-project.md`](../../commands/bootstrap-project.md) | Slash-command entrypoint with `argument-hint` |
| [`~/.claude/scripts/bootstrap_project.py`](../../scripts/bootstrap_project.py) | Python implementation (idempotent, `--dry-run`, rollback-on-fail) |
| `~/.claude/scripts/bootstrap_templates/` | ~25 `.tmpl` files (string-format, no jinja dep) |

Note: `~/.claude/scripts/` is a new subdirectory — the repo (`s-koirala/dotfiles`) already has `claude/scripts/` populated, so the global `.claude` directory adopting it is consistent.

### A.3 Generated layout

Top-level files (always): `CLAUDE.md`, `README.md`, `CHANGELOG.md`, `CITATION.cff`, `LICENSE`, `directory_structure.md`, `manifest.json`, `pyproject.toml`, `.gitignore`, `.gitattributes`, `.pre-commit-config.yaml`. Kind-conditional: `hypothesis_backlog.md` (quant), `docs/protocol/protocol_v0.md` (epi), `manuscript/manuscript.md` + `docs/ai_assistance_statement.md` (publishing).

Subdirs (always): `src/`, `tests/`, `scripts/`, `notebooks/`, `data/{raw,interim,processed,external}/`, `docs/{audits,decisions,literature,methodology,reports,research_notes,templates}/`, `research/`, `reports/`, `artifacts/{models,runs}/`, `config/`, `logs/reproducibility/`, `outputs/`. Kind-extras:

| Kind | Extra subdirs |
|---|---|
| quant | `config/instruments/`, `research/01_hypothesis_register/`, `research/00_literature_review/`, `logs/promotions/` |
| epi | `docs/protocol/`, `data/processed/_provenance/`, `logs/imputation/` |
| publishing | `manuscript/`, `manuscript/figures/`, `manuscript/supplement/`, `submissions/` |
| generic | (none) |

Mapping to the upstream library's layout: 1:1 for `src/`, `tests/`, `scripts/`, `notebooks/`, `data/raw/`, `data/interim/`, `data/processed/`, `data/external/`, `docs/{audits,decisions,literature,methodology,reports,research_notes,templates}/`, `research/`, `reports/`, `artifacts/{models,runs}/`, `config/`, `logs/reproducibility/`, `logs/promotions/`. The upstream library has BOTH a top-level `runs/` AND `artifacts/runs/` as sibling directories — bootstrap emits both to preserve compatibility with any existing tooling that hard-codes `runs/`; consolidation, if desired, is deferred to a per-project ADR.

Standards conformance:
- `CHANGELOG.md` per Keep a Changelog 1.1.0 [^3].
- `CITATION.cff` per CFF v1.2.0 [^4]; Zenodo-recognized for DOI binding.
- `directory_structure.md` per TIER Protocol 4.0 Metadata component [^5].
- ADR seed file per Nygard 2011 / MADR [^6].
- src-layout per PyPA discussion [^7] (prevents accidental sys.path imports of working-tree code over the installed package).
- Conventional Commits v1.0.0 [^8] for the initial `chore: bootstrap …` commit.
- SemVer 2.0.0 [^9] for bootstrap-script versioning.

### A.4 Reproducibility

The bootstrap script writes a `manifest.json` at project root containing:
- `bootstrap_script_version` (SemVer) and `bootstrap_script_git_head`
- `python_version` — read from the upstream library's `pyproject.toml` `[project] requires-python` at bootstrap time and pinned to that range; rationale is wheel-availability for `numba`/`llvmlite` per [numba installation matrix](https://numba.readthedocs.io/en/stable/user/installing.html). User override via `--python-version` flag.
- per-file SHA-256 of every templated file written
- `rules_file` (which `~/.claude/rules/*.md` activates for the chosen `--kind`)
- `venv_created` (bool — see §A.5 hook compatibility)
- `timestamp_utc`

The bootstrap is **itself a reproducible artifact**. Sandve 2013 Rules 1+2+10 [^10] satisfied: every result traces back to the bootstrap commit SHA + template version.

### A.5 Hook integration

- [`session_start_provenance.py`](../../hooks/session_start_provenance.py) (lines 23, 38–46, 53–90, 97–101, 108–119): expects `pyproject.toml`/lockfile, `.venv/`, `.git/HEAD`, `data/`. Bootstrap unconditionally creates `pyproject.toml`, `.git/`, and `data/`; the venv is created by `uv venv` + `uv sync` as a post-template step (else the hook's deps-sha field falls back from the venv interpreter to `uv pip freeze` via lockfile, and degrades to `None` if neither is reachable). The `venv_created` field in `manifest.json` flags this so missing deps-sha is auditable. **Hook compatibility holds, provided `uv sync` runs before the first session.**
- [`session_end_audit_log.py`](../../hooks/session_end_audit_log.py) (lines 40–48): creates `docs/audits/` if missing; bootstrap creates upfront so the first session's `session_trail_*` lands alongside future `audit_trail_*` from `audit-remediate-loop`. Filenames disambiguate. **No hook changes required.**
- [`pre_write_seed_guard.py`](../../hooks/pre_write_seed_guard.py) / [`precommit_seed_guard.py`](../../hooks/precommit_seed_guard.py): activate on any `.py`/`.ipynb` write; bootstrap-emitted files are templated text not triggering seed checks. **No hook changes required.**

### A.6 Open questions (pillar A)

1. **`[build-system]` declaration in pyproject template?** The upstream library defers it as a known follow-up. Add `hatchling`/`setuptools>=68` at bootstrap, or preserve the deferred-state pattern?
2. **Documentation site renderer?** Emit Quarto `_quarto.yml` (richer; PDF/HTML/docx from one source), Sphinx `conf.py` (Python-idiomatic), or none?
3. **Zenodo automation for `--kind=publishing`?** Emit `.zenodo.json` + a GitHub Action that auto-deposits on release tags? Requires user's Zenodo concept-DOI.
4. **`data/` versioning strategy?** Plain gitignore + `_provenance/` exceptions (upstream-library pattern) vs DVC vs git-LFS — confirm same default for epi/publishing kinds.
5. **Pre-commit Ruff pin?** Lock to v0.6.9 (upstream-library parity) or float to latest at bootstrap time?

---

## 2. Pillar B — Results delivery

### B.1 Decision: one skill, branches on cwd-rule

A single skill `deliver-results` because the pipeline (rcParams → save artifact → register in workbook/deck → log repro metadata) is identical across project classes; the divergence is two report-card templates. Splitting into `deliver-epi` / `deliver-quant` duplicates ~80% of the code. The `audit-remediate-loop` precedent confirms one skill + branching > two skills + overlap.

### B.2 Files to create

| Path | Role |
|---|---|
| [`~/.claude/skills/deliver-results/SKILL.md`](../../skills/deliver-results/SKILL.md) | Skill body |
| [`~/.claude/skills/deliver-results/assets/publication.mplstyle`](../../skills/deliver-results/assets/publication.mplstyle) | matplotlib style |
| [`~/.claude/skills/deliver-results/assets/save_figure.py`](../../skills/deliver-results/assets/save_figure.py) | Figure-export helper with `pdffonts` verification |
| [`~/.claude/skills/deliver-results/assets/workbook_skeleton.py`](../../skills/deliver-results/assets/workbook_skeleton.py) | `xlsxwriter` template (README/parameters/methods/results/figures/audit_trail sheets) |
| [`~/.claude/skills/deliver-results/assets/report_card_quant.md`](../../skills/deliver-results/assets/report_card_quant.md) | Backtest disposition-memo template |
| [`~/.claude/skills/deliver-results/assets/report_card_epi.md`](../../skills/deliver-results/assets/report_card_epi.md) | STROBE/CONSORT/STARD/TRIPOD report-card template |

### B.3 matplotlib stylesheet parameters

Every value is cited; no defaults are unjustified.

| Param | Value | Source |
|---|---|---|
| `font.sans-serif` | DejaVu Sans, Liberation Sans, Arial, Helvetica | Matplotlib default since v2.0 [^11]; Liberation = Red Hat metric-compatible Arial substitute [^12]; Helvetica/Arial preferred by Nature [^13]. Avoids font-bundling step on minimal containers. |
| `font.size` | 9.0 | Journal body-text size (Nature artwork guide [^13]) |
| `figure.figsize` | 3.5, 2.7 | Nature single-column 89 mm = 3.50" [^13] |
| `figure.dpi` | 100 | Matplotlib default; sufficient for notebook display |
| `savefig.dpi` | 300 (raster default; bump to 600 via `target=print_600` for line-art / combination figures per Nature artwork guide [^13]) | Nature: 300 dpi photograph/halftone minimum; 600 dpi for line art and combination figures. The user opts in to 600 via `target=` parameter. |
| `pdf.fonttype`, `ps.fonttype` | 42 | Matplotlib `fonttype=42` yields TrueType embedding in PDF (Type 42 is PostScript's TrueType wrapper [^14]); editable in Illustrator; avoids Type-3 subsetting. |
| `svg.fonttype` | none | Text as text (selectable/editable), not paths |
| `image.cmap` | viridis | Perceptually uniform, colorblind-safe; van der Walt & Smith 2015 [^15], peer-style derivation Kovesi 2015 [^74]; Crameri 2020 lists viridis among acceptable widely-available alternatives while primarily advocating Scientific colour maps (batlow, vik) [^16] |
| `axes.prop_cycle` | Okabe-Ito 8-color (#000000, #E69F00, #56B4E9, #009E73, #F0E442, #0072B2, #D55E00, #CC79A7) | Wong 2011 colorblind-safe palette [^17]. Note: matplotlib's `tab10` is Tableau-10 / D3 category10, distinct from Wong; we adopt Okabe-Ito explicitly. |
| `axes.spines.{top,right}` | False | Tufte 2001 data-ink minimization [^18] |
| `{x,y}tick.direction` | in | Tufte 2001 §3 |
| `legend.frameon` | False | Tufte 2001 |
| `text.usetex` | False | Avoids system TeX dependency; portability |

Target figure sizes (table-driven; user passes `target=` to `save_figure`):

| target | size (in) | source |
|---|---|---|
| `single_col` | 3.5 × 2.7 | Nature 89 mm [^13] |
| `two_col` | 7.2 × 4.5 | Nature 183 mm [^13] |
| `ppt_full` | 13.333 × 7.5 | MS Office default 16:9 [^19] |
| `ppt_half` | 6.5 × 7.5 | half of full minus 1/3" gutter |
| `ppt_quad` | 6.5 × 3.5 | quarter minus gutters |
| `print_600` | (target-relative) at 600 dpi | Nature combination-figure recommendation [^13] |

Three-format export bundle (PNG@300dpi + SVG + PDF). Post-write `pdffonts` check [^20] verifies every font shows `emb`+`sub`; non-zero exit raises.

### B.4 Tabular outputs

| Domain | Tool | Citation |
|---|---|---|
| Epi Table 1 (Python) | `tableone` | Pollard et al. 2018 JAMIA Open 1(1):26 [^21] |
| Epi Table 1 (R) | `gtsummary` | Sjoberg et al. 2021 R J 13(1) [^22] |
| Publication tables (Python) | `great_tables` | Iannone, Cheng, Schloerke [^23] |
| Publication tables (R) | `gt` | Iannone et al. [^23] |

Auto-fill coverage by reporting standard (tableone):

| Standard | Auto | User-authored |
|---|---|---|
| STROBE 22-item [^24] | 14, 15 | 1–13, 16–22 |
| CONSORT 2010 [^25] | 15 (baseline by group) | 1–14, 16–25 |
| STARD 2015 [^26] | 19, 20 | 1–18, 21–32 |
| TRIPOD+AI 2024 [^27] | 13b | 1–13a, 14–27 |
| PRISMA 2020 [^28] | flow diagram (via prisma2020 shiny [^29]) | all narrative items |

**Storage convention (mandatory):** every table emits source notebook + frozen CSV (`artifacts/tables/{slug}.csv`) + rendered HTML/PNG@300dpi. CSV is canonical; HTML/PNG are regenerable derivatives.

### B.5 Excel: xlsxwriter

Decisive comparison (xlsxwriter wins for write-only publication pipelines):

| Feature | openpyxl 3.x | xlsxwriter 3.x [^30] | Winner |
|---|---|---|---|
| Read existing .xlsx | yes | no (write-only) | openpyxl (ad-hoc only) |
| Native charts | partial | full object model | xlsxwriter |
| Sparklines | no | yes | xlsxwriter |
| Constant-memory mode for >1M rows | no | yes | xlsxwriter |
| Conditional formatting | yes | broader rule set | xlsxwriter |

Mandatory sheet order: `README → parameters → methods → results_* → figures → audit_trail → references`. README sheet header literal:

```
Results Workbook
Slug:                {type}_{description}_{YYYY-MM-DD}
Git HEAD:            {full sha} ({short})
Project venv:        uv pip freeze SHA-256 = {sha}
Dataset:             {dataset name}; SHA-256 = {sha}; snapshot = {ISO}
RNG seed:            {int}
Model commit:        {sha} or N/A
AI-assistance:       {models + roles per ICMJE 2026 [^31]}
Reporting standard:  {STROBE | CONSORT | STARD | TRIPOD | PRISMA | quant-backtest}
Generated by:        ~/.claude/skills/deliver-results v{semver}
Generated at (UTC):  {ISO8601}
```

### B.6 Slide deck

`python-pptx` [^32] assembles `artifacts/decks/{slug}.pptx` from `reports/{topic}/deck.yaml` manifest (version-controlled). Slide dimensions 13.333" × 7.5" (MS default 16:9 [^19]). PNG@300dpi default for figure inserts; EMF supported but rasterized PNG avoids cross-platform PowerPoint EMF rendering divergence.

### B.7 Quant report card (verbatim sections — see `report_card_quant.md` draft)

YAML frontmatter inherited from the upstream library's convention: `substrate_dataset_checksum`, `sidecar`, `sidecar_scientific_payload_sha256`, `git_head_at_authoring`, `rng_seed`, `pip_freeze_sha256`, `reporting_standard`, `ai_assistance`. Body sections: Universe & snapshot · Rebalance & execution · Returns convention · Splitter · Headline performance (with cited methods) · NW-HAC SE · Diagnostics · Disposition · Reproducibility appendix.

**Sharpe is reporting-only, not an optimization target** (user directive 2026-05-15). The headline performance table lists survival-constrained and risk-adjusted KPIs side by side; Sharpe appears as one row without elaboration. CI methodology for Sharpe — when reported — defers to [`rules/quant-project.md`](../../rules/quant-project.md), which already names Lo 2002 [^33], Opdyke 2007 [^34], and Ledoit-Wolf 2008 [^35] under cwd-scoped quant rules. No decision tree is inlined here.

Performance-table KPIs (one row each, with citation):
- Terminal-wealth-q05 (survival-constrained tail) — primary promotion gate per the upstream library's KPI list.
- Calmar ratio (annualized return / |MaxDD|).
- Profit factor (gross gain / gross loss).
- R-multiple distribution (per-trade reward / risk).
- MaxDD, MaxDD duration.
- Sortino — Sortino & Price 1994 [^42].
- Sharpe — KPI row only; CI deferred to project rule.
- Deflated Sharpe (if reporting Sharpe and multiple-tested) — Bailey & López de Prado 2014 [^38].
- PBO — Bailey et al. 2016 [^39].
- Turnover (annualized), capacity estimate.

HAC standard errors (any KPI requiring time-series SE): Newey & West 1994 [^40] data-driven OR Andrews 1991 [^41] plug-in.

### B.8 Epi report card

Same frontmatter pattern, body keyed on reporting standard claimed at top of doc. Auto-fill columns generated from `statistical-analysis` output JSON. PRISMA flow diagram externalized to PRISMA2020 Shiny [^29] (not re-implemented).

### B.9 Open questions (pillar B)

1. **Quarto vs raw markdown for longform reports?** Quarto adds CSL/citations + one-command multi-format render but introduces non-Python toolchain. Default proposed: raw markdown + pandoc; flip to Quarto only if you want native CSL.
2. **PDF engine?** tectonic (hermetic, Rust-pinnable), xelatex (system TeX Live), weasyprint (HTML→PDF, no LaTeX). Default proposed: tectonic for reproducibility.
3. **great_tables Python vs gt R?** Python reached near-parity in 2024; stay Python-first?
4. **batlow / cmcrameri as default?** Third-party install. Default to viridis (stdlib) and require opt-in for batlow, or pin cmcrameri as dev-dep?
5. **Slide template — Anthropic theme-factory vs raw python-pptx?** Theme-factory may produce nicer decks but introduces a cross-skill dependency.

---

## 3. Pillar C — Gap analysis & additions

### C.1 Upstream-library pattern extraction

Patterns currently in the upstream library that should be globalized into `~/.claude`:

| Upstream-library artifact | Pattern | Proposed `~/.claude` formalization |
|---|---|---|
| `utils/reproducibility.py` | 13-field ReproLog dataclass with atomic write | `skills/emit-repro-log/` + `templates/repro_log_schema.json` (JSON Schema 2020-12 [^43]) |
| `docs/templates/hypothesis_design.md` | 11-section frozen pre-reg | `skills/pre-register-hypothesis/` + `templates/hypothesis_design_TEMPLATE.md` |
| `docs/templates/hypothesis_config.yaml` | every scalar has inline `# justify:` neighbor | new `hooks/pre_write_justify_yaml.py` (parallel to existing seed-guard) |
| `scripts/_hooks/check_repro_log.py` | notebook-level repro gate | `hooks/post_write_repro_log_cell.py` (activates on `notebooks/reproducible/**`) |
| `scripts/_hooks/check_non_loss_deletion.py` | append-only on protected globs | `hooks/pre_bash_nonloss_guard.py` (reads per-project `.claude/protected_paths.yaml`) |
| `docs/decisions/ADR-XXXX-*.md` (23 ADRs in the upstream library) | Nygard/MADR ADR chain | `templates/adr_TEMPLATE.md` + `commands/adr-new.md` |
| `hypothesis_backlog.md` | Tier-organized, append-only register | `templates/hypothesis_backlog_TEMPLATE.md` + `commands/hypothesis-new.md` |
| `inference/power.py` + `power_simulation_*` | pre-data power artifacts | `skills/power-analysis/SKILL.md` (gate between `validate-data` and `statistical-analysis`) |
| `inference/e_value.py` | E-value sensitivity | enforce via `quant-auditor` agent prompt update |
| `research/_templates/kpi_report_card_template.md` | realized-OOS + bootstrap-forward | `templates/kpi_report_TEMPLATE.md` |
| `backtest/leak_canaries.py` | PIT canary | `skills/pit-canary/SKILL.md` (invoked by existing `quant-auditor` agent — no new agent; avoids inventory bloat) |

### C.2 Gap inventory — verdict table

Verdicts: NEEDED (build round 1) · NICE (build later) · SKIP (no value).

| # | Item | Verdict | Notes |
|---|---|---|---|
| 1 | Model versioning (DVC/MLflow/git-LFS) | NICE | `artifacts/runs/{HID}/{run_id}/sidecar.json` already covers solo-researcher need; cite Bailey-López de Prado 2014 [^38] for "parameter trial log over binary versioning" framing |
| 2 | Experiment tracking (MLflow/W&B/Aim) | SKIP | Functionally covered by sidecar.json + ReproLog; Aim [^44] only delta is plot UI |
| 3 | Citation management (CITATION.cff + CrossRef) | **NEEDED** | `templates/CITATION.cff.j2` + `hooks/precommit_citation_cff.py` + `commands/cite-add.md` (CrossRef [^45]) |
| 4 | Manuscript templates (Quarto) | **NEEDED** | `templates/manuscript_{strobe,consort,tripod,ssrn}_TEMPLATE.qmd` per Quarto [^46]; identity-hygiene check skill |
| 5 | Pre-registration (OSF/AsPredicted) | **NEEDED** | `skills/pre-register-hypothesis/` + `commands/preregister.md` (OSF [^47][^48]) |
| 6 | DAG drafting (dagitty) | **NEEDED** (epi) | `agents/dag-drafter.md` + `templates/dag_TEMPLATE.dag` (Textor 2016 [^49]; Pearl 2009 [^50]) |
| 7 | Power analysis | **NEEDED** | `skills/power-analysis/SKILL.md` (Cohen 1988 [^51]; pwr [^52]). **Gate placement: pre-registration → power-analysis → validate-data → statistical-analysis.** Power is design-time (pre-data); validate-data is post-pull. Retrospective power is sensitivity-only per Hoenig & Heisey 2001 [^76]. |
| 8 | Survival analysis | SKIP (merge) | Add Kaplan-Meier/log-rank/Cox + scaled-Schoenfeld-residual test (Grambsch & Therneau 1994 [^53] extending Schoenfeld 1982 [^77]) + lifelines [^54] to `statistical-analysis` §3 |
| 9 | Hypothesis backlog auto-curation | **NEEDED** | `commands/hypothesis-new.md` (port the upstream library's `scripts/hypothesis_new.py`); validates HID + DOI [^55] |
| 10 | ADR scaffold | **NEEDED** | `templates/adr_TEMPLATE.md` + `commands/adr-new.md` (Nygard [^6]) |
| 11 | `/commit-with-provenance` | **NEEDED** | wraps `git interpret-trailers` [^56]; depends on (25) |
| 12 | MCP servers (arXiv-OAI, CrossRef, Zenodo) | **NEEDED** | `~/.claude/mcp.json` (arXiv-OAI [^57], CrossRef [^45], Zenodo [^58]); Zotero [^59] only if user uses it |
| 13 | Jupytext paired notebooks | NICE | `templates/jupytext.toml` (paired `ipynb,qmd:percent` [^60]); reference in `rules/publishing.md` |
| 14 | DUA/IRB tracker (epi) | **NEEDED** | `templates/compliance/dua_TEMPLATE.md` (45 CFR §46.111 [^61]) + `hooks/pre_write_phi_guard.py` (HIPAA Safe Harbor 18 identifiers [^62]) |
| 15 | Stress-testing CPCV+PBO | SKIP (interaction) | Already in the upstream library (`cpcv_path_sharpe.py` + `stress_test.py`); bootstrap (pillar A) propagates the pattern |
| 16 | DSPy/GEPA prompt optimization | NICE | `commands/prompt-optimize.md` triggers at user's own 5-occurrence threshold (DSPy [^63]; Khattab et al. 2023 [^64]) |
| 17 | Multiple-testing family register | **NEEDED** | `templates/multipletest_family_TEMPLATE.yaml` + `skills/multipletest-gate/`; Hansen SPA [^37] / White Reality Check [^36] |
| 18 | NW-HAC bandwidth selector | **NEEDED** | inline into `statistical-analysis/SKILL.md` §3 (NW 1994 [^40]; Andrews 1991 [^41]) |
| 19 | ~~Sharpe-CI decision tree~~ | **DROPPED 2026-05-15** | Sharpe is reporting-only, not an optimization target. Sharpe-specific CI methodology stays scoped to [`rules/quant-project.md`](../../rules/quant-project.md) where it already appears. Generic time-series CI methodology (bootstrap, HAC, block-bootstrap) is covered by #18 and #21 — applicable to any KPI, not Sharpe specifically. |
| 20 | PIT canary skill | **NEEDED** | `skills/pit-canary/SKILL.md`; invoked by existing `quant-auditor` agent — no separate leakage-auditor agent (audit-remediate-loop already routes method-fidelity to quant-auditor) (López de Prado 2018 §7 [^65]) |
| 21 | Stationary (block) bootstrap with automatic block length | **NEEDED** | inline into `statistical-analysis/SKILL.md`; stationary bootstrap = Politis & Romano 1994 [^78]; automatic block-length selector = Politis & White 2004 [^66] |
| 22 | AI-assistance commit trailer | **NEEDED** | merged into (11); ICMJE 2026 [^31] + Conventional Commits 1.0.0 [^8] |
| 23 | `consolidate-memory` wiring check | FLAG | operational; verify `anthropic-skills:consolidate-memory` runs |
| 24 | E-value enforcement (epi/causal scope only) | **NEEDED** | one-line update to **new** `agents/epi-auditor.md` (or fold into `reproducibility-verifier` with cwd-conditional rule loading) — NOT `quant-auditor`. E-value (VanderWeele & Ding 2017 [^68]) is a confounding-bias sensitivity analysis for observational causal estimation; it does not map to backtested-Sharpe pipelines, where omitted-variable robustness uses Frank 2000 ITCV [^79] instead. Enforce only when cwd matches [`rules/population-health.md`](../../rules/population-health.md). |
| 25 | ReproLog emitter skill | **NEEDED (#1 priority)** | `skills/emit-repro-log/` + `templates/repro_log_schema.json` (JSON Schema 2020-12 [^43]); copy the upstream library's 13-field dataclass verbatim |

**Round-1 NEEDED count: 14.** Lower-priority NICE/FLAG: 6. SKIP: 4.

### C.3 Open questions (pillar C)

1. **Zotero?** If yes, MCP set includes Zotero local-server. If no, drop from (12).
2. **`templates/manuscript_*` placement?** Under `~/.claude/templates/` (global) or new `~/.claude/manuscripts/`? CLAUDE.md says "do not create new top-level dirs without reason" — keep under `templates/`.
3. **commit-with-provenance scope?** Add trailer always, or only when commit touches `artifacts/`, `logs/`, `research/`?
4. **OSF vs arXiv for pre-registration target?** OSF requires API token; arXiv requires endorsement. If arXiv-only, skill writes to internal `design.md` only.
5. **Overlap between pillar A (bootstrap) and pillar C (stress-testing/CPCV)?** Confirm bootstrap embeds CPCV/PBO scaffolding rather than leaving it for a separate skill.

---

## 4. Consolidated dependency map

```
ReproLog #25 ───┬─► commit-with-provenance #11 ◄── CITATION.cff #3 ◄── MCP #12
                │             ▲
                │             │
                └─────────────┴── AI-assistance trailer #22 ──► rules/publishing.md
                                                                       ▲
ADR scaffold #10 ──► hypothesis-new #9 ──► pre-reg #5 ──► manuscript templates #4
                                                  ▲
                                                  └── MCP #12 (OSF)

DAG drafter #6 ──► IRB/DUA tracker #14 ──► manuscript STROBE #4

power-analysis #7 ──► statistical-analysis (existing)
                              ├──► PIT canary #20 ──► leakage-auditor agent
                              ├──► NW-HAC #18
                              ├──► Sharpe-CI #19
                              ├──► block-bootstrap #21
                              └──► E-value #24 ──► quant-auditor (existing)

multipletest family #17 ──► quant-auditor (existing)
prompt-optimize #16 (standalone)
bootstrap-project (pillar A) ──► consumes ReproLog #25 manifest schema
deliver-results (pillar B)   ──► consumes ReproLog #25 schema + CITATION.cff #3
```

---

## 5. Consolidated open questions for the user (decisive only)

These are questions where the answer changes implementation paths. Non-decisive preference toggles are defaulted (see end of section).

1. **Build backend in pyproject template** — `hatchling` / `setuptools>=68` / defer (upstream-library pattern)?
2. **Documentation site renderer** — Quarto / Sphinx / none (for the docs *site*, not for docs *source*)?
3. **PDF engine** — tectonic / xelatex / weasyprint?
4. **Quarto vs raw markdown** for longform reports and manuscripts?
5. **Zotero MCP** — include or drop from the MCP set?
6. **OSF vs arXiv** as the pre-registration external target?
7. **commit-with-provenance trailer scope** — always, or only when commit touches `artifacts/`/`logs/`/`research/`?

**Defaulted (override by listing exceptions):**
- Colormap: viridis stdlib (no batlow/cmcrameri dependency).
- Slide assembly: native `python-pptx` (no `theme-factory` delegation).
- Ruff pin: float to latest at bootstrap time (reduces lag; pin only on user request).

---

## 6. Recommended implementation order

**Round 1 (foundations — no internal deps):**
1. (#25) `skills/emit-repro-log/SKILL.md` + `templates/repro_log_schema.json`
2. (#12) `~/.claude/mcp.json` with arXiv-OAI + CrossRef + Zenodo
3. (#3) `templates/CITATION.cff.j2` + `hooks/precommit_citation_cff.py`
4. (#10) `templates/adr_TEMPLATE.md` + `commands/adr-new.md`

**Round 2 (commands that wrap round-1):**
5. (#11+#22) `commands/commit-with-provenance.md`
6. (pillar A) `commands/bootstrap-project.md` + `scripts/bootstrap_project.py` + `scripts/bootstrap_templates/`
7. (pillar B) `skills/deliver-results/` (all 6 files)

**Round 3 (specialized + epi/quant track):**
8. (#9) `commands/hypothesis-new.md`
9. (#5) `skills/pre-register-hypothesis/SKILL.md` + `commands/preregister.md`
10. (#7) `skills/power-analysis/SKILL.md` — gate position: pre-register → power-analysis → validate-data → statistical-analysis
11. (#18, #21) inline updates to `skills/statistical-analysis/SKILL.md` — NW-HAC bandwidth + stationary block bootstrap + auto block length. (#19 Sharpe-CI dropped 2026-05-15 — see §C.2)
12. (#20) `skills/pit-canary/SKILL.md` — invoked by existing `quant-auditor`; no separate leakage-auditor agent
13. (#17) `templates/multipletest_family_TEMPLATE.yaml` + `skills/multipletest-gate/SKILL.md`
14. (#6) `agents/dag-drafter.md` + `templates/dag_TEMPLATE.dag`
15. (#14) `templates/compliance/dua_TEMPLATE.md` + `hooks/pre_write_phi_guard.py`
16. (#4) `templates/manuscript_{strobe,consort,tripod,ssrn}_TEMPLATE.qmd`
17. (#24) `agents/epi-auditor.md` (E-value enforcement, cwd-scoped to population-health glob)

**Deferred (NICE):** #1 (model-versioning manifest), #13 (jupytext.toml), #16 (prompt-optimize), #23 (consolidate-memory wiring verification).

---

## 7. References (deduped, numbered)

[^1]: Anthropic. Slash commands. https://docs.claude.com/en/docs/claude-code/slash-commands
[^2]: Anthropic. Skills. https://docs.claude.com/en/docs/claude-code/skills
[^3]: Keep a Changelog 1.1.0. https://keepachangelog.com/en/1.1.0/
[^4]: Druskat, S. et al. Citation File Format v1.2.0. https://citation-file-format.github.io/ ; https://doi.org/10.5281/zenodo.5171937
[^5]: Project TIER. TIER Protocol 4.0. https://www.projecttier.org/tier-protocol/
[^6]: Nygard, M. (2011). Documenting Architecture Decisions. https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions
[^7]: PyPA. src layout vs flat layout. https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/
[^8]: Conventional Commits 1.0.0. https://www.conventionalcommits.org/en/v1.0.0/
[^9]: Preston-Werner, T. Semantic Versioning 2.0.0. https://semver.org/
[^10]: Sandve, G. K. et al. (2013). Ten Simple Rules for Reproducible Computational Research. *PLOS Comput Biol* 9(10):e1003285. https://doi.org/10.1371/journal.pcbi.1003285
[^11]: Matplotlib customizing docs. https://matplotlib.org/stable/users/explain/customizing.html. DejaVu Sans default since v2.0 (2017-01-17): https://matplotlib.org/stable/users/prev_whats_new/whats_new_2.0.0.html
[^12]: Liberation Fonts project. https://github.com/liberationfonts/liberation-fonts
[^13]: Nature final artwork preparation. https://www.nature.com/documents/nature-final-artwork.pdf. Photograph/halftone ≥300 dpi; line art and combination figures ≥600 dpi; Helvetica or Arial preferred sans-serif.
[^14]: Matplotlib `backend_pdf`. https://matplotlib.org/stable/api/backend_pdf_api.html ; PostScript Type 42 (TrueType wrapper) — Adobe Type 42 spec.
[^15]: van der Walt, S. & Smith, N. (2015). A Better Default Colormap for Matplotlib. SciPy 2015. https://bids.github.io/colormap/
[^16]: Crameri, F., Shephard, G. E., Heron, P. J. (2020). The misuse of colour in science communication. *Nat Commun* 11:5444. https://doi.org/10.1038/s41467-020-19160-7 — primarily advocates Scientific colour maps (batlow, vik) at https://www.fabiocrameri.ch/colourmaps/; lists viridis/inferno among acceptable widely-available alternatives to rainbow/jet.
[^17]: Wong, B. (2011). Points of view: Color blindness. *Nat Methods* 8:441. https://doi.org/10.1038/nmeth.1618 — 8-color Okabe-Ito palette. Distinct from matplotlib's `tab10` (which is Tableau-10 / D3 category10).
[^18]: Tufte, E. R. (2001). *The Visual Display of Quantitative Information*, 2nd ed. Graphics Press. ISBN 0-9613921-4-2.
[^19]: Microsoft. Change the size of slides. https://learn.microsoft.com/office/troubleshoot/powerpoint/change-slide-size
[^20]: poppler `pdffonts` manpage. https://manpages.debian.org/bookworm/poppler-utils/pdffonts.1.en.html
[^21]: Pollard, T. J., Johnson, A. E. W., Raffa, J. D., Mark, R. G. (2018). tableone: An open source Python package. *JAMIA Open* 1(1):26-31. https://doi.org/10.1093/jamiaopen/ooy012
[^22]: Sjoberg, D. D. et al. (2021). Reproducible Summary Tables with the gtsummary Package. *R J* 13(1). https://doi.org/10.32614/RJ-2021-053
[^23]: Iannone, R., Cheng, J., Schloerke, B. great_tables. https://posit-dev.github.io/great-tables/
[^24]: von Elm, E. et al. (2007). STROBE Statement. *PLOS Med* 4:e296. https://doi.org/10.1371/journal.pmed.0040296 ; portal https://www.strobe-statement.org/
[^25]: Schulz, K. F., Altman, D. G., Moher, D. (2010). CONSORT 2010. *BMJ* 340:c332. https://doi.org/10.1136/bmj.c332 ; portal https://www.consort-statement.org/
[^26]: Bossuyt, P. M. et al. (2015). STARD 2015. *BMJ* 351:h5527. https://doi.org/10.1136/bmj.h5527
[^27]: Collins, G. S. et al. (2024). TRIPOD+AI statement. *BMJ* 385:e078378. https://doi.org/10.1136/bmj-2023-078378
[^28]: Page, M. J. et al. (2021). PRISMA 2020 statement. *BMJ* 372:n71. https://doi.org/10.1136/bmj.n71
[^29]: PRISMA2020 Shiny app. https://prisma.shinyapps.io/prisma2020/
[^30]: xlsxwriter docs. https://xlsxwriter.readthedocs.io/ ; memory mode https://xlsxwriter.readthedocs.io/working_with_memory.html
[^31]: ICMJE Recommendations (updated January 2026). https://www.icmje.org/recommendations/
[^32]: python-pptx. https://python-pptx.readthedocs.io/
[^33]: Lo, A. W. (2002). The Statistics of Sharpe Ratios. *Financial Analysts J* 58(4):36-52. https://doi.org/10.2469/faj.v58.n4.2453
[^34]: Opdyke, J. D. (2007). Comparing Sharpe Ratios: So Where Are the p-values? *J Asset Manag* 8:308-336. https://doi.org/10.1057/palgrave.jam.2250084
[^35]: Ledoit, O., Wolf, M. (2008). Robust performance hypothesis testing with the Sharpe ratio. *J Empir Finance* 15(5):850-859. https://doi.org/10.1016/j.jempfin.2008.03.002
[^36]: White, H. (2000). A Reality Check for Data Snooping. *Econometrica* 68(5):1097-1126. https://doi.org/10.1111/1468-0262.00152
[^37]: Hansen, P. R. (2005). A Test for Superior Predictive Ability. *J Bus Econ Stat* 23(4):365-380. https://doi.org/10.1198/073500105000000063
[^38]: Bailey, D. H., López de Prado, M. (2014). The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting, and Non-Normality. *J Portfolio Mgmt* 40(5):94-107. https://doi.org/10.3905/jpm.2014.40.5.094. (Note: a distinct 2012 paper by the same authors, "The Sharpe Ratio Efficient Frontier," *J Risk* 15(2):3-44, https://doi.org/10.21314/JOR.2012.255, is not cited in this memo but is the source for the related "deflation" framework.)
[^39]: Bailey, D. H., Borwein, J., López de Prado, M., Zhu, Q. J. (2016). The probability of backtest overfitting. *J Comput Finance*. https://doi.org/10.21314/JCF.2016.322
[^40]: Newey, W. K., West, K. D. (1994). Automatic Lag Selection in Covariance Matrix Estimation. *Rev Econ Stud* 61(4):631-653. https://doi.org/10.2307/2297912
[^41]: Andrews, D. W. K. (1991). HAC Covariance Matrix Estimation. *Econometrica* 59(3):817-858. https://doi.org/10.2307/2938229
[^42]: Sortino, F. A., Price, L. N. (1994). Performance measurement in a downside risk framework. *J Investing* 3:59-64.
[^43]: JSON Schema 2020-12. https://json-schema.org/draft/2020-12/json-schema-core
[^44]: Arakelyan, G. et al. Aim. https://aimstack.io ; https://doi.org/10.21105/joss.00631
[^45]: CrossRef REST API. https://api.crossref.org/swagger-ui/index.html
[^46]: Allaire, J. J. et al. Quarto. https://quarto.org/docs/guide/
[^47]: Foster, E. D., Deardorff, A. (2017). Open Science Framework. *J Med Libr Assoc* 105(2):203-206. https://doi.org/10.5195/jmla.2017.88
[^48]: AsPredicted. https://aspredicted.org/
[^49]: Textor, J. et al. (2016). dagitty. *Int J Epidemiol* 45(6):1887-1894. https://doi.org/10.1093/ije/dyw341
[^50]: Pearl, J. (2009). *Causality*, 2nd ed. Cambridge University Press. ISBN 978-0521895606.
[^51]: Cohen, J. (1988). *Statistical Power Analysis for the Behavioral Sciences*, 2nd ed. Lawrence Erlbaum. ISBN 978-0805802832.
[^52]: Champely, S. pwr R package. https://cran.r-project.org/web/packages/pwr/index.html
[^53]: Grambsch, P. M., Therneau, T. M. (1994). Proportional hazards tests and diagnostics. *Biometrika* 81(3):515-526. https://doi.org/10.1093/biomet/81.3.515
[^54]: Davidson-Pilon, C. (2019). lifelines. *JOSS* 4(40):1317. https://doi.org/10.21105/joss.01317
[^55]: International DOI Foundation. DOI Handbook. https://www.doi.org/the-identifier/resources/handbook/
[^56]: Git documentation. `git-interpret-trailers`. https://git-scm.com/docs/git-interpret-trailers
[^57]: arXiv OAI-PMH. https://info.arxiv.org/help/oa/index.html
[^58]: Zenodo REST API. https://developers.zenodo.org/
[^59]: Zotero Web/Local API. https://www.zotero.org/support/dev/web_api/v3/start
[^60]: Wouts, M. Jupytext. https://github.com/mwouts/jupytext
[^61]: 45 CFR §46.111. https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-A/part-46/subpart-A/section-46.111
[^62]: HHS HIPAA Safe Harbor §164.514(b)(2). https://www.hhs.gov/hipaa/for-professionals/privacy/special-topics/de-identification/index.html
[^63]: DSPy documentation. https://dspy.ai/
[^64]: Khattab, O. et al. (2023). DSPy. arXiv:2310.03714. https://arxiv.org/abs/2310.03714
[^65]: López de Prado, M. (2018). *Advances in Financial Machine Learning*. Wiley. ISBN 978-1119482086.
[^66]: Politis, D. N., White, H. (2004). Automatic Block-Length Selection for the Dependent Bootstrap. *Econometric Rev* 23(1):53-70. https://doi.org/10.1081/ETC-120028836
[^68]: VanderWeele, T. J., Ding, P. (2017). Sensitivity Analysis: E-Value. *Ann Intern Med* 167(4):268-274. https://doi.org/10.7326/M16-2607
[^69]: Wilson, G. et al. (2014). Best Practices for Scientific Computing. *PLOS Biol* 12(1):e1001745. https://doi.org/10.1371/journal.pbio.1001745
[^70]: Wilson, G. et al. (2017). Good Enough Practices in Scientific Computing. *PLOS Comput Biol* 13(6):e1005510. https://doi.org/10.1371/journal.pcbi.1005510
[^71]: Marwick, B., Boettiger, C., Mullen, L. (2018). Packaging Data Analytical Work Reproducibly Using R (and Friends). *Am Statistician* 72(1):80-88. https://doi.org/10.1080/00031305.2017.1375986
[^72]: Wickham, H. (2014). Tidy Data. *J Stat Softw* 59(10):1-23. https://doi.org/10.18637/jss.v59.i10
[^73]: Internal upstream research library (private; consulted for layout, dataclass field lists, and convention provenance during this memo).
[^74]: Kovesi, P. (2015). Good Colour Maps: How to Design Them. arXiv:1509.03700. https://arxiv.org/abs/1509.03700 — peer-style derivation of perceptual uniformity in colormaps.
[^75]: Mertens, E. (2002). Comments on Variance of the IID Estimator in Lo (2002). Working paper (Erasmus University Rotterdam / University of Basel). Cited via secondary aggregators (https://www.scirp.org/reference/referencespapers?referenceid=2920064; https://www.twosigma.com/wp-content/uploads/sharpe-tr-1.pdf). Tier-4 evidence; provides the IID skew/kurtosis correction to Lo 2002's Sharpe SE; generalized by Opdyke 2007 [^34].
[^76]: Hoenig, J. M., Heisey, D. M. (2001). The Abuse of Power: The Pervasive Fallacy of Power Calculations for Data Analysis. *Am Statistician* 55(1):19-24. https://doi.org/10.1198/000313001300339897 — retrospective/post-hoc power as analysis tool is unsound; pre-data design power is the correct use.
[^77]: Schoenfeld, D. (1982). Partial residuals for the proportional hazards regression model. *Biometrika* 69(1):239-241. https://doi.org/10.1093/biomet/69.1.239 — original Schoenfeld residuals; extended to the scaled-residual non-PH test by Grambsch & Therneau 1994 [^53].
[^78]: Politis, D. N., Romano, J. P. (1994). The Stationary Bootstrap. *J Am Stat Assoc* 89(428):1303-1313. https://doi.org/10.1080/01621459.1994.10476870 — the stationary bootstrap method itself; automatic block-length selector for it is Politis & White 2004 [^66].
[^79]: Frank, K. A. (2000). Impact of a Confounding Variable on a Regression Coefficient. *Sociol Methods Res* 29(2):147-194. https://doi.org/10.1177/0049124100029002001 — ITCV (Impact Threshold for a Confounding Variable); omitted-variable robustness sensitivity for regressions in non-causal-inference contexts (quant analog to E-value).
