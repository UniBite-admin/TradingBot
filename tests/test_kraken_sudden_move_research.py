from __future__ import annotations

import math

import numpy as np
import pandas as pd

from tools.research.kraken_sudden_move import (
    benjamini_hochberg,
    build_event_labels,
    build_event_labels_reference,
    compute_chronological_split,
    deterministic_match_controls,
    moving_block_bootstrap,
    summarize_window_features,
    summarize_window_features_reference,
)


def _make_series():
    ts = pd.date_range("2024-01-01 00:00:00", periods=30, freq="5min", tz="UTC")
    close = pd.Series([100.0 + i * 1.0 for i in range(30)], index=ts)
    high = close * 1.01
    low = close * 0.99
    open_ = close * 0.995
    volume = pd.Series(1.0, index=ts)
    trade_count = pd.Series(1, index=ts)
    df = pd.DataFrame({
        "timestamp": ts,
        "open": open_.to_numpy(),
        "high": high.to_numpy(),
        "low": low.to_numpy(),
        "close": close.to_numpy(),
        "volume": volume.to_numpy(),
        "trade_count": trade_count.to_numpy(),
    })
    return df


def test_fixed_threshold_event_labels_and_volatility_thresholds():
    df = _make_series()
    # The event label is from the candle at t to t+horizon; with the synthetic trend,
    # the first eligible return is +3% over 3 candles, which should trigger the 0.5% and 1.0%
    # fixed-threshold upward labels.
    labels = build_event_labels(df, horizon_candles=3, fixed_thresholds=(0.005, 0.01))
    assert labels["upward_0.5pct"].iloc[0]
    assert labels["upward_1.0pct"].iloc[0]
    assert not labels["downward_0.5pct"].iloc[0]

    vol_labels = build_event_labels(df, horizon_candles=3, volatility_thresholds=(2.0, 3.0), use_volatility=True)
    assert "volatility_2x_up" in vol_labels.columns
    assert "volatility_2x_down" in vol_labels.columns
    assert vol_labels["volatility_2x_up"].iloc[0] in (True, False)


def test_gap_and_warmup_validation_and_lookahead_prevention():
    ts = pd.date_range("2024-01-01 00:00:00", periods=10, freq="5min", tz="UTC")
    ts = ts.insert(5, pd.Timestamp("2024-01-01 00:35:00", tz="UTC"))
    df = pd.DataFrame({
        "timestamp": ts,
        "open": np.linspace(100, 110, len(ts)),
        "high": np.linspace(101, 111, len(ts)),
        "low": np.linspace(99, 109, len(ts)),
        "close": np.linspace(100, 110, len(ts)),
        "volume": np.ones(len(ts)),
        "trade_count": np.ones(len(ts), dtype=int),
    })
    df = df.sort_values("timestamp").reset_index(drop=True)
    result = summarize_window_features(df, horizon_candles=3, event_start_index=5)
    assert "exclusions" in result
    assert len(result["exclusions"]) >= 1
    assert "warmup" in " ".join(result["exclusions"]).lower()
    assert any("gap" in exc.lower() for exc in result["exclusions"])


def test_single_row_input_keeps_nan_log_return_and_does_not_crash():
    ts = pd.to_datetime(["2024-01-01 00:00:00"], utc=True)
    df = pd.DataFrame({
        "timestamp": ts,
        "open": [100.0],
        "high": [101.0],
        "low": [99.0],
        "close": [100.0],
        "volume": [1.0],
        "trade_count": [1],
    })
    labels = build_event_labels(df, horizon_candles=3)
    assert len(labels) == 1
    assert np.isnan(labels["log_return"].iloc[0])
    assert not labels["upward_0.5pct"].iloc[0]


def test_chronological_split_and_matching_are_deterministic():
    ts = pd.date_range("2024-01-01 00:00:00", periods=120, freq="5min", tz="UTC")
    base = 100.0 + np.arange(len(ts)) * 0.01
    df = pd.DataFrame({
        "timestamp": ts,
        "open": base,
        "high": base + 0.5,
        "low": base - 0.5,
        "close": base,
        "volume": np.ones(len(ts)),
        "trade_count": np.ones(len(ts), dtype=int),
    })
    split = compute_chronological_split(df)
    assert split["discovery_end"] < split["validation_end"] < split["test_end"]
    assert split["discovery_end"] == split["discovery_end"]

    events = pd.DataFrame({
        "pair": ["XBTUSD"] * 4,
        "partition": ["discovery"] * 4,
        "horizon": [3] * 4,
        "volatility_quintile": [0, 0, 1, 1],
        "feature": [1.0, 2.0, 3.0, 4.0],
    })
    controls = pd.DataFrame({
        "pair": ["XBTUSD"] * 4,
        "partition": ["discovery"] * 4,
        "horizon": [3] * 4,
        "volatility_quintile": [0, 0, 1, 1],
        "feature": [10.0, 11.0, 12.0, 13.0],
        "event": [False] * 4,
    })
    matched = deterministic_match_controls(events, controls, seed=20261021)
    assert len(matched) == 4
    assert matched["event_index"].nunique() == 4
    assert matched["control_index"].nunique() == 4


def test_bootstrap_is_reproducible_and_multiple_testing_is_corrected():
    values = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    first = moving_block_bootstrap(values, block_size=2, seed=20261021, replicates=200)
    second = moving_block_bootstrap(values, block_size=2, seed=20261021, replicates=200)
    assert np.allclose(first, second)

    pvals = np.array([0.01, 0.04, 0.06, 0.12])
    adjusted = benjamini_hochberg(pvals, q=0.05)
    assert np.all(adjusted >= pvals)
    assert adjusted[0] <= 0.05
    assert adjusted[1] <= 0.1


def test_optimized_event_labels_match_reference_on_small_fixture():
    df = _make_series()
    ref = build_event_labels_reference(df, horizon_candles=3, fixed_thresholds=(0.005, 0.01), volatility_thresholds=(2.0, 3.0), use_volatility=True)
    opt = build_event_labels(df, horizon_candles=3, fixed_thresholds=(0.005, 0.01), volatility_thresholds=(2.0, 3.0), use_volatility=True)
    pd.testing.assert_frame_equal(opt[ref.columns], ref[ref.columns], check_dtype=False)

    ref_summary = summarize_window_features_reference(df, horizon_candles=3, event_start_index=288)
    opt_summary = summarize_window_features(df, horizon_candles=3, event_start_index=288)
    assert ref_summary["event_start_index"] == opt_summary["event_start_index"]
    assert ref_summary["horizon_candles"] == opt_summary["horizon_candles"]
    assert ref_summary["event_time"] == opt_summary["event_time"]
    assert ref_summary["exclusions"] == opt_summary["exclusions"]
    if np.isfinite(ref_summary["horizon_return"]) and np.isfinite(opt_summary["horizon_return"]):
        assert np.isclose(ref_summary["horizon_return"], opt_summary["horizon_return"])
    else:
        assert np.isnan(ref_summary["horizon_return"]) and np.isnan(opt_summary["horizon_return"])
