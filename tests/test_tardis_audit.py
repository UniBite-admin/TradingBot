import csv
import gzip
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from data.tmp_tardis.audit_tardis_dataset import _raw_input_filename_for_date, audit_canonical_dataset, audit_raw_file
from tools.hsra.reader import compute_sha256


def _write_gzip_csv(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerows(rows)


def test_raw_quote_audit_flags_invalid_and_duplicate_rows(tmp_path):
    quote = tmp_path / "quotes.csv.gz"
    rows = [
        ["exchange", "symbol", "timestamp", "local_timestamp", "ask_amount", "ask_price", "bid_price", "bid_amount"],
        ["binance-jersey", "BTCEUR", "1000", "1000", "0.1", "101", "100", "0.2"],
        ["binance-jersey", "BTCEUR", "2000", "2000", "0.2", "103", "99", "0.3"],
        ["binance-jersey", "BTCEUR", "2000", "2000", "0.2", "103", "99", "0.3"],
        ["binance-jersey", "BTCEUR", "3000", "3000", "0.2", "98", "100", "0.4"],
    ]
    _write_gzip_csv(quote, rows)

    result = audit_raw_file(quote, "quote")

    assert result["status"] == "FAIL"
    assert result["quotes_with_bid_ge_ask"] == 1
    assert result["duplicate_rows"] == 1
    assert result["record_count"] == 4


def test_empty_file_and_missing_input_are_failed(tmp_path):
    empty = tmp_path / "empty.csv.gz"
    empty.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(empty, "wt", encoding="utf-8", newline="") as fh:
        fh.write("")

    assert audit_raw_file(empty, "quote")["status"] == "FAIL"
    assert audit_raw_file(tmp_path / "missing.csv.gz", "trade")["status"] == "FAIL"


def test_raw_filename_convention_handles_legacy_2019_and_2020_dates():
    assert _raw_input_filename_for_date("20191201", "quote") == "BTCEUR_quotes_20191201.csv.gz"
    assert _raw_input_filename_for_date("20191201", "trade") == "BTCEUR_trades_20191201.csv.gz"
    assert _raw_input_filename_for_date("20200101", "quote") == "BTCEUR_quotes_2020_01_01.csv.gz"
    assert _raw_input_filename_for_date("20200101", "trade") == "BTCEUR_trades_2020_01_01.csv.gz"


def test_canonical_dataset_accepts_quote_derived_ticker_contract(tmp_path):
    date = "20200101"
    raw_dir = tmp_path / "data" / "tmp_tardis"
    raw_dir.mkdir(parents=True, exist_ok=True)
    quote_rows = [
        ["exchange", "symbol", "timestamp", "local_timestamp", "ask_amount", "ask_price", "bid_price", "bid_amount"],
        ["binance-jersey", "BTCEUR", "1577836800000000", "1577836800000000", "0.5", "101.0", "100.0", "0.5"],
        ["binance-jersey", "BTCEUR", "1577836860000000", "1577836860000000", "0.5", "102.0", "101.0", "0.5"],
    ]
    trade_rows = [
        ["exchange", "symbol", "timestamp", "local_timestamp", "id", "side", "price", "amount"],
        ["binance-jersey", "BTCEUR", "1577836799000000", "1577836799000000", "t1", "buy", "100.5", "0.5"],
    ]
    quote_path = raw_dir / _raw_input_filename_for_date(date, "quote")
    trade_path = raw_dir / _raw_input_filename_for_date(date, "trade")
    _write_gzip_csv(quote_path, quote_rows)
    _write_gzip_csv(trade_path, trade_rows)

    canonical_dir = tmp_path / "data" / "canonical" / f"tardis_btc_eur_{date}"
    canonical_dir.mkdir(parents=True, exist_ok=True)
    with (canonical_dir / "canonical_events.jsonl").open("w", encoding="utf-8") as fh:
        fh.write(json.dumps({"event_time_utc": "2020-01-01T00:00:00+00:00", "event_type": "ticker", "market": "BTC-EUR", "bid": 100.0, "ask": 101.0, "last": 100.5}) + "\n")
        fh.write(json.dumps({"event_time_utc": "2020-01-01T00:01:00+00:00", "event_type": "ticker", "market": "BTC-EUR", "bid": 101.0, "ask": 102.0, "last": 100.5}) + "\n")
    with (canonical_dir / "provenance_sidecar.jsonl").open("w", encoding="utf-8") as fh:
        fh.write(json.dumps({"canonical_index": 0, "source_quote_id": f"{_raw_input_filename_for_date(date, 'quote')}:1", "source_trade_id": "t1", "source_trade_ts": "2020-01-01T00:00:00+00:00"}) + "\n")
        fh.write(json.dumps({"canonical_index": 1, "source_quote_id": f"{_raw_input_filename_for_date(date, 'quote')}:2", "source_trade_id": "t1", "source_trade_ts": "2020-01-01T00:00:00+00:00"}) + "\n")

    metadata = {
        "dataset_status": "CANONICALIZED",
        "completeness_status": "COMPLETE",
        "input_quote_count": 2,
        "input_trade_count": 1,
        "quotes_path_sha256": compute_sha256(quote_path),
        "trades_path_sha256": compute_sha256(trade_path),
        "emitted_canonical_count": 2,
        "status": "CANONICALIZED",
    }
    (canonical_dir / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")

    result = audit_canonical_dataset(canonical_dir, tmp_path)

    assert result["status"] == "PASS"
    assert result["sha_matches"]["quotes_path_sha256"] is True
    assert result["event_counts"] == {"ticker": 2}
    assert result["total_events"] == 2


def test_canonical_dataset_flags_decompressed_hash_mismatch(tmp_path):
    date = "20200102"
    raw_dir = tmp_path / "data" / "tmp_tardis"
    raw_dir.mkdir(parents=True, exist_ok=True)
    quote_path = raw_dir / _raw_input_filename_for_date(date, "quote")
    trade_path = raw_dir / _raw_input_filename_for_date(date, "trade")
    _write_gzip_csv(quote_path, [
        ["exchange", "symbol", "timestamp", "local_timestamp", "ask_amount", "ask_price", "bid_price", "bid_amount"],
        ["binance-jersey", "BTCEUR", "1577836800000000", "1577836800000000", "0.5", "101.0", "100.0", "0.5"],
    ])
    _write_gzip_csv(trade_path, [
        ["exchange", "symbol", "timestamp", "local_timestamp", "id", "side", "price", "amount"],
        ["binance-jersey", "BTCEUR", "1577836799000000", "1577836799000000", "t1", "buy", "100.5", "0.5"],
    ])

    canonical_dir = tmp_path / "data" / "canonical" / f"tardis_btc_eur_{date}"
    canonical_dir.mkdir(parents=True, exist_ok=True)
    with (canonical_dir / "canonical_events.jsonl").open("w", encoding="utf-8") as fh:
        fh.write(json.dumps({"event_time_utc": "2020-01-02T00:00:00+00:00", "event_type": "ticker", "market": "BTC-EUR", "bid": 100.0, "ask": 101.0, "last": 100.5}) + "\n")
    with (canonical_dir / "provenance_sidecar.jsonl").open("w", encoding="utf-8") as fh:
        fh.write(json.dumps({"canonical_index": 0, "source_quote_id": f"{_raw_input_filename_for_date(date, 'quote')}:1", "source_trade_id": "t1"}) + "\n")
    (canonical_dir / "metadata.json").write_text(json.dumps({
        "dataset_status": "CANONICALIZED",
        "completeness_status": "COMPLETE",
        "input_quote_count": 1,
        "input_trade_count": 1,
        "quotes_path_sha256": "not-the-real-sha",
        "trades_path_sha256": compute_sha256(trade_path),
        "emitted_canonical_count": 1,
        "status": "CANONICALIZED",
    }), encoding="utf-8")

    result = audit_canonical_dataset(canonical_dir, tmp_path)

    assert result["status"] == "FAIL"
    assert "checksum_mismatch_quotes" in result["reason"]
