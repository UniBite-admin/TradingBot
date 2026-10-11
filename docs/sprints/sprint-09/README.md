# Sprint 09 - Controlled Live Test, Evaluation, and Scale Gate

## Sprint Status

- Identifier: Sprint 09
- Status: BLOCKED - awaiting explicit human approval for live test and scale decisions
- Scope: final validation stage defined by the roadmap and technical plan
- Implementation state: final evaluation gate is implemented and validated; live testing and scaling remain blocked
- Live-trading state: not authorized until the approval gate is satisfied

## Objective

Cover the final validation endpoint required by the project: controlled live testing, final evaluation, and the final decision gate for controlled scaling only if evidence supports it.

## Scope

Sprint 09 covers:

- live-test preconditions and authorization gate,
- controlled spot-only live test under strict risk limits,
- evidence review across historical, paper, and live stages,
- final evaluation of repeatable positive expectancy,
- controlled scale decision only if supported by evidence and risk controls.

## Explicit exclusions

- no unapproved live trading,
- no leverage or derivative exposure,
- no uncontrolled scaling,
- no automatic scaling without explicit human authorization.

## Dependencies

- evidence from earlier sprints,
- explicit human approval for any live deployment,
- separate evaluation of the strategy under realistic constraints and operational conditions.

## Source references

- `PROJECT_DEFINITION.md`
- `ROADMAP.md`
- `TECHNICAL_PLAN.md`
- `STRATEGY_SPECIFICATION.md`
- `docs/sprints/sprint-08/README.md`
