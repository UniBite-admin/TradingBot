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

## Carried-Forward Unresolved Decisions

Sprint 02 carries forward the unresolved first-experiment decisions documented in Sprint 01, including:

- exchange and authoritative market-data source,
- market universe,
- primary timeframe,
- candle timestamp semantics,
- missing and malformed data handling,
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

## Next Actions

- Resolve `S02-101`, `S02-102`, and `S02-103` to enable the first bounded experiment specification.
- Resolve `S02-104` before any later implementation planning that depends on provisional coding of the proposed strategy.