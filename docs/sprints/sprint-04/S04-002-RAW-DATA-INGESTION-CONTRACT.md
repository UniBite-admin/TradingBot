# S04-002 - Raw-data Ingestion Contract

## Purpose

This record defines the minimum raw-data ingestion contract for the bounded Tardis historical research sample. It is intentionally conservative: it documents what is accepted, what is rejected, and how the raw file inventory is recorded before any downstream canonicalization or strategy work proceeds.

## Ingestion scope

- Source: Tardis.dev
- Market: BTC-EUR
- Data type: quote and trade CSV records
- Storage path: `data/tmp_tardis/`
- Approved sample: the first calendar day of each month, consistent with the S04-001 provenance boundary
- Only research files are accepted for the bounded sample; no broader market expansion is implied by this contract.

## File naming contract

The raw files in the working tree are treated as the repository inventory for the current sample. The accepted pattern is:

- `BTCEUR_quotes_<date>.csv.gz`
- `BTCEUR_trades_<date>.csv.gz`

Examples:

- `BTCEUR_quotes_20191201.csv.gz`
- `BTCEUR_trades_20191201.csv.gz`
- `BTCEUR_quotes_2020_01_01.csv.gz`
- `BTCEUR_trades_2020_01_01.csv.gz`

The contract requires the file name to be recorded alongside the SHA256 checksum and size in bytes. This makes the raw-input boundary reproducible and directly auditable.

## Reader and validation contract

The repository’s raw parser contract is implemented in:

- `tools/hsra/reader.py`
- `data/tmp_tardis/audit_tardis_dataset.py`

The rules currently enforced are:

1. Read gzip-compressed CSV files transparently when the filename ends in `.gz`.
2. Accept either integer epoch-microseconds timestamps or ISO-8601 timestamps with timezone information.
3. Normalize the market field to the canonical `BTC-EUR` style when relevant.
4. Reject missing files and empty files.
5. Reject rows with malformed timestamps.
6. Reject rows with missing required fields.
7. Reject exact duplicate rows.
8. Reject quote rows with `bid >= ask`.
9. Reject invalid trade rows with non-positive or malformed price/quantity values.
10. Record file-level metadata, including path, size, and SHA256.

## Deterministic audit behavior

The raw-data audit writes a machine-readable report under:

- `data/tmp_tardis/audit_reports/sprint04_raw_ingestion_contract.json`

The audit is intentionally read-only and uses the same file inventory, file parser, and checksum logic as the canonicalization pipeline. It does not rewrite or move the source archives.

## Explicit rejection policy

The audit is fail-closed for raw ingestion problems. If any of the following are detected, the file is marked as `FAIL` and the reason is recorded:

- missing input file,
- empty file,
- zero records,
- missing header,
- invalid timestamp,
- missing required fields,
- duplicate rows,
- invalid price or quantity,
- quote bid/ask inversion.

This policy ensures that any downstream processing only sees a deterministic, validated raw-input boundary rather than silently inventing missing or ambiguous data.

## Current evidence

Fresh verification was executed with:

- `python data/tmp_tardis/audit_tardis_dataset.py --root . --output data/tmp_tardis/audit_reports/sprint04_raw_ingestion_contract.json`

Result summary from the run:

- all raw quote files in the bounded sample reported `PASS`,
- all raw trade files in the bounded sample reported `PASS`,
- all canonicalized daily datasets for the first-calendar-day sample also reported `PASS`,
- the only rejected validation metadata is from intentionally partial validation windows, not from the accepted bounded sample itself.

This supports the raw-data contract without claiming broader market adequacy or execution readiness.

## Impact on Sprint 04

This action item is satisfied by a documented and tested ingestion contract for the bounded Tardis sample. The next gate is the canonical validation step, which must preserve the same fail-closed rules and evidence chain.

The next action item remains:

- S04-003 - Enforce canonical event validation
