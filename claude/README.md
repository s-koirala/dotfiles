# `claude/` — Claude Code user-level config

Subdirectory of [s-koirala/dotfiles](https://github.com/s-koirala/dotfiles). Contains user-level [Claude Code](https://claude.com/claude-code) configuration that deploys into `~/.claude/` on Windows / macOS / Linux via `scripts/deploy.py`.

Scope spans finance + financial markets + population science + public health + statistics + biostatistics + reproducible-research app development — see the top-level [README](../README.md) for details and rule-globs. General web/API/deployment tooling is out of scope.

## For installation, see [INSTALL.md](INSTALL.md).

`INSTALL.md` contains both the manual 3-line install and an AI-paste directive inside a collapsible `<details>` block. Only paste the contents of that fenced code block into Claude Code; not the surrounding documentation.

## Inventory (current, as of HEAD)

| Component | Count | Location |
|---|---|---|
| User-level directives | 1 | `CLAUDE.md` |
| Permissions + hook registration | 1 | `settings.json` |
| MCP server manifest | 1 | `mcp.json` |
| Specialist auditor agents | 7 | `agents/` |
| Slash commands | 10 | `commands/` |
| Python hooks (pre/post tool use, session start/end, pre-commit) | 8 | `hooks/` |
| Path-scoped rule files | 3 | `rules/` |
| Top-level Python scripts | 6 | `scripts/` |
| Procedural skills | 14 | `skills/` |
| Reusable templates (CITATION.cff, ADR, DAG, dua, manuscript reference.docx + 5 reporting-standard templates, schemas) | 12 | `templates/` |
| Bootstrap-project sub-templates (CLAUDE.md.tmpl, README.md.tmpl, pyproject.toml.tmpl, kind-specific, etc.) | 12 | `scripts/bootstrap_templates/` |
| Audit trails (design + R0–R3 implementation) | 16+ | `docs/audits/` |

### Skills (14)

| Name | Purpose |
|---|---|
| `audit-remediate-loop` | 5-branch parallel auditor pattern (quant/epi/code/research/format/repro) with 3-round cap |
| `statistical-analysis` | Assumption-driven method selection; HAC + stationary block bootstrap inline |
| `validate-data` | Schema + distribution + provenance checks before any downstream analysis |
| `emit-repro-log` | 13-field ReproLog JSON record (port of SKIE-Universe `reproducibility.py`) |
| `deliver-results` | Final-form figures (Okabe-Ito mplstyle, save_figure with pdffonts check), Excel workbook (xlsxwriter), report cards |
| `pre-register-hypothesis` | Freeze design.md with SHA-256 anchor; 11-section template port from SKIE-Universe |
| `power-analysis` | Pre-data n calculation; retrospective power forbidden per Hoenig & Heisey 2001 |
| `pit-canary` | Point-in-time leakage detection (López de Prado 2018 AFML §7) |
| `multipletest-gate` | Family-wise correction (Hansen SPA / White RC / BH FDR / Holm) |
| `survival-analysis` | Kaplan-Meier + Cox PH + Schoenfeld diagnostics + AFT (Therneau & Grambsch 2000) |
| `mediation-analysis` | VanderWeele 2014 counterfactual NDE/NIE; bootstrap CIs; E-value sensitivity |
| `multiple-imputation` | MICE with `m ≥ %incomplete` per White, Royston, Wood 2011; Rubin's rules |
| `bayesian-workflow` | Gelman 2020 11-step workflow; prior-predictive + posterior-predictive checks; R-hat + ESS + divergences; LOO-CV |
| `meta-analysis` | DerSimonian-Laird + REML + Hartung-Knapp-Sidik-Jonkman; I² + funnel + Egger; PRISMA-aligned |

### Slash commands (10)

`/audit-loop`, `/lit-check`, `/reproduce`, `/cite-add`, `/adr-new`, `/commit-with-provenance`, `/bootstrap-project`, `/hypothesis-new`, `/preregister`, `/render-manuscript`.

### Agents (7)

`quant-auditor`, `literature-check`, `reproducibility-verifier`, `dag-drafter`, `epi-auditor`, `code-reviewer`, `format-auditor`.

### Hooks (8)

`session_start_provenance`, `session_end_audit_log`, `pre_write_seed_guard`, `precommit_seed_guard`, `pre_bash_safety`, `post_write_notebook_clean`, `precommit_citation_cff`, `pre_write_phi_guard`.

## Updating after first install

```bash
cd ~/dotfiles && git pull --ff-only && python claude/scripts/deploy.py
```

`deploy.py` is idempotent: a second `--check` run reports `in sync` and writes nothing.

## See also

- [`INSTALL.md`](INSTALL.md) — install procedure (start here)
- [`CLAUDE.md`](CLAUDE.md) — user-level directives + path-scoped rule imports
- [`docs/audits/`](docs/audits/) — design memos + audit trails for every R0–R3 item
- Top-level [`README.md`](../README.md) — repo scope + identity hygiene
