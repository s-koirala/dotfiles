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
2. **Audit — spawn `quant-auditor` subagent.** Brief it with:
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
3. **Triage.** Drop `minor` findings unless the user's task specifically invites polish. `critical` blocks progression; `major` is remediated this round.
4. **Remediate.** Apply fixes. Each fix references the finding ID in its commit message or doc note.
5. **Exit check.** If `findings == []` or only `minor` remain → exit. Otherwise increment N.

### Post-loop
- Emit `audit_trail_{YYYY-MM-DD}_{slug}.md` under `docs/audits/` listing every finding + disposition + round number.
- Record final residual risk in the project README or analysis doc.

## Auditor selection
- Code correctness / method fidelity: `quant-auditor`.
- Citation validity / literature claims: `literature-check`.
- Reproducibility artifacts: `reproducibility-verifier`.
- For mixed-concern artifacts, run auditors in parallel (single message, multiple Agent calls).

## Empirical justification
- Single-shot code-generation baselines are weak on statistical code: DS-1000 Pandas Pass@1 = 0.265 (Codex-002; [arXiv 2211.11501](https://arxiv.org/abs/2211.11501)).
- Research-grade: SciCode main problems — Claude-3.5-Sonnet 4.6% ([arXiv 2407.13168](https://arxiv.org/abs/2407.13168)).
- Reflection/self-consistency improves code+reasoning: +17.9 pp GSM8K ([Wang et al., arXiv 2203.11171](https://arxiv.org/abs/2203.11171)).
Audit is empirically required; cap reflects diminishing-returns evidence, not a result for n=3 specifically.
