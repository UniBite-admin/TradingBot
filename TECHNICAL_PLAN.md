# Trading Bot - Comprehensive Technical Plan and Implementation Roadmap

## Document Status

- Status: Proposed for human review.
- Approval state: Not approved.
- Implementation state: Not implemented.
- Repository state: Planning only.
- Live-readiness state: Not ready.

Classification used in this document:

- `FACT`: established by repository evidence.
- `APPROVED`: explicitly approved by authoritative repository documents.
- `PROPOSED`: recommended in this plan but not yet approved.
- `UNRESOLVED DECISION`: materially affects implementation and requires human approval.
- `BLOCKER`: prevents safe progression to the affected phase.

## Part 1 - Repository Findings

### What Exists

`FACT`: The repository currently contains only the following files:

- `PROJECT_DEFINITION.md`
- `ROADMAP.md`
- `README.md`
- `STRATEGY_SPECIFICATION.md`

`FACT`: No implementation artifacts currently exist.

- No source code.
- No tests.
- No configuration files.
- No environment files.
- No dependency manifest.
- No data files.
- No CI configuration.
- No persistence schema.

`FACT`: Git is not initialized in the workspace. An attempted `git status --short --branch` returned `fatal: not a git repository`.

### What Is Authoritative

- `PROJECT_DEFINITION.md`: authoritative for mission, governance, scope, safety boundaries, and engineering principles.
- `ROADMAP.md`: authoritative roadmap.
- `STRATEGY_SPECIFICATION.md`: authoritative record of the current proposed strategy specification, but not approved.
- `README.md`: project entrypoint only.

### What Is Approved

`APPROVED`:

- Project mission: research-driven crypto trading system focused on short-term candlestick-based analysis.
- Scope: spot-only trading.
- Exclusions: no leverage, no margin, no futures, no perpetuals.
- Governance: no silent assumptions, evidence over intuition, risk authority over strategy, reproducibility required.
- Validation path: historical research -> backtesting -> realistic validation -> paper trading -> controlled small live test -> evaluation -> scaling decision.
- Multi-asset intent: the system should be able to monitor multiple markets and compare opportunities under documented rules.

### What Is Not Approved

`FACT`: The current strategy document explicitly states that it is proposed for human review and not approved.

`UNRESOLVED DECISION`:

- Exchange.
- Market universe.
- Candle timeframe.
- Candle timestamp semantics.
- Missing-candle policy.
- Technology stack.
- Storage approach.
- Logging and experiment tracking approach.
- Numerical risk limits.
- Position sizing policy.
- Maximum simultaneous positions.
- Paper-trading design details.
- Live deployment and authorization details.

### Conflict Assessment

`FACT`: No direct contradiction was found across the repository documents.

`FACT`: The only meaningful planning constraint is that Stage 2 technical planning should happen before implementation, while the strategy specification exists but remains unapproved. That is consistent.

`CONCLUSION`: Architecture and implementation planning may reference the current strategy specification as a proposed input, but not as an approved implementation requirement.

## Part 2 - Architecture Proposal

## Architecture Summary

`PROPOSED`: The first system should be a single-process modular monolith with strict logical boundaries and durable event recording where safety, auditability, and reproducibility matter.

Reasons:

- Smallest system that can answer the research question.
- Lower operational complexity than multi-service designs.
- Easier deterministic replay and debugging.
- Easier consistency between backtest, replay, paper, and later live logic.

The design should preserve the following invariants:

- A strategy signal is not an order.
- A risk approval is not an order submission.
- An order acknowledgement is not a fill.
- A fill is not final accounting until fees and position effects are reconciled.
- Missing or inconsistent essential state must block new exposure.
- The Risk Engine is an independent authorization boundary.
- Every material decision must be reproducible from recorded inputs, configuration, and state.

## Logical Components

### 1. Market Data

- Purpose: acquire raw public market data and, later, private exchange events.
- Responsibilities: source connectivity, event acquisition, health observation, source metadata.
- Inputs: REST, WebSocket, or historical replay inputs.
- Outputs: raw normalized market events and source health state.
- Authoritative data owned: connection and source state only.
- Dependencies: approved exchange and source semantics.
- Failure modes: disconnects, stale feeds, rate limits, gaps, duplicates.
- Recovery behavior: reconnect, gap fill where supported, mark source unhealthy, block new entries if unresolved.
- Logging: connection lifecycle, lag, reconnects, gaps, sequence anomalies.
- Unit and integration tests: source adapter contracts, reconnect logic, stale-feed detection.
- Acceptance criteria: produces ordered events with explicit health state.
- Immediate or deferred: required immediately.

### 2. Data Validation and Normalization

- Purpose: enforce source-agnostic structure and reject unusable inputs.
- Responsibilities: schema validation, timestamp checks, duplicate detection, ordering rules.
- Inputs: raw market events.
- Outputs: validated normalized events or explicit rejection records.
- Authoritative data owned: validation decisions.
- Dependencies: event schemas and timestamp semantics.
- Failure modes: impossible prices, invalid timestamps, duplicates, out-of-order records.
- Recovery behavior: reject or quarantine affected stream; request resync if supported.
- Logging: validation failures with explicit reason.
- Tests: deterministic fixtures for invalid, duplicate, stale, and out-of-order events.
- Acceptance criteria: invalid inputs never silently pass.
- Immediate or deferred: required immediately.

### 3. Candle Construction or Candle Ingestion

- Purpose: create or accept OHLCV candles and track commitment status.
- Responsibilities: candle series maintenance, bar finalization, gap detection.
- Inputs: normalized trades or exchange-provided candles.
- Outputs: committed candles, in-progress candles, candle health state.
- Authoritative data owned: candle state and finalization status.
- Dependencies: approved timeframe and candle semantics.
- Failure modes: missing intervals, partial bars, source inconsistency.
- Recovery behavior: mark context incomplete and block strategy evaluation where required.
- Logging: candle gaps, finalization transitions, source discrepancies.
- Tests: bar finalization, missing interval handling, timestamp semantics, anti-lookahead.
- Acceptance criteria: committed bars are explicitly distinguishable from in-progress bars.
- Immediate or deferred: required immediately.

### 4. Feature and Signal Calculation

- Purpose: derive deterministic strategy inputs from eligible committed candles.
- Responsibilities: feature generation, lookback enforcement, data-quality propagation.
- Inputs: committed candles and approved parameters.
- Outputs: feature snapshots with exact timing and source references.
- Authoritative data owned: derived feature snapshots.
- Dependencies: approved strategy data contract.
- Failure modes: insufficient lookback, stale context, missing bars.
- Recovery behavior: emit explicit unavailable status instead of fabricating values.
- Logging: feature readiness and missing-context reasons.
- Tests: deterministic replay and feature timing correctness.
- Acceptance criteria: no feature uses future data.
- Immediate or deferred: required immediately.

