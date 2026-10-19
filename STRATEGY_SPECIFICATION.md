# Strategy Specification — BTC/EUR Trend Following

## Status and authority
- **Active research target:** nine-submodel trend-following strategy described in the supplied implementation prompt and attributed there to Zarattini, Pagani, and Barbon, “Catching Crypto Trends,” SSRN 5209907.
- **State:** proposed research contract; data audit and source verification pending. Not yet implemented, tested, validated, or approved for trading.
- **Market:** BTC/EUR spot only.
- **Initial capital:** €100 per independent 30-day window.
- **Execution input required:** validated hourly BTC/EUR OHLCV. `data/kraken/XBTEUR_1440.csv` is present for cross-checking; it does not by itself support hourly execution simulation.
- **Trading permission:** historical research only. No paper/live trading or scaling authorization.

This is the sole authoritative active strategy specification. Box Theory and earlier Experiment A/B, breakout, and zero-cost strategy implementations/tests are obsolete and must not remain in active source code. Obsolete Box Theory implementation and tests have been removed from `main`; historical reports/manifests are retained for comparison only and must never be mixed with this strategy's results.

## Approved human decisions
- **Volatility convention (approved 2026-10-19):** use sample standard deviation (`ddof=1`) over the trailing 90 daily close-to-close returns, annualized by `sqrt(365)`. This is an explicit implementation convention; exact replication of the latest SSRN revision is not established.
- **Invalid volatility behavior (approved 2026-10-19):** when volatility is zero, non-finite, or unavailable, set target BTC exposure to zero and do not initiate/increase a BTC position. If BTC is already held, the portfolio layer must represent the target-zero rebalance and its costs explicitly; do not silently discard the holding.
- **Signal/execution boundary (approved 2026-10-19):** a daily signal is available only after the completed UTC daily candle ends. At zero configured delay, the first eligible hourly candle is the candle whose interval starts at or after that signal-availability timestamp; the simulated fill reference is that hourly candle's open, not the daily close. Delay sensitivities shift eligibility by the configured number of hours. This is a simulation convention, not a guarantee of a real fill.
- **Volatility-only rebalance threshold (approved 2026-10-19):** compare target BTC quantity with the current BTC quantity at the same decision price. Rebalance only when `abs(target_btc_qty - current_btc_qty) / abs(current_btc_qty) > 0.20`. Because the same BTC price applies to both quantities, this is equivalent to comparing target and current BTC notional values. The comparison is strictly greater than 20%, not greater-than-or-equal.
- **Zero current BTC position:** the relative-deviation formula is undefined when current BTC quantity is zero. Do not use this rule in that case; submodel entry/exit events remain separate rebalance triggers as specified above.
- **Primary fee assumption:** use 25 basis points per side as the primary conservative fee scenario, with slippage modeled separately. Retain the 5/10/25 bp fee grid. Delay sensitivity must use 25 bp fee per side and 1.5 bp slippage per side; the pre-registered Sharpe criterion at 10 bp remains a separate comparison and must not be mistaken for the primary cost case.

## Research question
Does this deterministic trend-following strategy show robust positive BTC/EUR spot returns after explicit fee, slippage, and execution-delay sensitivity? No positive expectancy or profitability is presumed.

## Source review and version limitation
- The SSRN record identifies the paper as last revised on 2025-10-02: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5209907.
- The authors-hosted 38-page PDF available at https://concretumgroup.com/wp-content/uploads/2026/02/Catching-Crypto-Trends.pdf labels itself “This Version: April 9, 2025”. The accessible PDF therefore does not establish the exact contents of the latest SSRN revision. Treat the source review as partial and do not claim exact replication of the October 2025 version.
- The accessible PDF supports the core close-based Donchian channels, entry when close equals the upper boundary, initial stop at the midpoint, non-decreasing midpoint trailing stop, 90-day annualized volatility targeting at 25%, nine lookbacks, and the 20% threshold applied only to volatility-targeting rebalances. It describes the threshold as a difference between current and target allocation exceeding 20%, but does not specify the denominator in the text reviewed. The current-position-relative denominator recorded below is the explicit human-approved research interpretation, not a verbatim source formula.

## Proposed strategy mechanics — source verification partial
The following mechanics are transcribed from the supplied prompt and checked against the accessible April 9, 2025 PDF where noted. They must not be described as an exact replication of the latest SSRN revision until that revision is verified.

