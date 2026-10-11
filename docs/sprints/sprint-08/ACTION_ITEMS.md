# Sprint 08 - Action Items

Status vocabulary: `PROPOSED`, `OPEN`, `BLOCKED`, `IMPLEMENTED`, `TESTED`, `VALIDATED`, `DONE`

| ID | Title | Work to perform | Deliverable / result | Source references | Dependencies | Verification | Acceptance criteria | Evidence | Status | Blockers |
|---|---|---|---|---|---|---|---|---|---|---|
| S08-001 | Define paper-trading mode | Specify the operational boundaries, simulated balance and order flows, and required logging. | Paper mode configuration and mode-safety rules. | `ROADMAP.md`, `TECHNICAL_PLAN.md` | S07-002, S07-003 | Inspect mode behavior against project rules. | Paper mode is not a live execution path. | mode spec | OPEN | human approval |
| S08-002 | Implement order simulation and reconciliation | Simulate signals, risk approvals, order lifecycle, and fill reconciliation without external capital exposure. | Simulated order ledger and position state. | `TECHNICAL_PLAN.md` | S08-001 | Replay live-like sequences and check reconciliation. | No signal is treated as a fill without recorded evidence. | simulation log | PROPOSED | validation evidence |
| S08-003 | Add health, freshness, and emergency-stop checks | Monitor data staleness, order ambiguity, and safety conditions so that the system blocks unsafe actions. | Health-state transitions and emergency-stop conditions. | `TECHNICAL_PLAN.md`, `PROJECT_DEFINITION.md` | S08-002 | Simulate stale or unhealthy conditions and inspect block decisions. | Unsafe conditions block new exposure. | alert log | PROPOSED | design approval |
| S08-004 | Run operational scenarios | Exercise outage, partial fill, stale-data, and cancellation scenarios under paper mode. | Operational incident records and failure-case reports. | `TECHNICAL_PLAN.md` | S08-002, S08-003 | Execute scenario tests and inspect logs. | The system behaves conservatively under failure. | scenario report | PROPOSED | validation evidence |
| S08-005 | Record the paper-to-live gate | Document the conditions that must be met before any live testing can even be considered. | Gate document with evidence requirements. | `ROADMAP.md`, `PROJECT_DEFINITION.md` | S08-004 | Inspect the gate against the project definition. | No progression without explicit human approval and evidence. | gate record | OPEN | human approval |

## Human decision tasks

| ID | Title | Decision to make | Output | Source refs | Dependencies | Verification | Acceptance | Status | Blockers |
|---|---|---|---|---|---|---|---|---|---|
| S08-101 | Approve paper-trading readiness | Decide whether the system is ready for paper mode or whether more validation is required. | Human approval or explicit gap list. | `ROADMAP.md`, `PROJECT_DEFINITION.md` | S08-004 | Review the evidence and risk posture together. | Paper mode must not introduce new operational assumptions. | BLOCKED | human approval required |
