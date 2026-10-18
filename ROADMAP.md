# TradingBot Roadmap — BTC/EUR Trend Strategy

## Current state
- **Active research target:** BTC/EUR spot trend-following strategy defined in `STRATEGY_SPECIFICATION.md`.
- **Current phase:** hourly/daily data layer and contract closure. Strategy engine/backtest implementation has not started under this specification.
- **Data:** 1h and 24h file contents have been inspected and cross-checked; details are in `STRATEGY_SPECIFICATION.md`. The 5m/4h/12h files are not inputs to the initial strategy path and have not been audited for this work. The isolated hourly reader and focused tests are on a research branch; tests have not yet run.
- **Previous Box Theory and other legacy strategies:** implementation and tests removed from `main`; historical reports/manifests retained for comparison only.
- **Paper trading, live orders, and scaling:** not authorized.

## Authoritative files
- `PROJECT_DEFINITION.md`: mission, boundaries, governance.
- `ROADMAP.md`: this roadmap and phase gates.
- `STRATEGY_SPECIFICATION.md`: sole active strategy contract.
- `TECHNICAL_PLAN.md`: implementation, tests, and acceptance evidence.
- `README.md`: project entrypoint and current status.

## Phase 0 — Contract and data audit
**Status: partially complete.** Hourly/daily content checks and daily cross-check are complete; source-paper verification and remaining strategy-contract decisions are still pending. Reader/tests are implemented on a research branch but not yet executed.

Scope:
- Verify the supplied research source and distinguish source-backed rules from prompt-derived assumptions.
- Inspect repository structure and actual BTC/EUR hourly/daily data files. **Completed for `XBTEUR_60.csv` and `XBTEUR_1440.csv` on 2026-10-19.**
- Determine timestamp units, UTC alignment, schema, coverage, gaps, duplicates, and OHLCV relationships.
- Cross-check hourly-resampled UTC daily candles against `data/kraken/XBTEUR_1440.csv`: 4,637 complete UTC days matched exactly for OHLC, volume, and trade count.
- Resolve exact signal/execution boundary behavior, price-equality semantics, volatility edge cases, accounting metrics, and window selection protocol.
- Keep Box Theory reports separate from this strategy.

Acceptance:
- Actual files and data boundaries are identified from their contents, not guessed.
- No silent data repair, synthetic candles, or inferred execution fills.
- Contract assumptions and unresolved blockers are recorded in the strategy specification.
- No strategy engine or backtest implementation begins until the data contract is sufficiently established.

## Phase 1 — Strategy core and focused tests
**Not started; gated on Phase 0 contract closure and successful reader tests.**

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
