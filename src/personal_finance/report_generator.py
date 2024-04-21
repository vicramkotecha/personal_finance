import matplotlib
matplotlib.use('Agg') # Required to generate pdf reports without a display

from matplotlib.backends.backend_pdf import PdfPages

class ReportGenerator(object):
    def __init__(self, generators):
        self.generators = generators
        
    def generate_report(self, book, output_path):
        
        try:
            pp = PdfPages(output_path)

            for generator in self.generators:
                generator.add_report(book, pp)

        finally:
            pp.close()        

        return 'Report generated'

