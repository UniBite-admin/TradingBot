# TradingBot Roadmap — Box Theory Only

## Current state
- **Active strategy:** Box Theory only.
- **Active historical input:** Kraken BTC/EUR 5-minute OHLCV under `data/kraken/`.
- **Implementation:** candidate engine, runner, and unit tests exist on `strategy/box-theory-research`; this does not mean tests or the full-data backtest have passed.
- **Costs:** gross P&L is separated from illustrative fee/spread/slippage sensitivity. Latency is not converted to EUR.
- **Legacy strategy code/specifications:** obsolete for active work. Historical reports/manifests remain comparison evidence only.
- **Paper trading, live trading, and scaling:** not authorized.

## Authoritative files
- `PROJECT_DEFINITION.md`: project boundaries and governance.
- `ROADMAP.md`: this roadmap and phase gates.
- `STRATEGY_SPECIFICATION.md`: the only active strategy contract.
- `TECHNICAL_PLAN.md`: implementation, tests, and acceptance evidence.
- `README.md`: entrypoint and run command.

## Phase 1 — Box Theory implementation and verification
**Status: implementation present; verification pending.**

Scope: validate Kraken OHLCV; build prior-day boxes only from complete 288-candle UTC days; detect lower-zone rejection; enter at next candle open; simulate midpoint target and buffered signal-low stop; split gaps and reset state; emit provenance, trade statistics, gross P&L, cost scenarios, and unpriced latency uncertainty.

Acceptance:
- Focused Box Theory tests pass in the target environment.
- Full report runs on the actual source CSV and is inspected.
- Hand-calculated cost examples match fees, spread, slippage, and net P&L.
- No legacy latency-to-EUR formula is used.
- No trade/state crosses a gap or partition boundary.
- Report is reproducible from source hash and configuration.

## Phase 2 — Research report review
**Blocked until Phase 1 evidence exists.**

Review source integrity, time coverage, complete-day eligibility, gap/segment counts, trade and exit distributions, unresolved trades, gross P&L, cost sensitivity, chronological split boundaries, and whether the sample supports any conclusion. Do not invent minimum-sample thresholds without evidence or approval.

Output: a reviewed, provenance-linked Box Theory report and a documented conclusion: supported, rejected, or inconclusive for further research.

## Phase 3 — Realistic validation
**Not started; requires Phase 2 review and separately approved scope.**

Required evidence: intended venue's current fee tier and order-type behavior; bid/ask spread and order-book depth; slippage, latency, partial/rejected fills, minimum order size, order constraints; controlled out-of-sample protocol; sample adequacy; risk limits and operational failure behavior.

## Phase 4 — Paper trading
**Not authorized.** Requires explicit human approval after research and validation gates.

## Phase 5 — Controlled small live test
**Not authorized.** Requires fresh explicit human authorization, withdrawal-disabled API keys, approved risk limits, and reviewed execution controls.

## Phase 6 — Evaluation and scaling
**Not authorized.** No automatic transition or scaling. Scaling requires prior-stage evidence and explicit human approval.

## Legacy comparison evidence
Reports under `data/experiments/` and `reports/` from Experiment A/B, breakout, and zero-cost research remain historical evidence. Their code/specifications are not active. Do not mix them into Box Theory performance claims; a head-to-head comparison requires the same source, period, data rules, costs, and approved protocol.
