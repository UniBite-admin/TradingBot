from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CostModel:
    maker_fee: float = 0.001
    taker_fee: float = 0.0015
    spread_bps: float = 4.0
    slippage_bps: float = 2.0
    latency_ms: float = 150.0
    min_order_eur: float = 10.0

    def estimate_trade_cost(self, *, price: float, notional: float, side: str) -> dict:
        if price <= 0:
            raise ValueError("price must be positive")
        if notional <= 0:
            raise ValueError("notional must be positive")
        if side not in {"buy", "sell"}:
            raise ValueError("side must be 'buy' or 'sell'")

        fee_rate = self.maker_fee if side == "buy" else self.taker_fee
        fee_eur = notional * fee_rate
        spread_eur = notional * (self.spread_bps / 10000.0)
        slippage_eur = notional * (self.slippage_bps / 10000.0)
        latency_cost_eur = (self.latency_ms / 1000.0) * 0.15 * price
        total_cost_eur = fee_eur + spread_eur + slippage_eur + latency_cost_eur

        return {
            "fee_eur": fee_eur,
            "spread_eur": spread_eur,
            "slippage_eur": slippage_eur,
            "latency_cost_eur": latency_cost_eur,
            "total_cost_eur": total_cost_eur,
            "min_order_eur": self.min_order_eur,
            "notional": notional,
        }
