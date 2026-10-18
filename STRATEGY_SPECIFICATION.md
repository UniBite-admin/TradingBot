# Strategy Specification — BTC/EUR Trend Following

## Status and authority
- **Active research target:** nine-submodel trend-following strategy described in the supplied implementation prompt and attributed there to Zarattini, Pagani, and Barbon, “Catching Crypto Trends,” SSRN 5209907.
- **State:** proposed research contract; data audit and source verification pending. Not yet implemented, tested, validated, or approved for trading.
- **Market:** BTC/EUR spot only.
- **Initial capital:** €100 per independent 30-day window.
- **Execution input required:** validated hourly BTC/EUR OHLCV. `data/kraken/XBTEUR_1440.csv` is present for cross-checking; it does not by itself support hourly execution simulation.
- **Trading permission:** historical research only. No paper/live trading or scaling authorization.

This is the sole authoritative active strategy specification. Box Theory and earlier Experiment A/B, breakout, and zero-cost strategy code/specifications are obsolete for active development. Preserve their historical reports for comparison only and never mix their results with this strategy.

## Research question
Does this deterministic trend-following strategy show robust positive BTC/EUR spot returns after explicit fee, slippage, and execution-delay sensitivity? No positive expectancy or profitability is presumed.

## Proposed strategy mechanics — source verification required
The following mechanics are transcribed from the supplied prompt. They must not be described as an exact replication of the cited paper until the source has been checked.

### Daily inputs and volatility
- Construct UTC daily OHLCV bars from validated hourly data. Use only completed daily bars.
- Daily close-to-close return: `ret_t = close_t / close_(t-1) - 1`.
- Volatility: standard deviation of the last 90 daily returns multiplied by `sqrt(365)`.
- The standard-deviation convention, return-count alignment, and zero/non-finite volatility handling must be explicitly fixed and tested before implementation.

### Nine submodels
Lookbacks: `[5, 10, 20, 30, 60, 90, 150, 250, 360]` daily bars.

For each lookback `n`, using the close series and the current completed daily bar:
- `Up_n = max(close[t-n+1 ... t])`
- `Down_n = min(close[t-n+1 ... t])`
- `Mid_n = (Up_n + Down_n) / 2`
- Each submodel maintains `pos_n ∈ {0, 1}` and a stop.
- If flat and `close_t == Up_n`, enter the long state and set the stop to `Mid_n`.
- If long, compare `close_t` with the old stop first. If `close_t <= stop_n`, exit; otherwise update the stop to `max(old_stop, Mid_n)`.
- Stop must never decrease.
- Do not silently replace exact equality with `>=` or add a tolerance. Define price precision/equality semantics after source/data review.

### Position sizing and rebalance
- Submodel weight: `w_n = pos_n * min(0.25 / sigma_t, CAP)`.
- Initial spot-only cap: `CAP = 1.0`; this is a research assumption, not a live setting.
- Target BTC exposure: mean of the nine submodel weights.
- BTC target notional is based on current portfolio equity multiplied by target exposure. Track EUR cash, BTC quantity, fees, and actual notional separately; do not repeatedly use remaining cash as the target base.
- Rebalance when any submodel enters or exits. If only volatility changes the target, rebalance when relative target deviation exceeds 20%, using a documented denominator and zero-exposure convention.
- No take-profit or additional stop beyond the submodel rules.
- At least 450 prior valid daily bars are required before a valid strategy evaluation.
- Define behavior when volatility is zero, non-finite, or unavailable; do not permit division by zero or accidental exposure.

## Execution and accounting contract
- Signal becomes available only after the daily candle has completed.
- Simulated execution is at the first eligible hourly bar after signal availability, with the configured delay; never fill at the signal close.
- Baseline delay: 0 hours; delay sensitivity: 0, 1, and 4 hours.
- Baseline slicing: one hourly bar (K=1). No additional slicing study in the initial implementation.
- Actual hourly timestamp semantics must be established from the data before mapping a signal to an execution bar.
- Track EUR cash, BTC quantity, trade notional, fees, slippage, equity, exposure, and mark-to-market P&L.
- Apply costs to actual traded notional on both entry and exit. Do not assume fills that the hourly OHLCV data cannot support.
- No portfolio state, position, or trade may bridge a data gap or an independent evaluation-window boundary.

