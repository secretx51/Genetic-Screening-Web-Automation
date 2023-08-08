import os
import PyPDF2
import argparse
import gepia as gp
import pandas as pd
import numpy as np
from pathlib import Path

# DO NOT CHANGE MAIN_DIR
MAIN_DIR = str(Path(__file__).resolve().parent)

class GepiaUtils():
    @staticmethod
    def importFile(filename):
        with open(filename, 'r') as file:
            data = file.read()
        # Split the data based on commas and store the strings in a list
        string_list = [string.strip() for string in data.split(',')]
        # Print the list of strings
        file.close()
        return string_list
    
    def writeErrors(self, errors: list, filename):
        with open(filename, 'w') as file:
                file.truncate(0)
                for error in errors:
                    error_format = error.split('.')[0]
                    file.write(f'{error_format},')
        file.close()

class Gepia(GepiaUtils):
    def __init__(self, genes, output_dir: str, cancer: str):
        self.genes = genes
        self._output_dir = output_dir
        self._cancer = cancer
        self._survival = gp.survival()

    def _createDownloadsDir(self):
        if not os.path.exists(self._output_dir):
            os.makedirs(self._output_dir)    

    def _setParams(self, survival):
        survival.setParam('dataset',[self._cancer])
        survival.setParam('groupcutoff1', 75)
        survival.setParam('groupcutoff2', 25)
        survival.setOutDir(self._output_dir)

    def _loopQuery(self, survival, genes):
        for gene in genes:
            self._setParams(survival)
            survival.setParam('signature', gene)
            survival.query()

    def _getErrors(self, genes):
        get_gene = lambda filename: str(filename).split('_')[0]
        success_genes = list(map(get_gene, os.listdir(self._output_dir)))
        errors = [gene for gene in genes if gene not in success_genes]
        self.writeErrors(errors, f"{MAIN_DIR}/gepiaErrors.txt")

    def generatePDFs(self):
        self._createDownloadsDir()
        self._loopQuery(self._survival, self.genes)
        self._getErrors(self.genes)

class PDFExtractor():
    def __init__(self, genes, directory: str):
        self.genes = genes
        self._directory = directory

    # Function to extract text from a PDF file
    def _extract_text_from_pdf(self, file_path):
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''.join(page.extract_text() for page in reader.pages)
        file.close()
        return text
    
    def _writeText(self, text):
        with open(f"{MAIN_DIR}/gepiaOutput.txt", 'a') as file:
            file.write(text)
        file.close()

    # Iterate through the PDF files and extract text from each file
    def iteratePDF(self):
        files = os.listdir(self._directory)
        for filename in files:
            gene_name = filename.split('/')[-1].split('_')[0] # Final Dir First Word
            if gene_name not in self.genes: # If not in gene list skip
                continue
            text = self._extract_text_from_pdf(self._directory + filename)
            self._writeText(text)
            
class TextExtract():
    def __init__(self, output_genes):
        self._output_genes = output_genes

    def _importLines(self):
        with open(f"{MAIN_DIR}/gepiaOutput.txt", 'r') as file:
            lines = file.readlines()
        file.close()
        return lines

    def _filterText(self, lines):
        values = []
        for line in lines:
            if "MonthsPercent" in line: #Get gene
                words = line.split(' ')
                values.append(words[2]) 
            elif "HR(high)" in line:
                HRs = line.split('=')
                HRs = HRs[1].split("\n")
                try:
                    values.append(float(HRs[0]))
                except:
                    values.append(HRs[0]) 
            elif "Logrank" in line:
                Logs = line.split('=')
                Logs = Logs[1].split("\n")
                try:
                    values.append(float(Logs[0]))
                except:
                    values.append(Logs[0])
        return values
    
    def outputText(self):
        lines = self._importLines()
        values = self._filterText(lines)
        lists_of_3 = [values[i:i+3] for i in range(0, len(values), 3)]
        df = pd.DataFrame(lists_of_3 ,columns=['Gene', 'LogRank', 'HR'])
        df.to_csv(self._output_genes, index=False)
        
class GepiaExpression(GepiaUtils):
    def __init__(self, genes, data_output):
        self.genes = genes
        self._data_output = data_output
        
        data = f"{MAIN_DIR}/data/gepiaOVExpressionData.csv"
        self.database = pd.read_csv(data, index_col='Gene Symbol')
        self.errors = []
    
    def filterDatabaseGenes(self):
        # Initialize lists to store found and not-found index names
        matched_genes = []
        # Iterate through the list and separate found and not-found index names
        for gene in self.genes:
            if gene in self.database.index:
                matched_genes.append(gene)
            else:
                self.errors.append(gene)
        # Return filtered genes
        self.database = self.database.loc[matched_genes]
    
    def log2Column(self, column) -> None:
        self.database[f'Log2 {column}'] = self.database[column].apply(lambda x: np.log2(x))
        
    def dropColumns(self):
        columns_to_drop = [0, 1, 2]
        self.database.drop(self.database.columns[columns_to_drop], axis=1, inplace=True)
        
    def reorderColumns(self):
        column_order = [2, 3, 0, 1]
        self.database = self.database.iloc[:, column_order]
    
    def getExpression(self):
        self.filterDatabaseGenes()
        self.log2Column('Median (Tumor)')
        self.log2Column('Median (Normal)')
        self.dropColumns()
        self.reorderColumns()
        # Outputs
        self.database.to_csv(self._data_output)
        self.writeErrors(self.errors, f"{MAIN_DIR}/gepiaExpressionErrors.txt")
        print("Expression data success, errors written.")

def argParser():
    parser = argparse.ArgumentParser(
        description='Gets Logrank, HR(high), log2-Fold-Change from Gepia survival and expression data')

    parser.add_argument("-o", "--outdir", default=f"{MAIN_DIR}/downloads/", 
                        help=f"Directory to where pdf graphs should be stored. Default is {MAIN_DIR}/downloads/.")
    parser.add_argument("-c", "--cancer", choices=gp.CANCERType, default='OV', 
                        help="Cancer type to run Gepia on. Default is: 'OV'." 
                        + '\nValid cancer types are: '+', '.join(gp.CANCERType), metavar='')
    parser.add_argument("-g", "--gepia", action='store_false', 
                        help="With this flag DO NOT search Gepia use files in downloads instead.")
    parser.add_argument("-e", "--expression", action='store_true', 
                        help="Flag to generate expression data only, NO survival data.")
    
    return parser.parse_args()

def main():
    genes = GepiaUtils.importFile(f"{MAIN_DIR}/gepiaGenes.txt")
    output_genes = f"{MAIN_DIR}/gepia_output.csv"
    output_expression = f"{MAIN_DIR}/gepia_expression_output.csv"
    parser = argParser() #Namespace
    
    GepiaExpression(genes, output_expression).getExpression()
    if parser.expression: #Skip remaining code only generates expression data.
        return None
    
    if parser.gepia:
        Gepia(genes, parser.outdir, parser.cancer).generatePDFs()
    PDFExtractor(genes, parser.outdir).iteratePDF()
    TextExtract(output_genes).outputText()

if __name__ == "__main__":
    main()
