from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .breakout_strategy import evaluate_price_channel_breakout_signal
from .kraken_ohlcv import extract_contiguous_kraken_windows, load_kraken_ohlcv

DATA_PATH = Path("data/kraken/XBTEUR_5.csv")

BREAKOUT_PARAMETER_GRID = [
    {"channel_lookback": 6, "trend_filter": "none", "hold_period": 3},
    {"channel_lookback": 6, "trend_filter": "none", "hold_period": 6},
    {"channel_lookback": 6, "trend_filter": "none", "hold_period": 12},
    {"channel_lookback": 6, "trend_filter": "close_above_sma20", "hold_period": 3},
    {"channel_lookback": 6, "trend_filter": "close_above_sma20", "hold_period": 6},
    {"channel_lookback": 6, "trend_filter": "close_above_sma20", "hold_period": 12},
    {"channel_lookback": 6, "trend_filter": "close_above_sma20_and_sma20_gt_sma50", "hold_period": 3},
    {"channel_lookback": 6, "trend_filter": "close_above_sma20_and_sma20_gt_sma50", "hold_period": 6},
    {"channel_lookback": 6, "trend_filter": "close_above_sma20_and_sma20_gt_sma50", "hold_period": 12},
    {"channel_lookback": 12, "trend_filter": "none", "hold_period": 3},
    {"channel_lookback": 12, "trend_filter": "none", "hold_period": 6},
    {"channel_lookback": 12, "trend_filter": "none", "hold_period": 12},
    {"channel_lookback": 12, "trend_filter": "close_above_sma20", "hold_period": 3},
    {"channel_lookback": 12, "trend_filter": "close_above_sma20", "hold_period": 6},
    {"channel_lookback": 12, "trend_filter": "close_above_sma20", "hold_period": 12},
    {"channel_lookback": 12, "trend_filter": "close_above_sma20_and_sma20_gt_sma50", "hold_period": 3},
    {"channel_lookback": 12, "trend_filter": "close_above_sma20_and_sma20_gt_sma50", "hold_period": 6},
    {"channel_lookback": 12, "trend_filter": "close_above_sma20_and_sma20_gt_sma50", "hold_period": 12},
    {"channel_lookback": 24, "trend_filter": "none", "hold_period": 3},
    {"channel_lookback": 24, "trend_filter": "none", "hold_period": 6},
    {"channel_lookback": 24, "trend_filter": "none", "hold_period": 12},
    {"channel_lookback": 24, "trend_filter": "close_above_sma20", "hold_period": 3},
    {"channel_lookback": 24, "trend_filter": "close_above_sma20", "hold_period": 6},
    {"channel_lookback": 24, "trend_filter": "close_above_sma20", "hold_period": 12},
    {"channel_lookback": 24, "trend_filter": "close_above_sma20_and_sma20_gt_sma50", "hold_period": 3},
    {"channel_lookback": 24, "trend_filter": "close_above_sma20_and_sma20_gt_sma50", "hold_period": 6},
    {"channel_lookback": 24, "trend_filter": "close_above_sma20_and_sma20_gt_sma50", "hold_period": 12},
    {"channel_lookback": 48, "trend_filter": "none", "hold_period": 3},
    {"channel_lookback": 48, "trend_filter": "none", "hold_period": 6},
    {"channel_lookback": 48, "trend_filter": "none", "hold_period": 12},
    {"channel_lookback": 48, "trend_filter": "close_above_sma20", "hold_period": 3},
    {"channel_lookback": 48, "trend_filter": "close_above_sma20", "hold_period": 6},
    {"channel_lookback": 48, "trend_filter": "close_above_sma20", "hold_period": 12},
    {"channel_lookback": 48, "trend_filter": "close_above_sma20_and_sma20_gt_sma50", "hold_period": 3},
    {"channel_lookback": 48, "trend_filter": "close_above_sma20_and_sma20_gt_sma50", "hold_period": 6},
    {"channel_lookback": 48, "trend_filter": "close_above_sma20_and_sma20_gt_sma50", "hold_period": 12},
]


def _field(candle, key: str):
    if isinstance(candle, dict):
        return candle.get(key)
    return getattr(candle, key)


def _sorted_ordered(candles: list[dict]) -> list[dict]:
    return sorted(candles, key=lambda candle: _field(candle, "interval_start"))


def _parameter_key(parameters: dict) -> tuple[int, str, int]:
    return (int(parameters["channel_lookback"]), str(parameters["trend_filter"]), int(parameters["hold_period"]))


def _parameter_from_key(key: tuple[int, str, int]) -> dict:
    return {"channel_lookback": key[0], "trend_filter": key[1], "hold_period": key[2]}


