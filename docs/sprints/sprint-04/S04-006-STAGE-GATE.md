# S04-006 - Research Progression Gate

## Purpose

This gate prevents progression from bounded historical research into any later stage unless the evidence chain is visible, the data contract is still valid, and the project remains inside the explicitly approved research scope.

The gate is intentionally conservative. It does not infer adequacy from a passing pipeline; it requires explicit evidence and a human decision before the project may treat sampled data as suitable for anything beyond bounded exploratory signal research.

## Gate condition

The project may move to the next implementation or design phase only when all of the following are true:

1. the exact sample scope and provenance are recorded,
2. the raw-data ingestion contract is still valid for the files in scope,
3. the canonicalization and rejection rules are consistently enforced,
4. the bounded-sample limitations are explicitly documented,
5. no anti-lookahead or hidden-assumption rule has been violated,
6. the relevant human approval is present for the intended next stage.

## Hard stop conditions

Progression is blocked immediately if any of the following are true:

- `S03-101` remains unresolved in a way that claims broader representativeness,
- `S03-102` remains unresolved for the implementation contract that the next stage depends on,
- the dataset contains unexplained gaps, duplicate records, stale timestamps, or out-of-order events that violate the approved policy,
- the evidence cannot be reproduced from the checked-in repo artifacts,
- the project tries to move from research-only analysis to broader strategy approval, execution design, or live testing without explicit authorization,
- any claim of profitability, validation realism, or adequacy exceeds the bounded sample boundary.

## Allowed status

The repository may continue in bounded exploratory signal research only when the data pipeline remains reproducible and the project clearly labels results as:

- historical research only,
- bounded sample only,
- no claim of representativeness,
- no claim of profitability,
- no claim of live-readiness.

## Evidence required before the gate is considered satisfied

Before a human marks the gate as passed, the repo must show:

- provenance of the exact sample used,
- raw-file intake validation,
- canonical event rejection/acceptance evidence,
- deterministic regression tests covering invalid and ambiguous data,
- explicit documentation of what remains unproven and why.

## Human approval requirement

This stage gate is not self-approving. Human approval remains required for any move beyond the current bounded research scope. Until that approval exists, the repository must remain in a stop-and-verify state.

## Outcome at the time of Sprint 04

For Sprint 04, the project has established the gate documentation and the required evidence checks. The gate is therefore recorded in the repository, but it remains externally blocked by the required human approval for the bounded-sample adequacy decision and the next-stage progression decision.
