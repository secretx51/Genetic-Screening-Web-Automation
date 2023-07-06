import os

#DIRECTORIES
MAIN_DIR = os.getcwd()

def importFile(filename):
    with open(filename, 'r') as file:
        data = file.read()
    # Split the data based on commas and store the strings in a list
    string_list = [string.strip() for string in data.split(',')]
    # Print the list of strings
    file.close()
    return string_list

def parseFile(filename, key_terms):
    all_go = [] #All the GO numbers
    terms = [] #All the GO numbers want to keep
    current_gene = True #Keeps track of if gene has already been logged
    with open(filename, 'r') as file:
        for line in file:
            if line.find("id: GO:") != -1: #If this is the id row append
                format_line = line.strip().split("id: ")[1]
                if format_line == "GO:0000910": #exlcude cytokinesis
                    continue
                all_go.append(format_line) #append GO number
                current_gene = True #Reset gene track - new gene
            for term in key_terms:
                #if has term we are looking for and haven't appended this gene yet
                if line.find(term) != -1 and current_gene: 
                    terms.append(all_go[-1]) #append term
                    current_gene = False #Say we've appended this gene now
    file.close()
    print(len(all_go))
    return terms

def writeTerms(filename, terms):
    with open(filename, 'w') as file:
            file.truncate(0)
            for term in terms:
                file.write(f'{term},')
    file.close()

def main():
    key_terms = importFile(f"{MAIN_DIR}/GO_search_terms.txt") #Key words to search for
    terms = parseFile(f"{MAIN_DIR}/data/go.txt", key_terms)
    writeTerms(f"{MAIN_DIR}/output_GO_terms.txt", terms)
    print(f"Wrote {len(terms)} terms")

if __name__ == "__main__":
    main()
# end main
