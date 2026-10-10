# Trading Bot

This repository is currently in the definition and planning stage.

Authoritative documents:

- [PROJECT_DEFINITION.md](PROJECT_DEFINITION.md)
- [ROADMAP.md](ROADMAP.md)
- [STRATEGY_SPECIFICATION.md](STRATEGY_SPECIFICATION.md)
- [TECHNICAL_PLAN.md](TECHNICAL_PLAN.md)

Current sprint documentation:

- [docs/sprints/sprint-01/README.md](docs/sprints/sprint-01/README.md)
- [docs/sprints/sprint-02/README.md](docs/sprints/sprint-02/README.md)
- [docs/sprints/sprint-03/README.md](docs/sprints/sprint-03/README.md)

Current status:

- A proposed trading strategy specification exists and is pending human review.
- A proposed technical plan and implementation roadmap exists and is pending human review.
- Sprint 01 is closed as a documentation-only sprint with deferred experiment-definition work transferred forward.
- Sprint 02 is closed as a documentation and decision-governance sprint. Its unresolved evidence gaps and blocked planning items were transferred to Sprint 03 without claiming strategy approval, implementation readiness, or live-trading authorization.
- Sprint 03 continues the remaining first-experiment evidence gates: historical-data adequacy and representativeness, candle construction and timestamp semantics, chronological holdout design, realistic cost-model evidence, and the blocked first-experiment specification.
- Bitvavo Spot is the intended execution venue and remains separate from the historical research dataset.
- The historical research dataset for the first experiment is provisionally accepted as Tardis.dev Binance Jersey BTCEUR quotes and trades in daily `.csv.gz` files, limited to the first calendar day of each month only.
- This provisional acceptance is for continued research under the current data-access and budget constraints; it does not prove statistical representativeness, final dataset adequacy, or strategy profitability.
- Official Tardis metadata confirms that the `btceur` symbol existed from 2019-10-30 through 2020-11-10, but the exact public dataset URLs for the candidate first-of-month BTCEUR trades/quotes files returned HTTP 404 in direct minimal checks from this environment. The file-level availability remains unverified until a documented access path confirms the exact daily files; the sample therefore remains provisional and is not final adequacy-validated.
- First-of-month sampling may introduce selection bias and may not represent the full month; a future full-month purchase remains a separate human budget decision and is not authorized by this provisional scope.
- The unresolved first-experiment evidence work has been transferred from Sprint 02 to Sprint 03. The strategy and first experiment remain unapproved.
- No implementation has started.
- Live trading is out of scope until research, validation, and controlled testing gates are passed.

Repository rule:

- If a requirement, parameter, or decision is not explicitly documented and approved, it is not approved.