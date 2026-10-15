# Trading Bot - Strategy Specification

## Status

- Status: descriptive and provider-specific research only
- Approval: not a live-trading approval
- Profitability claim: not authorized
- Historical source: Kraken BTC/EUR 5-minute OHLCV export

## Research objective

The repository studies a simple descriptive bullish-signal question on the Kraken BTC/EUR 5-minute OHLCV stream:

- Does a completed candle with close > open tend to be followed by a positive next-period return relative to the same eligible observation set?

This is a descriptive question only. It is not a profitability or execution claim.

## Descriptive mechanics

The signal, target, and baseline follow the frozen experimental contract:

- `signal_k = 1` if `close_k > open_k`, otherwise `0`
- `r_k = (close_{k+1} - close_k) / close_k`
- `label_k = 1` if `r_k > 0`, otherwise `0`
- `baseline_rate = count(label_k = 1) / count(eligible observations)`
- `signal_rate = count(label_k = 1 | signal_k = 1) / count(signal_k = 1)`

The comparison is descriptive and bounded to the same valid observation set.

## Data and validity rules

- Use only the Kraken BTC/EUR 5-minute OHLCV source.
- Treat timestamps as the interval start in UTC.
- Require structurally valid OHLCV rows: finite numeric values, aligned 5-minute timestamps, valid OHLC relation, no duplicate bars.
- Treat missing 5-minute intervals as gaps.
- Never backfill, bridge, or repair missing bars by assumption.
- Reject ambiguous or invalid windows instead of inferring missing semantics.
- Keep the study bounded to the actual retained source range; do not claim full-market or full-archive coverage.

## Rejection and anti-lookahead rules

- No look-ahead.
- No using future candle data to define a signal.
- No silent gap repair.
- Only completed bars are eligible.
- Any uncertain source semantics cause exclusion or a blocked run.
- Segment boundaries are hard barriers for signal evaluation, warm-up state, open positions, and holding periods; no state or position may cross a segment gap.

### Approved segmented historical research mode (2026-10-14)

This repository explicitly approves a separate segmented historical research mode for the existing Kraken BTC/EUR 5-minute dataset. This mode is limited to historical analysis and does not authorize live trading, paper trading, execution readiness, or profitability claims.

This approval is documentation-only. It does not imply that a segmented backtest has been implemented, validated, or separately authorized to run. Any segmented backtest must wait until the required implementation scope, eligibility rules, and unresolved thresholds are explicitly settled and documented. Paper trading, live trading, scaling, and profitability claims remain unauthorized.

The approved segmented research policy is:

- Split the source into maximal contiguous 5-minute segments using actual timestamps.
- Never backfill, bridge, or synthesize missing candles.
- Treat each segment as an independent observation domain.
- Reset all strategy state, indicator/lookback warm-up, pending signals, open positions, and holding-period state at every segment boundary.
- Never open a trade unless the full required lookback and signal formation occur inside the same segment.
- Never carry an open position or holding period across a segment boundary. Do not invent a boundary exit price or fill.
- Preserve the existing fail-closed behavior for any individual segment that violates timestamp, ordering, OHLCV, or other existing validity checks.
- Keep this mode explicitly separate from continuous-history replay; it does not weaken or silently change the existing replay contract.
- Report segment counts and length distribution, excluded segments, eligible candles, signals, simulated trades, boundary-related exclusions, exit reasons, gross P&L, costs, and net P&L where the implementation supports them.
- Label all outputs as segmented historical research. They are not proof of profitability and do not authorize paper or live trading.

The following policy elements remain unresolved and must not be silently fixed by implementation choice:

- minimum segment length
- minimum eligible-candle count per segment
- minimum trade count per segmented run

These thresholds may be decided later only with explicit human approval and authoritative support; they are intentionally not adopted here.

## Interpretation rules

- Results are descriptive only.
- They do not prove profitability, execution viability, or live readiness.
- They only support a statement about the observed sample under the documented source and validation rules.

## Required run metadata

Every run must record:

- source identity
- exact UTC bounds
- file identity
- row counts and validation counts
- rejected-window counts
- known limitations and gap handling
- explicit descriptive interpretation

This keeps the study consistent with the repository's risk and governance standards.
- the exact signal-definition and baseline logic used,
- any excluded windows and the reason for exclusion.

### Current active source contract

The current repository contract is:

- Active source: Kraken BTC/EUR 5-minute OHLCV export under `data/kraken/`.
- Active scope: descriptive research only, non-execution, fail-closed against ambiguous or invalid input.
- Historical artifacts retained: the legacy Tardis first-of-month manifest and reports are preserved for provenance and audit, but they are not active source requirements for the current Kraken research contract.
- No active-source claim is made that the current Kraken archive is fully representative, complete, or execution-ready.

