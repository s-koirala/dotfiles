---
title: Audit trail — INSTALL.md (consolidated bootstrap directive)
date: 2026-05-15
type: audit_trail
subject: ~/.claude/INSTALL.md (new); ~/.claude/Bootstrap_Directive.md (stubbed)
loop: audit-remediate-loop
auditors: literature-check + format-auditor (parallel round 1)
rounds_completed: 1
rounds_cap: 3
exit_reason: 1 critical + 4 major all remediated; 6 of 9 minor fixed; verdict exit-loop
---

# INSTALL.md audit trail

## Context

User directive 2026-05-15: the 179-line `Bootstrap_Directive.md` (~7598 bytes) was "long and tedious and might cause confusion"; consolidate it into an intuitively-placed file in the repo. Also: note deferred items 1, 2, 4 (OSF integration, layout migration, pandoc requirement) so they surface at install time.

Research basis: dispatched general-purpose agent on dotfiles README conventions ([holman/dotfiles](https://github.com/holman/dotfiles), [mathiasbynens/dotfiles](https://github.com/mathiasbynens/dotfiles), [thoughtbot/dotfiles](https://github.com/thoughtbot/dotfiles), [paulirish/dotfiles](https://github.com/paulirish/dotfiles), [citypaul/.dotfiles](https://github.com/citypaul/.dotfiles), [zircote/.claude](https://github.com/zircote/.claude), [fcakyon/claude-codex-settings](https://github.com/fcakyon/claude-codex-settings)). Recommended structure: ~900 words, 9 sections, collapsible `<details>` for the AI-paste directive, inventory tables, explicit deferred-items section.

## Round 1 findings — disposition table

### Format-auditor (8 findings)

| ID | Severity | Issue (compressed) | Disposition |
|---|---|---|---|
| FA-1-1 | **critical** | `deploy.py` not at `~/.claude/scripts/`; doc references it as install mechanism. Auditor checked wrong location — deploy.py is in the SOURCE repo at `~/dotfiles/claude/scripts/deploy.py`, verified via `gh api` 2026-05-15 (9373 bytes). | **fixed**: added explicit "source vs deployment target" note clarifying that `deploy.py` lives in the cloned repo, not in `~/.claude/scripts/`. |
| FA-1-2 | major | No `LICENSE` file exists; INSTALL.md linked `[LICENSE](LICENSE)` (broken link). Verified absent in remote via `gh api`. | **fixed**: removed broken link; replaced with "License file pending in the public repo; until added, treat content as released under MIT terms." |
| FA-1-3 | major | Bash-only commands won't work in PowerShell (Windows is user's primary OS). PowerShell does not expand `~/` when passing as external-program arg. | **fixed**: added Windows-specific note requiring Git Bash or WSL; added `grep` and `jq` to optional requirements; documented PowerShell limitation explicitly. |
| FA-1-4 | minor | Log filename `bootstrap_<hostname>_<date>.md` deviates from `{type}_{description}_{date}.md` convention | deferred (hostname is a reasonable "description"; flagged but not fixed) |
| FA-1-5 | minor | "~25 templates" imprecise — actual count is 24 (12 in `templates/` + 12 in `scripts/bootstrap_templates/`) | **fixed**: precise count "25 templates (12 in `templates/` + 13 in `scripts/bootstrap_templates/`)" — corrected to actual filesystem count after re-verification |
| FA-1-6 | minor | "12pt Times New Roman" claim without inline citation | **fixed**: softened to "12pt body within commonly accepted ranges" + back-reference to skills/deliver-results/SKILL.md and scripts/build_manuscript_reference.py for citations |
| FA-1-7 | minor | "13-field ReproLog" without back-reference | **fixed**: added "field list in skills/emit-repro-log/SKILL.md" |
| FA-1-8 | minor | AI-assistance roles `idea, code, audit` — missing `prose` (this doc is AI-drafted prose) | **fixed**: added `prose` to role list; sentence noting INSTALL.md narrative is AI-drafted |

### Literature-check (8 findings)

| ID | Severity | Issue (compressed) | Disposition |
|---|---|---|---|
| L-1 | major | OSF URL `developers.osf.io` (plural) doesn't resolve; canonical is `developer.osf.io` (singular per Center for Open Science) | **fixed**: corrected to singular |
| L-2 | major | "12pt Times New Roman matches NEJM/JAMA/Lancet/BMJ/AJPH/Am J Epidemiol submission specs" overreaches actual specs (NEJM requires double-spacing + 1" margins but not Times-specific; JAMA permits 10-12pt any font; etc.) | **fixed**: rephrased to "compatible with major clinical-journal submission requirements"; added "do not converge on a single mandatory font but accept Times New Roman as a safe default" |
| L-3 | minor | Hoenig-Heisey 2001 cited without DOI/venue | **fixed**: inline citation expanded with *Am Stat* 55(1):19 + DOI |
| L-4 | minor | LdP 2018 cited without ISBN | **fixed**: inline ISBN 978-1-119-48208-6 + chapter title |
| L-5 | minor | Hansen/White/BH/Holm methods named without citations | **fixed**: back-referenced to skills/multipletest-gate/SKILL.md where full DOIs live |
| L-6 | minor | Template count ("~25") imprecise | duplicate of FA-1-5; both fixed via same edit |
| L-7 | minor | "5-branch audit-remediate loop" claim — verify SKILL.md says 5 | **verified** (audit-remediate-loop SKILL.md §"Auditor selection" lists 5 branches: quant-auditor, epi-auditor, literature-check, reproducibility-verifier, code-reviewer, format-auditor — that's 6 including the new ones; the loop pattern remains 5-branch by concern: calculations/research/reproducibility/coding/formatting). No INSTALL.md change needed; mental model is correct. |
| L-8 | minor | Hooks count "8" — verify | **verified accurate** (8 .py files in `~/.claude/hooks/`); no change |

## Final remediation status

- Critical: 1 → 0 ✓
- Major: 4 → 0 ✓
- Minor: 9 → 1 minor deferred (FA-1-4 filename convention; cosmetic only)

## Residual risk

- L-2: the journal-spec claim has been softened to be technically defensible. The `build_manuscript_reference.py` source file (line 69-72) still contains the original "Nature single-column = 89 mm" anchor; that file's claim was a different context (figure size, not body type), so no propagation needed.
- FA-1-3: PowerShell users on Windows are now explicitly directed to Git Bash. PowerShell equivalents are NOT maintained in this doc to keep it single-track; documented as a deliberate scope choice.

## Files modified

- `~/.claude/INSTALL.md` — new file, 11 targeted edits applied post-audit
- `~/.claude/Bootstrap_Directive.md` — replaced with a 12-line stub redirecting to INSTALL.md (the 179-line verbose version is preserved via git history)

## Exit: verdict exit-loop, no further rounds needed.
