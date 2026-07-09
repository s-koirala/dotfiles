# REVIEW.md — quant project review directives

Source of record: this file encodes [rules/quant-project.md](https://github.com/s-koirala/dotfiles/blob/main/claude/rules/quant-project.md) from these dotfiles. The per-repo copy is static — cwd-glob activation logic stays in the rules file; this copy applies to the entire repository it sits in.

This file is written for cloud review: the managed Code Review service documents that a repo-root REVIEW.md is injected as highest-priority instructions into every review agent ([Code Review docs](https://code.claude.com/docs/en/code-review.md)); consumption by the `/code-review ultra` CLI path is expected but not explicitly documented — verify on the first ultra run in this repo. It is also honored by human reviewers.

## Blocking directives (request changes; do not approve)

1. **No look-ahead.** Every feature must be computable at time t using only data available at or before t. Flag any centered/forward-looking window, full-sample normalization or scaling fit on data that includes the evaluation period, target leakage through joins, or use of revised/restated data where point-in-time data existed.
2. **Split integrity.** Train/validation/test splits must be time-ordered and disjoint. Walk-forward cross-validation only — k-fold (shuffled or otherwise) on time series is a blocking defect. Flag any split where the boundary observation appears in more than one set.
3. **Corporate-action adjustment.** Prices must be adjusted for corporate actions (splits, dividends, spin-offs) before any return calculation. Unadjusted-price returns are a blocking defect.
4. **Return convention declared.** Every return series must specify log vs arithmetic and the compounding convention wherever results are computed or reported. Undeclared convention in reported results is blocking.
5. **HAC standard errors.** Standard errors on serially correlated data must be Newey-West (HAC) with the lag selected by the [Newey & West 1994](https://doi.org/10.2307/2297912) data-dependent bandwidth or the [Andrews 1991](https://doi.org/10.2307/2938229) parametric plug-in. A hardcoded or unjustified lag choice is blocking.
6. **Sharpe confidence intervals.** Backtests must report a bootstrap CI on Sharpe. Single-strategy CIs: [Opdyke 2007](https://doi.org/10.1057/palgrave.jam.2250084) or [Lo 2002](https://doi.org/10.2469/faj.v58.n4.2453) asymptotic. Pairwise strategy comparison: [Ledoit & Wolf 2008](https://doi.org/10.1016/j.jempfin.2008.03.002) studentized time-series bootstrap. A point-estimate Sharpe with no CI, or the wrong CI method for the comparison type, is blocking.
7. **Multiple testing across strategies.** Any inference over a family of strategies or signals must apply the [White 2000](https://doi.org/10.1111/1468-0262.00152) reality check or [Hansen 2005](https://doi.org/10.1198/073500105000000063) SPA. Reporting the best of N tested strategies without family-wise control is blocking.
8. **Citation or derivation.** Every factor, signal, or trading rule must carry a citation to published research or an in-repo derivation. Unattributed folklore factors are blocking.

## Advisory directives (comment; do not block on their own)

1. **Backtest reporting checklist.** Every backtest document must list: universe, rebalance frequency, transaction cost model, survivorship-bias treatment, and data vendor + snapshot date; and must report Sharpe, Sortino, MaxDD, turnover, and a capacity estimate. Flag each missing item. Escalate to blocking only when an omission could change the conclusion (e.g., no transaction cost model on a high-turnover strategy).
2. **Convention ambiguity in intermediate code.** Log-vs-arithmetic ambiguity in intermediate computations that provably does not reach reported results: comment with the exact location and suggest an explicit declaration.
3. **Leak-prone patterns.** Patterns that often precede look-ahead (resampling before splitting, groupby-then-shift ordering, unpinned data snapshots): comment even when no concrete leak is demonstrated, and say what evidence would confirm or clear it.

Cost note: the managed Code Review service averages $15–25 per review ([Code Review docs](https://code.claude.com/docs/en/code-review.md)); expect `/code-review ultra` runs to be of similar order — reserve cloud review for pre-release gates; default to local `/code-review` plus the audit loop.
