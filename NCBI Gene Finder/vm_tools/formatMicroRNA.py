import string

INPUT_FILE = "/Users/trent/Developer/ncbi/output/microRNAs_genes.csv"
OUTPUT_FILE = "/Users/trent/Developer/ncbi/output/microRNAs_formatted.csv"

def importFile(filename):
    with open(filename, 'r') as file:
        data = file.read()
    # Split the data based on commas and store the strings in a list
    string_list = [string.strip() for string in data.split(',')]
    # Print the list of strings
    file.close()
    return string_list

def writeGenes(filename, genes: list):
    with open(filename, 'w') as file:
            file.truncate(0)
            for gene in genes:
                file.write(f'{gene},')
    file.close()

def formatGenes(genes):
    formatted_genes = []
    for gene in genes:
        if "LET" in gene:
            gene = gene.split("MIR")[1] 
        if "HG" in gene:
            gene = gene.split("HG")[0]
        gene = gene[:3] + '-' + gene[3:]
        for letter in string.ascii_uppercase:
            for number in range(10):
                last_letter = gene.rfind(letter)
                last_number = gene.rfind(str(number))
                if last_letter > 2 and last_letter < last_number:
                    gene = gene[:last_letter + 1] + '-' + gene[last_letter + 1:]
        formatted_genes.append(gene)
    return formatted_genes

def main():
    genes = importFile(INPUT_FILE)
    formatted_genes = formatGenes(genes)
    writeGenes(OUTPUT_FILE, formatted_genes)

if __name__ == "__main__":
    main()
# end main
