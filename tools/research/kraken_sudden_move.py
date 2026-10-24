from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

FIXED_THRESHOLDS = (0.005, 0.01, 0.02)
VOLATILITY_THRESHOLDS = (2.0, 3.0)
HORIZONS = (3, 6, 12)
WARMUP_RETURNS = 288
BLOCK_SIZE = 288
SEED = 20261021


def _as_utc_ts(series: pd.Series) -> pd.Series:
    if pd.api.types.is_datetime64_any_dtype(series):
        return series.dt.tz_localize("UTC") if series.dt.tz is None else series.dt.tz_convert("UTC")
    return pd.to_datetime(series, unit="s", utc=True)


def _validate_row(row: list[str], *, file_name: str) -> tuple[bool, str | None, dict[str, float | int]]:
    if len(row) != 7:
        return False, "wrong_column_count", {}
    try:
        ts, open_price, high_price, low_price, close_price, volume, trade_count = [
            float(value.strip()) for value in row
        ]
    except (TypeError, ValueError):
        return False, "non_numeric_values", {}
    if not math.isfinite(ts) or not all(math.isfinite(value) for value in (open_price, high_price, low_price, close_price, volume, trade_count)):
        return False, "non_finite_values", {}
    if not float(ts).is_integer():
        return False, "non_integer_timestamp", {}
    ts_int = int(float(ts))
    if ts_int % 300 != 0:
        return False, "non_5m_timestamp", {}
    if min(open_price, high_price, low_price, close_price) <= 0:
        return False, "non_positive_ohlc", {}
    if high_price < max(open_price, low_price, close_price) or low_price > min(open_price, high_price, close_price):
        return False, "invalid_ohlcv_relationship", {}
    if volume < 0 or trade_count < 0:
        return False, "negative_volume_or_trades", {}
    if ts_int < 0:
        return False, "negative_timestamp", {}
    return True, None, {
        "timestamp": int(ts_int),
        "open": float(open_price),
        "high": float(high_price),
        "low": float(low_price),
        "close": float(close_price),
        "volume": float(volume),
        "trade_count": int(trade_count),
    }


def read_kraken_pair_csv(path: str | Path) -> pd.DataFrame:
    file_path = Path(path)
    valid_rows: list[dict[str, float | int]] = []
    invalid_counts: dict[str, int] = {}
    with file_path.open("r", encoding="utf-8", newline="") as handle:
        for line_no, raw_line in enumerate(handle, start=1):
            if not raw_line.strip() or raw_line.strip().startswith("#"):
                continue
            row = [cell.strip() for cell in raw_line.rstrip("\n").split(",")]
            ok, reason, values = _validate_row(row, file_name=file_path.name)
            if not ok:
                invalid_counts[reason or "unknown"] = invalid_counts.get(reason or "unknown", 0) + 1
                continue
            valid_rows.append(values)
    if not valid_rows:
        return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume", "trade_count"])

    frame = pd.DataFrame(valid_rows)
    frame = frame.sort_values("timestamp").reset_index(drop=True)
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], unit="s", utc=True)
    frame = frame.rename(columns={"timestamp": "timestamp"})
    return frame


