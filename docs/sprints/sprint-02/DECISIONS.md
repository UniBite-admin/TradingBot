# Sprint 02 - Decisions And Review Findings

This file records decisions already supported by authoritative repository documents, unresolved decisions carried forward into Sprint 02, and review findings from the roadmap and technical-plan audit.

## Supported Decisions And Status Facts

### S2D-001 - Project trading scope remains SPOT only

- Status: APPROVED
- Evidence: `PROJECT_DEFINITION.md`
- Why it matters: neither Sprint 02 nor the future first experiment may assume leverage, margin, futures, or perpetuals.

### S2D-002 - The strategy specification remains proposed, not approved

- Status: APPROVED FACT ABOUT STATUS
- Evidence: `STRATEGY_SPECIFICATION.md`
- Why it matters: Sprint 02 may plan around the proposed hypothesis, but it may not treat the rules as approved implementation requirements.

### S2D-003 - The technical plan remains proposed, not approved

- Status: APPROVED FACT ABOUT STATUS
- Evidence: `TECHNICAL_PLAN.md`
- Why it matters: Sprint 02 may review and improve the document, but it may not silently freeze its proposed decisions.

### S2D-004 - Distinct research and live gates remain required

- Status: APPROVED
- Evidence: `PROJECT_DEFINITION.md`, `ROADMAP.md`, `STRATEGY_SPECIFICATION.md`, and `TECHNICAL_PLAN.md`
- Why it matters: documentation completion, planning progress, or backtest results do not authorize live trading.

### S2D-005 - Signal, order, fill, and final account state must remain separate

- Status: APPROVED
- Evidence: `STRATEGY_SPECIFICATION.md` and `TECHNICAL_PLAN.md`
- Why it matters: Sprint 02 must preserve these distinctions in future experiment planning.

### S2D-006 - Bitvavo Spot is the intended execution venue

- Status: APPROVED HUMAN DECISION
- Evidence: explicit human instruction in Sprint 02 review and live-venue planning.
- Why it matters: Sprint 02 no longer needs to treat exchange venue selection itself as unresolved.

### S2D-007 - The bounded historical research source for the first study is Tardis.dev Binance Jersey BTCEUR quotes and trades

- Status: RECORDED HUMAN DIRECTION WITH OPEN ADEQUACY REVIEW
- Evidence: explicit human decision to use Tardis.dev historical data for Binance Jersey BTCEUR, delivered as daily `.csv.gz` files and limited to the first calendar day of each month only.
- Why it matters: the research sample is intentionally separate from the live execution venue and must be reviewed for adequacy, statistical limits, and anti-lookahead compliance before any experiment approval.

### S2D-008 - Historical collection for the first bounded study is limited to the first calendar day of each month

- Status: RECORDED HUMAN DIRECTION
- Evidence: explicit human instruction to collect only the first day of each month from the Tardis.dev Binance Jersey BTCEUR historical dataset.
- Why it matters: this constraint defines the research sample and must be preserved during any data import, validation, and backtest setup. It does not imply strategy approval or experimental success.

### S2D-009 - The Tardis.dev Binance Jersey BTCEUR first-day-of-month sample is provisionally accepted for continued research under current access and budget constraints

- Status: PROVISIONALLY ACCEPTED WITH OPEN FINAL-ADEQUACY REVIEW
- Evidence: explicit human acceptance of the current research scope under existing data-access and budget constraints; the dataset remains limited to the first calendar day of each month and continues to be separated from the intended Bitvavo Spot execution venue.
- Why it matters: this allows research to proceed without treating the sample as statistically representative or final data-adequacy validated. It also avoids silently authorizing paid access, subscriptions, or any future full-month purchase.
- Important limitations:
  - Sample selection may introduce bias and may not represent the full month.
  - Current acceptance supports continued research only; it does not validate strategy profitability or dataset completeness.
  - The official Tardis exchange metadata confirms `btceur` availability from 2019-10-30 through 2020-11-10, but direct minimal public checks of the exact candidate URLs for first-of-month BTCEUR trades and quotes files returned HTTP 404 in this environment. The exact file-level availability for the sample set is therefore not yet publicly proved for the candidate dates, and the sample remains provisionally accepted pending explicit adequacy review.
  - A future full-month historical acquisition remains an additional human budget decision and is not authorized by the current provisional scope.
  - No API purchase, subscription, or paid download is authorized by this decision.

