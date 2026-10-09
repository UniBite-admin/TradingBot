# Trading Bot - Authoritative Roadmap

## Purpose

This roadmap defines the approved project sequence and the current blocked decisions required before implementation begins.

This file is the authoritative roadmap for the repository.

## Current Status

- Stage: Definition and planning.
- Implementation status: Not started.
- Strategy status: Specification drafted and pending human review; not approved.
- Exchange status: Not approved.
- Live trading status: Not allowed.

## Approved Workflow

The project advances only through the following sequence:

1. Project definition and governance.
2. Technical planning.
3. Strategy specification.
4. Market data and research environment setup.
5. Backtesting implementation.
6. Validation with realistic costs and constraints.
7. Paper trading.
8. Controlled small live test.
9. Evaluation.
10. Controlled scaling only if evidence supports it.

## Stage Gates

### Stage 1 - Project definition and governance

Status: Complete.

Exit evidence:

- Project mission, boundaries, and operating principles documented.
- Capital protection and no-assumptions governance documented.
- Authoritative definition and roadmap created.

### Stage 2 - Technical planning

Status: In progress.

Objective:

- Define the minimum system architecture required for research and controlled execution.

Required decisions:

- Exchange.
- Market universe selection method.
- Candle intervals.
- Data sources.
- Initial language and runtime.
- Storage requirements.
- Logging and experiment tracking approach.

Required outputs:

- Technical architecture outline.
- Component boundaries.
- Initial repository layout.
- Environment and secret-handling rules.

Current repository evidence:

- `TECHNICAL_PLAN.md` records the proposed comprehensive technical plan and implementation roadmap for review.

Blocked by:

- Human approval of the unresolved technical choices listed above.

### Stage 3 - Strategy specification

Status: In progress.

Objective:

- Define one explicit candlestick-based strategy hypothesis without silent parameters.

Required decisions:

- Entry conditions.
- Exit conditions.
- Invalidation rules.
- Timeframe.
- Candidate assets or asset-selection rules.
- Position sizing method.
- Risk constraints.

Required outputs:

- Testable strategy specification.
- Clear distinction between hypothesis, approved rule, implemented rule, and validated result.

Current repository evidence:

- `STRATEGY_SPECIFICATION.md` records the proposed candlestick strategy specification for review.

Blocked by:

- Human approval of a concrete strategy specification.

### Stage 4 - Market data and research environment setup

Status: Not started.

Objective:

- Build the minimum data pipeline required to collect and inspect historical candlestick data for approved markets.

Required outputs:

- Verified data ingestion path.
- Reproducible research environment.
- Initial data quality checks.

### Stage 5 - Backtesting implementation

Status: Not started.

Objective:

- Implement a reproducible backtest for the approved strategy.

Required outputs:

- Strategy evaluation against historical data.
- Versioned configurations and run metadata.
- Reproducible result artifacts.

### Stage 6 - Validation with realistic costs and constraints

Status: Not started.

Objective:

- Determine whether the strategy remains viable after fees, spread, slippage, latency, liquidity limits, and order constraints.

Required outputs:

- Validation report with explicit assumptions.
- Failure analysis where profitability degrades under realistic execution.

### Stage 7 - Paper trading

Status: Not started.

Objective:

- Verify operational behavior without risking capital.

Required outputs:

- Decision logs.
- Order simulation evidence.
- Operational incident log.

### Stage 8 - Controlled small live test

Status: Not started.

Objective:

- Run a tightly constrained live spot test only after paper-trading evidence supports it.

Hard preconditions:

- Spot-only exchange configuration.
- No withdrawal permission on API keys.
- Approved numeric risk limits.
- Emergency stop tested.
- Human approval for live deployment.

### Stage 9 - Evaluation

Status: Not started.

Objective:

- Compare research, paper, and live results and decide whether the strategy has repeatable positive expectancy.

### Stage 10 - Controlled scaling

Status: Not started.

Objective:

- Scale only if evidence supports it and risk controls remain effective.

## Known Facts

- The project is for cryptocurrency spot trading only.
- The initial capital ceiling is EUR 50.
- The first live test should remain very small and controlled.
- The system must prioritize reproducibility, risk control, and honest evaluation over speed of deployment.

## Unknowns Requiring Human Decision

- Which exchange will be used.
- Which markets will be monitored.
- Which candle intervals will be evaluated.
- Which exact strategy hypothesis will be tested first.
- Which numerical risk limits will govern live behavior.
- Which implementation stack will be used.

## Immediate Next Task

Review and reconcile `TECHNICAL_PLAN.md` against the current repository state, then resolve the implementation-blocking Stage 2 decisions recorded there and in Sprint 01 documentation before implementation begins.