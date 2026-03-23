from datetime import datetime, timedelta
import csv
import os

import yfinance as yf


class FxRateCache:

    def __init__(self, ticker_symbol, cache_file=None):
        self.ticker_symbol = ticker_symbol
        self.ticker = yf.Ticker(ticker_symbol)
        self._cache = {}
        self._cache_file = cache_file

        if cache_file and os.path.exists(cache_file):
            with open(cache_file, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self._cache[row['date']] = row['rate']

    def get_rate(self, date_str):
        if date_str in self._cache:
            return self._cache[date_str]

        dt = datetime.strptime(date_str, '%Y-%m-%d')

        for lookback in range(5):
            start = dt - timedelta(days=lookback)
            end = start + timedelta(days=1)
            history = self.ticker.history(start=start.strftime('%Y-%m-%d'),
                                          end=end.strftime('%Y-%m-%d'))
            if not history.empty:
                rate = history['Close'].iloc[0]
                rate_str = f'{rate:.4f}'
                self._cache[date_str] = rate_str
                return rate_str

        raise ValueError(f'No FX rate found for {self.ticker_symbol} on {date_str} (tried 4 days back)')

    def save(self):
        if not self._cache_file:
            return
        with open(self._cache_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['date', 'rate'])
            for date_str, rate in sorted(self._cache.items()):
                writer.writerow([date_str, rate])
