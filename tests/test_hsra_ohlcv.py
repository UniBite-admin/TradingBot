import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from tools.hsra.ohlcv import build_ohlcv_window
from tools.hsra.merger import HSRAError


def _write_csv(path: Path, rows: list[str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        fh.write(rows[0] + "\n")
        for row in rows[1:]:
            fh.write(row + "\n")


def test_builds_utc_aligned_5m_candles_from_trade_events_only(tmp_path):
    trades = tmp_path / "trades.csv"
    _write_csv(trades, [
        "timestamp,market,price,amount,trade_id",
        "2020-01-01T00:00:00Z,BTC-EUR,100.0,1.0,t1",
        "2020-01-01T00:02:30Z,BTC-EUR,102.0,0.5,t2",
        "2020-01-01T00:04:00Z,BTC-EUR,99.0,0.75,t3",
        "2020-01-01T00:05:00Z,BTC-EUR,110.0,1.2,t4",
        "2020-01-01T00:06:00Z,BTC-EUR,115.0,0.4,t5",
        "2020-01-01T00:09:59Z,BTC-EUR,108.0,0.9,t6",
    ])

    candles = build_ohlcv_window(
        trades,
        requested_start=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc),
        requested_end=datetime(2020, 1, 1, 0, 10, tzinfo=timezone.utc),
    )

    assert [c.interval_start.isoformat() for c in candles] == [
        "2020-01-01T00:00:00+00:00",
        "2020-01-01T00:05:00+00:00",
    ]
    assert candles[0].open == 100.0
    assert candles[0].high == 102.0
    assert candles[0].low == 99.0
    assert candles[0].close == 99.0
    assert candles[0].volume == pytest.approx(2.25)
    assert candles[1].open == 110.0
    assert candles[1].high == 115.0
    assert candles[1].low == 108.0
    assert candles[1].close == 108.0
    assert candles[1].volume == pytest.approx(2.5)


def test_rejects_empty_intervals_without_synthesizing_candles(tmp_path):
    trades = tmp_path / "trades.csv"
    _write_csv(trades, [
        "timestamp,market,price,amount,trade_id",
        "2020-01-01T00:00:00Z,BTC-EUR,100.0,1.0,t1",
        "2020-01-01T00:10:00Z,BTC-EUR,101.0,1.5,t2",
    ])

    with pytest.raises(HSRAError) as ei:
        build_ohlcv_window(
            trades,
            requested_start=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc),
            requested_end=datetime(2020, 1, 1, 0, 15, tzinfo=timezone.utc),
        )

    info = json.loads(str(ei.value))
    assert info["reason"] == "empty_interval"
    assert "2020-01-01T00:05:00+00:00" in info["missing_intervals"]


def test_rejects_ambiguous_same_timestamp_trades(tmp_path):
    trades = tmp_path / "trades.csv"
    _write_csv(trades, [
        "timestamp,market,price,amount,trade_id",
        "2020-01-01T00:00:00Z,BTC-EUR,100.0,1.0,t1",
        "2020-01-01T00:00:00Z,BTC-EUR,101.0,0.5,t2",
        "2020-01-01T00:04:00Z,BTC-EUR,103.0,0.7,t3",
        "2020-01-01T00:05:30Z,BTC-EUR,105.0,0.8,t4",
    ])

    with pytest.raises(HSRAError) as ei:
        build_ohlcv_window(
            trades,
            requested_start=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc),
            requested_end=datetime(2020, 1, 1, 0, 10, tzinfo=timezone.utc),
        )

    info = json.loads(str(ei.value))
    assert info["reason"] == "ambiguous_same_timestamp_trades"
    assert info["bucket_start"] == "2020-01-01T00:00:00+00:00"


