# Installing `s-koirala/dotfiles` → `~/.claude/`

User-level Claude Code configuration for an independent researcher working
across finance + financial markets, population science + public health,
statistics + biostatistics, and reproducible-research app development.
The scope is research-tooling-flavored — general web/API/deployment work is
not covered by domain skills here (use base Claude Code capability for that).
See the top-level [README](../README.md) for the per-domain scope breakdown
and the cwd-glob rule activation table. This file is the installation procedure.

Deploys 14 skills, 8 slash commands, 7 agents, 7 hooks, 4 scripts, and 15
templates (5 in `templates/` + 10 in `scripts/bootstrap_templates/`) into
`~/.claude/` on Windows, macOS, or Linux via an idempotent Python script.

## How to use this guide

- **Manual install** (3 lines of bash): jump to [§Quickstart — manual](#quickstart--manual-no-ai).
- **AI-assisted install**: jump to [§Quickstart — Claude Code](#quickstart--claude-code-ai-assisted). Inside that section is a collapsible `<details>` block with a single fenced code block — **copy the contents of that code block (and only that block) into a fresh Claude Code session** at `~/`. The rest of this INSTALL.md is documentation; do not paste it.
- **Verification, inventory, MCP setup, updates, deferred items, identity hygiene**: continue past the quickstart sections.

## Requirements

- **Claude Code** (any recent version)
- **git**; **`gh` CLI** optional (public repo — only needed for MCP/API tasks)
- **Python 3.11+** with **`uv`** on PATH
- **Windows users:** Git Bash (ships with Git for Windows) or WSL. The commands below assume a POSIX-style shell; raw PowerShell will not expand `~/` when passed to external programs.
- Optional shell tools used in verification snippets: `grep`, `jq` (both included with Git Bash on Windows).
- Optional, install when needed: per-machine MCP server packages.

## Quickstart — manual (no AI)

`deploy.py` lives in the cloned repo at `~/dotfiles/claude/scripts/deploy.py` (the **source**), and copies content into `~/.claude/` (the **deployment target**). It is not present at `~/.claude/scripts/`; do not look for it there.

```bash
git clone https://github.com/s-koirala/dotfiles.git ~/dotfiles
python ~/dotfiles/claude/scripts/deploy.py --check    # diff-only, no writes
python ~/dotfiles/claude/scripts/deploy.py            # safe deploy; backs up
python ~/dotfiles/claude/scripts/deploy.py --init-local  # scaffold settings.local.json
```

Safe to re-run. Any file at `~/.claude/` that would be overwritten is first
backed up to `~/.claude/backups/<YYYY-MM-DDTHHMMSS>/`. A second `--check` run
must report `in sync`; if not, the deploy is non-deterministic and should be
investigated.

**Windows-specific:** run these inside **Git Bash** (installed with Git for Windows) or **WSL**, not raw PowerShell or cmd. The `~/` expansion and `grep`/`jq` invocations below require a POSIX shell. PowerShell equivalents would substitute `$HOME\dotfiles\...` and `Select-String` / `ConvertFrom-Json`; not maintained here to keep the doc single-track.

## Quickstart — Claude Code (AI-assisted)

**Copy *only* the contents of the fenced code block below** (not this paragraph, not the `<details>` markers, not anything outside the triple backticks) into a fresh Claude Code session started at `~/`. The block is self-contained: Claude will read it as a single instruction set and execute the 3-stage install + verify + audit protocol.

<details>
<summary>Click to expand the directive — paste contents of the inner code block only</summary>

```text
# ════════ BEGIN PASTE ════════
You are bootstrapping s-koirala/dotfiles on this machine. Execute every step
via Bash / Read / Write / Agent tools. Do NOT simulate — actually run each
command, capture output, halt on failure. Cap audit-remediate at 3 rounds per
the user's audit-remediate-loop skill.

REPO=https://github.com/s-koirala/dotfiles.git

# Stage 1 — install
1. Verify: `git --version`; `python --version` (>= 3.11). Halt on any failure.
   (`gh` is optional — only needed for MCP/API tasks, not to clone a public repo.)
2. Clone or fast-forward: if `~/dotfiles/.git` absent, `git clone $REPO ~/dotfiles`.
   If present + clean + on main, `cd ~/dotfiles && git pull --ff-only origin main`.
   If dirty or divergent, HALT — never force-pull.
3. `python ~/dotfiles/claude/scripts/deploy.py --check` — capture diff. If any
   PROTECTED name from deploy.py appears in the diff, HALT.
4. `python ~/dotfiles/claude/scripts/deploy.py` — safe deploy with backup.
5. `python ~/dotfiles/claude/scripts/deploy.py --init-local` — scaffold
   `settings.local.json`. Never inline API keys; recommend OS-keychain
   `apiKeyHelper` (Windows Credential Manager / macOS Keychain / Linux pass).
6. Re-run `--check`; must report "in sync".

# Stage 2 — verify (filesystem + runtime; not self-report)
7. `grep -c "{{CLAUDE_HOME}}" ~/.claude/settings.json` must be 0.
8. Smoke-test all hooks with empty stdin:
   `python -c "import subprocess,sys,glob,os; os.chdir(os.path.expanduser('~/.claude/hooks')); [print(f, subprocess.run([sys.executable,f], input=b'{}', capture_output=True, timeout=10).returncode) for f in sorted(glob.glob('*.py'))]"`
   Every returncode must be 0.
9. Realistic payload test: feed `{"tool_input": {"file_path": "/tmp/t.py",
   "content": "import numpy as np; x = np.random.rand(100)"}}` to
   `pre_write_seed_guard.py`. Output must contain `permissionDecision` and
   `ask`.
10. Tool inventory: `uv --version`, `ruff --version`, `pytest --version`,
    `nbstripout --version`, `nbqa --version`. Record presence; do not auto-install.
11. `claude mcp list` — report. Propose `claude mcp add-json <name> "$(jq
    '.mcpServers.<name>' ~/.claude/mcp.json)"` for each active server in
    `~/.claude/mcp.json`. Do not auto-register.
12. Identity check: report `git config --global user.{name,email}`, hostname,
    `uname -a` (or `ver` on Windows). Flag if the global git email looks
    unintended (e.g. a real email where the GitHub no-reply form was intended).

# Stage 3 — audit (parallel subagents; max 3 rounds)
13. Spawn in parallel (single message, multiple Agent calls), briefing each
    with the deployed `~/.claude/agents/<name>.md`:
    - `reproducibility-verifier`: verify `~/.claude/` tree matches source;
      hooks runnable; no `{{CLAUDE_HOME}}` placeholders remain.
    - `code-reviewer`: audit `~/.claude/hooks/*.py` for code quality,
      type hints, cross-platform path handling.
    - `quant-auditor`: audit hooks for `hookSpecificOutput` schema
      correctness and fail-open behavior on malformed stdin.
    - `format-auditor`: verify identity hygiene (no real-name strings),
      magic-numbers compliance, template substitution completeness.
    - `literature-check`: verify every URL/citation in `CLAUDE.md` + `rules/*.md`.
14. Triage: critical blocks; major remediated in-round; minor logged. Remediate
    in-place; do NOT modify the upstream dotfiles repo (no `git push`).
15. Re-spawn auditors that returned findings; exit when all return `accept` or
    after round 3.

# Final report
Write `~/dotfiles/claude/logs/bootstrap_<hostname>_<YYYY-MM-DD>.md` with:
machine info; stage 1/2/3 results; tool inventory; MCP proposals (not
executed); audit findings + disposition; identity check; manual follow-ups
(pandoc install, OSF token, MCP registrations).

Do NOT `git add`, `git commit`, or `git push`. Bootstrap is read-only toward
the repo. The report is gitignored; surface its path to the user.
# ════════ END PASTE ════════
```

</details>

The AI path runs the same `deploy.py` commands as the manual path, plus
filesystem/runtime verification, a 5-branch audit-remediate loop (per the user's
`audit-remediate-loop` skill spec), and an installation report. Stop pasting at
the `END PASTE` marker; everything after this point is documentation for the
human.

## Customize for your use

This is a template you fork. Two one-time steps make generated output yours:

1. **Identity** — copy `config.example.toml` → `config.toml` (gitignored) and set `author` / `email` / `github_user`. `bootstrap_project.py` reads these so scaffolded projects carry your identity. CLI flags (`--author`, `--user-email`, `--github-user`) and `AUTHOR` / `EMAIL` / `GITHUB_USER` env vars override.
2. **Rule activation** — the cwd globs at the top of [`rules/quant-project.md`](rules/quant-project.md) and [`rules/population-health.md`](rules/population-health.md) are generic examples (`**/*backtest*/`, `**/*epidemiolog*/`, …). Edit them to match your own project directory names.

## Verification (after deploy)

```bash
ls ~/.claude/{skills,agents,commands,hooks,rules}
# Expect: 14 skills/, 7 agents/, 8 commands/, 7 hooks/, 2 rules/

grep -c "{{CLAUDE_HOME}}" ~/.claude/settings.json    # 0 required
```

Inside a Claude Code session, `/help` should list `audit-loop`, `bootstrap-project`, `commit-with-provenance`, etc. (8 user-defined commands total).

## Inventory

### Skills (14)
- **audit-remediate-loop** — 5-branch parallel auditor pattern with 3-round cap
- **statistical-analysis** — assumption-driven method selection; HAC + stationary bootstrap inline
- **validate-data** — schema + distribution + provenance checks
- **emit-repro-log** — 13-field ReproLog (field list in [skills/emit-repro-log/SKILL.md](skills/emit-repro-log/SKILL.md))
- **deliver-results** — figures (mplstyle + save_figure), workbook (xlsxwriter), report cards
- **pre-register-hypothesis** — freeze design.md with SHA-256 anchor
- **power-analysis** — pre-data n calculation; retrospective power forbidden (Hoenig & Heisey 2001, *Am Stat* 55(1):19, [doi.org/10.1198/000313001300339897](https://doi.org/10.1198/000313001300339897))
- **pit-canary** — point-in-time leakage detection (López de Prado 2018, *Advances in Financial Machine Learning* Ch. 7 "Cross-Validation in Finance", ISBN 978-1-119-48208-6; full citations in [skills/pit-canary/SKILL.md](skills/pit-canary/SKILL.md))
- **multipletest-gate** — family-wise register + correction; methods + DOIs in [skills/multipletest-gate/SKILL.md](skills/multipletest-gate/SKILL.md) (Hansen 2005, White 2000, Benjamini & Hochberg 1995, Holm 1979)
- **survival-analysis** — Kaplan-Meier + Cox PH + scaled-Schoenfeld diagnostics + AFT; Therneau & Grambsch 2000; cross-domain (finance time-to-default, epi time-to-event, biostats duration outcomes)
- **mediation-analysis** — VanderWeele 2014 counterfactual NDE/NIE decomposition; bootstrap CIs; E-value sensitivity for unmeasured M-Y confounding
- **multiple-imputation** — MICE per White, Royston & Wood 2011 (`m ≥ %incomplete`); Rubin's rules; MAR-MNAR sensitivity
- **bayesian-workflow** — Gelman et al. 2020 11-step workflow; weakly-informative priors per Gelman 2008; R-hat + ESS + divergence diagnostics per Vehtari et al. 2021; LOO-CV via PSIS
- **meta-analysis** — DerSimonian-Laird + REML; Hartung-Knapp-Sidik-Jonkman for small k (IntHout, Ioannidis, Borm 2014); I² + Egger test + trim-and-fill; PRISMA 2020 aligned

### Slash commands (8)
`/audit-loop`, `/lit-check`, `/reproduce`, `/adr-new`, `/commit-with-provenance`, `/bootstrap-project`, `/hypothesis-new`, `/preregister`.

### Agents (7)
`quant-auditor`, `literature-check`, `reproducibility-verifier` (existing) · `dag-drafter`, `epi-auditor`, `code-reviewer`, `format-auditor` (new).

### Hooks (7)
`session_start_provenance`, `session_end_audit_log`, `pre_write_seed_guard`, `precommit_seed_guard`, `pre_bash_safety`, `post_write_notebook_clean`, `pre_write_phi_guard` (PHI guard cwd-scoped to population-health globs).

### Scripts (4)
`deploy.py`, `commit_with_provenance.py`, `bootstrap_project.py`, `build_data_manifest.py`.

## MCP servers

`~/.claude/mcp.json` is the canonical MCP manifest (declares `arxiv` / `arxiv-mcp-server` and `crossref` / `crossref-cite-mcp`). Older per-server descriptors under `scripts/mcp/` (`arxiv.json`, `filesystem.json`) predate the consolidated `mcp.json` and are retained for reference. Auto-registration is not part of deploy.py — register per-machine:

```bash
claude mcp add-json arxiv "$(jq '.mcpServers.arxiv' ~/.claude/mcp.json)"
claude mcp add-json crossref "$(jq '.mcpServers.crossref' ~/.claude/mcp.json)"
```

An OSF MCP is deferred (no canonical server exists yet).

## Updates

```bash
cd ~/dotfiles && git pull --ff-only && python claude/scripts/deploy.py
```

## Deferred (use-case-triggered)

These are functional but un-wired until a real use case arises. Track in this
section; re-evaluate when first encountered:

1. **OSF external pre-registration (R3-2b).** The R3-2a `pre-register-hypothesis` skill freezes design via internal SHA-256 + commit trailer and is fully reproducible. External OSF posting is an `--external=osf` opt-in that requires a thin Python helper around the OSF v2 REST API ([developer.osf.io](https://developer.osf.io/)) and a Personal Access Token at `~/.config/osf/token`. Implement at first external pre-registration.

2. **`~/.claude/` ↔ `s-koirala/dotfiles` layout migration.** Local working tree is flat (`~/.claude/<X>`); remote wraps content in `claude/<X>`. Future migration via `git filter-repo --to-subdirectory-filter claude/` (preserves history) or chezmoi/stow ([chezmoi.io](https://www.chezmoi.io/), [GNU Stow](https://www.gnu.org/software/stow/)). Defer until first push from local to remote.

## Identity hygiene

Commit history uses the GitHub no-reply email form (`<handle>@users.noreply.github.com`) to keep a real email out of public history. When you adopt this repo, set your own identity once in `config.toml` (copy `config.example.toml`); `bootstrap_project.py` then stamps your identity into scaffolded projects, not the template author's. Avoid embedding unwanted real-name metadata in committed files (notebook `kernelspec` / author fields; a `git config user.name` baked into templates).

## Development trail

Design and implementation are documented in [`docs/audits/`](docs/audits/) (audit trails + implementation plan + research memo). The repository was built with AI assistance.

## License

License file pending; until added, treat content as released under MIT terms by the repository owner.
