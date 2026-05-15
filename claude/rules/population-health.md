# Population-Health Rules

**Apply when cwd matches any of:** `**/PCP*Crisis/**`, `**/Infectious_Disease*/**`, `**/Ultrasound/**`, `**/epidemiolog*/**`.

If cwd does not match, ignore this section entirely.

## Reporting standards
- Observational: STROBE.
- RCT: CONSORT.
- Diagnostic: STARD.
- Prediction model: TRIPOD.
- Systematic review: PRISMA.

State which applies at the top of the analysis doc.

## Confounding & causal inference
- Declare DAG (dagitty or text) before adjustment-set selection.
- Adjustment set chosen via back-door criterion (Pearl), not kitchen-sink regression.
- Sensitivity: E-value ([VanderWeele & Ding 2017, Ann Intern Med 167:268](https://doi.org/10.7326/M16-2607)) for each primary estimate.

## Ethics / compliance
- PHI must not leave the project's data dir.
- Any IRB or dataset-use-agreement constraints documented at project root.

## Missingness
- Declare MCAR/MAR/MNAR assumption with evidence.
- Primary analysis: multiple imputation with m ≥ percentage of incomplete cases ([White, Royston, Wood 2011, Stat Med 30:377](https://doi.org/10.1002/sim.4067)) unless MCAR is supported.
- Complete-case as sensitivity only.
