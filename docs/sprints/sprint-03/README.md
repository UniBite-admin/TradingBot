# Sprint 03 - First-Experiment Evidence and Handoff

## Sprint Status

- Identifier: Sprint 03
- Status: CLOSED
- Closure mode: evidence-backed completion of the transferred Sprint 02 issues under the bounded research-only scope
- Scope state: Resolved and recorded within the approved bounded-research boundary
- Implementation state: The 5-minute OHLCV contract is implemented and verified for the current research scope; broader strategy, paper, and live-trading approval remain explicitly out of scope
- Strategy approval state: Not approved
- Live-trading state: Not allowed
- Research specification state: FROZEN for bounded exploratory signal research only; not a validation of implementation, profitability, or execution realism
- Backlog snapshot: `OPEN=0`, `IN_PROGRESS=0`, `DONE=5` from the current task register in [ACTION_ITEMS.md](ACTION_ITEMS.md)

## Closure Decision

Sprint 03 is closed as a bounded evidence-and-governance sprint. The transferred issues were resolved with explicit documentation and implementation evidence only within the research scope:

- the sample adequacy is recorded as provisional and bounded,
- the OHLCV contract is recorded and verified for the current research-bound implementation,
- the first bounded experiment remains explicit about its assumptions and evidence limits,
- no broader approval is inferred from the evidence.

## Relevant Sprint Records

- [ACTION_ITEMS.md](ACTION_ITEMS.md)
- [DECISIONS.md](DECISIONS.md)
- [ACCEPTANCE_CRITERIA.md](ACCEPTANCE_CRITERIA.md)
- [S03-102-OHLCV-VERIFICATION.md](S03-102-OHLCV-VERIFICATION.md)

## Objective

Continue the unresolved first-experiment evidence work transferred from Sprint 02 without silently promoting provisional research assumptions into approved strategy, implementation, paper, or live-trading requirements.

## Scope

Sprint 03 covers:

- historical-data adequacy and representativeness review for the bounded Tardis.dev Binance Jersey BTCEUR sample,
- verification of candle construction, timestamps, completed-candle rules, and missing/no-trade intervals,
- chronological research split and holdout-boundary definition,
- realistic execution-cost evidence and clear cost-model requirements,
- the blocked first-experiment specification and any dependent work,
- any remaining unresolved Sprint 02 decisions and acceptance requirements.

## Explicit Exclusions

Sprint 03 does not include:

- implementation of application code,
- strategy-rule changes without approval,
- paper-trading activation,
- live-trading activation,
- invention of exchange choices, assets, timeframes, parameters, risk limits, or cost assumptions.

## Handover From Sprint 02

The unresolved items transferred from Sprint 02 are:

| Source Sprint 02 ID | Destination Sprint 03 ID | Reason |
|---|---|---|
| S02-006 | S03-006 | First bounded experiment specification remains blocked by unresolved evidence gates. |
| S02-007 | S03-007 | State-separation requirements remain to be preserved in the first experiment definition. |
| S02-101 | S03-101 | Historical-data adequacy and representativeness remain unresolved. |
| S02-102 | S03-102 | Candle semantics and timestamp/completed-candle rules remain unresolved. |
| S02-104 | S03-104 | Implementation-governance decision remains open. |

The bounded `S02-103` policy decision remains part of the research boundary and must be treated as a policy note, not as a profitability or live-trading approval.

## Dependencies

Sprint 03 depends on:

- [PROJECT_DEFINITION.md](../../../PROJECT_DEFINITION.md)
- [README.md](../../../README.md)
- [ROADMAP.md](../../../ROADMAP.md)
- [STRATEGY_SPECIFICATION.md](../../../STRATEGY_SPECIFICATION.md)
- [TECHNICAL_PLAN.md](../../../TECHNICAL_PLAN.md)
- [../sprint-02/README.md](../sprint-02/README.md)
- [../sprint-02/ACTION_ITEMS.md](../sprint-02/ACTION_ITEMS.md)
- [../sprint-02/DECISIONS.md](../sprint-02/DECISIONS.md)
- [../sprint-02/ACCEPTANCE_CRITERIA.md](../sprint-02/ACCEPTANCE_CRITERIA.md)

## Relevant Sprint Records

- [ACTION_ITEMS.md](ACTION_ITEMS.md)
- [DECISIONS.md](DECISIONS.md)
- [ACCEPTANCE_CRITERIA.md](ACCEPTANCE_CRITERIA.md)

## Definition Of Done

Sprint 03 is done only when:

1. each transferred unresolved item has an explicit evidence-backed disposition,
2. historical-data adequacy and cost-model limitations are documented without claiming final validation,
3. candle semantics and holdout boundaries are resolved or honestly left blocked,
4. the first bounded experiment specification remains explicit about its assumptions and evidence requirements,
5. no implementation, approval, paper-trading, or live-trading claim is inserted by omission or implication.

## Notes

Sprint 03 is a continuation of the blocked planning and evidence gate, not a validation or authorization sprint. It does not approve a profitable strategy, authorise implementation beyond the current guardrails, authorize paper trading, or authorize live trading.
