# Eval fixture C1 -- clean control: no seeded defect (ground truth in ../evals.json)
"""Walk-forward evaluation of a lagged momentum feature (log returns).

Prices are back-adjusted for corporate actions upstream; returns are log
returns, continuously compounded.
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(20260709)  # seed logged in ReproLog

n = 1000  # justify: >= 126-day formation + 250-day holdout + warm-up margin
log_ret = pd.Series(rng.normal(0.0, 0.01, n), name="log_ret")

# 126-day (~6-month, J=6) trailing momentum with a 5-day skip between
# formation and evaluation, per the Jegadeesh & Titman (1993) J/K convention
# (J in {3,6,9,12} months, one-week skip), doi:10.1111/j.1540-6261.1993.tb04702.x.
# The shift also guarantees the feature at t uses only data through t-6
# (no look-ahead).
momentum = log_ret.rolling(window=126).sum().shift(6)

# Drop the rolling warm-up so downstream estimators see no NaN rows.
valid = momentum.notna()
momentum, log_ret = momentum[valid], log_ret[valid]

# Time-ordered, disjoint split: final 250 obs held out.
# justify: 250 obs (~1 trading year at 252 obs/yr) meets the large-sample
# regime for asymptotic Sharpe CIs per Lo 2002, doi:10.2469/faj.v58.n4.2453.
t = len(momentum) - 250
train_x, test_x = momentum[:t], momentum[t:]
train_y, test_y = log_ret[:t], log_ret[t:]
assert train_x.notna().all() and test_x.notna().all()
assert train_x.index.max() < test_x.index.min()  # disjoint, time-ordered
