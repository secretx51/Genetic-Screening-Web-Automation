import numpy as np

INPUT_FILE = "/Users/trent/Developer/ncbi/output/microRNAs_genes.csv"
OUT_DIR = "/Users/trent/Developer/ncbi/splits/microRNA"
PROJ_NAME = "microRNA"
PARTS = 5 #Number of parts to split csv into

def importFile(filename):
    with open(filename, 'r') as file:
        data = file.read()
    # Split the data based on commas and store the strings in a list
    string_list = [string.strip() for string in data.split(',')]
    # Print the list of strings
    file.close()
    return string_list

def writeFile(filename, genes):
    with open(filename, 'w') as file:
            file.write(genes)
    file.close()

def splitGenes(genes):
    split_genes = np.array_split(genes, PARTS) #Numpy array split into parts
    for index, part in enumerate(split_genes): #For each part in array
        gene_list = ','.join(part.astype(str)) #Make array string join with commas
        writeFile(f"{OUT_DIR}/{PROJ_NAME}_{index}.csv", gene_list) #Write the file
    return len(split_genes[0])

def main():
    genes = importFile(INPUT_FILE) #Returns list of all genes
    length = splitGenes(genes)
    print(f"Success split into {PARTS} parts, of length {length}")

if __name__ == "__main__":
    main()
# end main
