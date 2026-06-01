---
title: Audit trail — research_memo_dotfiles_additions_2026-05-15
date: 2026-05-15
type: audit_trail
subject: docs/audits/research_memo_dotfiles_additions_2026-05-15.md
loop: audit-remediate-loop
rounds_completed: 1
rounds_cap: 3
exit_reason: all critical + major findings remediated; no further critical/major residuals
---

# Audit trail

## Round 1 — auditors

- `literature-check` (citation validity, primary-source verification)
- `quant-auditor` (method fidelity, internal consistency, constraint compliance, infra compatibility)

Spawned in parallel per skill spec (mixed-concern artifact).

## Round 1 findings + disposition

| ID | Source | Severity | Location | Issue (compressed) | Disposition |
|---|---|---|---|---|---|
| F-1-1 | quant-auditor | **critical** | §B.7, §C.2 #19 | Sharpe-CI tree reversed Lo vs Opdyke roles | **fixed**: rewrote as assumption-keyed table; IID-Gaussian→textbook; IID-non-Gaussian→Opdyke; serial-dep→Lo or Ledoit-Wolf; pairwise→Ledoit-Wolf; family→White/Hansen |
| LIT-1 | literature-check | **critical** | [^38] | Bailey-LdP "Sharpe Ratio Efficient Frontier" 2014/J Risk DOI conflates two distinct papers | **fixed**: [^38] now cites Bailey-LdP 2014 *J Portfolio Mgmt* 40(5):94-107 Deflated Sharpe (DOI 10.3905/jpm.2014.40.5.094); note added about distinct 2012 Sharpe Efficient Frontier paper |
| F-1-2 | quant-auditor | major | §C.2 #24 | E-value scope mismatch (assigned to quant-auditor) | **fixed**: reassigned to new `agents/epi-auditor.md`, cwd-scoped to population-health; Frank 2000 ITCV cited as quant analog |
| F-1-3 | quant-auditor | major | §A.3 | the upstream library has both `runs/` AND `artifacts/runs/`; claim of "1:1 + rename" wrong | **fixed**: bootstrap emits both; consolidation deferred to per-project ADR |
| F-1-4 | quant-auditor | major | §A.5 | "No hook changes required" overstated; deps-sha degrades w/o venv | **fixed**: weakened to "hook compatibility holds provided uv sync runs"; `venv_created` field added to manifest |
| F-1-5 | quant-auditor | major | §0 ↔ §6 | Internal contradiction (top-5 vs round-1) | **fixed**: §0 now references §6 as source of truth; top-5 deleted |
| F-1-6 | quant-auditor | major | frontmatter | Memo's own repro anchors absent | **fixed**: pip_freeze_sha256, dataset_checksums, rng_seed, model_commit, reporting_standard added (with n/a markers where applicable) |
| F-1-8 | quant-auditor | major | §0, §A.4 | Magic numbers: Python 3.11 unjustified; "5-occurrence" ≠ CLAUDE.md ">5 times" | **fixed**: Python version now read from the upstream library's pyproject at bootstrap time; numba wheel matrix cited; ">5 times" quoted verbatim |
| F-1-11 | quant-auditor | major | §C.1, §C.2 #20 | leakage-auditor agent redundant with quant-auditor | **fixed**: dropped agent; pit-canary skill invoked by existing quant-auditor |
| LIT-2 | literature-check | major | §B.3 axes.prop_cycle | tab10/Wong misattribution (tab10 = Tableau-10, not Wong-Okabe-Ito) | **fixed**: replaced tab10 with explicit Okabe-Ito 8-color hex list; Wong [^17] citation retained for the actual palette |
| LIT-3 | literature-check | major | [^67] | Confirmed duplicate of [^8] | **fixed**: [^67] removed; §C.2 #22 citation changed to [^8] |
| LIT-4 | literature-check | major | §B.3 pdf.fonttype | "TrueType (Type 42)" terminology imprecise | **fixed**: rephrased as "fonttype=42 yields TrueType embedding; Type 42 is PostScript's TrueType wrapper" |
| LIT-5 | literature-check | major | [^13] | Nature URL returns 404 | **fixed**: URL corrected to https://www.nature.com/documents/nature-final-artwork.pdf |
| LIT-6 | literature-check | major | §B.3 savefig.dpi | DPI claim inverted (300=halftone not line-art) | **fixed**: savefig.dpi description corrected to "300 dpi photograph/halftone minimum; 600 dpi for line art / combination figures via `target=print_600`" |
| F-1-7 | quant-auditor | minor | §C.1 | "24 ADRs" — actually 23 | **fixed**: count corrected against the upstream library's ADR directory |
| F-1-9 | quant-auditor | minor | §C.2 #21 | Politis-Romano vs Politis-White conflation | **fixed**: row title and inline text now distinguish stationary bootstrap (Politis-Romano 1994 [^78]) from automatic block-length selector (Politis-White 2004 [^66]) |
| F-1-10 | quant-auditor | minor | §C.2 #8 | Schoenfeld 1982 vs Grambsch-Therneau 1994 conflated | **fixed**: now cites both — Grambsch-Therneau [^53] extending Schoenfeld 1982 [^77] |
| F-1-12 | quant-auditor | minor | §C.2 #7 | power-analysis gate placement inverted (between validate-data and statistical-analysis was wrong) | **fixed**: gate is now pre-register → power-analysis → validate-data → statistical-analysis; Hoenig-Heisey 2001 cited [^76] for retrospective-power caveat |
| F-1-13 | quant-auditor | minor | §5 | 3 non-decisive open questions (Q5/Q9/Q10) | **fixed**: collapsed into defaulted-preferences block; 7 decisive questions remain |
| F-1-14 | quant-auditor | minor | [^67] dup ref | duplicate ref | **fixed** (same as LIT-3) |
| F-1-15 | quant-auditor | minor | §0 grammar | sentence fragments in "magic numbers" claim | **fixed**: rewrote as "the only numeric literals introduced are…" |
| LIT-7 | literature-check | minor | [^11] | matplotlib "since v2.0" claim needs release-notes URL | **fixed**: added v2.0 release notes URL alongside customizing.html |
| LIT-8 | literature-check | minor | [^15] | viridis citation could be strengthened with Kovesi 2015 | **fixed**: Kovesi 2015 arXiv:1509.03700 added as [^74] |
| LIT-9 | literature-check | minor | [^16] | Crameri 2020 thrust mischaracterized (advocates batlow primarily) | **fixed**: description softened to "lists viridis among acceptable alternatives while primarily advocating Scientific colour maps (batlow, vik)" |
| LIT-10 | literature-check | minor | Mertens 2002 missing | Should be cited explicitly since Opdyke description references it | **fixed**: added as [^75] (tier-4: unpublished WP) |
| LIT-11 | literature-check | minor | [^40][^41] JSTOR DOIs | Concern raised but: JSTOR DOIs ARE canonical for pre-2000 papers in these journals | **noted** — no change required |
| LIT-12 | literature-check | minor | [^33] AR(1) labeling | "AR(1) baseline" understates Lo's scope | **fixed**: now "IID baseline and time-series-corrected SE for stationary returns" |

