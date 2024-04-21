import locale

import matplotlib.pyplot as plt

from personal_finance.book_utils import get_income_and_expenses


class PieChartReport(object):

    def __init__(self, main_pie_chart_item_count, minimum_amount, expenses_csv_path=None):
        self.main_pie_chart_item_count = main_pie_chart_item_count
        self.minimum_amount = minimum_amount
        self.expenses_csv_path = expenses_csv_path


    def add_report(self, book, pdf_pages):

        _income, expenses = get_income_and_expenses(book)
      
        for month_year in sorted(expenses, reverse=True):
            month_year_str = f"{month_year[1]}/{month_year[0]}"
            fig, fig_other = self.add_pie_chart(expenses[month_year].keys(), expenses[month_year].values(), f'Expenses {month_year_str}')
            pdf_pages.savefig(fig)
            if fig_other:
                pdf_pages.savefig(fig_other)
            plt.close(fig)
            if fig_other:
                plt.close(fig_other)

        
    def add_pie_chart(self, labels, values, title):
        ''' Add a pie chart to the pdf report: 
            The first chart will show the top main_pie_chart_item_count categories/expenses and the second chart will show the rest, only if they are above the minimum_amount'''

        count_not_in_other = self.main_pie_chart_item_count
        accounts_and_amounts = sorted(zip(labels, values), key=lambda x: x[1], reverse=True)
        labels, values = zip(*accounts_and_amounts)
        labels = list(labels)
        values = list(values)
        labels, labels_other = labels[:count_not_in_other], labels[count_not_in_other:]
        values, values_other = values[:count_not_in_other], values[count_not_in_other:]

        values_other = [abs(x) for x in values_other]

        labels.append('Other')
        values.append(sum(values_other))

        # enforce minimum amount
        label_values_other = list(zip(*[(label, value) for label, value in zip(labels_other, values_other) if abs(value) > self.minimum_amount]))

        fig, ax = plt.subplots()
        ax.pie(values, labels=labels, autopct=lambda v: f"${locale.format_string('%d', v * float(sum(values)) / 100, grouping=True)}")
        ax.axis('equal')
        fig.tight_layout()

        # Add title to the first pie chart
        total_amount = sum(values)
        ax.set_title(title + f' ${locale.format_string("%d", total_amount, grouping=True)}', fontsize=12, fontweight='bold', pad=20)

        # Adjust the layout of the first figure
        fig.tight_layout(rect=[0, 0.15, 1, 0.85])  # Adjust top and bottom margins

        if not label_values_other:
            return fig, None

        labels_other, values_other = label_values_other

        labels_other = list(labels_other)
        values_other = list(values_other)


        # other chart
        fig_other, ax = plt.subplots()
        ax.pie(values_other, labels=labels_other, autopct=lambda v: f"${locale.format_string('%d', v * float(sum(values_other)) / 100, grouping=True)}")
        ax.axis('equal')
        fig_other.tight_layout()

        # Add title to the first pie chart
        total_amount = sum(values_other)
        ax.set_title('Other ' + title + f' ${locale.format_string("%d", total_amount, grouping=True)}', fontsize=12, fontweight='bold', pad=20)

        # Adjust the layout of the second figure
        fig_other.tight_layout(rect=[0, 0.15, 1, 0.85])  # Adjust top and bottom margins

        return fig, fig_other
    
    
