from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .kraken_sudden_move import benjamini_hochberg

THRESHOLDS = (0.005, 0.01, 0.02)
HORIZON_MINUTES = (15, 30, 60)
WARMUP_CANDLES = 288
SEED = 20261021
BH_Q = 0.05
BOOTSTRAP_REPLICATES = 2000


def _prepare_frame(frame: pd.DataFrame) -> pd.DataFrame:
    if frame is None or frame.empty:
        raise ValueError("BTC/EUR OHLCV frame is empty")
    df = frame.copy()
    required = ["timestamp", "open", "high", "low", "close", "volume", "trade_count"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s", utc=True, errors="coerce")
    for col in ["open", "high", "low", "close", "volume", "trade_count"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["timestamp"]).copy()
    df = df[np.isfinite(df[["open", "high", "low", "close", "volume", "trade_count"]].to_numpy(dtype=float)).all(axis=1)].copy()
    df = df[(df["open"] > 0) & (df["high"] > 0) & (df["low"] > 0) & (df["close"] > 0)].copy()
    df = df[(df["high"] >= df[["open", "close", "low"]].max(axis=1)) & (df["low"] <= df[["open", "close", "high"]].min(axis=1))].copy()
    df = df.sort_values("timestamp").reset_index(drop=True)
    close = df["close"].to_numpy(dtype=float)
    if len(close) > 1:
        df["log_return"] = np.concatenate(([np.nan], np.diff(np.log(close))))
    else:
        df["log_return"] = np.nan
    return df


def load_btc_eur_5m(path: str | Path) -> pd.DataFrame:
    data_path = Path(path)
    if not data_path.exists():
        raise FileNotFoundError(f"BTC/EUR 5-minute OHLCV file not found: {data_path}")
    df = pd.read_csv(data_path, header=None, names=["timestamp", "open", "high", "low", "close", "volume", "trade_count"])
    return _prepare_frame(df)


def _chronological_periods(frame: pd.DataFrame, discovery_fraction: float = 0.6, validation_fraction: float = 0.2, test_fraction: float = 0.2) -> dict[str, tuple[int, int]]:
    if not np.isclose(discovery_fraction + validation_fraction + test_fraction, 1.0):
        raise ValueError("Discovery/validation/test fractions must sum to 1.0")
    n = len(frame)
    discovery_cut = int(round(n * discovery_fraction))
    validation_cut = int(round(n * (discovery_fraction + validation_fraction)))
    return {
        "discovery": (0, max(discovery_cut, WARMUP_CANDLES)),
        "validation": (discovery_cut, max(validation_cut, WARMUP_CANDLES)),
        "test": (validation_cut, n),
    }


def _window_is_contiguous(frame: pd.DataFrame, start_index: int, horizon_candles: int) -> bool:
    if start_index < 0 or start_index + horizon_candles >= len(frame):
        return False
    timestamps = frame["timestamp"].iloc[start_index : start_index + horizon_candles + 1]
    deltas = timestamps.diff().dropna().dt.total_seconds().to_numpy() / 60.0
    return len(deltas) == 0 or np.allclose(deltas, 5.0)


def scan_events(frame: pd.DataFrame, *, horizon_minutes: int, threshold: float, direction: str, period_name: str | None = None) -> pd.DataFrame:
    df = _prepare_frame(frame)
    horizon_candles = max(1, int(round(horizon_minutes / 5)))
    if direction not in {"up", "down"}:
        raise ValueError(f"Unsupported direction: {direction}")
    close = df["close"].to_numpy(dtype=float)
    n = len(close)
    trigger_mask = np.zeros(n, dtype=bool)
    event_starts: list[int] = []
    # The measured outcome needs a second full horizon after the trigger.
    # Require continuity across both windows and keep complete event/outcome
    # intervals non-overlapping.
    for idx in range(WARMUP_CANDLES, n - (2 * horizon_candles)):
        if not _window_is_contiguous(df, idx, 2 * horizon_candles):
            continue
        move = close[idx + horizon_candles] / close[idx] - 1.0
        if direction == "up":
            trigger_mask[idx] = move >= threshold
        else:
            trigger_mask[idx] = move <= -threshold
        if trigger_mask[idx]:
            if not event_starts or idx - event_starts[-1] >= 2 * horizon_candles:
                event_starts.append(idx)
    rows = []
    for idx in event_starts:
        move = close[idx + horizon_candles] / close[idx] - 1.0
        rows.append({
            "event_index": int(idx),
            "event_time": df["timestamp"].iloc[idx].isoformat(),
            "partition": period_name,
            "direction": direction,
            "threshold": float(threshold),
            "horizon_minutes": int(horizon_minutes),
            "horizon_candles": int(horizon_candles),
            "event_return": float(move),
            "eligible": True,
        })
    return pd.DataFrame(rows)


def _volatility_bucket(frame: pd.DataFrame, *, window: int = WARMUP_CANDLES) -> pd.Series:
    return frame["log_return"].rolling(window=window, min_periods=window).std(ddof=1)


def _matched_control_indices(frame: pd.DataFrame, event_df: pd.DataFrame, *, horizon_minutes: int, threshold: float, direction: str, seed: int = SEED) -> list[int]:
    df = _prepare_frame(frame)
    if event_df.empty:
        return []
    horizon_candles = max(1, int(round(horizon_minutes / 5)))
    close = df["close"].to_numpy(dtype=float)
    n = len(close)
    # A control must be a non-event for either direction and must have a
    # contiguous trigger-plus-outcome interval available.
    for idx in range(WARMUP_CANDLES, n - (2 * horizon_candles)):
        if not _window_is_contiguous(df, idx, 2 * horizon_candles):
            continue
        move = close[idx + horizon_candles] / close[idx] - 1.0
        trigger_mask[idx] = abs(move) >= threshold

    event_start_indices = event_df["event_index"].astype(int).to_numpy(dtype=int)
    exclusion_mask = np.zeros(n, dtype=bool)

    def exclude_complete_window(start_index: int) -> None:
        # [start, start + 2h] includes both the trigger and measured outcome.
        # A candidate start overlaps this interval iff it is within +/- 2h.
        start = max(0, start_index - (2 * horizon_candles))
        stop = min(n, start_index + (2 * horizon_candles) + 1)
        exclusion_mask[start:stop] = True

    for event_idx in event_start_indices:
        exclude_complete_window(int(event_idx))

    vol = _volatility_bucket(df)
    vol_bucket = pd.qcut(vol.fillna(0.0), q=5, duplicates="drop", labels=False)
    rng = np.random.default_rng(seed)
    chosen: list[int] = []
    for _, row in event_df.iterrows():
        event_idx = int(row["event_index"])
        bucket_value = vol_bucket.iloc[event_idx]
        if pd.isna(bucket_value):
            break
        candidates = np.flatnonzero(
            (~trigger_mask)
            & (~exclusion_mask)
            & (vol_bucket.to_numpy(dtype=float) == float(bucket_value))
        )
        candidates = candidates[(candidates >= WARMUP_CANDLES) & (candidates < n - (2 * horizon_candles))]
        if candidates.size == 0:
            # Keep the returned controls aligned with the first N event rows,
            # because the inference routine consumes event/control pairs in order.
            break
        selected = int(rng.choice(candidates))
        chosen.append(selected)
        exclude_complete_window(selected)
    return chosen


def _subsequent_return(frame: pd.DataFrame, event_start_index: int, horizon_minutes: int) -> float:
    horizon_candles = max(1, int(round(horizon_minutes / 5)))
    event_end_index = event_start_index + horizon_candles
    post_end_index = event_end_index + horizon_candles
    if event_end_index >= len(frame) or post_end_index >= len(frame):
        return float("nan")
    if not _window_is_contiguous(frame, event_end_index, horizon_candles):
        return float("nan")
    return float(frame["close"].iloc[post_end_index] / frame["close"].iloc[event_end_index] - 1.0)


def _paired_effect_and_p_value(
    frame: pd.DataFrame,
    events: pd.DataFrame,
    control_indices: list[int],
    *,
    horizon_minutes: int,
    direction: str,
    seed: int = SEED,
    bootstrap_replicates: int = BOOTSTRAP_REPLICATES,
) -> tuple[np.ndarray, np.ndarray, float, float, float, float, float]:
    if not control_indices:
        return (np.empty((0,), dtype=float), np.empty((0,), dtype=float), float("nan"), float("nan"), float("nan"), float("nan"), float("nan"))

    max_pairs = min(len(events), len(control_indices))
    event_indices = events["event_index"].astype(int).tolist()[:max_pairs]
    matched_controls = [int(control) for control in control_indices[:max_pairs]]
    event_returns: list[float] = []
    control_returns: list[float] = []
    for event_idx, control_idx in zip(event_indices, matched_controls):
        event_outcome = _subsequent_return(frame, event_idx, horizon_minutes)
        control_outcome = _subsequent_return(frame, control_idx, horizon_minutes)
        if np.isfinite(event_outcome) and np.isfinite(control_outcome):
            event_returns.append(float(event_outcome))
            control_returns.append(float(control_outcome))

    if not event_returns:
        return (np.empty((0,), dtype=float), np.empty((0,), dtype=float), float("nan"), float("nan"), float("nan"), float("nan"), float("nan"))

    event_arr = np.asarray(event_returns, dtype=float)
    control_arr = np.asarray(control_returns, dtype=float)
    diffs = event_arr - control_arr
    observed_effect = float(np.mean(diffs))

    n = diffs.size
    if n < 2 or bootstrap_replicates < 1:
        return event_arr, control_arr, observed_effect, float("nan"), float("nan"), float("nan"), float("nan")

    # The paired differences are kept in chronological event order. A moving
    # block bootstrap over this ordered difference series retains local
    # dependence between nearby event outcomes better than iid resampling.
    # It remains an approximation: controls are matched observations, not a
    # resampled reconstruction of the raw BTC/EUR return process.
    block_size = min(n, max(3 * int(round(horizon_minutes / 5)), 12))
    rng = np.random.default_rng(seed)
    replicates = int(bootstrap_replicates)
    bootstrap_stats = np.empty(replicates, dtype=float)
    null_stats = np.empty(replicates, dtype=float)
    centered_diffs = diffs - observed_effect
    for i in range(replicates):
        sample_indices: list[int] = []
        while len(sample_indices) < n:
            start = int(rng.integers(0, n - block_size + 1))
            sample_indices.extend(range(start, start + block_size))
        indices = np.asarray(sample_indices[:n], dtype=int)
        bootstrap_stats[i] = float(np.mean(diffs[indices]))
        null_stats[i] = float(np.mean(centered_diffs[indices]))

    # Two-sided null test; use a finite-sample correction so p-values cannot be 0.
    p_value = float((1 + np.count_nonzero(np.abs(null_stats) >= abs(observed_effect))) / (replicates + 1))
    ci_low, ci_high = np.quantile(bootstrap_stats, [0.025, 0.975])
    return event_arr, control_arr, observed_effect, p_value, float(ci_low), float(ci_high), float(np.std(diffs, ddof=1))


def evaluate_period_summary(
    frame: pd.DataFrame,
    *,
    period_name: str,
    threshold: float,
    horizon_minutes: int,
    direction: str,
    seed: int = SEED,
    bootstrap_replicates: int = BOOTSTRAP_REPLICATES,
) -> dict[str, object]:
    df = _prepare_frame(frame)
    events = scan_events(df, horizon_minutes=horizon_minutes, threshold=threshold, direction=direction, period_name=period_name)
    if events.empty:
        return {
            "period": period_name,
            "threshold": float(threshold),
            "horizon_minutes": int(horizon_minutes),
            "direction": direction,
            "event_count": 0,
            "control_count": 0,
            "continuation_rate": float("nan"),
            "reversal_rate": float("nan"),
            "mean_event_return": float("nan"),
            "mean_control_return": float("nan"),
            "effect_size": float("nan"),
            "effect_ci_95_low": float("nan"),
            "effect_ci_95_high": float("nan"),
            "p_value": float("nan"),
            "p_value_adj": float("nan"),
            "event_return_sd": float("nan"),
            "control_return_sd": float("nan"),
            "notes": "No qualifying events met warm-up and valid-window criteria in this period.",
        }

    control_indices = _matched_control_indices(df, events, horizon_minutes=horizon_minutes, threshold=threshold, direction=direction, seed=seed)
    event_returns = []
    control_returns = []
    for _, row in events.iterrows():
        outcome = _subsequent_return(df, int(row["event_index"]), horizon_minutes)
        if np.isfinite(outcome):
            event_returns.append(float(outcome))
    for control_idx in control_indices:
        outcome = _subsequent_return(df, int(control_idx), horizon_minutes)
        if np.isfinite(outcome):
            control_returns.append(float(outcome))

    event_arr = np.asarray(event_returns, dtype=float)
    control_arr = np.asarray(control_returns, dtype=float)
    if event_arr.size:
        sign = 1.0 if direction == "up" else -1.0
        continuation_rate = float(np.mean(np.sign(event_arr) == sign))
        reversal_rate = float(np.mean(np.sign(event_arr) == -sign))
    else:
        continuation_rate = float("nan")
        reversal_rate = float("nan")

    if event_arr.size and control_arr.size:
        effect_size = float(np.mean(event_arr) - np.mean(control_arr))
        se = float(np.sqrt(np.var(event_arr, ddof=1) / event_arr.size + np.var(control_arr, ddof=1) / control_arr.size))
        ci_low = effect_size - 1.96 * se
        ci_high = effect_size + 1.96 * se
    else:
        effect_size = float("nan")
        ci_low = float("nan")
        ci_high = float("nan")

    matched_event_arr, matched_control_arr, observed_effect, p_value, ci_low_bs, ci_high_bs, paired_sd = _paired_effect_and_p_value(
        df,
        events,
        control_indices,
        horizon_minutes=horizon_minutes,
        direction=direction,
        seed=seed,
        bootstrap_replicates=bootstrap_replicates,
    )
    if matched_event_arr.size and matched_control_arr.size:
        effect_size = float(np.mean(matched_event_arr) - np.mean(matched_control_arr))
        ci_low = ci_low_bs
        ci_high = ci_high_bs
    elif matched_event_arr.size == 0 or matched_control_arr.size == 0:
        effect_size = float("nan")
        ci_low = float("nan")
        ci_high = float("nan")
        p_value = float("nan")

    return {
        "period": period_name,
        "threshold": float(threshold),
        "horizon_minutes": int(horizon_minutes),
        "direction": direction,
        "event_count": int(len(events)),
        "control_count": int(len(control_indices)),
        "continuation_rate": continuation_rate,
        "reversal_rate": reversal_rate,
        "mean_event_return": float(np.mean(event_arr)) if event_arr.size else float("nan"),
        "mean_control_return": float(np.mean(control_arr)) if control_arr.size else float("nan"),
        "effect_size": effect_size,
        "effect_ci_95_low": ci_low,
        "effect_ci_95_high": ci_high,
        "p_value": float(p_value) if np.isfinite(p_value) else float("nan"),
        "p_value_adj": float("nan"),
        "event_return_sd": float(np.std(event_arr, ddof=1)) if event_arr.size > 1 else float("nan"),
        "control_return_sd": float(np.std(control_arr, ddof=1)) if control_arr.size > 1 else float("nan"),
        "paired_return_sd": float(paired_sd) if np.isfinite(paired_sd) else float("nan"),
        "notes": "Warm-up is 288 5-minute candles; event, control, and outcome windows are non-overlapping within a period; insufficient matches are reported explicitly and excluded from inference.",
    }


def run_continuation_study(
    data_path: str | Path,
    *,
    output_dir: str | Path | None = None,
    discovery_fraction: float = 0.6,
    validation_fraction: float = 0.2,
    test_fraction: float = 0.2,
    seed: int = SEED,
    bootstrap_replicates: int = BOOTSTRAP_REPLICATES,
) -> dict[str, object]:
    frame = load_btc_eur_5m(data_path)
    periods = _chronological_periods(frame, discovery_fraction=discovery_fraction, validation_fraction=validation_fraction, test_fraction=test_fraction)
    summary_rows: list[dict[str, object]] = []
    for period_name, (start_idx, end_idx) in periods.items():
        period_frame = frame.iloc[start_idx:end_idx].copy()
        for threshold in THRESHOLDS:
            for horizon_minutes in HORIZON_MINUTES:
                for direction in ("up", "down"):
                    row = evaluate_period_summary(
                        period_frame,
                        period_name=period_name,
                        threshold=threshold,
                        horizon_minutes=horizon_minutes,
                        direction=direction,
                        seed=seed,
                        bootstrap_replicates=bootstrap_replicates,
                    )
                    row["start_index"] = int(start_idx)
                    row["end_index"] = int(end_idx)
                    summary_rows.append(row)

    discovery_indices = [i for i, row in enumerate(summary_rows) if row.get("period") == "discovery" and np.isfinite(row.get("p_value", np.nan))]
    discovery_pvalues = np.asarray([float(summary_rows[i]["p_value"]) for i in discovery_indices], dtype=float)
    discovery_adjusted = benjamini_hochberg(discovery_pvalues, q=BH_Q) if discovery_pvalues.size else np.empty((0,), dtype=float)
    for pos, row_index in enumerate(discovery_indices):
        summary_rows[row_index]["p_value_adj"] = float(discovery_adjusted[pos])
        summary_rows[row_index]["significant_fdr_05"] = bool(discovery_adjusted[pos] <= BH_Q)

    discovery_adjusted_results = [
        {
            "period": row["period"],
            "threshold": row["threshold"],
            "horizon_minutes": row["horizon_minutes"],
            "direction": row["direction"],
            "p_value": row.get("p_value"),
            "p_value_adj": row.get("p_value_adj"),
            "significant_fdr_05": row.get("significant_fdr_05", False),
            "effect_size": row.get("effect_size"),
            "event_count": row.get("event_count"),
            "control_count": row.get("control_count"),
        }
        for row in summary_rows
        if row.get("period") == "discovery" and np.isfinite(row.get("p_value", np.nan))
    ]

    output_summary = {
        "study": "btc_eur_continuation",
        "file": Path(data_path).name,
        "source_path": str(Path(data_path)),
        "timeframe_start": frame["timestamp"].iloc[0].isoformat(),
        "timeframe_end": frame["timestamp"].iloc[-1].isoformat(),
        "thresholds": list(THRESHOLDS),
        "horizons_minutes": list(HORIZON_MINUTES),
        "directions": ["up", "down"],
        "periods": {k: {"start_index": int(v[0]), "end_index": int(v[1])} for k, v in periods.items()},
        "event_count_total": int(sum(int(row["event_count"]) for row in summary_rows)),
        "period_summaries": summary_rows,
        "discovery_adjusted_results": discovery_adjusted_results,
        "limitations": [
            "This is a descriptive continuation study, not a profitability or execution model.",
            "BH-FDR is applied only to the 54 discovery-period threshold/horizon/direction hypotheses at q=0.05.",
            "Controls must not cross either directional event threshold; control and event trigger-plus-outcome windows are unique and non-overlapping within each period and volatility bucket.",
            "Uncertainty uses a moving-block bootstrap over chronologically ordered paired differences (block length max(3 x horizon candles, 12), capped at pair count; 2,000 replicates by default). This approximates local dependence in paired effects but does not reconstruct the raw return process.",
            "The study uses a 288-candle warm-up and requires contiguous trigger and outcome windows; no outcome is measured across a timestamp gap.",
        ],
    }

    if output_dir is not None:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        json_path = output_path / "btc_eur_continuation_summary.json"
        csv_path = output_path / "btc_eur_continuation_summary.csv"
        json_path.write_text(json.dumps(output_summary, indent=2, ensure_ascii=False), encoding="utf-8")
        pd.DataFrame(summary_rows).to_csv(csv_path, index=False)

    return output_summary


def main() -> None:
    parser = argparse.ArgumentParser(description="BTC/EUR 5-minute trend-continuation study with matched non-event controls.")
    parser.add_argument("--data-path", type=str, default="data/kraken/XBTEUR_5.csv", help="Kraken BTC/EUR 5-minute OHLCV path.")
    parser.add_argument("--output-dir", type=str, default="reports/research/btc_eur_continuation_study_20261024", help="Directory for compact JSON and CSV outputs.")
    parser.add_argument("--discovery-fraction", type=float, default=0.6)
    parser.add_argument("--validation-fraction", type=float, default=0.2)
    parser.add_argument("--test-fraction", type=float, default=0.2)
    args = parser.parse_args()
    result = run_continuation_study(
        args.data_path,
        output_dir=args.output_dir,
        discovery_fraction=args.discovery_fraction,
        validation_fraction=args.validation_fraction,
        test_fraction=args.test_fraction,
    )
    print(json.dumps({
        "file": result["file"],
        "event_count_total": result["event_count_total"],
        "periods": result["periods"],
        "limitations": result["limitations"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