### 5. Strategy Engine

- Purpose: evaluate the approved strategy using feature and candle context.
- Responsibilities: rule evaluation, signal generation, rejection reason generation, reproducibility metadata.
- Inputs: feature snapshots, candle references, strategy parameters.
- Outputs: strategy proposals or strategy rejections.
- Authoritative data owned: strategy decision records.
- Dependencies: approved or explicitly authorized provisional strategy version.
- Failure modes: unresolved rules, missing features, ambiguous timing.
- Recovery behavior: reject signal generation.
- Logging: rule evaluations, triggered rules, rejection reasons.
- Tests: per-rule tests, replay determinism, anti-lookahead tests.
- Acceptance criteria: identical inputs reproduce identical signals.
- Immediate or deferred: required immediately after strategy approval.

### 6. Opportunity Ranking

- Purpose: compare simultaneous strategy proposals across markets.
- Responsibilities: deterministic ordering, stale proposal removal, limited candidate set selection.
- Inputs: strategy proposals, market health, portfolio state summaries.
- Outputs: ranked candidate list.
- Authoritative data owned: ranking results only.
- Dependencies: approved ranking policy and portfolio constraints.
- Failure modes: stale proposals, ties, excessive candidate volume.
- Recovery behavior: deterministic tie-breaks and stale proposal pruning.
- Logging: ranking inputs, ordering, and exclusions.
- Tests: tie handling, stale handling, deterministic sorting.
- Acceptance criteria: same inputs produce same order.
- Immediate or deferred: optional for single-market research; required before full multi-asset paper or live use.

### 7. Risk Management

- Purpose: independently authorize or deny trade proposals.
- Responsibilities: exposure checks, capital checks, operational-safety checks, fail-safe denial.
- Inputs: strategy proposals, balances, open orders, positions, exchange constraints, market health, approved risk config.
- Outputs: approve, deny, or fail-safe block decisions with reasons.
- Authoritative data owned: risk decision record.
- Dependencies: approved risk parameters and reconciled system state.
- Failure modes: unknown balances, unresolved orders, stale market data, inconsistent positions.
- Recovery behavior: deny by default.
- Logging: full input set and decision trace.
- Tests: per-control tests, fail-safe tests, restart-state tests.
- Acceptance criteria: no order can be submitted without an explicit approval record.
- Immediate or deferred: simplified form required for research simulation; full form required before paper or live trading.

### 8. Order Execution

- Purpose: convert approved order intents into simulator or exchange actions.
- Responsibilities: pre-submission validation, client-order identity, submission, timeout handling, reconciliation triggers.
- Inputs: risk-approved order intents, exchange constraints, mode configuration.
- Outputs: order-state events, fill events, and submission outcomes.
- Authoritative data owned: client order identifiers and submission records.
- Dependencies: exchange adapter or simulator, reconciliation support.
- Failure modes: timeout, ambiguous outcome, rejection, partial fill, disconnect.
- Recovery behavior: reconcile before retrying; never blind-resubmit.
- Logging: outbound requests, responses, correlation IDs, retry suppression reasons.
- Tests: timeout ambiguity, rejection, partial fill, retry safety.
- Acceptance criteria: duplicate order exposure is prevented under retry pressure.
- Immediate or deferred: simulator required for research; real exchange execution deferred.

### 9. Position Management

- Purpose: maintain position state from fills and reconciled exchange state.
- Responsibilities: local position transitions, open-order linkage, divergence detection.
- Inputs: fill events, order-state events, reconciliation results.
- Outputs: position state and exposure summaries.
- Authoritative data owned: local position model.
- Dependencies: execution events and accounting.
- Failure modes: partial fills, late fills, position mismatch.
- Recovery behavior: reconciliation workflow and fail-safe entry block.
- Logging: position transitions and divergence alerts.
- Tests: partial fill flows, cancel-then-fill flows, restart recovery.
- Acceptance criteria: position state can be reconstructed from persisted evidence.
- Immediate or deferred: required for simulation; full reconciliation required before paper or live.

### 10. Accounting and Trade Ledger

- Purpose: record the economic outcome of all trading activity and rejected actions.
- Responsibilities: fee handling, realized and unrealized P&L, trade linkage, completeness flags.
- Inputs: fills, fees, position closures, reconciliation results, failed operations.
- Outputs: ledger entries and performance-ready accounting records.
- Authoritative data owned: economic ledger.
- Dependencies: fill completeness and fee information.
- Failure modes: missing fees, incomplete order linkage, divergence from exchange records.
- Recovery behavior: mark results incomplete and block profitability claims.
- Logging: accounting adjustments and unresolved links.
- Tests: fee accounting, realized P&L, partial closes, incomplete data behavior.
- Acceptance criteria: a trade outcome is reconstructible from recorded evidence.
- Immediate or deferred: required immediately for research validity.

### 11. Persistence and Event Logging

- Purpose: make material state recoverable and auditable.
- Responsibilities: durable storage of domain events, checkpoints, run metadata, and logs.
- Inputs: all material domain events and state snapshots.
- Outputs: durable records and restart checkpoints.
- Authoritative data owned: persisted event and state history.
- Dependencies: storage technology choice.
- Failure modes: disk-full conditions, write failures, corruption.
- Recovery behavior: fail safe and block new entries if durability is compromised.
- Logging: write failures and checkpoint health.
- Tests: write-failure handling, restart recovery, schema compatibility.
- Acceptance criteria: restart can recover known-safe state and explicitly flag unknown state.
- Immediate or deferred: required immediately.

### 12. Performance Analytics

- Purpose: derive research and operational metrics from ledger and decision data.
- Responsibilities: report generation, segmentation, baseline comparison, cost sensitivity summaries.
- Inputs: ledger, fills, strategy records, rejection records, run metadata.
- Outputs: reproducible reports and metrics.
- Authoritative data owned: derived analytics only.
- Dependencies: accurate accounting and provenance records.
- Failure modes: incomplete inputs causing misleading reports.
- Recovery behavior: mark reports incomplete and list missing inputs.
- Logging: report provenance and config version.
- Tests: metric formula correctness and segmentation checks.
- Acceptance criteria: reports are reproducible from versioned inputs.
- Immediate or deferred: required for research; richer dashboards deferred.

### 13. Monitoring and Operational Safety

- Purpose: detect unsafe runtime conditions and enforce safe degradation.
- Responsibilities: freshness checks, latency checks, emergency stop, entry blocking, manual intervention signals.
- Inputs: health metrics from data, execution, persistence, reconciliation, and risk.
- Outputs: alerts, blocked-entry state, emergency-stop state.
- Authoritative data owned: health state and emergency-stop state.
- Dependencies: explicit health rules and thresholds.
- Failure modes: silent data freeze, unresolved orders, persistence loss, divergence.
- Recovery behavior: block new exposure and require reconciliation or manual review.
- Logging: health-state transitions and causes.
- Tests: stale-feed blocking, emergency-stop behavior, restart safety.
- Acceptance criteria: unsafe conditions reliably prevent new entries.
- Immediate or deferred: minimal health blocking required early; full operational safety required before paper or live.

