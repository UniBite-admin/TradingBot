# Sprint 05 - Candle Pipeline and Deterministic Replay

## Sprint Status

- Identifier: Sprint 05
- Status: OPEN - approved for bounded historical research implementation only
- Scope: stage-gated historical research implementation only
- Implementation state: S05-001 contract and policy are implemented and validated; S05-002 trade-based OHLCV builder is implemented and passing tests; S05-003 empty-gap rejection is enforced; S05-004 deterministic replay kernel is implemented and passing tests; S05-005 candle validation tests are passing; S05-006 gate is documented and enforced within the approved research scope
- Live-trading state: Not allowed

## Objective

Implement the deterministic candle pipeline and replay kernel required to convert raw trade data into committed, time-aligned OHLCV evidence without look-ahead or silent data synthesis.

## Scope

Sprint 05 covers:

- canonical trade-to-candle conversion,
- completed-candle eligibility,
- empty-interval and missing-gap rejection,
- deterministic replay ordering,
- anti-lookahead and data-quality enforcement,
- evidence gate for the `S03-102` implementation contract.

## Dependencies

- `S03-101` data-adequacy status remains a blocker for broader use.
- `S03-102` candle-contract approval remains the main stage gate.
- Sprint 04 output: provenance and canonical validation.

## Explicit exclusions

- no live or paper execution,
- no strategy approval,
- no scaling,
- no exchange private-order integration.

## Source references

- `STRATEGY_SPECIFICATION.md`
- `TECHNICAL_PLAN.md`
- `ROADMAP.md`
- `docs/sprints/sprint-03/DECISIONS.md`
- `docs/sprints/sprint-04/README.md`
