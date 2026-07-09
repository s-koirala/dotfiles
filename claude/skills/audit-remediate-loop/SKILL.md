---
name: audit-remediate-loop
description: Run the research→audit→remediate agentic QC pattern with a 3-round cap and structured findings. Invoke for any non-trivial implementation or analysis deliverable.
---

# Audit-Remediate Loop

## When to invoke
Any non-trivial deliverable: new statistical method, new module, new analysis notebook, revised claim. Skip for formatting, renames, or <20-line patches.

## Cap
Max 3 audit rounds. Empirical basis: single-model self-consistency gains taper at moderate sample counts ([arXiv 2511.00751](https://arxiv.org/abs/2511.00751)), extrapolated here to audit rounds, and multi-agent debate accuracy can degrade over rounds via sycophancy ([arXiv 2509.05396](https://arxiv.org/abs/2509.05396)); 3 is an operational cost/coverage choice, not a result in the cited papers. If residuals remain after round 3, surface them to the user — do not continue silently.

## Execution mechanism

**Primary — Workflow engine.** When the Workflow tool is available, invoke [workflows/audit-remediate.js](../../workflows/audit-remediate.js). One invocation = one round (route → parallel specialist audit → refute gate → triage); the lead session remediates between rounds and re-invokes with `round+1`. The 3-round cap is enforced in-script. Args contract (documented in the script header):

```json
{ "artifacts": ["<path>", ...], "taskSpec": "...", "cwd": "<project cwd>",
  "date": "YYYY-MM-DD", "round": 1,
  "flags": {"citations": false, "repro": false, "identity": false, "statistical": false},
  "invitesPolish": false, "priorDispositions": "<summary of prior rounds; only for round > 1>" }
```

Pass args as a JSON object; the script also tolerates a JSON-encoded string. Routing is deterministic from extensions, cwd globs, and flags (no agent involved); the script throws if `quant-auditor` and `epi-auditor` would ever co-run. The workflow returns `{remediate, refuted, minors_logged, residual_risks, verdict, next}`; the lead session applies fixes and, on exit, performs the post-loop steps below.

**Fallback — parallel Agent calls.** On harnesses without the Workflow tool, execute §"Loop structure" below directly. It is the original procedure, semantically unchanged except two documented insertions: the refutation pass (step 4) and the upgraded findings schema in step 2.

## Loop structure (fallback path)

### Round N (N ∈ {1, 2, 3})

1. **Produce/revise.** The lead agent (main session) produces or revises the artifact.
2. **Audit — spawn specialist auditors in parallel.** Brief each with:
   - The artifact path(s).
   - The task spec and acceptance criteria.
   - `CLAUDE.md` + relevant `rules/*.md`.
   - A directive to return findings only as structured JSON (the full 8-field schema from the agent definitions — `id` is load-bearing: refutations key on it):
     ```
     { "round": N,
       "findings": [
         {"id": "F-<round>-<n>", "severity": "critical|major|minor",
          "category": "...", "location": "file:line",
          "issue": "...", "evidence": "...", "fix": "...", "reference": "..."}
       ],
       "residual_risk": "...",
       "verdict": "block|proceed-with-remediation|accept" }
     ```
   Spawn all relevant auditors in a single message (parallel `Agent` calls) so they run concurrently. See §"Auditor selection" below.
3. **Triage.** Drop `minor` findings unless the user's task specifically invites polish. `critical` blocks progression; `major` is remediated this round.
4. **Refute.** For every surviving `critical`/`major` finding, spawn an adversarial refuter (parallel `Agent` calls, one per finding) briefed with the artifact path(s) and the full finding, prompted to disprove it per §"Refute-gate triage rule". Findings refuted with concrete counter-evidence are logged with disposition `refuted` and removed from the remediation list.
5. **Remediate.** Apply fixes. Each fix references the finding ID in its commit message or doc note.
6. **Exit check.** If no `critical`/`major` findings survive the gate → exit. Otherwise increment N.

### Post-loop
- Emit `audit_trail_{YYYY-MM-DD}_{slug}.md` under `docs/audits/` listing every finding + disposition + round number, including refute-gate dispositions.
- Record final residual risk in the project README or analysis doc.

## Refute-gate triage rule

Every `critical`/`major` finding passes an adversarial refuter before remediation. The refuter's single job is to disprove the finding: reproduce the claimed evidence, check the cited source, run the counter-test. A finding is dropped only on `refuted: true` with a concrete evidence type (`reproduced-check | source-quote | counter-test | logical-proof`) — bare doubt, plausibility arguments, or severity quibbles never drop a finding, guarding against systematic reviewer overcorrection ([AUSE 2026, doi 10.1007/s10515-026-00638-5](https://doi.org/10.1007/s10515-026-00638-5); judge consistency ≠ validity, [arXiv 2606.19544](https://arxiv.org/abs/2606.19544)). Empirical basis for the gate: adversarial verification killed ~79–83% of candidate findings as false positives in LLM-assisted defect discovery ([arXiv 2604.19049](https://arxiv.org/abs/2604.19049); C/C++ security libraries, compilers, and standards targets — directional, not a calibration target). Refuted findings are logged, never silently discarded. Gate recall is measured by the seeded-defect suite in [evals/](evals/) — a gate that kills seeded true defects fails the eval.

## Auditor selection — 5 parallel specialist branches

Pattern: parallel-specialist-ensemble ("Mixture of Agents" per [Wang et al. 2024 arXiv:2406.04692](https://arxiv.org/abs/2406.04692); multi-agent debate per [Du et al. 2023 arXiv:2305.14325](https://arxiv.org/abs/2305.14325)). Each auditor covers a non-overlapping concern; mixed-concern artifacts get multiple auditors spawned in parallel.

| Concern (user's 4-branch model + repro) | Auditor | Cwd scoping |
|---|---|---|
| **Calculations** (statistical method fidelity, numerical correctness) | [`quant-auditor`](../../agents/quant-auditor.md) | quant cwds (rules/quant-project.md globs); also the cwd-agnostic statistical default |
| **Calculations** (epi causal inference, E-value, STROBE/CONSORT/STARD/TRIPOD/PRISMA coverage) | [`epi-auditor`](../../agents/epi-auditor.md) | epi cwds (rules/population-health.md globs) |
| **Research** (citation validity, primary-source verification, method-attribution accuracy) | [`literature-check`](../../agents/literature-check.md) | cwd-agnostic |
| **Reproducibility** (ReproLog completeness, atomic-write spec, git HEAD logging, replay anchors) | [`reproducibility-verifier`](../../agents/reproducibility-verifier.md) | cwd-agnostic |
| **Coding** (project docstring/citation conventions, statistical-code idiom, ~/.claude production standards — general diffs go to the built-in `/code-review`) | [`code-reviewer`](../../agents/code-reviewer.md) | cwd-agnostic |
| **Formatting** (magic-numbers compliance, identity hygiene, template substitution, citation-format consistency, filename convention) | [`format-auditor`](../../agents/format-auditor.md) | cwd-agnostic |

### Routing rules

- **Code-bearing artifacts** (`.py`, `.ipynb`): always include `code-reviewer`.
- **Statistical analyses / backtests / inferences**: include `quant-auditor` (quant or neutral cwd) OR `epi-auditor` (epi cwd).
- **Artifacts with citations**: include `literature-check`.
- **Artifacts emitting ReproLog / dataset manifest / commits with provenance trailers**: include `reproducibility-verifier`.
- **Anything destined for `~/.claude/` or with magic-number / identity-hygiene exposure**: include `format-auditor`.
- **Quant vs epi**: never both for the calculations branch. Cwd-rule globs determine which; neutral cwds default to `quant-auditor`.

### Empirical basis for parallel-specialist over single-auditor

Single-auditor approaches have known coverage gaps (Wang et al. 2024 Mixture-of-Agents §3.3 Table 3: multiple-proposer vs single-proposer AlpacaEval 2.0 win rates 61.3% vs 56.7% at n=6, +4.6 pp, with consistent gains at n=2 and n=3). Specialist branches reduce the cross-domain dilution that occurs when one agent reasons over heterogeneous concerns (code + citations + repro + format). Intrinsic reasoning strength and group diversity are the dominant drivers of multi-agent debate success ([arXiv 2511.07784](https://arxiv.org/abs/2511.07784)) — diverse specialist lenses, not more homogeneous rounds.

## Empirical justification
- Single-shot code-generation baselines are weak on statistical code: DS-1000 Pandas Pass@1 = 0.265 (Codex-002; [arXiv 2211.11501](https://arxiv.org/abs/2211.11501)).
- Research-grade: SciCode main problems — Claude-3.5-Sonnet 4.6% ([arXiv 2407.13168](https://arxiv.org/abs/2407.13168)).
- Self-consistency improves arithmetic/commonsense reasoning: +17.9 pp GSM8K ([Wang et al., arXiv 2203.11171](https://arxiv.org/abs/2203.11171)); applied to code review by extrapolation.
- External auditors over self-review: attributing an erroneous claim to an external source rather than the model's own reasoning lifts explicit-correction rates by 23–93 pp ([arXiv 2606.05976](https://arxiv.org/abs/2606.05976); role-attribution study — mechanistic support, applied by extrapolation).
- Round cap: debate accuracy can degrade over rounds via sycophancy and conformity ([arXiv 2509.05396](https://arxiv.org/abs/2509.05396)), corroborating the plateau in [arXiv 2511.00751](https://arxiv.org/abs/2511.00751).
- Refute gate: adversarial verification kills ~79–83% of candidate findings as false positives ([arXiv 2604.19049](https://arxiv.org/abs/2604.19049); C/C++ security libraries, compilers, and standards targets — directional).

Audit is empirically required; cap reflects diminishing-returns evidence, not a result for n=3 specifically.
