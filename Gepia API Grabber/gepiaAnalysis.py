import os
import PyPDF2
import gepia as gp
import pandas as pd

OUTPUT_DIR = "/Users/trent/Developer/gepia/results/microRNA/" #Main dir
MAIN_DIR = "/Users/trent/Developer/gepia"

class Gepia():
    def __init__(self, input_filename: str, output_dir: str, survival: gp.survival):
        self._survival = survival
        self._input_filename = input_filename
        self._output_dir = output_dir

    def _importFile(self, filename):
        with open(filename, 'r') as file:
            data = file.read()
        # Split the data based on commas and store the strings in a list
        string_list = [string.strip() for string in data.split(',')]
        # Print the list of strings
        file.close()
        return string_list

    def _setParams(self, survival):
        survival.setParam('dataset',['OV'])
        survival.setParam('groupcutoff1', 75)
        survival.setParam('groupcutoff2', 25)
        survival.setOutDir(self._output_dir)

    def _loopQuery(self, survival, genes):
        for gene in genes:
            self._setParams(survival)
            survival.setParam('signature', gene)
            survival.query()

    def _writeErrors(self, errors: list):
        with open(f"{MAIN_DIR}/gepiaErrors.txt", 'w') as file:
                file.truncate(0)
                for error in errors:
                    error_format = error.split('.')[0]
                    file.write(f'{error_format},')
        file.close()

    def _getErrors(self, genes):
        errors = []
        get_gene = lambda filename: str(filename).split('_')[0]
        success_genes = list(map(get_gene, os.listdir(self._output_dir)))
        for gene in genes:
            if gene not in success_genes:
                errors.append(gene)
        self._writeErrors(errors)

    def generatePDFs(self):
        gene_names = self._importFile(self._input_filename)
        self._loopQuery(self._survival, gene_names)
        self._getErrors(gene_names)

class PDFExtractor():
    def __init__(self, directory: str):
        self._directory = directory

    # Function to extract text from a PDF file
    def _extract_text_from_pdf(self, file_path):
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page in reader.pages:
                text += page.extract_text()
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
            text = self._extract_text_from_pdf(OUTPUT_DIR + filename)
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
            if "MonthsPercent" in line:
                words = line.split(' ')
                values.append(words[2]) 
            if "HR(high)" in line:
                HRs = line.split('=')
                HRs = HRs[1].split("\n")
                try:
                    values.append(float(HRs[0]))
                except:
                    values.append(HRs[0]) 
            if "Logrank" in line:
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
        df = pd.DataFrame(lists_of_3 ,columns=['Gene', 'HR', 'LogRank'])
        df.to_csv(self._output_genes, index=False)

def main():
    input_genes = f"{MAIN_DIR}/gepiaGenes.txt"
    output_genes = f"{MAIN_DIR}/gepia_output.csv"
    Gepia(input_genes, OUTPUT_DIR, gp.survival()).generatePDFs()
    PDFExtractor(OUTPUT_DIR).iteratePDF()
    TextExtract(output_genes).outputText()

if __name__ == "__main__":
   main()