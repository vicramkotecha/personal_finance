import os
import shutil
import subprocess
import tempfile
import unittest

from personal_finance.gnucash_interface import (
    launch_gnucash,
    close_gnucash,
    open_account_register,
    enter_transaction,
)


class TestEnterTransactionIntegration(unittest.TestCase):
    """Integration test that launches GnuCash, opens the Checking Account
    register, enters one transaction via SendKeys, then closes GnuCash.

    Run explicitly:
        $env:PYTHONPATH="src"
        python -m unittest tests.integration.test_enter_transaction_integration -v
    """

    SOURCE_FILE = 'test_data/test_accounts.xml.gnucash'
    ACCOUNT_NAME = 'Checking Account'

    @classmethod
    def setUpClass(cls):
        cls.tmpdir = tempfile.mkdtemp(prefix='gnucash_test_')
        cls.gnucash_file = os.path.join(
            cls.tmpdir, os.path.basename(cls.SOURCE_FILE)
        )
        shutil.copy2(cls.SOURCE_FILE, cls.gnucash_file)

        result, pid = launch_gnucash(cls.gnucash_file)
        cls.pid = pid
        if pid is None:
            shutil.rmtree(cls.tmpdir, ignore_errors=True)
            raise RuntimeError(f'Failed to launch GnuCash: {result.stderr}')

    @classmethod
    def tearDownClass(cls):
        # Safety net: ensure GnuCash is closed even if a test fails
        check = subprocess.run(
            ['powershell', '-Command',
             'Get-Process -Name gnucash -ErrorAction SilentlyContinue'],
            capture_output=True, text=True,
        )
        if check.stdout.strip():
            subprocess.run(
                ['powershell', '-Command',
                 'Get-Process -Name gnucash | Stop-Process -Force'],
            )
        # Clean up temp directory
        shutil.rmtree(cls.tmpdir, ignore_errors=True)

    def test_01_open_account_register(self):
        result = open_account_register(self.pid, self.ACCOUNT_NAME)

        self.assertEqual(result.returncode, 0, f'stderr: {result.stderr}')

    def test_02_enter_transaction(self):
        result = enter_transaction(
            pid=self.pid,
            date='1/1/24',
            description='Integration Test Payment',
            transfer='Expenses:Miscellaneous',
            deposit='',
            withdrawal='42.00',
        )

        self.assertEqual(result.returncode, 0, f'stderr: {result.stderr}')

    def test_03_close_gnucash(self):
        result = close_gnucash(self.pid)

        self.assertEqual(result.returncode, 0, f'stderr: {result.stderr}')


if __name__ == '__main__':
    unittest.main()
