# Sprint 06 - Strategy, Features, and Backtesting

## Sprint Status

- Identifier: Sprint 06
- Status: OPEN - bounded historical research only
- Scope: historical research and deterministic backtesting only
- Implementation state: S06-001 feature and signal contract implemented and validated; S06-002 local-structure signal generation implemented and passing tests; S06-003 deterministic strategy engine implemented and tested; S06-004 replay-backed historical backtest harness implemented and tested; remaining Stage 6 items stay behind the bounded-research gate
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
