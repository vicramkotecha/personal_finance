from datetime import date
from personal_finance.foreign_bank_accounts_report import ForeignBankAccountsReport


class UsFbarReport(ForeignBankAccountsReport):
    
        def __init__(self, balances_csv_path=None):
            year = date.today().year - 1
            start_date = date(year, 1, 1)
            end_date = date(year, 12, 31)
            super().__init__('USD', start_date, end_date, True, True, balances_csv_path)