from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from tools.hsra.bounded_experiment import run_manifest_experiment
from tools.hsra.kraken_ohlcv import extract_contiguous_kraken_windows, load_kraken_ohlcv
from tools.hsra.merger import HSRAError
from tools.hsra.second_strategy_experiment import _signal_observations_for_window, run_second_strategy_experiment


def _write_kraken_csv(path: Path, rows: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        for row in rows:
            fh.write(row + "\n")


def test_kraken_ohlcv_parses_valid_schema_and_utc_timestamps(tmp_path):
    path = tmp_path / "XBTEUR_5.csv"
    _write_kraken_csv(path, [
        "1704067200,97.0,97.0,97.0,97.0,1.0,1",
        "1704067500,99.9,99.9,99.9,99.9,0.2,2",
        "1704067800,98.2,98.2,98.2,98.2,0.1,1",
    ])

    candles = load_kraken_ohlcv(path)

    assert [c.interval_start.isoformat() for c in candles] == [
        "2024-01-01T00:00:00+00:00",
        "2024-01-01T00:05:00+00:00",
        "2024-01-01T00:10:00+00:00",
    ]
    assert candles[0].open == 97.0
    assert candles[1].close == 99.9
    assert candles[2].high == 98.2


def test_kraken_ohlcv_rejects_duplicate_timestamp(tmp_path):
    path = tmp_path / "XBTEUR_5.csv"
    _write_kraken_csv(path, [
        "1704067200,97.0,97.0,97.0,97.0,1.0,1",
        "1704067200,99.0,100.0,96.0,98.0,1.1,2",
    ])

    with pytest.raises(HSRAError) as exc:
        load_kraken_ohlcv(path)

    assert json.loads(str(exc.value))["reason"] == "duplicate_kraken_timestamp"


def test_kraken_ohlcv_rejects_invalid_ohlcv_relationship(tmp_path):
    path = tmp_path / "XBTEUR_5.csv"
    _write_kraken_csv(path, [
        "1704067200,97.0,98.0,100.0,99.0,1.0,1",
    ])

    with pytest.raises(HSRAError) as exc:
        load_kraken_ohlcv(path)

    assert json.loads(str(exc.value))["reason"] == "invalid_ohlcv_relationship"


def test_kraken_ohlcv_keeps_sparse_gaps_and_excludes_incomplete_final_candle(tmp_path):
    path = tmp_path / "XBTEUR_5.csv"
    _write_kraken_csv(path, [
        "1704067200,97.0,97.0,97.0,97.0,1.0,1",
        "1704067500,99.9,99.9,99.9,99.9,0.2,2",
        "1704067800,98.2,98.2,98.2,98.2,0.1,1",
        "1704068400,96.91,96.91,96.9,96.9,1.0,2",
        "1704068700,96.8,96.8,96.8,96.8,0.25,1",
        "1704069000,96.7,96.7,96.7,96.7,0.4,1",
    ])

    candles = load_kraken_ohlcv(path)
    windows = extract_contiguous_kraken_windows(candles)

    assert len(windows) == 2
    assert [len(window) for window in windows] == [3, 3]
    assert windows[0][0].interval_start == datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)
    assert windows[1][0].interval_start == datetime(2024, 1, 1, 0, 20, tzinfo=timezone.utc)


def test_manifest_experiment_uses_kraken_loader_for_kraken_ohlcv_manifest(tmp_path):
    csv_path = tmp_path / "XBTEUR_5.csv"
    _write_kraken_csv(csv_path, [
        "1704067200,100.0,101.0,99.0,100.0,1.0,1",
        "1704067500,100.0,102.0,98.5,101.5,1.1,1",
        "1704067800,101.5,103.0,100.0,102.0,1.2,1",
        "1704068100,102.0,102.5,101.0,101.2,1.0,1",
        "1704068400,101.2,101.5,100.0,100.5,0.9,1",
        "1704068700,100.5,101.0,99.8,100.8,0.8,1",
    ])

    manifest = {
        "dataset_name": "kraken_btc_eur_5m_ohlcv",
        "source": "Kraken public OHLC export",
        "market": "BTC-EUR",
        "status": "PROVISIONAL_KRAKEN_OHLCV_RESEARCH_ONLY",
        "scope": {"sample_rule": "explicit Kraken BTC/EUR 5-minute OHLCV source only"},
        "files": [{"file": {"path": str(csv_path).replace("\\", "/")}}],
    }
    manifest_path = tmp_path / "kraken_manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    report = run_manifest_experiment(manifest_path=manifest_path, output_dir=tmp_path / "results")

    assert report["execution_status"] == "PARTIALLY_WORKING"
    assert report["manifest_status"] == "PROVISIONAL_KRAKEN_OHLCV_RESEARCH_ONLY"
    assert report["eligible_observation_count"] > 0