### Daily inputs and volatility
- Construct UTC daily OHLCV bars from validated hourly data. Use only completed daily bars.
- Daily close-to-close return: `ret_t = close_t / close_(t-1) - 1`.
- Volatility: sample standard deviation (`ddof=1`) of the trailing 90 close-to-close daily returns multiplied by `sqrt(365)`. A 90-return window requires 91 valid closes within the same contiguous daily segment.
- Use sample standard deviation (`ddof=1`) over the trailing 90 close-to-close daily returns and annualize by `sqrt(365)`. A valid 90-return window requires 91 valid closes within the same contiguous daily segment. If volatility is zero, non-finite, or unavailable, target BTC exposure is zero; do not initiate/increase BTC exposure, and route any existing holding toward target zero through normal portfolio execution and cost accounting.

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
- For zero, non-finite, or unavailable volatility, target BTC exposure is zero. An existing BTC holding is not erased from accounting; it must be reduced toward zero through normal execution with fees and slippage. No division by zero or accidental exposure is permitted.

## Execution and accounting contract
- Signal becomes available only after the UTC daily candle has completed, at its interval-end timestamp.
- With zero configured delay, the first eligible hourly candle has `interval_start >= signal_available_at`; use that candle's open as the simulated fill reference. For positive delays, apply the configured delay before selecting the first eligible hourly candle.
- Never fill at the signal close. This is a reproducible OHLCV simulation convention, not evidence that a live order would fill at that price.
- Baseline delay: 0 hours; delay sensitivity: 0, 1, and 4 hours.
- Baseline slicing: one hourly bar (K=1). No additional slicing study in the initial implementation.
- Daily signal availability is the completed daily candle's interval end. At zero delay, select the first hourly candle with `interval_start >= signal_available_at` and use its open as the simulated fill reference; positive delays shift this eligibility time. This convention must be tested and is not a guarantee of real execution.
- Track EUR cash, BTC quantity, trade notional, fees, slippage, equity, exposure, and mark-to-market P&L.
- Apply costs to actual traded notional on both entry and exit. Do not assume fills that the hourly OHLCV data cannot support.
- No portfolio state, position, or trade may bridge a data gap or an independent evaluation-window boundary.

## Cost scenarios
Research assumptions unless verified by dated, relevant evidence:
- Fee per side: 5, 10, and 25 basis points.
- Slippage per side: 1.5, 5, and 10 basis points.
- Run all nine fee/slippage combinations at baseline delay.
- Separately test delays 0, 1, and 4 hours using the approved primary fee assumption of 25 bp/side and slippage 1.5 bp/side.
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
- Continuous test: net Sharpe >= 0.8 at 10 bp fee per side (a separately pre-registered comparison; the primary conservative fee assumption is 25 bp/side); max drawdown <= 35%; no collapse from 5 to 25 bp fees; average gross profit per defined completed portfolio trade >= 3x round-trip cost.
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

### Observed hourly/daily file audit (2026-10-19; repository blobs inspected)
- `XBTEUR_60.csv`: 113,180 rows, seven columns, UTC-hour-aligned timestamps from 2013-09-10 23:00 UTC through 2026-09-30 23:00 UTC.
- `XBTEUR_1440.csv`: 4,764 rows, seven columns, UTC-day-aligned timestamps from 2013-09-10 through 2026-09-30 UTC.
- Observed row layout: `timestamp, open, high, low, close, volume, trade_count`; timestamps are Unix seconds. The hourly file has 272 gap transitions (1,253 missing hourly intervals) and 273 contiguous runs. The daily file has four gap transitions (five missing daily intervals) and five contiguous runs.
- All rows passed the inspected structural checks: seven columns, finite numeric values, valid OHLC relationships, non-negative volume/count, aligned timestamps, strict chronology, and no duplicate timestamps.
- Of 4,764 UTC dates containing at least one hourly row, 4,637 had all 24 expected hourly intervals. Aggregated OHLC, volume, and trade count matched the corresponding daily file exactly on all 4,637 complete days. The other 127 dates are incomplete and must not be synthesized or used as daily candles.
- Existing `tools/hsra/kraken_ohlcv.py` is hard-coded to five-minute intervals and, for seven-column rows, reads column 7 (trade count) as volume. Do not reuse it for the new strategy; the new isolated hourly reader maps volume and trade count separately.
- This is a content/schema and cross-check result, not a claim that the dataset is representative, execution-realistic, profitable, or independently authenticated against Kraken's upstream systems. It does not verify the 5m/4h/12h files.

## Acceptance gates
1. Verify the cited source and settle source-dependent mechanics.
2. **Completed on 2026-10-19:** inspect `data/kraken/XBTEUR_60.csv` and `data/kraken/XBTEUR_1440.csv` contents, row schema, chronology, gaps, OHLCV relationships, and cross-check complete UTC daily aggregates. New isolated reader/tests have been added on a research branch; test execution remains pending.
3. Freeze timestamp, daily-bar, gap, warm-up, price equality, volatility, window, accounting, and execution semantics.
4. Implement and test the deterministic strategy state machine.
5. Implement and test portfolio accounting, execution simulation, and costs.
6. Generate reproducible reports and inspect their contents before any conclusion.
7. Paper trading, live orders, and scaling remain blocked without separate explicit authorization.
