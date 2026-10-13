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

The remaining Stage 2 engineering decisions are still explicitly unresolved and have no explicit task owner or approval status:

- Market universe selection method.
- Initial language and runtime.
- Storage requirements.
- Logging and experiment tracking approach.

These items remain open and must not be silently treated as approved implementation choices.

## S3D-002 - Historical-data adequacy is approved only for bounded exploratory research

- Status: RESOLVED FOR BOUNDED RESEARCH ONLY; FINAL ADEQUACY REMAINS BLOCKED
- Evidence: user approval for the existing first-calendar-day-of-month Tardis.dev Binance Jersey BTCEUR sample as a bounded exploratory data source; repository documentation explicitly forbids representativeness or profitability claims from this sample.
- Why it matters: the sample is permissible for bounded exploratory signal research only, not as a final or representative market history and not as evidence of profitability.
- Approved scope boundary:
  - sample may be used to test signal logic and data handling under explicit research-only constraints,
  - no claim of statistical representativeness,
  - no claim of realistic Bitvavo execution realism from this historical sample,
  - no claim of strategy profitability or expectancy validation,
  - no paper-trading or live-trading authorization.
- Explicit separation of gates:
  - final historical-data adequacy and representativeness remain unresolved,
  - Bitvavo execution realism remains a separate, unapproved gate,
  - profitability validation remains a separate, unapproved gate.
- Remaining blocker:
  - any broader adequacy, representativeness, Bitvavo realism, or profitability claim remains unproven and is therefore outside the approved bounded research decision.

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

## S3D-007 - Delegated decision authority and first-experiment objective

- Status: RESOLVED UNDER DELEGATED HUMAN-AUTHORIZED DECISION
- Evidence: the project owner delegated authority to ChatGPT on 2026-10-11 for the bounded research decisions recorded in this document.
- Why it matters: the delegated decision is human-authorized, but it is still limited to the bounded research scope and does not authorize paper trading, live trading, deployment, or broader strategy approval.
- Decision:
  - The first experiment is a bounded, reproducible exploratory signal-research experiment using the accepted research boundary only.
  - Its purpose is to verify deterministic data handling, the existing 5-minute OHLCV contract, and reproducible exploratory signal evaluation.
  - It is not a profitability validation, a realistic Bitvavo execution-cost validation, or an authorization for paper or live trading.
  - The existing first-calendar-day-of-month Tardis.dev Binance Jersey BTCEUR sample remains the only permitted source for the first experiment, with its limited and potentially biased sampling characteristics preserved.

## S3D-008 - Delegated initial market universe

- Status: RESOLVED FOR THE FIRST BOUNDED EXPERIMENT ONLY
- Evidence: the existing accepted research sample is BTC-EUR only; this decision is recorded under delegated authority and remains limited to the first bounded experiment.
- Why it matters: the experiment must remain small and explicit. Multi-asset monitoring remains a future system objective, not part of the current experiment.
- Decision:
  - BTC-EUR only for the first bounded experiment.
  - No additional assets or cross-market data are added to this experiment.
  - Multi-asset monitoring remains a future system objective and not part of the current bounded research scope.

## S3D-009 - Delegated language and runtime

- Status: RESOLVED FOR THE INITIAL RESEARCH ENVIRONMENT ONLY
- Evidence: the repository documents recommended Python 3.12 as the initial runtime, and no dependency manifest or environment declaration currently verifies a broader runtime state.
- Why it matters: the runtime decision is resolved for the initial research environment but is still not equivalent to a validated production environment.
- Decision:
  - Use Python 3.12 for the initial research environment.
  - Compatibility requirements and verification remain needed before claiming the environment is fully verified for later implementation work.
  - No new framework or unnecessary dependency layer is introduced by this decision.

## S3D-010 - Delegated storage decision

- Status: RESOLVED FOR THE BOUNDED EXPERIMENT ONLY
- Evidence: the repository requires reproducible artifacts and immutable canonical source data; no persistent database requirement is introduced solely for this experiment.
- Why it matters: the experiment must keep canonical inputs immutable while preserving run metadata, results, and limitations in reproducible artifacts.
- Decision:
  - Use file-based, reproducible artifacts for the bounded research experiment.
  - Keep canonical source data immutable.
  - Store each experiment's configuration, input-data identity, code/version reference, run metadata, results, and limitations in documented machine-readable artifacts using the repository's existing established conventions.
  - Do not introduce a new database solely for this experiment.
  - This decision does not prohibit a future database for durable live-system state or accounting, but it does not authorize that future stage.

## S3D-011 - Delegated logging and experiment tracking

