# Trading Bot - Candlestick Strategy Specification

## Document Status

- Status: Proposed for human review.
- Approval state: Not approved.
- Implementation state: Not implemented.
- Validation state: Not validated.
- Profitability state: Unknown.

Classification used in this document:

- `FACT`: established by repository documents or exchange-style data semantics.
- `HYPOTHESIS`: an unvalidated trading claim to be tested.
- `PROPOSED RULE`: a deterministic candidate rule for research and later implementation.
- `UNRESOLVED DECISION`: materially affects the strategy and requires human approval.

## 1. Executive Summary

`FACT`: The project is spot-only, capital-constrained, research-driven, and not allowed to claim profitability without evidence. Bitvavo Spot is the intended execution venue, while the first historical research dataset is provisionally accepted as a bounded Tardis.dev Binance Jersey BTCEUR archive of quotes and trades in daily `.csv.gz` files limited to the first calendar day of each month only. This provisional acceptance allows research to continue under current data-access and budget constraints, but it does not prove statistical representativeness, final dataset adequacy, or strategy profitability. The market universe, timeframe, sample adequacy, and numeric risk limits remain unapproved.

`RESEARCH CONCLUSION`: A standalone named candlestick pattern strategy is not defensible as an approved trading rule at this stage. Pattern recognition is subjective unless codified, and predictive value is not established by the current project evidence.

`RECOMMENDATION`: Start with one minimal, deterministic long-only candlestick hypothesis for spot crypto.

- `HYPOTHESIS H1`: A completed downside rejection candle that sweeps a recent local low, then receives one completed-candle bullish confirmation, may have positive short-horizon expectancy after realistic costs in liquid spot crypto markets.

`PROPOSED BASE STRATEGY`: Test a two-candle bullish rejection setup with structural context, no discretionary chart drawing, no ML, and no extra indicators in the initial specification.

`STATUS OF STRATEGY`: Proposed for research only. Not approved, not implemented, not validated, not profitable by virtue of this document.

## 2. Research Basis and Limitations

`FACT`: Repository documents require simplicity, deterministic logic, anti-lookahead handling, realistic execution modeling, and no silent assumptions.

`FACT`: At least one major exchange OHLC API explicitly returns an in-progress candle alongside committed candles. That makes candle-close confirmation and exclusion of the current uncommitted candle mandatory for both live logic and backtests.

`FACT`: Candlestick naming and recognition are subjective unless explicit geometric rules are defined.

`LIMITATION`: This document does not establish empirical profitability for named candlestick patterns in crypto. It establishes only that:

- candlestick rules must be explicit,
- completed versus in-progress candles matter,
- execution costs can erase apparent edge,
- a minimal structure-first hypothesis is more defensible than a catalog of named patterns.

`RESEARCH POSITION`:

- Individual named patterns alone: not recommended as the primary research object.
- Consecutive-candle confirmation: recommended.
- Price-action structure: recommended.
- Support/resistance as hand-drawn zones: not recommended.
- Support/resistance as rolling local extrema: recommended.
- Trend filter: not included in the base strategy.
- Volume filter: optional, only if data quality is verified.
- Extra indicators: excluded from the base strategy.

## 3. Required Data and Unresolved Dependencies

`FACT`: The following are not yet approved in the repository:

- definitive historical-data adequacy and statistical validity of the bounded Tardis.dev Binance Jersey BTCEUR sample,
- eligible spot pairs,
- candle timeframe,
- numeric risk limits,
- implementation stack.

`REQUIRED DATA`:

- Symbol identifier and exchange identifier.
- Candle timestamps.
- `open`, `high`, `low`, `close`, `volume`.
- Confirmation that candles are complete versus still forming.
- Tick size and lot-size constraints.
- Fee schedule for maker and taker executions.
- Minimum notional and minimum quantity rules.
- If available: bid/ask quotes, spread snapshots, trade count, and order-book depth.

`REQUIRED DATA SEMANTICS`:

