# TradingBot — BTC/EUR Trend Strategy Research

## Current status
The active research target is a BTC/EUR spot trend-following strategy with nine daily submodels. The project is in the **contract and data-audit phase**. Strategy implementation, backtest results, and profitability have not been validated.

- [Project definition](PROJECT_DEFINITION.md) — mission, boundaries, governance.
- [Roadmap](ROADMAP.md) — phase status and acceptance gates.
- [Strategy specification](STRATEGY_SPECIFICATION.md) — sole active strategy contract.
- [Technical plan](TECHNICAL_PLAN.md) — data audit, implementation, and verification plan.

## Data required
Repository inventory on `main` confirms these Kraken BTC/EUR OHLCV files exist: `data/kraken/XBTEUR_5.csv`, `XBTEUR_60.csv`, `XBTEUR_240.csv`, `XBTEUR_720.csv`, and `XBTEUR_1440.csv`. Their presence and file sizes have been verified, but their row contents, schema, timestamp semantics, coverage, gaps, duplicates, and OHLCV validity have not yet been audited. Hourly data is required for the proposed hourly execution simulation; 24-hour data is a cross-check, not a substitute.

## Research boundaries
- SPOT only; no leverage, margin, futures, or perpetuals.
- No paper trading, live orders, or automatic scaling is authorized.
- All windows start independently with €100.
- Transaction fees and slippage are modeled as explicit scenarios, not claimed as verified future costs.
- Historical Box Theory and earlier strategy reports remain comparison evidence only and must not be mixed with this strategy's results.

## Next step
Next: audit the existing 1h and 24h files at content level, inspect 5m/4h/12h as supporting datasets, document schema and timestamp semantics, and cross-check UTC daily candles where boundaries are comparable. Resolve data blockers before implementing the strategy engine.
