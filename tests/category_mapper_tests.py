import unittest

from personal_finance.category_mapper import DefaultCategoryMapper, RegexCategoryMapper


class TestDefaultCategoryMapper(unittest.TestCase):

    def test_map_returns_default_transfer_account(self):
        mapper = DefaultCategoryMapper(
            default_transfer_account='Imbalance-USD',
            account_paths=['Assets:Current Assets:Checking Account', 'Expenses:Groceries'],
        )

        result = mapper.map('anything at all')

        self.assertEqual(result, 'Imbalance-USD')


class TestRegexCategoryMapper(unittest.TestCase):

    def setUp(self):
        self.patterns = {
            'Expenses:Groceries': 'MERCADONA|LIDL|CARREFOUR',
            'Expenses:Entertainment': 'NETFLIX|SPOTIFY',
            'Income:Salary': 'SALARY',
        }
        self.mapper = RegexCategoryMapper(
            patterns=self.patterns,
            default_transfer_account='Imbalance-USD',
        )

    def test_matches_first_matching_pattern(self):
        self.assertEqual(self.mapper.map('MERCADONA VIGO'), 'Expenses:Groceries')

    def test_matches_case_insensitively(self):
        self.assertEqual(self.mapper.map('netflix monthly'), 'Expenses:Entertainment')

    def test_falls_back_to_default_when_no_match(self):
        self.assertEqual(self.mapper.map('UNKNOWN VENDOR XYZ'), 'Imbalance-USD')


if __name__ == '__main__':
    unittest.main()
