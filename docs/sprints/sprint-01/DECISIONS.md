# Sprint 01 - Decisions And Unresolved Decision Register

This file records decisions supported by current repository evidence and unresolved decisions that materially affect the first controlled research experiment.

## Decisions Already Supported By Repository Evidence

### SD-001 - Project scope is spot only

- Status: APPROVED
- Repository evidence: `PROJECT_DEFINITION.md` restricts scope to spot markets only and excludes leverage, margin, futures, and perpetuals.
- Why it matters: the first experiment and any future implementation must not assume shorting, leverage, or derivatives behavior.

### SD-002 - The current strategy is proposed, not approved

- Status: APPROVED FACT ABOUT STATUS
- Repository evidence: `STRATEGY_SPECIFICATION.md` states that the strategy is proposed for human review, not approved, not implemented, not validated, and not proven profitable.
- Why it matters: Sprint 01 must not treat proposed strategy rules as approved implementation requirements.

### SD-003 - The technical plan exists but is also proposed, not approved

- Status: APPROVED FACT ABOUT STATUS
- Repository evidence: `TECHNICAL_PLAN.md` exists and states that it is proposed for human review and not approved.
- Why it matters: Sprint 01 may use it as repository evidence for planning, but not as proof that implementation decisions are frozen.

### SD-004 - Real-money progression remains gated

- Status: APPROVED
- Repository evidence: `PROJECT_DEFINITION.md`, `ROADMAP.md`, `STRATEGY_SPECIFICATION.md`, and `TECHNICAL_PLAN.md` all preserve distinct gates for historical research, backtesting, paper trading, controlled live testing, and scaling.
- Why it matters: Sprint 01 must not imply that documentation completion, positive backtests, or plan approval authorize live trading.

### SD-005 - Signal, risk, order, fill, and final economic state are distinct

- Status: APPROVED
- Repository evidence:
  - `STRATEGY_SPECIFICATION.md` separates strategy proposal, risk approval, order submission, fills, and outcome recording.
  - `TECHNICAL_PLAN.md` explicitly states that signal, order intent, acknowledgement, fill, reconciled position state, and complete accounting are distinct states.
- Why it matters: the first experiment and any later implementation must preserve this separation to avoid false fills, duplicate orders, or invalid accounting.

### SD-006 - Version control now exists locally and tracks a remote main branch

- Status: SUPPORTED FACT
- Repository evidence: inspected Git state showed local branch `main`, remote `origin`, and a clean tracked state of `main...origin/main`.
- Why it matters: Sprint 01 documentation should not continue to claim that the workspace is not a Git repository.

## Unresolved Decisions Affecting The First Research Experiment

