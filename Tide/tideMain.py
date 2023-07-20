import os
import shutil
import argparse
import pandas as pd
from pathlib import Path
from tideFormat import *
from tideQuery import RegisterTide
from tideQuery import QueryTide

class TideUtilities():
    def __init__(self, main_dir, download_dir, downloads, exclusion, genes) -> None:
        self.main_dir = main_dir
        self.download_dir = download_dir
        self.downloads = downloads
        self.exclusion = exclusion
        self.genes = genes

    def checkFileExists(self, filename):
        return filename in os.listdir(self.downloads)

    def renameFile(self, gene, exclusion):
        exclusion_str = "_exclusion" if exclusion else ""
        old_name = f"{self.download_dir}/{gene + exclusion_str}.csv"
        new_name = f"{self.downloads}/{gene + exclusion_str}.csv"
        shutil.move(old_name, new_name)

    @staticmethod
    def createDownloadsDir(downloads):
        if not os.path.exists(downloads):
            os.makedirs(downloads)   

    @staticmethod
    def importFile(filename):
        with open(filename, 'r') as file:
            data = file.read()
        # Split the data based on commas and store the strings in a list
        string_list = [string.strip() for string in data.split(',')]
        # Print the list of strings
        file.close()
        return string_list

    @staticmethod
    def writeErrors(filename, errors: list):
        with open(filename, 'w') as file:
                file.truncate(0)
                for error in errors:
                    file.write(f'{error},')
        file.close()

class TideQuery(TideUtilities):
    def __init__(self, main_dir, download_dir, downloads, exclusion, genes):
        super().__init__(main_dir, download_dir, downloads, exclusion, genes)
        self.errors = []

    def register(self):
        self.register = RegisterTide(self.download_dir) # type: ignore
        self.email = self.register.registerTide()
        
    def ifFileExists(self, gene):
        if self.exclusion:
            return self.checkFileExists(f"{gene}.csv") \
                and self.checkFileExists(f"{gene}_exclusion.csv")
        else:
            return self.checkFileExists(f"{gene}.csv")
        
    def renameFile(self, gene):
        super().renameFile(gene, False)
        if self.exclusion:
            super().renameFile(gene, True)

    def queryData(self):
        self.register()
        for index, gene in enumerate(self.genes, 1): #Start enumerate at 1 so doesn't register at start
            if self.ifFileExists(gene): #Check if file already in downloads, don't need to query.
                continue
            if index % 400 == 0: #400 seems reasonable till new account
                self.email = self.register.registerTide()
            try:
                QueryTide(self.download_dir, gene, self.email).tideQuery()
                self.renameFile(gene)
                print(f"{gene} success query")
            except Exception as error:
                self.errors.append(gene)
                print(f"{gene} failed query because: \n {error}")
        return self.errors
    
class TideFormat(TideUtilities):
    def __init__(self, main_dir, download_dir, downloads, exclusion, genes, cancers) -> None:
        super().__init__(main_dir, download_dir, downloads, exclusion, genes)
        self.cancers = cancers
        self.dataframes = []
        self.errors = []

    def combineDownloads(self):
        for gene in self.genes:
            try:
                self.dataframes.append(
                    FilerTide(self.downloads, gene, self.exclusion, self.cancers).filterData())
                concat_df = pd.concat(self.dataframes, ignore_index=True)
                concat_df.to_csv(f"{self.main_dir}/tide_output.csv", index=False)
                print(f"{gene} success combine")
            except FileNotFoundError as error:
                self.errors.append(gene)
                print(f"{gene} failed combine because: \n {error}")
    
    def downloadFormat(self):
        self.combineDownloads()

        columns = self.importFile(f"{self.main_dir}/tideCohorts.txt")
        FormatTide(f"{self.main_dir}/tide_output.csv", 
                   columns, self.exclusion).formatTide()\
                    .to_csv(f"{self.main_dir}/tide_output_formatted.csv", index=False)
        
        return self.errors

class Tide():
    def __init__(self, main_dir, download_dir, downloads, exclusion, query, cancers) -> None:
        self.main_dir = main_dir
        self.downloads = downloads
        self.query = query
        self.errors = []

        genes = TideUtilities.importFile(f"{self.main_dir}/tideGenes.txt")
        self.tideQuery = TideQuery(main_dir, download_dir, downloads, exclusion, genes)
        self.tideFormat = TideFormat(main_dir, download_dir, downloads, exclusion, genes, cancers)

    def tideMain(self):
        TideUtilities.createDownloadsDir(self.downloads)
        # if self.query:
        #     self.errors.extend(self.tideQuery.queryData())
        self.errors.extend(self.tideFormat.downloadFormat())
        TideUtilities.writeErrors(f"{self.main_dir}/tideErrors.txt", self.errors)
        print("Success All Genes Formatted")

def argParser(main_dir, downloads):
    parser = argparse.ArgumentParser(
        description='Gets Tide T_Dysfunction from expression and exclusion data')

    parser.add_argument("-o", "--outdir", default=main_dir, 
                        help="Directory to where outputted files and csv download files should be stored" 
                        + f"\nDefault is {main_dir}")
    
    parser.add_argument("-d", "--downloads", default=downloads, 
                        help="Change specifically where the csv files are downloaded to." 
                        + f"\nDefault is {downloads}")

    cancer_types = ["Head Neck", "Colorectal", "Lung", "Melanoma", "Lymphoma", "Ovary", "Leukemia",
                    "Breast", "Glioblastoma", "Myeloma", "Sarcoma", "Liver", "Bladder", "Brain",	
                    "Ovarian", "Esophageal", "Kidney"]
    parser.add_argument("-c", "--cancer", choices=cancer_types, default=['Ovarian', 'Ovary'], 
                        action='append', help="Cancer type to run Tide on. Default is: ['Ovarian', 'Ovary']." 
                        + '\nValid cancer types are: '+', '.join(cancer_types), metavar='')
    
    parser.add_argument("-q", "--query", action='store_false', 
                        help="Do NOT query Tide just combine and format downloaded genes.")
    
    parser.add_argument("-e", "--exclusion", action='store_false', 
                        help="Do NOT download or format exclusion values from Tide.")
    
    return parser.parse_args()

def main():
    MAIN_DIR = str(Path(__file__).resolve().parent) #Directory of python script
    DOWNLOADS = MAIN_DIR + "/Downloads"
    DOWNLOAD_DIR = str(Path.home() / "Downloads") #System downloads path.

    args = argParser(MAIN_DIR, DOWNLOADS)
    Tide(args.outdir, DOWNLOAD_DIR, args.downloads, 
         args.exclusion, args.query, args.cancer).tideMain()

if __name__ == "__main__":
   main()
