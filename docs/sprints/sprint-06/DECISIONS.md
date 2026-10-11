# Sprint 06 - Decisions and Backtest Boundaries

## D-06-001 - Strategy outputs are proposals, not executions

- Status: `REQUIRED`
- Evidence: `STRATEGY_SPECIFICATION.md`, `TECHNICAL_PLAN.md`.
- Why it matters: signals remain separate from risk approval and execution.

## D-06-002 - The research-only backtest must stay within the bounded historical sample

- Status: `APPROVED BOUNDARY`
- Evidence: `ROADMAP.md`, `S03-006`.
- Why it matters: the project does not approve larger or full-month data scope without a separate decision.

## D-06-003 - Parameter tuning must be disciplined and not a hidden optimization loop

- Status: `REQUIRED`
- Evidence: `STRATEGY_SPECIFICATION.md`, `TECHNICAL_PLAN.md`.
- Why it matters: the holdout set cannot be reused for parameter selection.

## D-06-004 - Backtest success is not strategy success

- Status: `APPROVED WARNING`
- Evidence: `PROJECT_DEFINITION.md` and `ROADMAP.md`.
- Why it matters: historical performance remains a research artifact until realistic validation, paper trading, and any required human approvals are satisfied.
