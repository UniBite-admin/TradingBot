from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
from statistics import mean, median

from .kraken_ohlcv import extract_contiguous_kraken_windows, load_kraken_ohlcv
from .merger import HSRAError
from .ohlcv import OHLCVCandle, _bucket_start, build_ohlcv_window
from .reader import iter_trades

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST_PATH = ROOT / "data" / "provenance" / "tardis_btc_eur_first_of_month_manifest.json"
DEFAULT_KRAKEN_MANIFEST_PATH = ROOT / "data" / "provenance" / "kraken_btc_eur_5m_manifest.json"
DEFAULT_OUTPUT_DIR = ROOT / "data" / "experiments"
DEFAULT_LOOKBACK = 12
DEFAULT_HOLD_PERIOD = 3


def _manifest_path(path: str | Path | None, *, source_kind: str = "tardis") -> Path:
    if path is not None:
        return Path(path)
    if source_kind == "kraken":
        return DEFAULT_KRAKEN_MANIFEST_PATH
    return DEFAULT_MANIFEST_PATH


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


def _extract_valid_run_windows_for_source(candles_path: Path, *, source_kind: str, candles: list[OHLCVCandle] | None = None) -> list[dict]:
    if source_kind != "kraken":
        return _extract_valid_run_windows(candles_path)

    if candles is None:
        try:
            candles = load_kraken_ohlcv(candles_path)
        except HSRAError:
            return []

    windows: list[dict] = []
    for run in extract_contiguous_kraken_windows(candles):
        if len(run) < 2:
            continue
        windows.append({
            "run_start": run[0].interval_start.isoformat(),
            "run_end": run[-1].interval_end.isoformat(),
            "candle_count": len(run),
            "candle_starts": [c.interval_start.isoformat() for c in run],
        })
    return windows


