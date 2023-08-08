import pandas as pd
from pathlib import Path

MAIN_DIR = str(Path(__file__).resolve().parent) #Directory of python script

def importFile(filename):
    with open(filename, 'r') as file:
        data = file.read()
    # Split the data based on commas and store the strings in a list
    string_list = [string.strip() for string in data.split(',')]
    # Print the list of strings
    file.close()
    return string_list

def getGenes(data_filename):
    df = pd.read_excel(data_filename)
    str_df = df.astype(str)
    return str_df.loc(axis=1)["Symbol"] #All Genes

def filterGenome(genes, target):
    saved_genes = [gene for gene in genes if gene.find(target) == 0]
    print(f"{target} Genes Filtered")
    return saved_genes

def concatGenome(data_filename, terms):
    genes = getGenes(data_filename)
    return [filterGenome(genes, term) for term in terms]

def writeGenes(filename, gene_names: list):
    with open(filename, 'w') as file:
            file.truncate(0)
            for genes in gene_names:
                for gene in genes:
                    file.write(f'{gene},')
    file.close()

def main():
    terms = importFile(f"{MAIN_DIR}/genomeSearchTerms.txt")
    gene_names = concatGenome(f"{MAIN_DIR}/ncbi-data/Homo_sapiens.xlsx", terms)
    writeGenes(f"{MAIN_DIR}/genome_output.txt", gene_names)
    print("Success file outputted")

if __name__ == "__main__":
    main()
# end main
