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

### S2D-006 - Bitvavo Spot is the intended trading venue

- Status: APPROVED HUMAN DECISION
- Evidence: explicit human instruction in Sprint 02 Bitvavo data-adequacy review.
- Why it matters: Sprint 02 no longer needs to treat exchange venue selection itself as unresolved.

### S2D-007 - Bitvavo's own public market-data endpoints are the preferred initial research source, subject to adequacy verification

- Status: APPROVED HUMAN DIRECTION WITH UNRESOLVED ADEQUACY
- Evidence: explicit human instruction in Sprint 02 Bitvavo data-adequacy review.
- Why it matters: Sprint 02 should evaluate Bitvavo-first data adequacy before considering any other source.

## Carried-Forward Unresolved Decisions

Sprint 02 carries forward the unresolved first-experiment decisions documented in Sprint 01, including:

- market universe,
- primary timeframe,
- candle timestamp semantics,
- missing and malformed data handling,
- authoritative Bitvavo public data adequacy and usage policy,
- parameter grid for `L` and `N`,
- signal-expiry policy,
- execution assumptions,
- cost-model policy,
- first-experiment accounting basis,
- exit-condition precedence,
- historical-data adequacy and out-of-sample methodology,
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

## Next Actions

- Resolve the remaining adequacy and approval questions in `S02-101`, `S02-102`, and `S02-103` to enable the first bounded experiment specification.
- Resolve `S02-104` before any later implementation planning that depends on provisional coding of the proposed strategy.