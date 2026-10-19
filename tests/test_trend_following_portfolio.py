from __future__ import annotations

import pytest

from tools.trend_following.core import TrendStrategyInputError
from tools.trend_following.portfolio import (
    PortfolioState,
    marked_equity,
    rebalance_portfolio,
)


def test_buy_applies_adverse_slippage_and_fee_to_fill_notional():
    state = PortfolioState(cash_eur=100.0)
    updated, execution = rebalance_portfolio(
        state, 0.5, 100.0, fee_bps_per_side=25.0, slippage_bps_per_side=1.5
    )

    assert execution is not None
    assert execution.side == "buy"
    assert execution.btc_qty == pytest.approx(0.5)
    assert execution.fill_price_eur == pytest.approx(100.015)
    assert execution.fill_notional_eur == pytest.approx(50.0075)
    assert execution.fee_eur == pytest.approx(50.0075 * 0.0025)
    assert execution.slippage_eur == pytest.approx(0.0075)
    assert updated.cash_eur == pytest.approx(100 - execution.fill_notional_eur - execution.fee_eur)
    assert updated.btc_qty == pytest.approx(0.5)
    assert updated.fees_eur == pytest.approx(execution.fee_eur)
    assert updated.slippage_eur == pytest.approx(execution.slippage_eur)
    assert marked_equity(updated, 100.0) == pytest.approx(
        100.0 - execution.fee_eur - execution.slippage_eur
    )


def test_buy_is_clipped_to_available_cash_including_costs():
    updated, execution = rebalance_portfolio(
        PortfolioState(cash_eur=100.0),
        1.0,
        100.0,
        fee_bps_per_side=25.0,
        slippage_bps_per_side=1.5,
    )

    assert execution is not None
    assert execution.side == "buy"
    assert updated.cash_eur == pytest.approx(0.0, abs=1e-10)
    assert updated.btc_qty < 1.0
    assert updated.cash_eur >= 0.0


def test_sell_reduces_btc_and_adds_net_proceeds_to_cash():
    start = PortfolioState(cash_eur=49.86748125, btc_qty=0.5)
    updated, execution = rebalance_portfolio(
        start, 0.0, 110.0, fee_bps_per_side=25.0, slippage_bps_per_side=1.5
    )

    assert execution is not None
    assert execution.side == "sell"
    assert execution.btc_qty == pytest.approx(0.5)
    assert execution.fill_price_eur == pytest.approx(109.9835)
    assert execution.fee_eur == pytest.approx(execution.fill_notional_eur * 0.0025)
    assert execution.slippage_eur == pytest.approx(0.00825)
    assert updated.btc_qty == pytest.approx(0.0)
    assert updated.cash_eur == pytest.approx(
        start.cash_eur + execution.fill_notional_eur - execution.fee_eur
    )


def test_no_order_when_already_at_target():
    state = PortfolioState(cash_eur=50.0, btc_qty=0.5)
    updated, execution = rebalance_portfolio(state, 0.5, 100.0)
    assert updated == state
    assert execution is None


def test_invalid_target_exposure_is_rejected():
    with pytest.raises(TrendStrategyInputError, match="target_exposure"):
        rebalance_portfolio(PortfolioState(), 1.01, 100.0)


def test_fractional_btc_is_supported():
    updated, execution = rebalance_portfolio(
        PortfolioState(cash_eur=100.0), 0.1, 30000.0, fee_bps_per_side=0, slippage_bps_per_side=0
    )
    assert execution is not None
    assert execution.btc_qty == pytest.approx(100 / 30000 * 0.1)
    assert updated.btc_qty == pytest.approx(execution.btc_qty)