def build_chronological_partitions(candles: list[dict]) -> dict[str, list[dict]]:
    ordered = _sorted_ordered(candles)
    if not ordered:
        raise ValueError("no_candles_available_for_partition")
    total = len(ordered)
    train_count = int(total * 0.60)
    validation_count = int(total * 0.20)
    test_count = total - train_count - validation_count
    if train_count <= 0 or validation_count <= 0 or test_count <= 0:
        raise ValueError("dataset_too_small_for_60_20_20_split")
    train = ordered[:train_count]
    validation = ordered[train_count:train_count + validation_count]
    test = ordered[train_count + validation_count:]
    return {"train": train, "validation": validation, "test": test}


def _partition_boundaries(partitions: dict[str, list[dict]]) -> dict[str, dict]:
    def boundaries(values: list[dict]) -> dict | None:
        if not values:
            return None
        return {
            "start": _field(values[0], "interval_start").isoformat(),
            "end": _field(values[-1], "interval_end").isoformat(),
            "count": len(values),
        }

    return {name: boundaries(values) for name, values in partitions.items()}


def _compute_gap_statistics(candles: list[dict]) -> dict:
    ordered = _sorted_ordered(candles)
    gaps: list[float] = []
    for previous, current in zip(ordered, ordered[1:]):
        delta_minutes = (_field(current, "interval_start") - _field(previous, "interval_start")).total_seconds() / 60.0
        if delta_minutes > 5.0:
            gaps.append(delta_minutes - 5.0)
    return {
        "gap_count": len(gaps),
        "total_gap_minutes": round(sum(gaps), 2),
        "max_gap_minutes": round(max(gaps), 2) if gaps else 0.0,
        "contiguous_windows": len(extract_contiguous_kraken_windows(ordered)),
    }


def select_breakout_parameters(records: dict[tuple[int, str, int], float], *, grid: list[dict] | None = None) -> dict:
    if not records:
        raise ValueError("no_validation_results_for_parameter_selection")
    ordered_grid = grid or BREAKOUT_PARAMETER_GRID
    best_key: tuple[int, str, int] | None = None
    best_score: float | None = None
    for parameters in ordered_grid:
        key = _parameter_key(parameters)
        score = float(records.get(key, float("-inf")))
        if best_key is None or score > (best_score if best_score is not None else float("-inf")):
            best_key = key
            best_score = score
    if best_key is None:
        raise ValueError("selection_failed")
    return _parameter_from_key(best_key)


def _trend_filter_passes(*, signal_close: float, candles: list[dict], signal_index: int, trend_filter: str) -> bool:
    if trend_filter == "none":
        return True

    lookback_20 = candles[max(0, signal_index - 20):signal_index]
    if len(lookback_20) < 20:
        return False
    sma_20 = sum(_field(candle, "close") for candle in lookback_20) / len(lookback_20)
    if trend_filter == "close_above_sma20":
        return signal_close > sma_20

    lookback_50 = candles[max(0, signal_index - 50):signal_index]
    if len(lookback_50) < 50:
        return False
    sma_50 = sum(_field(candle, "close") for candle in lookback_50) / len(lookback_50)
    return signal_close > sma_20 and sma_20 > sma_50


def _evaluate_partition_stats(candles: list[dict], *, channel_lookback: int, trend_filter: str, hold_period: int) -> dict:
    trade_returns: list[float] = []
    trade_details: list[dict] = []
    eligible_signal_count = 0
    for signal_index in range(channel_lookback, len(candles)):
        if signal_index + 1 >= len(candles):
            continue
        signal = candles[signal_index]
        channel_window = candles[signal_index - channel_lookback:signal_index]
        if len(channel_window) < channel_lookback:
            continue
        channel_high = max(_field(candle, "high") for candle in channel_window)
        if _field(signal, "close") <= channel_high:
            continue
        if not _trend_filter_passes(signal_close=_field(signal, "close"), candles=candles, signal_index=signal_index, trend_filter=trend_filter):
            continue

        entry_reference_index = signal_index + 1
        exit_reference_index = entry_reference_index + hold_period - 1
        if exit_reference_index >= len(candles):
            continue
        eligible_signal_count += 1
        entry_price = float(_field(candles[entry_reference_index], "open"))
        exit_price = float(_field(candles[exit_reference_index], "close"))
        if entry_price <= 0:
            continue
        trade_return = (exit_price - entry_price) / entry_price
        trade_returns.append(trade_return)
        trade_details.append({
            "signal_index": signal_index,
            "entry_index": entry_reference_index,
            "exit_index": exit_reference_index,
            "entry_timestamp": _field(candles[entry_reference_index], "interval_start").isoformat(),
            "exit_timestamp": _field(candles[exit_reference_index], "interval_end").isoformat(),
            "entry_price": entry_price,
            "exit_price": exit_price,
            "gross_return": trade_return,
        })

    gross_return_sum = sum(trade_returns)
    trade_count = len(trade_details)
    return {
        "channel_lookback": channel_lookback,
        "trend_filter": trend_filter,
        "hold_period": hold_period,
        "eligible_signal_count": eligible_signal_count,
        "trade_count": trade_count,
        "gross_return_sum": gross_return_sum,
        "average_trade_return": (gross_return_sum / trade_count) if trade_count else 0.0,
        "trades": trade_details,
    }


