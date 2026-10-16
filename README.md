# TradingBot — Box Theory Research

## Active strategy
**Box Theory is the only active strategy research path.** It is a historical, long-only SPOT candidate using Kraken BTC/EUR 5-minute OHLCV. It is not approved for paper trading or live orders.

- [Project definition](PROJECT_DEFINITION.md) — mission and safety boundaries.
- [Roadmap](ROADMAP.md) — phase status and acceptance gates.
- [Strategy specification](STRATEGY_SPECIFICATION.md) — the sole active strategy contract.
- [Technical plan](TECHNICAL_PLAN.md) — implementation and verification.

## Run a historical report
```bash
python -m tools.hsra.box_theory_experiment --input data/kraken/XBTEUR_5.csv --output reports/box_theory_kraken_btc_eur.json
```

Reports separate gross P&L from fee, spread, and slippage scenarios. The illustrative scenario is unverified; latency is not converted to EUR. Kraken candles do not prove Bitvavo execution quality or fills.

## Legacy comparison evidence
Old Experiment A/B, breakout, and zero-cost reports/manifests are retained as historical comparison evidence only. Their strategy code and specifications are obsolete for active development. Do not combine their results with Box Theory as a head-to-head comparison without a common, approved protocol.

## Current gates
- Box Theory code and tests are present on the research branch; tests and the full data run still require execution and review.
- Profitability is not established.
- Paper trading, live trading, and scaling are not authorized.

SPOT only. No leverage, margin, futures, or perpetuals. API keys must never have withdrawal permission.
