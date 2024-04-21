import matplotlib.pyplot as plt
import pandas as pd

from personal_finance.book_utils import get_account_currencies, get_balances


class BalanceHistoryReport(object):

    def add_report(self, book, pdf_pages):
        balances = get_balances(book)
        currencies = get_account_currencies(book)
        for account, balances_by_date in sorted(balances.items()):
            currency = currencies[account]
            if not balances_by_date:
                continue
            fig, _ax = plt.subplots()
            df = pd.DataFrame(balances_by_date, index=['Balance']).transpose().reset_index(names=['Date', 'Balance'])
            df['Date'] = pd.to_datetime(df['Date'])
            df['Balance'] = pd.to_numeric(df['Balance'], errors='coerce')
            df = df.fillna(0)
            df = df.sort_index()
            # title: account name
            plt.title(account)
            plt.plot(df['Date'], df['Balance'], label=account)
            plt.xlabel('Date')
            plt.ylabel(f'Balance ({currency})')
            plt.tight_layout()
            pdf_pages.savefig(fig)
            plt.close(fig)
