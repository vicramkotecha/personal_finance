import os
import unittest

from personal_finance.statement_importer import load_profile, parse_statement


SAMPLE_PROFILE_PATH = os.path.join('config', 'import_profiles', 'sample_bank.json')
TEST_CSV_PATH = os.path.join('test_data', 'test_csv_for_import.csv')


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


if __name__ == '__main__':
    unittest.main()