### Historical artifact classification

The following historical items remain preserved as evidence only and must not be described as the active Kraken input contract:

- Tardis first-of-month sampling rules.
- Tardis manifest paths and associated first-day-of-month file selection criteria.
- Historical reports generated from Tardis-style trade data.
- Any wording that implies those historical files are the authoritative input for current Kraken work.

The repository may retain those artifacts for traceability, but they must be explicitly labeled historical, not active.

### Approved research-direction decision: holistic component evaluation (2026-10-14)

`APPROVED (HUMAN-AUTHORIZED DELEGATED DECISION, 2026-10-14)`

- `S3D-014`: The repository approves a holistic, evidence-driven research direction for identifying complementary strategy components and evaluating integrated spot-trading candidates. This decision authorizes research-design documentation only; it does not authorize code changes, experiment execution, backtests, paper trading, live trading, or scaling.

This decision is an approved research-direction decision, not an approved trading strategy.

1. Research objective: identify and validate useful combinations of existing strategy components, rather than selecting a winner between Experiment A and Experiment B alone.
2. Experiment A and Experiment B: retain their current definitions and distinct descriptive-research purposes. They remain separate research questions and are not silently redefined or collapsed into a single winner-takes-all comparison.
3. Baselines B1 and B2: treat them as comparison methods only, not as approved production strategies.
4. Component research: inventory and verify the exact existing entry, confirmation, filter, exit, position-management, risk, and data-quality rules before selecting combinations.
5. Incremental evaluation: investigate the contribution of individual components and justified combinations. Do not assume that adding a filter improves performance or that all components should be combined.
6. Fair comparison: use a documented common data and evaluation framework where comparisons are valid, while preserving each method's legitimate signal eligibility and entry/return semantics. Do not force incompatible experiments onto an artificially identical observation set.
7. Overfitting controls: define parameter choices and the evaluation protocol before examining final evaluation results. Keep parameter selection separate from final out-of-sample evaluation. Do not invent arbitrary acceptance thresholds or statistical claims.
8. Integrated backtest: only after the candidate rules and protocol are explicitly specified and the required approvals are recorded, evaluate candidates with realistic fees, spread, slippage, execution assumptions, and relevant capital/risk constraints.
9. Evidence standard: distinguish descriptive signal observations from executable trades and net profitability. No profitability claim is justified without reproducible, appropriately controlled, cost-aware validation.
10. Scope boundary: SPOT only. This decision grants no paper-trading, live-trading, or scaling authorization. Those remain separate approval gates.

The approved research direction is therefore: document and validate the existing rule inventory, define a fair comparison protocol for justified combinations, and treat the integrated candidate as a proposal pending explicit approval and evidence from cost-aware validation. This does not approve a live strategy, a parameter grid, or a profitability claim.

### First bounded historical backtest scope (research design only)

The initial trade-level backtest is intentionally limited to a single long-only spot candidate using the existing local-structure signal logic already implemented in `tools/hsra/strategy.py` and the conservative cost model already present in `tools/hsra/cost.py`.

- Candidate design: local downside sweep + rejection morphology + one-bar confirmation, evaluated on valid contiguous Kraken BTC/EUR 5-minute windows.
- Initial fixed configuration for the first bounded historical run: `lookback=3` and a single-step exit horizon for a gross trade-level simulation only.
- Research configuration status: this `lookback=3` / single-step-exit design is an implemented research configuration for this bounded milestone only; it is not a live-trading approval, not a broader strategy approval, and not a claim that the parameter choice is validated or optimal.
- Entry semantics: use the next executable historical opportunity after the signal timestamp; do not silently assume a fill at the signal candle close.
- Risk and accounting: keep risk approval, position state, and cost accounting as separate concerns from signal generation; do not conflate signal generation with net profitability.
- Scope: historical research only; no paper trading, no live trading, and no scaling authorization.
- Interpretation: results are bounded and descriptive unless they are explicitly labeled as gross backtest results with costs separately reported; net profitability claims remain blocked until the full cost-aware validation and approval gate is satisfied.

### Research-only trend-filtered price-channel breakout candidate (2026-10-15)

`APPROVED FOR RESEARCH DESIGN ONLY, 2026-10-15`

This repository records a separate research-only breakout candidate that is intentionally distinct from the existing local-structure strategy in `tools/hsra/strategy.py` and is not a live-trading approval.

