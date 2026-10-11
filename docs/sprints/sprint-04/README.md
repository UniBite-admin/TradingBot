# Sprint 04 - Research Data Intake and Provenance

## Sprint Status

- Identifier: Sprint 04
- Status: OPEN
- Scope state: Documentation and research-environment setup only
- Implementation state: S04-001 provenance record complete, S04-002 raw-data ingestion contract implemented and verified, S04-003 canonical validation policy implemented and tested, S04-004 bounded-sample adequacy decision documented, S04-005 data-quality regression suite implemented and tested, and S04-006 stage gate recorded; the only remaining Sprint 04 item is the human approval gate for progression beyond bounded research
- Strategy approval state: Not approved
- Live-trading state: Not allowed
- Dependency gate: this sprint remains blocked if `S03-101` and `S03-102` remain unresolved or if the bounded-sample boundary is exceeded.

## Objective

Establish the evidence-backed historical-data intake path and the minimum provenance, validation, and replay controls required for the first bounded research experiment.

## Scope

Sprint 04 covers:

- historical-data source inventory and provenance,
- raw-file verification and local archive policy,
- schema validation and canonicalization rules,
- data-quality rejection criteria,
- deterministic chronological replay and conflict handling,
- the explicit evidence gate for bounded-sample adequacy.

## Explicit exclusions

Sprint 04 does not include:

- strategy-rule approval,
- paper trading,
- live trading,
- scaling,
- real-exchange private-order integration,
- profitability claims,
- full-month historical acquisition without a separate human budget decision.

## Source references

- [PROJECT_DEFINITION.md](../../../PROJECT_DEFINITION.md)
- [ROADMAP.md](../../../ROADMAP.md)
- [TECHNICAL_PLAN.md](../../../TECHNICAL_PLAN.md)
- [STRATEGY_SPECIFICATION.md](../../../STRATEGY_SPECIFICATION.md)
- [docs/sprints/sprint-03/README.md](../sprint-03/README.md)
- [docs/sprints/sprint-03/ACTION_ITEMS.md](../sprint-03/ACTION_ITEMS.md)
- [docs/sprints/sprint-03/DECISIONS.md](../sprint-03/DECISIONS.md)

## Dependencies

- `S03-101` historical-data adequacy remains a primary blocked dependency.
- `S03-102` candle semantics remain a primary blocked dependency.
- `S03-006` bounded experiment scope remains the accepted boundary, not a full implementation approval.

## Definition of done

Sprint 04 is complete only when:

1. the raw-data ingestion path, provenance log, and archive policy exist,
2. the canonicalization and validation policy is explicit and testable,
3. the bounded sample limitations are documented without claiming representativeness,
4. every data-quality rejection is replay-safe and reproducible,
5. the sprint produces evidence that no hidden assumptions were introduced.

## Known blockers

- `S03-101`: data adequacy remains provisional and cannot be upgraded to full representativeness without explicit evidence.
- `S03-102`: candle contract and verification remain open until the 5-minute builder and tests are implemented and pass.
- Human approval is still required before any experiment is treated as more than bounded exploratory research.