- Candle timestamp meaning must be approved: open-time or close-time.
- Candle timezone must be approved.
- Missing-candle convention must be explicit.
- Duplicate and out-of-order event policy must be explicit.
- Quote currency and volume field definition must be explicit.
- Whether historical data are raw exchange candles or vendor-resampled candles must be explicit.

`UNRESOLVED DECISION`: Whether the bounded Tardis.dev Binance Jersey BTCEUR historical sample is sufficient for the first research experiment and what statistical limitations it imposes.

Why it matters:

- The selected historical source determines the available quote and trade coverage, the time range, and the cross-market comparability of the research sample.
- Sampling only the first calendar day of each month introduces statistical and regime-coverage limitations that must be assessed before the experiment is treated as valid.
- Bitvavo remains the intended execution venue, but the historical research archive is intentionally separate from the live venue.

Recommended choice:

- Use Tardis.dev historical Binance Jersey BTCEUR quotes and trades as the bounded data source for the first research study.
- Limit collection to the first calendar day of each month only, with daily `.csv.gz` files and explicit documentation of the resulting sampling constraints.
- Treat the samples as a bounded research dataset, not as a final or comprehensive market representation.
- Continue to treat the first experiment as unapproved until adequacy, statistical limits, and execution assumptions are explicitly reviewed.

`UNRESOLVED DECISION`: Primary timeframe.

Why it matters:

- Signal frequency, noise, spread burden, and holding time depend on timeframe.

`PROPOSED RECOMMENDATION (NOT APPROVED)`: use `5m` as the provisional primary timeframe for the first historical SPOT research experiment.

Reasoning:

- The official Bitvavo documentation confirms that `5m` is a supported interval, but it does not provide comparative performance evidence that `5m` is superior to `1m` or other available intervals.
- The project requires a single-timeframe starting point for a bounded research experiment, and `5m` is a reasonable compromise between noise and signal frequency for a short-horizon spot strategy.
- At this stage, this is a provisional candidate rather than a comparative conclusion. The project still needs measurement of signal count, cost drag, and net expectancy to justify the timeframe beyond plausibility.

This remains a decision proposal until the human explicitly approves it.

`PROPOSED CANDLE POLICY FOR THE FIRST EXPERIMENT`:

- `FACT`: Bitvavo candle timestamps are Unix milliseconds and the `timestamp` value represents the start time of the candle interval.
- `FACT`: Bitvavo docs state that data are returned newest-to-oldest and that a no-trade interval can appear as a gap in data flow rather than a fabricated zero-volume candle.
- `FACT`: The inspected documentation does not establish a published semantic distinction between a confirmed no-trade gap and a data-loss or fetch-gap at the source level.
- `PROPOSED RULE`: normalize every candle timestamp to UTC before any replay, storage, or feature generation; treat the timestamp as the interval start in UTC, and treat `timestamp + interval` as the nominal candle close time for replay ordering only.
- `PROPOSED RULE`: for the first experiment, use fixed 5-minute boundaries aligned to the UTC clock. A candle with a start timestamp of `HH:MM:00` is assigned to that 5-minute bucket; the signal decision occurs only after the bar is finalized and the record is available to the replay process.
- `PROPOSED RULE`: only completed candles are eligible for entry evaluation. The most recent candle is treated as incomplete until the source confirms the interval is closed; no entry signal may depend on the current still-forming bar.
- `PROPOSED RULE`: the earliest permissible signal-decision time is after the close of candle `C` as represented in the finalized historical record; this does not imply any numerical latency buffer or assume that a nominal end time equals the moment the live process received the bar.
- `PROPOSED RULE`: reject any setup that relies on look-ahead, a still-forming candle, or a non-contiguous historical context window. Missing bars are not backfilled by assumption.
- `PROPOSED RULE`: duplicate timestamps are a data-integrity issue. If identical duplicates are confirmed as exact repeated rows from the same source, they may be collapsed only under a documented canonical rule; if the source semantics do not prove that they are harmless duplicates, the affected record set must be rejected rather than silently merged. Conflicting duplicates are never silently selected; they are treated as invalid and quarantined until the source or the ingest process resolves them.
- `PROPOSED RULE`: a no-trade gap is permitted only when the source semantics clearly indicate that the market was active and the interval simply had no trades. If the data cannot distinguish a no-trade gap from data loss, the gap is treated as missing/ambiguous data and the affected warm-up or signal window is rejected.
- `EVIDENCE NOTE`: the exact public Bitvavo trade request for `2024-01-01 05:35:00Z` to `2024-01-01 05:40:00Z` returned 0 trades. The adjacent 05:30:00Z to 05:35:00Z window returned 4 trades, and the following 05:40:00Z to 05:45:00Z window returned 18 trades. This is consistent with Bitvavo’s documented zero-trade-gap behavior, where no trades in an interval can appear as a gap in data flow. The conservative policy remains to treat the missing candle as unresolved historical completeness risk unless the source semantics and the chosen replay policy explicitly accept the gap, and to reject any signal that depends on silently inferring or filling the interval.
- `PROPOSED RULE`: historical warm-up for the first experiment requires `L + 2` completed candles immediately preceding the setup candle; if the required context is missing or ambiguous, the signal is rejected rather than interpolated.
- `PROPOSED RULE`: invalid OHLCV records are rejected if any of the following holds: non-finite values, `high < max(open, close)`, `low > min(open, close)`, `high < low`, or zero-range candle with an undefined structure. These diagnostics are deterministic and must be enforced before any strategy rule can evaluate.
- `PROPOSED RULE`: deterministic replay must sort by `(timestamp, symbol)` in ascending order, quarantine conflicting duplicates, and commit one consistent history per symbol before evaluating any entry. The policy does not invent exchange guarantees about duplicate semantics that were not documented.

