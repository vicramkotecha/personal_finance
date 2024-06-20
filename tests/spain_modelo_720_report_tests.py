import os
import unittest

from personal_finance.main import run_modelo_720_report


class Model720ReportTests(unittest.TestCase):

    def test_generate_report(self):
        gnucash_xml_file = 'test_data/test_accounts.xml.gnucash'
        test_csv_path = 'test_data/test_modelo_720_report.csv'

        run_modelo_720_report(gnucash_xml_file, test_csv_path)

        self.assertTrue(os.path.exists(test_csv_path))

if __name__ == '__main__':
    unittest.main()