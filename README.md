# TradingBot — BTC/EUR Trend Strategy Research

## Current status
The active research target is a BTC/EUR spot trend-following strategy with nine daily submodels. The project is in the **contract and data-audit phase**. Strategy implementation, backtest results, and profitability have not been validated.

- [Project definition](PROJECT_DEFINITION.md) — mission, boundaries, governance.
- [Roadmap](ROADMAP.md) — phase status and acceptance gates.
- [Strategy specification](STRATEGY_SPECIFICATION.md) — sole active strategy contract.
- [Technical plan](TECHNICAL_PLAN.md) — data audit, implementation, and verification plan.

## Data required
Validated BTC/EUR hourly OHLCV is required for the proposed hourly execution simulation. The user confirms that 24-hour BTC/EUR candles are available and plans to upload them for cross-checking. The actual files, schemas, timestamps, and date coverage must be inspected before selecting or running a backtest. Do not treat the 24-hour file as a substitute for hourly execution data.

## Research boundaries
- SPOT only; no leverage, margin, futures, or perpetuals.
- No paper trading, live orders, or automatic scaling is authorized.
- All windows start independently with €100.
- Transaction fees and slippage are modeled as explicit scenarios, not claimed as verified future costs.
- Historical Box Theory and earlier strategy reports remain comparison evidence only and must not be mixed with this strategy's results.

## Next step
Upload the BTC/EUR 24-hour data file(s). Then audit them alongside any available hourly data, document the exact schema and timestamp semantics, cross-check UTC daily candles, and resolve data blockers before implementing the strategy engine.