This policy is a recommendation for the first experiment and remains subject to explicit human approval.

`UNRESOLVED DECISION`: Eligible pairs.

Why it matters:

- Small, illiquid pairs can make candle patterns look attractive but untradeable.

Recommended choice:

- Start with a small set of liquid spot pairs on the approved exchange, selected by transparent liquidity criteria.
- Criteria should be documented before testing.

## 4. Exact Candidate Entry Rules

Base strategy scope:

- `PROPOSED RULE SET`: long-only entries from flat.

Reason:

- Spot-only scope does not support opening naked short positions.

Definitions used by the rules:

- Let `T` be the approved candle timeframe.
- Let `L` be the approved local-structure lookback in completed candles.
- Let `S` be the setup candle.
- Let `C` be the confirmation candle immediately after `S`.
- Let `lower_wick(X) = min(open_X, close_X) - low_X`.
- Let `body(X) = abs(close_X - open_X)`.
- Let `range(X) = high_X - low_X`.
- Let `prior_low(S, L) = min(low of the L completed candles immediately before S)`.

`PROPOSED RULE EN-01: Data eligibility prerequisite`

- Purpose: ensure the signal is evaluated only on usable, complete input.
- Required input data: ordered OHLCV candles, symbol metadata, completeness flag or equivalent committed-bar logic.
- Exact definition: `S` and `C` must both be completed candles; the `L` candles before `S` must exist and be contiguous according to the approved missing-candle policy.
- Evaluation timing: after `C` closes.
- Effect: prerequisite for entry evaluation.
- Edge cases: if candle completeness is ambiguous, reject the signal.
- Status: mandatory.
- How it will be tested: unit tests with incomplete-current-bar scenarios, missing-candle sequences, and duplicated candles.
- Known limitations: depends on approved candle semantics.

`PROPOSED RULE EN-02: Local downside sweep`

- Purpose: require the setup to occur after a local downside extension rather than in arbitrary noise.
- Required input data: completed candle lows.
- Exact definition: `low_S < prior_low(S, L)`.
- Evaluation timing: after `C` closes.
- Effect: entry condition.
- Edge cases: equality should not count as a sweep unless the exchange tick-size policy defines equality handling otherwise.
- Status: mandatory.
- How it will be tested: deterministic replay with varying `L`.
- Known limitations: `L` requires approval.

`PROPOSED RULE EN-03: Rejection morphology`