| ID | Question | What The Repository Establishes | What Remains Unknown | Why It Matters | Recommended Next Step | Human Approval Required |
|---|---|---|---|---|---|---|
| UD-001 | Which exchange and authoritative data source will be used? | The exchange is unresolved. The strategy and technical plan both treat exchange choice as materially important for candles, constraints, costs, and execution semantics. | The specific exchange, the public market-data source, and whether any secondary vendor is acceptable remain unknown. | Exchange choice affects symbols, fee schedule, tick size, lot size, order states, liquidity, and historical-data provenance. | Approve one liquid spot exchange and the authoritative historical/live data-source policy before experiment definition is finalized. | Yes |
| UD-002 | Which markets will be in the first experiment universe? | The strategy recommends a small liquid spot set, but no market universe is approved. | Exact pairs, quote-currency scope, and market-selection method remain unknown. | Asset selection affects liquidity, spread burden, and whether results generalize or overfit to a narrow set. | Approve a transparent initial market-universe rule after exchange selection. | Yes |
| UD-003 | What is the primary candle timeframe? | The strategy recommends `5m`, but explicitly says this is not approved. | The approved timeframe is unknown. | Timeframe affects signal frequency, noise, spread burden, holding horizon, and parameter interpretation. | Approve one initial timeframe before freezing the first experiment. | Yes |
| UD-004 | What are the authoritative candle semantics? | The repository requires explicit candle timestamp meaning, timezone, committed-versus-in-progress behavior, and no look-ahead. | Open-time versus close-time meaning, timezone convention, and exact bar-finalization policy remain unknown. | The experiment cannot be valid without explicit time semantics. | Approve candle timestamp, timezone, and bar-finalization semantics together with timeframe approval. | Yes |
| UD-005 | How must missing, duplicated, out-of-order, and incomplete candle data be handled? | The strategy requires explicit policy and rejects silent forward filling. The technical plan requires validation and continuity handling. | The approved continuity policy and reconciliation behavior are unknown. | This affects eligibility, determinism, replay validity, and anti-lookahead protection. | Approve a data-integrity policy that distinguishes strategy eligibility from data-recovery behavior. | Yes |
| UD-006 | What parameter grid will be allowed for `L` and `N`? | The strategy requires a small predeclared grid and forbids arbitrary tuning. | Exact research candidates for local lookback `L` and holding horizon `N` are unknown. | Parameter choice affects both hypothesis definition and overfitting risk. | Approve a small predeclared grid only after timeframe and market semantics are fixed. | Yes |
| UD-007 | What is the approved signal-expiry policy? | The strategy recommends one candle interval and marks that recommendation as needing approval. | The approved stale-signal window is unknown. | Signal freshness affects entry timing, stale trades, and simulated/live comparability. | Approve the signal-validity window when freezing the first experiment rules. | Yes |
| UD-008 | What execution assumptions define an entry or exit for research? | The strategy prohibits assuming fills at signal prices and requires next executable opportunity semantics. The technical plan preserves separation between signals, orders, acknowledgements, and fills. | The exact experiment-level entry and exit execution assumptions remain unknown, including whether candle-only data are sufficient for the first study. | Without explicit execution assumptions, backtest results can be materially misleading. | Freeze the first experiment's execution model before any research run is treated as valid. | Yes |
| UD-009 | What cost model will be accepted for the first experiment? | The strategy requires fees, spread, slippage, latency, liquidity, failed orders, minimum order sizes, and fill constraints where relevant. The technical plan also requires these. | Exact fee source, spread policy when quote data are absent, slippage model, latency assumption, liquidity rule, and fill model remain unknown. | Scalping results are highly sensitive to costs and execution assumptions. | Approve an explicit first-experiment cost-model policy and sensitivity approach before experiment runs are accepted. | Yes |
| UD-010 | What are the approved position-sizing and risk assumptions for research and later stages? | Numeric risk limits, position sizing, and maximum simultaneous positions remain unresolved. The Risk Engine has final authority. | It remains unknown whether the first experiment uses normalized unit trades, capital-constrained simulation, or another approved accounting basis. | This affects comparability of trade outcomes, account paths, and later paper/live continuity. | Decide whether the first experiment uses unit-normalized or capital-constrained accounting, and keep live-risk limits as a separate later approval if not yet needed. | Yes |
| UD-011 | How are simultaneous or competing exit conditions prioritized? | The strategy defines structural invalidation and fixed-horizon baseline exits, but does not explicitly prioritize them when they become true together on the same evaluation step. | Exact precedence or simultaneous-resolution policy is unknown. | Exit precedence can change simulated outcomes and must be deterministic. | Resolve this in the first bounded experiment specification before implementation or replay. | Yes |
| UD-012 | What historical dataset is sufficient for the first valid experiment? | The repository requires provenance, out-of-sample separation, and chronological integrity. | Specific dataset coverage, adequacy criteria, and the exact out-of-sample methodology remain unknown. | The experiment cannot be judged valid without a defined data scope and holdout discipline. | Approve dataset adequacy and out-of-sample methodology when freezing the first experiment plan. | Yes |
| UD-013 | Which runtime and core technical choices are approved for implementation? | The technical plan recommends Python 3.12, `venv`, SQLite, JSON-line logging, and a modular monolith, but marks them as proposed rather than approved. | The approved implementation stack remains unknown. | Later implementation work depends on these choices, even if Sprint 01 stays documentation-only. | Resolve stack approval before implementation begins. | Yes |

## Evidence-Backed Scope Deferral Candidates

The current technical plan already supports deferring the following from the first controlled research experiment scope:

- real exchange private execution adapter,
- full paper-trading mode,
- rich monitoring stack,
- advanced multi-asset ranking heuristics,
- advanced reconciliation tooling,
- deployment automation.

Why these are deferrable:

- `TECHNICAL_PLAN.md` already marks them as later-stage or non-immediate requirements.
- The first research objective is to determine whether the proposed strategy has positive expectancy after realistic costs, not to build a full live-trading platform.

This sprint does not change the technical plan. It records that these deferrals are already supported by existing repository evidence and should not be pulled into the first experiment scope without explicit justification.