### 14. Backtesting and Historical Replay

- Purpose: replay chronological data using shared live semantics.
- Responsibilities: deterministic replay clock, information-availability control, run metadata.
- Inputs: validated historical data, strategy version, cost model, config.
- Outputs: simulated decisions, orders, fills, accounting, metrics.
- Authoritative data owned: replay run records.
- Dependencies: candle semantics, strategy rules, execution simulation, accounting.
- Failure modes: look-ahead leakage, wrong ordering, unrealistic fills.
- Recovery behavior: invalidate run and surface violation.
- Logging: run metadata, data versions, anomalies.
- Tests: deterministic replay and chronological integrity.
- Acceptance criteria: identical dataset and config reproduce identical results.
- Immediate or deferred: required immediately for research.

### 15. Paper Trading

- Purpose: verify operational behavior without risking capital.
- Responsibilities: live data intake, simulated orders, operational incident tracking, semantic comparison to research assumptions.
- Inputs: live market data, simulated balances, exchange constraints.
- Outputs: paper-trading records, simulated fills, incident logs.
- Authoritative data owned: paper session records.
- Dependencies: approved exchange, risk engine, monitoring, reconciliation.
- Failure modes: semantic drift, data outages, unresolved order states.
- Recovery behavior: block progression to live if drift or instability appears.
- Logging: full live-style decision trail.
- Tests: mode safety, feed health, recovery from disconnects.
- Acceptance criteria: paper mode behaves consistently with system assumptions and safety rules.
- Immediate or deferred: deferred until post-research stages.

### 16. Configuration and Secrets Management

- Purpose: control system behavior safely by explicit configuration.
- Responsibilities: config schema validation, mode safety, secret loading, redaction.
- Inputs: environment variables, config files, runtime mode settings.
- Outputs: validated runtime config and safe secret handles.
- Authoritative data owned: config validation results.
- Dependencies: runtime stack and deployment approach.
- Failure modes: invalid config, missing secrets, accidental live mode.
- Recovery behavior: startup failure and no-trade default.
- Logging: validation results with secrets redacted.
- Tests: invalid config rejection and live-mode safeguard tests.
- Acceptance criteria: live trading cannot activate by accident.
- Immediate or deferred: required immediately in minimal form.

## First Working Research System Scope

`PROPOSED`: The first working research system should include:

- Market Data
- Data Validation and Normalization
- Candle Handling
- Feature Calculation
- Strategy Engine
- Simplified Risk boundary
- Execution simulator
- Position Management
- Accounting and Trade Ledger
- Persistence and Event Logging
- Backtesting and Historical Replay
- Configuration and Secrets Management

`PROPOSED`: The following can be deferred until later stages:

- Real exchange private execution adapter
- Full paper-trading mode
- Rich monitoring stack
- Advanced multi-asset ranking heuristics
- Advanced reconciliation tooling
- Deployment automation

## Part 3 - Technology Proposal

## Recommended Minimal Stack

### Programming Language and Runtime

`UNRESOLVED DECISION`: language and runtime.

`PROPOSED`: Python 3.12.

Why it is appropriate:

- Good fit for research, replay, data validation, and reporting.
- Strong testing ecosystem.
- Lower implementation friction for an early-stage project.
- Correctness and reproducibility matter more than low-level performance at current scope.

Alternatives considered:

- .NET: stronger static typing and runtime structure, but more friction for fast research iteration.
- TypeScript: good tooling, but weaker fit for numerical and research workflows.

Operational and maintenance costs:

- Requires disciplined testing because it is dynamically typed.
- Performance is sufficient at current scope, but not a reason to overengineer prematurely.

Decision status: recommended, not approved.

### Dependency and Environment Management

`UNRESOLVED DECISION`: dependency management approach.

`PROPOSED`: standard `venv` with pinned dependencies in a `pyproject.toml`-based workflow.

Why it is appropriate:

- Minimal complexity.
- Reproducible local environment.
- Compatible with common tooling.

Alternatives considered:

- Poetry.
- Conda.
- `uv`.

Decision status: recommended, not approved.

### Exchange Integration

`UNRESOLVED DECISION`: exchange.

`PROPOSED`: direct exchange adapter against the selected exchange documentation rather than relying on a high-level abstraction library for execution-critical behavior.

Why it is appropriate:

- Preserves exchange-specific semantics for order states, candles, limits, and fees.
- Reduces abstraction leakage in execution and reconciliation.

Alternative considered:

- CCXT or similar abstraction library.

Cost and reliability implications:

- More initial implementation work.
- Higher confidence in execution correctness.

Decision status: blocked pending exchange approval.

### Historical Market Data

`PROPOSED`: use exchange-native historical OHLCV if adequate; otherwise a documented secondary vendor with explicit provenance.

Why it is appropriate:

- Keeps live and research semantics aligned.
- Preserves traceability.

Decision status: blocked pending exchange and data-source approval.

### Persistence

`PROPOSED`: SQLite in WAL mode for durable local storage.

Why it is appropriate:

- Smallest durable store that supports auditability, replay metadata, and restart recovery.
- No need to operate a separate server.

Alternatives considered:

- Postgres.
- Flat files only.

Operational and maintenance costs:

- SQLite is sufficient for a single-process early-stage system.
- It becomes insufficient if multi-process concurrent write pressure or multi-user remote access becomes necessary.

Decision status: recommended, not approved.

### Structured Logging

`PROPOSED`: JSON lines.

Why it is appropriate:

- Easy to parse, search, archive, and attach to experiment artifacts.

Alternative considered:

- Plain text logs.

Decision status: recommended, not approved.

### Configuration Format

`PROPOSED`: TOML or YAML plus environment variables for secrets.

Recommended option:

- TOML preferred for lower ambiguity.

Decision status: recommended, not approved.

### Testing Framework

`PROPOSED`: pytest.

Why it is appropriate:

- Strong unit, integration, replay, and parameterized-test support.

Decision status: recommended, not approved.

### Backtesting and Replay

`PROPOSED`: custom event-driven replay kernel sharing live semantics.

Why it is appropriate:

- Prevents silent drift between research and live logic.
- Supports deterministic ordering and explicit information availability.

Alternative considered:

- Vectorized-only backtesting framework.

Decision status: recommended, not approved.

### Reporting

`PROPOSED`: generated markdown, CSV, and optional plots from versioned run artifacts.

Why it is appropriate:

- Sufficient for reproducible review without adding dashboard infrastructure.

Decision status: recommended, not approved.

### Continuous Integration

