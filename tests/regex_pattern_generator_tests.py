import unittest

from personal_finance.category_mapper import generate_regex_patterns


class TestGenerateRegexPatterns(unittest.TestCase):

    def test_generates_patterns_from_transaction_history(self):
        history = [
            {'description': 'MERCADONA VIGO', 'account': 'Expenses:Groceries'},
            {'description': 'MERCADONA MADRID', 'account': 'Expenses:Groceries'},
            {'description': 'LIDL VIGO', 'account': 'Expenses:Groceries'},
            {'description': 'CARREFOUR BARCELONA', 'account': 'Expenses:Groceries'},
            {'description': 'NETFLIX', 'account': 'Expenses:Entertainment'},
            {'description': 'NETFLIX MONTHLY', 'account': 'Expenses:Entertainment'},
            {'description': 'SPOTIFY', 'account': 'Expenses:Entertainment'},
            {'description': 'SALARY PAYMENT', 'account': 'Income:Salary'},
            {'description': 'SALARY JAN', 'account': 'Income:Salary'},
        ]

        patterns = generate_regex_patterns(history)

        # Should be a dict of account → regex pattern string
        self.assertIsInstance(patterns, dict)
        self.assertIn('Expenses:Groceries', patterns)
        self.assertIn('Expenses:Entertainment', patterns)
        self.assertIn('Income:Salary', patterns)

    def test_generated_pattern_matches_original_descriptions(self):
        history = [
            {'description': 'MERCADONA VIGO', 'account': 'Expenses:Groceries'},
            {'description': 'MERCADONA MADRID', 'account': 'Expenses:Groceries'},
            {'description': 'LIDL VIGO', 'account': 'Expenses:Groceries'},
            {'description': 'NETFLIX', 'account': 'Expenses:Entertainment'},
            {'description': 'SPOTIFY', 'account': 'Expenses:Entertainment'},
        ]

        patterns = generate_regex_patterns(history)

        import re
        grocery_re = re.compile(patterns['Expenses:Groceries'], re.IGNORECASE)
        self.assertTrue(grocery_re.search('MERCADONA VIGO'))
        self.assertTrue(grocery_re.search('LIDL PONTEVEDRA'))

        ent_re = re.compile(patterns['Expenses:Entertainment'], re.IGNORECASE)
        self.assertTrue(ent_re.search('NETFLIX'))
        self.assertTrue(ent_re.search('SPOTIFY PREMIUM'))

    def test_excludes_non_discriminating_tokens(self):
        """Tokens that appear across many accounts should not be in patterns."""
        history = [
            {'description': 'PAYMENT MERCADONA', 'account': 'Expenses:Groceries'},
            {'description': 'PAYMENT NETFLIX', 'account': 'Expenses:Entertainment'},
            {'description': 'PAYMENT SALARY', 'account': 'Income:Salary'},
        ]

        patterns = generate_regex_patterns(history)

        # 'PAYMENT' appears in all accounts, should not be a pattern token
        for account, pattern in patterns.items():
            self.assertNotIn('PAYMENT', pattern.upper(),
                             f'Non-discriminating token PAYMENT found in pattern for {account}')

    def test_removes_token_that_is_substring_of_token_in_another_category(self):
        """If CAR is in Auto but CARREFOUR is in Groceries, CAR should be removed."""
        history = [
            {'description': 'CAR WASH DOWNTOWN', 'account': 'Expenses:Auto'},
            {'description': 'CARREFOUR SUPERMARKET', 'account': 'Expenses:Groceries'},
            {'description': 'CARREFOUR WEEKLY', 'account': 'Expenses:Groceries'},
        ]

        patterns = generate_regex_patterns(history, min_token_length=3)

        # CAR is a substring of CARREFOUR; CAR should be dropped from Auto
        auto_tokens = patterns.get('Expenses:Auto', '').split('|')
        self.assertNotIn('CAR', auto_tokens,
                         'CAR should be removed because CARREFOUR exists in another category')
        # CARREFOUR should remain in Groceries
        grocery_tokens = patterns.get('Expenses:Groceries', '').split('|')
        self.assertIn('CARREFOUR', grocery_tokens)

    def test_sorts_categories_by_frequency(self):
        """Categories with more transactions should appear first in the dict."""
        history = [
            {'description': 'NETFLIX', 'account': 'Expenses:Entertainment'},
            {'description': 'MERCADONA VIGO', 'account': 'Expenses:Groceries'},
            {'description': 'LIDL VIGO', 'account': 'Expenses:Groceries'},
            {'description': 'CARREFOUR', 'account': 'Expenses:Groceries'},
            {'description': 'SALARY JAN', 'account': 'Income:Salary'},
            {'description': 'SALARY FEB', 'account': 'Income:Salary'},
        ]

        patterns = generate_regex_patterns(history)

        keys = list(patterns.keys())
        # Groceries has 3, Salary has 2, Entertainment has 1
        self.assertEqual(keys[0], 'Expenses:Groceries')
        self.assertEqual(keys[1], 'Income:Salary')
        self.assertEqual(keys[2], 'Expenses:Entertainment')


if __name__ == '__main__':
    unittest.main()
