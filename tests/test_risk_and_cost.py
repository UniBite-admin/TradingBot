from tools.hsra.cost import CostModel
from tools.hsra.ledger import Ledger
from tools.hsra.risk import RiskEngine


def test_cost_model_estimates_realistic_trade_costs():
    model = CostModel(
        maker_fee=0.001,
        taker_fee=0.0015,
        spread_bps=4.0,
        slippage_bps=2.0,
        latency_ms=150,
        min_order_eur=10.0,
    )

    result = model.estimate_trade_cost(price=100.0, notional=100.0, side="buy")

    assert result["fee_eur"] > 0
    assert result["spread_eur"] > 0
    assert result["slippage_eur"] > 0
    assert result["latency_cost_eur"] > 0
    assert result["total_cost_eur"] > 0


def test_risk_engine_blocks_over_exposure_and_duplicate_symbol_orders():
    engine = RiskEngine(max_open_exposure=1000.0, max_position_per_symbol=0.5)

    decision1 = engine.evaluate(
        symbol="BTC-EUR",
        proposed_notional=700.0,
        current_positions={"BTC-EUR": 0.4},
        open_orders={"BTC-EUR": 0.0},
    )
    assert decision1["approved"] is True

    decision2 = engine.evaluate(
        symbol="BTC-EUR",
        proposed_notional=700.0,
        current_positions={"BTC-EUR": 0.5},
        open_orders={"BTC-EUR": 0.0},
    )
    assert decision2["approved"] is False
    assert decision2["reason"] == "position_limit"

    decision3 = engine.evaluate(
        symbol="BTC-EUR",
        proposed_notional=900.0,
        current_positions={"BTC-EUR": 0.1},
        open_orders={"BTC-EUR": 0.2},
    )
    assert decision3["approved"] is False
    assert decision3["reason"] == "pending_order_conflict"


def test_ledger_tracks_trade_history_and_realized_pnl():
    ledger = Ledger()

    ledger.record_fill(
        symbol="BTC-EUR",
        side="buy",
        quantity=0.5,
        price=100.0,
        fee=0.1,
        trade_id="t-1",
    )
    ledger.record_fill(
        symbol="BTC-EUR",
        side="sell",
        quantity=0.5,
        price=105.0,
        fee=0.12,
        trade_id="t-2",
    )

    assert ledger.position_qty == 0
    assert ledger.realized_pnl > 0
    assert ledger.total_fee == 0.22
    assert len(ledger.trades) == 2
