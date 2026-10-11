# S04-003 - Canonical Event Validation

## Purpose

This document records the canonical validation policy used for the bounded Tardis historical research sample. It is a fail-closed validation contract for converting raw quote and trade rows into canonical market events without silently inventing missing data.

## Validation policy

The canonical event validation logic is implemented in:

- `tools/hsra/merger.py`
- `tests/test_hsra.py`

The validated rules are:

1. Input source files must exist.
2. The requested window must contain at least one trade; otherwise the dataset is rejected as `PARTIAL_WINDOW`.
3. The first trade in the window must not be preceded by valid quotes within the same requested interval; otherwise the dataset is rejected as `PRE_FIRST_TRADE_QUOTES_PRESENT`.
4. A quote is only valid if it follows a trade already seen in the same window.
5. No look-ahead is allowed: quotes cannot be emitted before the corresponding trade event in time.
6. `bid` and `ask` must be present and positive; `bid < ask` is required.
7. Trade price must be present and positive.
8. Events are sorted by timestamp ascending with the tie-break rule `trade_before_quote_when_equal_ts`.
9. Provenance records must map each canonical quote event to the last prior trade and preserve the exact schema used by the repository.
10. The canonical event stream is deterministic and must reproduce the same identity across repeated runs.

## Explicit rejection modes

The canonicalizer rejects a window with an explicit metadata payload rather than silently backfilling. Representative rejection modes include:

- `missing_required_source_file`
- `no_trades_in_requested_window`
- `pre_first_trade_quotes_present`
- `invalid_trade_price`
- `missing_bid_ask`
- `bid_not_lt_ask`
- `no_prior_trade_for_quote`

This means output is allowed only when the data is complete enough for an honest event stream under the current contract.

## Canonical schema

Each emitted canonical event uses this exact shape:

- `event_time_utc`
- `event_type`
- `market`
- `bid`
- `ask`
- `last`

Each provenance entry uses the exact schema:

- `canonical_index`
- `canonical_event_time`
- `source_quote_id`
- `source_quote_ts`
- `source_trade_id`
- `source_trade_ts`
- `adapter_version`
- `tie_break_rule`

## Fresh repository evidence

The focused validation suite was run with:

- `python -m pytest tests/test_hsra.py -q`

The current result is:

- 12 tests passed in 0.18s

This confirms that the canonicalizer and associated validation policies are working under the bounded sample contract without claiming broader adequacy or profitability.

## Impact on Sprint 04

This step satisfies the canonical validation gate for the data-intake workflow. The project remains within the bounded exploratory research scope and does not authorize strategy execution or scaling beyond the approved evidence boundary.

The next action item remains:

- S04-004 - Document bounded-sample adequacy decision
