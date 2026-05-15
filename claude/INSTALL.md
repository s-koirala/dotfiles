# Installing `s-koirala/dotfiles` → `~/.claude/`

User-level Claude Code configuration for an independent researcher working
across finance + financial markets, population science + public health,
statistics + biostatistics, and app development. See the top-level
[README](../README.md) for the per-domain scope breakdown and the cwd-glob
rule activation table. This file is the installation procedure.

Deploys 9 skills, 10 slash commands, 7 agents, 8 hooks, 6 scripts, and 24
templates (12 in `templates/` + 12 in `scripts/bootstrap_templates/`) into
`~/.claude/` on Windows, macOS, or Linux via an idempotent Python script.

## How to use this guide

- **Manual install** (3 lines of bash): jump to [§Quickstart — manual](#quickstart--manual-no-ai).
- **AI-assisted install**: jump to [§Quickstart — Claude Code](#quickstart--claude-code-ai-assisted). Inside that section is a collapsible `<details>` block with a single fenced code block — **copy the contents of that code block (and only that block) into a fresh Claude Code session** at `~/`. The rest of this INSTALL.md is documentation; do not paste it.
- **Verification, inventory, MCP setup, updates, deferred items, identity hygiene**: continue past the quickstart sections.

## Requirements

- **Claude Code** (any recent version)
- **git**, **`gh` CLI** authenticated (private repo)
- **Python 3.11+** with **`uv`** on PATH
- **Windows users:** Git Bash (ships with Git for Windows) or WSL. The commands below assume a POSIX-style shell; raw PowerShell will not expand `~/` when passed to external programs.
- Optional shell tools used in verification snippets: `grep`, `jq` (both included with Git Bash on Windows).
- Optional, install when needed: **pandoc** (for `/render-manuscript`), per-machine MCP server packages.

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
1. Verify: `git --version`; `python --version` (>= 3.11); `gh auth status`
   (private repo). Halt on any failure.
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
    `uname -a` (or `ver` on Windows). Flag if email matches a real-name
    pattern when this machine will be used for SKIE-pseudonym publishing
    work (per `rules/publishing.md`).

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

## Verification (after deploy)

```bash
ls ~/.claude/{skills,agents,commands,hooks,rules}
# Expect: 9 skills/, 7 agents/, 10 commands/, 8 hooks/, 3 rules/

grep -c "{{CLAUDE_HOME}}" ~/.claude/settings.json    # 0 required
```

Inside a Claude Code session, `/help` should list `audit-loop`, `bootstrap-project`, `commit-with-provenance`, `render-manuscript`, etc. (10 user-defined commands total).

## Inventory

### Skills (9)
- **audit-remediate-loop** — 5-branch parallel auditor pattern with 3-round cap
- **statistical-analysis** — assumption-driven method selection; HAC + stationary bootstrap inline
- **validate-data** — schema + distribution + provenance checks
- **emit-repro-log** — 13-field ReproLog (port of SKIE-Universe `reproducibility.py`; field list in [skills/emit-repro-log/SKILL.md](skills/emit-repro-log/SKILL.md))
- **deliver-results** — figures (mplstyle + save_figure), workbook (xlsxwriter), report cards
- **pre-register-hypothesis** — freeze design.md with SHA-256 anchor
- **power-analysis** — pre-data n calculation; retrospective power forbidden (Hoenig & Heisey 2001, *Am Stat* 55(1):19, [doi.org/10.1198/000313001300339897](https://doi.org/10.1198/000313001300339897))
- **pit-canary** — point-in-time leakage detection (López de Prado 2018, *Advances in Financial Machine Learning* Ch. 7 "Cross-Validation in Finance", ISBN 978-1-119-48208-6; full citations in [skills/pit-canary/SKILL.md](skills/pit-canary/SKILL.md))
- **multipletest-gate** — family-wise register + correction; methods + DOIs in [skills/multipletest-gate/SKILL.md](skills/multipletest-gate/SKILL.md) (Hansen 2005, White 2000, Benjamini & Hochberg 1995, Holm 1979)

### Slash commands (10)
`/audit-loop`, `/lit-check`, `/reproduce` (existing) · `/cite-add`, `/adr-new`, `/commit-with-provenance`, `/bootstrap-project`, `/hypothesis-new`, `/preregister`, `/render-manuscript` (new).

### Agents (7)
`quant-auditor`, `literature-check`, `reproducibility-verifier` (existing) · `dag-drafter`, `epi-auditor`, `code-reviewer`, `format-auditor` (new).

### Hooks (8)
`session_start_provenance`, `session_end_audit_log`, `pre_write_seed_guard`, `precommit_seed_guard`, `pre_bash_safety`, `post_write_notebook_clean` (existing) · `precommit_citation_cff`, `pre_write_phi_guard` (new; PHI guard cwd-scoped to population-health globs).

### Scripts (5)
`commit_with_provenance.py`, `bootstrap_project.py`, `build_data_manifest.py`, `build_manuscript_reference.py`, `render_manuscript.py`.

## MCP servers

`~/.claude/mcp.json` is the canonical MCP manifest (declares `arxiv` / `arxiv-mcp-server` and `crossref` / `crossref-cite-mcp`). Older per-server descriptors under `scripts/mcp/` (`arxiv.json`, `filesystem.json`, `zenodo.json`) predate the consolidated `mcp.json` and are retained for reference. Auto-registration is not part of deploy.py — register per-machine:

```bash
claude mcp add-json arxiv "$(jq '.mcpServers.arxiv' ~/.claude/mcp.json)"
claude mcp add-json crossref "$(jq '.mcpServers.crossref' ~/.claude/mcp.json)"
```

Zenodo + OSF MCPs are deferred (no canonical server exists yet).

## Updates

```bash
cd ~/dotfiles && git pull --ff-only && python claude/scripts/deploy.py
```

## Deferred (use-case-triggered)

These are functional but un-wired until a real use case arises. Track in this
section; re-evaluate when first encountered:

1. **OSF external pre-registration (R3-2b).** The R3-2a `pre-register-hypothesis` skill freezes design via internal SHA-256 + commit trailer and is fully reproducible. External OSF posting is an `--external=osf` opt-in that requires a thin Python helper around the OSF v2 REST API ([developer.osf.io](https://developer.osf.io/)) and a Personal Access Token at `~/.config/osf/token`. Implement at first external pre-registration.

2. **`~/.claude/` ↔ `s-koirala/dotfiles` layout migration.** Local working tree is flat (`~/.claude/<X>`); remote wraps content in `claude/<X>`. Future migration via `git filter-repo --to-subdirectory-filter claude/` (preserves history) or chezmoi/stow ([chezmoi.io](https://www.chezmoi.io/), [GNU Stow](https://www.gnu.org/software/stow/)). Defer until first push from local to remote.

3. **Pandoc dependency for `/render-manuscript`.** R3-9 ships `reference.docx` (minimalist B&W styling compatible with major clinical-journal submission requirements: double-spaced, 1-inch margins, 12pt body within commonly accepted ranges; NEJM/JAMA/Annals/AJPH author centers do not converge on a single mandatory font but accept Times New Roman as a safe default) + 5 reporting-standard templates (STROBE/CONSORT/STARD/TRIPOD/PRISMA) + render script + slash command. Per-journal style citations live in [skills/deliver-results/SKILL.md](skills/deliver-results/SKILL.md) and [scripts/build_manuscript_reference.py](scripts/build_manuscript_reference.py). Pandoc itself is NOT bundled. Install when first writing a manuscript: `choco install pandoc` (Windows) / `brew install pandoc` (macOS) / `apt install pandoc` (Linux).

## Identity hygiene

This repo lives under the `s-koirala` GitHub account (real-identity account, not pseudonymous). Local `git config --local user.email` is `s-koirala@users.noreply.github.com` (GitHub privacy form) to keep the real email out of public commit history. The **SKIE pseudonym** scope is separate, cwd-scoped via `rules/publishing.md` to `**/project-skie/**`, `**/*publication*/**`, `**/*manuscript*/**`.

## AI-assistance statement

Initial design and R0–R3 implementation (planned in `docs/audits/implementation_plan_dotfiles_additions_2026-05-15.md`): `claude-opus-4-7` in roles `idea`, `code`, `prose`, `audit`. The narrative in this INSTALL.md is AI-drafted; the inventory counts and citations were AI-verified against the filesystem and primary sources. Per [ICMJE recommendations (January 2026)](https://www.icmje.org/recommendations/), AI is acknowledged as a tool, not an author. Audit trail: `docs/audits/` (14 audit_trail files covering plan-compile, R0, every R1 item, every R2 subitem, R3 consolidated, and this INSTALL.md, plus the implementation plan and research memo — 16 files total). Reproducibility envelope per `CLAUDE.md` §Reproducibility.

## License

License file pending in the public repo; until added, treat content as released under MIT terms by the GitHub account holder. Real-name attribution discoverable from the GitHub account; never written into committed files.
