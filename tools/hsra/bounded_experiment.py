from __future__ import annotations

import argparse
import json
from datetime import timedelta
from pathlib import Path
from statistics import mean, median

from .merger import HSRAError
from .ohlcv import _bucket_start, build_ohlcv_window
from .reader import iter_trades

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST_PATH = ROOT / "data" / "provenance" / "tardis_btc_eur_first_of_month_manifest.json"
DEFAULT_OUTPUT_DIR = ROOT / "data" / "experiments"


def _manifest_path(path: str | Path | None) -> Path:
    if path is None:
        return DEFAULT_MANIFEST_PATH
    return Path(path)


def _load_manifest(manifest_path: Path) -> dict:
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")
    with manifest_path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _normalize_relative_path(raw: str) -> Path:
    return Path(raw.replace("\\", "/"))


def _extract_valid_run_windows(trade_path: Path) -> list[dict]:
    bucket_starts = sorted({
        _bucket_start(ts, 5)
        for ts in (trade.ts for trade in iter_trades(trade_path) if trade.ts is not None)
    })
    if not bucket_starts:
        return []

    runs: list[list] = []
    current = [bucket_starts[0]]
    for bucket_start in bucket_starts[1:]:
        if bucket_start == current[-1] + timedelta(minutes=5):
            current.append(bucket_start)
        else:
            runs.append(current)
            current = [bucket_start]
    runs.append(current)

    valid_runs: list[dict] = []
    for run in runs:
        if len(run) < 2:
            continue
        requested_start = run[0]
        requested_end = run[-1] + timedelta(minutes=5)
        try:
            candles = build_ohlcv_window(
                trade_path,
                requested_start=requested_start,
                requested_end=requested_end,
                interval_minutes=5,
            )
        except HSRAError:
            continue
        if len(candles) == len(run):
            valid_runs.append({
                "run_start": requested_start.isoformat(),
                "run_end": requested_end.isoformat(),
                "candle_count": len(candles),
                "candle_starts": [c.interval_start.isoformat() for c in candles],
            })
    return valid_runs


def _build_signal_metrics(candles: list) -> dict:
    eligible: list[dict] = []
    for idx in range(len(candles) - 1):
        source = candles[idx]
        target = candles[idx + 1]
        if source.close == 0:
            continue
        signal = 1 if source.close > source.open else 0
        next_return = (target.close - source.close) / source.close
        label = 1 if next_return > 0 else 0
        eligible.append({
            "source_candle_start": source.interval_start.isoformat(),
            "target_candle_start": target.interval_start.isoformat(),
            "signal": signal,
            "return": next_return,
            "label": label,
        })

    if not eligible:
        return {
            "eligible_observation_count": 0,
            "signal_observation_count": 0,
            "signal_positive_count": 0,
            "baseline_positive_count": 0,
            "signal_positive_rate": None,
            "baseline_positive_rate": None,
            "difference_pp": None,
            "mean_next_period_return": None,
            "median_next_period_return": None,
            "min_next_period_return": None,
            "max_next_period_return": None,
            "observations": [],
        }

    signal_count = sum(item["signal"] for item in eligible)
    signal_positive_count = sum(1 for item in eligible if item["signal"] == 1 and item["label"] == 1)
    baseline_positive_count = sum(1 for item in eligible if item["label"] == 1)
    returns = [item["return"] for item in eligible]
    signal_rate = (signal_positive_count / signal_count) if signal_count else None
    baseline_rate = (baseline_positive_count / len(eligible)) if eligible else None
    difference_pp = ((signal_rate - baseline_rate) * 100.0) if signal_rate is not None and baseline_rate is not None else None

    return {
        "eligible_observation_count": len(eligible),
        "signal_observation_count": signal_count,
        "signal_positive_count": signal_positive_count,
        "baseline_positive_count": baseline_positive_count,
        "signal_positive_rate": signal_rate,
        "baseline_positive_rate": baseline_rate,
        "difference_pp": difference_pp,
        "mean_next_period_return": mean(returns),
        "median_next_period_return": median(returns),
        "min_next_period_return": min(returns),
        "max_next_period_return": max(returns),
        "observations": eligible,
    }


