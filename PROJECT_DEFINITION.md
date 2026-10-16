# TradingBot — Project Definition and Governing Principles

## Mission
Build a reproducible cryptocurrency SPOT research system that tests whether the single active Box Theory candlestick strategy has positive expectancy after explicit transaction-cost and execution-uncertainty analysis. Prioritize correctness, evidence, capital protection, and a small understandable system.

The aspirational goal of growing €50 to €5,000 in 3–7 days is extremely aggressive, not assumed achievable, and never justifies weakening research or risk controls.

## Active strategy and data boundary
- The only active strategy specification is Box Theory in `STRATEGY_SPECIFICATION.md`.
- Current research input: Kraken BTC/EUR 5-minute OHLCV from `data/kraken/`.
- Bitvavo Spot remains a future intended venue concept; Kraken OHLCV is not Bitvavo order-book or execution evidence.
- Previous Experiment A/B, breakout, and zero-cost strategy code/specifications are obsolete for active development. Historical reports/manifests are retained for comparison and provenance only.
- Do not mix reports from different strategies, datasets, periods, cost models, or execution assumptions as if they were a controlled comparison.

## System boundaries
- SPOT only. No leverage, margin, futures, or perpetuals.
- Paper trading, live orders, and scaling are not authorized by this project definition.
- Exchange API keys must never have withdrawal permission. Secrets must not be committed or exposed in logs.
- A signal is not an order; an order is not a fill; an exchange response is not proof of final account state. Any future live system must give the Risk Engine final authority to reject trades.

## Research integrity
- AI-generated hypotheses are not evidence.
- Never claim profitability without reproducible results after realistic costs and execution constraints.
- Prevent look-ahead bias, data leakage, and uncontrolled tuning.
- Preserve source identity, exact UTC bounds, data-validation outcomes, strategy version, configuration, test boundaries, and report provenance.
- No silent gap repair, no synthetic candles, and no trade/state crossing a data gap or validation partition.
- Report gross P&L separately from fee, spread, and slippage scenarios.
- Do not convert latency to EUR without a defensible validated model. Report latency as unresolved execution uncertainty.
- Cost scenarios are assumptions unless supported by dated venue fee schedules and measured execution data.

## Development and approval path
`Historical Data → Backtest → Validation → Paper Trading → Controlled Small Live Test → Evaluation → Explicitly Approved Scaling`

Passing code tests or observing positive backtest P&L is not sufficient to advance. Each stage requires reviewed evidence and explicit authorization. Live trading and scaling must never be activated automatically.

## Engineering principles
- Inspect code, tests, data, and authoritative documents before changing them.
- Make small, verifiable changes and investigate root causes.
- Keep one authoritative project definition, roadmap, and strategy specification.
- Keep reusable data-validation and risk utilities separate from strategy logic.
- Avoid unnecessary frameworks, duplicate specifications, and infrastructure.
- Human authority decides unresolved critical decisions. Record approved decisions in the repository, not only in chat.

## Definition of done
A task is complete only when requirements are clear, implementation matches the specification, relevant tests have actually run, behavior and outputs are inspected, acceptance criteria are satisfied, and documents reflect verified reality. Clearly label untested, unvalidated, and blocked work.
