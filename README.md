# s-koirala/dotfiles

Personal configuration files. Currently a single subtree, [`claude/`](claude/), holding user-level [Claude Code](https://claude.com/claude-code) config that deploys into `~/.claude/` on Windows, macOS, and Linux.

## What this repo is for

Tooling for an independent researcher working across:

- **Finance & financial markets** — futures backtest pipelines (signal-decay, factor research, ML/HMM regime modeling), KPI report cards keyed to survival-constrained metrics (terminal-wealth-q05, Calmar, profit-factor, R-multiple; Sharpe is reporting-only), family-wise multiple-testing gates (Hansen SPA, White Reality Check, BH FDR, Holm).
- **Population science & public health** — STROBE / CONSORT / STARD / TRIPOD+AI / PRISMA reporting standards, DAG-driven adjustment-set selection (Pearl back-door criterion via dagitty), E-value sensitivity for unmeasured confounding (VanderWeele & Ding 2017), HIPAA Safe Harbor PHI write-guard, DUA/IRB compliance tracking (45 CFR §46.111).
- **Statistics & biostatistics** — assumption-driven method selection, HAC standard errors (Newey-West / Andrews) and stationary block bootstrap (Politis-Romano / Politis-White), pre-data power analysis (Cohen 1988; retrospective power forbidden per Hoenig & Heisey 2001).
- **Reproducible-research app development** — Python tooling for research code (`uv` env, `ruff` lint/format, `pytest`, `nbstripout` + `nbqa` for notebooks), pre-commit hooks (seed-guard with AST inspection, HIPAA PHI guard), 13-field ReproLog reproducibility envelope, atomic-write idioms, Conventional Commits 1.0.0. *Out of scope:* general web framework / API / container / deployment tooling — use Claude Code's base capability with project-specific guidance for those domains.

Path-scoped rules ([`claude/rules/`](claude/rules/)) activate per project cwd, so the same dotfiles behave appropriately across these domains:

| Rule | cwd globs (customize to your own project names) |
|---|---|
| `quant-project.md` | `**/*backtest*/`, `**/*factor*/`, `**/*signal*/`, `**/*alpha*/`, `**/*quant*/` |
| `population-health.md` | `**/*epidemiolog*/`, `**/*cohort*/`, `**/*clinical*/`, `**/*biostat*/`, `**/*public-health*/` |

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
├── commands/                 # 8 slash commands
├── docs/audits/              # audit trails covering design + implementation
├── hooks/                    # 7 pre/post-tool-use Python scripts
├── rules/                    # 2 cwd-scoped rule files
├── scripts/                  # deploy.py + 3 other Python tools
├── skills/                   # 14 procedural playbooks
└── templates/                # 5 reusable templates (ADR, DAG, DUA, schemas)
```
