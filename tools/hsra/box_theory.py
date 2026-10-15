from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Iterable

from .cost import CostModel
from .ohlcv import OHLCVCandle


@dataclass(frozen=True)
class BoxTheoryConfig:
    """Research-only Box Theory parameters; not approved live-trading settings."""

    symbol: str = "BTC-EUR"
    interval_minutes: int = 5
    zone_fraction: float = 0.25
    stop_buffer_bps: float = 5.0
    notional_eur: float = 50.0


def _valid_candle(candle: OHLCVCandle, interval_minutes: int) -> bool:
    values = (candle.open, candle.high, candle.low, candle.close, candle.volume)
    if not all(math.isfinite(value) for value in values):
        return False
    if min(candle.open, candle.high, candle.low, candle.close) <= 0 or candle.volume < 0:
        return False
    if candle.low > min(candle.open, candle.close) or candle.high < max(candle.open, candle.close):
        return False
    if candle.interval_start.tzinfo is None or candle.interval_end.tzinfo is None:
        return False
    start = candle.interval_start.astimezone(timezone.utc)
    end = candle.interval_end.astimezone(timezone.utc)
    return (
        start.second == 0
        and start.microsecond == 0
        and start.minute % interval_minutes == 0
        and end - start == timedelta(minutes=interval_minutes)
    )


def _daily_box(segment: list[OHLCVCandle], signal_index: int, interval_minutes: int) -> dict | None:
    signal_time = segment[signal_index].interval_start.astimezone(timezone.utc)
    previous_day = signal_time.date() - timedelta(days=1)
    expected_count = 1440 // interval_minutes
    expected_starts = [
        datetime.combine(previous_day, datetime.min.time(), tzinfo=timezone.utc)
        + timedelta(minutes=interval_minutes * index)
        for index in range(expected_count)
    ]
    by_start = {
        candle.interval_start.astimezone(timezone.utc): candle
        for candle in segment
        if candle.interval_start.tzinfo is not None
        and candle.interval_start.astimezone(timezone.utc).date() == previous_day
    }
    if len(by_start) != expected_count or any(start not in by_start for start in expected_starts):
        return None
    day_candles = [by_start[start] for start in expected_starts]
    if not all(_valid_candle(candle, interval_minutes) for candle in day_candles):
        return None
    box_low = min(candle.low for candle in day_candles)
    box_high = max(candle.high for candle in day_candles)
    if not math.isfinite(box_low) or not math.isfinite(box_high) or box_low <= 0 or box_high <= box_low:
        return None
    box_range = box_high - box_low
    return {
        "box_date_utc": previous_day.isoformat(),
        "box_low": box_low,
        "box_high": box_high,
        "box_mid": (box_low + box_high) / 2.0,
        "box_range": box_range,
        "zone_high": box_low + 0.25 * box_range,
    }


def _segment_is_valid(ordered: list[OHLCVCandle], interval_minutes: int) -> bool:
    if not ordered:
        return True
    for candle in ordered:
        if not _valid_candle(candle, interval_minutes):
            return False
    for previous, current in zip(ordered, ordered[1:]):
        if current.interval_start.astimezone(timezone.utc) - previous.interval_start.astimezone(timezone.utc) != timedelta(minutes=interval_minutes):
            return False
    return True