- Purpose: require evidence that the downside sweep was rejected within the setup candle.
- Required input data: `open_S`, `high_S`, `low_S`, `close_S`.
- Exact definition:
  - `close_S > low_(S-1)`, and
  - `lower_wick(S) > body(S)`, and
  - `range(S) > 0`.
- Evaluation timing: after `C` closes.
- Effect: entry condition.
- Edge cases: zero-range candles are invalid; if `S-1` is missing, signal is invalid.
- Status: mandatory.
- How it will be tested: fixture cases for zero-range bars, equal-body and equal-wick cases, and synthetic sweep/reclaim examples.
- Known limitations: this is a geometric definition, not evidence of edge.

`PROPOSED RULE EN-04: One-bar bullish confirmation`

- Purpose: reduce false positives from single-candle reversals that fail immediately.
- Required input data: `high_S`, `close_C`.
- Exact definition: `close_C > high_S`.
- Evaluation timing: immediately after `C` closes.
- Effect: entry signal becomes eligible for risk review.
- Edge cases: equality is not a breakout unless the human approves equality semantics.
- Status: mandatory.
- How it will be tested: replay tests where `C` closes below, at, and above `high_S`.
- Known limitations: may reduce trade count materially.

`PROPOSED RULE EN-05: Entry timestamp and reference price`

- Purpose: separate signal generation from execution.
- Required input data: signal close timestamp, next executable market data.
- Exact definition: when EN-01 through EN-04 hold, the strategy emits a long proposal at the close timestamp of `C`. It does not assume a fill at `close_C`. The earliest candidate execution is the next executable opportunity after the signal timestamp, subject to the Risk Engine and exchange constraints.
- Evaluation timing: at signal creation and later at execution simulation.
- Effect: signal generation only.
- Edge cases: if market-data or execution data are missing at the next opportunity, the order is not assumed filled.
- Status: mandatory.
- How it will be tested: replay tests with delayed or missing next-bar execution data.
- Known limitations: exact fill modeling depends on exchange data availability.

`OPTIONAL EXPERIMENTAL RULE EN-X1: Relative-volume confirmation`

- Purpose: test whether rejection events with above-normal participation are more robust.
- Required input data: reliable volume field, approved rolling window `V`.
- Exact definition: `volume_S > median(volume of previous V completed candles)`.
- Evaluation timing: after `C` closes.
- Effect: optional additional filter in experimental variants only.
- Edge cases: exchanges with unreliable volume definitions should disable this rule.
- Status: experimental hypothesis.
- How it will be tested: ablation test versus the base strategy.
- Known limitations: volume quality is exchange-dependent.

## 5. Exact Candidate Rejection Rules

`PROPOSED RULE RJ-01: Reject on incomplete or uncommitted candle data`

- Purpose: prevent look-ahead and ambiguous signals.
- Required input data: candle commitment status.
- Exact definition: if any signal rule relies on the current still-forming candle, reject.
- Evaluation timing: before signal emission.
- Effect: reject entry.
- Edge cases: feeds without explicit commitment flags require an approved bar-finalization convention.
- Status: mandatory.
- How it will be tested: live-style replay with intrabar updates.
- Known limitations: depends on feed semantics.

`PROPOSED RULE RJ-02: Reject on missing or non-contiguous context`

- Purpose: avoid evaluating local-structure rules on broken history.
- Required input data: ordered timestamps for required context window.
- Exact definition: if the required `L + 2` completed candles are not present and contiguous under the approved policy, reject.
- Evaluation timing: before entry-rule evaluation.
- Effect: reject entry.
- Edge cases: exchange maintenance gaps require explicit policy.
- Status: mandatory.
- How it will be tested: synthetic gaps in setup windows.
- Known limitations: continuity policy remains unresolved.

`PROPOSED RULE RJ-03: Reject on duplicate or out-of-order events`

- Purpose: preserve deterministic behavior.
- Required input data: ordered candle stream.
- Exact definition: if candle timestamps are duplicated or arrive out of order, the strategy must not evaluate a new signal using that inconsistent slice.
- Evaluation timing: on data ingestion or pre-evaluation validation.
- Effect: reject signal evaluation for the affected symbol until the data stream is reconciled.
- Edge cases: late corrections from vendors require explicit reconciliation handling.
- Status: mandatory.
- How it will be tested: duplicate-row and shuffled-order fixtures.
- Known limitations: exact reconciliation workflow is a system dependency.

