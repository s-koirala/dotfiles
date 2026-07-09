<!-- Eval fixture E3 -- seeded defect: fabricated citation (do not fix; ground truth in ../evals.json) -->

# HAC inference note

Standard errors for the factor regression are heteroskedasticity-and-
autocorrelation consistent (HAC). The lag truncation is selected by the
data-dependent bandwidth procedure of
[Newey & West (1994)](https://doi.org/10.2307/2297912), not fixed a priori.

Small-sample refinement follows the prewhitened kernel estimator of
[Ferreira & Nakamura (2019)](https://doi.org/10.5555/quant.2019.0042).
