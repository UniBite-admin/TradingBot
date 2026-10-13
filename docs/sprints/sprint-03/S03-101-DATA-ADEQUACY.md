# S03-101 - Historical Data Adequacy Decision Note

## Purpose

This note records the current evidence for the historical sample used in the bounded exploratory research plan. It does not claim final dataset adequacy, statistical representativeness, or strategy profitability.

## Evidence in the repository

The bounded sample was recorded in the provenance manifest at:

- `data/provenance/tardis_btc_eur_first_of_month_manifest.json`

The manifest states:

- dataset name: `tardis_btc_eur_first_of_month_sample`
- source: `Tardis.dev`
- market: `BTC-EUR`
- status: `PROVISIONAL_BOUND_RESEARCH_ONLY`
- scope: `first calendar day of each month only`
- allowed use: `bounded historical research and deterministic validation only`
- excluded claims: statistical representativeness, final dataset adequacy, profitability proof, paper-trading approval, live-trading approval

The repository also records that the sample contains 12 files covering the first calendar day of each month from 2019-12-01 through 2020-11-01.

## What the evidence proves

The current sample supports only the following bounded use:

- exploratory signal research under explicit research-only limits,
- deterministic validation and pipeline checks,
- documentation of data handling limits,
- controlled comparisons inside the frozen research boundary.

## What the evidence does not prove

The current sample does not establish any of the following:

- full-month representativeness,
- monthly regime coverage for all trading conditions,
- statistical validity for the entire BTC-EUR market,
- realistic Bitvavo execution cost or fill realism,
- strategy profitability or positive expectancy,
- approval for paper trading or live trading.

## Decision statement

The bounded Tardis.dev Binance Jersey BTCEUR first-of-month sample is provisionally acceptable only for exploratory research under the current project constraints. It remains a limited dataset with a non-random sample boundary and cannot be elevated to a final adequacy claim without separate evidence.

This decision is therefore recorded as a bounded, provisional adequacy status only. It is not a claim that the sample is representative, complete, or profitable, and it does not authorize a Bitvavo execution-realism or profitability claim. Final historical-data adequacy and representativeness remain unresolved; Bitvavo execution realism and profitability remain separate, unapproved gates.

## Impact on Sprint 03

This keeps the project aligned with the explicit gate:

- `S03-101` is complete only for the bounded exploratory research decision,
- the dataset can be used for bounded testing and signal research only,
- any broader adequacy, representativeness, Bitvavo realism, or profitability claim remains blocked until additional evidence is produced and explicitly approved.

The current evidence supports continuation of the project within the bounded research scope only. It does not authorize broader strategy validation, paper trading, or live trading.
