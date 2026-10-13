from __future__ import annotations

from tools.hsra.bounded_experiment import run_manifest_experiment


def test_manifest_experiment_runs_on_bounded_sample(tmp_path):
    report = run_manifest_experiment(output_dir=tmp_path / "results")

    assert report["execution_status"] == "PARTIALLY_WORKING"
    assert report["manifest_status"] == "PROVISIONAL_BOUND_RESEARCH_ONLY"
    assert report["eligible_observation_count"] == 204
    assert report["signal_observation_count"] == 31
    assert report["signal_positive_count"] == 11
    assert report["baseline_positive_count"] == 82
    assert report["signal_positive_rate"] == 0.3548387096774194
    assert report["baseline_positive_rate"] == 0.4019607843137255
    assert report["utc_boundary_status"]["status"] == "UNVERIFIED"


def test_manifest_experiment_marks_utc_boundary_limitation_explicitly(tmp_path):
    report = run_manifest_experiment(output_dir=tmp_path / "results")

    assert "UTC" in report["utc_boundary_status"]["reason"]
    assert "first calendar day of each month" in report["sample_rule"]
    assert "bounded descriptive observations" in report["utc_boundary_status"]["reason"]


def test_manifest_experiment_rejects_missing_manifest_cleanly(tmp_path):
    report = run_manifest_experiment(manifest_path="does-not-exist.json", output_dir=tmp_path / "results")

    assert report["execution_status"] == "BLOCKED"
    assert report["status_detail"] == "manifest_missing"
