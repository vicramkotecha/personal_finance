import datetime
import pandas as pd

from personal_finance.book_utils import get_balances, get_latest_price_before_or_on_date, get_account_currencies

class Model720Report(object):

    def __init__(self, balances_csv_path=None):
        self.balances_csv_path = balances_csv_path

    def add_report(self, book, pdf_pages):
        # no need to generate the report, just the csv
        account_balances = get_balances(book)
        self.write_balances_to_csv(book, account_balances)

    def write_balances_to_csv(self, book, account_balances):

        account_currencies = get_account_currencies(book)
        if self.balances_csv_path:
            with open(self.balances_csv_path, 'w') as f:
                #f.write('Account,Date,Balance,Currency\n')
                f.write('Account,Balance,Currency,Currency Price in USD,Price Date\n')
                for account, balances_by_date in sorted(account_balances.items()):
                    # for date, balance in sorted(balances_by_date.items()):
                    #     date_formatted = date.strftime('%m/%d/%Y')
                        #f.write(f'{account},{date_formatted},{balance},{account_currencies[account]}\n')
                    if account.startswith('Assets:') and account_currencies[account] != 'EUR': # Modelo 720 only requires foreign accounts
                        balance_2023_12_31 = balances_by_date.get(datetime.date(2023, 12, 31), 0)
                        balance_total_4q_2023 = 0
                        balance_average_4q_2023 = 0
                        balance_count_4q_2023 = 0
                        
                        for date in pd.date_range(start='2023-10-01', end='2023-12-31', inclusive='both'):
                            dt = datetime.date(date.year, date.month, date.day)
                            if dt in balances_by_date:
                                balance_total_4q_2023 += balances_by_date[dt]
                                balance_count_4q_2023 += 1
                        
                        if balance_count_4q_2023 == 0:
                            max_date = max(balances_by_date.keys())
                            if max_date < datetime.date(2023, 10, 1):
                                balance_average_4q_2023 = balances_by_date.get(max_date, 0)
                        else:
                            balance_average_4q_2023 = balance_total_4q_2023 / balance_count_4q_2023
                        
                        if balance_average_4q_2023 > balance_2023_12_31:
                            balance_to_count = balance_average_4q_2023
                        else:
                            balance_to_count = balance_2023_12_31

                        price, price_date = get_latest_price_before_or_on_date(book, account_currencies[account], datetime.date(2023, 12, 31))

                        f.write(f'{account},{balance_to_count},{account_currencies[account]},{price},{price_date}\n')