`PROPOSED RULE RJ-04: Reject if an open position already exists in the same symbol`

- Purpose: avoid uncontrolled stacking.
- Required input data: current position state and pending-order state for the symbol.
- Exact definition: if the symbol already has an open position or a still-pending entry order, do not create a second entry signal for that symbol.
- Evaluation timing: after signal generation, before submission.
- Effect: reject entry.
- Edge cases: partial fills require execution-state reconciliation.
- Status: mandatory.
- How it will be tested: stateful tests with open and pending symbol states.
- Known limitations: portfolio-level multi-entry policy is unresolved.

`PROPOSED RULE RJ-05: Reject stale signals`

- Purpose: prevent late chasing of a short-horizon setup.
- Required input data: signal timestamp and approved validity window.
- Exact definition: if the signal generated at the close of `C` is not submitted for execution within the approved signal-validity window, the signal expires.
- Evaluation timing: before order submission.
- Effect: reject entry.
- Edge cases: exchange outages may expire valid signals under this rule.
- Status: mandatory.
- How it will be tested: delayed-submission simulations.
- Known limitations: exact validity window requires approval.

Recommended initial validity window:

- one candle interval.

Why recommended:

- the pattern is intended as a short-horizon scalp and should not persist indefinitely.

Approval required:

- yes.

`PROPOSED RULE RJ-06: Reject when execution-cost viability is not met`

- Purpose: block trades whose economics cannot be defended.
- Required input data: approved cost model inputs.
- Exact definition: if estimated round-trip costs cannot be computed from the approved cost model, or if estimated costs exceed the approved share of expected move size, reject.
- Evaluation timing: before final submission eligibility.
- Effect: reject live entry and flag research ambiguity in backtests.
- Edge cases: candle-only research may not support precise expected-move estimation.
- Status: mandatory in live/paper modes, conditional in research mode.
- How it will be tested: missing-cost-input and high-cost scenarios.
- Known limitations: depends on unresolved exchange and cost-model approval.

`PROPOSED RULE RJ-07: Reject when Risk Engine denies`

- Purpose: enforce risk authority.
- Required input data: Risk Engine decision.
- Exact definition: any strategy signal without Risk Engine approval remains a rejected opportunity, not a trade.
- Evaluation timing: after strategy proposal creation.
- Effect: reject entry.
- Edge cases: unavailable Risk Engine service must default to no trade.
- Status: mandatory.
- How it will be tested: mocked deny and unavailable responses.
- Known limitations: depends on future risk-system behavior.

## 6. Exact Candidate Exit and Invalidation Rules

`PROPOSED RULE EX-01: Structural invalidation`

- Purpose: define when the reversal thesis is wrong.
- Required input data: `low_S`, completed post-entry candles.
- Exact definition: after entry, if any completed candle closes below `low_S`, the strategy requests exit at the next executable opportunity.
- Evaluation timing: at each completed candle close after entry.
- Effect: invalidation exit.
- Edge cases: intrabar trades below `low_S` cannot be assumed to trigger a historical stop fill unless finer-granularity data are available.
- Status: mandatory.
- How it will be tested: replay tests with gap-through and close-below events.
- Known limitations: stop realism depends on data granularity.

`PROPOSED RULE EX-02: Baseline research exit by fixed holding horizon`

- Purpose: isolate whether the entry has short-horizon edge before optimizing exits.
- Required input data: entry timestamp, approved horizon `N` in completed candles.
- Exact definition: if EX-01 has not triggered, exit after holding the position for `N` completed candles, at the next executable opportunity after the `N`th completed candle closes.
- Evaluation timing: each bar after entry.
- Effect: baseline exit.
- Edge cases: if execution data are missing at the exit event, do not assume perfect fill.
- Status: mandatory for baseline experiment.
- How it will be tested: run the same entry with multiple approved `N` values in a predeclared research grid.
- Known limitations: `N` requires approval.