def test_second_strategy_experiment_default_kraken_manifest_stays_kraken_only(tmp_path):
    report = run_second_strategy_experiment(output_dir=tmp_path / "results")
    assert report["manifest_status"] == "PROVISIONAL_KRAKEN_OHLCV_RESEARCH_ONLY"
    assert report["source_kind"] == "kraken"


def test_second_strategy_experiment_kraken_manifest_is_explicitly_isolated(tmp_path):
    csv_path = tmp_path / "kraken.csv"
    _write_kraken_csv(csv_path, [
        "1704067200,97.0,97.0,97.0,97.0,1.0,1",
        "1704067500,99.9,99.9,99.9,99.9,0.2,2",
        "1704067800,98.2,98.2,98.2,98.2,0.1,1",
        "1704068100,96.91,96.91,96.9,96.9,1.0,2",
        "1704068400,96.8,96.8,96.8,96.8,0.25,1",
        "1704068700,97.1,97.1,97.1,97.1,0.5,1",
        "1704069000,97.2,97.2,97.2,97.2,0.3,1",
    ])

    manifest = {
        "dataset_name": "kraken_test",
        "status": "PROVISIONAL_KRAKEN_OHLCV_RESEARCH_ONLY",
        "source": "kraken",
        "market": "BTC-EUR",
        "scope": {"sample_rule": "explicit Kraken BTC/EUR 5-minute OHLCV source only"},
        "files": [{"file": {"path": str(csv_path).replace("\\", "/")}}],
    }
    manifest_path = tmp_path / "kraken_manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    report = run_second_strategy_experiment(manifest_path=manifest_path, output_dir=tmp_path / "kraken_results", source_kind="kraken")
    assert report["source_kind"] == "kraken"
    assert report["manifest_status"] == "PROVISIONAL_KRAKEN_OHLCV_RESEARCH_ONLY"


def _legacy_signal_observations_for_window(candles, *, lookback: int, hold_period: int):
    ordered = sorted(candles, key=lambda candle: candle.interval_start)
    if len(ordered) < lookback + 2:
        return []

    observations = []
    for setup_index in range(lookback, len(ordered) - 1):
        setup = ordered[setup_index]
        confirmation = ordered[setup_index + 1]
        context = ordered[setup_index - lookback:setup_index]
        if len(context) < lookback:
            continue

        ordered_copy = sorted(ordered, key=lambda candle: candle.interval_start)
        for previous, current in zip(ordered_copy, ordered_copy[1:]):
            if current.interval_start != previous.interval_start + timedelta(minutes=5):
                break
        else:
            prior_low = min(candle.low for candle in context)
            lower_wick = min(setup.open, setup.close) - setup.low
            body = abs(setup.close - setup.open)
            candle_range = setup.high - setup.low
            prev_close_low = context[-1].low

            local_rule_matches = (
                setup.low < prior_low and
                setup.close > prev_close_low and
                lower_wick > body and
                candle_range > 0 and
                confirmation.close > setup.high
            )

            entry_reference_index = setup_index + 2
            if entry_reference_index >= len(ordered):
                continue
            entry_open = ordered[entry_reference_index].open
            exit_index = entry_reference_index + hold_period - 1
            if exit_index >= len(ordered) or entry_open == 0:
                continue
            forward_return = (ordered[exit_index].close - entry_open) / entry_open

            observations.append({
                "setup_index": setup_index,
                "confirmation_index": setup_index + 1,
                "entry_reference_index": entry_reference_index,
                "signal": 1 if local_rule_matches else 0,
                "forward_return": forward_return,
                "label": 1 if forward_return > 0 else 0,
                "entry_open": entry_open,
                "exit_close": ordered[exit_index].close,
                "signal_timestamp": confirmation.interval_end.isoformat(),
            })

    return observations


def test_kraken_signal_observations_are_equivalent_across_sparse_and_boundary_cases(tmp_path):
    csv_path = tmp_path / "equivalence.csv"
    _write_kraken_csv(csv_path, [
        "1704067200,97.0,97.0,97.0,97.0,1.0,1",
        "1704067500,99.9,99.9,99.9,99.9,0.2,2",
        "1704067800,98.2,98.2,98.2,98.2,0.1,1",
        "1704068400,96.91,96.91,96.9,96.9,1.0,2",
        "1704068700,96.8,96.8,96.8,96.8,0.25,1",
        "1704069000,97.1,97.1,97.1,97.1,0.5,1",
        "1704069300,97.2,97.2,97.2,97.2,0.3,1",
    ])

    candles = load_kraken_ohlcv(csv_path)
    windows = extract_contiguous_kraken_windows(candles)
    for window in windows:
        expected = _legacy_signal_observations_for_window(window, lookback=12, hold_period=3)
        actual = _signal_observations_for_window(window, lookback=12, hold_period=3)
        assert actual == expected


