import os
import unittest

from personal_finance.main import run_fbar_report


class FbarReportTests(unittest.TestCase):

    def test_generate_report(self):
        gnucash_xml_file = 'test_data/test_accounts.xml.gnucash'
        test_csv_path = 'test_data/test_fbar_report.csv'

        run_fbar_report(gnucash_xml_file, test_csv_path)

        self.assertTrue(os.path.exists(test_csv_path))

if __name__ == '__main__':
    unittest.main()