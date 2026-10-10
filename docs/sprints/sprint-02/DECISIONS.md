# Sprint 02 - Decisions And Review Findings

This file records decisions already supported by authoritative repository documents, unresolved decisions carried forward into Sprint 02, and review findings from the roadmap and technical-plan audit.

## Sprint Closure Decision

- Status: CLOSED AS A DOCUMENTATION AND DECISION-GOVERNANCE SPRINT
- Evidence: all unresolved first-experiment evidence gaps, blocked specification work, and implementation-governance questions have been transferred to Sprint 03 with traceable source/destination references.
- Why it matters: Sprint 02 satisfied its review and planning scope without silently converting provisional research decisions into approved strategy, implementation, paper-trade, or live-trade approvals.
- Transfer mapping:
  - `S02-006` -> `S03-006`
  - `S02-007` -> `S03-007`
  - `S02-101` -> `S03-101`
  - `S02-102` -> `S03-102`
  - `S02-104` -> `S03-104`
- Explicit non-claims:
  - Sprint 02 closure does not approve a profitable strategy.
  - Sprint 02 closure does not prove positive expectancy.
  - Sprint 02 closure does not authorize implementation beyond the existing approvals.
  - Sprint 02 closure does not authorize paper trading or live trading.

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
- Why it matters: this resolves the venue choice but does not resolve the remaining historical-data adequacy question for the first bounded experiment.

### Local Evidence Snapshot (working tree only, not committed repository truth)

- Local working-tree evidence currently available: the Tardis audit run reports `12/12` canonical datasets as passing, and the focused HSRA/Tardis pytest command reports `18` passing tests.
- This is uncommitted evidence from the current working tree only. It does not upgrade the provisional Tardis sample to final adequacy, does not prove statistical representativeness, and does not authorize strategy implementation or live trading.

### S2D-007 - The bounded historical research source for the first study is Tardis.dev Binance Jersey BTCEUR quotes and trades

- Status: RECORDED HUMAN DIRECTION WITH OPEN ADEQUACY REVIEW
- Evidence: explicit human decision to use Tardis.dev historical data for Binance Jersey BTCEUR, delivered as daily `.csv.gz` files and limited to the first calendar day of each month only.
- Why it matters: the research sample is intentionally separate from the live execution venue and must be reviewed for adequacy, statistical limits, and anti-lookahead compliance before any experiment approval.

### S2D-008 - Historical collection for the first bounded study is limited to the first calendar day of each month

- Status: RECORDED HUMAN DIRECTION
- Evidence: explicit human instruction to collect only the first day of each month from the Tardis.dev Binance Jersey BTCEUR historical dataset.
- Why it matters: this constraint defines the research sample and must be preserved during any data import, validation, and backtest setup. It does not imply strategy approval or experimental success.

### S2D-009 - The Tardis.dev Binance Jersey BTCEUR first-day-of-month sample is provisionally accepted for continued research under current access and budget constraints

- Status: PROVISIONALLY ACCEPTED FOR BOUNDED EXPLORATORY SIGNAL RESEARCH ONLY
- Evidence: explicit human acceptance of the current research scope under existing data-access and budget constraints; the dataset remains limited to the first calendar day of each month and continues to be separated from the intended Bitvavo Spot execution venue.
- Why it matters: this allows limited signal-research to proceed without treating the sample as statistically representative, execution-realistic, or sufficient for profitability validation. It also avoids silently authorizing paid access, subscriptions, or any future full-month purchase.
- Important limitations:
  - Sample selection may introduce bias and may not represent the full month.
  - This scope accepts the sample only for bounded exploratory signal research under current budget and access constraints; it does not validate strategy profitability, realistic fill costs, historical spread-depth adequacy, or dataset completeness.
  - The local integrity audit confirms file-level coherence, hash integrity, and provenance coherence for the currently available canonicalized sample; it does not prove statistical adequacy or execution realism.
  - The official Tardis exchange metadata confirms `btceur` availability from 2019-10-30 through 2020-11-10, but direct minimal public checks of the exact candidate URLs for first-of-month BTCEUR trades and quotes files returned HTTP 404 in this environment. The exact file-level availability for the sample set is therefore not yet publicly proved for the candidate dates, and the sample remains provisionally accepted only for bounded exploratory research pending explicit adequacy review.
  - A future full-month historical acquisition remains an additional human budget decision and is not authorized by the current provisional scope.
  - No API purchase, subscription, or paid download is authorized by this decision.
  - This does not establish realistic Bitvavo historical spread, order-book depth, or fill costs, and it does not authorize paper trading or live trading.

### S2D-010 - Execution-cost realism and profitability validation remain separate acceptance gates from the bounded exploratory-signal-research decision

- Status: APPROVED GATE SEPARATION
- Evidence: `PROJECT_DEFINITION.md`, `STRATEGY_SPECIFICATION.md`, `TECHNICAL_PLAN.md`, and the human-approved bounded-research direction for Sprint 02.
- Why it matters: the approved bounded research scope permits exploratory signal work under the current data and budget constraints, but it does not replace the later execution-cost and profitability validation gates.
- Explicit non-claims:
  - The sample is not approved as statistically representative.
  - The sample is not approved as sufficient for profitability validation.
  - The project is not approved to invent or assume a realistic Bitvavo historical fill model.
  - The current scope does not authorize paper trading, strategy implementation, or live trading.
  - Historical spread, order-book depth, latency, slippage, and fill-cost realism remain open until a separate evidence-based acceptance gate is satisfied.