def test_kraken_signal_observations_are_exactly_equivalent_on_real_windows_and_boundaries(tmp_path):
    real_path = Path("data/kraken/XBTEUR_5.csv")
    if real_path.exists():
        real_candles = load_kraken_ohlcv(real_path)
        real_windows = [window for window in extract_contiguous_kraken_windows(real_candles) if len(window) >= 17][:10]
        for window in real_windows:
            expected = _legacy_signal_observations_for_window(window, lookback=12, hold_period=3)
            actual = _signal_observations_for_window(window, lookback=12, hold_period=3)
            assert actual == expected

    sparse_path = tmp_path / "legacy_equivalence_sparse.csv"
    sparse_case = [
        "1704067200,97.0,97.0,97.0,97.0,1.0,1",
        "1704067500,99.9,99.9,99.9,99.9,0.2,2",
        "1704067800,98.2,98.2,98.2,98.2,0.1,1",
        "1704068400,96.91,96.91,96.9,96.9,1.0,2",
        "1704068700,96.8,96.8,96.8,96.8,0.25,1",
        "1704069000,97.1,97.1,97.1,97.1,0.5,1",
        "1704069300,97.2,97.2,97.2,97.2,0.3,1",
    ]
    _write_kraken_csv(sparse_path, sparse_case)
    sparse_candles = load_kraken_ohlcv(sparse_path)
    for window in extract_contiguous_kraken_windows(sparse_candles):
        expected = _legacy_signal_observations_for_window(window, lookback=12, hold_period=3)
        actual = _signal_observations_for_window(window, lookback=12, hold_period=3)
        assert actual == expected

    boundary_path = tmp_path / "legacy_equivalence_boundary.csv"
    boundary_case = [
        f"{1704067200 + 300 * i},{97.0 + i},{97.5 + i},{96.5 + i},{97.2 + i},{1.0 + i * 0.01},{i + 1}"
        for i in range(14)
    ]
    _write_kraken_csv(boundary_path, boundary_case)
    boundary_candles = load_kraken_ohlcv(boundary_path)
    for window in extract_contiguous_kraken_windows(boundary_candles):
        expected = _legacy_signal_observations_for_window(window, lookback=12, hold_period=3)
        actual = _signal_observations_for_window(window, lookback=12, hold_period=3)
        assert actual == expected


def test_kraken_run_uses_single_file_load_for_each_manifest_file(monkeypatch, tmp_path):
    csv_path = tmp_path / "kraken.csv"
    _write_kraken_csv(csv_path, [
        "1704067200,97.0,97.0,97.0,97.0,1.0,1",
        "1704067500,99.9,99.9,99.9,99.9,0.2,2",
        "1704067800,98.2,98.2,98.2,98.2,0.1,1",
        "1704068100,96.91,96.91,96.9,96.9,1.0,2",
        "1704068400,96.8,96.8,96.8,96.8,0.25,1",
        "1704068700,97.1,97.1,97.1,97.1,0.5,1",
        "1704069000,97.2,97.2,97.2,97.2,0.3,1",
    ])

    manifest = {
        "dataset_name": "kraken_test",
        "status": "PROVISIONAL_KRAKEN_OHLCV_RESEARCH_ONLY",
        "source": "kraken",
        "market": "BTC-EUR",
        "scope": {"sample_rule": "explicit Kraken BTC/EUR 5-minute OHLCV source only"},
        "files": [{"file": {"path": str(csv_path).replace("\\", "/")}}],
    }
    manifest_path = tmp_path / "kraken_manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    real_load = load_kraken_ohlcv
    real_extract = extract_contiguous_kraken_windows
    load_calls = []

    def spy_load(path):
        load_calls.append(path)
        return real_load(path)

    def spy_extract(candles):
        return real_extract(candles)

    monkeypatch.setattr("tools.hsra.second_strategy_experiment.load_kraken_ohlcv", spy_load)
    monkeypatch.setattr("tools.hsra.second_strategy_experiment.extract_contiguous_kraken_windows", spy_extract)

    report = run_second_strategy_experiment(manifest_path=manifest_path, output_dir=tmp_path / "kraken_results", source_kind="kraken")

    assert len(load_calls) == 1
    assert report["source_kind"] == "kraken"
