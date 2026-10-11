# S03-102 - OHLCV Contract Verification Note

## Purpose

This note records the current evidence for the approved 5-minute OHLCV contract without claiming project approval, strategy readiness, or live execution authorization.

## Verified implementation evidence

The current implementation in `tools/hsra/ohlcv.py` is consistent with the bounded research contract and enforces the following behavior:

- trade-only OHLCV construction,
- UTC-aligned 5-minute bucket boundaries,
- interval-start timestamp semantics,
- open/high/low/close calculation from eligible trade prices,
- volume aggregation from trade quantities in the base asset,
- rejection of empty intervals instead of synthesizing or carry-forward candles,
- rejection of same-timestamp ambiguous trade sets,
- rejection of exact duplicate raw rows,
- rejection of conflicting duplicates that share a meaningful source ID but disagree on economic content,
- deterministic ordering by timestamp before bucket assignment.

This implementation is intentionally conservative and fail-closed. It does not claim to prove broader market adequacy or execution realism beyond the bounded research setting.

## Test evidence

Command run:

```bash
python -m pytest tests/test_hsra_ohlcv.py -q
```

Result:

```text
12 passed in 0.27s
```

This verifies that the implementation matches the current research contract for the tested trade-based 5-minute OHLCV behavior and edge-case rejection rules.

## Current status

- `S03-102` is active and evidence-backed.
- The implementation evidence and focused tests are positive.
- The human approval gate remains distinct from implementation correctness and must not be treated as automatic.
- This status does not authorize strategy implementation, paper trading, or live trading.
- The bounded historical sample still remains subject to the separate adequacy decision recorded under `S03-101`.
