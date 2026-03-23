import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from personal_finance.fx_rate_cache import FxRateCache


class TestFxRateCache(unittest.TestCase):

    @patch('personal_finance.fx_rate_cache.yf')
    def test_returns_rate_for_date(self, mock_yf):
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = MagicMock(
            empty=False,
            __getitem__=lambda self, key: MagicMock(iloc=MagicMock(__getitem__=lambda self, i: 1.0834)),
        )
        mock_yf.Ticker.return_value = mock_ticker

        cache = FxRateCache('EURUSD=X')
        rate = cache.get_rate('2024-01-15')

        self.assertEqual(rate, '1.0834')
        mock_yf.Ticker.assert_called_once_with('EURUSD=X')

    @patch('personal_finance.fx_rate_cache.yf')
    def test_caches_rate_and_does_not_call_yfinance_twice(self, mock_yf):
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = MagicMock(
            empty=False,
            __getitem__=lambda self, key: MagicMock(iloc=MagicMock(__getitem__=lambda self, i: 1.0834)),
        )
        mock_yf.Ticker.return_value = mock_ticker

        cache = FxRateCache('EURUSD=X')
        rate1 = cache.get_rate('2024-01-15')
        rate2 = cache.get_rate('2024-01-15')

        self.assertEqual(rate1, rate2)
        # history should only be called once for the same date
        self.assertEqual(mock_ticker.history.call_count, 1)

    @patch('personal_finance.fx_rate_cache.yf')
    def test_save_writes_cache_to_csv(self, mock_yf):
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = MagicMock(
            empty=False,
            __getitem__=lambda self, key: MagicMock(iloc=MagicMock(__getitem__=lambda self, i: 1.0834)),
        )
        mock_yf.Ticker.return_value = mock_ticker

        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, 'fx_cache.csv')
            cache = FxRateCache('EURUSD=X', cache_file=csv_path)
            cache.get_rate('2024-01-15')
            cache.save()

            with open(csv_path, 'r') as f:
                contents = f.read()

            self.assertIn('2024-01-15', contents)
            self.assertIn('1.0834', contents)

    @patch('personal_finance.fx_rate_cache.yf')
    def test_retries_previous_days_when_no_data_on_requested_date(self, mock_yf):
        empty_history = MagicMock(empty=True)
        good_history = MagicMock(
            empty=False,
            __getitem__=lambda self, key: MagicMock(iloc=MagicMock(__getitem__=lambda self, i: 1.2650)),
        )
        mock_ticker = MagicMock()
        # First two calls (day 0 and day-1) return empty, third (day-2) succeeds
        mock_ticker.history.side_effect = [empty_history, empty_history, good_history]
        mock_yf.Ticker.return_value = mock_ticker

        cache = FxRateCache('GBPUSD=X')
        rate = cache.get_rate('2026-03-15')  # a Sunday

        self.assertEqual(rate, '1.2650')
        self.assertEqual(mock_ticker.history.call_count, 3)
        # The rate should be cached under the originally requested date
        self.assertEqual(cache._cache['2026-03-15'], '1.2650')

    @patch('personal_finance.fx_rate_cache.yf')
    def test_raises_after_exhausting_lookback(self, mock_yf):
        empty_history = MagicMock(empty=True)
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = empty_history
        mock_yf.Ticker.return_value = mock_ticker

        cache = FxRateCache('GBPUSD=X')
        with self.assertRaises(ValueError):
            cache.get_rate('2026-03-15')

        # Should have tried 5 times (day 0 through day-4)
        self.assertEqual(mock_ticker.history.call_count, 5)

    @patch('personal_finance.fx_rate_cache.yf')
    def test_load_reads_cache_from_csv_and_skips_api(self, mock_yf):
        mock_ticker = MagicMock()
        mock_yf.Ticker.return_value = mock_ticker

        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, 'fx_cache.csv')
            with open(csv_path, 'w') as f:
                f.write('date,rate\n')
                f.write('2024-01-15,1.0834\n')

            cache = FxRateCache('EURUSD=X', cache_file=csv_path)
            rate = cache.get_rate('2024-01-15')

            self.assertEqual(rate, '1.0834')
            mock_ticker.history.assert_not_called()


if __name__ == '__main__':
    unittest.main()