## Carried-Forward Unresolved Decisions

Sprint 02 carries forward the unresolved first-experiment decisions documented in Sprint 01, including:

- market universe,
- primary timeframe,
- candle timestamp semantics,
- missing and malformed data handling,
- adequacy and statistical validity of the bounded Tardis.dev Binance Jersey BTCEUR first-day-of-month sample,
- parameter grid for `L` and `N`,
- signal-expiry policy,
- execution assumptions,
- cost-model policy,
- first-experiment accounting basis,
- exit-condition precedence,
- out-of-sample methodology,
- implementation stack approval.

These remain unresolved because the authoritative repository documents still do not approve them.

## Review Findings

### F-001 - Sprint 01 can be closed only with a documented scope correction

- Classification: Confirmed contradiction in sprint status versus actual scope
- Evidence: Sprint 01 originally included open experiment-definition tasks while also aiming for documentation-only completion.
- Impact: Closing Sprint 01 without correction would imply completion of work that was not actually done.
- Recommended correction: close Sprint 01 as a documentation-only sprint and explicitly transfer unfinished experiment-definition work.
- Human approval required: no.
- Result: corrected in this sprint.

### F-002 - The roadmap immediate-next-task statement needed updating after Sprint 01 and Sprint 02 review work

- Classification: Confirmed contradiction
- Evidence: the roadmap's next action must reflect the actual repository phase and current review work.
- Impact: a stale next-action statement misstates the current planning sequence.
- Recommended correction: point the immediate next action at Sprint 02 review and resolution of Stage 2 decision blockers.
- Human approval required: no.
- Result: corrected in this sprint.

### F-003 - The technical plan needed repository-state refresh after Sprint 02 creation

- Classification: Confirmed contradiction
- Evidence: repository findings in the technical plan must match the actual docs present in the repo.
- Impact: stale findings reduce trust in the plan and obscure the current documentation baseline.
- Recommended correction: update the repository findings to include Sprint 02 documentation and the current clean Git-backed state.
- Human approval required: no.
- Result: corrected in this sprint.

### F-004 - The roadmap stage ordering remains logically coherent

- Classification: No issue found
- Evidence: `ROADMAP.md` still preserves distinct stages for planning, strategy specification, market data setup, backtesting, validation, paper trading, controlled live testing, evaluation, and scaling.
- Impact: none.
- Human approval required: no.

### F-005 - The technical plan already contains evidence-backed candidates for deferral from the first historical research experiment

- Classification: No issue found
- Evidence: `TECHNICAL_PLAN.md` already marks paper trading, private exchange execution, advanced monitoring, advanced ranking, advanced reconciliation tooling, and deployment automation as later-stage work.
- Impact: none.
- Human approval required: no.

### F-006 - The technical plan still mixes first-experiment requirements with later-stage operational requirements in one document

- Classification: Proposed improvement
- Evidence: `TECHNICAL_PLAN.md` is intentionally comprehensive, but the first-experiment path benefits from a clearer split between minimum historical-research requirements and later paper/live requirements.
- Impact: without that split, early implementation could drift toward premature infrastructure.
- Recommended correction: add a concise scoping clarification inside `TECHNICAL_PLAN.md` without deleting later-stage architecture.
- Human approval required: no.
- Result: corrected in this sprint.

### F-007 - First-experiment freeze remains blocked by unresolved human decisions

