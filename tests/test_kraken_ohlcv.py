from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from tools.hsra.kraken_ohlcv import extract_contiguous_kraken_windows, load_kraken_ohlcv
from tools.hsra.merger import HSRAError
from tools.hsra.second_strategy_experiment import run_second_strategy_experiment


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


def test_second_strategy_experiment_default_tardis_manifest_stays_unchanged(tmp_path):
    report = run_second_strategy_experiment(output_dir=tmp_path / "results")
    assert report["manifest_status"] == "PROVISIONAL_BOUND_RESEARCH_ONLY"
    assert report["source_kind"] == "tardis"


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
