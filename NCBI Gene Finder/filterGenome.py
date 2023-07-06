import pandas as pd

GENOME = "/Users/trent/Developer/ncbi/downloads/NCBI Genomes/Homo_sapiens.xlsx"
OUTPUT_DIR = "/Users/trent/Developer/ncbi/output"
SERCH_TERMS = "MIR", "LET"

def filterGenome(target):
    saved_genes = []
    df = pd.read_excel(GENOME)
    str_df = df.astype(str)
    genes = str_df.loc(axis=1)["Symbol"]
    for gene in genes:
        if gene.find(target) == 0:
            saved_genes.append(gene)
    print(f"{target} Genes Filtered")
    return saved_genes

def concatGenome(*searchterms):
    dfs = []
    for term in searchterms:
        dfs.append(filterGenome(term))
    return pd.concat(dfs)

def main():
    concat_df = concatGenome(SERCH_TERMS)
    concat_df.to_csv(f"{OUTPUT_DIR}/microRNAs_genes.csv", index=False)
    print("Success file outputted")

if __name__ == "__main__":
    main()
# end main
    