- Classification: Unresolved decision
- Evidence: the strategy specification and technical plan both require approval of exchange, timeframe, data semantics, parameter policy, and execution-cost policy before the experiment can be frozen honestly.
- Impact: the first experiment cannot yet be finalized.
- Recommended next step: resolve `S02-101` through `S02-103`.
- Human approval required: yes.

### F-008 - Official Bitvavo evidence supports OHLCV research and limited trade-based execution analysis, but not documented historical spread or order-book-depth analysis

- Classification: Confirmed limitation
- Evidence:
	- official Bitvavo candlestick docs list public OHLCV intervals, limits, timestamp alignment requirements, chronological ordering, and zero-trade gaps,
	- official Bitvavo trades docs list public trade fields and the 24-hour time-window limitation per request,
	- official Bitvavo markets docs list tick size, order-size constraints, decimals, market status, and fee category,
	- official Bitvavo ticker-book docs document current best bid and ask only,
	- no inspected official Bitvavo document established a historical bid/ask or order-book-depth endpoint,
	- a public read-only probe returned BTC-EUR candle data for a historical 24-hour window starting 2024-01-01 and returned historical trades for the same 24-hour window.
- Impact:
	- Bitvavo data is evidenced as sufficient for OHLCV-based signal research,
	- Bitvavo data is evidenced as partially supportive for trade-based execution-cost analysis,
	- historical spread and order-book-depth analysis is not established from current official evidence.
- Recommended correction: document Bitvavo adequacy as partial rather than complete, and keep `S02-101` open until adequacy requirements for the first experiment are explicitly satisfied.
- Human approval required: yes, for acceptance of the data-source adequacy decision.

### F-009 - Bitvavo candlestick completeness behavior is probe-supported but not explicitly established in the inspected candlestick documentation

- Classification: Unresolved question
- Evidence:
	- the inspected Bitvavo candlestick documentation defines candle timestamps and ordering but does not explicitly state whether the latest returned candle may be in progress,
	- a public read-only probe of `BTC-EUR` `1h` candles returned a latest candle whose start timestamp fell within the current hour at query time.
- Impact: first-experiment anti-lookahead handling must treat the latest returned candle as potentially incomplete unless finalization behavior is otherwise confirmed.
- Recommended next step: record this as a Bitvavo-specific experiment constraint and require implementation or replay logic to exclude the most recent still-forming candle unless completeness is explicitly proven.
- Human approval required: no for the constraint itself, yes if later policy changes rely on a stronger assumption.

### F-010 - A 5-minute primary timeframe remains a provisional candidate for the first historical SPOT experiment, not a comparative superiority claim

- Classification: Proposed recommendation, not approved
- Evidence:
  - Bitvavo candlestick docs list valid intervals including `1m`, `5m`, `15m`, `30m`, `1h`, `2h`, `4h`, `6h`, `8h`, `12h`, `1d`, `1W`, and `1M`.
  - Bitvavo docs state that candle timestamps are Unix milliseconds and that the `timestamp` is the start time of the candle interval.
  - Bitvavo docs state that candle data are returned newest-to-oldest and that a no-trade interval may appear as a gap in data flow rather than a fabricated zero-volume candle.
  - The project strategy specification already defines a minimal two-candle bullish rejection hypothesis and requires completed-candle validation.
  - The currently inspected documentation does not include comparative evidence that `5m` is superior to `1m` or other supported intervals.
- Impact:
  - `5m` is a defensible provisional default only because it is compatible with the project’s short-horizon spot research objective and is less sensitive to microstructure noise than `1m`.
  - It is not yet a proven superior timeframe, and comparative performance data are still required before calling it a justified default.
- Recommended proposal:
  - Treat `5m` as the provisional primary timeframe for the first historical SPOT experiment only.
  - Treat each candle timestamp as the interval start time in UTC milliseconds.
  - Evaluate only completed candles; do not evaluate any still-forming bar.
  - Use contiguous completed-candle context only; reject signals when required candles are missing, duplicated, or ambiguous.
  - Require a stable replay sort order by `(timestamp, symbol)` and reject any signal that depends on look-ahead or on data that was unavailable at the decision point.
  - Continue to regard the 5-minute recommendation as provisional until human approval and empirical evidence justify a stronger preference.
