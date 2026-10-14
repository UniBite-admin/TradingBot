# Trading Bot - Kraken-Only Research Roadmap

## Purpose

This roadmap defines the current, provider-specific research path for the repository: Kraken BTC/EUR 5-minute OHLCV is the historical source, and all descriptive study work remains bounded and non-trading.

## Current status

- Historical source: Kraken BTC/EUR 5-minute OHLCV export under `data/kraken/`.
- Research scope: descriptive, sparse-sample, non-execution, and provider-specific.
- Implementation status: the repository contains Kraken validation and signal-analysis utilities, but no live-trading deployment or profitability claim is authorized.
- Live trading status: not allowed.
- Scaling status: not allowed without fresh evidence and human approval.

## Research workflow

1. Validate source schema and timestamp semantics.
2. Keep the Experiment A-equivalent mechanics fixed and provider-neutral.
3. Reject ambiguous or missing windows instead of backfilling.
4. Record provenance, UTC bounds, validation counts, and limitations.
5. Assess descriptive outcome only.
6. Only after explicit approval may later stages consider broader validation or execution.

## Stage gates

### Stage 1 - Governance and scope

Status: complete.

Evidence:

- Project mission, risk boundaries, and no-assumptions rules are documented.
- Kraken is the active research source and Tardis is removed from the active repository contract.

### Stage 2 - Data validation and source contract

Status: active.

Objective:

- Keep a single, valid source contract for Kraken OHLCV: row semantics, 5-minute alignment, sparse-gap handling, and fail-closed rejection rules.

### Stage 3 - Strategy specification

Status: active.

Objective:

- Keep the descriptive signal mechanics provider-independent:
  - signal = 1 if close > open
  - next-period return = (close_{k+1} - close_k) / close_k
  - baseline = unconditional positive-return rate on the same eligible observations
  - no look-ahead
  - no silent gap repair

### Stage 4 - Historical analysis

Status: enabled for the Kraken sample.

Objective:

- Run only bounded descriptive analysis over the retained Kraken OHLCV source and record all limits explicitly.

### Stage 5 - Realistic validation and paper-trading readiness

Status: not started.

Objective:

- Determine whether the strategy can survive realistic cost and execution constraints before any broader decision.

### Stage 6 - Controlled live test

Status: not started.

Objective:

- Permit only a tightly controlled spot test under explicit human approval and risk controls.

### Stage 7 - Controlled scaling

Status: not started.

Objective:

- Scale only after approval, evidence, and persistent risk checks.

## Known Facts

- The project is for cryptocurrency spot trading only.
- The initial capital ceiling is EUR 50.
- The first live test should remain very small and controlled.
- The system must prioritize reproducibility, risk control, and honest evaluation over speed of deployment.
- The current historical dataset is provisionally accepted for continued research under current access and budget constraints, but first-of-month sampling may introduce selection bias and may not represent the full month.
- A future full-month data acquisition remains a separate human budget decision and does not follow automatically from this provisional scope.

## Unknowns Requiring Human Decision

- Whether the bounded Tardis.dev Binance Jersey BTCEUR historical sample is sufficient for the first experiment and what statistical limitations it imposes.
- Whether a full-month historical purchase through the appropriate Tardis.dev access method is warranted under a separate future budget decision.
- Which markets will be monitored beyond the controlled research dataset.
- Which candle intervals will be evaluated.
- Which exact strategy hypothesis will be tested first.
- Which numerical risk limits will govern live behavior.
- Which implementation stack will be used.

## Immediate Next Task

Complete the Sprint 02 review of `ROADMAP.md` and `TECHNICAL_PLAN.md`, then resolve the implementation-blocking Stage 2 decisions required to freeze the first controlled historical research experiment before implementation begins.