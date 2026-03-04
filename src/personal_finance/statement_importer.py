import json

import pandas as pd


def load_profile(profile_path):
    with open(profile_path, 'r') as f:
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
