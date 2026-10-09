# Sprint 01 - Action Items

This file is the authoritative Sprint 01 task register.

Historical transfer note:

- Sprint 01 is closed as a documentation-only sprint.
- Unfinished experiment-definition and human-decision work has been transferred to Sprint 02 with traceable references.

Status vocabulary:

- `NOT_STARTED`
- `IN_PROGRESS`
- `BLOCKED`
- `DONE`

Priority vocabulary:

- `HIGH`
- `MEDIUM`
- `LOW`

## Documentation Tasks

| ID | Type | Description | Rationale | Priority | Status | Dependencies | Expected Output | Verification Method | Required Evidence | Blocker / Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| S01-001 | DOCUMENTATION | Establish the Sprint 01 documentation set and link it from the repository entrypoint. | Sprint tracking must live in the repository, not only in chat history. | HIGH | DONE | - | `docs/sprints/sprint-01/README.md`, `ACTION_ITEMS.md`, `DECISIONS.md`, `ACCEPTANCE_CRITERIA.md`, plus root README link. | Inspect created files and root README link targets. | File inspection and Git diff. | Completed in this change set. |
| S01-002 | DOCUMENTATION | Correct the stale Stage 2 roadmap inconsistency in `ROADMAP.md`. | The roadmap still stated that the technical plan had to be produced even though `TECHNICAL_PLAN.md` already exists. | HIGH | DONE | - | `ROADMAP.md` reflects that the technical plan exists and the next action is review plus resolution of blocked Stage 2 decisions, not plan creation. | Inspect `ROADMAP.md` and compare against repository contents. | File inspection and Git diff. | Completed in this change set. |
| S01-003 | DOCUMENTATION | Correct stale repository findings in `TECHNICAL_PLAN.md` using current Git-backed evidence only. | The technical plan contained stale repository findings that omitted `TECHNICAL_PLAN.md` and incorrectly said the workspace was not a Git repository. | HIGH | DONE | - | `TECHNICAL_PLAN.md` reflects the inspected repository file set, current Git state, and current version-control reality. | Inspect corrected sections and compare with `git status`, branch, and remote state. | File inspection, Git status output, and Git diff. | Completed in this change set. |
| S01-004 | DOCUMENTATION | Create a complete unresolved-decision register for the first research experiment. | Critical decisions are split across the strategy and technical plan and must be visible in one sprint-level place. | HIGH | DONE | S01-001 | `DECISIONS.md` with supported decisions, unresolved decisions, and deferral candidates. | Inspect identifiers, decision content, and cross-check against the strategy and technical plan. | File inspection and repository-document inspection. | Completed in this change set. |
| S01-005 | DOCUMENTATION | Record Sprint 01 acceptance criteria and evidence requirements. | Sprint completion cannot be claimed from file creation alone. | HIGH | DONE | S01-001 | `ACCEPTANCE_CRITERIA.md` with measurable completion criteria and required evidence. | Inspect criteria and evidence requirements. | File inspection. | Completed in this change set. |
| S01-006 | DOCUMENTATION | Define the first bounded research experiment as a separate controlled specification. | The proposed strategy cannot be evaluated reproducibly until the first experiment is frozen with explicit data, timing, cost-model, and validation rules. | HIGH | BLOCKED | S01-004, S01-101, S01-102, S01-103 | A bounded first-experiment specification that states hypothesis, inputs, outputs, timing, anti-lookahead rules, cost model, validation split, and acceptance or rejection evidence. | Human review against the authoritative strategy specification, technical plan, and unresolved-decision register. | Future approved experiment document or approved experiment section. | Transferred to `S02-006`. Completion remains blocked by unresolved exchange, timeframe, candle semantics, parameter-grid, and cost-model decisions. |
| S01-007 | DOCUMENTATION | Record which technical-plan components are candidates for deferral from the first research experiment scope. | The first experiment should not silently expand into full operational infrastructure. | MEDIUM | DONE | S01-004 | Sprint documentation that preserves evidence-backed deferral candidates already supported by `TECHNICAL_PLAN.md`. | Inspect `DECISIONS.md` deferral section against `TECHNICAL_PLAN.md`. | File inspection. | Completed in this change set without rewriting the technical plan. |
| S01-008 | DOCUMENTATION | Preserve the separation between signal, risk approval, order request, acknowledgement, fill, and final account or position state in the future experiment definition. | Research and accounting become invalid if these states are conflated. | HIGH | NOT_STARTED | S01-006 | First-experiment documentation that explicitly preserves the existing cross-document state distinctions. | Inspect future experiment specification against the strategy and technical plan. | Future experiment document review. | Transferred to `S02-007`. Current authoritative docs already separate these states; this task is to preserve that separation in the first experiment definition. |
| S01-009 | DOCUMENTATION | Verify the Sprint 01 documentation-only change set with file inspection, Git status, and Git diff. | Sprint completion claims require post-edit inspection and proof that no unrelated files changed. | HIGH | DONE | S01-001, S01-002, S01-003, S01-004, S01-005 | Verified post-edit repository state. | Inspect created and modified files, run `git status --short --branch`, and inspect `git diff --stat` plus `git diff`. | File inspection, Git status output, and Git diff. | Completed in this change set. |

