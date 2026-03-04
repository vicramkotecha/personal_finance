import unittest

import gnucashxml

from personal_finance.book_utils import get_all_account_paths


TEST_GNUCASH_FILE = 'test_data/test_accounts.xml.gnucash'


class TestGetAllAccountPaths(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(TEST_GNUCASH_FILE, 'r') as f:
            cls.book = gnucashxml.parse(f)

    def test_returns_non_empty_list(self):
        paths = get_all_account_paths(self.book)

        self.assertIsInstance(paths, list)
        self.assertGreater(len(paths), 0)

    def test_contains_known_account(self):
        paths = get_all_account_paths(self.book)

        self.assertIn('Assets:Current Assets:Checking Account', paths)


if __name__ == '__main__':
    unittest.main()
