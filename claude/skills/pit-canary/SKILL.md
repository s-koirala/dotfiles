---
name: pit-canary
description: Point-in-time leakage canary for backtest pipelines. Inject a known future-knowing feature; if it does NOT dominate the unmolested feature set, the pipeline already has a leak. Invoked by quant-auditor when reviewing quant backtests; standalone for the user via /audit-loop. Cwd-scoped to quant projects.
---

# pit-canary

## When to invoke

Before any walk-forward run on time-series data, OR as part of `quant-auditor` review of a completed backtest. Quant-project cwd only (matches `rules/quant-project.md` globs).

**Hand-off:** invoked by existing `quant-auditor`, NOT a new agent. The plan §C.2 #20 + audit finding F-1-11 explicitly forbade adding a leakage-auditor agent — `quant-auditor` already covers method-fidelity / leakage at the rule level.

## Canary pattern

Per López de Prado 2018 *Advances in Financial Machine Learning* §7. Three canaries port from SKIE-Universe `src/skie_ninja/backtest/leak_canaries.py`:

1. **Future-return-feature canary.** Inject the (t+1) realized return as a feature. Refit. If the future-feature does NOT achieve dominant feature importance (permutation importance > 0.5 of total), the pipeline has a leak — some pre-existing feature already encodes the future return.
2. **Label-horizon-exceeds-purge canary.** Verify `label_horizon < purge` in the splitter. If `label_horizon >= purge`, training-set labels reach into validation-set features → information leak.
3. **HMM-fit-on-test canary** (if HMM regime layer is present). Verify the regime model was fit on TRAIN only, never on TEST. If the regime indicator improves OOS performance when fit on test, the regime layer is leaking.

## Test statistic

For canary 1 (future-return-feature):
- Permutation test, **n_perm = 1000**  # justify: SKIE-Universe `leak_canaries.py` default; matches Politis-Romano stationary bootstrap reference resample size
- p-value threshold: **p < 0.01**  # justify: SKIE-Universe default; conservative since false negative = silent leak, false positive = re-investigate (cheap)
- Statistic: permutation-test feature importance ratio = `imp(future_feature) / sum(imp(all_features))`

Canary FAILS (i.e., LEAK DETECTED) if the future-feature does NOT dominate at p < 0.01 — meaning the unmolested pipeline already encodes the future return through some other channel.

## Procedure

1. **Locate the project's backtest config and feature set** (look for `config/hypotheses/<HID>.yaml` per SKIE-Universe convention).
2. **Run baseline backtest** without injecting the canary.
3. **Inject canary 1** (future-return feature), refit, run baseline.
4. **Compute permutation importance** for the injected feature.
5. **Compute permutation p-value** (n_perm=1000) under the null that the injected feature is no more important than any randomly-permuted feature.
6. **Verify canaries 2 and 3** by inspecting the splitter config and HMM fit log.
7. **Write report** to `research/01_hypothesis_register/<HID>/pit_canary_{YYYY-MM-DD}.md`:
   ```markdown
   ---
   title: PIT canary report — <HID>
   date: <YYYY-MM-DD>
   hypothesis_id: <HID>
   type: pit_canary
   verdict: <PASS | FAIL>
   ---

   # PIT canary — <HID>

   ## Canary 1: future-return-feature
   - Injected feature: `return_t_plus_1`
   - Permutation importance ratio: <value>
   - Permutation p-value (n_perm=1000): <value>
   - Verdict: <PASS (p < 0.01) | FAIL (p >= 0.01 — leak detected)>

   ## Canary 2: label-horizon vs purge
   - `label_horizon`: <value>
   - `purge`: <value>
   - Verdict: <PASS (purge > label_horizon) | FAIL>

   ## Canary 3: HMM-fit-on-test (if applicable)
   - Fit window: <value>
   - Test window: <value>
   - Verdict: <PASS | FAIL | N/A>

   ## Overall: <PASS | FAIL>
   ```
8. **Emit R1-A ReproLog** with `phase=validation`, `hypothesis_id=<HID>`, `rng_seed=<seed used for permutation>`, `config_resolved_sha256=<pit_canary report SHA>`.
9. **If any canary FAILS:** raise to `audit-remediate-loop` as a `critical` finding. Quant-auditor blocks the run; user must fix the leak before proceeding.

## Necessary, not sufficient

PIT canaries detect *some* forms of look-ahead bias but cannot prove the pipeline is leak-free. Pair with:
- `quant-auditor` review of feature lag operators
- Code review of any feature using `pd.shift` or `rolling`
- Visual inspection of feature/label timestamp distributions

## Hand-off

- Invoked by [`quant-auditor`](../../agents/quant-auditor.md) when reviewing quant backtests.
- Reports emit ReproLog via [emit-repro-log](../emit-repro-log/SKILL.md).
- Failures escalate to [`audit-remediate-loop`](../audit-remediate-loop/SKILL.md) as critical findings.

## References

- López de Prado, M. (2018). *Advances in Financial Machine Learning*. Wiley. ISBN 978-1119482086. §7 "Cross-validation in finance"; introduces purge + embargo and discusses look-ahead bias.
- SKIE-Universe `src/skie_ninja/backtest/leak_canaries.py` — port source; threshold defaults verified via `gh api` 2026-05-15.
- Politis, D. N., & Romano, J. P. (1994). "The Stationary Bootstrap." *J Am Stat Assoc* 89(428):1303. https://doi.org/10.1080/01621459.1994.10476870 — n_perm=1000 default matches stationary-bootstrap canonical resample size.
