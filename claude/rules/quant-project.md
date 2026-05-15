# Quant-Project Rules

**Apply when cwd matches any of:** `**/signal-decay-auditor/**`, `**/Futures_ML_Prediction/**`, `**/SKIE_Ninja/**`, `**/SKIE-Ninja/**`, `**/SKIE-Ninja*/**`, `**/SKIE-Universe*/**`, `**/*backtest*/**`, `**/*factor*/**`.

If cwd does not match, ignore this section entirely.

## Time-series integrity
- No look-ahead: every feature must be computable at time t using only data available at time t.
- Train/val/test splits are time-ordered and disjoint. Walk-forward CV, never k-fold.
- Returns: always specify log vs arithmetic and the compounding convention.
- Prices: adjust for corporate actions before any return calc.

## Inference
- Standard errors: Newey-West (HAC) with lag selected by [Newey & West 1994](https://doi.org/10.2307/2297912) data-dependent bandwidth or [Andrews 1991](https://doi.org/10.2307/2938229) parametric plug-in.
- Backtests: report bootstrap CI on Sharpe. For single-strategy CIs use [Opdyke 2007](https://doi.org/10.1057/palgrave.jam.2250084) or [Lo 2002](https://doi.org/10.2469/faj.v58.n4.2453) asymptotic; for pairwise strategy comparison use [Ledoit & Wolf 2008](https://doi.org/10.1016/j.jempfin.2008.03.002) studentized time-series bootstrap.
- Multiple testing across strategies: [White 2000](https://doi.org/10.1111/1468-0262.00152) reality check or [Hansen 2005](https://doi.org/10.1198/073500105000000063) SPA.

## Reporting
- Every backtest doc lists: universe, rebalance freq, transaction cost model, survivorship-bias treatment, data vendor + snapshot date.
- Sharpe, Sortino, MaxDD, turnover, capacity estimate.

## Published research
- Any factor, signal, or rule must have a citation or a derivation. No unattributed folklore factors.
