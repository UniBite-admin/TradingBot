from __future__ import annotations

import json
import math
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, Iterator

from .merger import HSRAError
from .reader import SourceRecord, iter_trades


@dataclass(frozen=True)
class OHLCVCandle:
    interval_start: datetime
    interval_end: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    trade_count: int


def _coerce_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _bucket_start(ts: datetime, interval_minutes: int = 5) -> datetime:
    ts = _coerce_utc(ts)
    base_minute = (ts.minute // interval_minutes) * interval_minutes
    return ts.replace(minute=base_minute, second=0, microsecond=0)


def _bucket_starts(start: datetime, end: datetime, interval_minutes: int = 5) -> list[datetime]:
    starts: list[datetime] = []
    cursor = _coerce_utc(start)
    stop = _coerce_utc(end)
    while cursor < stop:
        starts.append(cursor)
        cursor += timedelta(minutes=interval_minutes)
    return starts


def _trade_amount(trade: SourceRecord) -> float:
    amount_raw = trade.raw_row.get("amount")
    if amount_raw in (None, ""):
        raise HSRAError(json.dumps({
            "status": "REJECTED",
            "reason": "missing_trade_amount",
            "trade_id": trade.source_id,
            "trade_ts": trade.ts.isoformat() if trade.ts is not None else None,
        }))
    try:
        amount = float(amount_raw)
    except (TypeError, ValueError):
        raise HSRAError(json.dumps({
            "status": "REJECTED",
            "reason": "invalid_trade_amount",
            "trade_id": trade.source_id,
            "trade_ts": trade.ts.isoformat() if trade.ts is not None else None,
        })) from None
    if not math.isfinite(amount) or amount <= 0:
        raise HSRAError(json.dumps({
            "status": "REJECTED",
            "reason": "invalid_trade_amount",
            "trade_id": trade.source_id,
            "trade_ts": trade.ts.isoformat() if trade.ts is not None else None,
        }))
    return amount


def _detect_exact_duplicate_rows(trades: list[SourceRecord]) -> None:
    """Detect exact duplicate raw trade rows (all fields identical).
    
    Policy: If the same trade appears twice in the raw data (exact row match),
    reject the entire window as the source data cannot be trusted.
    
    This checks raw_row, which is the complete dict from CSV parsing.
    """
    seen_rows: set = set()
    for trade in trades:
        # Create a hashable representation of the raw row
        # Convert the dict to a frozenset of items for hashing
        row_tuple = tuple(sorted((k, str(v)) for k, v in trade.raw_row.items()))
        if row_tuple in seen_rows:
            raise HSRAError(json.dumps({
                "status": "REJECTED",
                "reason": "exact_duplicate_raw_row",
                "source_id": trade.source_id,
                "trade_ts": trade.ts.isoformat() if trade.ts is not None else None,
                "raw_row": dict(trade.raw_row),
            }))
        seen_rows.add(row_tuple)


def _detect_repeated_source_ids_with_different_contents(trades: list[SourceRecord]) -> None:
    """Detect if the same meaningful source_id appears on different economic events.
    
    Policy: If trade_id or id field appears multiple times with different timestamps,
    prices, or amounts, reject the window as the source data has conflicting duplicates.
    
    Fallback IDs (filename:offset) are not treated as meaningful identifiers for this check,
    as filename collisions are possible and offset is only file-scoped. Only check if the
    original CSV had trade_id or id fields.
    """
    # Track meaningful source IDs (trade_id or id from CSV, not fallback)
    # Fallback IDs look like "filename:offset"
    meaningful_id_records: dict[str, list[SourceRecord]] = {}
    
    for trade in trades:
        # Check if this trade has a meaningful source_id (not a fallback)
        # Fallback format is "filename:offset", meaningful IDs typically don't contain ":"
        # But we can also check the raw_row to see if trade_id or id was present
        has_meaningful_id = "trade_id" in trade.raw_row or "id" in trade.raw_row
        
        if has_meaningful_id and trade.source_id:
            if trade.source_id not in meaningful_id_records:
                meaningful_id_records[trade.source_id] = []
            meaningful_id_records[trade.source_id].append(trade)
    
    # Now check for conflicts: same ID with different content
    for source_id, records in meaningful_id_records.items():
        if len(records) > 1:
            # Check if all records are truly identical or if they differ
            first_record = records[0]
            for other_record in records[1:]:
                # Consider records different if timestamp, price, or amount differs
                if (first_record.ts != other_record.ts or
                    first_record.price != other_record.price or
                    first_record.raw_row.get("amount") != other_record.raw_row.get("amount")):
                    # Conflicting records with same source_id
                    raise HSRAError(json.dumps({
                        "status": "REJECTED",
                        "reason": "conflicting_duplicate_source_id",
                        "source_id": source_id,
                        "conflict_count": len(records),
                        "first_record_ts": first_record.ts.isoformat() if first_record.ts else None,
                        "other_record_ts": other_record.ts.isoformat() if other_record.ts else None,
                        "note": "same source_id appears on records with different timestamps, prices, or amounts",
                    }))


def build_ohlcv_window(
    trades_path: str | Path,
    *,
    requested_start: datetime,
    requested_end: datetime,
    interval_minutes: int = 5,
) -> list[OHLCVCandle]:
    """Construct UTC-aligned 5-minute candles from raw trade events.

    Conservative, fail-closed behavior:
    - reject missing/invalid trade rows;
    - reject empty requested buckets;
    - reject same-timestamp ambiguous trade ordering within a bucket;
    - reject exact duplicate raw rows;
    - reject conflicting duplicates (same source_id on different economic events);
    - do not synthesize or forward-fill candles.
    
    Completed-candle caveat: The builder rejects the requested window if any
    validation fails, but it cannot independently establish that the final candle
    is "completed" without external metadata about source coverage. The caller
    must verify that requested_end represents an actual source-coverage boundary
    (e.g., via metadata from window_analysis.py or explicit confirmation).
    """
    if interval_minutes <= 0:
        raise HSRAError(json.dumps({
            "status": "REJECTED",
            "reason": "invalid_interval_minutes",
            "interval_minutes": interval_minutes,
        }))

    start = _coerce_utc(requested_start)
    end = _coerce_utc(requested_end)
    if end <= start:
        raise HSRAError(json.dumps({
            "status": "REJECTED",
            "reason": "invalid_window",
            "requested_start": start.isoformat(),
            "requested_end": end.isoformat(),
        }))

    path = Path(trades_path)
    if not path.exists() or not path.is_file():
        raise HSRAError(json.dumps({
            "status": "REJECTED",
            "reason": "missing_required_source_file",
            "source": "trades",
            "source_path": str(path),
        }))

    trades = [
        t for t in iter_trades(path)
        if t.ts is not None and start <= t.ts < end
    ]
    if not trades:
        raise HSRAError(json.dumps({
            "status": "REJECTED",
            "reason": "no_trades_in_requested_window",
            "requested_start": start.isoformat(),
            "requested_end": end.isoformat(),
        }))

    # Detect exact duplicate raw rows (all fields identical)
    _detect_exact_duplicate_rows(trades)
    
    # Detect conflicting duplicates (same source_id on different economic events)
    _detect_repeated_source_ids_with_different_contents(trades)

    # Sort trades by timestamp before bucketing.
    # Consistent with merger.py (line 127) and window_analysis.py (_sort_valid_trades).
    # Raw input order is not guaranteed; sorting establishes deterministic chronology.
    # Ambiguity detection (same-timestamp trades) happens per-bucket below.
    trades = sorted(trades, key=lambda t: t.ts)

    expected_buckets = _bucket_starts(start, end, interval_minutes)
    bucket_map: dict[datetime, list[SourceRecord]] = defaultdict(list)
    for trade in trades:
        bucket_start = _bucket_start(trade.ts, interval_minutes)
        if bucket_start < start or bucket_start >= end:
            continue
        bucket_map[bucket_start].append(trade)

    missing = [bucket.isoformat() for bucket in expected_buckets if bucket not in bucket_map]
    if missing:
        raise HSRAError(json.dumps({
            "status": "REJECTED",
            "reason": "empty_interval",
            "requested_start": start.isoformat(),
            "requested_end": end.isoformat(),
            "missing_intervals": missing,
        }))

    candles: list[OHLCVCandle] = []
    for bucket_start in expected_buckets:
        bucket_trades = sorted(bucket_map[bucket_start], key=lambda t: t.ts)
        by_ts: dict[datetime, list[SourceRecord]] = defaultdict(list)
        for trade in bucket_trades:
            by_ts[trade.ts].append(trade)

        ambiguous = [
            (ts.isoformat(), [t.source_id for t in members])
            for ts, members in by_ts.items()
            if len(members) > 1
        ]
        if ambiguous:
            raise HSRAError(json.dumps({
                "status": "REJECTED",
                "reason": "ambiguous_same_timestamp_trades",
                "bucket_start": bucket_start.isoformat(),
                "ambiguous_timestamps": ambiguous,
            }))

        ordered_prices: list[float] = []
        total_volume = 0.0
        for trade in bucket_trades:
            if trade.price is None or not math.isfinite(trade.price) or trade.price <= 0:
                raise HSRAError(json.dumps({
                    "status": "REJECTED",
                    "reason": "invalid_trade_price",
                    "trade_id": trade.source_id,
                    "trade_ts": trade.ts.isoformat() if trade.ts is not None else None,
                }))
            ordered_prices.append(float(trade.price))
            total_volume += _trade_amount(trade)

        candle = OHLCVCandle(
            interval_start=bucket_start,
            interval_end=bucket_start + timedelta(minutes=interval_minutes),
            open=ordered_prices[0],
            high=max(ordered_prices),
            low=min(ordered_prices),
            close=ordered_prices[-1],
            volume=total_volume,
            trade_count=len(bucket_trades),
        )
        candles.append(candle)

    return candles
