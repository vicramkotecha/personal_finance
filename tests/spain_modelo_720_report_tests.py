import os
import unittest

from personal_finance.main import run_modelo_720_report


class Model720ReportTests(unittest.TestCase):

    def test_generate_report(self):
        gnucash_xml_file = 'tests/test_accounts.xml.gnucash'
        test_report_path = 'tests/test_modelo_720_report.pdf'
        test_csv_path = 'tests/test_modelo_720_report.csv'

        run_modelo_720_report(gnucash_xml_file, test_report_path, test_csv_path)

        self.assertTrue(os.path.exists(test_csv_path))

if __name__ == '__main__':
    unittest.main()