# Trading Bot

This repository is focused on a Kraken-backed historical research workflow for a descriptive BTC/EUR 5-minute signal study.

Authoritative documents:

- [PROJECT_DEFINITION.md](PROJECT_DEFINITION.md)
- [ROADMAP.md](ROADMAP.md)
- [STRATEGY_SPECIFICATION.md](STRATEGY_SPECIFICATION.md)
- [TECHNICAL_PLAN.md](TECHNICAL_PLAN.md)

Current status:

- Kraken BTC/EUR 5-minute OHLCV is the active historical research source.
- The repository retains the provider-neutral Experiment A-equivalent descriptive mechanics: bullish signal on close > open, next-period return, baseline comparison, and fail-closed gap handling.
- The project remains descriptive-only and does not claim live trading, execution feasibility, or profitability.
- Bitvavo Spot remains the intended live venue conceptually, but no orders or live deployment are authorized by this repository state.
- Any new result must be documented with source provenance, UTC bounds, validation counts, and known limitations.

Repository rule:

- If a requirement, parameter, or decision is not explicitly documented and approved, it is not approved.