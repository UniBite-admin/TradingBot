# Trading Bot - Authoritative Roadmap

## Purpose

This roadmap defines the approved project sequence and the current blocked decisions required before implementation begins.

This file is the authoritative roadmap for the repository.

## Current Status

- Stage: Definition and planning.
- Implementation status: Not started.
- Strategy status: Specification drafted and pending human review; not approved.
- Exchange status: Bitvavo Spot intended execution venue selected; historical research source provisionally set to Tardis.dev Binance Jersey BTCEUR quotes and trades with daily `.csv.gz` files limited to the first calendar day of each month only; the first experiment remains unapproved.
- Historical-sample status: the first-of-month sample is provisionally accepted for continued research under current data-access and budget constraints, but it is not yet a final adequacy validation and may not represent the full month.
- Live trading status: Not allowed.
- Decision authority: delegated by the project owner to ChatGPT on 2026-10-11. Classification: human-authorized delegated decision. The project owner delegated the decision; the specific choice was made under that delegation.
- Delegated-scope limitation: this delegation does not authorize live trading activation, real-money trading, exchange orders, deployment, or advancement to later project phases beyond the bounded research scope recorded in `S3D-007` through `S3D-013`.

## Approved Workflow

The project advances only through the following sequence:

1. Project definition and governance.
2. Technical planning.
3. Strategy specification.
4. Market data and research environment setup.
5. Backtesting implementation.
6. Validation with realistic costs and constraints.
7. Paper trading.
8. Controlled small live test.
9. Evaluation.
10. Controlled scaling only if evidence supports it.

## Stage Gates

### Stage 1 - Project definition and governance

Status: Complete.

Exit evidence:

- Project mission, boundaries, and operating principles documented.
- Capital protection and no-assumptions governance documented.
- Authoritative definition and roadmap created.

### Stage 2 - Technical planning

Status: Handover to Sprint 03.

Objective:

- Define the minimum system architecture required for research and controlled execution.

Required decisions:

- Historical-data adequacy and statistical validity of the bounded Tardis.dev Binance Jersey BTCEUR sample for the first experiment.
- Market universe selection method.
- Candle intervals.
- Data sources.
- Initial language and runtime.
- Storage requirements.
- Logging and experiment tracking approach.

Required outputs:

- Technical architecture outline.
- Component boundaries.
- Initial repository layout.
- Environment and secret-handling rules.

Current repository evidence:

- `TECHNICAL_PLAN.md` records the proposed comprehensive technical plan and implementation roadmap for review.
- Sprint 02 closed after documenting the unresolved Stage 2 evidence gaps and transferring them to Sprint 03.

Blocked by:

- unresolved evidence gates beyond the bounded research scope,
- the remaining validation, realism, and profitability requirements for later project stages,
- continued stage-gate discipline before broader implementation or paper/live activation.

Previously unowned Stage 2 decisions are now resolved for the bounded research scope under the delegated authority recorded in `S3D-007` through `S3D-013`:

- `S3D-008` - BTC-EUR only for the first bounded experiment.
- `S3D-009` - Python 3.12 for the initial research environment, with compatibility and verification still required.
- `S3D-010` - file-based, reproducible artifacts for the bounded experiment; no new database required solely for this experiment.
- `S3D-011` - Python standard logging plus structured, machine-readable experiment records using existing repository conventions.

These delegated decisions resolve the earlier ownership gap only within the bounded, exploratory research scope. They do not authorize broader implementation, paper trading, live trading, or scaling.

### Stage 3 - Strategy specification

Status: In progress.

Objective:

- Define one explicit candlestick-based strategy hypothesis without silent parameters.

Required decisions:

- Entry conditions.
- Exit conditions.
- Invalidation rules.
- Timeframe.
- Candidate assets or asset-selection rules.
- Position sizing method.
- Risk constraints.

Required outputs:

- Testable strategy specification.
- Clear distinction between hypothesis, approved rule, implemented rule, and validated result.

Current repository evidence:

- `STRATEGY_SPECIFICATION.md` records the proposed candlestick strategy specification for review.

Blocked by:

- Human approval of a concrete strategy specification.

### Stage 4 - Market data and research environment setup

Status: Not started.

Objective:

- Build the minimum data pipeline required to collect and inspect historical candlestick data for approved markets.

Required outputs:

- Verified data ingestion path.
- Reproducible research environment.
- Initial data quality checks.

### Stage 5 - Backtesting implementation

Status: Not started.

Objective:

- Implement a reproducible backtest for the approved strategy.

Required outputs:

- Strategy evaluation against historical data.
- Versioned configurations and run metadata.
- Reproducible result artifacts.

### Stage 6 - Validation with realistic costs and constraints

Status: Not started.

Objective:

- Determine whether the strategy remains viable after fees, spread, slippage, latency, liquidity limits, and order constraints.

Required outputs:

- Validation report with explicit assumptions.
- Failure analysis where profitability degrades under realistic execution.

### Stage 7 - Paper trading

Status: Not started.

Objective:

- Verify operational behavior without risking capital.

Required outputs:

- Decision logs.
- Order simulation evidence.
- Operational incident log.

### Stage 8 - Controlled small live test

Status: Not started.

Objective:

- Run a tightly constrained live spot test only after paper-trading evidence supports it.

Hard preconditions:

- Spot-only exchange configuration.
- No withdrawal permission on API keys.
- Approved numeric risk limits.
- Emergency stop tested.
- Human approval for live deployment.

### Stage 9 - Evaluation

Status: Not started.

Objective:

- Compare research, paper, and live results and decide whether the strategy has repeatable positive expectancy.

### Stage 10 - Controlled scaling

Status: Not started.

Objective:

- Scale only if evidence supports it and risk controls remain effective.

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