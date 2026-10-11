# Sprint 06 - Strategy, Features, and Backtesting

## Sprint Status

- Identifier: Sprint 06
- Status: OPEN
- Scope: historical research and deterministic backtesting only
- Implementation state: conditional on `S05-001` to `S05-006` passing evidence gates
- Live-trading state: Not allowed

## Objective

Translate the approved bounded strategy rules into a deterministic feature and backtest pipeline that can replicate historical outcomes under explicit data and execution assumptions.

## Scope

Sprint 06 covers:

- feature and lookback definitions,
- strategy-rule implementation,
- replay-safe signal generation,
- backtest infrastructure,
- chronological split and parameter discipline,
- reproduction and artifact collection.

## Explicit exclusions

- no live trading,
- no private exchange integration,
- no direct scaling,
- no assumption that a positive backtest proves profitability.

## Dependencies

- completion of Sprint 05 evidence gate,
- explicit human approval of the bounded experiment boundary,
- preserved data integrity and replay semantics from prior sprints.

## Source references

- `STRATEGY_SPECIFICATION.md`
- `TECHNICAL_PLAN.md`
- `ROADMAP.md`
- `docs/sprints/sprint-03/DECISIONS.md`
- `docs/sprints/sprint-05/README.md`