`PROPOSED RULE EX-03: Signal expiry before fill`

- Purpose: prevent an old scalp setup from becoming a late chase.
- Required input data: signal timestamp, order state, approved validity window.
- Exact definition: if an order is not accepted or filled within the approved signal-validity window after signal creation, cancel the signal and record it as unexecuted.
- Evaluation timing: while awaiting order acceptance or fill.
- Effect: cancel signal.
- Edge cases: partial fills require execution-policy decisions outside this document.
- Status: mandatory.
- How it will be tested: delayed or rejected-entry scenarios.
- Known limitations: exact handling of partially filled entry orders depends on execution design.

`EXPERIMENTAL EXIT FAMILY EX-X1: Reward-multiple exit`

- Purpose: compare fixed-horizon exits against a risk-multiple take-profit structure.
- Required input data: entry reference price, `low_S`, approved multiple `m`.
- Exact definition: compare EX-01 plus a profit-taking exit at an approved multiple `m` of initial risk, where initial risk is `entry_reference - low_S`.
- Evaluation timing: post-entry.
- Effect: experimental alternative exit.
- Edge cases: initial risk must be positive and executable after tick-size rounding.
- Status: experimental only.
- How it will be tested: side-by-side comparison against EX-02 under fixed rules.
- Known limitations: do not approve take-profit rules before the entry edge itself is shown.

`EXPERIMENTAL EXIT FAMILY EX-X2: Trailing structural exit`

- Purpose: compare fixed-horizon exits against a structural trail.
- Required input data: completed post-entry lows and favorable-close state.
- Exact definition: compare EX-01 plus exit on close below the prior completed candle low after at least one favorable completed close.
- Evaluation timing: post-entry on each completed candle.
- Effect: experimental alternative exit.
- Edge cases: equal lows require approved equality semantics.
- Status: experimental only.
- How it will be tested: side-by-side comparison against EX-02 under fixed rules.
- Known limitations: candidate follow-up research, not part of the base strategy.

## 7. Signal and Position Lifecycle

1. Receive market data for a symbol.
2. Validate timestamp order, candle commitment status, and continuity.
3. Mark the current in-progress candle as ineligible for signal confirmation.
4. On each completed candle close, evaluate EN-01 through EN-04.
5. If satisfied, generate a strategy proposal with signal metadata.
6. Pass the proposal to the Risk Engine.
7. If denied, record rejection with explicit rule and risk reason.
8. If approved, submit order request through the execution layer.
9. Await order acknowledgment and fill events.
10. If unfilled or partially filled, reconcile according to execution policy; do not assume the theoretical entry occurred.
11. Once a position is open, monitor EX-01 and EX-02 on completed bars.
12. Submit exit request when an exit condition triggers.
13. Reconcile exit fills and final position closure.
14. Record trade outcome, including signal timestamp, execution timestamps, fills, costs, and rule identifiers.

Overlapping and repeated signals:

- Same symbol while flat: only the latest valid signal may be active if earlier ones expired unfilled.
- Same symbol while already long: reject new long entries.
- Different symbols at the same time: strategy may emit multiple proposals; final selection is a risk and portfolio dependency, not silently defined here.
- Repeated signals from the same local structure: treat each signal as distinct only if a new setup candle `S` forms after the prior signal lifecycle ends.

## 8. Risk Engine Interface

The strategy must provide, at minimum:

- `strategy_id`
- `strategy_version`
- `signal_id`
- `symbol`
- `side = BUY`
- `signal_timestamp`
- `setup_candle_timestamp`
- `confirmation_candle_timestamp`
- `timeframe`
- `lookback_L`
- `entry_rule_ids_triggered`
- `rejection_rule_ids_checked`
- `invalidation_reference_price = low_S`
- `baseline_exit_family_id`
- `baseline_holding_horizon_N`
- `reference_prices`:
  - `open_S`, `high_S`, `low_S`, `close_S`, `close_C`
- `data_quality_flags`
- `estimated_execution_cost_inputs`
- `human-readable rationale`