def test_rejects_invalid_trade_records(tmp_path):
    trades = tmp_path / "trades.csv"
    _write_csv(trades, [
        "timestamp,market,price,amount,trade_id",
        "2020-01-01T00:00:00Z,BTC-EUR,0.0,1.0,t1",
    ])

    with pytest.raises(HSRAError):
        build_ohlcv_window(
            trades,
            requested_start=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc),
            requested_end=datetime(2020, 1, 1, 0, 5, tzinfo=timezone.utc),
        )


def test_is_deterministic_for_identical_inputs(tmp_path):
    trades = tmp_path / "trades.csv"
    _write_csv(trades, [
        "timestamp,market,price,amount,trade_id",
        "2020-01-01T00:00:00Z,BTC-EUR,100.0,1.0,t1",
        "2020-01-01T00:02:00Z,BTC-EUR,102.0,0.5,t2",
        "2020-01-01T00:05:00Z,BTC-EUR,103.0,2.0,t3",
        "2020-01-01T00:07:00Z,BTC-EUR,104.0,0.6,t4",
    ])

    first = build_ohlcv_window(
        trades,
        requested_start=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc),
        requested_end=datetime(2020, 1, 1, 0, 10, tzinfo=timezone.utc),
    )
    second = build_ohlcv_window(
        trades,
        requested_start=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc),
        requested_end=datetime(2020, 1, 1, 0, 10, tzinfo=timezone.utc),
    )

    assert [c.__dict__ for c in first] == [c.__dict__ for c in second]


def test_accepts_and_sorts_out_of_order_input(tmp_path):
    """Accept out-of-order input and sort by event timestamp.
    
    Policy basis: Raw trade data may arrive in any order from source files.
    The builder sorts by event timestamp before bucketing, consistent with
    merger.py (line 127) and window_analysis.py canonicalization patterns.
    
    Evidence: Both merger.py and window_analysis.py explicitly sort input
    by timestamp, indicating raw input order is not guaranteed.
    
    Do not reject based on arrival order. Preserve deterministic output:
    identical timestamps produce identical candles regardless of input order.
    """
    trades = tmp_path / "trades.csv"
    _write_csv(trades, [
        "timestamp,market,price,amount,trade_id",
        "2020-01-01T00:02:00Z,BTC-EUR,102.0,0.5,t2",
        "2020-01-01T00:00:00Z,BTC-EUR,100.0,1.0,t1",
        "2020-01-01T00:05:00Z,BTC-EUR,103.0,0.8,t3",
        "2020-01-01T00:07:00Z,BTC-EUR,104.0,0.6,t4",
    ])

    # Should not reject out-of-order input; should sort by timestamp
    candles = build_ohlcv_window(
        trades,
        requested_start=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc),
        requested_end=datetime(2020, 1, 1, 0, 10, tzinfo=timezone.utc),
    )

    # Should get 2 candles (both intervals have trades after sorting)
    assert len(candles) == 2
    # First candle [00:00, 00:05) contains t1@00:00 and t2@00:02 (after sorting by ts)
    assert candles[0].interval_start.isoformat() == "2020-01-01T00:00:00+00:00"
    assert candles[0].open == 100.0
    assert candles[0].close == 102.0
    # Second candle [00:05, 00:10) contains t3@00:05 and t4@00:07
    assert candles[1].interval_start.isoformat() == "2020-01-01T00:05:00+00:00"
    assert candles[1].open == 103.0
    assert candles[1].close == 104.0


def test_rejects_exact_duplicate_raw_rows(tmp_path):
    """Reject if an identical raw trade row appears multiple times.
    
    Policy basis (STRATEGY_SPECIFICATION L139): "If identical duplicates are 
    confirmed as exact repeated rows from the same source, they may be collapsed 
    only under a documented canonical rule; if the source semantics do not prove 
    that they are harmless duplicates, the affected record set must be rejected 
    rather than silently merged."
    
    Implementation: Compare all raw rows for exact field-by-field match.
    If found, reject entire window.
    """
    trades = tmp_path / "trades.csv"
    _write_csv(trades, [
        "timestamp,market,price,amount,trade_id",
        "2020-01-01T00:00:00Z,BTC-EUR,100.0,1.0,t1",
        "2020-01-01T00:00:00Z,BTC-EUR,100.0,1.0,t1",  # exact duplicate
        "2020-01-01T00:05:00Z,BTC-EUR,102.0,0.8,t2",
    ])

    with pytest.raises(HSRAError) as ei:
        build_ohlcv_window(
            trades,
            requested_start=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc),
            requested_end=datetime(2020, 1, 1, 0, 10, tzinfo=timezone.utc),
        )

    info = json.loads(str(ei.value))
    assert info["reason"] == "exact_duplicate_raw_row"


