import unittest

from personal_finance.fx_rate_cache import FxRateCache


class TestFxRateCacheIntegration(unittest.TestCase):

    def test_get_rate_returns_plausible_eurusd_rate(self):
        cache = FxRateCache('EURUSD=X')
        rate = cache.get_rate('2025-01-02')

        rate_float = float(rate)
        self.assertGreater(rate_float, 0.90)
        self.assertLess(rate_float, 1.50)

    def test_get_rate_caches_across_calls(self):
        cache = FxRateCache('EURUSD=X')
        rate1 = cache.get_rate('2025-01-02')
        rate2 = cache.get_rate('2025-01-02')

        self.assertEqual(rate1, rate2)


if __name__ == '__main__':
    unittest.main()
