# Trading Bot - Kraken-Only Research Roadmap

## Purpose

This roadmap defines the current, provider-specific research path for the repository: Kraken BTC/EUR 5-minute OHLCV is the active historical source for descriptive research, and all research remains bounded and non-trading.

## Current status

- Active source: Kraken BTC/EUR 5-minute OHLCV export under `data/kraken/`.
- Historical artifacts retained as evidence only: legacy Tardis first-of-month files and their associated reports are preserved for provenance and comparison, but they are not the active repository input contract.
- Research scope: descriptive, provider-specific, non-execution, and fail-closed against ambiguous source semantics.
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
  - No look-ahead; no silent gap repair; no strategy-approval claim.

### Stage 4 - Historical analysis

Status: enabled for the Kraken sample.

Objective:

- Run only bounded descriptive analysis over the retained Kraken OHLCV source and record all limits explicitly.

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