`PROPOSED`: lightweight CI after Git is initialized.

Why it is appropriate:

- Maintains test discipline once code exists.

Decision status: blocked until version control is established.

### Deployment and Monitoring

`PROPOSED`: no deployment platform initially; local research first.

Why it is appropriate:

- The project is still in the planning stage.
- Operational infrastructure is premature until research justifies it.

Decision status: recommended, not approved.

## Part 4 - Detailed Technical Design

## End-to-End Data and Decision Flow

The complete flow is:

`Market Data -> Validation -> Candles -> Features -> Strategy -> Opportunity Ranking -> Risk Approval -> Execution -> Position Management -> Accounting -> Analytics`

### Flow Description

1. Market data enters from a replay source, exchange REST, or exchange WebSocket.
2. Validation and normalization enforce schema, ordering, and time semantics.
3. Candle handling produces committed and in-progress candle state.
4. Features are calculated only from information available at evaluation time.
5. Strategy rules emit either a proposal or a rejection record.
6. Opportunity ranking compares concurrent proposals across markets where applicable.
7. Risk approval independently authorizes or blocks the proposal.
8. Approved proposals become order intents.
9. Execution submits intents to a simulator or exchange adapter.
10. Order and fill reconciliation update positions.
11. Accounting records the actual economic outcome.
12. Analytics derive metrics from accounting and run metadata.

### Boundary Distinctions

The system must explicitly preserve these distinctions:

- Signal != order.
- Approved order intent != submitted exchange order.
- Exchange acknowledgement != fill.
- Fill != reconciled position state.
- Reconciled position state != complete accounting until fees are known.

### Duplicate-Processing Prevention

`PROPOSED`:

- Stable event identifiers for normalized market events.
- Deterministic candle keys: symbol + timeframe + open time.
- Stable signal identifiers derived from strategy version, symbol, timeframe, and confirmation-candle close time.
- Client order identifiers generated and persisted before submission.
- Reconcile-before-retry rule for ambiguous timeouts.

### Stale-Signal Prevention

`PROPOSED`:

- Every proposal includes an expiry timestamp.
- Ranking drops expired proposals.
- Risk decisions reference a specific proposal instance.
- Execution refuses expired or superseded intents.

### Inconsistent Position and Accounting Prevention

`PROPOSED`:

- Positions derive from fills and reconciled adjustments, not from requested orders.
- Rejected risk decisions create no executed-trade ledger entries.
- Acknowledged orders create no realized P&L.
- Profitability claims remain blocked when accounting completeness is false.

## Multi-Asset Architecture and Opportunity Ranking

`PROPOSED`: represent each market as an independent state object containing:

- symbol metadata,
- market-data health,
- latest committed and in-progress candle state,
- feature readiness,
- latest signal state,
- open-order and position summaries.

The system should:

- process markets independently,
- serialize portfolio-affecting decisions through the Risk Engine,
- mark lagging or stale markets ineligible,
- never allow simultaneous signals to bypass capital and exposure controls.

### Market Discovery and Eligibility

`UNRESOLVED DECISION`: market universe and discovery policy.

`PROPOSED`: start with a small curated set of liquid spot pairs after approval, not full dynamic discovery.

### Ranking Policy

`PROPOSED`: keep the first ranking policy minimal and deterministic.

Allowed early ranking inputs:

- signal freshness,
- data-health eligibility,
- execution-constraint eligibility,
- deterministic symbol ordering as a final tie-break.

`FACT`: ranking weights or learned scoring are not currently approved and should not be invented.

## Strategy Integration Contract

`FACT`: `STRATEGY_SPECIFICATION.md` is proposed, not approved.

Architecture must therefore support:

- strategy versioning,
- explicit provisional strategy status,
- rule-level identifiers,
- signal expiry,
- rule-level rejection reasons,
- reproducibility metadata.

The strategy input contract should include:

- symbol,
- timeframe,
- candle references,
- feature snapshot timestamp,
- feature values,
- data-quality flags,
- strategy version and parameter set.

The strategy output contract should include:

- signal identifier,
- side,
- creation timestamp,
- expiry timestamp,
- entry rule identifiers,
- rejection rule identifiers where applicable,
- invalidation reference values,
- reference prices,
- decision rationale,
- reproducibility metadata.

The architecture must keep separate:

- strategy rules,
- ranking logic,
- risk authorization,
- execution,
- position management,
- accounting.

## Risk Management Architecture

The Risk Engine is an independent authorization boundary.

### Required Controls

The design must support checks for:

- maximum position size,
- maximum risk per trade,
- available balances,
- capital allocation,
- existing exposure,
- maximum simultaneous positions,
- maximum daily loss,
- maximum consecutive losses,
- market-data health,
- abnormal market conditions,
- exchange connectivity,
- unresolved order and position state,
- minimum order constraints,
- emergency stop,
- restart and recovery safety.

### Control Behavior

For every control:

- required inputs must be explicit,
- the Risk Engine owns the decision,
- failure behavior is deny-by-default,
- the output is a structured approve or reject record,
- relevant unit and integration tests are mandatory.

`FACT`: numerical limits are unresolved and must not be invented here.

Numerical risk decisions still requiring approval:

- position-size limits,
- risk per trade,
- daily loss limits,
- consecutive loss limits,
- maximum simultaneous positions,
- capital-allocation policy.

## Execution and Position Management

The order lifecycle should explicitly model:

- created,
- submitted,
- acknowledged,
- partially filled,
- filled,
- cancel requested,
- canceled,
- rejected,
- timed out with unknown outcome,
- reconciled closed.

Execution design requirements:

- pre-submission validation,
- idempotent client-order identifiers,
- ambiguity-safe timeout handling,
- no blind retries,
- explicit partial-fill handling,
- explicit late-fill-after-cancel handling,
- restart reconciliation before new exposure.

`FACT`: canceling an order does not guarantee that no later fill can occur.

## Accounting, Persistence, and Auditability

The system must record:

- market-data references,
- strategy evaluations,
- risk decisions,
- order requests,
- exchange order identifiers,
- order-state transitions,
- partial and final fills,
- fees,
- position changes,
- realized and unrealized P&L,
- rejected and failed operations,
- recovery checkpoints,
- reconciliation results.

Authoritative-state guidance:

- strategy evaluation records own the decision rationale,
- execution state owns order-state history,
- fill records own executed quantity and fee evidence,
- positions own local exposure state,
- the ledger owns realized economic interpretation.

`PROPOSED`: SQLite is the simplest persistence approach that satisfies current requirements.

## Historical Data, Backtesting, and Replay

Historical research pipeline requirements:

- documented provenance,
- explicit timestamp semantics,
- duplicate detection,
- ordering validation,
- missing-interval handling,
- invalid-price rejection,
- asset or market-rule change tracking,
- fee modeling,
- spread and slippage modeling,
- liquidity feasibility checks,
- latency assumptions,
- partial fill and failed-order handling,
- minimum-order constraints,
- portfolio capital constraints.

