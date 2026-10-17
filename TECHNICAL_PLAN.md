# Technical Plan — BTC/EUR Trend Strategy Research

## Status
- **Current phase:** contract and data audit.
- **Active target:** BTC/EUR spot trend-following strategy in `STRATEGY_SPECIFICATION.md`.
- **Strategy engine/backtest:** not yet implemented under this specification.
- **Input data:** user confirms 24-hour BTC/EUR candles are available and will upload them. Required hourly source, exact paths, schema, timestamp semantics, and coverage remain to be verified.
- **Paper/live/scaling:** not authorized.
- **Previous Box Theory:** obsolete for active development; preserve historical reports/code as comparison evidence only.

## Proposed runtime path
```text
BTC/EUR hourly OHLCV
  -> source/schema/time validation
  -> gap-aware contiguous segments
  -> complete UTC daily bars
  -> compare against uploaded 24-hour candles
  -> deterministic daily strategy state machine
  -> target exposure
  -> hourly execution simulation
  -> EUR/BTC portfolio accounting and explicit costs
  -> reproducible window and continuous reports
```

## Phase 0 — repository and data audit
1. Inspect the current repository and relevant existing code/tests before selecting implementation locations.
2. Inspect actual files, not filenames or prior assumptions.
3. Record path, size, schema, row count, first/last timestamp, timestamp units, timezone, bar-open/bar-close convention, ordering, duplicates, gaps, invalid OHLCV, zero volume, and suspicious moves.
4. Do not silently deduplicate, forward-fill, synthesize candles, or repair data.
5. Resample only complete hourly groups to UTC daily bars; gap boundaries split continuity.
6. Compare the resulting daily candles with the user's 24-hour data when boundaries are comparable. Report mismatches; do not silently replace the hourly-resampled series.
7. Do not implement strategy logic until the data contract and key ambiguities are recorded.

## Phase 1 — deterministic strategy core
Implement the nine submodel states/stops, volatility calculation, target exposure, and rebalance decision as pure deterministic logic. Add focused tests for:
- each lookback and warm-up;
- entry condition and exact equality semantics;
- stop check using old stop before ratchet;
- stop monotonicity;
- volatility sizing, cap, zero/non-finite volatility;
- rebalance triggers and zero-exposure denominator;
- state resets at data gaps and experiment boundaries;
- no look-ahead from incomplete daily candles.

## Phase 2 — portfolio backtest
Implement EUR cash, BTC quantity, target exposure, hourly execution delay, fee/slippage calculations, mark-to-market equity, and separate WARM/COLD window initialization. Keep strategy, portfolio accounting, execution simulation, costs, and analytics logically distinct while reusing the existing repository architecture where practical.

Required verification:
- Hand-calculated accounting examples.
- Costs applied to actual traded notional on each side.
- No fill at the signal close.
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
- The 24-hour file is pending upload/inspection.
- Hourly data and exact coverage have not yet been verified in this phase.
- Fee and slippage values are research scenarios unless backed by relevant dated evidence.
- Hourly OHLCV cannot establish exact intrabar path, order-book depth, or actual fills.
- Paper trading, live orders, and scaling remain blocked.