- Human approval required: yes. This recommendation remains proposed, not approved.

### F-011 - Bitvavo public data supports a bounded historical OHLCV and trade-based research experiment, but not a fully evidenced historical spread-depth cost model

- Classification: PASS WITH LIMITATIONS
- Evidence:
  - Public `GET /v2/BTC-EUR/candles?interval=5m&start=...&end=...&limit=10` returned 10 historical 5-minute candle records for a 2024-01-01 sample window.
  - Public `GET /v2/BTC-EUR/trades?start=...&end=...&limit=10` returned 10 historical trade records with `timestamp`, `amount`, `price`, and `side`.
  - Public `GET /v2/markets?market=BTC-EUR` returned `status`, `minOrderInBaseAsset`, `minOrderInQuoteAsset`, `quantityDecimals`, `tickSize`, `maxOpenOrders`, and `feeCategory`.
  - Public `GET /v2/ticker/book?market=BTC-EUR` returned current best bid/ask snapshot fields only; it did not provide a documented historical spread-depth dataset.
  - The inspected official docs do not publish a historical order-book-depth endpoint or a historical spread-history endpoint for Bitvavo public data.
- Impact:
  - Bitvavo public data is supportable for a minimal historical research experiment based on OHLCV and trade records, including basic market metadata and fee-category awareness.
  - It is not sufficient to claim a fully evidenced historical spread-depth or order-book-depth execution-cost model without additional assumptions or a separate source.
- Recommended next step:
  - Keep `S02-101` open until the project explicitly accepts the limitation that historical spread-depth evidence is unavailable from the current public source and that the first experiment will rely on a bounded OHLCV/trade-based study rather than a full order-book cost model.
- Human approval required: yes. This is a limitation-based adequacy assessment, not an approval of the full first-experiment design.

### F-012 - The missing 2024-01-01 05:35:00-05:40:00 UTC candle is consistent with a documented no-trade gap, not a confirmed candle-data inconsistency

- Classification: No-trade gap consistent with Bitvavo semantics; completeness caveat remains
- Evidence:
  - Official Bitvavo docs for candles state: "Data is returned when trades are made in the interval represented by that candlestick. If no trades occur you see a gap in data flow - zero trades are represented by zero candlesticks."
  - Public read-only request: `GET /v2/BTC-EUR/trades?start=1704087300000&end=1704087600000&limit=1000`
  - Exact interval queried: `2024-01-01T05:35:00Z` to `2024-01-01T05:40:00Z`
  - Response count: 0 trade records.
  - Adjacent-window checks: `2024-01-01T05:30:00Z` to `2024-01-01T05:35:00Z` returned 4 trades; `2024-01-01T05:40:00Z` to `2024-01-01T05:45:00Z` returned 18 trades.
  - The exact 05:35 UTC boundary window has no trades and no trade records at either `start` or `end` boundary.
- Impact:
  - This is consistent with the documented Bitvavo behavior for a zero-trade interval and is not evidence of a confirmed candle-data inconsistency.
  - It remains conservative to treat the missing candle as an ambiguous but no-trade-compatible gap unless the source explicitly guarantees zero-trade feed completeness for a given interval.
- Recommended next step:
  - Keep `S02-101` open.
  - Continue to require explicit missing-candle handling and reject silent fill or look-ahead assumptions.
  - Do not claim full historical data adequacy based on this single window alone.
- Human approval required: yes, for any closure decision after more evidence is gathered.

## Next Actions

- Resolve the remaining adequacy and approval questions in `S02-101`, `S02-102`, and `S02-103` to enable the first bounded experiment specification.
- Resolve `S02-104` before any later implementation planning that depends on provisional coding of the proposed strategy.