from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Iterable

from .ohlcv import OHLCVCandle


@dataclass(frozen=True)
class CostScenario:
    """Explicit per-side cost assumptions; these are not venue facts."""
    name: str
    fee_rate: float
    spread_bps: float
    slippage_bps: float
    status: str

    def __post_init__(self) -> None:
        values = (self.fee_rate, self.spread_bps, self.slippage_bps)
        if not self.name or not all(math.isfinite(v) and v >= 0 for v in values):
            raise ValueError("Cost scenario values must be finite and non-negative.")


def default_cost_scenarios(*, taker_fee_rate: float = 0.0025, spread_bps: float = 4.0, slippage_bps: float = 2.0) -> list[CostScenario]:
    """Return a gross-only diagnostic and an explicitly unverified sensitivity case."""
    return [
        CostScenario("gross_only", 0.0, 0.0, 0.0, "diagnostic_not_executable_net_pnl"),
        CostScenario("illustrative_taker_spread_slippage", taker_fee_rate, spread_bps, slippage_bps, "illustrative_unverified_sensitivity_case"),
    ]


def _scenario_costs(scenario: CostScenario, entry_notional: float, exit_notional: float) -> dict:
    entry_fees = entry_notional * scenario.fee_rate
    exit_fees = exit_notional * scenario.fee_rate
    entry_spread = entry_notional * scenario.spread_bps / 10000.0
    exit_spread = exit_notional * scenario.spread_bps / 10000.0
    entry_slippage = entry_notional * scenario.slippage_bps / 10000.0
    exit_slippage = exit_notional * scenario.slippage_bps / 10000.0
    fees = entry_fees + exit_fees
    spread = entry_spread + exit_spread
    slippage = entry_slippage + exit_slippage
    return {
        "status": scenario.status,
        "fee_rate_per_side": scenario.fee_rate,
        "spread_bps_per_side": scenario.spread_bps,
        "slippage_bps_per_side": scenario.slippage_bps,
        "entry_fees_eur": entry_fees,
        "exit_fees_eur": exit_fees,
        "entry_spread_cost_eur": entry_spread,
        "exit_spread_cost_eur": exit_spread,
        "entry_slippage_cost_eur": entry_slippage,
        "exit_slippage_cost_eur": exit_slippage,
        "fees_eur": fees,
        "spread_cost_eur": spread,
        "slippage_cost_eur": slippage,
        "total_cost_eur": fees + spread + slippage,
    }


def _summarize_cost_scenarios(trades: list[dict], scenarios: list[CostScenario]) -> dict:
    output = {}
    for scenario in scenarios:
        costs = [trade["cost_scenarios"][scenario.name] for trade in trades]
        net = [trade["gross_pnl_eur"] - cost["total_cost_eur"] for trade, cost in zip(trades, costs)]
        output[scenario.name] = {
            "status": scenario.status,
            "trade_count": len(trades),
            "fees_eur": sum(cost["fees_eur"] for cost in costs),
            "spread_cost_eur": sum(cost["spread_cost_eur"] for cost in costs),
            "slippage_cost_eur": sum(cost["slippage_cost_eur"] for cost in costs),
            "total_cost_eur": sum(cost["total_cost_eur"] for cost in costs),
            "gross_pnl_eur": sum(trade["gross_pnl_eur"] for trade in trades),
            "net_pnl_eur": sum(net),
            "win_count": sum(value > 0 for value in net),
            "loss_count": sum(value <= 0 for value in net),
        }
    return output


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


