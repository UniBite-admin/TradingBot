from __future__ import annotations

from datetime import datetime, timedelta, timezone

from tools.hsra.box_theory import BoxTheoryConfig, default_cost_scenarios, run_box_theory_segment, run_box_theory_segmented
from tools.hsra.ohlcv import OHLCVCandle


def _candle(start: datetime, *, open_: float = 100.0, high: float = 101.0, low: float = 99.0, close: float = 100.0) -> OHLCVCandle:
    return OHLCVCandle(
        interval_start=start,
        interval_end=start + timedelta(minutes=5),
        open=open_,
        high=high,
        low=low,
        close=close,
        volume=1.0,
        trade_count=1,
    )


def _day_plus_signals() -> list[OHLCVCandle]:
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    candles = []
    for index in range(288):
        bar_start = start + timedelta(minutes=5 * index)
        candles.append(_candle(bar_start))
    candles[0] = _candle(start, open_=100, high=101, low=90, close=100)
    candles[1] = _candle(start + timedelta(minutes=5), open_=100, high=110, low=99, close=100)
    next_day = start + timedelta(days=1)
    candles.append(_candle(next_day, open_=96, high=98, low=94, close=96))
    candles.append(_candle(next_day + timedelta(minutes=5), open_=97, high=101, low=96, close=99))
    candles.append(_candle(next_day + timedelta(minutes=10), open_=99, high=100, low=98, close=99))
    return candles


def test_box_uses_previous_complete_utc_day_and_next_open_entry():
    result = run_box_theory_segment(_day_plus_signals())

    assert result["summary"]["signals"] == 1
    assert result["summary"]["trades"] == 1
    signal = result["signals"][0]
    trade = result["trades"][0]
    assert signal["box_date_utc"] == "2024-01-01"
    assert signal["box_low"] == 90
    assert signal["box_high"] == 110
    assert signal["box_mid"] == 100
    assert signal["zone_high"] == 95
    assert signal["entry_price"] == 97
    assert trade["exit_reason"] == "target"
    assert trade["exit_price"] == 100
    scenario = result["summary"]["cost_scenarios"]["illustrative_taker_spread_slippage"]
    assert scenario["net_pnl_eur"] < trade["gross_pnl_eur"]
    assert trade["cost_scenarios"]["illustrative_taker_spread_slippage"]["total_cost_eur"] > 0


def test_incomplete_previous_day_cannot_form_a_box():
    candles = _day_plus_signals()
    del candles[100]
    result = run_box_theory_segmented(candles)

    assert result["summary"]["signals"] == 0
    assert result["summary"]["trades"] == 0


def test_stop_wins_when_one_candle_touches_both_stop_and_target():
    candles = _day_plus_signals()
    candles[289] = _candle(
        candles[289].interval_start,
        open_=97,
        high=101,
        low=93,
        close=99,
    )
    result = run_box_theory_segment(candles)

    assert result["summary"]["trades"] == 1
    assert result["trades"][0]["exit_reason"] == "stop"
    assert result["trades"][0]["exit_price"] < result["trades"][0]["target_price"]


def test_segmented_mode_rejects_duplicate_timestamps():
    candles = _day_plus_signals()
    candles.insert(200, _candle(datetime(2024, 1, 1, 16, 40, tzinfo=timezone.utc)))
    result = run_box_theory_segmented(candles)

    assert result["summary"]["status"] == "rejected_duplicate_timestamps"
    assert result["summary"]["trades"] == 0


def test_invalid_configuration_is_rejected():
    result = run_box_theory_segment(
        _day_plus_signals(),
        config=BoxTheoryConfig(zone_fraction=0.5),
    )

    assert result["summary"]["status"] == "invalid_configuration"
    assert result["summary"]["trades"] == 0


def test_latency_is_unpriced_and_scenarios_are_explicit():
    result = run_box_theory_segment(_day_plus_signals())
    assert result["latency_cost"]["status"] == "not_priced"
    assert "gross_only" in result["summary"]["cost_scenarios"]
    assert result["summary"]["cost_scenarios"]["gross_only"]["total_cost_eur"] == 0
    assert result["cost_scenario_definitions"][1]["status"] == "illustrative_unverified_sensitivity_case"


def test_cost_scenario_arithmetic_uses_both_turnover_legs():
    scenarios = default_cost_scenarios(taker_fee_rate=0.01, spread_bps=10, slippage_bps=5)
    result = run_box_theory_segment(_day_plus_signals(), cost_scenarios=scenarios)
    trade = result["trades"][0]
    expected_turnover = trade["entry_notional_eur"] + trade["exit_notional_eur"]
    cost = trade["cost_scenarios"]["illustrative_taker_spread_slippage"]
    assert abs(cost["fees_eur"] - expected_turnover * 0.01) < 1e-10
    assert abs(cost["spread_cost_eur"] - expected_turnover * 10 / 10000) < 1e-10
    assert abs(cost["slippage_cost_eur"] - expected_turnover * 5 / 10000) < 1e-10
    assert abs(cost["total_cost_eur"] - cost["fees_eur"] - cost["spread_cost_eur"] - cost["slippage_cost_eur"]) < 1e-10


def test_segmented_mode_rejects_invalid_interval_without_division_error():
    result = run_box_theory_segmented(
        _day_plus_signals(),
        config=BoxTheoryConfig(interval_minutes=0),
    )
    assert result["summary"]["status"] == "invalid_configuration"
