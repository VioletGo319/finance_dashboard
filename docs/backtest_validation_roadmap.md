# Backtest validation roadmap — evidence gates

**Current state (2026-11-09): RESEARCH-ONLY, NOT VALIDATED INVESTMENT ALPHA.** The website reports price-only 1Y/3Y/5Y diagnostics for a *current* 40-stock supplier universe. These are useful for investigation but do not prove deployable alpha. The website explicitly shows the three unresolved gates below.

## Gate A — point-in-time securities universe

- Obtain daily historical membership including delisted and subsequently acquired names. Differentiate exchange listings, IPO effective dates, ticker changes, spin-offs and supplier relationship evidence dates.
- Build security-master records keyed by immutable identifiers (CIK, PERMNO if licensed, exchange identifiers), rather than treating today's 40 ticker symbols as an unbiased historical sample.
- Each historical portfolio formation date must contain only securities available on that date. Record missing/late-listed positions and survivorship exclusions; do not interpolate hypothetical pre-IPO stock prices.
- Audit the difference between this historical pool and today's 40-stock illustrative supplier subset. Until reconstructed, `historical_universe.status=PENDING`.

## Gate B — split/dividend/total-return price audit

- Cross-check vendor OHLC with corporate action calendars, share splits, cash dividends and any extraordinary distributions; check ADR adjustment units and currency conversions.
- Calculate and compare both price-return and total-return series using an independently validated adjusted-price/source basis; declare the version and exact provider.
- Flag large one-session returns and discontinuities for review, **not** automatic smoothing. Do not treat raw close and adjusted close as interchangeable.
- Verify QQQ is matched on the same return convention (including dividend reinvestment where total return is claimed).
- Until validation is complete, `corporate_actions.status=PENDING`.

## Gate C — walk-forward with parameters frozen

- Create chronological folds and a development/validation/test split. For each fold, estimate factor thresholds, temperature, transaction-cost assumptions and any risk parameters only on preceding dates.
- Freeze them for the future test period; generate signals using only previous-close information, with explicit next-close fills and nonzero modeled transaction costs.
- Publish per-fold CAGR, Sharpe, volatility, max drawdown, turnover, information ratio vs QQQ, and paired bootstrap confidence intervals on excess return.
- Log overlapping test exposure, listing eligibility, unobserved prices and stale-fundamental availability. Separate model selection from held-out reporting.
- Benchmark simple equal-weight/QQQ and identical exposure-matched QQQ strategies; report fail cases, not only winning windows.
- Until an auditable fold manifest and held-out runs are available, `walk_forward.status=PENDING`.

## Publication policy

Do not promote historical return numbers to validated strategy results until all three gates have programmatically and manually auditable evidence. The existing dashboard label must remain **Exploratory price-only research diagnostic**. The autonomous paper ledger is separate, uses simulated next-close fills, and does not inherit historical returns.

All daily outputs under `data/quant/latest.json` must include the gate statuses. The CI and daily pipeline must reject mismatched Overview versus Quant Supply Alpha snapshots.
