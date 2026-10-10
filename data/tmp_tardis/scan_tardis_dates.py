import csv
import gzip
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

base = Path('data/tmp_tardis')
base.mkdir(exist_ok=True, parents=True)

start = datetime(2019, 11, 28)
end = datetime(2019, 12, 10)


def fetch(url: str, out: Path) -> None:
    if out.exists():
        return
    urllib.request.urlretrieve(url, out)


def inspect_csv(path: Path):
    if not path.exists():
        return None
    with gzip.open(path, 'rt', encoding='utf-8', newline='') as fh:
        rows = list(csv.reader(fh))
    if not rows:
        return None
    header = rows[0]
    first = None
    last = None
    missing_bid = 0
    missing_ask = 0
    invalid_numeric = 0
    bid_ge_ask = 0
    bad_row_shape = 0
    for row in rows[1:]:
        if len(row) != len(header):
            bad_row_shape += 1
            continue
        d = dict(zip(header, row))
        bid = d.get('bid_price') if d.get('bid_price') not in (None, '') else d.get('bid')
        ask = d.get('ask_price') if d.get('ask_price') not in (None, '') else d.get('ask')
        ts = d.get('timestamp')
        if first is None:
            first = ts
        last = ts
        if bid in (None, ''):
            missing_bid += 1
        if ask in (None, ''):
            missing_ask += 1
        if bid in (None, '') or ask in (None, ''):
            continue
        try:
            float(bid)
            float(ask)
            int(str(ts))
        except Exception:
            invalid_numeric += 1
            continue
        if float(bid) >= float(ask):
            bid_ge_ask += 1
    return {
        'rows': len(rows)-1,
        'header': header,
        'first': first,
        'last': last,
        'missing_bid': missing_bid,
        'missing_ask': missing_ask,
        'invalid_numeric': invalid_numeric,
        'bid_ge_ask': bid_ge_ask,
        'bad_row_shape': bad_row_shape,
    }

for offset in range((end - start).days + 1):
    day = start + timedelta(days=offset)
    ds = day.strftime('%Y%m%d')
    q_url = f'https://datasets.tardis.dev/v1/binance-jersey/quotes/{day.year}/{day.month:02d}/{day.day:02d}/BTCEUR.csv.gz'
    t_url = f'https://datasets.tardis.dev/v1/binance-jersey/trades/{day.year}/{day.month:02d}/{day.day:02d}/BTCEUR.csv.gz'
    q_path = base / f'BTCEUR_quotes_{ds}.csv.gz'
    t_path = base / f'BTCEUR_trades_{ds}.csv.gz'
    try:
        fetch(q_url, q_path)
        fetch(t_url, t_path)
    except Exception as exc:
        print(f'DATE {ds} FETCH_ERROR {type(exc).__name__}: {exc}')
        continue
    q_stats = inspect_csv(q_path)
    t_stats = inspect_csv(t_path)
    print(f'DATE {ds}')
    print(f'  QUOTES: {q_stats}')
    print(f'  TRADES: {t_stats}')
    if q_stats and t_stats:
        if q_stats['missing_bid'] == 0 and q_stats['missing_ask'] == 0 and q_stats['invalid_numeric'] == 0 and q_stats['bid_ge_ask'] == 0 and q_stats['bad_row_shape'] == 0:
            print(f'  CANDIDATE_DAY {ds} passes raw quality gates')
