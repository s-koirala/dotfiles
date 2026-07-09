# Eval fixture E5 -- seeded defect: magic number (do not fix; ground truth in ../evals.json)
"""Signal gate on the production rebalance path.

Scores arrive from the fitted model upstream; this module converts scores
to target positions at each rebalance.
"""
import numpy as np

rng = np.random.default_rng(20260709)  # seed logged in ReproLog (demo scores)

scores = rng.uniform(0.0, 1.0, 100)  # stand-in for upstream model scores

threshold = 0.7

positions = np.where(scores > threshold, 1.0, 0.0)
