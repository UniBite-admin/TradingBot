# Sprint 01 - Acceptance Criteria

Sprint 01 completion is measured by documentation integrity, traceability, and evidence quality. It is not measured by strategy profitability, code existence, or operational activation.

## Completion Criteria

Sprint 01 can be declared complete only if all of the following are true:

1. The Sprint 01 document set exists at `docs/sprints/sprint-01/`.
2. `README.md`, `ACTION_ITEMS.md`, `DECISIONS.md`, and `ACCEPTANCE_CRITERIA.md` all exist and have distinct responsibilities.
3. The repository entrypoint links to Sprint 01 documentation.
4. `ACTION_ITEMS.md` contains unique stable task identifiers and valid dependency references.
5. Every sprint task records status, priority, expected output, verification method, and required evidence.
6. Documentation tasks are visibly separated from human-decision tasks.
7. `DECISIONS.md` separates repository-supported decisions from unresolved decisions.
8. No proposed strategy rule, technical recommendation, or human-decision item is silently represented as approved.
9. `ROADMAP.md` no longer states that the technical plan must be produced when `TECHNICAL_PLAN.md` already exists.
10. `TECHNICAL_PLAN.md` no longer contains stale repository findings disproved by inspected Git-backed evidence.
11. Sprint records clearly state that the proposed strategy is a hypothesis, not validated profitability.
12. Sprint records clearly preserve the distinct gates for historical research, backtesting, paper trading, controlled live testing, and scaling.
13. Sprint records clearly state that documentation completion does not authorize live trading.
14. Sprint records clearly state that out-of-sample evidence must not be repeatedly reused for parameter tuning.
15. Sprint records clearly state that unfavorable results must not be handled by weakening acceptance criteria.
16. Unfinished experiment-definition and human-decision work is explicitly transferred to the next sprint with traceable references rather than being silently closed or erased.
17. Git status and Git diff are inspected after the documentation changes.
18. The post-edit inspection shows that no application code or test files were modified.
19. The post-edit inspection shows that no unrelated changes were included.

## Required Evidence

The following evidence is required before Sprint 01 can be declared complete:

- inspection of the created Sprint 01 files,
- inspection of the modified root documentation files,
- post-edit `git status --short --branch` output,
- post-edit `git diff --stat` output,
- post-edit `git diff` inspection,
- sprint-transfer mapping from unfinished Sprint 01 tasks into Sprint 02,
- confirmation that all changed files are documentation files only,
- confirmation that strategy rules were not altered.

## Honest Closure Rule

Sprint 01 may close as `DONE` when its documentation-only scope is satisfied and any unfinished experiment-definition or approval-dependent work is explicitly transferred forward with traceable IDs and blockers.

## Explicit Non-Criteria

The following do not satisfy Sprint 01 completion on their own:

- creating files without verification,
- passing documentation linting alone,
- a profitable-looking hypothetical backtest,
- a positive narrative about the strategy,
- existence of a technical plan,
- existence of a strategy specification,
- existence of a Git repository.

## Live-Trading Safety Statement

Passing Sprint 01 documentation checks:

- does not establish strategy profitability,
- does not validate the backtest methodology,
- does not authorize paper trading,
- does not authorize live trading,
- does not authorize scaling,
- does not override Risk Engine authority,
- does not replace required human approvals.