import os
import unittest
from unittest.mock import patch, MagicMock

from personal_finance.category_mapper import DefaultCategoryMapper
from personal_finance.statement_importer import (
    load_profile, parse_statement, normalize_transactions, import_statement,
)


SAMPLE_PROFILE_PATH = os.path.join('config', 'import_profiles', 'sample_bank.json')
SAMPLE_XLS_PROFILE_PATH = os.path.join('config', 'import_profiles', 'sample_bank_xls.json')
TEST_CSV_PATH = os.path.join('test_data', 'test_csv_for_import.csv')
TEST_XLS_PATH = os.path.join('test_data', 'excel_stmt_template.xls')


class TestLoadProfile(unittest.TestCase):

    def test_load_profile_returns_dict(self):
        profile = load_profile(SAMPLE_PROFILE_PATH)
        self.assertIsNotNone(profile)
        self.assertIn('file_format', profile)

    def test_load_profile_with_fx_ticker(self):
        profile = load_profile(SAMPLE_XLS_PROFILE_PATH)
        self.assertEqual(profile['fx_ticker'], 'EURUSD=X')


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

    def test_normalize_sanitizes_long_digit_sequences_from_description(self):
        import pandas as pd
        df = pd.DataFrame([{
            'date': '2024-01-01',
            'description': 'PAYMENT CARD 123456789012 STORE XYZ',
            'amount': -50.00,
        }])
        mapper = DefaultCategoryMapper(
            default_transfer_account='Imbalance-USD',
            account_paths=[],
        )
        transactions = normalize_transactions(df, self.profile, mapper)
        self.assertEqual(transactions[0]['description'], 'PAYMENT CARD  STORE XYZ')


class TestImportStatement(unittest.TestCase):

    @patch('personal_finance.statement_importer.close_gnucash')
    @patch('personal_finance.statement_importer.enter_transaction')
    @patch('personal_finance.statement_importer.open_account_register')
    @patch('personal_finance.statement_importer.launch_gnucash')
    def test_import_statement_enters_each_transaction(
        self, mock_launch, mock_open, mock_enter, mock_close,
    ):
        ok = MagicMock()
        ok.returncode = 0
        mock_launch.return_value = (ok, 1234)
        mock_open.return_value = ok
        mock_enter.return_value = ok
        mock_close.return_value = ok

        import_statement(
            profile_path=SAMPLE_PROFILE_PATH,
            gnucash_file='test_data/test_accounts.xml.gnucash',
            statement_file=TEST_CSV_PATH,
            account_name='Checking Account',
            default_transfer='Imbalance-USD',
        )

        mock_launch.assert_called_once_with('test_data/test_accounts.xml.gnucash')
        mock_open.assert_called_once_with(1234, 'Checking Account')
        # 1 row in test CSV → 1 enter_transaction call
        mock_enter.assert_called_once_with(
            pid=1234,
            date='1/1/24',
            description='Salary Payment',
            transfer='Imbalance-USD',
            deposit='5000.00',
            withdrawal='',
            fx_rate='1',  # TODO: look up rate by date
        )
        mock_close.assert_called_once_with(1234)

    @patch('personal_finance.statement_importer.FxRateCache')
    @patch('personal_finance.statement_importer.close_gnucash')
    @patch('personal_finance.statement_importer.enter_transaction')
    @patch('personal_finance.statement_importer.open_account_register')
    @patch('personal_finance.statement_importer.launch_gnucash')
    def test_import_statement_uses_fx_rate_from_cache_when_profile_has_ticker(
        self, mock_launch, mock_open, mock_enter, mock_close, mock_fx_cache_cls,
    ):
        ok = MagicMock()
        ok.returncode = 0
        mock_launch.return_value = (ok, 1234)
        mock_open.return_value = ok
        mock_enter.return_value = ok
        mock_close.return_value = ok

        mock_cache = MagicMock()
        mock_cache.get_rate.return_value = '1.0834'
        mock_fx_cache_cls.return_value = mock_cache

        import_statement(
            profile_path=SAMPLE_XLS_PROFILE_PATH,
            gnucash_file='test_data/test_accounts.xml.gnucash',
            statement_file=TEST_XLS_PATH,
            account_name='Checking Account',
            default_transfer='Imbalance-USD',
        )

        # FxRateCache constructed with ticker and cache_file in data/cache
        mock_fx_cache_cls.assert_called_once()
        call_args = mock_fx_cache_cls.call_args
        self.assertEqual(call_args.args[0], 'EURUSD=X')
        self.assertIn('cache_file', call_args.kwargs)
        cache_file = call_args.kwargs['cache_file']
        self.assertTrue(cache_file.endswith(os.path.join('data', 'cache', 'EURUSD=X_cache.csv')))
        # enter_transaction called with looked-up rate
        mock_enter.assert_called_once()
        call_kwargs = mock_enter.call_args
        self.assertEqual(call_kwargs.kwargs['fx_rate'], '1.0834')
        # get_rate called with the transaction date in YYYY-MM-DD format
        mock_cache.get_rate.assert_called_once()


if __name__ == '__main__':
    unittest.main()
