from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass
class LedgerTrade:
    symbol: str
    side: str
    quantity: float
    price: float
    fee: float
    trade_id: str


@dataclass
class Ledger:
    trades: list[LedgerTrade] = field(default_factory=list)
    position_qty: float = 0.0
    cost_basis: float = 0.0
    average_cost_basis: float = 0.0
    realized_pnl: float = 0.0
    total_fee: float = 0.0

    def _validate_fill(self, *, quantity: float, price: float, fee: float) -> None:
        if not math.isfinite(quantity) or quantity <= 0:
            raise ValueError("quantity must be a positive finite number")
        if not math.isfinite(price) or price <= 0:
            raise ValueError("price must be a positive finite number")
        if not math.isfinite(fee) or fee < 0:
            raise ValueError("fee must be a finite non-negative number")

    def record_fill(self, *, symbol: str, side: str, quantity: float, price: float, fee: float, trade_id: str) -> None:
        if side not in {"buy", "sell"}:
            raise ValueError("side must be 'buy' or 'sell'")

        self._validate_fill(quantity=quantity, price=price, fee=fee)

        if side == "sell" and quantity > self.position_qty:
            raise ValueError("sell quantity exceeds available position")

        record = LedgerTrade(symbol=symbol, side=side, quantity=quantity, price=price, fee=fee, trade_id=trade_id)

        if side == "buy":
            self.cost_basis += quantity * price + fee
            self.position_qty += quantity
            self.total_fee += fee
            self.trades.append(record)
            self.average_cost_basis = self.cost_basis / self.position_qty if self.position_qty > 0 else 0.0
            return

        sold_cost_basis = self.average_cost_basis * quantity if self.position_qty > 0 else 0.0
        proceeds_after_exit_fee = quantity * price - fee
        self.realized_pnl += proceeds_after_exit_fee - sold_cost_basis

        self.cost_basis -= sold_cost_basis
        self.position_qty -= quantity
        self.total_fee += fee
        self.trades.append(record)

        self.average_cost_basis = self.cost_basis / self.position_qty if self.position_qty > 0 else 0.0

    def snapshot(self) -> dict:
        return {
            "position_qty": self.position_qty,
            "cost_basis": self.cost_basis,
            "average_cost_basis": self.average_cost_basis,
            "realized_pnl": self.realized_pnl,
            "total_fee": self.total_fee,
            "trades": [
                {
                    "symbol": trade.symbol,
                    "side": trade.side,
                    "quantity": trade.quantity,
                    "price": trade.price,
                    "fee": trade.fee,
                    "trade_id": trade.trade_id,
                }
                for trade in self.trades
            ],
        }
