# TradingBot Roadmap — BTC/EUR Trend Strategy

## Current state
- **Active research target:** BTC/EUR spot trend-following strategy defined in `STRATEGY_SPECIFICATION.md`.
- **Current phase:** contract and data audit. Strategy engine/backtest implementation has not started under this specification.
- **Data:** all five Kraken BTC/EUR files (5m, 1h, 4h, 12h, 24h) are present on `main`. File presence is verified; content-level semantics, coverage, and quality remain unaudited.
- **Previous Box Theory and other legacy strategies:** implementation and tests removed from `main`; historical reports/manifests retained for comparison only.
- **Paper trading, live orders, and scaling:** not authorized.

## Authoritative files
- `PROJECT_DEFINITION.md`: mission, boundaries, governance.
- `ROADMAP.md`: this roadmap and phase gates.
- `STRATEGY_SPECIFICATION.md`: sole active strategy contract.
- `TECHNICAL_PLAN.md`: implementation, tests, and acceptance evidence.
- `README.md`: project entrypoint and current status.

## Phase 0 — Contract and data audit
**Status: in progress; files are present, content-level data audit is pending.**

Scope:
- Verify the supplied research source and distinguish source-backed rules from prompt-derived assumptions.
- Inspect repository structure, local changes where available, and actual BTC/EUR data files.
- Determine timestamp units, timezone, bar-open/bar-close convention, schema, date coverage, gaps, duplicates, invalid OHLCV, and suspicious movements.
- Cross-check hourly-resampled UTC daily candles against `data/kraken/XBTEUR_1440.csv` when timestamp boundaries are semantically comparable.
- Resolve exact signal/execution boundary behavior, price-equality semantics, volatility edge cases, accounting metrics, and window selection protocol.
- Keep Box Theory reports separate from this strategy.

Acceptance:
- Actual files and data boundaries are identified from their contents, not guessed.
- No silent data repair, synthetic candles, or inferred execution fills.
- Contract assumptions and unresolved blockers are recorded in the strategy specification.
- No strategy engine or backtest implementation begins until the data contract is sufficiently established.

## Phase 1 — Strategy core and focused tests
**Not started; gated on Phase 0 review.**

Implement only the approved deterministic daily strategy state machine and tests. No portfolio backtest engine or live interfaces unless explicitly included in the next approved scope.

Acceptance:
- All lookback, stop-ordering, state-reset, volatility-sizing, and rebalance behaviors have focused tests.
- No look-ahead: only completed daily bars are used for a signal.
- Results are deterministic and boundary/gap behavior is tested.

## Phase 2 — Portfolio backtest and cost scenarios
**Not started; gated on Phase 1 passing.**

Simulate EUR cash, BTC quantity, target exposure, actual execution prices, fees, and slippage using the approved hourly execution convention. Run independent 30-day window experiments and a continuous BTC/EUR descriptive backtest, with saved configuration and source provenance.

Acceptance:
- Hand-calculated trade/accounting examples match the engine.
- No cash, position, state, or P&L crosses independent window or data-gap boundaries.
- Costs are applied to actual traded notionals and reported separately.
- Reports are reproducible and include limitations.

## Phase 3 — Results review and robustness
**Not started; requires Phase 2 evidence and review.**

Review sample adequacy, continuous results, WARM/COLD window results, costs, delays, drawdown, buy-and-hold comparisons, and out-of-sample discipline. Do not tune against the final test set or weaken criteria after seeing results.

## Phase 4 — Paper trading
**Not authorized.** Requires separate explicit human approval after research and validation gates.

## Phase 5 — Controlled small live test
**Not authorized.** Requires fresh explicit human authorization, withdrawal-disabled API keys, approved risk limits, and reviewed execution controls.

## Phase 6 — Evaluation and scaling
**Not authorized.** No automatic transition or scaling. Scaling requires prior-stage evidence and explicit human approval.

## Legacy comparison evidence
Historical Experiment A/B, breakout, zero-cost, and Box Theory reports/manifests remain historical evidence only. Their obsolete strategy implementation and tests have been removed from `main`. These reports are not results for the new strategy. A controlled comparison requires a common source, period, data policy, costs, and approved protocol.