def _ensure_columns(frame: pd.DataFrame) -> pd.DataFrame:
    required = ["timestamp", "open", "high", "low", "close", "volume", "trade_count"]
    missing = [name for name in required if name not in frame.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    out = frame.copy()
    out["timestamp"] = _as_utc_ts(out["timestamp"])
    for col in ["open", "high", "low", "close", "volume"]:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    out["trade_count"] = pd.to_numeric(out["trade_count"], errors="coerce")
    out = out[np.isfinite(out[["open", "high", "low", "close", "volume", "trade_count"]].to_numpy(dtype=float)).all(axis=1)].copy()
    out = out[(out["open"] > 0) & (out["high"] > 0) & (out["low"] > 0) & (out["close"] > 0)].copy()
    out = out[(out["high"] >= out[["open", "close", "low"]].max(axis=1)) & (out["low"] <= out[["open", "close", "high"]].min(axis=1))].copy()
    if len(out) > 1:
        out = out.sort_values("timestamp").reset_index(drop=True)
        ts_ns = out["timestamp"].astype("int64").to_numpy()
        gaps = np.diff(ts_ns) / 1_000_000_000
        if not np.all(gaps == 300):
            out["gap_flag"] = False
            for idx in range(1, len(out)):
                if (out["timestamp"].iloc[idx] - out["timestamp"].iloc[idx - 1]).total_seconds() != 300:
                    out.loc[idx, "gap_flag"] = True
        else:
            out["gap_flag"] = False
    else:
        out["gap_flag"] = False
    return out


def _log_return(close: pd.Series) -> pd.Series:
    values = np.asarray(close, dtype=float)
    if len(values) == 0:
        return pd.Series(np.array([], dtype=float), index=close.index)
    if len(values) == 1:
        return pd.Series(np.array([np.nan], dtype=float), index=close.index)
    with np.errstate(divide="ignore", invalid="ignore"):
        out = np.log(values / np.roll(values, 1))
    out[0] = np.nan
    return pd.Series(out, index=close.index)


def _valid_horizon_for_index(frame: pd.DataFrame, start_idx: int, horizon_candles: int) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    if start_idx < 0:
        reasons.append("invalid_start_index")
    if start_idx < 288:
        reasons.append("warmup")
    if start_idx + horizon_candles >= len(frame):
        reasons.append("lookahead")
        reasons.append("missing_future_candle")
    if len(frame) >= 2 and start_idx + horizon_candles < len(frame):
        seq = frame["timestamp"].iloc[start_idx : start_idx + horizon_candles + 1].astype("int64").to_numpy() / 1_000_000_000
        deltas = np.diff(seq)
        if not np.allclose(deltas, 300.0):
            reasons.append("gap")
    return (len(reasons) == 0), reasons


def _decimals_from_threshold(threshold: float) -> str:
    return f"{threshold * 100:.1f}pct"


def build_event_labels_reference(
    frame: pd.DataFrame,
    horizon_candles: int = 3,
    fixed_thresholds: Iterable[float] = FIXED_THRESHOLDS,
    volatility_thresholds: Iterable[float] = VOLATILITY_THRESHOLDS,
    use_volatility: bool = False,
) -> pd.DataFrame:
    frame = _ensure_columns(frame)
    result = frame.copy()
    result["log_return"] = _log_return(result["close"])
    result["close_to_close_return"] = result["close"].pct_change()

    for threshold in fixed_thresholds:
        if threshold <= 0:
            continue
        up_name = f"upward_{_decimals_from_threshold(threshold)}"
        down_name = f"downward_{_decimals_from_threshold(threshold)}"
        horizon_return = result["close"].pct_change(periods=horizon_candles).shift(-horizon_candles)
        result[up_name] = (horizon_return >= threshold).fillna(False)
        result[down_name] = (horizon_return <= -threshold).fillna(False)

    if use_volatility or volatility_thresholds:
        recent = []
        for idx in range(len(result)):
            if idx < 1:
                recent.append(np.nan)
                continue
            start = max(0, idx - WARMUP_RETURNS)
            sample = result["log_return"].iloc[start:idx].dropna().to_numpy(dtype=float)
            if sample.size < 288:
                recent.append(np.nan)
            else:
                recent.append(sample.std(ddof=1))
        vol_series = pd.Series(recent, index=result.index)
        for threshold in volatility_thresholds:
            threshold_name = str(threshold).replace(".0", "")
            up_name = f"volatility_{threshold_name}x_up"
            down_name = f"volatility_{threshold_name}x_down"
            horizon_log_return = np.log(result["close"].shift(-horizon_candles) / result["close"]) 
            scaled = vol_series * math.sqrt(horizon_candles) * threshold
            result[up_name] = ((horizon_log_return >= scaled) & (vol_series.notna())).fillna(False)
            result[down_name] = ((horizon_log_return <= -scaled) & (vol_series.notna())).fillna(False)
    return result


def build_event_labels(
    frame: pd.DataFrame,
    horizon_candles: int = 3,
    fixed_thresholds: Iterable[float] = FIXED_THRESHOLDS,
    volatility_thresholds: Iterable[float] = VOLATILITY_THRESHOLDS,
    use_volatility: bool = False,
) -> pd.DataFrame:
    frame = _ensure_columns(frame)
    result = frame.copy()
    close = result["close"].astype(float)
    if close.empty:
        return result

    log_return = np.full(len(close), np.nan, dtype=float)
    if len(close) > 1:
        with np.errstate(divide="ignore", invalid="ignore"):
            log_return[1:] = np.log(close.to_numpy()[1:] / close.to_numpy()[:-1])
    result["log_return"] = pd.Series(log_return, index=result.index)
    result["close_to_close_return"] = close.pct_change()

    future_close = close.shift(-horizon_candles)
    fixed_horizon_return = (future_close / close) - 1.0
    for threshold in fixed_thresholds:
        if threshold <= 0:
            continue
        up_name = f"upward_{_decimals_from_threshold(threshold)}"
        down_name = f"downward_{_decimals_from_threshold(threshold)}"
        result[up_name] = (fixed_horizon_return >= threshold).fillna(False)
        result[down_name] = (fixed_horizon_return <= -threshold).fillna(False)

    if use_volatility or volatility_thresholds:
        prev_log = result["log_return"].shift(1)
        vol_series = prev_log.rolling(window=WARMUP_RETURNS, min_periods=WARMUP_RETURNS).std(ddof=1)
        future_log_return = np.full(len(close), np.nan, dtype=float)
        if len(close) > horizon_candles:
            with np.errstate(divide="ignore", invalid="ignore"):
                future_log_return[:-horizon_candles] = np.log(close.to_numpy()[horizon_candles:] / close.to_numpy()[:-horizon_candles])
        future_log_return = pd.Series(future_log_return, index=result.index)
        for threshold in volatility_thresholds:
            threshold_name = str(threshold).replace(".0", "")
            up_name = f"volatility_{threshold_name}x_up"
            down_name = f"volatility_{threshold_name}x_down"
            scaled = vol_series * math.sqrt(horizon_candles) * threshold
            result[up_name] = ((future_log_return >= scaled) & vol_series.notna()).fillna(False)
            result[down_name] = ((future_log_return <= -scaled) & vol_series.notna()).fillna(False)
    return result


def compute_chronological_split(frame: pd.DataFrame) -> dict[str, pd.Timestamp | float | int | str]:
    df = _ensure_columns(frame).copy()
    start = df["timestamp"].min()
    end = df["timestamp"].max()
    total_seconds = (end - start).total_seconds()
    first_cut = start + pd.Timedelta(seconds=0.6 * total_seconds)
    second_cut = start + pd.Timedelta(seconds=0.8 * total_seconds)
    return {
        "start": start,
        "end": end,
        "total_seconds": total_seconds,
        "discovery_end": first_cut,
        "validation_end": second_cut,
        "test_end": end,
        "split_fraction": {"discovery": 0.6, "validation": 0.2, "test": 0.2},
    }


def deterministic_match_controls(
    events: pd.DataFrame,
    controls: pd.DataFrame,
    *,
    seed: int = SEED,
) -> pd.DataFrame:
    if events.empty or controls.empty:
        return pd.DataFrame(columns=["event_index", "control_index", "pair", "partition", "horizon", "volatility_quintile"])

    rng = np.random.default_rng(seed)
    event_index = []
    control_index = []
    paired_rows: list[dict[str, object]] = []

    event_cols = [col for col in ["pair", "partition", "horizon", "volatility_quintile"] if col in events.columns]
    control_cols = [col for col in ["pair", "partition", "horizon", "volatility_quintile"] if col in controls.columns]
    if not set(event_cols).issubset(events.columns):
        raise ValueError("events missing required matching columns")
    if not set(control_cols).issubset(controls.columns):
        raise ValueError("controls missing required matching columns")

    groups = controls.groupby(control_cols, sort=True)
    for event_idx, event_row in events.iterrows():
        key = tuple(event_row[col] for col in event_cols)
        candidate_df = groups.get_group(key) if key in groups.groups else pd.DataFrame(columns=controls.columns)
        if candidate_df.empty:
            continue
        available = candidate_df.index.to_numpy()
        if len(available) == 0:
            continue
        chosen = rng.choice(available, size=1, replace=False)[0]
        event_index.append(event_idx)
        control_index.append(chosen)
        paired_rows.append({
            "event_index": event_idx,
            "control_index": chosen,
            "pair": event_row.get("pair"),
            "partition": event_row.get("partition"),
            "horizon": event_row.get("horizon"),
            "volatility_quintile": event_row.get("volatility_quintile"),
        })

    return pd.DataFrame(paired_rows)


def moving_block_bootstrap(
    values: Iterable[float] | np.ndarray,
    *,
    block_size: int = BLOCK_SIZE,
    seed: int = SEED,
    replicates: int = 2000,
) -> np.ndarray:
    arr = np.asarray(list(values), dtype=float)
    if arr.size == 0:
        return np.empty((replicates,), dtype=float)
    rng = np.random.default_rng(seed)
    n = arr.size
    block_count = max(1, int(math.ceil(n / block_size)))
    bootstrap_means = np.empty(replicates, dtype=float)
    for i in range(replicates):
        sample = []
        for _ in range(block_count):
            start = rng.integers(0, n - block_size + 1)
            sample.extend(arr[start : start + block_size])
        sample_arr = np.asarray(sample[:n], dtype=float)
        bootstrap_means[i] = sample_arr.mean()
    return bootstrap_means


def benjamini_hochberg(p_values: Iterable[float], *, q: float = 0.05) -> np.ndarray:
    _ = q
    arr = np.asarray(list(p_values), dtype=float)
    if arr.size == 0:
        return np.empty((0,), dtype=float)
    m = arr.size
    order = np.argsort(arr)
    sorted_p = arr[order]
    adjusted_sorted = np.empty(m, dtype=float)
    running_min = 1.0
    for idx in range(m - 1, -1, -1):
        rank = idx + 1
        adjusted_sorted[idx] = min(1.0, sorted_p[idx] * (m / rank))
        if idx < m - 1:
            adjusted_sorted[idx] = min(adjusted_sorted[idx], adjusted_sorted[idx + 1])
    adjusted = np.empty(m, dtype=float)
    adjusted[order] = adjusted_sorted
    return adjusted


def summarize_window_features_reference(
    frame: pd.DataFrame,
    *,
    horizon_candles: int,
    event_start_index: int,
) -> dict[str, object]:
    event_df = _ensure_columns(frame).copy()
    exclusion_reasons: list[str] = []
    if event_start_index < WARMUP_RETURNS:
        exclusion_reasons.append("warmup: fewer than 288 prior valid returns")
    if event_start_index + horizon_candles >= len(event_df):
        exclusion_reasons.append("lookahead: missing future candles for required horizon")
    if len(event_df) > 1:
        start = max(0, event_start_index)
        end = min(len(event_df), event_start_index + horizon_candles + 1)
        if end > start:
            seq = pd.to_datetime(event_df["timestamp"].iloc[start:end]).astype("int64").to_numpy() / 1_000_000_000
            deltas = np.diff(seq)
            if not np.allclose(deltas, 300.0):
                exclusion_reasons.append("gap: required five-minute sequence not contiguous")
    return {
        "horizon_candles": horizon_candles,
        "event_start_index": event_start_index,
        "event_time": event_df["timestamp"].iloc[event_start_index].isoformat() if event_start_index < len(event_df) else None,
        "exclusions": exclusion_reasons,
        "prior_return_std": float(event_df["close"].pct_change().iloc[max(0, event_start_index - 288) : event_start_index].dropna().std(ddof=1)) if event_start_index > 0 else float("nan"),
        "horizon_return": float(event_df["close"].iloc[event_start_index + horizon_candles] / event_df["close"].iloc[event_start_index] - 1) if event_start_index + horizon_candles < len(event_df) else float("nan"),
    }


def summarize_window_features(
    frame: pd.DataFrame,
    *,
    horizon_candles: int,
    event_start_index: int,
) -> dict[str, object]:
    event_df = _ensure_columns(frame).copy()
    exclusion_reasons: list[str] = []
    if event_start_index < WARMUP_RETURNS:
        exclusion_reasons.append("warmup: fewer than 288 prior valid returns")
    if event_start_index + horizon_candles >= len(event_df):
        exclusion_reasons.append("lookahead: missing future candles for required horizon")
    if len(event_df) > 1:
        start = max(0, event_start_index)
        end = min(len(event_df), event_start_index + horizon_candles + 1)
        if end > start:
            seq = pd.to_datetime(event_df["timestamp"].iloc[start:end]).astype("int64").to_numpy() / 1_000_000_000
            deltas = np.diff(seq)
            if not np.allclose(deltas, 300.0):
                exclusion_reasons.append("gap: required five-minute sequence not contiguous")
    prior_close = event_df["close"].iloc[max(0, event_start_index - 288) : event_start_index].to_numpy(dtype=float)
    prior_std = float(np.std(np.diff(np.log(prior_close)), ddof=1)) if prior_close.size > 1 else float("nan")
    return {
        "horizon_candles": horizon_candles,
        "event_start_index": event_start_index,
        "event_time": event_df["timestamp"].iloc[event_start_index].isoformat() if event_start_index < len(event_df) else None,
        "exclusions": exclusion_reasons,
        "prior_return_std": prior_std,
        "horizon_return": float(event_df["close"].iloc[event_start_index + horizon_candles] / event_df["close"].iloc[event_start_index] - 1) if event_start_index + horizon_candles < len(event_df) else float("nan"),
    }


def _inventory_for_file(path: Path) -> dict[str, object]:
    frame = read_kraken_pair_csv(path)
    return {
        "pair": path.stem.replace("_5", ""),
        "file": path.name,
        "rows": int(len(frame)),
        "first_ts": frame["timestamp"].min().isoformat() if not frame.empty else None,
        "last_ts": frame["timestamp"].max().isoformat() if not frame.empty else None,
        "coverage_seconds": int((frame["timestamp"].max() - frame["timestamp"].min()).total_seconds()) if len(frame) > 1 else 0,
    }


def run_historical_analysis(data_dir: str | Path, output_dir: str | Path | None = None) -> dict[str, object]:
    data_root = Path(data_dir)
    if not data_root.exists():
        raise FileNotFoundError(f"Data directory not found: {data_root}")

    files = sorted(data_root.glob("*_5.csv"))
    inventory: list[dict[str, object]] = []
    event_rows: list[dict[str, object]] = []
    for path in files:
        frame = read_kraken_pair_csv(path)
        if frame.empty:
            continue
        pair_name = path.stem.replace("_5", "")
        inventory.append(_inventory_for_file(path))

        # Basic event-rate summary by fixed thresholds and horizons for each file.
        for horizon in HORIZONS:
            labels = build_event_labels(frame, horizon_candles=horizon)
            for threshold in FIXED_THRESHOLDS:
                up_col = f"upward_{_decimals_from_threshold(threshold)}"
                down_col = f"downward_{_decimals_from_threshold(threshold)}"
                event_rows.append({
                    "pair": pair_name,
                    "horizon": horizon,
                    "threshold": threshold,
                    "direction": "up",
                    "count": int(labels[up_col].fillna(False).sum()),
                    "period": "all",
                })
                event_rows.append({
                    "pair": pair_name,
                    "horizon": horizon,
                    "threshold": threshold,
                    "direction": "down",
                    "count": int(labels[down_col].fillna(False).sum()),
                    "period": "all",
                })

    summary = {
        "data_dir": str(data_root),
        "file_count": len(files),
        "inventory": inventory,
        "event_counts": event_rows,
        "strongest_by_direction": sorted(event_rows, key=lambda item: item["count"], reverse=True)[:10],
        "weakest_by_direction": sorted(event_rows, key=lambda item: item["count"])[:10],
    }

    if output_dir is not None:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        json_path = output_path / "kraken_sudden_move_summary.json"
        csv_path = output_path / "kraken_sudden_move_counts.csv"
        json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        pd.DataFrame(event_rows).to_csv(csv_path, index=False)

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Kraken sudden-move pattern research baseline: duplicate-free, read-only analysis.")
    parser.add_argument("--data-dir", type=str, default="data/kraken_5", help="Directory containing *_5.csv files.")
    parser.add_argument("--output-dir", type=str, default="reports/research/kraken_sudden_move_20261021", help="Directory for compact JSON and CSV outputs.")
    args = parser.parse_args()
    result = run_historical_analysis(args.data_dir, args.output_dir)
    print(json.dumps({
        "data_dir": result["data_dir"],
        "file_count": result["file_count"],
        "strongest": result["strongest_by_direction"][:3],
        "weakest": result["weakest_by_direction"][:3],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
