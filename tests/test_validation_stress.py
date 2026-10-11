from tools.hsra.cost import CostModel
from tools.hsra.validation import HistoricalValidationStressRunner


def test_realistic_validation_stress_rejects_small_move_trades_under_conservative_costs():
    runner = HistoricalValidationStressRunner(
        cost_model=CostModel(
            maker_fee=0.001,
            taker_fee=0.0015,
            spread_bps=4.0,
            slippage_bps=2.0,
            latency_ms=150.0,
            min_order_eur=10.0,
        )
    )

    report = runner.run_signal_stress(
        symbol="BTC-EUR",
        entry_price=100.0,
        exit_price=100.1,
        notional=100.0,
        direction="long",
    )

    assert report["gross_pnl_eur"] > 0
    assert report["cost_drag_eur"] > 0
    assert report["net_pnl_eur"] < report["gross_pnl_eur"]
    assert report["passes_realistic_gate"] is False
    assert report["status"] == "reject_under_realistic_costs"


def test_realistic_validation_stress_allows_margin_when_move_exceeds_costs():
    runner = HistoricalValidationStressRunner(
        cost_model=CostModel(
            maker_fee=0.001,
            taker_fee=0.0015,
            spread_bps=4.0,
            slippage_bps=2.0,
            latency_ms=150.0,
            min_order_eur=10.0,
        )
    )

    report = runner.run_signal_stress(
        symbol="BTC-EUR",
        entry_price=100.0,
        exit_price=106.0,
        notional=100.0,
        direction="long",
    )

    assert report["gross_pnl_eur"] > 5.0
    assert report["net_pnl_eur"] > 0.0
    assert report["passes_realistic_gate"] is True
    assert report["status"] == "pass_under_realistic_costs"