- Status: RESOLVED FOR THE BOUNDED EXPERIMENT ONLY
- Evidence: the repository requires traceability and reproducibility; the project plan recommends JSON Lines and structured metadata artifacts.
- Why it matters: the approved experiment must be auditable without claiming deterministic success before it is tested.
- Decision:
  - Use Python's standard logging facilities and structured, machine-readable experiment records.
  - Prefer JSON Lines for event and log records and a per-run manifest in the repository's existing suitable format.
  - Record at minimum: experiment/run identifier, exact input dataset and provenance reference, code revision/source identity, configuration and parameter values actually used, run start/end and completion status, data-quality exclusions and rejected windows, results and interpretation limits, and errors and reproducibility outcomes.
  - Do not claim deterministic reproducibility until it is tested.

## S3D-012 - Delegated evaluation and cost boundary

- Status: RESOLVED FOR THE CURRENT RESEARCH BOUNDARY ONLY
- Evidence: the project already freezes the research scope and parameter-exploration rules; the historical sample is not evidence of realistic Bitvavo execution conditions.
- Why it matters: the project must preserve the distinction between exploratory results and validated economic performance.
- Decision:
  - Keep the existing frozen research boundary and parameter-exploration rules.
  - Any exploratory results must be labeled exploratory.
  - Do not select parameters using the holdout, alter rules after examining holdout results, or make optimality claims.
  - The current sample is not evidence of realistic Bitvavo spread, fees, slippage, latency, liquidity, or fills.
  - Do not label gross exploratory results as net profitability.
  - Keep execution-cost realism and positive-expectancy validation as separate unresolved evidence gates.

## S3D-013 - Delegated implementation and safety boundary

- Status: RESOLVED FOR THE BOUNDED RESEARCH SCOPE ONLY
- Evidence: the roadmap, project definition, and sprint records all require the stage gates to remain in force; the delegation is limited to research planning and documentation.
- Why it matters: the delegated decisions resolve the earlier Stage 2 planning gap without creating a later-stage approval.
- Decision:
  - The above decisions resolve the corresponding Stage 2 planning choices only within the bounded research scope.
  - They do not automatically approve strategy implementation beyond the already documented research-only scope, broader data acquisition, paper trading, live trading, or scaling.
  - The current roadmap stage gates remain in force.
  - The documentation must not silently imply a later stage has passed.

## S3D-014 - Delegated first bounded candlestick research hypothesis

- Status: RESOLVED UNDER PROJECT-OWNER-AUTHORIZED DELEGATED RESEARCH DECISION
- Evidence: the project owner delegated technical and research decision authority to ChatGPT for the bounded research scope, and the repository already records the bounded research boundary, the BTC-EUR-only, 5-minute candle contract, and the no-implementation/no-profitability guardrails.
- Why it matters: the first bounded experiment must remain explicit, small, and honest about its limits; it is a signal-predictiveness test only and not a general trading-edge claim.
- Decision:
  - Candidate hypothesis: “When a completed 5-minute BTC-EUR candle closes above its open, the following 5-minute period has a greater-than-baseline tendency to produce a positive price return.”
  - Signal definition: a candle is bullish only if its completed close is strictly greater than its open; equal open and close never generates a signal.
  - Observation target: measure the next completed 5-minute return as `r_k = (close_{k+1} - close_k) / close_k`, using the candle close as the representative price for each interval; this is a descriptive close-to-close return and does not assume a fill or a realistic execution cost.
  - Timing: the signal is formed only after the source candle is complete and valid; the target interval is the next completed 5-minute period; no look-ahead or future-data leakage is allowed.
  - Baseline: compare the signal set’s positive-return frequency to the unconditional positive-return frequency of the same eligible next-period observations.
  - Metrics: report eligible sample count, signal positive-return frequency, baseline positive-return frequency, difference in percentage points, mean return, median return, and descriptive uncertainty appropriate to the sample size. No acceptance threshold is currently approved.
  - Data integrity: reject incomplete, missing, duplicate, ambiguous, or invalid windows under the existing frozen data-validation and ambiguous-window policies; no silent backfill or repair policy is introduced.
  - Reproducibility: a run manifest must identify the hypothesis/specification version, dataset provenance, input file identities or hashes where available, Python/software version, UTC evaluation boundaries, validation/rejection counts, and output artifact identities. No reproducibility claim is made until an actual run verifies it.
  - No tuning and no generalization: do not optimize thresholds or tune on the final holdout; do not describe the small sample as representative of the whole market or the full month.
  - Cost boundary: this remains a gross signal-predictiveness test only. It does not establish realistic Bitvavo costs, fills, net expectancy, profitability, paper-trading readiness, live-trading approval, or scaling.
  - Spot boundary: do not introduce short selling, leverage, margin, futures, perpetuals, or exchange orders.
  - Unresolved threshold: no minimum sample threshold or statistical significance threshold is approved by the repository. The numerical acceptance threshold remains unresolved and must be decided in the next research-specification step.

