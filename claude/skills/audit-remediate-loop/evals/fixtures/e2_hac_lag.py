# Eval fixture E2 -- seeded defect: wrong HAC lag justification (do not fix; ground truth in ../evals.json)
"""Newey-West (HAC) standard errors for a factor exposure regression."""
import numpy as np
import statsmodels.api as sm

rng = np.random.default_rng(20260709)  # seed logged in ReproLog

n = 750
beta = 0.5  # simulation DGP coefficient (ground truth by construction, not tuned)
x = rng.normal(size=n)
y = beta * x + rng.normal(size=n)

X = sm.add_constant(x)
# justify: lag selected by the data-dependent bandwidth of Newey & West
# (1994), doi:10.2307/2297912
fit = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": 4})
print(fit.bse)
