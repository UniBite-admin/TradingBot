from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

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


def _status_reconciliation(signals: list[dict]) -> dict[str, int]:
    counts = {"candidate": 0, "rejected": 0, "unresolved": 0}
    for signal in signals:
        status = signal.get("status")
        if status == "candidate":
            counts["candidate"] += 1
        elif isinstance(status, str) and status.startswith("rejected_"):
            counts["rejected"] += 1
        elif status == "unclosed_at_segment_end":
            counts["unresolved"] += 1
    return counts


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


def test_stop_gap_uses_open_price_when_price_opens_below_stop():
    candles = _day_plus_signals()
    candles[289] = _candle(
        candles[289].interval_start,
        open_=97.0,
        high=98.0,
        low=96.0,
        close=97.2,
    )
    candles[290] = _candle(
        candles[290].interval_start,
        open_=93.0,
        high=96.0,
        low=92.0,
        close=94.0,
    )
    result = run_box_theory_segment(candles)

    assert result["summary"]["trades"] == 1
    trade = result["trades"][0]
    assert trade["exit_reason"] == "stop_gap"
    assert trade["exit_price"] == pytest.approx(93.0)
    assert trade["exit_price"] == pytest.approx(trade["entry_price"] - 4.0)


def test_target_gap_uses_target_price_when_price_opens_above_target():
    candles = _day_plus_signals()
    candles[289] = _candle(
        candles[289].interval_start,
        open_=97.0,
        high=98.0,
        low=96.0,
        close=97.2,
    )
    candles[290] = _candle(
        candles[290].interval_start,
        open_=101.0,
        high=110.0,
        low=99.0,
        close=102.0,
    )
    result = run_box_theory_segment(candles)

    assert result["summary"]["trades"] == 1
    trade = result["trades"][0]
    assert trade["exit_reason"] == "target_gap"
    assert trade["exit_price"] == pytest.approx(trade["target_price"])


def test_stop_wins_when_one_candle_touches_both_stop_and_target():
    candles = _day_plus_signals()
    candles[289] = _candle(
        candles[289].interval_start,
        open_=97.0,
        high=98.0,
        low=96.0,
        close=97.2,
    )
    candles[290] = _candle(
        candles[290].interval_start,
        open_=95.0,
        high=101.0,
        low=93.0,
        close=98.0,
    )
    result = run_box_theory_segment(candles)

    assert result["summary"]["trades"] == 1
    trade = result["trades"][0]
    assert trade["exit_reason"] == "stop"
    assert trade["exit_price"] < trade["target_price"]
    assert trade["exit_price"] == pytest.approx(trade["stop_price"])


def test_unresolved_open_position_is_marked_unclosed_and_excluded_from_trade_pnl():
    candles = _day_plus_signals()
    candles[289] = _candle(
        candles[289].interval_start,
        open_=97.0,
        high=98.0,
        low=96.0,
        close=97.2,
    )
    candles[290] = _candle(
        candles[290].interval_start,
        open_=97.5,
        high=98.5,
        low=96.5,
        close=97.8,
    )
    result = run_box_theory_segment(candles)

    assert result["summary"]["trades"] == 0
    assert result["summary"]["open_at_segment_end"] == 1
    assert len(result["signals"]) == 1
    assert result["signals"][0]["status"] == "unclosed_at_segment_end"
    assert result["summary"]["gross_pnl_eur"] == 0.0


def test_no_overlapping_positions_are_opened_within_one_contiguous_segment():
    candles = _day_plus_signals()
    candles[289] = _candle(candles[289].interval_start, open_=97, high=101, low=96, close=98)
    candles[290] = _candle(candles[290].interval_start, open_=97.5, high=102, low=96.5, close=99.5)
    result = run_box_theory_segment(candles)

    assert result["summary"]["trades"] == 1
    assert len(result["signals"]) == 1
    assert result["signals"][0]["status"] == "candidate"
    assert result["trades"][0]["exit_reason"] in {"stop", "target", "stop_gap", "target_gap"}


def test_noncontiguous_or_invalid_segments_reject_without_misleading_trades():
    candles = _day_plus_signals()
    candles.insert(200, _candle(datetime(2024, 1, 2, 0, 0, tzinfo=timezone.utc)))
    result = run_box_theory_segmented(candles)

    assert result["summary"]["status"] == "rejected_duplicate_timestamps"
    assert result["summary"]["trades"] == 0
    assert result["summary"]["signals"] == 0
    assert result["segment_count"] == 0


def test_signal_status_audit_counts_reconcile_with_implementation_status_transitions():
    result = run_box_theory_segment(_day_plus_signals())
    counts = _status_reconciliation(result["signals"])

    assert counts["candidate"] == result["summary"]["trades"]
    assert counts["candidate"] + counts["rejected"] + counts["unresolved"] == len(result["signals"])


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


def test_summary_cost_and_trade_pnl_match_individual_trade_records():
    result = run_box_theory_segment(_day_plus_signals())
    expected_gross = sum(trade["gross_pnl_eur"] for trade in result["trades"])
    assert result["summary"]["gross_pnl_eur"] == pytest.approx(expected_gross)
    assert result["summary"]["trades"] == len(result["trades"])
    for scenario_name, summary in result["summary"]["cost_scenarios"].items():
        if scenario_name == "gross_only":
            continue
        expected_cost = sum(trade["cost_scenarios"][scenario_name]["total_cost_eur"] for trade in result["trades"])
        assert summary["total_cost_eur"] == pytest.approx(expected_cost)
        expected_net = sum(trade["gross_pnl_eur"] - trade["cost_scenarios"][scenario_name]["total_cost_eur"] for trade in result["trades"])
        assert summary["net_pnl_eur"] == pytest.approx(expected_net)


def test_segmented_mode_rejects_invalid_interval_without_division_error():
    result = run_box_theory_segmented(
        _day_plus_signals(),
        config=BoxTheoryConfig(interval_minutes=0),
    )
    assert result["summary"]["status"] == "invalid_configuration"