### S2D-011 - The 5-minute timeframe is approved as the primary timeframe for the first bounded historical research experiment only

- Status: APPROVED HUMAN DECISION
- Evidence: explicit human approval recorded in Sprint 02 review and project planning.
- Why it matters: this approves the 5-minute primary timeframe for the first bounded historical research experiment only. It does not establish that 5m is optimal, profitable, statistically representative, or suitable for live trading.
- Scope and non-claims:
  - Approved for the first bounded historical research experiment only.
  - This does not authorize implementation, paper trading, or live trading.
  - This does not claim 5m is superior to other supported intervals.
  - This does not approve any specific execution-cost model, fill assumptions, or profitability claim.
  - This does not imply that the first experiment is frozen, validated, or ready to scale.
- Remaining open items:
  - fixed UTC interval semantics, if the project chooses to formalize them,
  - whether timestamps are treated as interval start or close,
  - completed-candle-only policy,
  - explicit handling of missing or no-trade intervals,
  - final incomplete-candle handling,
  - later approval of parameter-grid, cost-model, and data-validity policy.
- Human approval required: the 5m timeframe approval is recorded as human-approved. The detailed candle-contract semantics remain proposal-level and must be treated as separate from the timeframe approval unless they are later implemented and verified.

### S2D-012 - S02-103 research boundaries and bounded exploratory parameter policy

- Status: DELEGATED BOUNDED RESEARCH DECISION; FULL PARAMETER APPROVAL REMAINS BLOCKED BY MISSING EVIDENCE
- Evidence: `TECHNICAL_PLAN.md`, `STRATEGY_SPECIFICATION.md`, and the delegated project-lead research direction for Sprint 02 task `S02-103`.
- Why it matters: this records the bounded research decisions for the first historical signal-only study without moving those decisions into approved profitability or live-trading authorization.
- Decision record:
  - Research boundary: bounded historical signal-only research may proceed before execution-cost realism is established, provided it is explicitly labeled as signal-only and not as proof of profitability, positive net expectancy, representative market behavior, or executable real-world fills.
  - Parameter candidates: `L ∈ {8, 12, 16}`, `N ∈ {4, 8, 12}`, and `signal_expiry ∈ {2, 4}` are recorded as proposed candidates for a bounded exploratory study only. These are not validated optimal parameters and must not be described as proven or generally approved strategy settings. They are candidate values to review, not a frozen winner.
  - Volume filter: the optional volume filter is excluded from the initial baseline experiment and must be treated as a separate experimental variant only if the data quality and research evidence justify it later.
  - Cost sensitivity: any fee, spread, slippage, latency, or fill assumptions must be explicitly labeled as assumptions or stress-test inputs and must not be represented as measured historical Bitvavo execution costs. The available Binance Jersey data does not establish historical Bitvavo execution quality.
  - No live authorization: these bounded research decisions authorize neither real-money trading nor automatic paper/live execution or scaling. The project's explicit approval gate remains in force.
- Explicit blockers that remain unresolved:
  - exact chronological holdout dates or split boundaries before sample adequacy is reviewed,
  - candle construction, finalization, and missing/no-trade interval handling unless these are already specified and verified,
  - a cost model claimed to represent actual Bitvavo fills,
  - any claim that the current sample is representative or sufficient to demonstrate profitability.
- Human approval required: the delegated research decision is recorded as a bounded project-lead decision for initial signal research only. Any broader approval of a specific parameter set, cost model, or profitability claim remains blocked pending evidence and explicit human approval.

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

### F-010 - 5-minute primary timeframe is approved for the first bounded historical research experiment only; detailed candle semantics remain proposal-level unless implemented and verified

- Classification: Approved timeframe; detailed candle semantics remain proposed rather than approved implementation contract
- Evidence:
  - The project now records `5m` as the approved primary timeframe for the first bounded historical research experiment only.
  - Bitvavo candlestick docs list valid intervals including `1m`, `5m`, `15m`, `30m`, `1h`, `2h`, `4h`, `6h`, `8h`, `12h`, `1d`, `1W`, and `1M`.
  - Bitvavo docs state that candle timestamps are Unix milliseconds and that the `timestamp` is the start time of the candle interval.
  - Bitvavo docs state that candle data are returned newest-to-oldest and that a no-trade interval may appear as a gap in data flow rather than a fabricated zero-volume candle.
  - The project strategy specification already defines a minimal two-candle bullish rejection hypothesis and requires completed-candle validation.
  - The currently inspected documentation still does not establish comparative superiority of `5m` over `1m` or other supported intervals.
- Impact:
  - The 5-minute timeframe is approved as the primary timeframe for the first bounded historical research experiment only.
  - This approval does not claim that `5m` is optimal, profitable, or statistically representative.
  - The detailed candle contract remains proposal-level unless and until it is implemented and verified in code and tests.
- Recommended treatment:
  - Keep the approved 5m timeframe as the first bounded historical research default.
  - Keep the following candle-contract rules as proposed policy only unless they are already implemented and validated: UTC-aligned fixed intervals, timestamp as interval start, completed-candle-only evaluation, explicit missing/no-trade gap handling, and final incomplete-candle handling.
  - Do not treat those detailed candle semantics as approved operational requirements merely because the timeframe is approved.
- Human approval required: the timeframe approval is already recorded. Any further tightening of the candle contract must remain separate from the timeframe approval and must be treated as an implementation decision after code and test verification.

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