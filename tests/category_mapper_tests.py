import unittest

from personal_finance.category_mapper import DefaultCategoryMapper


class TestDefaultCategoryMapper(unittest.TestCase):

    def test_map_returns_default_transfer_account(self):
        mapper = DefaultCategoryMapper(
            default_transfer_account='Imbalance-USD',
            account_paths=['Assets:Current Assets:Checking Account', 'Expenses:Groceries'],
        )

        result = mapper.map('anything at all')

        self.assertEqual(result, 'Imbalance-USD')


if __name__ == '__main__':
    unittest.main()
