# S04-001 - Research Data Scope and Provenance

## Purpose

This document records the exact historical sample currently accepted for the bounded research workflow. It is a provenance and boundary record only. It does not claim that the sample is representative, complete, profitable, or approved for live trading.

## Approved source

- Source: Tardis.dev
- Market: BTC-EUR
- Instrument scope: Binance Jersey BTCEUR quote and trade data
- File type: daily gzip-compressed CSV files
- Use status: PROVISIONAL_BOUND_RESEARCH_ONLY

## Sample definition

The current approved sample is limited to the first calendar day of each month only.

This means that the accepted research boundary is:

- 2019-12-01
- 2020-01-01
- 2020-02-01
- 2020-03-01
- 2020-04-01
- 2020-05-01
- 2020-06-01
- 2020-07-01
- 2020-08-01
- 2020-09-01
- 2020-10-01
- 2020-11-01

The repository records this sample in the provenance manifest:

- `data/provenance/tardis_btc_eur_first_of_month_manifest.json`

The manifest states the dataset name, source, market, and the explicit status:

- dataset_name: `tardis_btc_eur_first_of_month_sample`
- source: `Tardis.dev`
- market: `BTC-EUR`
- status: `PROVISIONAL_BOUND_RESEARCH_ONLY`
- scope: `first calendar day of each month only`
- allowed_use: `bounded historical research and deterministic validation only`

## File naming and archive pattern

The accepted raw archive uses daily quote and trade pairs. The actual files observed in the working tree follow a mixed naming convention, as preserved in the manifest:

- `BTCEUR_quotes_20191201.csv.gz`
- `BTCEUR_trades_20191201.csv.gz`
- `BTCEUR_quotes_2020_01_01.csv.gz`
- `BTCEUR_trades_2020_01_01.csv.gz`
- ... and the same pattern continues for the remaining first-of-month dates.

The repository therefore treats file names as part of the raw provenance record rather than assuming a single normalized naming convention. The inventory is the source of truth for the current sample.

## Provenance evidence

The manifest records a file count of 12 and includes both quote and trade pairs for each accepted date. Each archive entry stores:

- the relative path,
- the file size in bytes,
- the SHA256 digest.

The accepted file pairs are:

| Date | Quote file | Trade file |
|---|---|---|
| 2019-12-01 | `data/tmp_tardis/BTCEUR_quotes_20191201.csv.gz` | `data/tmp_tardis/BTCEUR_trades_20191201.csv.gz` |
| 2020-01-01 | `data/tmp_tardis/BTCEUR_quotes_2020_01_01.csv.gz` | `data/tmp_tardis/BTCEUR_trades_2020_01_01.csv.gz` |
| 2020-02-01 | `data/tmp_tardis/BTCEUR_quotes_2020_02_01.csv.gz` | `data/tmp_tardis/BTCEUR_trades_2020_02_01.csv.gz` |
| 2020-03-01 | `data/tmp_tardis/BTCEUR_quotes_2020_03_01.csv.gz` | `data/tmp_tardis/BTCEUR_trades_2020_03_01.csv.gz` |
| 2020-04-01 | `data/tmp_tardis/BTCEUR_quotes_2020_04_01.csv.gz` | `data/tmp_tardis/BTCEUR_trades_2020_04_01.csv.gz` |
| 2020-05-01 | `data/tmp_tardis/BTCEUR_quotes_2020_05_01.csv.gz` | `data/tmp_tardis/BTCEUR_trades_2020_05_01.csv.gz` |
| 2020-06-01 | `data/tmp_tardis/BTCEUR_quotes_2020_06_01.csv.gz` | `data/tmp_tardis/BTCEUR_trades_2020_06_01.csv.gz` |
| 2020-07-01 | `data/tmp_tardis/BTCEUR_quotes_2020_07_01.csv.gz` | `data/tmp_tardis/BTCEUR_trades_2020_07_01.csv.gz` |
| 2020-08-01 | `data/tmp_tardis/BTCEUR_quotes_2020_08_01.csv.gz` | `data/tmp_tardis/BTCEUR_trades_2020_08_01.csv.gz` |
| 2020-09-01 | `data/tmp_tardis/BTCEUR_quotes_2020_09_01.csv.gz` | `data/tmp_tardis/BTCEUR_trades_2020_09_01.csv.gz` |
| 2020-10-01 | `data/tmp_tardis/BTCEUR_quotes_2020_10_01.csv.gz` | `data/tmp_tardis/BTCEUR_trades_2020_10_01.csv.gz` |
| 2020-11-01 | `data/tmp_tardis/BTCEUR_quotes_2020_11_01.csv.gz` | `data/tmp_tardis/BTCEUR_trades_2020_11_01.csv.gz` |

## Explicit exclusions

The sample does not support the following claims:

- statistical representativeness of the full BTC-EUR market,
- full-month adequacy or full-year completeness,
- profitability proof,
- paper-trading approval,
- live-trading approval,
- execution realism for Bitvavo,
- generalization beyond the frozen first-of-month research boundary.

The manifest also explicitly states the venue distinction:

- "historical research dataset is not a Bitvavo execution dataset"

## Decision status

This sample is accepted only as a bounded exploratory research archive for deterministic validation and historical signal analysis under explicit project rules.

It remains provisional and intentionally limited. The repository does not treat this sample as a final adequacy certificate or as an authorization to widen scope.

## Impact on Sprint 04

This record satisfies the first sprint deliverable for research data provenance and ensures that subsequent validation work can reference a fixed, documented dataset boundary.

The next action item remains:

- S04-002 - Implement raw-data ingestion contract
