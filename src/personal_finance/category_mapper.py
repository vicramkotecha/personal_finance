import os
import re
from collections import defaultdict


class DefaultCategoryMapper:

    def __init__(self, default_transfer_account, account_paths):
        self.default_transfer_account = default_transfer_account
        self.account_paths = account_paths

    def map(self, description):
        return self.default_transfer_account


class RegexCategoryMapper:

    def __init__(self, patterns, default_transfer_account):
        self.default_transfer_account = default_transfer_account
        # Compile patterns: {account: compiled_regex}
        self._compiled = []
        for account, pattern in patterns.items():
            self._compiled.append((account, re.compile(pattern, re.IGNORECASE)))

    def map(self, description):
        for account, regex in self._compiled:
            if regex.search(description):
                return account
        return self.default_transfer_account


def generate_regex_patterns(history, min_token_length=4, exclude_accounts=None):
    """Generate regex patterns from transaction history.

    Groups descriptions by account, tokenizes them, and finds tokens that are
    discriminating (appear predominantly in one account). Returns a dict of
    account → regex pattern string (alternation of discriminating tokens).

    Args:
        history: list of {'description': str, 'account': str} dicts
        min_token_length: minimum token length to consider (default 3)
        exclude_accounts: set/list of account paths to skip (default: None)

    Returns:
        dict of account_path → regex pattern string
    """
    exclude = set(exclude_accounts) if exclude_accounts else set()

    # Group descriptions by account
    descriptions_by_account = defaultdict(list)
    for entry in history:
        if entry['account'] not in exclude:
            descriptions_by_account[entry['account']].append(entry['description'])

    # Count how many accounts each token appears in
    token_account_count = defaultdict(set)
    # Count token frequency per account
    token_freq_by_account = defaultdict(lambda: defaultdict(int))

    for account, descriptions in descriptions_by_account.items():
        for desc in descriptions:
            tokens = set(re.findall(r'[A-Za-záéíóúñüÁÉÍÓÚÑÜ]+', desc.upper()))
            for token in tokens:
                if len(token) >= min_token_length:
                    token_account_count[token].add(account)
                    token_freq_by_account[account][token] += 1

    # A token is discriminating only if it appears in exactly one account
    patterns = {}
    for account, descriptions in descriptions_by_account.items():
        token_freqs = token_freq_by_account[account]
        discriminating = []
        for token, freq in sorted(token_freqs.items(), key=lambda x: -x[1]):
            if len(token_account_count[token]) == 1:
                discriminating.append(token)

        if discriminating:
            patterns[account] = discriminating

    # Remove tokens that are substrings of tokens in other categories
    all_tokens_by_account = {acct: set(tokens) for acct, tokens in patterns.items()}
    for account, tokens in list(patterns.items()):
        filtered = []
        for token in tokens:
            is_substring_of_other = False
            for other_account, other_tokens in all_tokens_by_account.items():
                if other_account == account:
                    continue
                for other_token in other_tokens:
                    if token != other_token and token in other_token:
                        is_substring_of_other = True
                        break
                if is_substring_of_other:
                    break
            if not is_substring_of_other:
                filtered.append(token)
        patterns[account] = filtered

    # Remove accounts that ended up with no tokens after filtering
    patterns = {acct: tokens for acct, tokens in patterns.items() if tokens}

    # Sort categories by number of transactions (most frequent first)
    account_txn_counts = {acct: len(descs) for acct, descs in descriptions_by_account.items()}
    sorted_patterns = {}
    for account in sorted(patterns.keys(), key=lambda a: -account_txn_counts.get(a, 0)):
        sorted_patterns[account] = '|'.join(patterns[account])

    return sorted_patterns


if __name__ == '__main__':
    import argparse
    import json

    import gnucashxml

    from personal_finance.book_utils import get_transaction_history

    parser = argparse.ArgumentParser(
        description='Generate regex category patterns from GnuCash transaction history',
    )
    parser.add_argument('gnucash_file', help='Path to the GnuCash XML file')
    parser.add_argument('-o', '--output', default=None,
                        help='Output JSON file (default: print to stdout)')
    parser.add_argument('--exclude', nargs='*',
                        default=['Expenses:Miscellaneous'],
                        help='Account paths to exclude (default: Expenses:Miscellaneous)')
    args = parser.parse_args()

    with open(args.gnucash_file, 'r') as f:
        book = gnucashxml.parse(f)

    history = get_transaction_history(book)
    print(f'Extracted {len(history)} categorized transactions.')

    patterns = generate_regex_patterns(history, exclude_accounts=args.exclude)
    print(f'Generated patterns for {len(patterns)} accounts:\n')

    for account, pattern in sorted(patterns.items()):
        print(f'  {account}')
        print(f'    {pattern}\n')

    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(patterns, f, indent=2, ensure_ascii=False)
        print(f'Saved to {args.output}')
