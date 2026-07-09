<!-- Eval fixture C2 -- clean control: no seeded defect (ground truth in ../evals.json) -->

# Sensitivity and missing-data note (STROBE observational analysis)

Unmeasured-confounding sensitivity is reported as the E-value of
[VanderWeele & Ding (2017)](https://doi.org/10.7326/M16-2607) for each
primary estimate and for the confidence-interval limit closer to the null.

Missing covariate data are assumed missing at random (MAR), supported by
observed-data comparisons across missingness patterns. The primary analysis
uses multiple imputation by chained equations, with the number of
imputations m at least the percentage of incomplete cases, per
[White, Royston & Wood (2011)](https://doi.org/10.1002/sim.4067).
Complete-case results are reported as sensitivity analysis only.
