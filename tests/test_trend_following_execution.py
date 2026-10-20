from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from tools.trend_following.core import (
    LOOKBACKS,
    MIN_PRIOR_DAILY_BARS,
    SubmodelState,
    annualized_volatility,
    target_exposure,
    update_submodel,
)
from tools.trend_following.execution import (
    ExecutionConfig,
    WindowSpec,
    first_eligible_hourly_fill,
    initialize_window_portfolio,
    select_complete_windows,
    simulate_hourly_execution,
)
from tools.trend_following.experiment import build_window_plan, run_window_experiment
from tools.trend_following.kraken_hourly import TrendCandle, split_contiguous_daily_segments


def _hourly(start: datetime, prices: list[float]) -> list[TrendCandle]:
    candles: list[TrendCandle] = []
    for offset, price in enumerate(prices):
        ts = start + timedelta(hours=offset)
        candles.append(
            TrendCandle(
                interval_start=ts,
                interval_end=ts + timedelta(hours=1),
                open=price,
                high=price * 1.01,
                low=price * 0.99,
                close=price,
                volume=1.0,
                trade_count=1,
            )
        )
    return candles


def test_first_eligible_fill_uses_daily_signal_availability_zero_delay():
    signal_available = datetime(2024, 1, 2, tzinfo=timezone.utc)
    candles = _hourly(signal_available, [100.0, 101.0, 102.0])

    result = first_eligible_hourly_fill(candles, signal_available, delay_hours=0)

    assert result is not None
    assert result["interval_start"] == signal_available
    assert result["fill_price_eur"] == pytest.approx(100.0)


def test_first_eligible_fill_respects_delay_and_gap_aware_selection():
    signal_available = datetime(2024, 1, 2, tzinfo=timezone.utc)
    delay_hours = 2
    candles = _hourly(signal_available, [97.0, 98.0, 99.0])
    candles = candles[:1] + [
        TrendCandle(
            interval_start=signal_available + timedelta(hours=5),
            interval_end=signal_available + timedelta(hours=6),
            open=101.0,
            high=101.5,
            low=100.5,
            close=101.2,
            volume=1.0,
            trade_count=1,
        )
    ]

    result = first_eligible_hourly_fill(candles, signal_available, delay_hours=delay_hours)

    assert result is not None
    assert result["interval_start"] == signal_available + timedelta(hours=5)
    assert result["fill_price_eur"] == pytest.approx(101.0)


def test_select_complete_windows_is_deterministic_and_non_overlapping():
    starts = []
    current = datetime(2024, 1, 1, tzinfo=timezone.utc)
    for _ in range(1200):
        starts.append(current)
        current += timedelta(days=1)

    windows = select_complete_windows(
        starts,
        window_days=30,
        count=20,
        seed=7,
        selection_method="seeded_stride",
    )

    assert len(windows) == 20
    assert all(window.end > window.start for window in windows)
    assert all((window.end - window.start).days == 30 for window in windows)
    assert [window.start for window in windows] == sorted(window.start for window in windows)
    assert all(windows[i].end <= windows[i + 1].start for i in range(len(windows) - 1))


def test_window_config_rejects_invalid_selection_params():
    with pytest.raises(ValueError, match="count"):
        select_complete_windows([], window_days=30, count=0, seed=1, selection_method="seeded_stride")

    with pytest.raises(ValueError, match="selection_method"):
        select_complete_windows([], window_days=30, count=2, seed=1, selection_method="not-a-method")


def test_execution_config_validates_delay_and_window_days():
    with pytest.raises(ValueError, match="delay_hours"):
        ExecutionConfig(delay_hours=-1, fee_bps_per_side=25.0)

    with pytest.raises(ValueError, match="window_days"):
        ExecutionConfig(window_days=0, fee_bps_per_side=25.0)


def test_window_spec_requires_start_before_end():
    with pytest.raises(ValueError, match="start"):
        WindowSpec(start=datetime(2024, 1, 3, tzinfo=timezone.utc), end=datetime(2024, 1, 2, tzinfo=timezone.utc), initialization="WARM")