def run_box_theory_segment(
    candles: Iterable[OHLCVCandle],
    *,
    config: BoxTheoryConfig | None = None,
    cost_model: CostModel | None = None,
) -> dict:
    """Backtest one contiguous segment; never bridges gaps or carries state across segments.

    Entry: after a completed candle trades into the bottom quarter of the prior UTC day's
    box and closes back above that zone, buy at the next candle open.
    Exit: box midpoint target; signal-candle low minus a configurable 5-bps price buffer.
    If OHLC data cannot determine whether stop or target came first, stop wins.
    """
    cfg = config or BoxTheoryConfig()
    costs = cost_model or CostModel()
    ordered = sorted(candles, key=lambda candle: candle.interval_start)
    empty_summary = {
        "status": "eligible",
        "candles": len(ordered),
        "signals": 0,
        "trades": 0,
        "open_at_segment_end": 0,
        "gross_pnl_eur": 0.0,
        "estimated_cost_eur": 0.0,
        "net_pnl_eur": 0.0,
        "win_count": 0,
        "loss_count": 0,
    }
    if cfg.interval_minutes <= 0 or 1440 % cfg.interval_minutes != 0:
        return {"config": asdict(cfg), "summary": {**empty_summary, "status": "invalid_configuration"}, "trades": [], "signals": []}
    if not 0 < cfg.zone_fraction < 0.5 or cfg.stop_buffer_bps < 0 or cfg.notional_eur <= 0:
        return {"config": asdict(cfg), "summary": {**empty_summary, "status": "invalid_configuration"}, "trades": [], "signals": []}
    if not _segment_is_valid(ordered, cfg.interval_minutes):
        return {"config": asdict(cfg), "summary": {**empty_summary, "status": "rejected_invalid_or_noncontiguous_segment"}, "trades": [], "signals": []}

    signals: list[dict] = []
    trades: list[dict] = []
    index = 0
    open_at_end = 0
    while index < len(ordered) - 1:
        candle = ordered[index]
        box = _daily_box(ordered, index, cfg.interval_minutes)
        if box is None:
            index += 1
            continue
        zone_high = box["box_low"] + cfg.zone_fraction * box["box_range"]
        if not (
            candle.low <= zone_high
            and candle.close > zone_high
            and box["box_low"] <= candle.close <= box["box_high"]
        ):
            index += 1
            continue

        entry_index = index + 1
        entry_candle = ordered[entry_index]
        entry = entry_candle.open
        stop = candle.low - candle.low * cfg.stop_buffer_bps / 10000.0
        target = box["box_mid"]
        signal = {
            "signal_index": index,
            "signal_timestamp": candle.interval_end.astimezone(timezone.utc).isoformat(),
            "entry_index": entry_index,
            "entry_timestamp": entry_candle.interval_start.astimezone(timezone.utc).isoformat(),
            "box_date_utc": box["box_date_utc"],
            "box_low": box["box_low"],
            "box_high": box["box_high"],
            "box_mid": box["box_mid"],
            "zone_high": zone_high,
            "entry_price": entry,
            "stop_price": stop,
            "target_price": target,
        }
        signals.append(signal)
        if not (math.isfinite(entry) and stop < entry < target):
            signal["status"] = "rejected_invalid_entry_stop_target_geometry"
            index += 1
            continue
        signal["status"] = "candidate"

        exit_index = None
        exit_price = None
        exit_reason = None
        for cursor in range(entry_index, len(ordered)):
            bar = ordered[cursor]
            # Stop-first is the conservative policy when intrabar order is unknowable.
            if bar.open <= stop:
                exit_index, exit_price, exit_reason = cursor, bar.open, "stop_gap"
                break
            if bar.open >= target:
                exit_index, exit_price, exit_reason = cursor, target, "target_gap"
                break
            stop_hit = bar.low <= stop
            target_hit = bar.high >= target
            if stop_hit:
                exit_index, exit_price, exit_reason = cursor, stop, "stop"
                break
            if target_hit:
                exit_index, exit_price, exit_reason = cursor, target, "target"
                break

        if exit_index is None:
            open_at_end += 1
            signal["status"] = "unclosed_at_segment_end"
            index = len(ordered)
            continue

        quantity = cfg.notional_eur / entry
        exit_notional = quantity * exit_price
        entry_cost = costs.estimate_trade_cost(price=entry, notional=cfg.notional_eur, side="buy")
        exit_cost = costs.estimate_trade_cost(price=exit_price, notional=exit_notional, side="sell")
        gross = (exit_price - entry) * quantity
        total_cost = entry_cost["total_cost_eur"] + exit_cost["total_cost_eur"]
        net = gross - total_cost
        trades.append({
            **signal,
            "exit_index": exit_index,
            "exit_timestamp": ordered[exit_index].interval_end.astimezone(timezone.utc).isoformat(),
            "exit_price": exit_price,
            "exit_reason": exit_reason,
            "quantity": quantity,
            "gross_pnl_eur": gross,
            "entry_cost_eur": entry_cost["total_cost_eur"],
            "exit_cost_eur": exit_cost["total_cost_eur"],
            "estimated_cost_eur": total_cost,
            "net_pnl_eur": net,
        })
        index = exit_index + 1

    summary = {
        **empty_summary,
        "signals": len(signals),
        "trades": len(trades),
        "open_at_segment_end": open_at_end,
        "gross_pnl_eur": sum(trade["gross_pnl_eur"] for trade in trades),
        "estimated_cost_eur": sum(trade["estimated_cost_eur"] for trade in trades),
        "net_pnl_eur": sum(trade["net_pnl_eur"] for trade in trades),
        "win_count": sum(trade["net_pnl_eur"] > 0 for trade in trades),
        "loss_count": sum(trade["net_pnl_eur"] <= 0 for trade in trades),
    }
    return {
        "config": asdict(cfg),
        "summary": summary,
        "signals": signals,
        "trades": trades,
        "interpretation": "historical research only; no profitability or execution-readiness claim",
    }


def run_box_theory_segmented(
    candles: Iterable[OHLCVCandle],
    *,
    config: BoxTheoryConfig | None = None,
    cost_model: CostModel | None = None,
) -> dict:
    """Split input at missing intervals and reset all strategy state for each segment."""
    cfg = config or BoxTheoryConfig()
    ordered = sorted(candles, key=lambda candle: candle.interval_start)
    segments: list[list[OHLCVCandle]] = []
    for candle in ordered:
        if not segments or candle.interval_start - segments[-1][-1].interval_start != timedelta(minutes=cfg.interval_minutes):
            segments.append([candle])
        else:
            segments[-1].append(candle)

    results = [
        run_box_theory_segment(segment, config=cfg, cost_model=cost_model)
        for segment in segments
    ]
    trades = [
        {**trade, "segment_index": segment_index}
        for segment_index, result in enumerate(results)
        for trade in result["trades"]
    ]
    signals = [
        {**signal, "segment_index": segment_index}
        for segment_index, result in enumerate(results)
        for signal in result["signals"]
    ]
    return {
        "config": asdict(cfg),
        "segment_count": len(segments),
        "segments": [
            {"segment_index": index, **result["summary"]}
            for index, result in enumerate(results)
        ],
        "signals": signals,
        "trades": trades,
        "summary": {
            "candles": len(ordered),
            "segment_count": len(segments),
            "signals": len(signals),
            "trades": len(trades),
            "open_at_segment_end": sum(result["summary"]["open_at_segment_end"] for result in results),
            "gross_pnl_eur": sum(trade["gross_pnl_eur"] for trade in trades),
            "estimated_cost_eur": sum(trade["estimated_cost_eur"] for trade in trades),
            "net_pnl_eur": sum(trade["net_pnl_eur"] for trade in trades),
            "win_count": sum(trade["net_pnl_eur"] > 0 for trade in trades),
            "loss_count": sum(trade["net_pnl_eur"] <= 0 for trade in trades),
        },
        "interpretation": "segmented historical research only; no profitability or execution-readiness claim",
    }