def test_rejects_repeated_source_id_different_timestamp(tmp_path):
    """Reject if the same trade_id appears with different timestamps.
    
    Policy basis (STRATEGY_SPECIFICATION L143): "deterministic replay must...
    quarantine conflicting duplicates... The policy does not invent exchange 
    guarantees about duplicate semantics that were not documented."
    
    Implementation: If a meaningful source_id (trade_id or id field from CSV)
    appears on multiple records with different timestamps, prices, or amounts,
    the records conflict and the window must be rejected.
    """
    trades = tmp_path / "trades.csv"
    _write_csv(trades, [
        "timestamp,market,price,amount,trade_id",
        "2020-01-01T00:00:00Z,BTC-EUR,100.0,1.0,t1",
        "2020-01-01T00:00:30Z,BTC-EUR,100.0,1.0,t1",  # same trade_id, different timestamp
        "2020-01-01T00:05:00Z,BTC-EUR,102.0,0.8,t2",
    ])

    with pytest.raises(HSRAError) as ei:
        build_ohlcv_window(
            trades,
            requested_start=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc),
            requested_end=datetime(2020, 1, 1, 0, 10, tzinfo=timezone.utc),
        )

    info = json.loads(str(ei.value))
    assert info["reason"] == "conflicting_duplicate_source_id"


def test_rejects_repeated_source_id_different_price(tmp_path):
    """Reject if the same trade_id appears with different prices.
    
    Policy basis: Same as above. Conflicting duplicates must be rejected.
    """
    trades = tmp_path / "trades.csv"
    _write_csv(trades, [
        "timestamp,market,price,amount,trade_id",
        "2020-01-01T00:00:00Z,BTC-EUR,100.0,1.0,t1",
        "2020-01-01T00:00:00Z,BTC-EUR,101.0,1.0,t1",  # same trade_id, same timestamp, different price
        "2020-01-01T00:05:00Z,BTC-EUR,102.0,0.8,t2",
    ])

    with pytest.raises(HSRAError) as ei:
        build_ohlcv_window(
            trades,
            requested_start=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc),
            requested_end=datetime(2020, 1, 1, 0, 10, tzinfo=timezone.utc),
        )

    info = json.loads(str(ei.value))
    assert info["reason"] == "conflicting_duplicate_source_id"


def test_fallback_id_collision_not_treated_as_duplicate_proof(tmp_path):
    """Fallback IDs (filename:offset) are file-scoped and collisions don't prove duplicates.
    
    Policy basis (approved duplicate policy): "Distinguish meaningful source 
    identifiers from fallback identifiers such as filename:offset. Do not treat 
    fallback-ID collisions alone as proof of duplicate economic events."
    
    Implementation: When trade_id or id fields are missing from CSV, the builder
    falls back to filename:offset. Two trades with no meaningful ID but similar
    offset (if they existed in different files) would create fallback ID collision.
    However, the builder only rejects if the collision has been proven to be on
    a meaningful ID that conflicts. Fallback collisions are NOT checked.
    
    This test verifies that the builder accepts two trades where one or both lack
    a meaningful ID, because fallback IDs are not treated as proof of duplicates.
    """
    trades = tmp_path / "trades.csv"
    # Note: Can't easily create fallback ID in test (would need multiple files
    # with same name), so test by verifying trades without trade_id are accepted.
    # If both were treated as duplicates by fallback ID, they'd be rejected.
    _write_csv(trades, [
        "timestamp,market,price,amount",  # NO trade_id field
        "2020-01-01T00:00:00Z,BTC-EUR,100.0,1.0",
        "2020-01-01T00:02:00Z,BTC-EUR,102.0,0.5",
        "2020-01-01T00:05:00Z,BTC-EUR,103.0,0.8",
    ])

    # Should accept because fallback IDs are not checked for duplicates
    candles = build_ohlcv_window(
        trades,
        requested_start=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc),
        requested_end=datetime(2020, 1, 1, 0, 10, tzinfo=timezone.utc),
    )
    
    assert len(candles) == 2
    assert candles[0].trade_count == 2
    assert candles[1].trade_count == 1


