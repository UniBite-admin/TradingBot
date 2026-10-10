# Sprint 03 - Decisions And Handoff

This file records the unresolved decisions and evidence gates transferred from Sprint 02. Sprint 03 is a continuation of the planning and evidence-review work only; it does not approve implementation, paper trading, or live trading.

## S3D-001 - Unresolved Sprint 02 issues are carried forward into Sprint 03

- Status: TRANSFERRED
- Evidence: Sprint 02 closure record and task-transfer mapping.
- Why it matters: the unresolved Stage 2 evidence gates remain visible and are not silently treated as approved.
- Transfer mapping:
  - `S02-006` -> `S03-006`
  - `S02-007` -> `S03-007`
  - `S02-101` -> `S03-101`
  - `S02-102` -> `S03-102`
  - `S02-104` -> `S03-104`

## S3D-002 - Historical-data adequacy remains an unresolved evidence gate

- Status: OPEN
- Evidence: the bounded Tardis.dev Binance Jersey BTCEUR sample remains provisional and separated from the intended Bitvavo execution venue.
- Why it matters: file-level integrity and canonicalization do not prove representativeness, completeness, or statistical adequacy.
- Explicit non-claims:
  - no final adequacy approval,
  - no profitability or expectancy claim,
  - no implied full-month data purchase approval,
  - no paper-trading or live-trading authorization.

## S3D-003 - Candle semantics remain a separate unresolved implementation gate

- Status: OPEN
- Evidence: the 5-minute timeframe is a human-approved research default, but the detailed candle contract remains proposal-level unless implemented and verified.
- Why it matters: timestamp meaning, interval alignment, completed-candle policy, missing/no-trade handling, and final incomplete-candle handling affect replay correctness and anti-lookahead compliance.
- Required evidence before acceptance:
  - explicit timestamp semantics,
  - completed-candle-only evaluation,
  - missing and no-trade gap policy,
  - deterministic sorting and temporal continuity rules,
  - code-level verification.

## S3D-004 - Execution-cost realism and profitability validation remain separate acceptance gates

- Status: OPEN
- Evidence: `PROJECT_DEFINITION.md`, `STRATEGY_SPECIFICATION.md`, `TECHNICAL_PLAN.md`, and the Sprint 02 decision record.
- Why it matters: the project still requires separate evidence for realistic cost modeling and the profitability gate before strategy approval or implementation expansion.
- Explicit non-claims:
  - no realistic Bitvavo historical fill model is approved,
  - no positive expectancy claim is approved,
  - no execution-cost assumption may be silently promoted to repository-truth.

## S3D-005 - The first bounded experiment specification remains blocked until evidence is complete

- Status: BLOCKED
- Evidence: `S02-006`, `S03-006`, and the unresolved data, timing, and cost-evidence gates transferred from Sprint 02.
- Why it matters: the experiment specification cannot be honestly frozen without a documented adequacy judgment, valid candle semantics, and cost-model discipline.
- Required evidence before approval:
  - explicit sample adequacy and representativeness status,
  - approved data windowing and holdout boundaries,
  - approved candle contract,
  - explicit execution-cost assumptions or validated models,
  - clear anti-lookahead and validation rules.

## Handoff Status

Sprint 03 is not a strategy-approval sprint. It is the commanded continuation of the unresolved technical and evidence-gate work from Sprint 02, with the same no-approval guardrails and audit discipline.