def _daily_boxes(segment: list[OHLCVCandle], interval_minutes: int) -> dict[date, dict]:
    """Build complete UTC-day boxes once, avoiding repeated full-segment scans."""
    grouped: dict[date, dict[datetime, OHLCVCandle]] = {}
    for candle in segment:
        start = candle.interval_start.astimezone(timezone.utc)
        grouped.setdefault(start.date(), {})[start] = candle

    expected_count = 1440 // interval_minutes
    boxes: dict[date, dict] = {}
    for day, by_start in grouped.items():
        if len(by_start) != expected_count:
            continue
        expected_starts = [
            datetime.combine(day, datetime.min.time(), tzinfo=timezone.utc)
            + timedelta(minutes=interval_minutes * index)
            for index in range(expected_count)
        ]
        if any(start not in by_start for start in expected_starts):
            continue
        day_candles = [by_start[start] for start in expected_starts]
        if not all(_valid_candle(candle, interval_minutes) for candle in day_candles):
            continue
        box_low = min(candle.low for candle in day_candles)
        box_high = max(candle.high for candle in day_candles)
        if not math.isfinite(box_low) or not math.isfinite(box_high) or box_low <= 0 or box_high <= box_low:
            continue
        box_range = box_high - box_low
        boxes[day] = {
            "box_date_utc": day.isoformat(),
            "box_low": box_low,
            "box_high": box_high,
            "box_mid": (box_low + box_high) / 2.0,
            "box_range": box_range,
        }
    return boxes

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
    cost_scenarios: list[CostScenario] | None = None,
) -> dict:
    """Backtest one contiguous segment; never bridges gaps or carries state across segments.

    Entry: after a completed candle trades into the bottom quarter of the prior UTC day's
    box and closes back above that zone, buy at the next candle open.
    Exit: box midpoint target; signal-candle low minus a configurable 5-bps price buffer.
    If OHLC data cannot determine whether stop or target came first, stop wins.
    """
    cfg = config or BoxTheoryConfig()
    scenarios = cost_scenarios if cost_scenarios is not None else default_cost_scenarios()
    ordered = sorted(candles, key=lambda candle: candle.interval_start)
    empty_summary = {
        "status": "eligible",
        "candles": len(ordered),
        "signals": 0,
        "trades": 0,
        "open_at_segment_end": 0,
        "gross_pnl_eur": 0.0,
        "cost_scenarios": _summarize_cost_scenarios([], scenarios),
    }
    if cfg.interval_minutes <= 0 or 1440 % cfg.interval_minutes != 0:
        return {"config": asdict(cfg), "summary": {**empty_summary, "status": "invalid_configuration"}, "trades": [], "signals": []}
    if (
        not math.isfinite(cfg.zone_fraction)
        or not 0 < cfg.zone_fraction < 0.5
        or not math.isfinite(cfg.stop_buffer_bps)
        or cfg.stop_buffer_bps < 0
        or not math.isfinite(cfg.notional_eur)
        or cfg.notional_eur <= 0
    ):
        return {"config": asdict(cfg), "summary": {**empty_summary, "status": "invalid_configuration"}, "trades": [], "signals": []}
    if not scenarios or len({scenario.name for scenario in scenarios}) != len(scenarios):
        return {"config": asdict(cfg), "summary": {**empty_summary, "status": "invalid_cost_scenarios"}, "trades": [], "signals": []}
    if not _segment_is_valid(ordered, cfg.interval_minutes):
        return {"config": asdict(cfg), "summary": {**empty_summary, "status": "rejected_invalid_or_noncontiguous_segment"}, "trades": [], "signals": []}

    daily_boxes = _daily_boxes(ordered, cfg.interval_minutes)
    signals: list[dict] = []
    trades: list[dict] = []
    index = 0
    open_at_end = 0
    while index < len(ordered) - 1:
        candle = ordered[index]
        signal_day = candle.interval_start.astimezone(timezone.utc).date()
        box = daily_boxes.get(signal_day - timedelta(days=1))
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
        gross = (exit_price - entry) * quantity
        trade_costs = {
            scenario.name: _scenario_costs(scenario, cfg.notional_eur, exit_notional)
            for scenario in scenarios
        }
        trades.append({
            **signal,
            "exit_index": exit_index,
            "exit_timestamp": ordered[exit_index].interval_end.astimezone(timezone.utc).isoformat(),
            "exit_price": exit_price,
            "exit_reason": exit_reason,
            "quantity": quantity,
            "entry_notional_eur": cfg.notional_eur,
            "exit_notional_eur": exit_notional,
            "gross_pnl_eur": gross,
            "cost_scenarios": trade_costs,
        })
        index = exit_index + 1

    summary = {
        **empty_summary,
        "signals": len(signals),
        "trades": len(trades),
        "open_at_segment_end": open_at_end,
        "gross_pnl_eur": sum(trade["gross_pnl_eur"] for trade in trades),
        "cost_scenarios": _summarize_cost_scenarios(trades, scenarios),
    }
    return {
        "config": asdict(cfg),
        "summary": summary,
        "signals": signals,
        "trades": trades,
        "cost_scenario_definitions": [asdict(scenario) for scenario in scenarios],
        "latency_cost": {"status": "not_priced", "reason": "No validated latency-to-EUR model is available."},
        "interpretation": "historical research only; no profitability or execution-readiness claim",
    }