## Human-Decision Tasks

| ID | Type | Description | Rationale | Priority | Status | Dependencies | Expected Output | Verification Method | Required Evidence | Blocker / Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| S01-101 | HUMAN_DECISION | Approve the exchange and authoritative market-data source for the first research experiment. | Exchange and source semantics affect candles, fees, liquidity, fills, and execution constraints. | HIGH | NOT_STARTED | - | Approved exchange and data-source decision recorded in an authoritative project document. | Inspect the authoritative document update. | Approved documentation update. | Transferred to `S02-101`. Blocks completion of the first bounded experiment definition. |
| S01-102 | HUMAN_DECISION | Approve the primary timeframe and candle-semantics policy for the first research experiment. | The strategy and replay logic depend on timeframe, timestamp meaning, finalization rules, and missing-candle handling. | HIGH | NOT_STARTED | - | Approved decision covering timeframe, candle timestamps, timezone, finalization, and continuity policy. | Inspect the authoritative document update. | Approved documentation update. | Transferred to `S02-102`. Blocks completion of the first bounded experiment definition. |
| S01-103 | HUMAN_DECISION | Approve the first experiment's parameter-selection and execution-cost policy. | The first experiment cannot be frozen without a decision on parameter-grid discipline and how fees, spread, slippage, latency, liquidity, and fill assumptions will be modeled. | HIGH | NOT_STARTED | - | Approved experiment-policy decision covering `L`, `N`, signal expiry, cost-model policy, and out-of-sample discipline. | Inspect the authoritative document update. | Approved documentation update. | Transferred to `S02-103`. Blocks completion of the first bounded experiment definition. |
| S01-104 | HUMAN_DECISION | Decide whether provisional strategy implementation is allowed before the proposed strategy is formally approved. | The technical plan explicitly treats this as a gating decision for later implementation phases. | MEDIUM | NOT_STARTED | - | Approved implementation-governance decision recorded in an authoritative document. | Inspect the authoritative document update. | Approved documentation update. | Transferred to `S02-104`. Does not block Sprint 01 documentation completion, but it blocks later implementation planning beyond documentation. |

## Deferred Work Mapping

| Sprint 01 ID | Sprint 02 ID | Reason For Transfer |
|---|---|---|
| S01-006 | S02-006 | Experiment specification work remains blocked by unresolved human decisions. |
| S01-008 | S02-007 | Depends on the future experiment specification rather than Sprint 01 documentation integrity. |
| S01-101 | S02-101 | Human approval still required. |
| S01-102 | S02-102 | Human approval still required. |
| S01-103 | S02-103 | Human approval still required. |
| S01-104 | S02-104 | Human approval still required. |