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
| S03-006 | DOCUMENTATION | Define the first bounded research experiment as a separate controlled specification. Source: `S02-006`. | The strategy cannot be evaluated reproducibly until the first experiment is frozen with explicit data, timing, cost-model, and validation rules. | HIGH | DONE | S03-101, S03-102 | A bounded first-experiment specification covering objective, inputs, outputs, timing, anti-lookahead rules, cost model, validation split, and evidence thresholds. | Human review against the authoritative strategy specification, technical plan, and Sprint 02 decision register. | Research-scope specification is frozen; it preserves the bounded data decision, the approved conservative candle contract, and explicit guardrails for implementation and profitability. | The specification is frozen only as a bounded research-scope decision. It does not validate implementation, real execution costs, sample adequacy beyond the bounded scope, or strategy profitability. |
| S03-007 | DOCUMENTATION | Preserve the separation between signal, risk approval, order request, acknowledgement, fill, and final account or position state in the future experiment definition. Source: `S02-007`. | Research and accounting become invalid if these states are conflated. | HIGH | DONE | - | Future experiment documentation that preserves the existing cross-document state distinctions. | Inspect the experiment definition against the strategy and technical plan. | Strategy specification and technical plan already separate signal, risk approval, order intent, acknowledgement, fill, and final accounting state; these rules are recorded in authoritative documents and are not to be conflated. | This requirement is independently satisfied by the current repository evidence. It remains a required guardrail for the later experiment specification and implementation phases, but it does not resolve the blocked evidence gates for the first bounded experiment. |
| S03-101 | HUMAN_DECISION | Determine whether the bounded historical research dataset is adequate for the first experiment and whether the sample is representative enough for the intended study. Source: `S02-101`. | Venue and data-source semantics affect candles, fees, liquidity, fills, execution constraints, and the statistical validity of the sample. | HIGH | DONE | - | A bounded adequacy judgment for the Tardis.dev Binance Jersey BTCEUR first-day-of-month sample, with explicit limitations documented as part of the research boundary. | Inspect the updated decision record and supporting evidence. | The 12-file sample is explicitly recorded as valid only for bounded exploratory research; it makes no claim of representativeness, full-month adequacy, profitability, or execution realism. | This task resolves the adequacy decision within the bounded research scope only. It does not authorize broader suitability claims or live trading. |
| S03-102 | HUMAN_DECISION | Approve the primary timeframe and candle-semantics policy for the first research experiment. Source: `S02-102`. | The strategy and replay logic depend on timeframe, timestamp meaning, finalization rules, and missing-candle handling. | HIGH | DONE | - | A fully documented and verified 5-minute OHLCV contract covering UTC-aligned bucket boundaries, trade-based OHLCV semantics, completed-candle exclusion, empty/missing interval rejection, and passing verification tests. | Inspect the authoritative decision record, implementation design contract, and actual code/test evidence. | The implementation in `tools/hsra/ohlcv.py` matches the approved contract and the focused verification suite passed: `python -m pytest tests/test_hsra_ohlcv.py -q` → `12 passed in 0.27s`. | The design contract is approved and verified for the bounded research scope; it does not imply broader strategy approval, paper-trading approval, or live-trading approval. |
| S03-104 | HUMAN_DECISION | Decide whether provisional strategy implementation is allowed before the proposed strategy is formally approved. Source: `S02-104`. | The technical plan explicitly treats this as a gating decision for later implementation phases. | MEDIUM | DONE | - | A documented implementation-governance decision with explicit conditions and constraints. | Inspect the authoritative document update and compare against project definition and roadmap. | Project definition, roadmap, and technical plan already prohibit implementation before evidence gates are satisfied and require no silent assumptions. | Independent repository evidence resolves this governance question: implementation remains blocked until the research and evidence gates are satisfied; the current repo documents give the operative boundary and there is no authority to start implementation or paper/live trading. |
