import os
import unittest

from personal_finance.category_mapper import DefaultCategoryMapper
from personal_finance.statement_importer import load_profile, parse_statement, normalize_transactions


SAMPLE_PROFILE_PATH = os.path.join('config', 'import_profiles', 'sample_bank.json')
SAMPLE_XLS_PROFILE_PATH = os.path.join('config', 'import_profiles', 'sample_bank_xls.json')
TEST_CSV_PATH = os.path.join('test_data', 'test_csv_for_import.csv')
TEST_XLS_PATH = os.path.join('test_data', 'excel_stmt_template.xls')


class TestLoadProfile(unittest.TestCase):

    def test_load_profile_returns_dict(self):
        profile = load_profile(SAMPLE_PROFILE_PATH)
        self.assertIsNotNone(profile)
        self.assertIn('file_format', profile)


class TestParseStatement(unittest.TestCase):

    def setUp(self):
        self.profile = load_profile(SAMPLE_PROFILE_PATH)

    def test_parse_csv_returns_dataframe_with_mapped_columns(self):
        df = parse_statement(TEST_CSV_PATH, self.profile)

        self.assertIn('date', df.columns)
        self.assertIn('description', df.columns)
        self.assertIn('amount', df.columns)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]['description'], 'Salary Payment')
        self.assertAlmostEqual(df.iloc[0]['amount'], 5000.00)

    def test_parse_xls_skips_preamble_and_maps_columns(self):
        profile = load_profile(SAMPLE_XLS_PROFILE_PATH)
        df = parse_statement(TEST_XLS_PATH, profile)

        self.assertEqual(len(df), 1)
        self.assertIn('date', df.columns)
        self.assertIn('description', df.columns)
        self.assertIn('amount', df.columns)
        self.assertEqual(df.iloc[0]['description'], 'abcd')
        self.assertAlmostEqual(df.iloc[0]['amount'], -1.00)


class TestNormalizeTransactions(unittest.TestCase):

    def setUp(self):
        self.profile = load_profile(SAMPLE_PROFILE_PATH)
        self.df = parse_statement(TEST_CSV_PATH, self.profile)

    def test_normalize_returns_transaction_dicts_with_transfer(self):
        mapper = DefaultCategoryMapper(
            default_transfer_account='Imbalance-USD',
            account_paths=[],
        )
        transactions = normalize_transactions(self.df, self.profile, mapper)

        self.assertEqual(len(transactions), 1)
        txn = transactions[0]
        self.assertIn('date', txn)
        self.assertIn('description', txn)
        self.assertIn('deposit', txn)
        self.assertIn('withdrawal', txn)
        self.assertIn('transfer', txn)
        # Positive amount → deposit, empty withdrawal
        self.assertEqual(txn['deposit'], '5000.00')
        self.assertEqual(txn['withdrawal'], '')
        # Date reformatted from 2024-01-01 → 1/1/24 (GnuCash M/d/yy)
        self.assertEqual(txn['date'], '1/1/24')
        # Transfer from mapper
        self.assertEqual(txn['transfer'], 'Imbalance-USD')


if __name__ == '__main__':
    unittest.main()
