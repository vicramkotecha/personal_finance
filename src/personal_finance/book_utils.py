import datetime
import pandas as pd

def get_balances(book):
    account_transaction_totals = {} # <account name> -> <date> -> <balance>
    for account, _subaccounts, splits in book.walk():
        account = get_account_full_path_name(account)
        totals_by_date = {} # <date> -> <balance>
        for split in sorted(splits, key=lambda x: x.transaction.date):
            dt = datetime.date(split.transaction.date.year, split.transaction.date.month, split.transaction.date.day)
            
            totals_by_date[dt] = totals_by_date.get(dt, 0) + split.quantity

        account_transaction_totals[account] = totals_by_date

    account_balances = {}
    for account, totals_by_date in account_transaction_totals.items():
        balances_by_date = {}
        if not totals_by_date:
            continue
        min_date = min(totals_by_date.keys())
        max_date = max(max(totals_by_date.keys()), datetime.date.today())
        current_balance = 0
        for date in pd.date_range(start=min_date, end=max_date, inclusive='both'):
            date = datetime.date(date.year, date.month, date.day)
            transations_for_day = totals_by_date.get(date, 0)
            balances_by_date[date] = current_balance + transations_for_day
            current_balance = balances_by_date[date]

        account_balances[account] = balances_by_date
        
    return account_balances


def get_latest_price_before_or_on_date(book, commodity, date):
    commodity_prices_by_date = {}
    for price in book.prices:
        if price.commodity.name == commodity and price.date.date() <= date:
            if price.currency.name == 'USD':
                commodity_prices_by_date[price.date] = price.value
            elif price.commodity.name == 'NA': # edge case Vic
                # Convert to USD
                exchange_rate = get_latest_price_before_or_on_date(book, price.currency.name, price.date.date())[0]
                if exchange_rate:
                    commodity_prices_by_date[price.date] = price.value * exchange_rate

    if not commodity_prices_by_date:
        return 0, None
    price_date = max(commodity_prices_by_date.keys())
    return commodity_prices_by_date.get(price_date, 0), price_date


def get_account_currencies(book):
    account_currencies = {}
    for account, _subaccounts, splits in book.walk():
        commodity = account.commodity
        account = get_account_full_path_name(account)
        if commodity:
            account_currencies[account] = commodity.name
        else:
            account_currencies[account] = 'Unknown'

    return account_currencies            


def get_account_full_path_name(account):
    account_path = get_account_path(account)
    account = ':'.join(account_path[1:]) # ignore root account
    return account


def get_account_path(account):
    account_path = []
    while account:
        account_path.insert(0, account.name)
        account = account.parent
    return account_path


def get_income_and_expenses(book):
    expenses_by_account = {} # <month, year> -> <account name> -> <amount>
    income_by_account = {} # <month, year> -> <account name> -> <amount>
    all_expenses = []

    # partition into months
    for account, _subaccounts, splits in book.walk():
        for split in splits:
            dt = split.transaction.date

            month_year = (dt.year, dt.month)
            if account.actype == 'INCOME' and account.name == 'Salary':
                income_by_account[month_year] = income_by_account.get(month_year, {})
                income_by_account[month_year][account.name] = income_by_account[month_year].get(account.name, 0) + split.quantity
            elif account.actype == 'EXPENSE':
                if month_year[0] == 2023 and month_year[1] <= 8 and account.name == 'Home' and abs(split.quantity) > 1000:
                    continue # ignore home purchase and related large expenses
                expenses_by_account[month_year] = expenses_by_account.get(month_year, {})
                expenses_by_account[month_year][account.name] = expenses_by_account[month_year].get(account.name, 0) + split.quantity
                all_expenses.append([dt.strftime("%d/%m/%Y"), str(split.quantity), split.account.name, str(split.quantity), split.transaction.description, split.transaction.currency])

    # if self.expenses_csv_path:
    #     # csv of expenses
    #     pd.DataFrame(columns=["Date", "Amount", "Account", "Debit/Credit", "Description", "Currency"], data=all_expenses).to_csv(self.expenses_csv_path, index=False)

    return income_by_account, expenses_by_account