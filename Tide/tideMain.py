import os
import shutil
import pandas as pd
from pathlib import Path
from tideFormat import *
from tideQuery import RegisterTide
from tideQuery import QueryTide

#DIRECTORIES - DO NOT CHANGE
MAIN_DIR = os.getcwd()
DOWNLOADS = MAIN_DIR + "/downloads" 
DOWNLOAD_DIR = str(Path.home() / "Downloads") 
# CHANGEME for different dataset filtering
COLUMNS = ['Gene', "GSE26712@PRECOG", "GSE13876@PRECOG", "GSE3149@PRECOG", 
            "GSE9899@PRECOG", "GSE17260@PRECOG", 
            "GSE17260", "GSE49997", "GSE32062", "GSE26712", 
            'TCGA1', 'TCGA2','CAF FAP', 'MDSC', 'TAM M2']
EXCLUSION = True

def createDownloadsDir():
    if not os.path.exists(DOWNLOADS):
        os.makedirs(DOWNLOADS)    

def checkFileExists(filename):
    return filename in os.listdir(DOWNLOADS)

def renameFile(gene, exclusion):
    exclusion_str = "_exclusion" if exclusion else ""
    old_name = f"{DOWNLOADS}/{gene + exclusion_str}.csv"
    new_name = f"{DOWNLOADS}/{gene + exclusion_str}.csv"
    shutil.move(old_name, new_name)

def importFile(filename):
    with open(filename, 'r') as file:
        data = file.read()
    # Split the data based on commas and store the strings in a list
    string_list = [string.strip() for string in data.split(',')]
    # Print the list of strings
    file.close()
    return string_list

def writeErrors(errors: list):
    with open(f"{MAIN_DIR}/tideErrors.txt", 'w') as file:
            file.truncate(0)
            for error in errors:
                file.write(f'{error},')
    file.close()

def queryData(genes):
    errors = []
    register = RegisterTide(DOWNLOAD_DIR)
    email = register.registerTide()
    for index, gene in enumerate(genes, 1): #Start enumerate at 1 so doesn't register at start
        if checkFileExists(f"{gene}.csv") \
            and checkFileExists(f"{gene}_exclusion.csv"):
            continue
        if index % 400 == 0: #400 seems reasonable till new account
            email = register.registerTide()
        try:
            QueryTide(DOWNLOAD_DIR, gene, email).tideQuery()
            renameFile(gene, False) #For the expression download file
            renameFile(gene, True) #For the exclusion download file
            print(f"{gene} success query")
        except Exception as error:
            errors.append(gene)
            print(f"{gene} failed query because: \n {error}")
    return errors

def combineDownloads(genes):
    dataframes = []
    errors = []
    for gene in genes:
        try:
            dataframes.append(FilerTide(DOWNLOADS, gene, EXCLUSION).filterData())
            concat_df = pd.concat(dataframes, ignore_index=True)
            concat_df.to_csv(f"{MAIN_DIR}/tide_output.csv", index=False)
            print(f"{gene} success combine")
        except FileNotFoundError as error:
            errors.append(gene)
            print(f"{gene} failed combine because: \n {error}")
    FormatTide(f"{MAIN_DIR}/tide_output.csv", COLUMNS, EXCLUSION).formatTide()\
        .to_csv(f"{MAIN_DIR}/tide_output_formatted.csv")
    return errors

def main():
    genes = importFile(f"{MAIN_DIR}/tideGenes.txt")
    errors = [] #define errors so can combine downloads without querying and won't error
    createDownloadsDir()
    errors = queryData(genes)
    errors.extend(combineDownloads(genes))
    writeErrors(errors)
    print("Success All Genes Formatted")

if __name__ == "__main__":
   main()