def _datetime_from_iso(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _is_intervals_contiguous(candles: list[OHLCVCandle]) -> bool:
    ordered = sorted(candles, key=lambda candle: candle.interval_start)
    for previous, current in zip(ordered, ordered[1:]):
        if current.interval_start != previous.interval_start + timedelta(minutes=5):
            return False
    return True


def evaluate_local_rejection_signal(
    candles: list[OHLCVCandle],
    *,
    lookback: int = DEFAULT_LOOKBACK,
    current_bar_start: datetime | None = None,
) -> dict:
    """Evaluate the original local downside sweep + rejection candle + bullish confirmation rule.

    The signal is only considered valid when the setup and confirmation bars are completed,
    the local downside sweep occurs over the approved preceding lookback, and the setup is
    followed by one completed bullish confirmation bar. The earliest candidate execution is the
    next candle open after the confirmation candle; no fill is assumed.
    """
    ordered = sorted(candles, key=lambda candle: candle.interval_start)
    if not ordered:
        return {"eligible": False, "reason": "empty_candle_set"}

    if lookback < 1:
        return {"eligible": False, "reason": "invalid_lookback"}

    if current_bar_start is not None:
        if any(candle.interval_start >= current_bar_start for candle in ordered):
            return {"eligible": False, "reason": "incomplete_current_bar"}

    if len(ordered) < lookback + 2:
        return {"eligible": False, "reason": "missing_context"}

    if not _is_intervals_contiguous(ordered):
        return {"eligible": False, "reason": "non_contiguous_candles"}

    for setup_index in range(lookback, len(ordered) - 1):
        setup = ordered[setup_index]
        confirmation = ordered[setup_index + 1]

        if current_bar_start is not None and confirmation.interval_start >= current_bar_start:
            return {"eligible": False, "reason": "incomplete_current_bar"}

        context = ordered[setup_index - lookback:setup_index]
        if len(context) < lookback:
            return {"eligible": False, "reason": "missing_context"}

        prior_low = min(candle.low for candle in context)
        lower_wick = min(setup.open, setup.close) - setup.low
        body = abs(setup.close - setup.open)
        candle_range = setup.high - setup.low
        prev_close_low = context[-1].low

        if not (setup.low < prior_low):
            continue
        if not (setup.close > prev_close_low):
            continue
        if not (lower_wick > body):
            continue
        if not (candle_range > 0):
            continue
        if not (confirmation.close > setup.high):
            continue

        entry_reference_index = setup_index + 2
        if entry_reference_index >= len(ordered):
            return {"eligible": False, "reason": "missing_entry_reference"}

        return {
            "eligible": True,
            "setup_index": setup_index,
            "confirmation_index": setup_index + 1,
            "entry_reference_index": entry_reference_index,
            "signal_timestamp": confirmation.interval_end,
            "entry_reference_time": ordered[entry_reference_index].interval_start,
            "entry_reference_open": ordered[entry_reference_index].open,
            "setup_candle": setup,
            "confirmation_candle": confirmation,
            "reason": "candidate_signal",
        }

    return {"eligible": False, "reason": "no_signal"}


def _candidate_forward_return(candles: list[OHLCVCandle], *, entry_reference_index: int, hold_period: int = DEFAULT_HOLD_PERIOD) -> float | None:
    if entry_reference_index < 0 or entry_reference_index >= len(candles):
        return None
    if hold_period < 1:
        return None
    exit_index = entry_reference_index + hold_period - 1
    if exit_index >= len(candles):
        return None
    entry_open = candles[entry_reference_index].open
    if entry_open == 0:
        return None
    return (candles[exit_index].close - entry_open) / entry_open


def _signal_observations_for_window(
    candles: list[OHLCVCandle],
    *,
    lookback: int,
    hold_period: int,
) -> list[dict]:
    ordered = sorted(candles, key=lambda candle: candle.interval_start)
    if len(ordered) < lookback + 2:
        return []
    if not _is_intervals_contiguous(ordered):
        return []

    observations: list[dict] = []
    for setup_index in range(lookback, len(ordered) - 1):
        setup = ordered[setup_index]
        confirmation = ordered[setup_index + 1]
        context = ordered[setup_index - lookback:setup_index]
        if len(context) < lookback:
            continue

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
        forward_return = _candidate_forward_return(
            ordered,
            entry_reference_index=entry_reference_index,
            hold_period=hold_period,
        )
        if forward_return is None:
            continue

        observations.append({
            "setup_index": setup_index,
            "confirmation_index": setup_index + 1,
            "entry_reference_index": entry_reference_index,
            "signal": 1 if local_rule_matches else 0,
            "forward_return": forward_return,
            "label": 1 if forward_return > 0 else 0,
            "entry_open": ordered[entry_reference_index].open,
            "exit_close": ordered[entry_reference_index + hold_period - 1].close,
            "signal_timestamp": confirmation.interval_end.isoformat(),
        })

    return observations


def run_second_strategy_experiment(*, manifest_path: str | Path | None = None, output_dir: str | Path | None = None, lookback: int = DEFAULT_LOOKBACK, hold_period: int = DEFAULT_HOLD_PERIOD, source_kind: str = "tardis") -> dict:
    manifest_path = _manifest_path(manifest_path, source_kind=source_kind)
    output_dir = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR

    try:
        manifest = _load_manifest(manifest_path)
    except FileNotFoundError:
        result = {
            "experiment_name": "btc_eur_local_rejection_confirmation_experiment",
            "execution_status": "BLOCKED",
            "status_detail": "manifest_missing",
            "source_kind": source_kind,
            "lookback": lookback,
            "forward_horizon_candles": hold_period,
            "entry_reference": "next_candle_open",
            "signal_validity": "immediately_following_confirmation_candle",
            "reason": f"Manifest was not found at {manifest_path}",
        }
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "btc_eur_second_strategy_report.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
        return result

    source_files = manifest.get("files", [])
    if not source_files:
        result = {
            "experiment_name": "btc_eur_local_rejection_confirmation_experiment",
            "execution_status": "BLOCKED",
            "status_detail": "manifest_empty",
            "source_kind": source_kind,
            "lookback": lookback,
            "forward_horizon_candles": hold_period,
            "entry_reference": "next_candle_open",
            "signal_validity": "immediately_following_confirmation_candle",
            "reason": "Manifest contains no file entries.",
            "manifest_status": manifest.get("status"),
        }
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "btc_eur_second_strategy_report.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
        return result

    valid_runs: list[dict] = []
    observations: list[dict] = []
    rejected_windows: list[dict] = []

    for entry in source_files:
        if source_kind == "kraken":
            trade_path = ROOT / _normalize_relative_path(entry["file"]["path"])
        else:
            trade_path = ROOT / _normalize_relative_path(entry["trade_file"]["path"])

        if not trade_path.exists():
            rejected_windows.append({"trade_file": str(trade_path), "reason": "missing_trade_file"})
            continue

        if source_kind == "kraken":
            try:
                candles = load_kraken_ohlcv(trade_path)
            except HSRAError:
                rejected_windows.append({"trade_file": str(trade_path), "reason": "no_valid_contiguous_run_under_research_contract"})
                continue
            windows = _extract_valid_run_windows_for_source(trade_path, source_kind=source_kind, candles=candles)
        else:
            windows = _extract_valid_run_windows_for_source(trade_path, source_kind=source_kind)

        if not windows:
            rejected_windows.append({"trade_file": str(trade_path), "reason": "no_valid_contiguous_run_under_research_contract"})
            continue

        valid_runs.extend({"trade_file": str(trade_path), **window} for window in windows)
        if source_kind == "kraken":
            window_lookup = {
                (run[0].interval_start.isoformat(), run[-1].interval_end.isoformat()): run
                for run in extract_contiguous_kraken_windows(candles)
            }
            for window in windows:
                relevant = window_lookup.get((window["run_start"], window["run_end"]))
                if relevant is None:
                    continue
                observations.extend(_signal_observations_for_window(relevant, lookback=lookback, hold_period=hold_period))
            continue

        for window in windows:
            try:
                candles = build_ohlcv_window(
                    trade_path,
                    requested_start=_datetime_from_iso(window["run_start"]),
                    requested_end=_datetime_from_iso(window["run_end"]),
                    interval_minutes=5,
                )
            except HSRAError:
                rejected_windows.append({
                    "trade_file": str(trade_path),
                    "run_start": window["run_start"],
                    "run_end": window["run_end"],
                    "reason": "window_validation_failed",
                })
                continue
            observations.extend(_signal_observations_for_window(candles, lookback=lookback, hold_period=hold_period))

    if not observations:
        result = {
            "experiment_name": "btc_eur_local_rejection_confirmation_experiment",
            "execution_status": "BLOCKED",
            "status_detail": "no_valid_observations",
            "source_kind": source_kind,
            "lookback": lookback,
            "forward_horizon_candles": hold_period,
            "entry_reference": "next_candle_open",
            "signal_validity": "immediately_following_confirmation_candle",
            "reason": "The approved bounded sample produced no eligible forward-return observations under the fail-closed strategy contract.",
            "manifest_status": manifest.get("status"),
            "sample_rule": manifest.get("scope", {}).get("sample_rule"),
            "valid_window_count": len(valid_runs),
            "rejected_windows": rejected_windows[:20],
        }
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "btc_eur_second_strategy_report.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
        return result

    signal_observations = [item for item in observations if item["signal"] == 1]
    signal_count = len(signal_observations)
    signal_positive_count = sum(1 for item in signal_observations if item["label"] == 1)
    baseline_positive_count = sum(1 for item in observations if item["label"] == 1)
    baseline_rate = (baseline_positive_count / len(observations)) if observations else None
    signal_positive_rate = (signal_positive_count / signal_count) if signal_count else None
    difference_pp = ((signal_positive_rate - baseline_rate) * 100.0) if signal_positive_rate is not None and baseline_rate is not None else None
    returns = [item["forward_return"] for item in observations]

    report = {
        "experiment_name": "btc_eur_local_rejection_confirmation_experiment",
        "execution_status": "PARTIALLY_WORKING",
        "status_detail": "bounded_second_strategy_sample_processed",
        "manifest_status": manifest.get("status"),
        "sample_rule": manifest.get("scope", {}).get("sample_rule"),
        "allowed_use": manifest.get("scope", {}).get("allowed_use"),
        "source_kind": source_kind,
        "lookback": lookback,
        "forward_horizon_candles": hold_period,
        "entry_reference": "next_candle_open",
        "signal_validity": "immediately_following_confirmation_candle",
        "valid_window_count": len(valid_runs),
        "eligible_observation_count": len(observations),
        "signal_observation_count": signal_count,
        "signal_count": signal_count,
        "signal_positive_count": signal_positive_count,
        "baseline_positive_count": baseline_positive_count,
        "eligible_outcome_count": len(observations),
        "signal_positive_rate": signal_positive_rate,
        "baseline_positive_rate": baseline_rate,
        "difference_pp": difference_pp,
        "mean_forward_return": mean(returns) if returns else None,
        "median_forward_return": median(returns) if returns else None,
        "min_forward_return": min(returns) if returns else None,
        "max_forward_return": max(returns) if returns else None,
        "signal_observations": signal_observations[:20],
        "baseline_observations": observations[:20],
        "rejected_windows": rejected_windows[:20],
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "btc_eur_second_strategy_report.json"
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the bounded BTC-EUR local downside sweep + rejection candle + bullish confirmation experiment.")
    parser.add_argument("--manifest", default=None, help="Path to the manifest JSON file. If omitted, the selected source default is used.")
    parser.add_argument("--outdir", default=str(DEFAULT_OUTPUT_DIR), help="Directory for the generated report.")
    parser.add_argument("--lookback", type=int, default=DEFAULT_LOOKBACK, help="Approved local downside sweep lookback in completed candles.")
    parser.add_argument("--horizon", type=int, default=DEFAULT_HOLD_PERIOD, help="Fixed holding horizon in completed candles for the descriptive forward-return measurement.")
    parser.add_argument("--source-kind", default="tardis", choices=["tardis", "kraken"], help="Select the explicit research data source for the experiment.")
    args = parser.parse_args(argv)

    manifest_path = args.manifest if args.manifest is not None else _manifest_path(None, source_kind=args.source_kind)

    result = run_second_strategy_experiment(
        manifest_path=manifest_path,
        output_dir=args.outdir,
        lookback=args.lookback,
        hold_period=args.horizon,
        source_kind=args.source_kind,
    )
    print(json.dumps({
        "execution_status": result["execution_status"],
        "lookback": result.get("lookback"),
        "forward_horizon_candles": result.get("forward_horizon_candles"),
        "eligible_observation_count": result.get("eligible_observation_count"),
        "signal_positive_rate": result.get("signal_positive_rate"),
        "baseline_positive_rate": result.get("baseline_positive_rate"),
        "difference_pp": result.get("difference_pp"),
        "output_path": str(Path(args.outdir) / "btc_eur_second_strategy_report.json"),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