def run_box_theory_segmented(
    candles: Iterable[OHLCVCandle],
    *,
    config: BoxTheoryConfig | None = None,
    cost_scenarios: list[CostScenario] | None = None,
) -> dict:
    """Split input at missing intervals and reset all strategy state for each segment."""
    cfg = config or BoxTheoryConfig()
    scenarios = cost_scenarios if cost_scenarios is not None else default_cost_scenarios()
    ordered = sorted(candles, key=lambda candle: candle.interval_start)
    if cfg.interval_minutes <= 0 or 1440 % cfg.interval_minutes != 0:
        return {
            "config": asdict(cfg),
            "segment_count": 0,
            "segments": [],
            "signals": [],
            "trades": [],
            "summary": {
                "status": "invalid_configuration",
                "candles": len(ordered),
                "segment_count": 0,
                "signals": 0,
                "trades": 0,
                "open_at_segment_end": 0,
                "gross_pnl_eur": 0.0,
                "cost_scenarios": _summarize_cost_scenarios([], scenarios),
            },
            "interpretation": "invalid configuration; no simulation performed",
        }
    if any(current.interval_start == previous.interval_start for previous, current in zip(ordered, ordered[1:])):
        return {
            "config": asdict(cfg),
            "segment_count": 0,
            "segments": [],
            "signals": [],
            "trades": [],
            "summary": {
                "status": "rejected_duplicate_timestamps",
                "candles": len(ordered),
                "segment_count": 0,
                "signals": 0,
                "trades": 0,
                "open_at_segment_end": 0,
                "gross_pnl_eur": 0.0,
                "cost_scenarios": _summarize_cost_scenarios([], scenarios),
            },
            "interpretation": "rejected input; duplicate timestamps are not treated as ordinary gaps",
        }
    segments: list[list[OHLCVCandle]] = []
    for candle in ordered:
        if not segments or candle.interval_start - segments[-1][-1].interval_start != timedelta(minutes=cfg.interval_minutes):
            segments.append([candle])
        else:
            segments[-1].append(candle)

    results = [
        run_box_theory_segment(segment, config=cfg, cost_scenarios=scenarios)
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
        "cost_scenario_definitions": [asdict(scenario) for scenario in scenarios],
        "latency_cost": {"status": "not_priced", "reason": "No validated latency-to-EUR model is available."},
        "summary": {
            "candles": len(ordered),
            "segment_count": len(segments),
            "signals": len(signals),
            "trades": len(trades),
            "open_at_segment_end": sum(result["summary"]["open_at_segment_end"] for result in results),
            "gross_pnl_eur": sum(trade["gross_pnl_eur"] for trade in trades),
            "cost_scenarios": _summarize_cost_scenarios(trades, scenarios),
        },
        "interpretation": "segmented historical research only; no profitability or execution-readiness claim",
    }