## Counts

- Critical: 2 (both fixed)
- Major: 11 (all fixed)
- Minor: 14 (12 fixed; 1 noted no-change; 1 collapsed into another fix)

## Residual risk

From quant-auditor: "14 NEEDED items in round 1 against an existing infrastructure of 3 skills + 3 agents + 3 commands + 6 hooks; the implementation surface roughly triples, and the dependency map (§4) is hand-drawn rather than derived from a manifest."

From literature-check: "(1) Nature artwork PDF binary parsing prevented direct primary read for DPI/font-size claims — relied on consistent secondary aggregators; (2) book citations [^18 Tufte], [^50 Pearl], [^51 Cohen], [^65 LdP] not online-verifiable but ISBNs match standard editions; (3) Mertens 2002 is tier-4 (unpublished WP); (4) ICMJE January 2026 update flagged as recent — assertion stands but full version-diff between 2024 and 2026 not parsed."

**Net residual risk after round 1:** the memo's recommendations are method-fidelity-clean and citation-clean. The unaddressed concern is implementation surface — even at the proposed round-1 of only 4 foundation items (ReproLog, MCP, CITATION.cff, ADR), each downstream proposal adds dependency tracing the user must validate before merging. Recommendation: at implementation time, treat each `~/.claude` addition as its own audit-remediate-loop target with cap=3.

## Exit decision

Per `audit-remediate-loop` skill spec:
- `findings.critical == 0` after remediation ✓
- `findings.major == 0` after remediation ✓
- only `minor` residuals remain (all addressed or noted) ✓

**Exit round 1.** No round 2 invocation. Residual risk surfaced to user.

## Files modified during round 1

- `docs/audits/research_memo_dotfiles_additions_2026-05-15.md` — 23 edits across frontmatter, §0, §A.3-5, §B.3, §B.7, §C.1, §C.2 (#7, #8, #19, #20, #21, #22, #24), §5, §6, §7 (References)
- `docs/audits/audit_trail_dotfiles_additions_2026-05-15.md` — this file (newly written)

No code, hook, skill, agent, command, rule, or settings file was modified. The output is a research memo only, per the user's "Do NOT implement yet" directive.

## Post-loop amendment (2026-05-15, user directive)

User: "Sharpe is arbitrary and archaic. it will only be a KPI for reporting purposes but no longer an optimization target. I fail to see the relevancy of sharpe to the dotfiles project."

Disposition:
- §C.2 #19 (Sharpe-CI decision tree inline into statistical-analysis) **DROPPED**. Reason: Sharpe-specific machinery is project-scoped (rules/quant-project.md already covers it), not dotfiles-scoped. Generic time-series CI methodology stays in #18 (HAC bandwidth) and #21 (stationary block bootstrap), applicable to any KPI.
- §B.7 quant report card: Sharpe demoted to one row in a KPI table (no decision tree); primary promotion gate is now terminal-wealth-q05 + Calmar + profit-factor + R-multiple (per the upstream library's survival-constrained KPI list).
- Memory written: [`memory/feedback_sharpe_kpi_only.md`](../../memory/feedback_sharpe_kpi_only.md) — Sharpe is reporting KPI only, never an optimization target.
- No change to [`rules/quant-project.md`](../../rules/quant-project.md): existing rule already frames Sharpe under "Inference / report bootstrap CI on Sharpe" — i.e., reporting context, consistent with KPI-only treatment.

Net NEEDED count: 14 → 13.

## Replay anchor

To re-run this audit:
1. Re-spawn `literature-check` against the memo as written at HEAD.
2. Re-spawn `quant-auditor` with the same brief (this audit_trail's "Round 1 — auditors" section).
3. Compare new findings against §1 above. Net-new findings = drift; absent findings = remediation stuck.

The upstream-library layout/source references in the memo should be re-checked at replay time and compared against the `dataset_checksums` frontmatter field of the memo (currently a placeholder; will be populated when `~/.claude` becomes a git repo per pillar A round-0 prerequisite).
