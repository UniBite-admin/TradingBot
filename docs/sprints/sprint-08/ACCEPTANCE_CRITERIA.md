# Sprint 08 - Acceptance Criteria

Sprint 08 is acceptable only when the system behaves safely under simulated operations and clearly preserves the live-risk boundary.

## Completion conditions

1. Paper-trading mode is documented and structurally distinct from live execution.
2. Simulated fills, rejections, and reconciliations are traceable.
3. Safety and emergency-stop checks can block exposure under stale or unhealthy conditions.
4. Incident and review logs are preserved for later evidence.
5. No live approval is implied by the paper-trading stage.

## Required evidence

- paper-mode spec,
- operational scenario logs,
- health-check incident reports,
- gate record requiring human approval before moving to live testing.

## Non-criteria

- no real-money execution,
- no scaling,
- no claim of profitability or deployment readiness.