## S3D-015 - Delegated descriptive-only interpretation for the first bounded candlestick experiment

- Status: RESOLVED UNDER PROJECT-OWNER-AUTHORIZED DELEGATED RESEARCH DECISION
- Evidence: the project owner delegated routine technical and research decisions to ChatGPT for the bounded research scope, and the repository records the experiment as a small, descriptive, first-step signal-check with no profitability or live-execution approval. The current sample is sparse, covers only the first calendar day of each month, and may contain serial dependence, so the repository must not treat it as inferential evidence without a justified method.
- Why it matters: the research plan must remain honest about what the bounded dataset can and cannot support; otherwise the project would quietly convert a small exploratory sample into a statistical claim it has not justified.
- Decision:
  - This experiment remains descriptive and exploratory only. It may report the observed bullish-signal frequency, the unconditional baseline frequency, the percentage-point difference, eligible observation counts, and the mean and median next-period returns.
  - The experiment may also report descriptive variation transparently, including separate pooled summaries and summaries by sampled calendar-day segment. These segment-level results are descriptive only and are not independent statistical evidence unless a separate, justified inferential method is explicitly approved.
  - Do not report inferential confidence intervals, p-values, statistical significance, or a statistical pass/fail verdict for this bounded dataset. The current sparse sampling design and the possibility of serial dependence do not yet justify a defensible inferential method.
  - Do not invent or select a minimum sample count, significance threshold, effect-size threshold, or profitability threshold after inspecting the results. Any future inferential acceptance criteria must be specified before the corresponding confirmatory evaluation and supported by an appropriate sampling and dependence methodology.
  - Outcome labels are limited to the available evidence and must not be presented as statistical confirmation, statistical rejection, net profitability, or strategy acceptance. The project's allowed classifications are: `Unusable`, `Descriptive but inconclusive`, `Descriptive sample result in the hypothesized direction`, and `Descriptive sample result opposite to the hypothesized direction`.
  - The experiment does not establish historical-data adequacy, Bitvavo execution-cost realism, net expectancy, profitability, implementation authorization, paper-trading authorization, live-trading authorization, or scaling approval. The remaining frozen candle, look-ahead, duplicate, timestamp-ambiguity, and invalid-window policies remain in force.
  - The hypothesis remains unchanged. No threshold or signal rule is optimized after observing results, and no implementation code or tests are modified as part of this documentation-only decision.

### Contract clarifications retained under S3D-015

- The repository permits the sample-set decision to be written as `first calendar day of each month only`, but the exact UTC interpretation of that phrase remains a blocker unless the selected source files and run metadata establish it explicitly. The manifest defines the in-scope file set and the sample boundary, but it does not silently define a UTC evaluation boundary for every observation.
- File/sample selection and observation eligibility are intentionally separate by contract: a file may be in scope while an individual observation is still rejected for missing, ambiguous, or invalid next-period data.
- The minimal output contract for the descriptive experiment is defined as a deterministic package of pooled metrics, per-day summaries, and a run manifest; the exact artifact names and required fields are preserved in the authoritative strategy specification and are not treated as a broader implementation approval.
- Empty and unusable result classifications are bounded to descriptive labels only. They do not create significance, profitability, or strategy-approval claims.
- Repeat-run equivalence is defined semantically: the same inputs and specification version must yield equivalent normalized values and deterministic ordering, while non-semantic metadata such as wall-clock timestamps may legitimately differ.

### Delegated technical clarifications under S3D-015

- This repository treats the exact manifest-listed input set as the authoritative file selection for the bounded experiment; no wider calendar-day re-selection is introduced by this decision.
- The evaluation boundary is a delegated technical decision only to the extent that it is explicitly recorded in the run metadata or the source provenance. If that boundary cannot be proven from authoritative evidence, the run must be rejected or flagged as unresolved rather than silently assuming UTC.
- The output contract is fixed as UTF-8 JSON with a canonical field ordering, Decimal-based quantization to 12 decimal places, `allow_nan=False`, and `-0` normalized to `0.0`.
- The classification procedure is fixed as precedence-ordered and mutually exclusive; it retains the descriptive-only boundary and does not create profitability or inferential claims.

## Handoff Status

Sprint 03 is not a strategy-approval sprint. It is the continued governance and evidence boundary work for the bounded research scope, now explicitly reconciled with the delegated human-authorized decisions recorded above.
