# TradingBot — BTC/EUR Trend Strategy Research

## Current status
The active research target is a BTC/EUR spot trend-following strategy with nine daily submodels. The project is in the **data-layer and contract-closure phase**. Strategy implementation, backtest results, and profitability have not been validated.

- [Project definition](PROJECT_DEFINITION.md) — mission, boundaries, governance.
- [Roadmap](ROADMAP.md) — phase status and acceptance gates.
- [Strategy specification](STRATEGY_SPECIFICATION.md) — sole active strategy contract.
- [Technical plan](TECHNICAL_PLAN.md) — data audit, implementation, and verification plan.

## Data required
Repository inventory on `main` confirms these Kraken BTC/EUR OHLCV files exist: `data/kraken/XBTEUR_5.csv`, `XBTEUR_60.csv`, `XBTEUR_240.csv`, `XBTEUR_720.csv`, and `XBTEUR_1440.csv`. The 1h and 24h files have been inspected at content level. Their seven-column schema is timestamp, OHLC, volume, trade count; the hourly file contains gaps that are preserved, not filled. Aggregating only complete UTC days from the hourly file produced 4,637 daily candles that matched the 24h file exactly for OHLC, volume, and trade count. The 5m/4h/12h files have not been audited for this strategy. The isolated hourly reader and focused tests exist on a research branch; automated test execution is still pending.

## Research boundaries
- SPOT only; no leverage, margin, futures, or perpetuals.
- No paper trading, live orders, or automatic scaling is authorized.
- All windows start independently with €100.
- Transaction fees and slippage are modeled as explicit scenarios, not claimed as verified future costs.
- Obsolete Box Theory and earlier strategy implementations/tests have been removed from `main`. Historical reports/manifests remain comparison evidence only and must not be mixed with this strategy's results.

## Next step
Next: execute the new hourly-reader tests and verify the code on the local checkout. Then close source-dependent and mathematical strategy-contract decisions before implementing the deterministic strategy core. No backtest or trading permission is implied.
