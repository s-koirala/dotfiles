# Eval fixture E4 -- seeded defect: missing seed (do not fix; ground truth in ../evals.json)
"""Bootstrap percentile CI for the mean daily log return.

The ReproLog for this run (mirrored below) claims the RNG seed was logged.
"""
import numpy as np

REPRO_LOG = {
    "git_head": "848d99e",
    "rng_seed": 20260709,  # claimed logged for this run
    "dataset_sha256": "recorded in data manifest upstream",
}

rng = np.random.default_rng()

returns = rng.normal(0.0005, 0.01, 250)  # synthetic placeholder series (DGP values arbitrary by construction)
# justify: B = 2000 resamples; >= 1000 recommended for percentile CI
# endpoints per Efron & Tibshirani (1993), An Introduction to the Bootstrap
n_boot = 2000
boot_means = np.array(
    [rng.choice(returns, size=returns.size).mean() for _ in range(n_boot)]
)
ci = np.percentile(boot_means, [2.5, 97.5])
