from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Sequence

from tools.trend_following.core import (
    LOOKBACKS,
    MIN_PRIOR_DAILY_BARS,
    SubmodelState,
    TrendStrategyInputError,
    annualized_volatility,
    target_exposure,
    update_submodel,
    volatility_rebalance_required,
)
from tools.trend_following.kraken_hourly import TrendCandle, split_contiguous_daily_segments
from tools.trend_following.portfolio import PortfolioState, marked_equity, rebalance_portfolio


VALID_INITIALIZATION = {"WARM", "COLD"}


@dataclass(frozen=True)
class ExecutionConfig:
    delay_hours: int = 0
    fee_bps_per_side: float = 25.0
    slippage_bps_per_side: float = 1.5
    window_days: int = 30
    selection_seed: int = 0
    selection_method: str = "seeded_stride"
    initialization: str = "WARM"

    def __post_init__(self) -> None:
        if self.delay_hours < 0:
            raise ValueError("delay_hours must be nonnegative")
        if self.window_days <= 0:
            raise ValueError("window_days must be positive")
        if self.selection_method != "seeded_stride":
            raise ValueError("selection_method must be 'seeded_stride'")
        if self.initialization not in VALID_INITIALIZATION:
            raise ValueError("initialization must be 'WARM' or 'COLD'")


@dataclass(frozen=True)
class WindowSpec:
    start: datetime
    end: datetime
    initialization: str = "WARM"
    selection_seed: int | None = None
    selection_method: str | None = None

    def __post_init__(self) -> None:
        if self.end <= self.start:
            raise ValueError("window end must be after window start")
        if self.initialization not in VALID_INITIALIZATION:
            raise ValueError("initialization must be 'WARM' or 'COLD'")


def initialize_window_portfolio(initialization: str = "WARM") -> PortfolioState:
    if initialization not in VALID_INITIALIZATION:
        raise ValueError("initialization must be 'WARM' or 'COLD'")
    return PortfolioState(cash_eur=100.0, btc_qty=0.0, fees_eur=0.0, slippage_eur=0.0)


def first_eligible_hourly_fill(
    candles: Sequence[TrendCandle],
    signal_available_at: datetime,
    *,
    delay_hours: int = 0,
    window_start: datetime | None = None,
    window_end: datetime | None = None,
) -> dict | None:
    if delay_hours < 0:
        raise ValueError("delay_hours must be nonnegative")
    if not candles:
        return None

    ready_at = signal_available_at.astimezone(timezone.utc) + timedelta(hours=delay_hours)
    start_bound = window_start.astimezone(timezone.utc) if window_start is not None else None
    end_bound = window_end.astimezone(timezone.utc) if window_end is not None else None
    for candle in sorted(candles, key=lambda item: item.interval_start):
        interval_start = candle.interval_start.astimezone(timezone.utc)
        if interval_start < ready_at:
            continue
        if start_bound is not None and interval_start < start_bound:
            continue
        if end_bound is not None and interval_start >= end_bound:
            break
        return {
            "interval_start": candle.interval_start,
            "interval_end": candle.interval_end,
            "fill_price_eur": float(candle.open),
            "signal_available_at": signal_available_at.astimezone(timezone.utc),
            "eligible_at": ready_at,
            "delay_hours": delay_hours,
        }
    return None


