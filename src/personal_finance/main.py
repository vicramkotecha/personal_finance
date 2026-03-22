import os

import gnucashxml

from dotenv import load_dotenv

from personal_finance.balance_history_report import BalanceHistoryReport
from personal_finance.pie_chart_report import PieChartReport
from personal_finance.report_generator import ReportGenerator
from personal_finance.spain_modelo_720_report import Model720Report
from personal_finance.us_fbar_report import UsFbarReport


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

def run_fbar_report(gnucash_xml_file, csv_path):

    UsFbarReport(balances_csv_path=csv_path).add_report(gnucash_xml_file, None)

def run_modelo_720_report(gnucash_xml_file, csv_path):

    Model720Report(balances_csv_path=csv_path).add_report(gnucash_xml_file, None)

def run_balance_history_report(gnucash_xml_file, report_path):

    generators = [
        BalanceHistoryReport()
    ]

    run_report(gnucash_xml_file, generators, report_path)

def run_combined_report(gnucash_xml_file, report_path, modelo720csvpath, fbarcsvpath):
    generators = [
        Model720Report(balances_csv_path=modelo720csvpath),
        PieChartReport(5, 1),
        BalanceHistoryReport(),
        UsFbarReport(balances_csv_path=fbarcsvpath)
    ]

    run_report(gnucash_xml_file, generators, report_path)

if __name__ == '__main__':
    base_dir = os.environ.get('PERSONAL_FINANCE_BASE_DIR', os.path.expanduser('~'))
    gnucash_xml_file = os.path.join(base_dir, 'accounts.gnucash')
    report_path = os.path.join(base_dir, 'reports', 'combined_report.pdf')
    modelo720csvpath = os.path.join(base_dir, 'reports', 'modelo720.csv')
    fbarcsvpath = os.path.join(base_dir, 'reports', 'fbar.csv')
    run_combined_report(gnucash_xml_file, report_path, modelo720csvpath, fbarcsvpath)
    print('Report generated at: {}'.format(report_path))