def evaluate_breakout_grid(candles: list[dict], *, grid: list[dict] | None = None) -> list[dict]:
    ordered_grid = grid or BREAKOUT_PARAMETER_GRID
    results: list[dict] = []
    for parameters in ordered_grid:
        result = _evaluate_partition_stats(
            candles,
            channel_lookback=int(parameters["channel_lookback"]),
            trend_filter=str(parameters["trend_filter"]),
            hold_period=int(parameters["hold_period"]),
        )
        results.append(result)
    return results


def run_breakout_experiment(*, data_path: str | Path = DATA_PATH, output_dir: str | Path = "reports") -> dict:
    source_path = Path(data_path)
    candles = load_kraken_ohlcv(source_path)
    sha256 = hashlib.sha256(source_path.read_bytes()).hexdigest()
    partitions = build_chronological_partitions(candles)
    train_summary = evaluate_breakout_grid(partitions["train"])
    validation_summary = evaluate_breakout_grid(partitions["validation"])
    validation_scores = {
        _parameter_key({
            "channel_lookback": item["channel_lookback"],
            "trend_filter": item["trend_filter"],
            "hold_period": item["hold_period"],
        }): float(item["gross_return_sum"])
        for item in validation_summary
    }
    selected = select_breakout_parameters(validation_scores)
    final_test_summary = _evaluate_partition_stats(
        partitions["test"],
        channel_lookback=int(selected["channel_lookback"]),
        trend_filter=str(selected["trend_filter"]),
        hold_period=int(selected["hold_period"]),
    )

    payload = {
        "report_name": "kraken_breakout_parameter_grid_2026-10-15",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python -m tools.hsra.breakout_experiment",
        "exit_status": 0,
        "source": {
            "path": str(source_path),
            "sha256": sha256,
            "row_count": len(candles),
            "start_utc": _field(candles[0], "interval_start").isoformat(),
            "end_utc": _field(candles[-1], "interval_end").isoformat(),
            "validation": {
                "duplicate_timestamps": 0,
                "gap_statistics": _compute_gap_statistics(candles),
                "contiguous_windows": len(extract_contiguous_kraken_windows(candles)),
            },
            "note": "This dataset is a Kraken BTC/EUR 5-minute OHLCV source only and does not represent Bitvavo execution conditions.",
        },
        "chronological_split": {
            "partition_rule": "60% train, 20% validation, 20% final test by chronological order",
            "boundary_indices": {
                "train_end": len(partitions["train"]),
                "validation_end": len(partitions["validation"]),
                "test_end": len(partitions["test"]),
            },
            "boundaries": _partition_boundaries(partitions),
            "boundary_handling": "Boundary candles remain inside the partition where their timestamps fall; no trade may span a partition boundary.",
        },
        "selection_rule": {
            "rule": "Evaluate all 36 parameter combinations on the training and validation partitions only. Rank by validation gross return sum descending, tie-break by the fixed grid order, and freeze the best parameters before final-test evaluation.",
            "grid_order": BREAKOUT_PARAMETER_GRID,
        },
        "training_results": train_summary,
        "validation_results": validation_summary,
        "selected_parameters": selected,
        "final_test_results": final_test_summary,
        "limitations": [
            "Gross returns are reported, not net profitability.",
            "No realistic execution costs, spread, slippage, or risk limits are modeled.",
            "This is a historical research study only and is not a live-trading approval.",
            "Final-test results are evaluated only after parameter selection is fixed.",
        ],
    }

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    report_path = output_path / "kraken_breakout_parameter_grid_2026-10-15.json"
    manifest_path = output_path / "kraken_breakout_parameter_grid_2026-10-15_manifest.json"
    report_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    manifest_path.write_text(json.dumps({
        "report_path": str(report_path),
        "sha256": sha256,
        "selected_parameters": selected,
        "partition_boundaries": _partition_boundaries(partitions),
    }, indent=2, sort_keys=True), encoding="utf-8")
    return payload


if __name__ == "__main__":
    run_breakout_experiment()
