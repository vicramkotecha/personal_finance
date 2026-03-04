import unittest
import subprocess
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from personal_finance.gnucash_interface import launch_gnucash


class TestGnuCashInterface(unittest.TestCase):

    def test_launch_gnucash_returns_success(self):
        gnucash_file = 'test_data/test_accounts.xml.gnucash'
        result = launch_gnucash(gnucash_file)

        # Exit code is 0
        self.assertEqual(result.returncode, 0)

        # stdout contains the window title with "GnuCash"
        self.assertIn('GnuCash', result.stdout)

        # stderr is empty (no errors)
        self.assertEqual(result.stderr.strip(), '')

        # GnuCash process is no longer running
        check = subprocess.run(
            ['powershell', '-Command', 'Get-Process -Name gnucash -ErrorAction SilentlyContinue'],
            capture_output=True, text=True
        )
        self.assertEqual(check.stdout.strip(), '', 'GnuCash process is still running')


if __name__ == '__main__':
    unittest.main()
