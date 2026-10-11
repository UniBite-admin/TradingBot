# S04-004 - Bounded-sample Adequacy Decision

## Purpose

This document records the repository decision for the current Tardis historical sample used in the bounded research workflow. It is a scope and evidence statement, not a claim that the dataset is statistically representative, complete, or suitable for full production validation.

## Evidence base

The current evidence includes:

- `data/provenance/tardis_btc_eur_first_of_month_manifest.json`
- `docs/sprints/sprint-03/S03-101-DATA-ADEQUACY.md`
- `docs/sprints/sprint-03/DECISIONS.md`
- `tools/hsra/reader.py`
- `tools/hsra/merger.py`
- `tools/hsra/ohlcv.py`

The manifest records the attached sample as:

- dataset_name: `tardis_btc_eur_first_of_month_sample`
- source: `Tardis.dev`
- market: `BTC-EUR`
- status: `PROVISIONAL_BOUND_RESEARCH_ONLY`
- scope: `first calendar day of each month only`
- allowed_use: `bounded historical research and deterministic validation only`

## What is proven

The current sample is sufficient to support only the following bounded uses:

- deterministic pipeline validation,
- historical data handling checks,
- canonicalization and rejection-policy tests,
- bounded exploratory signal research under explicit scope limits,
- reproducible documentation and replay tests within the frozen sample boundary.

## What is not proven

The current sample does not establish any of the following:

- full market representativeness,
- full-month or full-year adequacy,
- profitability or positive expectancy,
- realistic Bitvavo execution cost or fill behavior,
- live-trading or paper-trading approval,
- broad generalization beyond the first-calendar-day sample boundary.

The repository also explicitly distinguishes the historical research archive from the intended Bitvavo execution venue.

## Decision statement

The bounded Tardis.dev Binance Jersey BTCEUR first-of-month sample is accepted only for exploratory research under the project’s explicit constraints. It remains a limited dataset with a non-random boundary and must not be treated as a final adequacy claim, a representative market history, or a profitability signal.

This decision therefore stands as a provisional, bounded adequacy statement only.

## Remaining gap

The unresolved adequacy gap remains separate from the technical implementation evidence. The project can continue within the frozen research boundary only if:

- the bounded sample remains the only data source,
- the no-backfill and no-lookahead rules stay in place,
- no broader adequacy claim is promoted beyond the sample boundary,
- no strategy approval or scaling decision is made without new evidence and explicit human approval.

## Impact on Sprint 04

This record resolves the action item for documenting the adequacy decision and preserves the repository’s distinction between:

- bounded exploratory research, and
- final representativeness or execution approval.

The next action item remains:

- S04-005 - Create data-quality regression suite
