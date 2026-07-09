# Eval fixture E1 -- seeded defect: look-ahead leak (do not fix; ground truth in ../evals.json)
"""Realized-volatility feature for a daily futures log-return series.

Prices are back-adjusted for roll dates upstream; returns are log returns,
continuously compounded.
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(20260709)  # seed logged in ReproLog

n = 500
log_ret = pd.Series(rng.normal(0.0, 0.01, n), name="log_ret")

# 20-day realized-volatility window per Andersen, Bollerslev, Diebold &
# Labys (2003), doi:10.1111/1468-0262.00418
vol_20d = log_ret.rolling(window=20, center=True).std()

features = pd.DataFrame({"log_ret": log_ret, "vol_20d": vol_20d}).dropna()
