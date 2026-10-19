# Technical Plan — BTC/EUR Trend Strategy Research

## Status
- **Current phase:** deterministic strategy core and initial portfolio-accounting primitives are implemented on the research branch. Core tests passed locally (17/17; full suite 61/61) before the latest portfolio files were added. Portfolio tests and the updated full suite are pending local execution.
- **Active target:** BTC/EUR spot trend-following strategy in `STRATEGY_SPECIFICATION.md`.
- **Strategy core:** implemented and locally verified. **Portfolio accounting:** initial buy/sell, fee, slippage, and cash-constraint primitives implemented; focused tests added but not yet locally verified. **Hourly execution simulator and window backtest:** not implemented.
- **Input data:** the 1h and 24h files have been inspected on `main`; see the observed audit recorded in `STRATEGY_SPECIFICATION.md`. The 5m/4h/12h files have not been inspected for this strategy and are not inputs to its initial hourly/daily path.
- **Paper/live/scaling:** not authorized.
- **Previous Box Theory and earlier strategies:** obsolete strategy code/tests are removed from `main`; preserve historical reports/manifests as comparison evidence only.

## Approved human decisions
- **Volatility (approved 2026-10-19):** sample standard deviation (`ddof=1`) of the trailing 90 close-to-close daily returns, annualized by `sqrt(365)`. A 90-return window requires 91 valid closes within the same daily segment.
- **Invalid volatility (approved 2026-10-19):** target exposure zero for zero/non-finite/unavailable volatility; any existing BTC holding must be reduced through normal execution/accounting with costs, not erased.
- **Signal/execution boundary (approved 2026-10-19):** after the daily interval ends, select the first eligible hourly candle whose interval starts at or after signal availability plus configured delay; use its open as simulated fill reference, never the daily close.
- **Volatility-only rebalance (approved 2026-10-19):** compare target BTC quantity against current BTC quantity at the same decision price and rebalance only if `abs(target_btc_qty - current_btc_qty) / abs(current_btc_qty) > 0.20`. If current BTC quantity is zero, this relative-deviation rule is not applied; signal-driven submodel entry/exit events remain independent rebalance triggers.
- **Primary fee assumption:** 25 bp per side, with slippage separate. Preserve the 5/10/25 bp fee grid. Delay sensitivity uses 25 bp fee per side and 1.5 bp slippage per side. The 10 bp Sharpe acceptance comparison is separate from the primary conservative scenario.

## Proposed runtime path
```text
BTC/EUR hourly OHLCV
  -> source/schema/time validation
  -> gap-aware contiguous segments
  -> complete UTC daily bars
  -> compare against `data/kraken/XBTEUR_1440.csv`
  -> deterministic daily strategy state machine
  -> target exposure
  -> hourly execution simulation
  -> EUR/BTC portfolio accounting and explicit costs
  -> reproducible window and continuous reports
```

## Phase 0 — repository and data audit
1. **Completed content review:** inspect actual `XBTEUR_60.csv` and `XBTEUR_1440.csv` blobs, including schema, timestamp alignment, chronology, duplicates, gaps, and OHLCV relationships.
2. **Completed cross-check:** 4,637 complete UTC daily bars aggregated from hourly rows match the 24h file exactly for OHLC, volume, and trade count.
3. **Implemented and locally tested on research branch:** isolated hourly reader with strict seven-column mapping and gap-aware UTC daily aggregation. Do not reuse the legacy five-minute reader, which maps trade count into volume for seven-column input.
4. Do not silently deduplicate, forward-fill, synthesize candles, or repair data. Incomplete UTC days are excluded.
5. Source-version limitation and approved volatility/execution conventions are documented. Remaining edge cases must be resolved or explicitly blocked before portfolio backtest conclusions.

## Phase 1 — deterministic strategy core
**Initial implementation added on the research branch:** nine submodel states/stops, sample-volatility calculation, target exposure, and the strict rebalance threshold as pure deterministic logic. Focused tests have been added; execution and inspection are still required. Add focused tests for:
- each lookback and warm-up;
- entry condition and exact equality semantics;
- stop check using old stop before ratchet;
- stop monotonicity;
- volatility sizing, cap, zero/non-finite volatility and target-zero behavior for any existing holding;
- approved 20% rebalance threshold, strict `> 20%` comparison, and zero-current-position behavior;
- state resets at data gaps and experiment boundaries;
- no look-ahead from incomplete daily candles.

## Phase 2 — portfolio backtest
**In progress:** `tools/trend_following/portfolio.py` implements explicit EUR/BTC accounting, adverse slippage, fees on fill notional, fractional BTC, and cash-limited buys. `tests/test_trend_following_portfolio.py` adds hand-calculated examples; local execution is pending. The hourly execution simulator, reproducible WARM/COLD window runner, and reporting are not implemented. Keep strategy, portfolio accounting, execution simulation, costs, and analytics logically distinct while reusing the existing repository architecture where practical.

Required verification:
- Hand-calculated accounting examples pass locally (pending for the newly added portfolio tests).
- Costs applied to actual traded notional on each side.
- No fill at the signal close; zero-delay fill reference is the open of the first hourly candle starting at/after signal availability.
- No state, position, or P&L carried across independent windows or gaps.
- Exact 30-day half-open windows and saved random seed/boundaries.
- Independent fully-liquidated final-equity calculation with exit costs.

## Phase 3 — reproducible experiments
- Main: 20 non-overlapping 30-day windows.
- Additional: 200 overlapping 30-day windows, separate report.
- Cost grid: 3 fee levels x 3 slippage levels at baseline delay.
- Delay sensitivity: 0/1/4 hours at baseline costs.
- Continuous descriptive backtest after window behavior is verified.
- Reports must contain configuration, source hashes/bounds, QA findings, exact window boundaries, assumptions, results, and limitations.

## Verification commands
Commands must be adjusted after inspecting the actual repository and dependencies. Do not assume a test path or report runner until verified. Record commands and actual outputs. GitHub-hosted file edits do not execute Python tests or verify local datasets.

## Acceptance criteria
- Data schema, timestamps, and UTC resampling are verified against actual files.
- Strategy behavior is specified and covered by focused tests.
- Portfolio balances and cost arithmetic match independent hand calculations.
- No look-ahead, gap bridging, silent repair, or boundary-crossing state.
- Reports are reproducible and inspected.
- Results are described as historical research only; no profitability or live-trading claim without sufficient evidence and explicit authorization.

## Known limitations
- The 24-hour file is present; content-level inspection is pending.
- The hourly file is present; its content, semantics, and exact coverage have not yet been verified in this phase.
- Fee and slippage values are research scenarios unless backed by relevant dated evidence.
- Hourly OHLCV cannot establish exact intrabar path, order-book depth, or actual fills.
- Paper trading, live orders, and scaling remain blocked.
