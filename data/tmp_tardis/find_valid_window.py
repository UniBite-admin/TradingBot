from pathlib import Path
from tools.hsra.window_analysis import find_largest_candidate_by_contract

quotes = Path('data/tmp_tardis/BTCEUR_quotes_20191201.csv.gz')
trades = Path('data/tmp_tardis/BTCEUR_trades_20191201.csv.gz')

best, valid = find_largest_candidate_by_contract(quotes, trades)
print('BEST', best)
print('VALID_COUNT', len(valid))
for c in sorted(valid, key=lambda x: x.duration_seconds, reverse=True)[:10]:
    print(c)
