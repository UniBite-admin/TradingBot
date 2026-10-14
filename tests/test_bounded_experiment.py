from __future__ import annotations

from tools.hsra.bounded_experiment import run_manifest_experiment


def test_manifest_experiment_runs_on_default_kraken_sample(tmp_path):
    report = run_manifest_experiment(output_dir=tmp_path / "results")

    assert report["execution_status"] == "PARTIALLY_WORKING"
    assert report["manifest_status"] == "PROVISIONAL_KRAKEN_OHLCV_RESEARCH_ONLY"
    assert report["eligible_observation_count"] == 1284979
    assert report["signal_observation_count"] == 613360
    assert report["signal_positive_count"] == 289553
    assert report["baseline_positive_count"] == 622562
    assert report["signal_positive_rate"] == 0.47207675753228123
    assert report["baseline_positive_rate"] == 0.4844919644601196
    assert report["utc_boundary_status"]["status"] == "UNVERIFIED"


def test_manifest_experiment_marks_kraken_utc_boundary_limitation_explicitly(tmp_path):
    report = run_manifest_experiment(output_dir=tmp_path / "results")

    assert "UTC" in report["utc_boundary_status"]["reason"]
    assert "explicit Kraken BTC/EUR 5-minute OHLCV source only" in report["sample_rule"]
    assert "bounded descriptive observations" in report["utc_boundary_status"]["reason"]


def test_manifest_experiment_rejects_missing_manifest_cleanly(tmp_path):
    report = run_manifest_experiment(manifest_path="does-not-exist.json", output_dir=tmp_path / "results")

    assert report["execution_status"] == "BLOCKED"
    assert report["status_detail"] == "manifest_missing"
