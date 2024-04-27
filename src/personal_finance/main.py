import os

import gnucashxml

from personal_finance.balance_history_report import BalanceHistoryReport
from personal_finance.pie_chart_report import PieChartReport
from personal_finance.report_generator import ReportGenerator
from personal_finance.spain_modelo_720_report import Model720Report


def run_report(gnucash_xml_file, generators, report_path):
    with open(gnucash_xml_file, 'r') as file:
        book = gnucashxml.parse(file)

    report_generator = ReportGenerator(generators)
    report_generator.generate_report(book, report_path)


def run_pie_chart_report(gnucash_xml_file, report_path):

    generators = [
        PieChartReport(5, 1),
    ]
    
    run_report(gnucash_xml_file, generators, report_path)

def run_modelo_720_report(gnucash_xml_file, report_path, csv_path):

    generators = [
        Model720Report(balances_csv_path=csv_path)
    ]

    run_report(gnucash_xml_file, generators, report_path)

def run_balance_history_report(gnucash_xml_file, report_path):

    generators = [
        BalanceHistoryReport()
    ]

    run_report(gnucash_xml_file, generators, report_path)

def run_combined_report(gnucash_xml_file, report_path, csv_path):
    generators = [
        Model720Report(balances_csv_path=csv_path),
        PieChartReport(5, 1),
        BalanceHistoryReport()
    ]

    run_report(gnucash_xml_file, generators, report_path)

if __name__ == '__main__':
    home_dir = os.path.expanduser('~')
    gnucash_xml_file = os.path.join(home_dir, 'gnucash', 'accounts.gnucash')
    report_path = os.path.join(home_dir, 'gnucash', 'reports', 'combined_report.pdf')
    csv_path = os.path.join(home_dir, 'gnucash', 'reports', 'balance_sheet.csv')
    run_combined_report(gnucash_xml_file, report_path, csv_path)
