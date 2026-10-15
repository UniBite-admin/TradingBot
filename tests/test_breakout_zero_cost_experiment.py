from datetime import timedelta

from tools.hsra.breakout_zero_cost_experiment import (
    BREAKOUT_ZERO_COST_CONFIG,
    get_period_ranges,
    run_breakout_experiment,
)


def test_breakout_zero_cost_uses_frozen_configuration():
    assert BREAKOUT_ZERO_COST_CONFIG == {
        "channel_lookback": 6,
        "trend_filter": "close_above_sma20_and_sma20_gt_sma50",
        "hold_period": 6,
        "entry_reference": "next_candle_open",
        "exit_reference": "final_candle_close",
        "initial_cash_eur": 100.0,
    }


def test_breakout_zero_cost_uses_exact_20_periods():
    weekly, monthly = get_period_ranges()
    assert len(weekly) == 10
    assert len(monthly) == 10
    assert weekly[0]["period_id"] == "7d-01"
    assert monthly[0]["period_id"] == "30d-01"
    assert weekly[0]["start"] == "2018-03-04T19:25:00+00:00"
    assert weekly[-1]["end"] == "2026-05-01T15:05:00+00:00"
    assert monthly[0]["start"] == "2019-12-31T18:20:00+00:00"
    assert monthly[-1]["end"] == "2026-07-09T14:20:00+00:00"


def test_breakout_zero_cost_experiment_produces_20_results():
    payload = run_breakout_experiment()
    assert len(payload["weekly_runs"]) == 10
    assert len(payload["monthly_runs"]) == 10
    assert payload["weekly_summary"]["period_count"] == 10
    assert payload["monthly_summary"]["period_count"] == 10
    for item in payload["weekly_runs"] + payload["monthly_runs"]:
        assert item["initial_cash_eur"] == 100.0
        assert item["end_equity_eur"] >= 0.0



def test_breakout_period_skips_signals_that_overlap_previous_trade(monkeypatch):
    from datetime import datetime, timezone
    from types import SimpleNamespace

    import tools.hsra.breakout_zero_cost_experiment as experiment

    candles = [
        SimpleNamespace(
            interval_start=datetime.fromtimestamp(index * 300, tz=timezone.utc),
            interval_end=datetime.fromtimestamp((index + 1) * 300, tz=timezone.utc),
        )
        for index in range(80)
    ]
    signals = [
        {
            "signal_index": 60,
            "entry_reference_index": 61,
            "exit_reference_index": 66,
            "entry_price": 10.0,
            "exit_price": 11.0,
            "signal_timestamp": candles[60].interval_end,
        },
        {
            "signal_index": 62,
            "entry_reference_index": 63,
            "exit_reference_index": 68,
            "entry_price": 10.0,
            "exit_price": 12.0,
            "signal_timestamp": candles[62].interval_end,
        },
        {
            "signal_index": 66,
            "entry_reference_index": 67,
            "exit_reference_index": 72,
            "entry_price": 10.0,
            "exit_price": 9.0,
            "signal_timestamp": candles[66].interval_end,
        },
    ]
    monkeypatch.setattr(experiment, "_candidate_signals_for_period", lambda _candles: iter(signals))

    result = experiment.run_breakout_zero_cost_period(candles, period_id="synthetic-overlap-check")

    assert [trade["setup_index"] for trade in result["completed_trades"]] == [60, 66]
    assert result["trades_count"] == 2