The live and historical systems should share strategy semantics wherever practical.

The replay model must preserve chronological information availability and prevent look-ahead.

Minimum evidence before a backtest result can be considered valid:

- validated input dataset,
- versioned strategy and configuration,
- chronological replay,
- explicit cost model,
- accounting completeness,
- out-of-sample separation,
- reproducible result artifacts.

## Testing and Quality Assurance

### Unit Tests

Must cover:

- deterministic calculations,
- validation rules,
- state transitions,
- risk checks,
- accounting formulas,
- config validation,
- strategy rule logic.

### Integration Tests

Must cover:

- market-data processing boundaries,
- persistence,
- exchange adapter contracts,
- order lifecycle,
- reconciliation,
- risk-to-execution gating.

### Replay and Backtest Tests

Must cover:

- deterministic replay,
- chronological correctness,
- accounting consistency,
- execution-cost model application.

### Failure-Injection Tests

Must cover:

- disconnects,
- timeouts,
- stale data,
- duplicate events,
- delayed responses,
- partial fills,
- process restarts,
- inconsistent exchange state,
- persistence failures.

### Security Tests

Must cover:

- secret redaction,
- safe configuration handling,
- prevention of withdrawal-enabled credential use where inspectable,
- mode-safety for live execution.

### Anti-Lookahead Tests

Must cover:

- incomplete candles,
- future information leakage,
- feature timing,
- signal availability timing,
- execution timestamp separation from signal timestamp.

### Regression Tests

Must cover:

- previously verified behavior after future changes.

Test success should be measured by:

- correctness against explicit expected outcomes,
- deterministic reproducibility,
- safe failure behavior,
- preserved invariants.

Passing tests do not prove profitability.

## Monitoring, Reliability, and Emergency Controls

The system must detect and respond to:

- market-data staleness,
- connectivity loss,
- API errors,
- rate limiting,
- processing delays,
- missed events,
- order submission latency,
- unresolved order states,
- position or accounting divergence,
- abnormal loss behavior,
- persistence failures,
- configuration errors,
- emergency-stop activation.

Required behaviors:

- some failures must block new entries,
- some failures must trigger reconciliation,
- some failures must require manual intervention,
- emergency stop must prevent new exposure,
- existing-position treatment during emergency must be explicitly specified and tested later.

## Security and Operational Safety

The system should enforce:

- API-key storage outside source-controlled files,
- least-privilege permissions,
- separation of public and private API access,
- secret redaction in logs,
- safe configuration validation,
- local environment isolation,
- repository secret protection,
- CI security checks after version control exists,
- explicit research, paper, and live mode separation,
- explicit safeguards preventing accidental live execution.

`APPROVED`: withdrawal permission must never be enabled for trading API keys.

## Part 5 - Comprehensive Implementation Roadmap

`PROPOSED`: Use 12 implementation phases rather than a longer artificially segmented roadmap. Each phase should deliver a coherent, verifiable capability.

### Phase 1 - Baseline Decisions and Repository Readiness

- Objective: freeze enough decisions to begin implementation safely.
- Why necessary: current repository has no code and no version-control baseline.
- Entry conditions: current documents reviewed.
- Inputs and dependencies: authoritative docs.
- Exact work items:
  - initialize decision register,
  - choose version-control workflow,
  - choose language and runtime,
  - decide whether provisional strategy implementation is allowed before formal strategy approval,
  - decide exchange-selection policy.
- Expected files or modules when justified: documentation updates only after authorization.
- Interface contracts affected: none.
- Test requirements: none beyond document review.
- Verification procedures: human review of decisions.
- Measurable acceptance criteria: implementation-blocking decisions are explicitly recorded.
- Required evidence and artifacts: approved decision record.
- Known limitations after completion: strategy still not validated.
- Explicitly excluded work: production code, dependency installation, data acquisition.
- Failure and rollback considerations: stop if decisions conflict or remain ambiguous.
- Decisions requiring human approval: yes.
- Blockers to next phase: unresolved language or exchange-selection policy.

### Phase 2 - Architecture and Interface Freeze

- Objective: freeze module boundaries, core contracts, and invariants.
- Why necessary: prevents semantic drift between research and later live behavior.
- Entry conditions: Phase 1 decisions recorded.
- Inputs and dependencies: language direction, proposed strategy contract.
- Exact work items:
  - define domain models,
  - define event flow,
  - define failure-state behavior,
  - define mode separation,
  - define persistence ownership boundaries.
- Expected files or modules when justified: architecture specs only.
- Interface contracts affected: all core contracts.
- Test requirements: scenario walk-through review.
- Verification procedures: trace representative flows end to end.
- Measurable acceptance criteria: each boundary has documented inputs, outputs, owner, and fail-safe behavior.
- Required evidence and artifacts: reviewed architecture specification.
- Known limitations after completion: exchange specifics remain abstract.
- Explicitly excluded work: concrete adapters.
- Failure and rollback considerations: if a contract cannot be specified safely, mark it blocked rather than guessed.
- Decisions requiring human approval: architecture acceptance.
- Blockers to next phase: unresolved event-model ownership or missing contracts.

### Phase 3 - Development and Test Foundation

- Objective: establish minimal development, testing, and CI foundations.
- Why necessary: enables small feedback loops.
- Entry conditions: architecture interfaces frozen.
- Inputs and dependencies: approved language and dependency-management choice.
- Exact work items:
  - initialize repository under version control,
  - set up package structure,
  - set up test runner,
  - set up formatting and linting rules,
  - define secret-handling conventions,
  - define run modes.
- Expected files or modules when justified: package scaffold, test scaffold, CI config after Git exists.
- Interface contracts affected: config and test harness only.
- Test requirements: smoke tests and config-validation smoke tests.
- Verification procedures: run test harness and static checks.
- Measurable acceptance criteria: a clean minimal repository can run tests locally.
- Required evidence and artifacts: passing smoke-test outputs.
- Known limitations after completion: no trading logic yet.
- Explicitly excluded work: market logic, strategy logic.
- Failure and rollback considerations: reduce tooling complexity if it becomes excessive.
- Decisions requiring human approval: minimal.
- Blockers to next phase: missing test harness or unsafe secret-handling design.

### Phase 4 - Market Data Contracts and Validation Layer

- Objective: implement normalized market-event ingestion and validation.
- Why necessary: downstream correctness depends on trustworthy temporal semantics.
- Entry conditions: Phase 3 foundation complete.
- Inputs and dependencies: approved exchange or explicit source abstraction.
- Exact work items:
  - define adapter interfaces,
  - implement validators,
  - implement data-health flags,
  - define duplicate and ordering policy behavior.
