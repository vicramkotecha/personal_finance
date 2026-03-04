import json
from datetime import datetime

import pandas as pd

from personal_finance.category_mapper import DefaultCategoryMapper
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


def normalize_transactions(df, profile, mapper):
    date_format = profile['date_format']
    transactions = []

    for _, row in df.iterrows():
        parsed_date = datetime.strptime(str(row['date']), date_format)
        gnucash_date = f'{parsed_date.month}/{parsed_date.day}/{parsed_date.strftime("%y")}'

        amount = float(row['amount'])
        if amount >= 0:
            deposit = f'{amount:.2f}'
            withdrawal = ''
        else:
            deposit = ''
            withdrawal = f'{abs(amount):.2f}'

        description = str(row['description'])

        transactions.append({
            'date': gnucash_date,
            'description': description,
            'transfer': mapper.map(description),
            'deposit': deposit,
            'withdrawal': withdrawal,
        })

    return transactions


def import_statement(profile_path, gnucash_file, statement_file, account_name,
                     default_transfer='Imbalance-USD'):
    profile = load_profile(profile_path)
    df = parse_statement(statement_file, profile)
    mapper = DefaultCategoryMapper(default_transfer, account_paths=[])
    transactions = normalize_transactions(df, profile, mapper)

    result, pid = launch_gnucash(gnucash_file)
    if pid is None:
        raise RuntimeError(f'Failed to launch GnuCash: {result.stderr}')

    try:
        result = open_account_register(pid, account_name)
        if result.returncode != 0:
            raise RuntimeError(f'Failed to open register: {result.stderr}')

        for txn in transactions:
            result = enter_transaction(
                pid=pid,
                date=txn['date'],
                description=txn['description'],
                transfer=txn['transfer'],
                deposit=txn['deposit'],
                withdrawal=txn['withdrawal'],
            )
            if result.returncode != 0:
                raise RuntimeError(
                    f'Failed to enter transaction: {txn["description"]}: {result.stderr}'
                )
    finally:
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

    args = parser.parse_args()

    import_statement(
        profile_path=args.profile,
        gnucash_file=args.gnucash_file,
        statement_file=args.statement_file,
        account_name=args.account,
        default_transfer=args.default_transfer,
    )
