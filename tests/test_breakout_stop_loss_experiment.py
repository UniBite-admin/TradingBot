from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

import tools.hsra.breakout_stop_loss_experiment as experiment


def make_candles(count=80):
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return [
        SimpleNamespace(
            interval_start=start + timedelta(minutes=5 * index),
            interval_end=start + timedelta(minutes=5 * (index + 1)),
            open=100.0,
            high=101.0,
            low=99.0,
            close=100.0,
        )
        for index in range(count)
    ]


def signal(candles, setup=60, entry=61, exit=66, entry_price=100.0, exit_price=105.0):
    return {
        "signal_index": setup,
        "entry_reference_index": entry,
        "exit_reference_index": exit,
        "entry_price": entry_price,
        "exit_price": exit_price,
        "signal_timestamp": candles[setup].interval_end,
    }


def run_one(monkeypatch, candles, candidate):
    monkeypatch.setattr(
        experiment,
        "_candidate_signals_for_period",
        lambda _candles: iter([candidate]),
    )
    return experiment.run_breakout_stop_loss_period(
        candles,
        period_id="synthetic",
        initial_cash_eur=100.0,
    )


def test_stop_is_triggered_when_candle_low_reaches_stop(monkeypatch):
    candles = make_candles()
    candles[63].low = 98.0
    result = run_one(monkeypatch, candles, signal(candles))

    trade = result["completed_trades"][0]
    assert trade["exit_price"] == pytest.approx(98.0)
    assert trade["exit_reference_index"] == 63
    assert trade["exit_reason"] == "stop_loss_exit"
    assert result["stop_hit_count"] == 1


def test_gap_through_stop_exits_at_observed_open(monkeypatch):
    candles = make_candles()
    candles[63].open = 96.5
    candles[63].low = 95.0
    result = run_one(monkeypatch, candles, signal(candles))

    trade = result["completed_trades"][0]
    assert trade["exit_price"] == pytest.approx(96.5)
    assert trade["exit_reason"] == "stop_loss_gap_exit"


def test_scheduled_exit_is_used_when_stop_is_not_hit(monkeypatch):
    candles = make_candles()
    candles[66].close = 105.0
    result = run_one(monkeypatch, candles, signal(candles, exit_price=105.0))

    trade = result["completed_trades"][0]
    assert trade["exit_price"] == pytest.approx(105.0)
    assert trade["exit_reference_index"] == 66
    assert trade["exit_reason"] == "hold_period_exit"
    assert result["stop_hit_count"] == 0


def test_stop_takes_precedence_over_scheduled_exit_on_same_candle(monkeypatch):
    candles = make_candles()
    candles[66].low = 97.0
    candles[66].close = 110.0
    result = run_one(monkeypatch, candles, signal(candles, exit_price=110.0))

    trade = result["completed_trades"][0]
    assert trade["exit_price"] == pytest.approx(98.0)
    assert trade["exit_reason"] == "stop_loss_exit"


def test_signals_during_open_trade_are_skipped(monkeypatch):
    candles = make_candles()
    candidates = [
        signal(candles, setup=60, entry=61, exit=66, exit_price=105.0),
        signal(candles, setup=62, entry=63, exit=68, exit_price=110.0),
        signal(candles, setup=66, entry=67, exit=72, exit_price=104.0),
    ]
    monkeypatch.setattr(
        experiment,
        "_candidate_signals_for_period",
        lambda _candles: iter(candidates),
    )

    result = experiment.run_breakout_stop_loss_period(candles, period_id="synthetic")

    assert [trade["setup_index"] for trade in result["completed_trades"]] == [60, 66]
    assert result["trades_count"] == 2


def test_invalid_stop_fraction_is_rejected():
    with pytest.raises(ValueError, match="stop_loss_fraction_must_be_between_zero_and_one"):
        experiment.run_breakout_stop_loss_period(
            make_candles(),
            period_id="invalid-stop",
            stop_loss_fraction=1.0,
        )