- Expected files or modules when justified: adapters, validators, market-event models.
- Interface contracts affected: market-event and health contracts.
- Test requirements: duplicates, out-of-order events, stale events, malformed payloads.
- Verification procedures: replay fixtures through validation layer.
- Measurable acceptance criteria: ambiguous or invalid data is rejected or quarantined deterministically.
- Required evidence and artifacts: fixture outputs and health-state traces.
- Known limitations after completion: private account data may still be stubbed.
- Explicitly excluded work: strategy and execution.
- Failure and rollback considerations: block the source rather than pass unsafe data.
- Decisions requiring human approval: exchange and source semantics if still unresolved.
- Blockers to next phase: untrustworthy timestamp semantics.

### Phase 5 - Historical Data Acquisition and Candle Semantics

- Objective: acquire reproducible historical data and guarantee committed-candle semantics.
- Why necessary: the strategy depends on candle finalization and anti-lookahead correctness.
- Entry conditions: validated ingestion semantics defined.
- Inputs and dependencies: approved timeframe, source policy, timestamp semantics.
- Exact work items:
  - design historical data acquisition,
  - record provenance metadata,
  - implement candle builder or verifier,
  - define missing-interval policy behavior,
  - implement commitment handling.
- Expected files or modules when justified: historical-data loader, candle validator or builder.
- Interface contracts affected: candle and dataset metadata contracts.
- Test requirements: missing intervals, timestamp semantics, bar finalization.
- Verification procedures: deterministic rebuild or validation of a fixed sample dataset.
- Measurable acceptance criteria: committed bars are explicit and reproducible.
- Required evidence and artifacts: dataset provenance and candle-quality report.
- Known limitations after completion: spread data may still be absent.
- Explicitly excluded work: live execution.
- Failure and rollback considerations: pause rather than continue with poor-quality data.
- Decisions requiring human approval: timeframe and missing-candle policy.
- Blockers to next phase: unresolved finalization semantics.

### Phase 6 - Replay Kernel and Anti-Lookahead Guarantees

- Objective: build the chronological replay engine for research.
- Why necessary: research is invalid if replay semantics differ from real-time information availability.
- Entry conditions: validated historical candle semantics.
- Inputs and dependencies: candle data and core domain contracts.
- Exact work items:
  - implement replay clock,
  - implement event ordering,
  - implement state snapshots,
  - implement feature-availability timing,
  - define deterministic run metadata.
- Expected files or modules when justified: replay engine and run metadata model.
- Interface contracts affected: replay run and event-ordering contracts.
- Test requirements: deterministic replay and no-future-data tests.
- Verification procedures: repeated identical runs with identical outputs.
- Measurable acceptance criteria: replay proves what information was available at each decision point.
- Required evidence and artifacts: replay determinism report.
- Known limitations after completion: execution realism still incomplete.
- Explicitly excluded work: live exchange adapter.
- Failure and rollback considerations: invalidate any run that violates chronology.
- Decisions requiring human approval: none beyond earlier time semantics.
- Blockers to next phase: anti-lookahead invariants fail.

### Phase 7 - Strategy and Feature Implementation

- Objective: implement the approved first strategy and its feature calculations.
- Why necessary: research requires executable strategy semantics.
- Entry conditions: strategy specification reviewed and approved for implementation, or explicitly authorized as provisional research code.
- Inputs and dependencies: strategy rules, replay engine, candle semantics.
- Exact work items:
  - implement feature snapshots,
  - implement rule evaluation,
  - implement proposal and rejection records,
  - implement signal expiry semantics.
- Expected files or modules when justified: features, strategy engine, signal models.
- Interface contracts affected: feature and strategy contracts.
- Test requirements: per-rule unit tests, deterministic replay, anti-lookahead regression.
- Verification procedures: fixtures for each rule and rejection case.
- Measurable acceptance criteria: strategy outputs match the approved rule definitions exactly.
- Required evidence and artifacts: rule-test matrix and sample replay traces.
- Known limitations after completion: still no execution realism proof.
- Explicitly excluded work: ranking and live execution.
- Failure and rollback considerations: version the strategy if rules change.
- Decisions requiring human approval: strategy approval status, parameter grid, signal-expiry window.
- Blockers to next phase: unresolved strategy rules.

### Phase 8 - Ranking, Risk, and Execution Simulation

- Objective: implement portfolio gating and simulated order lifecycle.
- Why necessary: a signal alone does not answer whether a trade is executable or authorized.
- Entry conditions: working strategy outputs.
- Inputs and dependencies: strategy proposals, exchange constraints, provisional or approved risk config.
- Exact work items:
  - implement minimal ranking,
  - implement Risk Engine decisions,
  - implement simulator order states,
  - implement partial-fill and timeout ambiguity handling.
- Expected files or modules when justified: ranking module, risk module, simulator execution module.
- Interface contracts affected: risk, order-intent, order-state, and fill contracts.
- Test requirements: deny-by-default, simultaneous signals, timeout ambiguity, partial fills.
- Verification procedures: scenario replay with limited capital and multiple symbols.
- Measurable acceptance criteria: no trade occurs without explicit approval; simulator preserves order/fill distinctions.
- Required evidence and artifacts: trace logs from proposal to denial or simulated fill.
- Known limitations after completion: simulator realism depends on available market microstructure data.
- Explicitly excluded work: private exchange adapter.
- Failure and rollback considerations: surface simulation limitations rather than hide them.
- Decisions requiring human approval: research-mode cost-model policy and provisional risk parameters.
- Blockers to next phase: unauditable risk or simulation behavior.

### Phase 9 - Persistence, Ledger, and Analytics

- Objective: make outcomes durable and economically interpretable.
- Why necessary: backtest results are meaningless without auditable accounting.
- Entry conditions: simulated orders and fills exist.
- Inputs and dependencies: fills, rejections, positions, costs, run metadata.
- Exact work items:
  - implement persistence schema,
  - implement ledger logic,
  - implement position accounting,
  - implement report derivation.
- Expected files or modules when justified: persistence layer, ledger, analytics reports.
- Interface contracts affected: ledger and position contracts.
- Test requirements: fee accounting, partial closes, restart recovery, incomplete-data flags.
- Verification procedures: compare against hand-worked examples.
- Measurable acceptance criteria: every reported result is traceable to persisted evidence.
- Required evidence and artifacts: accounting test cases and reproducible report artifacts.
- Known limitations after completion: still research mode only.
- Explicitly excluded work: live exchange trading.
- Failure and rollback considerations: mark results incomplete when fee or linkage data is missing.
- Decisions requiring human approval: storage choice if not already approved.
- Blockers to next phase: accounting completeness not demonstrated.

### Phase 10 - Backtesting, Cost Modeling, and Robustness Research