def test_completed_candle_eligibility_requires_external_validation(tmp_path):
    """Document the completed-candle limitation: the builder cannot independently 
    establish that a candle is "completed" without external metadata.
    
    Policy basis (STRATEGY_SPECIFICATION L98-99, S3D-006): 
    "only completed and valid candles are eligible for entry evaluation. 
    The most recent candle is treated as incomplete until the source confirms 
    the interval is closed; no entry signal may depend on the current still-forming bar."
    
    Known limitation: The builder accepts a requested_end parameter that defines when
    to stop including trades, but this parameter alone does NOT prove that:
    1. The source's trade feed was complete until requested_end
    2. The interval [requested_end - interval, requested_end) has no future trades
    3. The system clock or data collection actually paused at requested_end
    
    The builder does NOT add metadata to candles to distinguish:
    - Completed vs. incomplete intervals
    - Historical verified data vs. real-time still-forming data
    - Whether requested_end was a source-confirmed boundary
    
    This is an unresolved gap: the builder is a pure calculation engine. Determining
    completed-candle eligibility requires either:
    A) Explicit metadata from the source (e.g., window_analysis.py confirms coverage)
    B) External time-series logic confirming requested_end is in the past and stable
    C) An API change to the builder to accept and return completion flags
    
    For now, the caller is responsible for ensuring requested_end represents an
    actual source-coverage boundary. The builder itself cannot verify this.
    """
    trades = tmp_path / "trades.csv"
    _write_csv(trades, [
        "timestamp,market,price,amount,trade_id",
        "2020-01-01T00:00:00Z,BTC-EUR,100.0,1.0,t1",
        "2020-01-01T00:02:00Z,BTC-EUR,102.0,0.5,t2",
        "2020-01-01T00:05:00Z,BTC-EUR,103.0,0.8,t3",
        "2020-01-01T00:07:00Z,BTC-EUR,104.0,0.6,t4",
    ])

    # Build candles with requested_end at 00:10
    candles = build_ohlcv_window(
        trades,
        requested_start=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc),
        requested_end=datetime(2020, 1, 1, 0, 10, tzinfo=timezone.utc),
    )

    # The builder returns candles, but does NOT annotate whether the final candle
    # [00:05, 00:10) is "completed". The builder has no way to know:
    # - Is 00:10 in the past or the future?
    # - Did the source confirm no more trades until 00:10?
    # - Will a future fetch return trades between 00:07 and 00:10?
    
    # Verify that candles are returned (builder's job is fulfilled)
    assert len(candles) == 2
    assert candles[1].interval_start.isoformat() == "2020-01-01T00:05:00+00:00"
    assert candles[1].interval_end.isoformat() == "2020-01-01T00:10:00+00:00"
    
    # Verify that the builder does NOT have a "completed" flag or metadata
    # (proving that completion eligibility is unresolved)
    assert not hasattr(candles[1], "completed")
    assert not hasattr(candles[1], "is_complete")
    assert not hasattr(candles[1], "validation_status")
    
    # Note: The caller must obtain completion confirmation from:
    # - window_analysis.py (which validates coverage)
    # - Source metadata (e.g., Tardis data with known completeness guarantees)
    # - External time-series logic (e.g., "is requested_end > now() - buffer?")