# Eval fixture E6 -- seeded defect: off-by-one split overlap (do not fix; ground truth in ../evals.json)
"""Time-ordered train/test split for a daily-strategy backtest (log returns)."""
import numpy as np

rng = np.random.default_rng(20260709)  # seed logged in ReproLog

n = 1000
log_ret = rng.normal(0.0, 0.01, n)

# Hold out the final 250 observations (~1 trading year) as the test window;
# the split is time-ordered per walk-forward convention.
t = n - 250

train = log_ret[: t + 1]
test = log_ret[t:]
