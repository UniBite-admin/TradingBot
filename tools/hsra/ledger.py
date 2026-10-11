from __future__ import annotations

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
    realized_pnl: float = 0.0
    total_fee: float = 0.0

    def record_fill(self, *, symbol: str, side: str, quantity: float, price: float, fee: float, trade_id: str) -> None:
        if side not in {"buy", "sell"}:
            raise ValueError("side must be 'buy' or 'sell'")

        record = LedgerTrade(symbol=symbol, side=side, quantity=quantity, price=price, fee=fee, trade_id=trade_id)
        self.trades.append(record)
        self.total_fee += fee

        if side == "buy":
            self.position_qty += quantity
        else:
            self.position_qty -= quantity

        if side == "sell" and self.position_qty >= 0:
            self.realized_pnl += quantity * price - fee

    def snapshot(self) -> dict:
        return {
            "position_qty": self.position_qty,
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
