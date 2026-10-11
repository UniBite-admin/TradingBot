# Sprint 06 - Acceptance Criteria

Sprint 06 is acceptable only when the strategy and backtest pipeline are deterministic, evidence-based, and clearly labeled as research artifacts.

## Completion conditions

1. Feature and signal inputs are defined and reproducible.
2. Strategy rules operate only on committed data and valid context windows.
3. The backtest harness can replay the bounded historical dataset and produce deterministic outputs.
4. Parameter and holdout discipline is documented and enforced.
5. Negative, flat, and neutral results are logged without pressure to reinterpret them.
6. No paper or live activation is implied by the backtest results.

## Required evidence

- deterministic replay outputs,
- signal and rejection logs,
- fixed split and parameter metadata,
- stage gate stating the backtest remains research-only.

## Non-criteria

- no profitability proof,
- no live execution approval,
- no scaling approval,
- no claim that the strategy is finalized.
