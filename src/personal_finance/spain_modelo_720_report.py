from datetime import date
from personal_finance.foreign_bank_accounts_report import ForeignBankAccountsReport


class Model720Report(ForeignBankAccountsReport):
    
        def __init__(self, balances_csv_path=None):
            year = date.today().year - 1
            start_date = date(year, 10, 1)
            end_date = date(year, 12, 31)
            super().__init__('EUR', start_date, end_date, False, False, balances_csv_path)