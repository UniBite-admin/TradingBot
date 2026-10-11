# Trading Bot

This repository is now in the final evidence and approval gate, not in the planning-only stage.

Authoritative documents:

- [PROJECT_DEFINITION.md](PROJECT_DEFINITION.md)
- [ROADMAP.md](ROADMAP.md)
- [STRATEGY_SPECIFICATION.md](STRATEGY_SPECIFICATION.md)
- [TECHNICAL_PLAN.md](TECHNICAL_PLAN.md)

Current sprint documentation:

- [docs/sprints/sprint-01/README.md](docs/sprints/sprint-01/README.md)
- [docs/sprints/sprint-02/README.md](docs/sprints/sprint-02/README.md)
- [docs/sprints/sprint-03/README.md](docs/sprints/sprint-03/README.md)
- [docs/sprints/sprint-04/README.md](docs/sprints/sprint-04/README.md)
- [docs/sprints/sprint-05/README.md](docs/sprints/sprint-05/README.md)
- [docs/sprints/sprint-06/README.md](docs/sprints/sprint-06/README.md)
- [docs/sprints/sprint-07/README.md](docs/sprints/sprint-07/README.md)
- [docs/sprints/sprint-08/README.md](docs/sprints/sprint-08/README.md)
- [docs/sprints/sprint-09/README.md](docs/sprints/sprint-09/README.md)

Current status:

- The historical research pipeline, deterministic replay, strategy logic, backtest harness, validation stress checks, paper-trading safety model, and final evaluation gate are implemented and validated.
- The repository evidence supports a bounded research-and-validation system with explicit guardrails, but it does not prove a profitable live strategy.
- The system remains in a historical research and controlled validation state. It is not authorized to trade live or scale automatically.
- Sprint 08 is in the validated paper-mode safety state: simulated execution and safety rules are in place, but live transition remains blocked by explicit human approval.
- Sprint 09 is the final decision gate: controlled live test and controlled scale remain explicitly blocked until the evidence and human approval are both present.
- Bitvavo Spot remains the intended live venue, but the project is still separated from live execution by the approval chain.
- The dataset, OHLCV semantics, and validation rules have been implemented and tested under strict no-lookahead rules.
- No strategy profitability claim is valid without explicit evaluation evidence and human approval.

Repository rule:

- If a requirement, parameter, or decision is not explicitly documented and approved, it is not approved.