- Market and source: Kraken BTC/EUR, 5-minute OHLCV only.
- Trade type: long-only spot, research-only, no execution, no paper-trading authorization.
- Signal definition: a completed candle closes strictly above the maximum high of the preceding `N` completed candles, excluding the signal candle from the channel calculation.
- Channel lookback grid: `N ∈ {6, 12, 24, 48}` completed candles.
- Trend filters:
  1. no trend filter,
  2. `signal_close > SMA(20)`,
  3. `signal_close > SMA(20) and SMA(20) > SMA(50)`.
- SMA calculation: use only completed candles that are available at signal time; never use future candles.
- Entry reference: next candle open.
- Exit reference: close of the final candle in the holding period.
- Holding horizon grid: `H ∈ {3, 6, 12}` completed candles.
- Reject conditions: insufficient completed history, non-contiguous candles, missing or ambiguous entry/exit horizon, or any use of future information.
- Implementation status: historical signal-generation logic only; no order placement, no live execution, no risk-limit claim, no profitability claim.

The first approved research design grid is therefore:

- `channel_lookback ∈ {6, 12, 24, 48}`
- `trend_filter ∈ {none, close_above_sma20, close_above_sma20_and_sma20_gt_sma50}`
- `hold_period ∈ {3, 6, 12}`

This is a proposed parameter grid for controlled descriptive research only. It must not be treated as a valid profitability result, an optimization result, or a live-trading configuration.

### Approved 60/20/20 chronological split and parameter-selection policy (2026-10-15)

`APPROVED (HUMAN-AUTHORIZED DECISION, 2026-10-15)`

The repository now approves the following experiment policy for the existing Kraken BTC/EUR 5-minute OHLCV source and the research-only trend-filtered breakout candidate:

1. Chronological split
   - Split the validated dataset into 60% training, 20% validation, and 20% final test by order of time.
   - The dataset must be considered valid only after timestamp ordering, duplicate detection, OHLCV validity, UTC interpretation, and continuity validation pass.
   - A trade's entry-to-exit window must remain inside a single partition; no trade may cross a train/validation/test boundary.
   - Training and validation data are used only for parameter selection.
   - The final test remains untouched until the selection procedure and selected parameters are fixed.
   - Exact boundaries must be reported along with the handling of boundary candles and excluded observations.

2. Source validation
   - Use only the existing Kraken BTC/EUR 5-minute OHLCV source under `data/kraken/`.
   - Validate timestamp ordering, duplicate timestamps, OHLCV validity, UTC interpretation, and continuity.
   - Do not silently repair malformed rows, merge duplicate timestamps, or synthesize missing candles.
   - Treat gaps as segment boundaries and exclude invalid observations according to documented, tested rules.
   - Record the input file path, SHA-256, row count, timestamp range, gap statistics, and validation outcome in the experiment report.
   - Do not claim this dataset represents Bitvavo execution conditions or live trading performance.

3. Parameter selection and evaluation
   - Evaluate the approved 36-combination grid, with the exact candidate definitions already recorded above.
   - Use a deterministic selection rule applied to training and validation data only before final-test inspection.
   - The selection rule must be fixed before final-test results are examined and must be documented in the report.
   - No minimum sample thresholds or statistical acceptance thresholds are invented here; sample sizes and limitations are reported explicitly.
   - If a critical detail cannot be resolved from this documentation or the approved rules, the experiment is stopped and the issue is reported rather than guessed.

The approved deterministic selection procedure is:

- For each parameter combination in the fixed 36-combination grid, evaluate the candidate over the training and validation partitions separately.
- Compute the validation gross return as the aggregate return across all eligible validation trades for that parameter set.
- Rank parameter sets by validation gross return descending.
- Break ties deterministically by the parameter order `(channel_lookback, trend_filter, hold_period)` as enumerated in the approved grid.
- Select the first-ranked parameter set for final-test evaluation.
- Final-test results are evaluated once after the selection is fixed and are never used to choose parameters.

This approval defines the historical research protocol only. It does not authorize paper trading, live trading, or profitability claims.

### Experiment A contract

Experiment A is the descriptive bullish-close signal study currently implemented in `tools/hsra/bounded_experiment.py`.

- Signal: `signal_k = 1 if close_k > open_k else 0`
- Target return: `r_k = (close_{k+1} - close_k) / close_k`
- Baseline: positive-return frequency across all eligible observations in the same valid observation set.
- Signal rate: positive-return frequency among eligible bullish-signal observations.
- Eligibility: valid adjacent completed candles within contiguous Kraken windows; missing, ambiguous, or invalid windows are rejected rather than repaired by assumption.
- Interpretation: descriptive only; no profitability, execution, or live-trading approval.

### Experiment B contract

Experiment B is the local rejection/confirmation signal study currently implemented in `tools/hsra/second_strategy_experiment.py`.

