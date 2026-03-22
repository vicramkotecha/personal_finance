import unittest

import gnucashxml

from personal_finance.book_utils import get_transaction_history


TEST_GNUCASH_FILE = 'test_data/test_accounts.xml.gnucash'


class TestGetTransactionHistory(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(TEST_GNUCASH_FILE, 'r') as f:
            cls.book = gnucashxml.parse(f)

    def test_returns_list_of_description_account_pairs(self):
        history = get_transaction_history(self.book)

        self.assertIsInstance(history, list)
        self.assertGreater(len(history), 0)
        # Each entry is a dict with 'description' and 'account'
        entry = history[0]
        self.assertIn('description', entry)
        self.assertIn('account', entry)

    def test_account_is_full_colon_delimited_path(self):
        history = get_transaction_history(self.book)

        for entry in history:
            self.assertIn(':', entry['account'],
                          f'Expected colon-delimited path, got: {entry["account"]}')

    def test_only_includes_expense_and_income_accounts(self):
        history = get_transaction_history(self.book)

        for entry in history:
            account = entry['account']
            self.assertTrue(
                account.startswith('Expenses:') or account.startswith('Income:'),
                f'Expected Expense/Income account, got: {account}',
            )


if __name__ == '__main__':
    unittest.main()
