import json
import os
import re
import signal
import time
from datetime import datetime

import pandas as pd

from personal_finance.category_mapper import DefaultCategoryMapper, RegexCategoryMapper
from personal_finance.fx_rate_cache import FxRateCache
from personal_finance.gnucash_interface import (
    launch_gnucash,
    close_gnucash,
    open_account_register,
    enter_transaction,
)


def load_profile(profile_path):
    with open(profile_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def parse_statement(file_path, profile):
    file_format = profile['file_format']
    column_mappings = profile['column_mappings']
    header_rows_to_skip = profile.get('header_rows_to_skip', 0)

    if file_format == 'csv':
        df = pd.read_csv(
            file_path,
            skiprows=header_rows_to_skip,
            delimiter=profile.get('delimiter', ','),
            encoding=profile.get('encoding', 'utf-8'),
        )
    elif file_format in ('xls', 'xlsx'):
        df = pd.read_excel(
            file_path,
            skiprows=header_rows_to_skip,
        )
    else:
        raise ValueError(f'Unsupported file format: {file_format}')

    # Rename columns from source names to normalized names
    rename_map = {source: target for target, source in column_mappings.items()}
    missing = [src for src in rename_map if src not in df.columns]
    if missing:
        raise KeyError(f'Mapped columns not found in file: {missing}')

    df = df.rename(columns=rename_map)

    # Keep only the mapped columns
    df = df[list(column_mappings.keys())]

    return df


def parse_amount(value):
    """Parse a numeric string in either English (1,000.00) or European (1.000,00) format."""
    s = str(value).strip()
    # Find positions of last dot and last comma
    last_dot = s.rfind('.')
    last_comma = s.rfind(',')
    if last_comma > last_dot:
        # European format: dots are thousands separators, comma is decimal
        s = s.replace('.', '').replace(',', '.')
    else:
        # English format or no separators: commas are thousands separators
        s = s.replace(',', '')
    return float(s)


def normalize_transactions(df, profile, mapper, start_date=None):
    date_format = profile['date_format']
    transactions = []

    for _, row in df.iterrows():
        parsed_date = datetime.strptime(str(row['date']), date_format)
        if start_date and parsed_date.date() < start_date:
            continue
        gnucash_date = f'{parsed_date.month}/{parsed_date.day}/{parsed_date.strftime("%y")}'

        amount = parse_amount(row['amount'])
        if amount >= 0:
            deposit = f'{amount:.2f}'
            withdrawal = ''
        else:
            deposit = ''
            withdrawal = f'{abs(amount):.2f}'

        description = re.sub(r'\d{6,}', '', str(row['description']))

        transactions.append({
            'date': gnucash_date,
            'iso_date': parsed_date.strftime('%Y-%m-%d'),
            'description': description,
            'transfer': mapper.map(description),
            'deposit': deposit,
            'withdrawal': withdrawal,
        })

    return transactions


def import_statement(profile_path, gnucash_file, statement_file, account_name,
                     default_transfer='Imbalance-USD', category_mapping=None,
                     start_date=None):
    profile = load_profile(profile_path)
    df = parse_statement(statement_file, profile)

    # Load category mapping: CLI arg > profile field > default
    mapping_path = category_mapping or profile.get('category_mapping')
    if mapping_path:
        with open(mapping_path, 'r', encoding='utf-8') as f:
            patterns = json.load(f)
        mapper = RegexCategoryMapper(patterns, default_transfer)
        print(f'Using regex category mapping from {mapping_path} ({len(patterns)} patterns)')
    else:
        mapper = DefaultCategoryMapper(default_transfer, account_paths=[])

    transactions = normalize_transactions(df, profile, mapper, start_date=start_date)

    fx_ticker = profile.get('fx_ticker')
    if fx_ticker:
        cache_dir = os.path.join(os.path.dirname(os.path.abspath(profile_path)), '..', '..', 'data', 'cache')
        os.makedirs(cache_dir, exist_ok=True)
        cache_file = os.path.join(cache_dir, f'{fx_ticker}_cache.csv')
        fx_cache = FxRateCache(fx_ticker, cache_file=cache_file)
    else:
        fx_cache = None

    result, pid = launch_gnucash(gnucash_file)
    if pid is None:
        raise RuntimeError(f'Failed to launch GnuCash: {result.stderr}')

    interrupted = False

    def _handle_sigint(sig, frame):
        nonlocal interrupted
        interrupted = True
        print('\nCtrl-C received — finishing current transaction then closing GnuCash...')

    original_handler = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, _handle_sigint)

    try:
        result = open_account_register(pid, account_name)
        if result.returncode != 0:
            raise RuntimeError(f'Failed to open register: {result.stderr}')

        for i, txn in enumerate(transactions):
            if interrupted:
                print(f'Stopped after {i} of {len(transactions)} transactions.')
                break

            print(f'[{i+1}/{len(transactions)}] {txn["date"]} {txn["description"][:50]}')
            if fx_cache:
                fx_rate = fx_cache.get_rate(txn['iso_date'])
            else:
                fx_rate = '1'

            result = enter_transaction(
                pid=pid,
                date=txn['date'],
                description=txn['description'],
                transfer=txn['transfer'],
                deposit=txn['deposit'],
                withdrawal=txn['withdrawal'],
                fx_rate=fx_rate,
            )
            if result.returncode != 0:
                raise RuntimeError(
                    f'Failed to enter transaction: {txn["description"]}: {result.stderr}'
                )
            time.sleep(1)
        else:
            print(f'All {len(transactions)} transactions entered.')
    finally:
        if fx_cache:
            fx_cache.save()
        signal.signal(signal.SIGINT, original_handler)
        print('Saving and closing GnuCash...')
        close_gnucash(pid)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Import a bank statement into GnuCash')
    parser.add_argument('profile', help='Path to the import profile JSON file')
    parser.add_argument('gnucash_file', help='Path to the GnuCash file')
    parser.add_argument('statement_file', help='Path to the bank statement file')
    parser.add_argument('account', help='GnuCash account name to import into')
    parser.add_argument('--default-transfer', default='Imbalance-USD',
                        help='Default transfer account (default: Imbalance-USD)')
    parser.add_argument('--category-mapping', default=None,
                        help='Path to category mapping JSON (regex patterns)')
    parser.add_argument('--start-date', default=None,
                        help='Ignore transactions before this date (YYYY-MM-DD, inclusive)')
    args = parser.parse_args()

    start_date = datetime.strptime(args.start_date, '%Y-%m-%d').date() if args.start_date else None

    import_statement(
        profile_path=args.profile,
        gnucash_file=args.gnucash_file,
        statement_file=args.statement_file,
        account_name=args.account,
        default_transfer=args.default_transfer,
        category_mapping=args.category_mapping,
        start_date=start_date,
    )
