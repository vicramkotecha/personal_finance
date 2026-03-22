
# Personal Finance Tracking System

## Project Overview

This system is built as a wrapper around Gnucash, providing enhanced reporting for expenses, balance history, cash flow, and tax reporting. 

## Key Features

- **Reporting Suite**: Generate reports for expenses, income, cash flow, balance history, and tax compliance (including support for country-specific forms like Spain's Modelo 720 and US FBAR).
- **Data Visualization**: Interactive charts and graphs for visualizing spending patterns, account balances, and financial trends.

## System Architecture

### 1. Import & Categorization Module
- Imports transaction data from various file formats.
- Categorizes transactions using rule-based methods.

### 2. Reporting & Visualization
- Generates standard and custom financial reports.
- Visualizes data with pie charts, history graphs, and summary tables.

### 3. Tax & Compliance Tools
- Prepares data for country-specific tax forms (e.g., Spain Modelo 720, US FBAR).
- Summarizes foreign account holdings and reportable transactions.

### 4. Extensibility & Integration
- Modular design allows for easy addition of new data sources, reports, and integrations.
- Automated calculation and rollup of asset values in different denominations for unified reporting.
