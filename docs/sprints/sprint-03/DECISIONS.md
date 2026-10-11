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

## S3D-002 - Historical-data adequacy is approved only for bounded exploratory research

- Status: RESOLVED FOR BOUNDED RESEARCH ONLY
- Evidence: user approval for the existing first-calendar-day-of-month Tardis.dev Binance Jersey BTCEUR sample as a bounded exploratory data source; repository documentation explicitly forbids representativeness or profitability claims from this sample.
- Why it matters: the sample is permissible for bounded exploratory signal research only, not as a final or representative market history and not as evidence of profitability.
- Approved scope boundary:
  - sample may be used to test signal logic and data handling under explicit research-only constraints,
  - no claim of statistical representativeness,
  - no claim of realistic Bitvavo execution realism from this historical sample,
  - no claim of strategy profitability or expectancy validation,
  - no paper-trading or live-trading authorization.
- Remaining blocker:
  - a broader adequacy or representativeness claim remains unproven and is therefore recorded as `S03-101` in blocked status.

## S3D-003 - Candle semantics are approved for the bounded research contract only

- Status: RESOLVED FOR RESEARCH CONTRACT; IMPLEMENTATION EVIDENCE VERIFIED
- Evidence: user approval of the conservative candle contract as the research bound, plus the current read-only implementation evidence from `tools/hsra/ohlcv.py` and its verification tests.
- Why it matters: effective signal evaluation depends on timestamp meaning, interval alignment, completed-candle policy, missing/no-trade handling, and incomplete-candle handling within the bounded research scope.
- Approved research contract:
  - fixed 5-minute bars aligned to the UTC clock,
  - interval-start timestamp semantics,
  - only completed candles are eligible for signal evaluation,
  - an unconfirmed or still-forming candle is ineligible,
  - missing or ambiguous market windows are rejected and not silently backfilled,
  - anti-lookahead is enforced by using only information available at the relevant decision time,
  - deterministic ordering and continuity follow the existing canonicalization rules from `tools/hsra/merger.py`.
- Current evidence status:
  - the implementation in `tools/hsra/ohlcv.py` currently enforces UTC bucket boundaries, trade-only OHLCV semantics, empty-interval rejection, duplicate rejection, and same-timestamp ambiguity rejection,
  - the targeted verification suite in `tests/test_hsra_ohlcv.py` passes, but this is evidence for implementation correctness only and is separate from human approval of the broader research gate,
  - the active item remains `S03-102`; completion still requires the repository-level human decision gate and any remaining data-adequacy review to be resolved explicitly.

## S3D-004 - Execution-cost realism and profitability validation remain separate acceptance gates

- Status: OPEN
- Evidence: `PROJECT_DEFINITION.md`, `STRATEGY_SPECIFICATION.md`, `TECHNICAL_PLAN.md`, and the Sprint 02 decision record.
- Why it matters: the project still requires separate evidence for realistic cost modeling and the profitability gate before strategy approval or implementation expansion.
- Explicit non-claims:
  - no realistic Bitvavo historical fill model is approved,
  - no positive expectancy claim is approved,
  - no execution-cost assumption may be silently promoted to repository-truth.

## S3D-005 - The first bounded experiment specification is frozen as a research-scope decision only

- Status: FROZEN FOR RESEARCH SCOPE ONLY
- Evidence: explicit user approval of the bounded sample decision and the conservative candle contract; no strategy, implementation, paper-trading, live-trading, or profitability validation was approved.
- Why it matters: the experiment specification is now frozen as a controlled research boundary for exploratory signal work only, not as a validation of implementation, data adequacy beyond the bounded scope, or profitability.
- Frozen research boundary:
  - purpose: bounded exploratory signal research only,
  - data: existing first-calendar-day-of-month Tardis Binance Jersey BTCEUR sample only,
  - venue distinction: historical sample is not Bitvavo execution data,
  - timeframe: fixed 5-minute bars aligned to UTC,
  - timestamp semantics: interval-start semantics,
  - evaluation: completed candles only; no use of an unconfirmed or still-forming candle,
  - missing or ambiguous data: reject affected windows; do not silently backfill missing bars,
  - ordering and continuity: use the existing verified canonicalization rules in `tools/hsra/merger.py` and explicitly separate verified behavior from unimplemented candle rules,
  - anti-lookahead: features and signals use only information available at the relevant decision time,
  - parameter exploration: retain the documented candidate grid and exclude any optimality claim,
  - validation: chronological separation only; the holdout is not used for parameter selection or rule changes,
  - costs: do not claim realistic Bitvavo spread, fees, slippage, latency, liquidity, or fills from the current dataset; any future assumptions remain explicitly labeled,
  - acceptance: successful exploratory signal research means the experiment is reproducible, bounded, and honest about its limits; it does not count as proof of profitability or strategy validity.
- Remaining blockers:
  - `S03-101` remains blocked because sampling adequacy and representativeness are still not proven beyond the bounded research boundary,
  - `S03-102` remains blocked for implementation and test verification even though the research contract is approved,
  - no strategy implementation, paper trading, or live trading is authorized by this frozen spec.

## S3D-006 - Approved OHLCV implementation contract for the 5-minute builder design

- Status: RESOLVED FOR RESEARCH CONTRACT; IMPLEMENTATION VERIFIED
- Evidence: explicit human approval recorded for the OHLCV builder contract and focused passing verification of the implementation against the contract.
- Why it matters: these are the source-of-truth design decisions that the eventual implementation must satisfy; they must not be reinterpreted or silently replaced by a different rule set.
- Approved implementation contract:
  - Input source: build OHLCV exclusively from raw trade events; do not use quote events to construct OHLCV.
  - OHLC semantics: for each UTC-aligned 5-minute interval,
    - open = first eligible trade price,
    - high = maximum eligible trade price,
    - low = minimum eligible trade price,
    - close = last eligible trade price.
  - Volume semantics: sum trade amounts expressed in the base asset; do not use quote-asset volume or order-book-derived volume.
  - Time boundaries: use fixed UTC-aligned 5-minute intervals; candle timestamps represent interval start.
  - Completed-candle policy: only completed and valid candles may be used for signal evaluation; incomplete or still-forming candles must be excluded.
  - Empty-interval policy: in the first version, reject the affected interval; do not synthesize an empty candle, carry forward a previous close, or silently fill the gap.
  - Missing or ambiguous data policy: reject affected research intervals when validity cannot be established; do not silently backfill.
  - Deterministic and validation requirements: eventual implementation must be tested for UTC bucket boundaries, interval-start timestamps, OHLCV calculations, incomplete-candle exclusion, empty/missing interval rejection, duplicate and out-of-order events, deterministic output, and look-ahead prevention.
- Important distinction:
  - this is an approved design contract for the future implementation;
  - the repository now has concrete implementation evidence and passing validation tests, but that evidence still does not constitute human approval of the broader strategy or live-trading path,
  - `S03-102` remains an active gate because the design approval and the human decision gate are separate checks.
- Human approval required: no additional approval is required for the recorded implementation contract itself; any variation from this contract remains a new design decision and must be explicitly re-approved.

## Handoff Status

Sprint 03 is not a strategy-approval sprint. It is the commanded continuation of the unresolved technical and evidence-gate work from Sprint 02, with the same no-approval guardrails and audit discipline.
