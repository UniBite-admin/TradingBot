# Sprint 04 - Action Items

Status vocabulary:

- `PROPOSED`
- `OPEN`
- `BLOCKED`
- `IMPLEMENTED`
- `TESTED`
- `VALIDATED`
- `DONE`

## Data and provenance tasks

| ID | Title | Work to perform | Deliverable / observable result | Source references | Dependencies | Verification procedure | Acceptance criteria | Evidence required | Status | Blockers |
|---|---|---|---|---|---|---|---|---|---|---|
| S04-001 | Define research data scope and provenance | Record the exact historical sample, source, file naming, and time-window boundaries for the bounded Tardis data. | A data provenance document for the current bounded sample with explicit limits and exclusions. | `ROADMAP.md`, `TECHNICAL_PLAN.md`, `S03-101`, `S03-006` | - | Inspect sample file inventory, archive notes, and boundary rules. | Only the approved bounded sample is listed; no attempt to claim full-month adequacy. | file inspection + sample inventory | IMPLEMENTED | `S03-101` may remain blocked |
| S04-002 | Implement raw-data ingestion contract | Build the minimal importer contract for raw quotes and trades in the approved bounded sample. | Stable import log and raw-file manifest for the data source. | `TECHNICAL_PLAN.md`, `STRATEGY_SPECIFICATION.md` | S04-001 | Check import logs and file parse results. | Raw rows are ingested reproducibly with metadata recorded. | import log and file inventory | TESTED | none |
| S04-003 | Enforce canonical event validation | Validate schema, timestamp normalization, duplicate detection, and ordering policy against the approved canonicalization rules. | Validated canonical event stream or explicit rejection records. | `TECHNICAL_PLAN.md`, `STRATEGY_SPECIFICATION.md`, `docs/sprints/sprint-03/DECISIONS.md` | S04-002 | Run deterministic validation fixtures and inspect rejected rows. | Invalid rows are quarantined; valid rows remain deterministic and ordered. | validation report | TESTED | `S03-102` remains open |
| S04-004 | Document bounded-sample adequacy decision | Record what is and is not proven by the current sample without claiming representativeness. | Decision record for `S03-101` stating the evidence status and remaining gap. | `ROADMAP.md`, `STRATEGY_SPECIFICATION.md`, `S03-101` | S04-001 | Compare the decision record against actual sample coverage and current repo evidence. | Decision distinguishes bounded research from final adequacy. | written decision record | IMPLEMENTED | `S03-101` remains invalidated |
| S04-005 | Create data-quality regression suite | Add deterministic fixtures for empty intervals, duplicates, stale timestamps, cross-file continuity issues, and missing data. | Reproducible data-quality test suite covering all rejection modes. | `TECHNICAL_PLAN.md`, `STRATEGY_SPECIFICATION.md` | S04-003 | Run tests and inspect pass/fail categories. | Rejected records are explicit and deterministic. | test report | TESTED | depends on sample contract |
| S04-006 | Prepare sprint gate for next-stage progression | Record the stage gate that blocks progression if the data evidence is not adequate or if anti-lookahead rules are violated. | A research gate that prevents progression into strategy implementation on insufficient evidence. | `PROJECT_DEFINITION.md`, `ROADMAP.md`, `TECHNICAL_PLAN.md` | S04-004, S04-005 | Review the gate against project definition and roadmap requirements. | Progression occurs only with evidence and explicit human approval. | gate document and signoff | IMPLEMENTED | requires human approval |

## Human decision tasks

| ID | Title | Decision to make | Output | Source references | Dependencies | Verification | Acceptance | Status | Blockers |
|---|---|---|---|---|---|---|---|---|---|
| S04-101 | Approve bounded-sample adequacy status | Decide whether the sample is adequate only for bounded exploratory signal research, or whether extra evidence is required before use. | Human-approved evidence statement for `S03-101`. | `ROADMAP.md`, `STRATEGY_SPECIFICATION.md`, `TECHNICAL_PLAN.md` | - | Document the final decision and its limitations. | The decision clearly states whether the sample is provisional or insufficient. | BLOCKED | requires human approval |
