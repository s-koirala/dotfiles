# Seeded-defect eval suite for the audit-remediate loop

Internal benchmark of record for the audit-remediate skill/workflow. Public
agent benchmarks are gameable ([BenchJack, arXiv 2605.12673](https://arxiv.org/abs/2605.12673));
this suite plants known defects in small fixtures so detection can be scored
against ground truth. Created per WI-5 of
[implementation_plan_bootstrap_modernization_2026-07-09.md](../../../docs/audits/implementation_plan_bootstrap_modernization_2026-07-09.md).

## Layout

- [evals.json](evals.json) — case registry: 6 defect cases (E1–E6) + 2 clean
  controls (C1, C2). Each case carries `fixture`, `defect_class` (defect cases
  only), `ground_truth` (`location`, `expected_severity`, `expected_branch`),
  and a one-sentence pass `assertion`.
- [fixtures/](fixtures/) — one small artifact per case (each ≤ 40 lines).
  Every defect fixture contains exactly one planted defect and is otherwise
  clean (seeded RNG, real citations, justified constants) so detection is
  unambiguous. Each fixture's header comment declares its case id and class;
  do not "fix" fixtures.

## Registry semantics

- `expected_branch` is an array; the case passes if at least one listed
  auditor branch reports the defect (relevant for E6, where quant-auditor and
  code-reviewer legitimately overlap).
- `expected_severity` is the severity band the finding should land in
  (`critical` or `major`); a finding one band off is scored as
  class-detected/severity-missed, not as a miss.
- Clean cases set `expected_findings_post_gate: 0` — the pass condition is
  zero critical/major findings after the refute gate; the raw pre-gate count
  is recorded, not penalized.

## Run procedure

Per case:

1. Spawn the audit loop against the fixture path.
   - Primary: the Workflow engine script at
     [workflows/audit-remediate.js](../../../workflows/audit-remediate.js)
     (route → audit → refute → triage stages).
   - Fallback (harnesses without the Workflow tool): the parallel-Agent
     procedure documented in [SKILL.md](../SKILL.md) §Loop structure.
2. Collect the consolidated findings JSON (post-refute-gate survivors plus
   the logged `refuted` dispositions).
3. Compare against the case's `ground_truth`:
   - defect found (binary): any surviving finding whose location matches
     `ground_truth.location` (same file, line within ±2 of the annotated
     line/range — findings often anchor on the enclosing statement);
   - correct class: the finding's issue text identifies the
     `defect_class`;
   - correct severity band per §Registry semantics;
   - correct branch: the finding originates from a branch in
     `expected_branch`.
4. Record raw (pre-gate) and surviving (post-gate) finding counts for every
   case, defect and clean alike.

The skill-creator plugin eval harness supports with/without-skill
benchmarking and A/B comparison over an `evals/evals.json` registry; this
registry is structured to be consumable by that harness (array of cases with
id, fixture, ground truth, assertion).

## Suite metrics

- **Recall on seeded defects**: fraction of E1–E6 with the defect found
  post-gate. A refute gate that kills a seeded true defect fails the eval
  (gate-overcorrection check, per the plan risk register;
  [AUSE 2026, doi 10.1007/s10515-026-00638-5](https://doi.org/10.1007/s10515-026-00638-5)).
- **False positives on clean artifacts**, reported both pre- and
  post-refute-gate on C1/C2. The gate's headline metric:
  [arXiv 2604.19049](https://arxiv.org/abs/2604.19049) reports ~79–83% of raw
  candidate findings die under adversarial verification, so most raw findings
  on clean artifacts should be killed at the gate (expected post-gate count ≈ 0).
- Per-case binary sub-scores: defect found, correct class, correct severity
  band, correct branch.

## Hold-out discipline

This suite is the optimization target once GEPA runs (below). To limit eval
overfitting — auditor prompts tuned to exactly these 6 defect classes —
**expand the suite with new cases (new defect classes and fresh fixtures for
existing classes) before any optimizer run**, and hold out a subset never
shown to the optimizer. Rationale: plan risk register "Eval overfitting";
internal suites are preferred precisely because public benchmarks are
gameable ([arXiv 2605.12673](https://arxiv.org/abs/2605.12673)).

## Notes on the pre-write seed guard

- [hooks/pre_write_seed_guard.py](../../../hooks/pre_write_seed_guard.py)
  excludes any path containing a `fixtures`, `tests`, or `test` segment
  (`_is_excluded`), so writing these fixtures does **not** trigger the guard.
  No Write was blocked during suite creation. The same E4/E5 content written
  to a production (non-fixtures) path would be in scope for the guard's
  magic-number check.
- The guard treats any `default_rng(...)` call — including the argless,
  unseeded form — as a seed declaration (`_is_seed_call`), so E4's defect is
  invisible to the hook even on production paths. E4 therefore exercises the
  `reproducibility-verifier` branch (ReproLog claim vs code), not the hook;
  the hook gap is a known limitation of the guard, not of this suite.

## Note on the fabricated DOI (E3)

`10.5555/quant.2019.0042` was verified non-resolving on 2026-07-09
(HTTP 404 from doi.org, vs 302 for every real DOI cited in the fixtures).
`10.5555` is additionally the reserved example DOI prefix, so the case
remains safe even if resolution is unavailable at run time.

## Deferred — GEPA prompt optimization

**Status: deferred until ≥ 1 full baseline run of this suite exists.** GEPA
requires a metric; this suite provides it. Deferral also satisfies the
CLAUDE.md rule that prompts reused > 5 times get search-based optimization,
not hand-tuning.

Procedure (execute only after the baseline run):

1. Pin the DSPy version from the [DSPy changelog](https://github.com/stanfordnlp/dspy/releases)
   at implementation time — the [GEPA docs](https://dspy.ai/api/optimizers/GEPA/overview/)
   state no minimum version.
2. Optimize the auditor prompts with `dspy.GEPA`
   ([arXiv 2507.19457](https://arxiv.org/abs/2507.19457), ICLR 2026 oral;
   reported >10% over MIPROv2 and up to 20% over GRPO with up to 35x fewer
   rollouts), configured as:
   - `auto='light'`;
   - `reflection_lm` strictly stronger than the task lm (GEPA requirement:
     the reflection model proposes prompt mutations from textual feedback);
   - metric = textual comparison of auditor findings against the seeded
     ground truth in [evals.json](evals.json) (GEPA consumes textual
     feedback natively — return the ground-truth `note`/`assertion` diff as
     the feedback string, not just a scalar score).
3. Before the run, expand the suite and hold out cases per §Hold-out
   discipline; report optimized-vs-baseline recall and clean-artifact false
   positives on the held-out cases only.
