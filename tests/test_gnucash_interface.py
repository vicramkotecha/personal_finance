import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from personal_finance.gnucash_interface import launch_gnucash


class TestGnuCashInterface(unittest.TestCase):

    def test_launch_gnucash_returns_success(self):
        gnucash_file = 'test_data/test_accounts.xml.gnucash'
        result = launch_gnucash(gnucash_file)
        self.assertEqual(result, 0)


if __name__ == '__main__':
    unittest.main()