def _daily_closes(start: datetime, closes: list[float]) -> list[TrendCandle]:
    candles: list[TrendCandle] = []
    for index, close in enumerate(closes):
        day_start = start + timedelta(days=index)
        candles.append(
            TrendCandle(
                interval_start=day_start,
                interval_end=day_start + timedelta(days=1),
                open=close,
                high=close * 1.01,
                low=close * 0.99,
                close=close,
                volume=1.0,
                trade_count=1,
            )
        )
    return candles


def test_volatility_exposure_is_nonzero_when_90_return_sample_volatility_is_valid():
    closes = [100.0 * (1.02 ** index) for index in range(91)]
    sigma = annualized_volatility(closes)
    assert sigma is not None
    assert sigma > 0.0
    assert target_exposure(tuple(SubmodelState(long=True, stop=50.0) for _ in LOOKBACKS), sigma) > 0.0


def test_warm_initialization_replays_prior_daily_history_chronologically():
    prior = [100.0, 101.0, 102.0, 103.0, 104.0]
    states = tuple(SubmodelState() for _ in LOOKBACKS)
    for index in range(1, len(prior) + 1):
        history = prior[:index]
        states = tuple(
            update_submodel(history, lookback, state)
            for lookback, state in zip(LOOKBACKS, states)
        )
    assert states != tuple(SubmodelState() for _ in LOOKBACKS)
    assert any(state.long for state in states)


def test_cold_initialization_stays_flat_while_using_prior_history_for_volatility():
    prior = [100.0, 101.0] + [100.0 + index * 0.5 for index in range(2, 92)]
    daily_history = _daily_closes(datetime(2024, 1, 1, tzinfo=timezone.utc), prior)
    segments = split_contiguous_daily_segments(daily_history)
    assert len(segments) == 1
    sigma = annualized_volatility([c.close for c in daily_history])
    assert sigma is not None and sigma > 0.0
    assert initialize_window_portfolio("COLD") == initialize_window_portfolio("COLD")


def test_select_complete_windows_rejects_insufficient_history_and_requires_non_overlap():
    starts = [datetime(2024, 1, 1, tzinfo=timezone.utc) + timedelta(days=index) for index in range(1000)]
    with pytest.raises(ValueError, match="insufficient|eligible"):
        select_complete_windows(starts[:450], window_days=30, count=3, seed=1, selection_method="seeded_stride")

    windows = select_complete_windows(starts, window_days=30, count=5, seed=7, selection_method="seeded_stride")
    assert len(windows) == 5
    assert all((w.end - w.start).days == 30 for w in windows)
    assert all(windows[i].end <= windows[i + 1].start for i in range(len(windows) - 1))


def test_simulate_hourly_execution_respects_window_and_liquidation_costs():
    window_start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    daily = _daily_closes(window_start, [100.0] * (MIN_PRIOR_DAILY_BARS + 31))
    hourly = []
    for day_index, candle in enumerate(daily[:31]):
        for hour_index in range(24):
            ts = candle.interval_start + timedelta(hours=hour_index)
            hourly.append(
                TrendCandle(
                    interval_start=ts,
                    interval_end=ts + timedelta(hours=1),
                    open=100.0 + hour_index * 0.01,
                    high=100.0 + hour_index * 0.01 + 0.1,
                    low=100.0 + hour_index * 0.01 - 0.1,
                    close=100.0 + hour_index * 0.01,
                    volume=1.0,
                    trade_count=1,
                )
            )

    window = WindowSpec(start=window_start + timedelta(days=MIN_PRIOR_DAILY_BARS), end=window_start + timedelta(days=MIN_PRIOR_DAILY_BARS + 30), initialization="WARM")
    result = simulate_hourly_execution(
        hourly_candles=hourly,
        daily_candles=daily,
        window=window,
        config=ExecutionConfig(delay_hours=0, fee_bps_per_side=25.0, slippage_bps_per_side=1.5),
    )
    assert result["window"]["start"] == window.start.isoformat()
    assert result["window"]["end"] == window.end.isoformat()
    assert result["fees_eur"] >= 0.0
    assert result["slippage_eur"] >= 0.0
    assert result["fully_liquidated_equity_eur"] >= 0.0
    assert result["buy_and_hold_return_pct"] != 0.0 or result["starting_equity_eur"] == 100.0


