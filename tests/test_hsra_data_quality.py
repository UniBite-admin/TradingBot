from datetime import datetime
from pathlib import Path

import pytest

from tools.hsra.merger import HSRAError, canonicalize_window


def _write_csv(path: Path, header: str, rows: list[str]):
    with path.open("w", encoding="utf-8") as fh:
        fh.write(header + "\n")
        for row in rows:
            fh.write(row + "\n")


def test_regression_empty_interval_is_rejected(tmp_path):
    quotes = tmp_path / "quotes.csv"
    trades = tmp_path / "trades.csv"
    _write_csv(quotes, "timestamp,market,bid,ask,quote_id", [
        "2019-12-01T00:10:00Z,BTC-EUR,6800.0,6810.0,q1",
    ])
    _write_csv(trades, "timestamp,market,price,trade_id", [
        "2019-12-01T02:10:00Z,BTC-EUR,6820.0,t1",
    ])

    start = datetime.fromisoformat("2019-12-01T00:00:00+00:00")
    end = datetime.fromisoformat("2019-12-01T00:20:00+00:00")

    with pytest.raises(HSRAError) as exc:
        canonicalize_window(quotes, trades, requested_start=start, requested_end=end)

    assert "no_trades_in_requested_window" in str(exc.value)


def test_regression_pre_first_trade_quotes_are_rejected(tmp_path):
    quotes = tmp_path / "quotes.csv"
    trades = tmp_path / "trades.csv"
    _write_csv(quotes, "timestamp,market,bid,ask,quote_id", [
        "2019-12-01T00:00:00Z,BTC-EUR,6700.0,6710.0,q1",
        "2019-12-01T00:05:00Z,BTC-EUR,6710.0,6720.0,q2",
    ])
    _write_csv(trades, "timestamp,market,price,trade_id", [
        "2019-12-01T00:10:00Z,BTC-EUR,6730.0,t1",
    ])

    start = datetime.fromisoformat("2019-12-01T00:00:00+00:00")
    end = datetime.fromisoformat("2019-12-01T00:20:00+00:00")

    with pytest.raises(HSRAError) as exc:
        canonicalize_window(quotes, trades, requested_start=start, requested_end=end)

    assert "pre_first_trade_quotes_present" in str(exc.value)


def test_regression_lookahead_is_rejected(tmp_path):
    quotes = tmp_path / "quotes.csv"
    trades = tmp_path / "trades.csv"
    _write_csv(quotes, "timestamp,market,bid,ask,quote_id", [
        "2019-12-01T01:00:00Z,BTC-EUR,6800.0,6810.0,q1",
    ])
    _write_csv(trades, "timestamp,market,price,trade_id", [
        "2019-12-01T01:00:01Z,BTC-EUR,6801.0,t1",
    ])

    start = datetime.fromisoformat("2019-12-01T01:00:00+00:00")
    end = datetime.fromisoformat("2019-12-01T01:05:00+00:00")

    with pytest.raises(HSRAError):
        canonicalize_window(quotes, trades, requested_start=start, requested_end=end)


def test_regression_missing_file_is_rejected(tmp_path):
    quotes = tmp_path / "quotes.csv"
    trades = tmp_path / "missing.csv"
    _write_csv(quotes, "timestamp,market,bid,ask,quote_id", [
        "2019-12-01T01:00:00Z,BTC-EUR,6800.0,6810.0,q1",
    ])

    start = datetime.fromisoformat("2019-12-01T01:00:00+00:00")
    end = datetime.fromisoformat("2019-12-01T01:05:00+00:00")

    with pytest.raises(HSRAError) as exc:
        canonicalize_window(quotes, trades, requested_start=start, requested_end=end)

    assert "missing_required_source_file" in str(exc.value)
