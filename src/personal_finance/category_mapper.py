class DefaultCategoryMapper:

    def __init__(self, default_transfer_account, account_paths):
        self.default_transfer_account = default_transfer_account
        self.account_paths = account_paths

    def map(self, description):
        return self.default_transfer_account
