# Sprint 03 - Acceptance Criteria

Sprint 03 completion is measured by whether the unresolved evidence gates from Sprint 02 are actually resolved or honestly carried forward with an explicit blocker. It is not measured by implementation progress, profitability claims, or approval-by-omission.

## Completion Criteria

Sprint 03 may be declared complete only if all of the following are true:

1. Every unresolved Sprint 02 item has a traceable Sprint 03 destination and a clear reason for transfer.
2. Historical-data adequacy and sample limitations are documented without pretending the bounded sample is final or representative.
3. Candle construction, timestamps, completed-candle rules, missing/no-trade handling, and incomplete-candle rules are explicitly documented and, if accepted, verified in code and tests.
4. The first bounded experiment specification remains explicit about assumptions, validation split, and evidence thresholds rather than silently acting as an approval document.
5. Execution-cost realism and profitability validation remain separate gates and are not conflated with exploratory signal research.
6. No implementation, paper-trading, or live-trading approval is inferred from documentation work alone.
7. No application code, tests, market-data files, dependencies, or configuration files are added or modified.
8. Final Git status, `git diff --check`, and full diff inspection have been performed.

## Explicit Non-Criteria

The following do not satisfy Sprint 03 completion on their own:

- a positive backtest result,
- a claim of profitability,
- a paper-trading authorization,
- a live-trading authorization,
- an implementation approval,
- a silent assumption that the bounded research sample is final or representative.

## Safety Statement

Passing Sprint 03 documentation checks does not validate the strategy, prove economic edge, authorize implementation, authorize paper trading, or authorize live trading. It only preserves the research boundary, evidence requirements, and human-review gates required to keep the project honest.