def run_manifest_experiment(*, manifest_path: str | Path | None = None, output_dir: str | Path | None = None) -> dict:
    manifest_path = _manifest_path(manifest_path)
    output_dir = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR

    try:
        manifest = _load_manifest(manifest_path)
    except FileNotFoundError:
        result = {
            "experiment_name": "bounded_btc_eur_5m_descriptive_signal",
            "execution_status": "BLOCKED",
            "status_detail": "manifest_missing",
            "utc_boundary_status": "UNVERIFIED",
            "reason": f"Manifest was not found at {manifest_path}",
        }
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "btc_eur_bounded_experiment_report.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        return result

    source_files = manifest.get("files", [])
    if not source_files:
        result = {
            "experiment_name": "bounded_btc_eur_5m_descriptive_signal",
            "execution_status": "BLOCKED",
            "status_detail": "manifest_empty",
            "utc_boundary_status": "UNVERIFIED",
            "reason": "Manifest contains no file entries.",
            "manifest_status": manifest.get("status"),
        }
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "btc_eur_bounded_experiment_report.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        return result

    valid_runs: list[dict] = []
    all_observations: list[dict] = []
    rejected_windows: list[dict] = []

    for entry in source_files:
        trade_path = ROOT / _normalize_relative_path(entry["trade_file"]["path"])
        if not trade_path.exists():
            rejected_windows.append({
                "trade_file": str(trade_path),
                "reason": "missing_trade_file",
            })
            continue
        windows = _extract_valid_run_windows(trade_path)
        if not windows:
            rejected_windows.append({
                "trade_file": str(trade_path),
                "reason": "no_valid_contiguous_run_under_research_contract",
            })
            continue
        valid_runs.extend({
            "trade_file": str(trade_path),
            **window,
        } for window in windows)
        for window in windows:
            # Rebuild candle objects for each window to compute metrics over the same valid runs.
            requested_start = window["run_start"]
            requested_end = window["run_end"]
            try:
                candles = build_ohlcv_window(
                    trade_path,
                    requested_start=datetime_from_iso(requested_start),
                    requested_end=datetime_from_iso(requested_end),
                    interval_minutes=5,
                )
            except HSRAError:
                rejected_windows.append({
                    "trade_file": str(trade_path),
                    "run_start": requested_start,
                    "run_end": requested_end,
                    "reason": "window_validation_failed",
                })
                continue
            metric = _build_signal_metrics(candles)
            all_observations.extend(metric["observations"])

    if not all_observations:
        result = {
            "experiment_name": "bounded_btc_eur_5m_descriptive_signal",
            "execution_status": "BLOCKED",
            "status_detail": "no_valid_observations",
            "utc_boundary_status": "UNVERIFIED",
            "reason": "The manifest-listed sample produces no eligible observation windows under the fail-closed research contract.",
            "manifest_status": manifest.get("status"),
            "sample_rule": manifest.get("scope", {}).get("sample_rule"),
            "valid_window_count": len(valid_runs),
            "rejected_windows": rejected_windows[:25],
        }
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "btc_eur_bounded_experiment_report.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        return result

    signal_count = sum(item["signal"] for item in all_observations)
    signal_positive_count = sum(1 for item in all_observations if item["signal"] == 1 and item["label"] == 1)
    baseline_positive_count = sum(1 for item in all_observations if item["label"] == 1)
    baseline_rate = baseline_positive_count / len(all_observations)
    signal_rate = (signal_positive_count / signal_count) if signal_count else None
    difference_pp = ((signal_rate - baseline_rate) * 100.0) if signal_rate is not None else None
    returns = [item["return"] for item in all_observations]

    report = {
        "experiment_name": "bounded_btc_eur_5m_descriptive_signal",
        "execution_status": "PARTIALLY_WORKING",
        "status_detail": "bounded_manifest_sample_processed",
        "manifest_status": manifest.get("status"),
        "sample_rule": manifest.get("scope", {}).get("sample_rule"),
        "allowed_use": manifest.get("scope", {}).get("allowed_use"),
        "utc_boundary_status": {
            "status": "UNVERIFIED",
            "reason": "The sample is limited to the first calendar day of each month and the event timestamps are UTC epoch microseconds; the file names and timestamps do not prove full UTC-day completeness. Valid windows are extracted only from contiguous observed trade buckets, and these are reported as bounded descriptive observations rather than complete UTC-day coverage.",
        },
        "files_processed": len(source_files),
        "valid_window_count": len(valid_runs),
        "eligible_observation_count": len(all_observations),
        "signal_observation_count": signal_count,
        "signal_positive_count": signal_positive_count,
        "baseline_positive_count": baseline_positive_count,
        "signal_positive_rate": signal_rate,
        "baseline_positive_rate": baseline_rate,
        "difference_pp": difference_pp,
        "mean_next_period_return": mean(returns),
        "median_next_period_return": median(returns),
        "min_next_period_return": min(returns),
        "max_next_period_return": max(returns),
        "valid_windows": valid_runs[:20],
        "rejected_windows": rejected_windows[:20],
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "btc_eur_bounded_experiment_report.json"
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return report


def datetime_from_iso(value: str):
    from datetime import datetime
    return datetime.fromisoformat(value)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the bounded BTC-EUR descriptive research experiment over the manifest-listed sample.")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST_PATH), help="Path to the manifest JSON file.")
    parser.add_argument("--outdir", default=str(DEFAULT_OUTPUT_DIR), help="Directory for the generated report.")
    args = parser.parse_args(argv)

    result = run_manifest_experiment(manifest_path=args.manifest, output_dir=args.outdir)
    print(json.dumps({
        "execution_status": result["execution_status"],
        "eligible_observation_count": result.get("eligible_observation_count"),
        "signal_positive_rate": result.get("signal_positive_rate"),
        "baseline_positive_rate": result.get("baseline_positive_rate"),
        "difference_pp": result.get("difference_pp"),
        "output_path": str(Path(args.outdir) / "btc_eur_bounded_experiment_report.json"),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