- Signal family: local downside sweep + rejection candle + bullish confirmation.
- Current implementation defaults: `lookback=12`, `hold_period=3`.
- Implementation contract: the signal is evaluated on completed, contiguous Kraken windows; it requires sufficient lookback and forward observations, and it uses the next-candle open as the entry reference for the fixed forward return calculation.
- Return definition: the fixed-horizon forward return is computed from the entry reference open to the close at `entry_reference_index + hold_period - 1`.
- Strictness: it has stricter eligibility requirements than Experiment A, and it is still a descriptive signal evaluation only, not an execution-aware backtest or live-trading model.

### Provenance and reproducibility blockers

The current Kraken manifest records `sha256: null`. This means the raw archive identity has not yet been cryptographically established.

Minimum evidence required before the next controlled rerun:

- SHA-256 of the exact raw CSV bytes without modifying the file.
- Exact manifest path and manifest identity.
- Input row count, timestamp bounds, validation counts, and gap policy.
- Code version or commit identity.
- Experiment parameters and eligibility definitions.
- Full aggregate counts and ratios.
- Deterministic output artifacts with a clear distinction between complete results and illustrative observation samples.

The repository must not claim verified archive coverage or exact UTC bounds unless this evidence exists.

### Resolved stale-wording status for the generated A report

The generator wording and the focused validation contract for the bounded A report have been corrected in the repository. This resolves the stale wording issue only.

This does not prove that the report was regenerated, nor does it independently establish raw archive identity, exact UTC coverage, or complete day-level data coverage. The current descriptive result remains bounded research evidence only and does not constitute execution evidence or proof of profitability.

The repository continues to preserve the historical Tardis provenance notes and must not imply that historical Tardis artifacts were deleted or that the Kraken dataset has been fully verified.

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

## Box Theory candidate strategy (research implementation)

**Status:** implemented on the `strategy/box-theory-research` branch as a research-only candidate. It is not profitability-validated and does not authorize paper or live trading. Experiment A and Experiment B retain their existing frozen definitions.

### Initial deterministic rules

- Market/source: Kraken BTC/EUR 5-minute OHLCV only.
- Clock: UTC calendar days; each day requires exactly 288 valid, aligned 5-minute candles.
- Box: previous completed UTC day's high and low; midpoint is the arithmetic midpoint.
- Lower entry zone: bottom 25% of the box, configurable as `zone_fraction=0.25`.
- Long signal: a completed candle's low reaches the upper boundary of the lower zone or below, then closes strictly above that boundary and within the box.
- Entry: next eligible candle's open; no entry is simulated from the signal candle itself.
- Stop: signal candle low minus a 5-basis-point price buffer (`stop_buffer_bps=5.0`).
- Target: previous-day box midpoint.
- Trade eligibility: entry must be strictly above the stop and strictly below the target. Invalid geometry is rejected.
- Position policy: long-only spot research, one position at a time per contiguous segment. No short selling, leverage, margin, futures, or perpetuals.
- Exit simulation: inspect candles from the entry candle onward. A gap below the stop exits at the observed open; a gap above the target is conservatively filled at the target. If a candle touches both stop and target and intrabar order is unknowable, the stop is assumed first. A position still open at segment end is reported as unresolved and is not force-closed at an invented price.
- Data gaps: split into maximal contiguous segments and reset all state at every gap. A prior-day box is unavailable unless all 288 candles for that day are present inside the same segment. No backfill or synthetic candles.
- Costs: use the existing `CostModel` defaults, including its configured fees, spread, slippage, and latency estimate. These are model assumptions, not verified Bitvavo execution costs.

### Research-only defaults and limitations

The 25% zone, 5-bps stop buffer, and €50 notional are explicit initial research settings, not optimized or approved live settings. The existing cost model is a proxy and does not establish actual fills, liquidity, or Bitvavo costs. The first implementation does not yet include dynamic intraday box redraws, historical support/resistance confluence, shorts, or discretionary candlestick patterns; those are excluded to keep the initial hypothesis falsifiable.

### Implementation entry points

- `tools/hsra/box_theory.py`: deterministic signal, stop/target, cost-aware trade simulation, and gap-segmented runner.
- `tools/hsra/box_theory_experiment.py`: command-line runner for a Kraken OHLCV CSV with SHA-256 provenance in the output report.
- `tests/test_box_theory.py`: focused behavior tests.

Example local invocation:

```powershell
python -m tools.hsra.box_theory_experiment --input data/kraken/XBTEUR_5.csv --output reports/box_theory_kraken_btc_eur.json
```

All outputs are historical research only. No strategy profitability, paper-trading readiness, live-trading readiness, or scaling claim follows from implementation or test success.
