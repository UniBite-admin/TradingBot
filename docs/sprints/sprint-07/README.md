# Sprint 07 - Realistic Validation, Risk, and Accounting

## Sprint Status

- Identifier: Sprint 07
- Status: OPEN
- Scope: validation and risk controls before paper trading
- Implementation state: conditional on historical replay and deterministic data
- Live-trading state: Not allowed

## Objective

Validate the strategy under realistic cost and operational constraints and ensure the risk engine, position model, and accounting layer remain distinct and auditable.

## Scope

Sprint 07 covers:

- realistic fee, spread, slippage, and latency assumptions,
- execution cost model review,
- risk controls and position state handling,
- accounting and ledger reconstruction,
- decision records that separate research and validation results.

## Explicit exclusions

- no live trading,
- no exchange credential activation,
- no deployment automation,
- no scaling.

## Dependencies

- Sprint 06 backtest harness and strategy output,
- human approval for any cost-model assumptions that are intended to represent real execution conditions,
- explicit risk constraints from project definition.

## Source references

- `PROJECT_DEFINITION.md`
- `ROADMAP.md`
- `TECHNICAL_PLAN.md`
- `STRATEGY_SPECIFICATION.md`
- `docs/sprints/sprint-06/README.md`
