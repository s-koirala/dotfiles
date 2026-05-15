---
name: statistical-analysis
description: Rigorous statistical analysis workflow — assumption checking, method selection, inference, diagnostics. Invoke for any hypothesis test, estimation, or inference task.
---

# Statistical Analysis

## When to invoke
User asks for a hypothesis test, confidence interval, effect size, power analysis, regression fit, time-series model, change detection, or any inference over data. Also invoke when a notebook is being built around an analytical question.

## Execution sequence

### 1. Frame the question
Write one sentence: estimand, target population, unit of analysis, comparison. If the user's ask is ambiguous on any of these, ask once.

### 2. Inspect the data (before choosing methods)
- Types, missingness pattern (MCAR/MAR/MNAR evidence), sample size per cell.
- Distribution: QQ, KS vs candidate, skew/kurtosis.
- Dependence: autocorrelation (time series), ICC (clustered), VIF (regression covariates).
- Record findings in a `data_profile_{YYYY-MM-DD}.md` under `docs/`.

### 3. Select method from assumption fit, not convention
Map verified assumptions → method. Examples:
- Non-normal + small n → bootstrap CI or exact permutation test, not t-test.
- Autocorrelation → HAC/Newey-West SE or block bootstrap, not iid SE.
- Heteroskedastic → HC3 for small n (MacKinnon & White 1985), not HC0.
- Multiple comparisons → Benjamini-Hochberg FDR unless family-wise control is required (then Holm).
- Changepoint → PELT ([Killick, Fearnhead, Eckley 2012, JASA 107:1590](https://arxiv.org/abs/1101.1438)) with penalty selected via CROPS ([Haynes, Eckley, Fearnhead 2017, JCGS 26:134](https://doi.org/10.1080/10618600.2015.1116445)) or BIC-bootstrap.

Cite the paper/standard that justifies the choice. No convention-driven defaults.

### 4. Tune every parameter empirically
- Regularization, lag order, window size, penalty, bandwidth: CV, AIC/BIC, or bootstrap-stability selection.
- Document grid/prior and the search outcome in an inline `# cv:` or `# justify:` comment on the assignment line. Hook will block otherwise.

### 5. Fit + inference
- Report point estimate, SE, CI (bootstrap preferred if assumptions doubtful), effect size with interpretable units.
- For ML: train/val/test split pre-declared; nested CV if tuning; held-out metrics only.

### 6. Diagnostics
- Residuals: normality, homoskedasticity, autocorrelation (Ljung-Box), influence (Cook's D, DFBETAS).
- Sensitivity: re-fit dropping top leverage points; report delta.
- Specification: alternative functional forms, different lag order, robust to link function.

### 7. Reporting
- Follow STROBE (observational), CONSORT (trial), TRIPOD (prediction model) where relevant.
- State every assumption that was tested and its outcome.
- Pre-register if inference is primary; add protocol hash to the README.

## Hand-off
After completion, invoke `audit-remediate-loop` with `target=statistical-analysis-output` unless the caller is already inside that loop.

## References
- MacKinnon & White (1985) *J. Econometrics* — HC estimator variants.
- Killick, Fearnhead, Eckley (2012) *JASA* — PELT.
- Benjamini & Hochberg (1995) *JRSS-B* — FDR.
- Efron & Tibshirani (1993) — bootstrap.
- Giacomini & White (2006) *Econometrica* — conditional forecast comparison.