- Objective: produce valid strategy research under realistic assumptions.
- Why necessary: raw strategy signals do not establish profitability.
- Entry conditions: replay, strategy, simulator, and ledger are working.
- Inputs and dependencies: historical datasets, approved cost assumptions, parameter grid.
- Exact work items:
  - run baseline comparisons,
  - apply fees, spread, slippage, and constraint modeling,
  - run validation and holdout studies,
  - run sensitivity and robustness analysis.
- Expected files or modules when justified: experiment runner, report generator, run catalog.
- Interface contracts affected: experiment config and report schemas.
- Test requirements: reproducibility and report correctness.
- Verification procedures: rerun fixed experiments and compare results.
- Measurable acceptance criteria: reports clearly distinguish gross from net and in-sample from out-of-sample.
- Required evidence and artifacts: versioned experiment outputs and validation reports.
- Known limitations after completion: still no live operational proof.
- Explicitly excluded work: live funds deployment.
- Failure and rollback considerations: reject the strategy if results collapse under realistic costs.
- Decisions requiring human approval: acceptance thresholds and interpretation criteria.
- Blockers to next phase: inadequate out-of-sample validity or cost realism.

### Phase 11 - Exchange Adapter, Paper Trading, Monitoring, and Recovery

- Objective: connect the system to a real exchange in non-live-risk mode.
- Why necessary: operational behavior must be observed before any live test.
- Entry conditions: strategy has survived research validation gates.
- Inputs and dependencies: approved exchange, credentials policy, paper-trading design, monitoring design.
- Exact work items:
  - implement public and private exchange adapters,
  - implement reconciliation,
  - implement paper mode,
  - implement emergency stop,
  - implement restart recovery.
- Expected files or modules when justified: exchange adapter, paper execution mode, reconciliation, monitoring modules.
- Interface contracts affected: live data, order, fill, and reconciliation contracts.
- Test requirements: disconnects, reconnects, stale feeds, rate limits, partial fills, restart safety, emergency stop.
- Verification procedures: scripted failure-injection scenarios in paper mode.
- Measurable acceptance criteria: the system blocks new exposure safely under degraded state and recovers deterministically.
- Required evidence and artifacts: paper-trading logs, reconciliation reports, incident test outputs.
- Known limitations after completion: paper fills are still not live fills.
- Explicitly excluded work: real-money trading.
- Failure and rollback considerations: disable entries and require manual review if reconciliation is unclear.
- Decisions requiring human approval: exchange credentials policy and paper-trading acceptance.
- Blockers to next phase: material semantic drift or unresolved operational instability.

### Phase 12 - Live Readiness Review and Controlled Live Test

- Objective: authorize and execute a tightly constrained live test only if all gates pass.
- Why necessary: real capital risk requires explicit human authorization and operational proof.
- Entry conditions: paper-trading acceptance and live-safety review passed.
- Inputs and dependencies: approved risk limits, approved credentials, explicit human authorization, emergency controls.
- Exact work items:
  - complete live-readiness review,
  - perform emergency-stop drill,
  - execute first live test,
  - perform post-test evaluation.
- Expected files or modules when justified: operational procedures and evaluation artifacts, not major new modules.
- Interface contracts affected: live-mode configuration and operator procedures.
- Test requirements: emergency stop, restart recovery, reconciliation before and after live session.
- Verification procedures: operator checklist and post-session audit.
- Measurable acceptance criteria: live exposure remains within approved limits and every event is auditable.
- Required evidence and artifacts: live session report, reconciliation report, post-test decision log.
- Known limitations after completion: one small live test does not justify scaling.
- Explicitly excluded work: automatic scaling or unattended live deployment.
- Failure and rollback considerations: immediate stop and reconciliation on unsafe discrepancy.
- Decisions requiring human approval: mandatory.
- Blockers to next phase: any unresolved live-safety or accounting failure.

## Part 6 - Dependency Graph

### Critical Path

- Phase 1 -> Phase 2 -> Phase 4 -> Phase 5 -> Phase 6 -> Phase 7 -> Phase 8 -> Phase 9 -> Phase 10.

This is the minimum path to produce credible research evidence.

### Major Decision Dependencies

- Exchange choice blocks market-data integration, candle semantics, exchange constraints, paper trading, and live readiness.
- Timeframe and candle semantics block candle handling, replay, strategy implementation, and validation.
- Strategy approval blocks reliable implementation of strategy logic.
- Numerical risk limits block meaningful paper-trading and live-readiness work.
- Version-control setup blocks CI and disciplined implementation workflow.

### Work That Can Proceed in Parallel Once Interfaces Are Frozen

- Development and test foundation can proceed while some exchange-specific details are still being finalized.
- Report-generation design can proceed alongside late simulation work.
- Monitoring design can begin before paper trading but cannot be validated until later.

### High-Risk Architectural Dependencies

- Replay/live semantic alignment.
- Fill/position/ledger consistency.
- Risk gating as a hard authorization boundary.
- Timeout ambiguity and duplicate-order prevention.

## Part 7 - Configuration and Decision Register

### Implementation-Blocking Decisions

| ID | Decision | Current status | Evidence | Alternatives | Recommended option | Human approval | Resolve by |
|---|---|---|---|---|---|---|---|
| D-01 | Version-control workflow | unresolved | workspace is not a Git repo | GitHub, Azure Repos, local-only | Git with remote hosting | yes | Phase 1 |
| D-02 | Programming language | unresolved | no code exists | Python, .NET, TypeScript | Python 3.12 | yes | Phase 1 |
| D-03 | Dependency management | unresolved | no environment exists | `venv`, Poetry, Conda, `uv` | `venv` with pinned dependencies | yes | Phase 1 |
| D-04 | Exchange | unresolved | repo documents mark it unresolved | liquid spot exchanges | one liquid spot exchange with clear docs | yes | Phase 1 |
| D-05 | Historical data source | unresolved | no data policy exists | exchange-native, vendor | exchange-native first | yes | Phase 5 |
| D-06 | Primary timeframe | proposed only | strategy spec recommends `5m` | `1m`, `3m`, `5m`, `15m` | `5m` for first study | yes | Phase 5 |
| D-07 | Candle timestamp semantics | unresolved | explicitly unresolved in strategy spec | open-time, close-time | explicit open and close times with close-based signal evaluation | yes | Phase 5 |
| D-08 | Missing-candle policy | unresolved | explicitly unresolved | reject gaps, resync, forward-fill | reject for eligibility, resync for recovery, never forward-fill signals | yes | Phase 5 |
| D-09 | Initial asset universe | unresolved | roadmap marks it unresolved | curated list, dynamic discovery | curated liquid spot list | yes | Phase 10 |
| D-10 | Strategy approval for implementation | unresolved | strategy spec is proposed, not approved | wait, provisional implementation | provisional only if explicitly authorized | yes | Phase 7 |
| D-11 | Strategy parameter grid | unresolved | strategy spec marks unresolved | narrow or broad search | small predeclared grid | yes | Phase 10 |
| D-12 | Signal validity window | proposed only | strategy spec recommends one candle interval | shorter, equal to 1 interval, longer | one candle interval | yes | Phase 7 |
| D-13 | Storage | unresolved | no implementation exists | SQLite, Postgres, flat files | SQLite | yes | Phase 9 |
| D-14 | Structured logging format | unresolved | no tooling exists | JSON lines, plain text | JSON lines | yes | Phase 3 |
| D-15 | Numerical risk limits | unresolved | project definition forbids silent invention | many possible values | no default recommended here | yes | Phase 8 research gating, Phase 11 paper/live |
| D-16 | Position sizing method | unresolved | strategy spec marks unresolved | fixed notional, volatility-scaled, risk-based | fixed notional for first constrained live test only after approval | yes | Phase 11 |
| D-17 | Maximum simultaneous positions | unresolved | project definition requires this control | 1, small fixed N, dynamic | small fixed limit after approval | yes | Phase 8 |
| D-18 | Cost-model policy without spread history | unresolved | strategy spec flags this limitation | synthetic penalties, vendor data, reject study | conservative synthetic sensitivity bands | yes | Phase 10 |
| D-19 | Paper-trading model | unresolved | roadmap requires paper trading | exchange testnet, internal simulator | internal simulator on live public data plus exchange constraints | yes | Phase 11 |
| D-20 | Live-mode safeguards | unresolved | project definition requires safety | single flag, dual control, checklist | multi-step enable plus startup block and checklist | yes | Phase 11 |
| D-21 | Deployment environment | unresolved | no runtime target exists | local only, VPS, container host | local first | yes | Phase 11 |

