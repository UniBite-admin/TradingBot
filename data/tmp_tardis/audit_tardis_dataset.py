#!/usr/bin/env python3
"""Read-only audit of the committed Tardis BTCEUR raw and canonical data.

This script intentionally does not rewrite or move raw data. It streams files and
writes a separate machine-readable report under data/tmp_tardis/audit_reports/.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.hsra.reader import compute_sha256


DEFAULT_ROOT = ROOT


def sha256_file(path: Path) -> str:
    return compute_sha256(path)


def csv_reader_for(path: Path):
    opener = gzip.open if path.suffix == ".gz" else open
    return opener(path, "rt", encoding="utf-8", newline="")


def parse_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return int(text)
    except ValueError:
        return None


def parse_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def record_status(pass_fail: bool, status: str = "PASS") -> str:
    if not pass_fail:
        return "FAIL"
    return status


def audit_raw_file(path: Path, kind: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "path": str(path),
        "kind": kind,
        "exists": path.exists(),
        "is_non_empty": False,
        "format": "csv.gz" if path.suffix == ".gz" else "csv",
        "status": "NOT_VERIFIABLE",
        "reason": "",
        "record_count": 0,
        "header": [],
        "min_timestamp": None,
        "max_timestamp": None,
        "invalid_rows": 0,
        "invalid_timestamp_rows": 0,
        "missing_required_fields": 0,
        "invalid_price_rows": 0,
        "invalid_quantity_rows": 0,
        "duplicate_rows": 0,
        "quotes_with_bid_ge_ask": 0,
        "size_bytes": int(path.stat().st_size) if path.exists() else 0,
        "sha256": sha256_file(path) if path.exists() else None,
    }

    if not path.exists():
        result["status"] = "FAIL"
        result["reason"] = "missing_input_file"
        return result

    if path.stat().st_size == 0:
        result["status"] = "FAIL"
        result["reason"] = "empty_file"
        return result

    result["is_non_empty"] = True
    seen_rows: set = set()
    min_ts: Optional[int] = None
    max_ts: Optional[int] = None

    try:
        with csv_reader_for(path) as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames is None:
                result["status"] = "FAIL"
                result["reason"] = "missing_header"
                return result
            result["header"] = reader.fieldnames

            required_fields = {
                "quote": {"timestamp", "local_timestamp", "bid_price", "ask_price", "bid_amount", "ask_amount"},
                "trade": {"timestamp", "local_timestamp", "price", "amount"},
            }.get(kind, {"timestamp"})

            for row in reader:
                if row is None:
                    continue
                result["record_count"] += 1
                row_key = tuple((k, row.get(k)) for k in row.keys())
                if row_key in seen_rows:
                    result["duplicate_rows"] += 1
                else:
                    seen_rows.add(row_key)

                ts_value = row.get("timestamp")
                ts_int = parse_int(ts_value)
                if ts_int is None:
                    result["invalid_timestamp_rows"] += 1
                    result["invalid_rows"] += 1
                else:
                    min_ts = ts_int if min_ts is None else min(min_ts, ts_int)
                    max_ts = ts_int if max_ts is None else max(max_ts, ts_int)

                missing = [field for field in sorted(required_fields) if row.get(field) in (None, "")]
                if missing:
                    result["missing_required_fields"] += 1
                    result["invalid_rows"] += 1

                if kind == "quote":
                    bid = parse_float(row.get("bid_price", row.get("bid")))
                    ask = parse_float(row.get("ask_price", row.get("ask")))
                    if bid is None or ask is None:
                        result["invalid_price_rows"] += 1
                        result["invalid_rows"] += 1
                    elif bid >= ask:
                        result["quotes_with_bid_ge_ask"] += 1
                        result["invalid_price_rows"] += 1
                        result["invalid_rows"] += 1

                    qty_bid = parse_float(row.get("bid_amount", row.get("bid_qty")))
                    qty_ask = parse_float(row.get("ask_amount", row.get("ask_qty")))
                    if qty_bid is None or qty_ask is None:
                        result["invalid_quantity_rows"] += 1
                        result["invalid_rows"] += 1

                if kind == "trade":
                    price = parse_float(row.get("price"))
                    qty = parse_float(row.get("amount"))
                    if price is None or qty is None:
                        result["invalid_price_rows"] += 1
                        result["invalid_rows"] += 1
                    elif price <= 0 or qty <= 0:
                        result["invalid_price_rows"] += 1
                        result["invalid_rows"] += 1

        result["min_timestamp"] = min_ts
        result["max_timestamp"] = max_ts
    except Exception as exc:  # pragma: no cover - conservative failure branch
        result["status"] = "FAIL"
        result["reason"] = f"read_error:{type(exc).__name__}:{exc}"
        return result

    if result["record_count"] == 0:
        result["status"] = "FAIL"
        result["reason"] = "zero_records"
        return result

    result["status"] = "PASS"
    result["reason"] = "streamed_and_validated"
    if result["invalid_rows"]:
        result["status"] = "FAIL"
        result["reason"] = "invalid_rows_detected"
    elif result["duplicate_rows"]:
        result["status"] = "FAIL"
        result["reason"] = "duplicate_rows_detected"
    elif kind == "quote" and result["quotes_with_bid_ge_ask"]:
        result["status"] = "FAIL"
        result["reason"] = "bid_ge_ask_detected"

    return result


def _collect_raw_trade_ids(path: Path) -> set[str]:
    ids: set[str] = set()
    if not path.exists():
        return ids
    try:
        with csv_reader_for(path) as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                if row is None:
                    continue
                for key in ("trade_id", "id"):
                    value = row.get(key)
                    if value not in (None, ""):
                        ids.add(str(value))
    except Exception:
        return ids
    return ids


def _raw_input_filename_for_date(date_token: str, kind: str) -> str:
    file_kind = "quotes" if kind == "quote" else "trades"
    if len(date_token) == 8 and date_token.isdigit():
        normalized = date_token if date_token == "20191201" else f"{date_token[:4]}_{date_token[4:6]}_{date_token[6:8]}"
    else:
        normalized = date_token
    return f"BTCEUR_{file_kind}_{normalized}.csv.gz"


def audit_canonical_dataset(canonical_dir: Path, raw_root: Path) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "path": str(canonical_dir),
        "exists": canonical_dir.exists(),
        "status": "NOT_VERIFIABLE",
        "reason": "",
        "dataset_dir": canonical_dir.name,
        "metadata": {},
        "event_counts": {},
        "total_events": 0,
        "unique_source_quote_ids": 0,
        "unique_source_trade_ids": 0,
        "sha_matches": {
            "quotes_path_sha256": False,
            "trades_path_sha256": False,
        },
        "quote_file_exists": False,
        "trade_file_exists": False,
        "metadata_files_present": False,
        "provenance_present": False,
        "trade_events_present": False,
        "missing_raw_input": False,
    }

    metadata_path = canonical_dir / "metadata.json"
    if not canonical_dir.exists():
        result["status"] = "FAIL"
        result["reason"] = "missing_canonical_directory"
        return result

    if not metadata_path.exists():
        result["status"] = "FAIL"
        result["reason"] = "missing_metadata_json"
        return result

    try:
        result["metadata"] = json.loads(metadata_path.read_text(encoding="utf-8"))
        result["metadata_files_present"] = True
    except Exception as exc:
        result["status"] = "FAIL"
        result["reason"] = f"invalid_metadata_json:{type(exc).__name__}:{exc}"
        return result

    date_token = canonical_dir.name.replace("tardis_btc_eur_", "")
    quote_path = raw_root / "data" / "tmp_tardis" / _raw_input_filename_for_date(date_token, "quote")
    trade_path = raw_root / "data" / "tmp_tardis" / _raw_input_filename_for_date(date_token, "trade")
    result["quote_file_exists"] = quote_path.exists()
    result["trade_file_exists"] = trade_path.exists()

    if quote_path.exists():
        actual_hash = sha256_file(quote_path)
        expected_hash = result["metadata"].get("quotes_path_sha256")
        result["sha_matches"]["quotes_path_sha256"] = expected_hash == actual_hash
    if trade_path.exists():
        actual_hash = sha256_file(trade_path)
        expected_hash = result["metadata"].get("trades_path_sha256")
        result["sha_matches"]["trades_path_sha256"] = expected_hash == actual_hash

    events_path = canonical_dir / "canonical_events.jsonl"
    sidecar_path = canonical_dir / "provenance_sidecar.jsonl"
    result["provenance_present"] = sidecar_path.exists()

    if events_path.exists():
        counts: Counter = Counter()
        with events_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                result["total_events"] += 1
                event_type = obj.get("event_type", "unknown")
                counts[event_type] += 1
        result["event_counts"] = dict(sorted(counts.items()))
        result["trade_events_present"] = any(k == "trade" for k in counts)

    raw_trade_ids: set[str] = set()
    if trade_path.exists():
        raw_trade_ids = _collect_raw_trade_ids(trade_path)

    if sidecar_path.exists():
        quote_ids: set = set()
        trade_ids: set = set()
        with sidecar_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if obj.get("source_quote_id") is not None:
                    quote_ids.add(str(obj["source_quote_id"]))
                if obj.get("source_trade_id") is not None:
                    trade_ids.add(str(obj["source_trade_id"]))
        result["unique_source_quote_ids"] = len(quote_ids)
        result["unique_source_trade_ids"] = len(trade_ids)

    input_quote_count = int(result["metadata"].get("input_quote_count") or 0)
    input_trade_count = int(result["metadata"].get("input_trade_count") or 0)
    emitted_count = int(result["metadata"].get("emitted_canonical_count") or 0)
    event_count_total = sum(result["event_counts"].values())
    provenance_trade_ids = set()
    if sidecar_path.exists():
        with sidecar_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                trade_id = obj.get("source_trade_id")
                if trade_id not in (None, ""):
                    provenance_trade_ids.add(str(trade_id))

    status = "PASS"
    reasons: List[str] = []

    if not quote_path.exists() or not trade_path.exists():
        status = "FAIL"
        reasons.append("missing_raw_input")
    if quote_path.exists() and not result["sha_matches"]["quotes_path_sha256"]:
        status = "FAIL"
        reasons.append("checksum_mismatch_quotes")
    if trade_path.exists() and "trades_path_sha256" in result["metadata"] and not result["sha_matches"]["trades_path_sha256"]:
        status = "FAIL"
        reasons.append("checksum_mismatch_trades")
    if result["total_events"] != emitted_count:
        status = "FAIL"
        reasons.append("event_count_mismatch")
    if input_quote_count and event_count_total != input_quote_count:
        status = "FAIL"
        reasons.append("canonical_quote_count_not_equal_to_raw_quotes")
    if sidecar_path.exists() and input_quote_count and result["unique_source_quote_ids"] != event_count_total:
        status = "FAIL"
        reasons.append("provenance_quote_count_mismatch")
    if sidecar_path.exists() and raw_trade_ids and provenance_trade_ids and not provenance_trade_ids.issubset(raw_trade_ids):
        status = "FAIL"
        reasons.append("provenance_trade_ids_missing_from_raw")
    if input_trade_count and not result["trade_events_present"] and "source_trade_id" in result["metadata"]:
        status = "FAIL"
        reasons.append("trade_reference_missing_from_contract")
    if input_trade_count and not result["trade_events_present"] and not sidecar_path.exists():
        status = "FAIL"
        reasons.append("trade_reference_missing_from_provenance")

    result["status"] = status
    result["reason"] = ";".join(reasons) if reasons else "coherent_metadata_and_event_stream"
    return result


def audit_validation_metadata(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"path": str(path), "status": "FAIL", "reason": "missing_validation_metadata"}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"path": str(path), "status": "FAIL", "reason": f"invalid_json:{type(exc).__name__}:{exc}"}

    dataset_status = str(data.get("dataset_status", "UNKNOWN"))
    completeness = str(data.get("completeness_status", "UNKNOWN"))
    reason = str(data.get("reason", ""))

    return {
        "path": str(path),
        "dataset_status": dataset_status,
        "completeness_status": completeness,
        "reason": reason,
        "input_quote_count": data.get("input_quote_count"),
        "input_trade_count": data.get("input_trade_count"),
        "status": dataset_status,
    }


def audit_repo(root: Path) -> Dict[str, Any]:
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "raw_files": [],
        "canonical_files": [],
        "validation_metadata": [],
        "findings": [],
    }

    raw_root = root / "data" / "tmp_tardis"
    for path in sorted(raw_root.glob("BTCEUR_*.csv*")):
        kind = "quote" if "quotes" in path.name else "trade"
        report["raw_files"].append(audit_raw_file(path, kind))

    canonical_root = root / "data" / "canonical"
    for path in sorted(canonical_root.glob("tardis_btc_eur_*")):
        if path.is_dir():
            report["canonical_files"].append(audit_canonical_dataset(path, root))

    for path in sorted(raw_root.glob("**/metadata.json")):
        if path.parent.name in {"hsra_validation", "hsra_validation_full_day"}:
            report["validation_metadata"].append(audit_validation_metadata(path))

    # High-level findings written as explicit pass / fail / not verifiable checks.
    for item in report["raw_files"]:
        if item["status"] == "FAIL":
            report["findings"].append({"asset": item["path"], "status": "FAIL", "reason": item["reason"]})
        elif item["status"] == "PASS":
            report["findings"].append({"asset": item["path"], "status": "PASS", "reason": item["reason"]})

    for item in report["canonical_files"]:
        if item["status"] == "FAIL":
            report["findings"].append({"asset": item["path"], "status": "FAIL", "reason": item["reason"]})
        elif item["status"] == "PASS":
            report["findings"].append({"asset": item["path"], "status": "PASS", "reason": item["reason"]})

    return report


def write_report(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit commited Tardis BTCEUR raw and canonical data.")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to audit.")
    parser.add_argument("--output", type=Path, default=None, help="Path for JSON audit report output.")
    args = parser.parse_args()

    report = audit_repo(args.root)
    output_path = args.output or args.root / "data" / "tmp_tardis" / "audit_reports" / f"tardis_dataset_audit_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    write_report(report, output_path)

    print(f"AUDIT_REPORT={output_path}")
    print("=" * 70)
    for entry in report["raw_files"]:
        print(f"{entry['status']:5} {entry['kind']:<5} {entry['path']} rows={entry['record_count']} min_ts={entry['min_timestamp']} max_ts={entry['max_timestamp']} reason={entry['reason']}")
    for entry in report["canonical_files"]:
        print(f"{entry['status']:5} CANON {entry['dataset_dir']} event_counts={entry['event_counts']} reason={entry['reason']}")
    for entry in report["validation_metadata"]:
        print(f"{entry['status']:5} VALID {entry['path']} dataset_status={entry['dataset_status']} completeness={entry.get('completeness_status')} reason={entry.get('reason')}")


if __name__ == "__main__":
    main()
