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

## Scope Clarifications

- `S03-101` is complete only for the bounded exploratory research-scope decision. Final historical-data adequacy and representativeness remain unresolved.
- `S03-102` is complete only for the verified bounded research OHLCV contract. It does not approve broader strategy, paper-trading, or live-trading authorization.
- `S02-103` records a bounded research policy only; it does not constitute final execution-cost realism, profitability, or parameter approval.
- The first bounded candlestick signal hypothesis (`S3D-014`) is a proposed exploratory research decision only and does not approve a production strategy, execution-cost model, profitability claim, or live-execution path.
- `S3D-015` resolves the descriptive-only interpretation and outcome classification for the first bounded candlestick experiment: the current result may be reported as descriptive only, but it must not be labeled as inferential evidence, statistical confirmation, statistical rejection, profitability, or strategy approval. Any future inferential method remains blocked until a separate, justified sampling and dependence methodology is explicitly specified.
- The repository now records explicit contract clarifications for the bounded research task: file/sample selection and observation eligibility remain distinct, the exact UTC interpretation of the first-of-month sample is a documented blocker unless it is explicitly authenticated, and the minimal deterministic output contract is specified without creating a broader implementation approval.
- The output contract and repeatability policy are fixed to a canonical UTF-8 JSON schema with ordered keys, SHA-256 hashing of exact raw file bytes when available, canonical semantic comparison, and explicit handling of unavailable hashes or non-finite values.
- The ordered classification procedure is fixed as mutually exclusive and precedence-ordered, with outcome labels remaining descriptive-only and without statistical or profitability thresholds.
- The previously unowned Stage 2 items are now resolved under the delegated authority recorded in `S3D-007` through `S3D-013` for the bounded research scope only: market universe selection (`S3D-008`), initial language/runtime (`S3D-009`), storage requirements (`S3D-010`), and logging and experiment tracking (`S3D-011`).
- These delegated decisions resolve ownership ambiguity without changing the current implementation gate: broader strategy implementation, paper trading, live trading, and scaling remain blocked by the uncompleted evidence gates and the roadmap stage boundaries.

## Unresolved Work Transferred From Sprint 02

| ID | Type | Description | Rationale | Priority | Status | Dependencies | Expected Output | Verification Method | Required Evidence | Blocker / Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| S03-006 | DOCUMENTATION | Define the first bounded research experiment as a separate controlled specification. Source: `S02-006`. | The strategy cannot be evaluated reproducibly until the first experiment is frozen with explicit data, timing, cost-model, and validation rules. | HIGH | DONE | S03-101, S03-102 | A bounded first-experiment specification covering objective, inputs, outputs, timing, anti-lookahead rules, cost model, validation split, and evidence thresholds. | Human review against the authoritative strategy specification, technical plan, and Sprint 02 decision register. | Research-scope specification is frozen; it preserves the bounded data decision, the approved conservative candle contract, and explicit guardrails for implementation and profitability. | The specification is frozen only as a bounded research-scope decision. It does not validate implementation, real execution costs, sample adequacy beyond the bounded scope, or strategy profitability. |
| S03-007 | DOCUMENTATION | Preserve the separation between signal, risk approval, order request, acknowledgement, fill, and final account or position state in the future experiment definition. Source: `S02-007`. | Research and accounting become invalid if these states are conflated. | HIGH | DONE | - | Future experiment documentation that preserves the existing cross-document state distinctions. | Inspect the experiment definition against the strategy and technical plan. | Strategy specification and technical plan already separate signal, risk approval, order intent, acknowledgement, fill, and final accounting state; these rules are recorded in authoritative documents and are not to be conflated. | This requirement is independently satisfied by the current repository evidence. It remains a required guardrail for the later experiment specification and implementation phases, but it does not resolve the blocked evidence gates for the first bounded experiment. |
| S03-101 | HUMAN_DECISION | Determine whether the bounded historical research dataset is adequate for the first bounded research experiment and define the exact scope of that approval. Source: `S02-101`. | Venue and data-source semantics affect candles, fees, liquidity, fills, execution constraints, and the statistical validity of the sample. | HIGH | DONE | - | A bounded adequacy judgment for the Tardis.dev Binance Jersey BTCEUR first-day-of-month sample, with explicit limitations documented as part of the research boundary. | Inspect the updated decision record and supporting evidence. | The 12-file sample is explicitly recorded as valid only for bounded exploratory research; it does not establish final adequacy, statistical representativeness, full-month coverage, Bitvavo execution realism, or profitability. | This task is complete only for the bounded research-scope decision. Final adequacy, broader representativeness, Bitvavo execution realism, and profitability remain separate, unapproved gates and are not authorized by this task. |
| S03-102 | HUMAN_DECISION | Approve the primary timeframe and candle-semantics policy for the first research experiment. Source: `S02-102`. | The strategy and replay logic depend on timeframe, timestamp meaning, finalization rules, and missing-candle handling. | HIGH | DONE | - | A fully documented and verified 5-minute OHLCV contract covering UTC-aligned bucket boundaries, trade-based OHLCV semantics, completed-candle exclusion, empty/missing interval rejection, and passing verification tests. | Inspect the authoritative decision record, implementation design contract, and actual code/test evidence. | The implementation in `tools/hsra/ohlcv.py` matches the approved contract and the focused verification suite passed: `python -m pytest tests/test_hsra_ohlcv.py -q` → `12 passed in 0.27s`. | The design contract is approved and verified for the bounded research scope; it does not imply broader strategy approval, paper-trading approval, or live-trading approval. |
| S03-104 | HUMAN_DECISION | Decide whether provisional strategy implementation is allowed before the proposed strategy is formally approved. Source: `S02-104`. | The technical plan explicitly treats this as a gating decision for later implementation phases. | MEDIUM | DONE | - | A documented implementation-governance decision with explicit conditions and constraints. | Inspect the authoritative document update and compare against project definition and roadmap. | Project definition, roadmap, and technical plan already prohibit implementation before evidence gates are satisfied and require no silent assumptions. | Independent repository evidence resolves this governance question: implementation remains blocked until the research and evidence gates are satisfied; the current repo documents give the operative boundary and there is no authority to start implementation or paper/live trading. |
