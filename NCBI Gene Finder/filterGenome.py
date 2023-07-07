import os
import pandas as pd

MAIN_DIR = os.getcwd()

def importFile(filename):
    with open(filename, 'r') as file:
        data = file.read()
    # Split the data based on commas and store the strings in a list
    string_list = [string.strip() for string in data.split(',')]
    # Print the list of strings
    file.close()
    return string_list

def filterGenome(target):
    saved_genes = []
    df = pd.read_excel(f"{MAIN_DIR}/data/Homo_sapiens.xlsx")
    str_df = df.astype(str)
    genes = str_df.loc(axis=1)["Symbol"]
    for gene in genes:
        if gene.find(target) == 0:
            saved_genes.append(gene)
    print(f"{target} Genes Filtered")
    return saved_genes

def concatGenome(terms):
    dfs = []
    for term in terms:
        dfs.append(filterGenome(term))
    return pd.concat(dfs)

def main():
    terms = importFile(f"{MAIN_DIR}/genomeSearchTerms.txt")
    concat_df = concatGenome(terms)
    concat_df.to_csv(f"{MAIN_DIR}/microRNAs_genes.csv", index=False)
    print("Success file outputted")

if __name__ == "__main__":
    main()
# end main
    