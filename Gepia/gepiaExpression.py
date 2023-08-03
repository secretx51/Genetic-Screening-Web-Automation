import pandas as pd
import numpy as np
from pathlib import Path
from gepiaMain import GepiaUtils

# DO NOT CHANGE MAIN_DIR
MAIN_DIR = str(Path(__file__).resolve().parent)
DATA = f"{MAIN_DIR}/data/gepiaOVExpressionData.csv"

class GepiaExpression():
    def __init__(self, gene_input, data_output):
        self._data_output = data_output
        self.database = pd.read_csv(DATA, index_col='Gene Symbol')
        self.genes = GepiaUtils.importFile(gene_input)
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
        GepiaUtils.writeErrors(self.errors, f"{MAIN_DIR}/gepiaExpressionErorrs.txt")
        
def main():
    GepiaExpression(f"{MAIN_DIR}/gepiaGenes.txt", 
                    f"{MAIN_DIR}/gepiaExpression.csv").getExpression()

if __name__ == "__main__":
	main()