def select_complete_windows(
    day_starts: Sequence[datetime],
    *,
    window_days: int = 30,
    count: int = 20,
    seed: int = 0,
    selection_method: str = "seeded_stride",
    require_non_overlapping: bool = True,
) -> list[WindowSpec]:
    if count <= 0:
        raise ValueError("count must be positive")
    if window_days <= 0:
        raise ValueError("window_days must be positive")
    if selection_method != "seeded_stride":
        raise ValueError("selection_method must be 'seeded_stride'")

    starts = sorted(
        {
            dt.astimezone(timezone.utc)
            if dt.tzinfo is not None
            else dt.replace(tzinfo=timezone.utc)
            for dt in day_starts
        }
    )
    if not starts:
        return []

    eligible_starts: list[int] = []
    for start_index in range(len(starts) - window_days + 1):
        end_index = start_index + window_days
        if start_index < MIN_PRIOR_DAILY_BARS:
            continue
        if end_index > len(starts):
            continue
        eligible_starts.append(start_index)

    if len(eligible_starts) < count:
        raise ValueError("insufficient_eligible_windows_for_requested_count")

    if require_non_overlapping:
        selected: list[int] = []
        rng = seed % max(1, len(eligible_starts))
        step = max(1, len(eligible_starts) // max(1, count))
        candidate_positions = sorted(
            (rng + offset * step) % len(eligible_starts)
            for offset in range(len(eligible_starts))
        )
        for position in candidate_positions:
            candidate = eligible_starts[position]
            if selected and candidate < selected[-1] + window_days:
                continue
            selected.append(candidate)
            if len(selected) == count:
                break
        if len(selected) < count:
            raise ValueError("insufficient_non_overlapping_eligible_windows")
        selected = sorted(selected)
    else:
        step = max(1, len(eligible_starts) // count)
        selected = [eligible_starts[(seed + offset * step) % len(eligible_starts)] for offset in range(count)]
        selected = sorted(set(selected))
        if len(selected) < count:
            raise ValueError("insufficient_eligible_windows_for_requested_count")

    windows = [
        WindowSpec(
            start=starts[start_index],
            end=starts[start_index + window_days - 1] + timedelta(days=1),
            initialization="WARM",
            selection_seed=seed,
            selection_method=selection_method,
        )
        for start_index in selected[:count]
    ]
    return windows


def start_is_complete_window(day_starts: Sequence[datetime], start_index: int, window_days: int) -> bool:
    if start_index < MIN_PRIOR_DAILY_BARS:
        return False
    return start_index + window_days <= len(day_starts)


def _window_daily_candles(candles: Sequence[TrendCandle], window: WindowSpec) -> list[TrendCandle]:
    return [
        candle
        for candle in candles
        if window.start <= candle.interval_start and candle.interval_start < window.end
    ]


def _prior_contiguous_daily_candles(candles: Sequence[TrendCandle], boundary: datetime) -> list[TrendCandle]:
    for segment in split_contiguous_daily_segments(list(candles)):
        if not segment:
            continue
        first_ts = segment[0].interval_start
        last_ts = segment[-1].interval_start
        segment_end = last_ts + timedelta(days=1)
        if first_ts <= boundary < segment_end:
            return [c for c in segment if c.interval_start < boundary]
    return []


def _replay_prior_states(prior_closes: Sequence[float]) -> tuple[SubmodelState, ...]:
    states = tuple(SubmodelState() for _ in LOOKBACKS)
    history: list[float] = []
    for close in prior_closes:
        history.append(float(close))
        states = tuple(
            update_submodel(history, lookback, state)
            for lookback, state in zip(LOOKBACKS, states)
        )
    return states


def _daily_state_decision(
    closes: Sequence[float],
    states: Sequence[SubmodelState],
) -> tuple[tuple[SubmodelState, ...], float] | None:
    if len(closes) < MIN_PRIOR_DAILY_BARS + 1:
        return None
    target_states = tuple(
        update_submodel(closes, lookback, state)
        for lookback, state in zip(LOOKBACKS, states)
    )
    volatility = annualized_volatility(closes)
    target = target_exposure(target_states, volatility)
    return target_states, target


def simulate_hourly_execution(
    *,
    hourly_candles: Sequence[TrendCandle],
    daily_candles: Sequence[TrendCandle],
    window: WindowSpec,
    config: ExecutionConfig | None = None,
) -> dict:
    cfg = config or ExecutionConfig()
    if window.initialization not in VALID_INITIALIZATION:
        raise TrendStrategyInputError("window_initialization_must_be_warm_or_cold")

    state = initialize_window_portfolio(window.initialization)
    prior_closes = [
        float(c.close)
        for c in _prior_contiguous_daily_candles(daily_candles, window.start)
    ]
    if window.initialization == "WARM":
        states = _replay_prior_states(prior_closes)
    else:
        states = tuple(SubmodelState() for _ in LOOKBACKS)

    if len(prior_closes) < MIN_PRIOR_DAILY_BARS:
        prior_closes = []

    trades: list[dict] = []
    window_daily = _window_daily_candles(daily_candles, window)
    is_valid_segment = any(
        c.interval_start <= window.start < c.interval_start + timedelta(days=1)
        for c in daily_candles
    )
    if not is_valid_segment and window.initialization == "WARM":
        window_daily = []

    for candle in window_daily:
        closes_so_far = [float(item.close) for item in daily_candles if item.interval_start < candle.interval_end]
        if len(closes_so_far) < MIN_PRIOR_DAILY_BARS + 1:
            continue
        decision = _daily_state_decision(closes_so_far, states)
        if decision is None:
            continue
        states, target_exposure_value = decision

        fill = first_eligible_hourly_fill(
            hourly_candles,
            candle.interval_end,
            delay_hours=cfg.delay_hours,
            window_start=window.start,
            window_end=window.end,
        )
        if fill is None:
            continue

        reference_price = float(fill["fill_price_eur"])
        target_btc_qty = (marked_equity(state, reference_price) * target_exposure_value) / reference_price
        if state.btc_qty == 0.0 and target_exposure_value <= 0.0:
            continue
        if state.btc_qty == 0.0 or volatility_rebalance_required(target_btc_qty, state.btc_qty):
            updated, execution = rebalance_portfolio(
                state,
                target_exposure_value,
                reference_price,
                fee_bps_per_side=cfg.fee_bps_per_side,
                slippage_bps_per_side=cfg.slippage_bps_per_side,
            )
            if execution is not None:
                state = updated
                trades.append(
                    {
                        "signal_available_at": candle.interval_end,
                        "fill": fill,
                        "execution": execution,
                        "target_exposure": target_exposure_value,
                        "target_btc_qty": target_btc_qty,
                    }
                )

    mark_price = 100.0
    window_close_prices = [float(c.close) for c in window_daily]
    if len(window_close_prices) >= 2:
        start_price = float(window_daily[0].close)
        end_price = float(window_daily[-1].close)
    elif len(window_close_prices) == 1:
        start_price = end_price = float(window_close_prices[0])
    else:
        start_price = end_price = 100.0
    if any(c.interval_start < window.end for c in daily_candles):
        mark_price = float([c for c in daily_candles if c.interval_start < window.end][-1].close)

    liquidation, liquidation_execution = rebalance_portfolio(
        state,
        0.0,
        mark_price,
        fee_bps_per_side=cfg.fee_bps_per_side,
        slippage_bps_per_side=cfg.slippage_bps_per_side,
    )
    buy_and_hold_return_pct = ((end_price - start_price) / start_price) * 100.0 if start_price > 0 else 0.0
    ending_equity = marked_equity(state, mark_price)
    liquidated_equity = liquidation.cash_eur
    total_costs_eur = state.fees_eur + state.slippage_eur + liquidation_execution.fee_eur + liquidation_execution.slippage_eur if liquidation_execution is not None else state.fees_eur + state.slippage_eur

    return {
        "window": {
            "start": window.start.isoformat(),
            "end": window.end.isoformat(),
            "initialization": window.initialization,
            "selection_seed": window.selection_seed,
            "selection_method": window.selection_method,
        },
        "starting_equity_eur": 100.0,
        "ending_equity_eur": ending_equity,
        "marked_equity_eur": ending_equity,
        "fully_liquidated_equity_eur": liquidated_equity,
        "net_return_pct": ((ending_equity - 100.0) / 100.0) * 100.0,
        "buy_and_hold_return_pct": buy_and_hold_return_pct,
        "buy_and_hold_assumption": {
            "start_price_eur": start_price,
            "end_price_eur": end_price,
            "statement": "Buy-and-hold return uses the first and last complete daily closes inside the selected UTC window, with no carry-over from outside the window.",
        },
        "completed_executions": len(trades),
        "fees_eur": state.fees_eur,
        "slippage_eur": state.slippage_eur,
        "liquidation_fee_eur": liquidation_execution.fee_eur if liquidation_execution is not None else 0.0,
        "liquidation_slippage_eur": liquidation_execution.slippage_eur if liquidation_execution is not None else 0.0,
        "total_costs_eur": total_costs_eur,
        "trades": trades,
        "portfolio": state,
    }
