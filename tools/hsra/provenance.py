from __future__ import annotations

import hashlib
import json
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_DATA_ROOT = _ROOT / "data" / "tmp_tardis"
_OUTPUT_PATH = _ROOT / "data" / "provenance" / "tardis_btc_eur_first_of_month_manifest.json"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _month_files() -> list[tuple[str, str, Path, Path]]:
    entries: list[tuple[str, str, Path, Path]] = []
    for quote_path in sorted(_DATA_ROOT.glob("BTCEUR_quotes_*.csv.gz")):
        name = quote_path.name
        stem = name.removeprefix("BTCEUR_quotes_")
        date_token = stem.removesuffix(".csv.gz")

        if "_" in date_token:
            if date_token[-2:] != "01":
                continue
        elif date_token[-2:] != "01":
            continue

        trade_name = f"BTCEUR_trades_{date_token}.csv.gz"
        trade_path = _DATA_ROOT / trade_name
        if trade_path.exists():
            entries.append((date_token, "BTC-EUR", quote_path, trade_path))
    return entries


def build_manifest() -> dict:
    files: list[dict] = []
    for date_token, market, quote_path, trade_path in _month_files():
        files.append({
            "date": date_token,
            "market": market,
            "quote_file": {
                "path": str(quote_path.relative_to(_ROOT)),
                "size_bytes": quote_path.stat().st_size,
                "sha256": _sha256(quote_path),
            },
            "trade_file": {
                "path": str(trade_path.relative_to(_ROOT)),
                "size_bytes": trade_path.stat().st_size,
                "sha256": _sha256(trade_path),
            },
        })

    return {
        "dataset_name": "tardis_btc_eur_first_of_month_sample",
        "source": "Tardis.dev",
        "market": "BTC-EUR",
        "status": "PROVISIONAL_BOUND_RESEARCH_ONLY",
        "scope": {
            "sample_rule": "first calendar day of each month only",
            "allowed_use": "bounded historical research and deterministic validation only",
            "excluded_claims": [
                "statistical representativeness",
                "final dataset adequacy",
                "profitability proof",
                "paper-trading approval",
                "live-trading approval",
            ],
            "venue_distinction": "historical research dataset is not a Bitvavo execution dataset",
        },
        "file_count": len(files),
        "files": files,
    }


def main() -> int:
    _OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    manifest = build_manifest()
    _OUTPUT_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote provenance manifest: {_OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
