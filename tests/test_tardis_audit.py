import csv
import gzip
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from data.tmp_tardis.audit_tardis_dataset import audit_canonical_dataset, audit_raw_file


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


def test_canonical_dataset_flags_hash_mismatch_and_quote_only_output(tmp_path):
    date = "20200101"
    raw_dir = tmp_path / "data" / "tmp_tardis"
    raw_dir.mkdir(parents=True, exist_ok=True)
    quote_path = raw_dir / f"BTCEUR_quotes_{date}.csv.gz"
    trade_path = raw_dir / f"BTCEUR_trades_{date}.csv.gz"
    quote_path.write_bytes(b"placeholder")
    trade_path.write_bytes(b"placeholder")

    canonical_dir = tmp_path / "data" / "canonical" / f"tardis_btc_eur_{date}"
    canonical_dir.mkdir(parents=True, exist_ok=True)
    with (canonical_dir / "canonical_events.jsonl").open("w", encoding="utf-8") as fh:
        fh.write(json.dumps({"event_time_utc": "2020-01-01T00:00:00Z", "event_type": "ticker", "market": "BTC-EUR", "bid": 100.0, "ask": 101.0, "last": 100.5}) + "\n")
        fh.write(json.dumps({"event_time_utc": "2020-01-01T00:01:00Z", "event_type": "ticker", "market": "BTC-EUR", "bid": 101.0, "ask": 102.0, "last": 101.5}) + "\n")
    with (canonical_dir / "provenance_sidecar.jsonl").open("w", encoding="utf-8") as fh:
        fh.write(json.dumps({"canonical_index": 0, "source_quote_id": "BTCEUR_quotes_20200101.csv.gz:1", "source_trade_id": "1"}) + "\n")
        fh.write(json.dumps({"canonical_index": 1, "source_quote_id": "BTCEUR_quotes_20200101.csv.gz:2", "source_trade_id": "2"}) + "\n")
    (canonical_dir / "metadata.json").write_text(json.dumps({
        "dataset_status": "CANONICALIZED",
        "completeness_status": "COMPLETE",
        "input_quote_count": 2,
        "input_trade_count": 1,
        "quotes_path_sha256": "bad-hash",
        "trades_path_sha256": "bad-hash",
        "emitted_canonical_count": 2,
        "status": "CANONICALIZED",
    }), encoding="utf-8")

    result = audit_canonical_dataset(canonical_dir, tmp_path)

    assert result["status"] == "FAIL"
    assert "checksum_mismatch_quotes" in result["reason"]
    assert "quote_only_canonical_output" in result["reason"]
