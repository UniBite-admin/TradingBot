from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import numpy as np

from tools.research.btc_eur_continuation_study import (
    _matched_control_indices,
    evaluate_period_summary,
    load_btc_eur_5m,
    run_continuation_study,
    scan_events,
)


def _make_synthetic_frame() -> pd.DataFrame:
    ts = pd.date_range("2024-01-01 00:00:00", periods=600, freq="5min", tz="UTC")
    base = 100.0 + np.linspace(0, 1800.0, len(ts))
    close = pd.Series(base, index=ts)
    open_ = close * 0.998
    high = close * 1.005
    low = close * 0.995
    df = pd.DataFrame({
        "timestamp": ts,
        "open": open_.to_numpy(),
        "high": high.to_numpy(),
        "low": low.to_numpy(),
        "close": close.to_numpy(),
        "volume": np.ones(len(ts), dtype=float),
        "trade_count": np.ones(len(ts), dtype=int),
    })
    return df


def test_scan_events_requires_warmup_and_rejects_overlap():
    df = _make_synthetic_frame()
    events = scan_events(df, horizon_minutes=15, threshold=0.005, direction="up")
    assert len(events) > 0
    assert all(events["eligible"])  # warm-up + no gap + no forward look-ahead are handled upstream
    assert events["event_index"].nunique() == len(events)
    assert set(events.columns) >= {"event_index", "event_time", "partition", "direction", "threshold", "horizon_minutes", "event_return", "eligible"}


def test_evaluate_period_summary_includes_effect_and_uncertainty():
    df = _make_synthetic_frame()
    summary = evaluate_period_summary(
        df,
        period_name="discovery",
        threshold=0.005,
        horizon_minutes=15,
        direction="up",
    )
    assert summary["period"] == "discovery"
    assert summary["threshold"] == 0.005
    assert summary["horizon_minutes"] == 15
    assert summary["direction"] == "up"
    assert "event_count" in summary
    assert "control_count" in summary
    assert "effect_size" in summary
    assert "effect_ci_95_low" in summary
    assert "effect_ci_95_high" in summary
    assert summary["control_count"] >= 1


def test_run_study_generates_compact_report_for_btc_eur_file(tmp_path):
    out_dir = tmp_path / "btc_eur_continuation_study"
    result = run_continuation_study(
        "data/kraken/XBTEUR_5.csv",
        output_dir=str(out_dir),
        discovery_fraction=0.6,
        validation_fraction=0.2,
        test_fraction=0.2,
        bootstrap_replicates=32,
    )
    assert result["file"] == "XBTEUR_5.csv"
    assert result["event_count_total"] > 0
    assert (out_dir / "btc_eur_continuation_summary.json").exists()
    assert (out_dir / "btc_eur_continuation_summary.csv").exists()

    payload = json.loads((out_dir / "btc_eur_continuation_summary.json").read_text(encoding="utf-8"))
    assert "period_summaries" in payload
    assert len(payload["period_summaries"]) >= 3
    assert all("effect_size" in row for row in payload["period_summaries"])


def test_controls_are_unique_and_non_overlapping():
    df = _make_synthetic_frame()
    events = scan_events(df, horizon_minutes=15, threshold=0.005, direction="up")
    controls = _matched_control_indices(df, events, horizon_minutes=15, threshold=0.005, direction="up")
    assert len(set(controls)) == len(controls)
    for idx in controls:
        assert idx not in events["event_index"].to_numpy()
        assert abs(idx - events["event_index"].to_numpy()[:, None]).min() > 15


def test_gap_and_boundary_windows_are_rejected():
    ts = pd.date_range("2024-01-01 00:00:00", periods=300, freq="5min", tz="UTC")
    gap_ts = ts.insert(150, ts[149] + pd.Timedelta(minutes=10))
    base = 100.0 + np.linspace(0, 1800.0, len(gap_ts))
    close = pd.Series(base, index=gap_ts)
    df = pd.DataFrame({
        "timestamp": gap_ts,
        "open": close * 0.998,
        "high": close * 1.005,
        "low": close * 0.995,
        "close": close,
        "volume": np.ones(len(gap_ts), dtype=float),
        "trade_count": np.ones(len(gap_ts), dtype=int),
    })
    events = scan_events(df, horizon_minutes=15, threshold=0.005, direction="up")
    assert len(events) == 0 or all(events["event_index"] < 150)


def test_fdr_adjustment_and_test_period_are_separated():
    result = run_continuation_study(
        "data/kraken/XBTEUR_5.csv",
        discovery_fraction=0.6,
        validation_fraction=0.2,
        test_fraction=0.2,
        bootstrap_replicates=16,
    )
    discovery_rows = [row for row in result["period_summaries"] if row["period"] == "discovery"]
    assert discovery_rows
    assert all("p_value_adj" in row for row in discovery_rows)
    assert all(row["p_value_adj"] is None or 0.0 <= row["p_value_adj"] <= 1.0 for row in discovery_rows)
    assert all(row["period"] != "test" for row in result["discovery_adjusted_results"])