## Part 8 - Risk Register

### Highest-Priority Risks

1. Incorrect or incomplete market data.
2. Look-ahead bias.
3. Data leakage in parameter tuning.
4. Overfitting.
5. Unrealistic backtest fill assumptions.
6. Fee and slippage underestimation.
7. Low liquidity.
8. Exchange outages or degraded exchange state.
9. Duplicate orders after timeout.
10. Unknown order outcomes.
11. Partial fills.
12. Accounting divergence.
13. Position mismatch.
14. Unsafe restart behavior.
15. Secret exposure.
16. Accidental live trading.
17. Insufficient critical-path test coverage.
18. Insufficient statistical evidence.

### Risk-Handling Principles

For each risk, the system and roadmap must define:

- prevention,
- detection,
- recovery,
- explicit test coverage,
- residual risk acknowledgement.

`FACT`: some risk likelihoods and impacts cannot yet be quantified defensibly because the exchange, timeframe, and asset universe remain unresolved. Those assessments must therefore remain provisional until later phases.

## Part 9 - Stage Gates

### Gate 1 - Requirements Readiness

Pass criteria:

- authoritative documents reviewed,
- no unresolved contradictions,
- blocked decisions explicitly listed.

Required evidence:

- repository findings,
- decision register.

Authority:

- human approval.

### Gate 2 - Architecture Readiness

Pass criteria:

- core boundaries, contracts, and invariants are documented,
- fail-safe behavior is defined.

Required evidence:

- architecture specification,
- scenario walk-through review.

Authority:

- human approval.

### Gate 3 - Implementation Correctness

Pass criteria:

- relevant unit and integration tests pass,
- logs and state transitions inspect correctly for the implemented phase.

Required evidence:

- test results,
- sample traces.

Authority:

- human plus test suite outputs.

### Gate 4 - Historical-Data Validity

Pass criteria:

- provenance recorded,
- timestamp semantics fixed,
- gaps and anomalies reported.

Required evidence:

- dataset quality report.

Authority:

- human approval.

### Gate 5 - Backtest Validity

Pass criteria:

- replay is chronological,
- cost model is documented,
- accounting completeness is established,
- runs are reproducible.

Required evidence:

- reproducible run metadata,
- validation report.

Authority:

- human approval.

### Gate 6 - Out-of-Sample Strategy Validation

Pass criteria:

- final untouched holdout remains acceptable after realistic costs, or the strategy is rejected,
- robustness checks do not reveal a narrow fragile edge.

Required evidence:

- out-of-sample report,
- sensitivity analysis,
- baseline comparison.

Authority:

- human approval.

### Gate 7 - Paper-Trading Readiness

Pass criteria:

- exchange adapter,
- monitoring,
- reconciliation,
- emergency stop,
- mode safety implemented and tested.

Required evidence:

- paper-mode readiness checklist.

Authority:

- human approval.

### Gate 8 - Paper-Trading Acceptance

Pass criteria:

- operational behavior is stable,
- no unresolved safety divergence exists.

Required evidence:

- paper-trading logs,
- reconciliation reports,
- incident review.

Authority:

- human approval.

### Gate 9 - Live-System Safety

Pass criteria:

- withdrawal-disabled credentials,
- approved numeric risk limits,
- restart recovery,
- emergency controls,
- reconciliation procedures verified.

Required evidence:

- live-safety checklist,
- emergency-stop drill evidence.

Authority:

- human approval.

### Gate 10 - Controlled Live-Test Authorization

Pass criteria:

- all prior gates passed,
- explicit human authorization for real-money mode recorded.

Required evidence:

- signed-off live test plan.

Authority:

- human only.

### Gate 11 - Post-Live Evaluation

Pass criteria:

- live events reconciled,
- outcomes evaluated honestly,
- no hidden divergence remains.

Required evidence:

- live session report,
- reconciliation report,
- decision log.

Authority:

- human approval.

### Gate 12 - Scaling Decision

Pass criteria:

- evidence supports scaling,
- risk controls remain adequate,
- scaling is explicitly approved.

Required evidence:

- comparative research, paper, and live results.

Authority:

- human only.

## Part 10 - Readiness Assessment

`READY FOR HUMAN REVIEW`

This technical plan is complete enough for review because it:

- is grounded in the actual repository contents,
- preserves the authority of the existing documents,
- treats the strategy specification as proposed rather than approved,
- defines a minimal implementation architecture,
- identifies the implementation-critical decisions without inventing them,
- establishes phase-by-phase acceptance criteria and gating.

### Exact Decisions That Must Be Resolved Before Implementation Begins

1. Version-control workflow.
2. Programming language and dependency-management approach.
3. Whether provisional strategy implementation is allowed before formal strategy approval.
4. Exchange-selection choice or approved selection criteria.
5. Primary timeframe and candle timestamp semantics.
6. Missing-candle policy.
7. Initial storage choice.
8. Initial logging and experiment-tracking approach.
9. Initial asset-universe selection method.
10. Strategy parameter-selection process for the first study.

### Decisions That Can Remain Open Longer

1. Exact live deployment environment.
2. Rich monitoring stack.
3. Final scaling policy.
4. Longer-term repository expansion beyond the first research system.