## Cost scenarios
Research assumptions unless verified by dated, relevant evidence:
- Fee per side: 5, 10, and 25 basis points.
- Slippage per side: 1.5, 5, and 10 basis points.
- Run all nine fee/slippage combinations at baseline delay.
- Separately test delays 0, 1, and 4 hours using baseline fee 10 bp/side and slippage 1.5 bp/side.
- Do not add funding costs: this is spot-only research.
- Report assumptions and results separately; no cost model is proof of actual future execution.

## Window experiments
### Main experiment
- 20 non-overlapping 30-day windows, selected reproducibly from eligible dates; save seed, exact UTC boundaries, and selection method.
- Each window starts independently with €100. No holdings, cash, or P&L carry over between windows.
- Require at least 450 valid daily bars of prior history and 30 complete days in the window.
- Define windows as half-open UTC intervals `[start, end)`; ensure exactly 30 complete daily intervals and no duplicated boundary bars.
- WARM: use prior history only to initialize submodel states/stops and determine the target exposure at the boundary. The simulated portfolio starts with €100 cash and no inherited holdings/P&L; execute the initial target inside the window using the approved boundary convention.
- COLD: reset all submodel states/stops to flat at the window start, while allowing prior price history to inform rolling indicators.
- Report final marked-to-market equity and hypothetical fully liquidated equity after exit costs, returns, buy-and-hold, max drawdown, trade/execution counts, costs, and average exposure.
- Define portfolio-level trade attribution before reporting trade win rate/profit factor; do not conflate submodel state flips, rebalance orders, and completed portfolio round trips.

### Additional stability experiment
- 200 overlapping 30-day windows, reported separately.
- Must not replace, rescue, or alter interpretation of the 20-window main experiment.

## Continuous backtest and reporting
After window tests are implemented and verified, run a continuous descriptive BTC/EUR backtest over the validated eligible period. Report yearly returns, CAGR, Sharpe, Sortino, maximum drawdown, exposure, turnover, cost totals, and buy-and-hold comparison where definitions are valid. Trade-level metrics require a documented portfolio trade attribution method.

Every report must record strategy version, full configuration, source identity/hash, exact UTC bounds, data QA findings, window seed/boundaries, cost assumptions, and known limitations. Reports must distinguish gross from net results.

## Pre-registered research criteria — provisional assumptions
The supplied prompt proposes the following criteria; they are not profitability claims or trading authorization:
- Continuous test: net Sharpe >= 0.8 at 10 bp fee per side; max drawdown <= 35%; no collapse from 5 to 25 bp fees; average gross profit per defined completed portfolio trade >= 3x round-trip cost.
- WARM 30-day windows: mean net return > 0; at least 50% positive windows; mean in-window max drawdown lower than buy-and-hold.
- Freeze these criteria before observing results. Do not tune on the final test set or weaken criteria after seeing results.
- Any multi-asset expansion requires a separate approved scope and a selection rule frozen before evaluating those assets.

## Data contract and blockers
- Inspect actual BTC/EUR files before assuming path, schema, start/end date, timestamp units, timezone, or bar-open/bar-close semantics.
- Hourly data is required for the proposed execution simulation. `data/kraken/XBTEUR_1440.csv` is an additional cross-check source, not an automatic replacement.
- Resample hourly candles to UTC daily bars with a documented convention. Only complete daily intervals with all expected hourly observations in the same contiguous segment are eligible.
- Compare resampled daily data with the 24-hour file only when timestamps and daily boundaries are semantically comparable.
- Detect and report gaps, duplicates, invalid OHLCV, non-finite values, zero-volume bars, and suspicious price jumps. Do not silently delete, deduplicate, forward-fill, synthesize, or repair rows.
- Gaps split continuity. No signal or state crosses a gap.
- The approximate February 2025 end date mentioned in the supplied prompt is unconfirmed; derive actual coverage from the repository files after inspecting their contents.
- Do not claim data adequacy or representativeness based on row count alone.

## Acceptance gates
1. Verify the cited source and settle source-dependent mechanics.
2. Inspect and validate `data/kraken/XBTEUR_60.csv` and `data/kraken/XBTEUR_1440.csv`.
3. Freeze timestamp, daily-bar, gap, warm-up, price equality, volatility, window, accounting, and execution semantics.
4. Implement and test the deterministic strategy state machine.
5. Implement and test portfolio accounting, execution simulation, and costs.
6. Generate reproducible reports and inspect their contents before any conclusion.
7. Paper trading, live orders, and scaling remain blocked without separate explicit authorization.