The strategy must not provide or infer:

- approved position size,
- approved risk-per-trade,
- approved max daily loss,
- approval to bypass risk,
- assumption of fill.

Dependencies not yet resolved:

- position sizing policy,
- simultaneous-position limits,
- daily-loss limits,
- emergency stop behavior,
- portfolio conflict resolution across symbols.

These must be approved before live deployment and materially limit what can be validated beyond signal quality.

## 9. Anti-Lookahead and Deterministic-Behavior Requirements

Mandatory controls:

- Only completed candles may participate in signal confirmation.
- The current in-progress candle must never contribute its final `high`, `low`, `close`, or `volume` to a decision.
- Candle order must be strictly chronological.
- Duplicate timestamps must fail validation for that slice.
- Missing candles must trigger the approved continuity policy before evaluation.
- Signal generation timestamp and execution timestamp must be recorded separately.
- Replaying the same ordered input data with the same approved parameters must reproduce the same signal decisions.

Required anti-lookahead tests:

- Test that signals do not change when a currently forming candle later updates before close.
- Test that backtests using committed bars only differ from naive backtests that accidentally include the current live bar.
- Test that shuffling or misordering candles changes validation state rather than silently changing signals.
- Test that missing intermediate candles do not get forward-filled without an explicit approved rule.
- Test that execution is modeled after signal timestamp, never at a price not available at decision time.
- Test that parameter selection uses only development data and never the final untouched holdout.

## 10. Execution-Cost Assumptions and Limitations

`FACT`: A signal is not the same thing as an executable trade.

Research cost model must include, where available:

- entry fee,
- exit fee,
- half-spread or realized spread penalty,
- slippage,
- latency between signal and submission,
- minimum order size constraints,
- partial fills,
- rejected orders,
- skipped trades due to execution infeasibility.

Recommended research convention:

- Backtest signal generation on candles.
- Simulate execution at the earliest post-signal executable price permitted by the approved market-data granularity.
- Apply fees and spread explicitly rather than assuming candle close is tradable.
- Where spread data are unavailable, run sensitivity scenarios with conservative cost increments and do not label profitability robust unless conclusions survive them.

Known limitation:

- Candle-only data are insufficient for precise stop-fill realism and intrabar execution path modeling.
- If only OHLCV are available, the research should state that invalidation and exit fills are approximations.

## 11. Experimental Validation Methodology

Research objective:

- determine whether H1 has positive net expectancy after costs, not whether the backtest can be made attractive.

Method:

1. Freeze the strategy definition before testing.
2. Approve one exchange, one primary timeframe, one initial asset universe, one candle-semantics policy, and one cost-model policy.
3. Pull raw historical data and run data-quality checks.
4. Reserve a final untouched chronological holdout period before any tuning.
5. Use development data only to compare a small, predeclared set of `L` and `N` values and any optional volume-filter variant.
6. Evaluate the selected candidate on validation data without changing the rule family.
7. Run one final untouched out-of-sample evaluation on the holdout period.
8. If still promising, run paper trading before any live test.

Recommended parameter discipline:

- Keep the grid small and predeclared.
- Recommended research candidates for `L`: values representing short local structure only.
- Recommended research candidates for `N`: values representing short scalp holding windows only.
- Exact values require approval because timeframe is unresolved.

Recommended split method:

- Anchored or rolling walk-forward chronological evaluation rather than random shuffling.

Reason:

- preserves regime order and avoids leakage.

Required data-quality checks:

- candle continuity,
- duplicate timestamps,
- out-of-order rows,
- zero or impossible prices,
- suspicious zero-volume sequences,
- exchange rule changes over time,
- delisted or renamed pairs,
- survivorship bias in asset selection.

Robustness checks:

- vary costs upward,
- test across multiple chronological regimes,
- test across approved assets separately and pooled,
- compare with and without optional volume filter,
- verify results do not collapse outside one narrow parameter combination.

## 12. Metrics and Baseline

Required metrics:

