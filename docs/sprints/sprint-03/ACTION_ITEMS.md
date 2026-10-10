# Sprint 03 - Action Items

This file is the authoritative Sprint 03 task register.

Sprint handoff note:

- Sprint 03 carries forward the unresolved evidence-gate and specification work transferred from Sprint 02.
- The bounded `S02-103` policy record remains in force as a documented limit, not as a strategy approval.

Status vocabulary:

- `NOT_STARTED`
- `IN_PROGRESS`
- `BLOCKED`
- `DONE`

Priority vocabulary:

- `HIGH`
- `MEDIUM`
- `LOW`

## Unresolved Work Transferred From Sprint 02

| ID | Type | Description | Rationale | Priority | Status | Dependencies | Expected Output | Verification Method | Required Evidence | Blocker / Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| S03-006 | DOCUMENTATION | Define the first bounded research experiment as a separate controlled specification. Source: `S02-006`. | The strategy cannot be evaluated reproducibly until the first experiment is frozen with explicit data, timing, cost-model, and validation rules. | HIGH | BLOCKED | S03-101, S03-102, S02-103 | A bounded first-experiment specification covering objective, inputs, outputs, timing, anti-lookahead rules, cost model, validation split, and evidence thresholds. | Human review against the authoritative strategy specification, technical plan, and Sprint 02 decision register. | Approved experiment document or approved experiment section with explicit assumptions and blocked evidence gates. | Blocked by unresolved historical-data adequacy, exact holdout strategy, candle semantics, and realistic execution-cost evidence. The bounded `S02-103` decision remains in force as a research boundary, not as an approval of profitability or implementation. |
| S03-007 | DOCUMENTATION | Preserve the separation between signal, risk approval, order request, acknowledgement, fill, and final account or position state in the future experiment definition. Source: `S02-007`. | Research and accounting become invalid if these states are conflated. | HIGH | NOT_STARTED | S03-006 | Future experiment documentation that preserves the existing cross-document state distinctions. | Inspect the experiment definition against the strategy and technical plan. | Future experiment document review. | Depends on `S03-006`; the state distinctions must stay explicit and separate throughout the first experiment definition. |
| S03-101 | HUMAN_DECISION | Determine whether the bounded historical research dataset is adequate for the first experiment and whether the sample is representative enough for the intended study. Source: `S02-101`. | Venue and data-source semantics affect candles, fees, liquidity, fills, execution constraints, and the statistical validity of the sample. | HIGH | BLOCKED | - | An explicit adequacy judgment for the Tardis.dev Binance Jersey BTCEUR first-day-of-month sample, with limitations recorded as part of the research boundary. | Inspect the updated decision record and supporting evidence. | A traceable adequacy decision, including explicit sampling limits and remaining evidence gaps. | This task does not authorize final profitability validation or live trading. Any accepted adequacy remains bounded and provisional unless separate evidence supports a stronger claim. |
| S03-102 | HUMAN_DECISION | Approve the primary timeframe and candle-semantics policy for the first research experiment. Source: `S02-102`. | The strategy and replay logic depend on timeframe, timestamp meaning, finalization rules, and missing-candle handling. | HIGH | BLOCKED | - | A documented contract for the primary timeframe and candle semantics, including time basis, completion rules, missing/no-trade handling, and incomplete-candle handling. | Inspect the authoritative decision record and any implementation/test evidence. | Explicit timeframe and candle-contract decisions with separate evidence for code-level implementation and testing. | The 5-minute timeframe is recorded as approved for the first bounded historical research experiment only. Detailed candle semantics remain separate and must not be silently treated as approved unless implemented and verified. |
| S03-104 | HUMAN_DECISION | Decide whether provisional strategy implementation is allowed before the proposed strategy is formally approved. Source: `S02-104`. | The technical plan explicitly treats this as a gating decision for later implementation phases. | MEDIUM | NOT_STARTED | S03-006 | A documented implementation-governance decision with explicit conditions and constraints. | Inspect the authoritative document update and compare against project definition and roadmap. | Approved documentation update. | This decision blocks later implementation planning beyond documentation until the research and evidence gates are satisfied. |
