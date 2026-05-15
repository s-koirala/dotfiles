# s-koirala/dotfiles

Personal configuration files. Currently a single subtree, [`claude/`](claude/), holding user-level [Claude Code](https://claude.com/claude-code) config that deploys into `~/.claude/` on Windows, macOS, and Linux.

## What this repo is for

Tooling for an independent researcher working across:

- **Finance & financial markets** — futures backtest pipelines (signal-decay, factor research, ML/HMM regime modeling), KPI report cards keyed to survival-constrained metrics (terminal-wealth-q05, Calmar, profit-factor, R-multiple; Sharpe is reporting-only), family-wise multiple-testing gates (Hansen SPA, White Reality Check, BH FDR, Holm).
- **Population science & public health** — STROBE / CONSORT / STARD / TRIPOD+AI / PRISMA reporting standards, DAG-driven adjustment-set selection (Pearl back-door criterion via dagitty), E-value sensitivity for unmeasured confounding (VanderWeele & Ding 2017), HIPAA Safe Harbor PHI write-guard, DUA/IRB compliance tracking (45 CFR §46.111).
- **Statistics & biostatistics** — assumption-driven method selection, HAC standard errors (Newey-West / Andrews) and stationary block bootstrap (Politis-Romano / Politis-White), pre-data power analysis (Cohen 1988; retrospective power forbidden per Hoenig & Heisey 2001).
- **App development** — Python tooling (`uv` env, `ruff` lint/format, `pytest`, `nbstripout` + `nbqa` for notebooks), pre-commit hooks (seed-guard with AST inspection, CITATION.cff validator), 13-field ReproLog reproducibility envelope, atomic-write idioms, Conventional Commits 1.0.0 + ICMJE 2026 AI-assistance disclosure trailers.

Path-scoped rules ([`claude/rules/`](claude/rules/)) activate per project cwd, so the same dotfiles behave appropriately across these domains:

| Rule | cwd globs |
|---|---|
| `quant-project.md` | `**/SKIE-Ninja*/`, `**/Futures_ML_Prediction/`, `**/*backtest*/`, `**/*factor*/` |
| `population-health.md` | `**/PCP*Crisis/`, `**/Infectious_Disease*/`, `**/Ultrasound/`, `**/epidemiolog*/` |
| `publishing.md` | `**/project-skie/`, `**/*publication*/`, `**/*manuscript*/` |

## Installation

**See [`claude/INSTALL.md`](claude/INSTALL.md)** for the full procedure (manual 3-line clone+deploy, or AI-paste directive in a collapsible block).

Quick manual path:
```bash
git clone https://github.com/s-koirala/dotfiles.git ~/dotfiles
python ~/dotfiles/claude/scripts/deploy.py --check
python ~/dotfiles/claude/scripts/deploy.py
```

For the **AI-assisted path**, [`claude/INSTALL.md`](claude/INSTALL.md) contains a copy-paste directive inside a `<details>` block (look for the heading "Copy this block into a fresh Claude Code session"). **Paste only the contents of that fenced code block**, not the entire INSTALL.md file.

## Layout

```
.gitattributes                # text/binary classification + nbstripout filter
.gitignore                    # root-level ignores
README.md                     # this file
claude/                       # Claude Code user-level config (→ ~/.claude/)
├── INSTALL.md                # installation guide — START HERE
├── README.md                 # claude/-specific inventory
├── CLAUDE.md                 # user-level directives (evidence hierarchy, parameter selection)
├── settings.json             # permissions + hook registration (with {{CLAUDE_HOME}} placeholder)
├── mcp.json                  # MCP server manifest (arxiv + crossref)
├── agents/                   # 7 specialist auditor agents
├── commands/                 # 10 slash commands
├── docs/audits/              # audit trails covering design + R0-R3 implementation
├── hooks/                    # 8 pre/post-tool-use Python scripts
├── rules/                    # 3 cwd-scoped rule files
├── scripts/                  # deploy.py + 5 other Python tools
├── skills/                   # 9 procedural playbooks
└── templates/                # 12 reusable templates (manuscript ref.docx, ADR, etc.)
```


Per [ICMJE Recommendations (January 2026)](https://www.icmje.org/recommendations/): `claude-opus-4-7` contributed in roles `idea`, `code`, `prose`, `audit` to the R0–R3 implementation arc (commit count varies as work continues; full audit trail under [`claude/docs/audits/`](claude/docs/audits/) — 14 audit_trail files plus implementation_plan + research_memo, 16 files total). AI is acknowledged as a tool, not an author.