- `Net return after costs`: realized PnL after fees, spread, slippage, and rejected or partial-fill effects.
- `Expectancy per trade after costs`: mean trade PnL after costs.
  Interpretation: primary measure of economic edge.
- `Win rate`: fraction of profitable closed trades.
  Interpretation: never sufficient alone.
- `Average win`, `average loss`, and `win/loss ratio`.
  Interpretation: needed to contextualize win rate.
- `Profit factor`: gross profits divided by gross losses.
  Interpretation: useful only with enough trades and after costs.
- `Maximum drawdown`: largest peak-to-trough equity decline.
  Interpretation: economic survivability.
- `Trade frequency`: number of executed trades per period.
  Interpretation: determines whether apparent edge is scalable or too sparse.
- `Exposure time` and `average holding time`.
  Interpretation: confirms the strategy is truly a scalp and not an unintended swing system.
- `Cost burden ratio`: fraction of gross edge consumed by fees and slippage.
  Interpretation: shows fragility to execution.
- `Segmented performance`: by asset and chronological regime.
  Interpretation: detects concentration of results.
- `Cost sensitivity`: performance under plausible higher-cost scenarios.
  Interpretation: robustness check.

Primary baseline:

- `BASELINE B1`: enter long after any new `L`-bar low break, without rejection-morphology and confirmation rules, then hold for the same `N` horizon under the same cost model.

Reason:

- tests whether the candlestick rejection logic adds value beyond naive dip buying after a local breakdown.

Secondary optional baseline:

- `BASELINE B2`: frequency-matched unconditional entries on the same symbols and horizon.

Reason:

- tests whether any observed edge is simply broad market drift.

## 13. Explicit Rejection Criteria

Reject the strategy if any of the following hold:

- Net expectancy after costs is non-positive on the final untouched holdout.
- Apparent profitability disappears under realistic fee and spread assumptions.
- Performance depends on one narrow parameter choice and is not stable nearby.
- Out-of-sample results materially deteriorate relative to development and validation.
- Results are driven by one asset, one short date range, or one exceptional regime.
- Bootstrap or segmented uncertainty remains too wide to distinguish expectancy from zero.
- Execution feasibility fails because minimum order sizes, spread, or liquidity make trades non-executable.
- Data-quality failures materially affect the result and cannot be resolved reproducibly.
- Paper-trading behavior diverges materially from backtest assumptions.
- The signal cannot be reproduced deterministically from identical input data.

## 14. Known Limitations

- This specification defines one minimal long-only spot hypothesis, not a proven edge.
- Without an approved exchange, live cost realism is incomplete.
- Without approved timeframe and asset universe, exact parameter values should not be finalized.
- OHLCV-only research cannot fully model intrabar path dependence, queue position, or true spread capture.
- The strategy does not yet define portfolio selection among simultaneous cross-asset signals.
- The strategy does not define numeric position sizing or account-level risk limits because those belong to the Risk Engine and remain unresolved.

## 15. Decisions Requiring Human Approval

1. Exchange and authoritative historical and live data source.
2. Primary execution timeframe.
3. Initial liquid spot asset universe and asset-selection criteria.
4. Candle timestamp semantics and timezone convention.
5. Missing-candle policy.
6. Research parameter grid for `L` and `N`.
7. Signal-validity window.
8. Whether the optional volume filter is in scope for the first experiment.
9. Cost-model policy when spread or order-book history is unavailable.
10. Risk Engine numeric limits and simultaneous-position policy.

## 16. Proposed Acceptance Criteria for the Specification Itself

The specification should be accepted for implementation planning only if:

- all mandatory rules are deterministic and auditable,
- signal generation is clearly separated from risk approval and execution,
- anti-lookahead controls are explicit,
- unresolved dependencies are identified rather than guessed,
- the base strategy uses the smallest practical rule set,
- the validation plan can falsify the strategy rather than only support it,
- the document makes no profitability claim,
- the human approves the unresolved decisions listed above.

## Final Status

`READY FOR HUMAN REVIEW`

This strategy is complete enough for review because the rule set, validation method, and unresolved decisions are explicit. It is not approved, implemented, validated, or profitable by virtue of this document.