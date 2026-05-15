---
name: audit-remediate-loop
description: Run the research→audit→remediate agentic QC pattern with a 3-round cap and structured findings. Invoke for any non-trivial implementation or analysis deliverable.
---

# Audit-Remediate Loop

## When to invoke
Any non-trivial deliverable: new statistical method, new module, new analysis notebook, revised claim. Skip for formatting, renames, or <20-line patches.

## Cap
Max 3 audit rounds. Empirical basis: multi-agent self-consistency gains taper at moderate sample counts ([arXiv 2511.00751](https://arxiv.org/abs/2511.00751)); 3 is an operational cost/coverage choice, not a result in the cited paper. If residuals remain after round 3, surface them to the user — do not continue silently.

## Loop structure

### Round N (N ∈ {1, 2, 3})

1. **Produce/revise.** The lead agent (main session) produces or revises the artifact.
2. **Audit — spawn specialist auditors in parallel.** Brief each with:
   - The artifact path(s).
   - The task spec and acceptance criteria.
   - `CLAUDE.md` + relevant `rules/*.md`.
   - A directive to return findings only as structured JSON:
     ```
     { "round": N,
       "findings": [
         {"severity": "critical|major|minor", "location": "file:line",
          "issue": "...", "evidence": "...", "fix": "..."}
       ],
       "residual_risk": "..." }
     ```
   Spawn all relevant auditors in a single message (parallel `Agent` calls) so they run concurrently. See §"Auditor selection" below.
3. **Triage.** Drop `minor` findings unless the user's task specifically invites polish. `critical` blocks progression; `major` is remediated this round.
4. **Remediate.** Apply fixes. Each fix references the finding ID in its commit message or doc note.
5. **Exit check.** If `findings == []` or only `minor` remain → exit. Otherwise increment N.

### Post-loop
- Emit `audit_trail_{YYYY-MM-DD}_{slug}.md` under `docs/audits/` listing every finding + disposition + round number.
- Record final residual risk in the project README or analysis doc.

## Auditor selection — 5 parallel specialist branches

Pattern: parallel-specialist-ensemble ("Mixture of Agents" per [Wang et al. 2024 arXiv:2406.04692](https://arxiv.org/abs/2406.04692); multi-agent debate per [Du et al. 2023 arXiv:2305.14325](https://arxiv.org/abs/2305.14325)). Each auditor covers a non-overlapping concern; mixed-concern artifacts get multiple auditors spawned in parallel.

| Concern (user's 4-branch model + repro) | Auditor | Cwd scoping |
|---|---|---|
| **Calculations** (statistical method fidelity, numerical correctness) | [`quant-auditor`](../../agents/quant-auditor.md) | quant cwds (rules/quant-project.md globs) |
| **Calculations** (epi causal inference, E-value, STROBE/CONSORT/STARD/TRIPOD/PRISMA coverage) | [`epi-auditor`](../../agents/epi-auditor.md) | epi cwds (rules/population-health.md globs) |
| **Research** (citation validity, primary-source verification, method-attribution accuracy) | [`literature-check`](../../agents/literature-check.md) | cwd-agnostic |
| **Reproducibility** (ReproLog completeness, atomic-write spec, git HEAD logging, replay anchors) | [`reproducibility-verifier`](../../agents/reproducibility-verifier.md) | cwd-agnostic |
| **Coding** (Python/general code quality, idiom, types, error handling, design patterns) | [`code-reviewer`](../../agents/code-reviewer.md) | cwd-agnostic |
| **Formatting** (magic-numbers compliance, identity hygiene, template substitution, citation-format consistency, filename convention) | [`format-auditor`](../../agents/format-auditor.md) | cwd-agnostic |

### Routing rules

- **Code-bearing artifacts** (`.py`, `.ipynb`): always include `code-reviewer`.
- **Statistical analyses / backtests / inferences**: include `quant-auditor` (quant) OR `epi-auditor` (epi).
- **Artifacts with citations**: include `literature-check`.
- **Artifacts emitting ReproLog / dataset manifest / commits with provenance trailers**: include `reproducibility-verifier`.
- **Anything destined for `~/.claude/` or with magic-number / identity-hygiene exposure**: include `format-auditor`.
- **Quant vs epi**: never both for the calculations branch. Cwd-rule globs determine which.

### Empirical basis for parallel-specialist over single-auditor

Single-auditor approaches have known coverage gaps (Wang et al. 2024 Mixture-of-Agents §3.2 reports +6.4% MT-Bench score for 4-agent vs 1-agent ensembles). Specialist branches reduce the cross-domain dilution that occurs when one agent reasons over heterogeneous concerns (code + citations + repro + format).

## Empirical justification
- Single-shot code-generation baselines are weak on statistical code: DS-1000 Pandas Pass@1 = 0.265 (Codex-002; [arXiv 2211.11501](https://arxiv.org/abs/2211.11501)).
- Research-grade: SciCode main problems — Claude-3.5-Sonnet 4.6% ([arXiv 2407.13168](https://arxiv.org/abs/2407.13168)).
- Reflection/self-consistency improves code+reasoning: +17.9 pp GSM8K ([Wang et al., arXiv 2203.11171](https://arxiv.org/abs/2203.11171)).
Audit is empirically required; cap reflects diminishing-returns evidence, not a result for n=3 specifically.
