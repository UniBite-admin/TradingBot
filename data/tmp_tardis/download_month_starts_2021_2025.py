import urllib.request
from pathlib import Path
from datetime import date

BASE = Path("data/tmp_tardis")
BASE.mkdir(parents=True, exist_ok=True)

success = []
failed = []

for year in range(2021, 2026):
    for month in range(1, 13):
        ds = f"{year}_{month:02d}_01"
        path_date = f"{year}/{month:02d}/01"

        quote = BASE / f"BTCEUR_quotes_{ds}.csv.gz"
        trade = BASE / f"BTCEUR_trades_{ds}.csv.gz"

        urls = [
            (
                f"https://datasets.tardis.dev/v1/binance-jersey/quotes/{path_date}/BTCEUR.csv.gz",
                quote,
            ),
            (
                f"https://datasets.tardis.dev/v1/binance-jersey/trades/{path_date}/BTCEUR.csv.gz",
                trade,
            ),
        ]

        print(f"\n[{ds}]")

        day_ok = True

        for url, output in urls:
            if output.exists() and output.stat().st_size > 0:
                print(f"  EXISTS  {output.name}")
                continue

            try:
                urllib.request.urlretrieve(url, output)
                print(f"  OK      {output.name} ({output.stat().st_size:,} bytes)")
            except Exception as exc:
                day_ok = False
                print(f"  ERROR   {output.name}: {type(exc).__name__}: {exc}")
                if output.exists():
                    output.unlink()

        if day_ok and quote.exists() and trade.exists():
            success.append(ds)
        else:
            failed.append(ds)

print("\n" + "=" * 60)
print(f"SUCCESSFUL DAYS: {len(success)}")
print(f"FAILED DAYS:     {len(failed)}")

if failed:
    print("\nFAILED:")
    for ds in failed:
        print(f"  {ds}")

print("\nDOWNLOAD PROCESS FINISHED")
