# Sprint 05 - Action Items

Status vocabulary: `PROPOSED`, `OPEN`, `BLOCKED`, `IMPLEMENTED`, `TESTED`, `VALIDATED`, `DONE`

| ID | Title | Work to perform | Deliverable / result | Source references | Dependencies | Verification | Acceptance criteria | Evidence | Status | Blockers |
|---|---|---|---|---|---|---|---|---|---|---|
| S05-001 | Freeze the 5-minute candle contract | Finalize the interval, timezone, bucket semantics, and completed-bar policy for the bounded research version. | Human-approved implementation contract reflected in project docs. | `STRATEGY_SPECIFICATION.md`, `TECHNICAL_PLAN.md`, `S03-102` | S04-003 | Inspect the contract and confirm it is consistent with source docs. | Every bucket and time boundary is explicit and reproducible. | contract note + review record | BLOCKED | `S03-102` |
| S05-002 | Build trade-based OHLCV builder | Convert raw trade events into per-bucket OHLCV with open/high/low/close/volume semantics. | `OHLCV` records or equivalent output for trade-only bars. | `STRATEGY_SPECIFICATION.md`, `S03-006`, `S03-102` | S04-003, S05-001 | Run deterministic bucket fixtures. | Open/close/high/low/volume match the documented contract. | test output + validation log | OPEN | `S03-102` |
| S05-003 | Enforce completed-bar and empty-gap policy | Reject still-forming, ambiguous, or missing intervals rather than synthesizing them. | Evidence of explicit invalidation for incomplete or empty windows. | `STRATEGY_SPECIFICATION.md`, `S03-102` | S05-002 | Run gap, empty interval, and partial-candle fixtures. | No silent fill or backfill occurs. | rejection log and tests | OPEN | `S03-102` |
| S05-004 | Create replay kernel for deterministic chronology | Build an event-driven replay loop that preserves order, data availability, and anti-lookahead constraints. | Replay history with explicit data state at each time step. | `TECHNICAL_PLAN.md`, `STRATEGY_SPECIFICATION.md` | S04-003, S05-002 | Run identical inputs twice and compare the output. | Deterministic output for identical inputs and config. | replay artifact | PROPOSED | needs contract approval |
| S05-005 | Implement candle validation tests | Add tests for UTC boundaries, duplicate timestamps, exact duplicates, missing intervals, and incomplete current candles. | A complete test set covering the candle contract. | `TECHNICAL_PLAN.md`, `STRATEGY_SPECIFICATION.md` | S05-002, S05-003 | Execute the candle test suite. | No validation gap remains untested. | pytest result + coverage notes | PROPOSED | `S03-102` |
| S05-006 | Record the implementation gate | Ensure the project cannot move beyond research-only implementation without passing the candle contract tests. | Stage gate and review record. | `ROADMAP.md`, `PROJECT_DEFINITION.md`, `S03-102` | S05-005 | Review gate against Stage 5 and Stage 6 requirements. | Progression requires tested candle validity evidence. | gate record | OPEN | requires human approval |

## Human decision tasks

| ID | Title | Work to perform | Output | Source references | Dependencies | Verification | Acceptance | Status | Blockers |
|---|---|---|---|---|---|---|---|---|---|
| S05-101 | Approve candle implementation verification | Decide whether the documented candle contract is sufficiently accepted to proceed with implementation and testing. | Human approval or explicit blocker for `S03-102`. | `S03-102`, `STRATEGY_SPECIFICATION.md`, `TECHNICAL_PLAN.md` | S04-003 | Review the contract, implementation, and test evidence together. | The contract is explicit, approved, and verifiable. | BLOCKED | human approval required |
