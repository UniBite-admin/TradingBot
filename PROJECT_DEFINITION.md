# TradingBot — Project Definition and Governing Principles

## Mission
Build a reproducible cryptocurrency SPOT research system that tests, with realistic costs and execution constraints, whether a specified BTC/EUR trend-following strategy has positive expectancy. Optimize for evidence, reproducibility, capital protection, and a minimal understandable system.

The aspirational goal of growing €50 to €5,000 in 3–7 days is extremely aggressive, not assumed achievable, and never justifies weakening research or risk controls.

## Active strategy and transition
- **New active research target:** BTC/EUR spot trend-following strategy defined in `STRATEGY_SPECIFICATION.md`.
- **State:** specification/data-audit phase; strategy implementation and results are not yet validated.
- **Previous Box Theory and other legacy strategies:** obsolete implementation and tests are removed from `main`. Historical reports/manifests are retained as comparison evidence only; do not mix their results with the new strategy.
- **Required source:** validated BTC/EUR hourly OHLCV for execution simulation. The repository inventory on `main` confirms that `data/kraken/XBTEUR_1440.csv` is present for cross-checking. The actual files, schemas, timestamp semantics, and coverage must be inspected before data adequacy is claimed.
- Do not assume that 24-hour data can replace hourly data for hourly execution simulation.

## System boundaries
- SPOT only. No leverage, margin, futures, or perpetuals.
- This project phase is historical research only. Paper trading, live orders, and scaling are not authorized.
- Exchange API keys must never have withdrawal permission. Secrets must not be committed or exposed in logs.
- A signal is not an order; an order is not a fill; an exchange response is not proof of final account state. Any future live system must give the Risk Engine final authority to reject trades.

## Research integrity
- AI-generated hypotheses are not evidence.
- Never claim profitability without reproducible results after realistic costs and execution constraints.
- Prevent look-ahead bias, data leakage, and uncontrolled tuning.
- Preserve source identity, exact UTC bounds, data-validation outcomes, strategy version, configuration, test boundaries, and report provenance.
- No silent gap repair, synthetic candles, or trade/state crossing a data gap or evaluation boundary.
- Report gross results separately from fees, spread, slippage, and unresolved execution uncertainty.
- Treat costs and parameters as research assumptions unless supported by dated, relevant evidence.
- The source paper must be checked before claiming exact replication; details inherited from the supplied prompt remain provisional where not independently verified.

## Development and approval path
`Historical Data → Backtest → Validation → Paper Trading → Controlled Small Live Test → Evaluation → Explicitly Approved Scaling`

Passing code tests or observing positive backtest P&L is not sufficient to advance. Each stage requires reviewed evidence and explicit authorization. Live trading and scaling must never be activated automatically.

## Engineering principles
- Inspect actual code, tests, data, and authoritative documents before changing them.
- Make small, verifiable changes and investigate root causes.
- Keep one authoritative project definition, roadmap, and strategy specification.
- Reuse existing architecture where reasonable; avoid duplicate specifications and speculative infrastructure.
- Human authority decides unresolved critical decisions. Record approved decisions in the repository, not only in chat.
- The user handles Git commits/pushes unless explicitly requested otherwise; repository edits for this task are made on a dedicated research branch, not directly on the default branch.

## Definition of done
A task is complete only when requirements are clear, implementation matches the specification, relevant tests have actually run, behavior and outputs are inspected, acceptance criteria are satisfied, and documents reflect verified reality. Clearly label proposed, approved, implemented, tested, validated, and blocked work.
