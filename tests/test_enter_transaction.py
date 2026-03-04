import unittest
from unittest.mock import patch, MagicMock

from personal_finance.gnucash_interface import enter_transaction


class TestEnterTransaction(unittest.TestCase):

    @patch('personal_finance.gnucash_interface._run_ps1')
    def test_enter_transaction_calls_ps1_with_correct_args(self, mock_run_ps1):
        mock_run_ps1.return_value = MagicMock(returncode=0, stderr='')

        result = enter_transaction(
            pid=1234,
            date='1/1/24',
            description='Salary Payment',
            transfer='Income:Salary',
            deposit='5000.00',
            withdrawal='',
        )

        mock_run_ps1.assert_called_once_with(
            'enter_transaction.ps1',
            '1234', '1/1/24', 'Salary Payment', 'Income:Salary', '5000.00', '',
        )
        self.assertEqual(result.returncode, 0)


if __name__ == '__main__':
    unittest.main()
