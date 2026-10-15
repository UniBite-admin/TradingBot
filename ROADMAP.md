# Trading Bot - Kraken-Only Research Roadmap

## Purpose

This roadmap defines the current, provider-specific research path for the repository: Kraken BTC/EUR 5-minute OHLCV is the active historical source for descriptive research, and all research remains bounded and non-trading.

## Current status

- Active source: Kraken BTC/EUR 5-minute OHLCV export under `data/kraken/`.
- Historical artifacts retained as evidence only: legacy Tardis first-of-month files and their associated reports are preserved for provenance and comparison, but they are not the active repository input contract.
- Research scope: descriptive, provider-specific, non-execution, and fail-closed against ambiguous source semantics. Box Theory is now the primary experimental candidate for the next cost-aware historical trade study; this does not replace Experiment A/B contracts or authorize trading.
- Approved research direction: holistic component evaluation using the explicitly documented existing rules, baselines, and validation constraints, while keeping Experiment A and Experiment B distinct descriptive studies. This is a research-design approval only; it does not authorize code changes, experiments, paper trading, live trading, or scaling.
- Human authorization (2026-10-16): implement the Box Theory candidate and its reproducible historical research runner. This authorization is limited to research implementation and historical backtesting; it does not authorize paper trading, live orders, or scaling.
- Approved segmented historical research mode: on 2026-10-14, the user approved a separate research mode that evaluates maximal contiguous 5-minute Kraken BTC/EUR segments as independent observation domains for historical research only. This approval is documentation-only and does not imply that a segmented backtest has been implemented, validated, or separately authorized to run. Any segmented backtest must wait until the required implementation scope, eligibility rules, and unresolved thresholds are explicitly settled and documented. This does not authorize continuous-history replay changes, paper trading, live trading, scaling, strategy profitability claims, or execution beyond the approved research scope.
- Live trading status: not allowed.
- Scaling status: not allowed without fresh evidence and human approval.

## Research workflow

1. Validate the Kraken source schema and UTC timestamp semantics.
2. Keep Experiment A and Experiment B as separate descriptive research questions unless a future comparison protocol is explicitly approved.
3. Reject ambiguous or missing windows instead of backfilling.
4. Record provenance, UTC bounds, validation counts, and known limitations.
5. Assess each descriptive outcome separately and do not claim cross-experiment superiority without a valid common comparison protocol.
6. Only after explicit approval may later stages consider broader validation, paper-trading readiness, or execution.

## Stage gates

### Stage 1 - Governance and scope

Status: complete.

Evidence:

- Project mission, risk boundaries, and no-assumptions rules are documented.
- Kraken BTC/EUR 5-minute OHLCV is the active descriptive research source.
- Legacy Tardis material remains historical evidence only and is not the current active source contract.

### Stage 2 - Data validation and source contract

Status: active.

Objective:

- Keep one valid source contract for the current descriptive study: Kraken OHLCV row semantics, 5-minute UTC alignment, sparse-gap handling, and fail-closed rejection rules.

### Stage 3 - Strategy specification

Status: active.

Objective:

- Keep the descriptive mechanics explicit and separate by experiment:
  - Experiment A: bullish-close signal, next-period return, baseline comparison, and same-eligible-observation logic.
  - Experiment B: local rejection/confirmation signal using the current implementation defaults, reported as a descriptive signal evaluation only.
  - Box Theory is the primary new experimental candidate: prior complete UTC-day range, lower-quarter rejection, next-candle-open entry, midpoint target, signal-low stop with explicit buffer, conservative OHLC exit ordering, and cost-aware simulated trades.
  - The trend-filtered price-channel breakout remains a separate research-only candidate with no execution claim.
  - Baselines B1 and B2 remain comparison methods, not approved production strategies.
  - Use the existing documented entry, confirmation, filter, exit, position-management, risk, and data-quality rules as the inventory for a holistic component-research design.
  - No look-ahead; no silent gap repair; no strategy-approval claim.

Required next dependency:

- Define the comparison semantics and candidate-combination protocol for justified component combinations before any integrated backtest, paper-trading design, or implementation change.

### Stage 4 - Historical analysis

Status: enabled for the Kraken sample, with a separately approved segmented research mode.

Objective:

- Run only bounded descriptive analysis over the retained Kraken OHLCV source and record all limits explicitly.
- Run the implemented Box Theory candidate as a bounded long-only spot historical backtest on Kraken BTC/EUR 5-minute OHLCV, preserving Experiment A and Experiment B as separate descriptive studies. Record source SHA-256, contiguous segments, eligible complete-day boxes, signals, trades, exit reasons, gross P&L, modeled costs, and net P&L. Treat outputs as research only.
- Segment the existing Kraken BTC/EUR 5-minute source into maximal contiguous 5-minute observation domains using actual timestamps, and evaluate those segments as independent historical research units without bridging or backfilling gaps.
- Do not treat the initial backtest as a profitability claim or as a live-trading approval.

Approved chronological split and selection policy (2026-10-15):

- Split the validated Kraken BTC/EUR 5-minute dataset chronologically into 60% training, 20% validation, and 20% final test.
- Do not allow any trade's entry-to-exit window to cross a partition boundary.
- Use only training and validation data for parameter selection.
- Keep the final test untouched until the selection procedure and selected parameters are fixed and documented.
- Define the partition boundaries using the valid retained source range and document the exact boundary timestamps and the handling of boundary candles.
- For each candidate parameter set, evaluate only signals whose entry and exit references both lie within the same partition.
- Record the final selection rule before final-test evaluation and do not inspect the final-test results during selection.
- If the source validation or boundary logic is ambiguous, stop and report the issue rather than guessing.

Segmented research policy (approved 2026-10-14):

- Split the source into maximal contiguous 5-minute segments using actual timestamps.
- Never backfill, bridge, or synthesize missing candles.
- Treat each segment as an independent observation domain.
- Reset strategy state, indicator/lookback warm-up, pending signals, open positions, and holding-period state at every segment boundary.
- Never open a trade unless the full required lookback and signal formation occur inside the same segment.
- Never carry an open position or holding period across a segment boundary; do not invent a boundary exit price or fill.
- Preserve the existing fail-closed behavior for any individual segment that violates timestamp, ordering, OHLCV, or other existing validity checks.
- Keep this segmented research mode explicitly separate from continuous-history replay; it does not weaken the existing contiguous-replay contract.
- Report segment counts and length distribution, excluded segments, eligible candles, signals, simulated trades, boundary-related exclusions, exit reasons, gross P&L, costs, and net P&L where the implementation supports them.
- Label outputs as segmented historical research only; they are not proof of profitability and do not authorize paper trading or live trading.
- Minimum segment length, minimum eligible-candle count, and minimum trade count remain unresolved decisions and must not be silently adopted without authoritative support.

### Stage 5 - Realistic validation and paper-trading readiness

Status: not started.

Objective:

- Determine whether any candidate survives realistic cost and execution constraints before broader decisions.

### Stage 6 - Controlled live test

Status: not started.

Objective:

- Permit only a tightly controlled spot test under explicit human approval and risk controls.

### Stage 7 - Controlled scaling

Status: not started.

Objective:

- Scale only after approval, evidence, and persistent risk checks.

## Historical artifacts retained as evidence only

- The legacy Tardis first-of-month manifest, sample output, and associated report remain in the repository as historical evidence.
- They are not treated as the active source requirement for current Kraken research.
- Their findings are not claimed to be replicated on Kraken.
- Any continuing references to first-of-month Tardis sampling must be read as historical context, not the active research contract.

## Provenance and reproducibility blockers

- The current Kraken manifest has `sha256: null` and therefore the exact raw-input identity is not yet cryptographically established.
- The repository does not yet prove full archive coverage or the exact UTC sink/selection boundary for the raw CSV from the available artifacts alone.
- The next validation stage requires raw-byte SHA-256, manifest identity, row count, timestamp bounds, validation counts, code identity, and deterministic output provenance before a rerun can be treated as a controlled reproduction.

## Known facts

- The project is for cryptocurrency spot trading only.
- The initial capital ceiling is EUR 50.
- The first live test should remain very small and controlled.
- The system must prioritize reproducibility, risk control, and honest evaluation over speed of deployment.
- The current Kraken dataset is the active descriptive source for this repository state.
- Historical Tardis-first-of-month artifacts remain preserved for traceability and audit, but they are not active-source requirements.

## Unknowns requiring human decision

- Whether a future comparison protocol will define a valid common comparison between Experiment A and Experiment B.
- Which markets will be monitored beyond the controlled research dataset.
- Which candle intervals will be evaluated beyond the current Kraken 5-minute research contract.
- Which numerical risk limits will govern live behavior.
- Which implementation stack will be used.

## Immediate next task

Review and fix the authoritative document set so that the active-source contract, the historical artifact status, and the separate A/B research boundaries remain consistent without changing experiment logic or raw data.