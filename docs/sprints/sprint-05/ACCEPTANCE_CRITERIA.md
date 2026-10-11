# Sprint 05 - Acceptance Criteria

Sprint 05 is acceptable only when the candle pipeline is deterministic, valid, and explicit about its limits.

## Completion conditions

1. The 5-minute candle contract and bucket semantics are written and traceable.
2. The OHLCV builder uses raw trades only and rejects invalid or ambiguous intervals.
3. The replay kernel preserves time ordering and excludes the current incomplete candle from entry logic.
4. Deterministic tests cover missing, empty, duplicate, and out-of-order window behavior.
5. No silent backfilling or assumption-based completion is allowed.
6. The sprint records its remaining evidence gap without claiming profitability or live readiness.

## Required evidence

- test suite output,
- rejection logs for invalid intervals,
- deterministic replay comparison,
- stage gate showing no automatic progression.

## Non-criteria

- no positive expectancy claim,
- no paper-trading authorization,
- no live-trading authorization,
- no claim that the implementation is production-ready.