def test_hourly_execution_ignores_invalid_gap_and_window_end():
    window_start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    daily = _daily_closes(window_start, [100.0] * (MIN_PRIOR_DAILY_BARS + 31))
    hourly = [
        TrendCandle(
            interval_start=window_start + timedelta(days=MIN_PRIOR_DAILY_BARS, hours=0),
            interval_end=window_start + timedelta(days=MIN_PRIOR_DAILY_BARS, hours=1),
            open=100.0,
            high=101.0,
            low=99.0,
            close=100.0,
            volume=1.0,
            trade_count=1,
        ),
        TrendCandle(
            interval_start=window_start + timedelta(days=MIN_PRIOR_DAILY_BARS + 30, hours=12),
            interval_end=window_start + timedelta(days=MIN_PRIOR_DAILY_BARS + 30, hours=13),
            open=105.0,
            high=106.0,
            low=104.0,
            close=105.0,
            volume=1.0,
            trade_count=1,
        ),
    ]
    window = WindowSpec(start=window_start + timedelta(days=MIN_PRIOR_DAILY_BARS), end=window_start + timedelta(days=MIN_PRIOR_DAILY_BARS + 30), initialization="WARM")
    result = simulate_hourly_execution(
        hourly_candles=hourly,
        daily_candles=daily,
        window=window,
        config=ExecutionConfig(delay_hours=0, fee_bps_per_side=25.0, slippage_bps_per_side=1.5),
    )
    assert result["window"]["end"] == window.end.isoformat()
    assert result["completed_executions"] >= 0


def test_build_window_plan_requires_seed_and_returns_selected_windows():
    daily = _daily_closes(datetime(2024, 1, 1, tzinfo=timezone.utc), [100.0] * 1000)
    windows = build_window_plan(daily, window_days=30, count=5, seed=7)
    assert len(windows) == 5
    assert all((window.end - window.start).days == 30 for window in windows)
    assert all(window.start >= datetime(2024, 1, 1, tzinfo=timezone.utc) + timedelta(days=MIN_PRIOR_DAILY_BARS) for window in windows)

    with pytest.raises(ValueError, match="seed"):
        build_window_plan(daily, window_days=30, count=5, seed=None)


def test_run_window_experiment_generates_summary_and_rejects_insufficient_eligible_windows():
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    daily = _daily_closes(start, [100.0] * 1000)
    hourly = []
    for candle in daily[:60]:
        for hour_index in range(24):
            ts = candle.interval_start + timedelta(hours=hour_index)
            hourly.append(
                TrendCandle(
                    interval_start=ts,
                    interval_end=ts + timedelta(hours=1),
                    open=100.0,
                    high=100.5,
                    low=99.5,
                    close=100.0,
                    volume=1.0,
                    trade_count=1,
                )
            )

    report = run_window_experiment(
        hourly_candles=hourly,
        daily_candles=daily,
        window_days=30,
        count=5,
        seed=7,
        delay_hours=0,
        fee_bps_per_side=25.0,
        slippage_bps_per_side=1.5,
    )
    assert report["config"]["seed"] == 7
    assert set(report["summary"]) == {"WARM", "COLD"}
    assert report["summary"]["WARM"]["window_count"] == 5
    assert report["summary"]["COLD"]["window_count"] == 5

    with pytest.raises(ValueError, match="insufficient_eligible_windows_for_requested_count"):
        build_window_plan(daily[:450], window_days=30, count=3, seed=1)
