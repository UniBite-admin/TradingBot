# Sprint 07 - Action Items

Status vocabulary: `PROPOSED`, `OPEN`, `BLOCKED`, `IMPLEMENTED`, `TESTED`, `VALIDATED`, `DONE`

| ID | Title | Work to perform | Deliverable / result | Source references | Dependencies | Verification | Acceptance criteria | Evidence | Status | Blockers |
|---|---|---|---|---|---|---|---|---|---|---|
| S07-001 | Define realistic cost model | Separate fee, spread, slippage, latency, liquidity, fill probability, and minimum-order constraints. | A documented cost-model specification with explicit assumptions. | `PROJECT_DEFINITION.md`, `STRATEGY_SPECIFICATION.md`, `TECHNICAL_PLAN.md` | S06-004 | Compare the model against the project definition and stage gates. | No hidden or mixed assumptions. | cost-model document | OPEN | requires human approval |
| S07-002 | Implement risk-control boundary | Define position-size, maximum open exposure, rejection conditions, and emergency-stop policy. | Risk engine with explicit deny-by-default behavior. | `PROJECT_DEFINITION.md`, `TECHNICAL_PLAN.md` | S06-003 | Verify reject conditions and state transitions. | The risk engine can block without strategy changes. | risk decision logs | PROPOSED | no live approval |
| S07-003 | Build accounting and ledger | Record trades, fees, unrealized and realized P&L, and unresolved-accounting flags. | Reconstructable ledger from domain events. | `TECHNICAL_PLAN.md` | S07-002 | Use deterministic fixture cases for partial fills and fee splits. | A trade outcome is reconstructible from recorded evidence. | ledger artifacts | PROPOSED | needs validation model |
| S07-004 | Run realistic validation stress tests | Re-run the strategy under conservative cost assumptions and failure cases. | Validation report that distinguishes realistic cost drag from optimistic backtests. | `ROADMAP.md`, `TECHNICAL_PLAN.md`, `PROJECT_DEFINITION.md` | S07-001, S07-003 | Run the same strategy under conservative assumptions and compare outputs. | Profitability claims are not accepted without explicit evidence. | validation report | OPEN | cost-model approval |
| S07-005 | Review final validation gate | Establish the evidence required before paper trading may even be considered. | Final validation gate narrative and review checklist. | `ROADMAP.md`, `PROJECT_DEFINITION.md` | S07-004 | Inspect the gate against the project’s staged validation flow. | No stage is skipped. | gate record | OPEN | human approval |

## Human decision tasks

| ID | Title | Decision to make | Output | Source refs | Dependencies | Verification | Acceptance | Status | Blockers |
|---|---|---|---|---|---|---|---|---|---|
| S07-101 | Approve realistic validation model | Decide whether the project may use current public fee and liquidity assumptions as a realistic validation model or must keep validation as a stress-test only. | Human-approved validation boundary. | `PROJECT_DEFINITION.md`, `STRATEGY_SPECIFICATION.md`, `TECHNICAL_PLAN.md` | S07-001 | Validate the model against the evidence and project rules. | Validation stays honest about realism and uncertainty. | BLOCKED | human approval required |
