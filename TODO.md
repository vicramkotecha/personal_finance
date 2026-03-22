# Statement Importer — Remaining Work

## Completed

- [x] `load_profile()` — load JSON import profile (file format, column mappings, date format)
- [x] `parse_statement()` — CSV and XLS via pandas, column renaming
- [x] `normalize_transactions()` — date reformatting (M/d/yy), amount→deposit/withdrawal split, category mapping
- [x] `DefaultCategoryMapper` — accepts `account_paths` for future ML/fuzzy/LLM mapping
- [x] `get_all_account_paths()` — walk GnuCash book for full account path list
- [x] `enter_transaction.ps1` — SendKeys automation with autocomplete rejection (Delete), FX dialog handling
- [x] `open_account_register.ps1` — Find Account dialog → Edit > Open Account
- [x] `close_gnucash.ps1` — Ctrl+S then Ctrl+Q
- [x] `import_statement()` orchestrator — full pipeline with progress output
- [x] CLI entry point (`python -m personal_finance.statement_importer`)
- [x] Ctrl-C handling — graceful stop + save/close GnuCash
- [x] Integration test — launch, open register, enter transaction, close (temp dir copy)
- [x] FX Rate Lookup by Date — per-transaction rate via `yfinance`, cached in `FxRateCache`, currency pair from profile
- [x] RegexCategoryMapper — config-driven regex patterns, falls back to `default_transfer_account`

## TODO

### Duplicate Detection
- [ ] Before entering transactions, check for duplicates: match on account + date + description + amount
- [ ] Verify with balance field from statement
- [ ] Skip duplicates, log them, continue with non-duplicates

### Balance Reconciliation
- [ ] After all transactions entered, compare final balance in GnuCash with expected balance from statement
- [ ] If mismatch, insert adjustment row(s) to reconcile

### Future Category Mapping (Mental Bookmark)
- [ ] Fuzzy matching using account_paths
- [ ] ML/LLM-based category suggestion using account_paths + transaction history

### Robustness
- [ ] Handle GnuCash autocomplete edge cases more reliably (cursor position after autocomplete)
- [ ] Add timeouts / retry logic for SendKeys operations
- [ ] Better error messages when GnuCash UI state is unexpected
