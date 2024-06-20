import os
import unittest

from personal_finance.main import run_balance_history_report

class BalanceHistoryReportTests(unittest.TestCase):
    def test_generate_report(self):
        gnucash_xml_file = 'test_data/test_accounts.xml.gnucash'
        test_report_path = 'test_data/test_balance_history_report.pdf'
        
        run_balance_history_report(gnucash_xml_file, test_report_path)

        self.assertTrue(os.path.exists(test_report_path))

if __name__ == '__main__':
    unittest.main()