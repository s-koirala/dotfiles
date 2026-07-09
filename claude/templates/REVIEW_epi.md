# REVIEW.md — population-health project review directives

Source of record: this file encodes [rules/population-health.md](https://github.com/s-koirala/dotfiles/blob/main/claude/rules/population-health.md) from these dotfiles. The per-repo copy is static — cwd-glob activation logic stays in the rules file; this copy applies to the entire repository it sits in.

This file is written for cloud review: the managed Code Review service documents that a repo-root REVIEW.md is injected as highest-priority instructions into every review agent ([Code Review docs](https://code.claude.com/docs/en/code-review.md)); consumption by the `/code-review ultra` CLI path is expected but not explicitly documented — verify on the first ultra run in this repo. It is also honored by human reviewers.

## Blocking directives (request changes; do not approve)

1. **PHI containment.** Protected health information must never leave the project's data directory. Flag any PHI written to logs, notebooks, commit messages, test fixtures, cache files, or paths outside the data dir. This is the highest-priority check.
2. **IRB / data-use-agreement constraints.** Any IRB or dataset-use-agreement constraints must be documented at the project root. Analyses touching a governed dataset without that documentation are blocking.
3. **Reporting standard declared.** Every analysis document must state the applicable standard at the top: STROBE (observational), CONSORT (RCT), STARD (diagnostic), TRIPOD (prediction model), PRISMA (systematic review). A missing or wrong declaration is blocking.
4. **DAG before adjustment.** A causal DAG (dagitty or text form) must be declared before adjustment-set selection, and the adjustment set must follow from the back-door criterion (Pearl). Kitchen-sink regression — adjusting for whatever covariates are available — is a blocking defect, as is any adjustment set that includes a collider or a mediator of the declared effect.
5. **E-value sensitivity.** Every primary causal estimate must carry an E-value ([VanderWeele & Ding 2017](https://doi.org/10.7326/M16-2607)). A primary estimate without one is blocking.
6. **Missingness handling.** The MCAR/MAR/MNAR assumption must be declared with supporting evidence. Unless MCAR is supported, the primary analysis must use multiple imputation with the number of imputations m at least the percentage of incomplete cases ([White, Royston & Wood 2011](https://doi.org/10.1002/sim.4067)). Complete-case analysis as the primary analysis without MCAR support is blocking; complete-case is a sensitivity analysis only.

## Advisory directives (comment; do not block on their own)

1. **Standard-checklist completeness.** Once the reporting standard is declared, flag individual checklist items the document does not yet satisfy (e.g., missing flow diagram, unreported eligibility criteria). Escalate to blocking only when the gap hides a validity threat.
2. **DAG plausibility.** Where the DAG is declared but an edge or omitted confounder looks substantively questionable, comment with the specific variable and the literature or domain reasoning a defense would need — do not block on subject-matter disagreement alone.
3. **Sensitivity breadth.** Suggest additional sensitivity analyses (alternative imputation models, alternative adjustment sets consistent with the DAG) where they would materially bound the primary estimate.

Cost note: the managed Code Review service averages $15–25 per review ([Code Review docs](https://code.claude.com/docs/en/code-review.md)); expect `/code-review ultra` runs to be of similar order — reserve cloud review for pre-release gates; default to local `/code-review` plus the audit loop.
