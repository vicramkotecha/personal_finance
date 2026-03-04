import unittest
import subprocess
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from personal_finance.gnucash_interface import launch_gnucash, close_gnucash


class TestGnuCashInterface(unittest.TestCase):

    GNUCASH_FILE = 'test_data/test_accounts.xml.gnucash'

    @classmethod
    def setUpClass(cls):
        result, pid = launch_gnucash(cls.GNUCASH_FILE)
        cls.launch_result = result
        cls.pid = pid

    @classmethod
    def tearDownClass(cls):
        # Safety net: ensure GnuCash is closed even if the close test fails
        check = subprocess.run(
            ['powershell', '-Command', 'Get-Process -Name gnucash -ErrorAction SilentlyContinue'],
            capture_output=True, text=True
        )
        if check.stdout.strip():
            subprocess.run(
                ['powershell', '-Command', 'Get-Process -Name gnucash | Stop-Process -Force'],
            )

    def test_launch_returns_success(self):
        result = self.launch_result

        # Exit code is 0
        self.assertEqual(result.returncode, 0)

        # stderr is empty (no errors)
        self.assertEqual(result.stderr.strip(), '')

        # PID was returned
        self.assertIsNotNone(self.pid)

    def test_close_returns_success(self):
        self.assertIsNotNone(self.pid, 'Launch must have provided a PID')

        result = close_gnucash(self.pid)

        # Exit code is 0
        self.assertEqual(result.returncode, 0)

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
