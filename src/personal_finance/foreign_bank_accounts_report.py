import datetime
from decimal import Decimal
from math import e
import pandas as pd
import requests

from personal_finance.book_utils import get_balances, get_latest_price_before_or_on_date, get_account_currencies

currency_url_map = {
    'EUR': 'https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/rates_of_exchange?filter=currency:eq:Euro,country:eq:Euro Zone,effective_date:eq:{date}',
    'GBP': 'https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/rates_of_exchange?filter=currency:eq:Pound,country:eq:United Kingdom,effective_date:eq:{date}',
}

def get_exchange_rate(url, currency, date):
    data = requests.get(url.format(date=datetime.date.strftime(date, '%Y-%m-%d'))).json()
    return 1 / float(data['data'][0]['exchange_rate'])

class ForeignBankAccountsReport(object):

    def __init__(self, base_currency, start_date, end_date, use_max_balance, use_yearend_rate, balances_csv_path=None):
        self.balances_csv_path = balances_csv_path
        self.base_currency = base_currency
        self.start_date = start_date
        self.end_date = end_date
        self.use_max_balance = use_max_balance
        self.use_yearend_rate = use_yearend_rate
        self.exchange_rates = {}
        exchange_rates_to_usd = {}
        for currency, url in currency_url_map.items():
            exchange_rates_to_usd[currency] = get_exchange_rate(url, currency, end_date)
        exchange_rates_to_usd['USD'] = 1
        for currency, rate in exchange_rates_to_usd.items():
            if currency == self.base_currency:
                self.exchange_rates[currency] = 1
            self.exchange_rates[currency] = rate / exchange_rates_to_usd[self.base_currency]

    def add_report(self, book, pdf_pages):
        # no need to generate the report, just the csv
        account_balances = get_balances(book)
        self.write_balances_to_csv(book, account_balances)

    def write_balances_to_csv(self, book, account_balances):

        account_currencies = get_account_currencies(book)
        if self.balances_csv_path:
            with open(self.balances_csv_path, 'w') as f:
                f.write(f'Account,Balance Date,{self.base_currency} Balance,Account Currency Balance,Currency,Currency Price in USD,Price Date\n')
                for account, balances_by_date in sorted(account_balances.items()):
                    if account.startswith('Assets:') and account_currencies[account] != self.base_currency: # only require foreign accounts
                        balance_year_end = balances_by_date.get(self.end_date, 0)
                        balance_total = 0
                        balance_average = 0
                        balance_count = 0
                        balance_max = 0
                        balance_date = None
                        
                        for date in pd.date_range(start=self.start_date, end=self.end_date, inclusive='both'):
                            dt = datetime.date(date.year, date.month, date.day)
                            if dt in balances_by_date:
                                balance_total += balances_by_date[dt]
                                balance_count += 1
                                if balances_by_date[dt] > balance_max:
                                    balance_max = balances_by_date[dt]
                                    balance_date = dt
                        
                        if balance_count == 0:
                            max_date = max(balances_by_date.keys())
                            if max_date < datetime.date(2023, 10, 1):
                                balance_average = balances_by_date.get(max_date, 0)
                        else:
                            balance_average = balance_total / balance_count
                        
                        if self.use_max_balance:
                            balance_to_count = balance_max
                        elif balance_average > balance_year_end:
                            balance_to_count = balance_average
                            balance_date = "Average"
                        else:
                            balance_to_count = balance_year_end
                            balance_date = "Year End"

                        if self.use_yearend_rate and account_currencies[account] in self.exchange_rates:
                            price = self.exchange_rates[account_currencies[account]]
                            price_date = self.end_date
                        else:
                            price, price_date = get_latest_price_before_or_on_date(book, account_currencies[account], self.end_date)

                        balance_in_base_currency = balance_to_count * Decimal(price)

                        f.write(f'{account},{balance_date},{balance_in_base_currency},{balance_to_count},{account_currencies[account]},{price},{price_date}\n')

