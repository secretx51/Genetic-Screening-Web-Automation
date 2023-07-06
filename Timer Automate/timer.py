import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys

#DIRECTORIES
DOWNLOAD_DIR = "/Users/trent/Downloads"
DOWNLOADS = "/Users/trent/Developer/timer/downloads"
MAIN_DIR = "/Users/trent/Developer/timer"

def timer(gene):
    options = webdriver.ChromeOptions()
    options.add_argument(f"download.default_directory={DOWNLOAD_DIR}") # Set the download Path
    driver = webdriver.Chrome(options=options)

    driver.get("http://timer.comp-genomics.org/timer/")

    title = driver.title
    #assert title == "Web form"
    driver.implicitly_wait(2)
    driver.find_element(by=By.XPATH, value="//a[normalize-space()='Immune']").click() #Immune tab
    time.sleep(1)
    
    entry_box = driver.find_element(by=By.TAG_NAME, value='select')
    print(Select(entry_box).all_selected_options)
    time.sleep(1)
    text_box = driver.find_element(by=By.TAG_NAME, value='input')
    text_box.send_keys(gene)
    time.sleep(2)
    text_box.send_keys(Keys.ENTER)
    time.sleep(1)
    text_box.send_keys(Keys.ENTER)
    time.sleep(1)

    driver.find_element(by=By.ID, value="geneInput_submit").click() #submit 
    time.sleep(3.25)
    driver.find_element(by=By.ID, value="geneOutput_txt").click() #table
    time.sleep(1)
    driver.find_element(by=By.ID, value="geneOutput_txt").click() #table
    time.sleep(2)
    driver.quit()

def renameFile(gene):
    old_name = f"{DOWNLOAD_DIR}/gene_table.csv"
    new_name = f"{DOWNLOADS}/{gene}.csv"
    os.rename(old_name, new_name)

def filterData(gene):
    filename = f"{DOWNLOADS}/{gene}.csv"
    df = pd.read_csv(filename)
    filtered_df = df[df.iloc[:, 0] == "OV (n=303)"] #OV only
    filtered_df = filtered_df.iloc[:, 1:] #remove first column
    filtered_df.reset_index(drop=True, inplace=True) #reset index for filter
    selected_rows = filtered_df.loc[[3, 5, 6, 7, 8, 9]] #rows to filter out
    selected_rows = selected_rows.transpose() #transpose for correct format
    format_df = selected_rows #naming
    format_df['Gene'] = gene #add gene name
    format_df = format_df.iloc[1:] #Remove orignal name column
    return format_df

def importFile(filename):
    with open(filename, 'r') as file:
        data = file.read()
    # Split the data based on commas and store the strings in a list
    string_list = [string.strip() for string in data.split(',')]
    # Print the list of strings
    file.close()
    return string_list

def writeErrors(errors: list):
    with open('/Users/trent/Developer/timer/timerErrors.txt', 'w') as file:
            file.truncate(0)
            for error in errors:
                file.write(f'{error},')
    file.close()

def checkFileExists(filename):
    for file in os.listdir("/Users/trent/Developer/timer/downloads"):
        if file == filename:
            return True
    return False

def queryData(genes):
    errors = []
    for gene in genes:
        try:
            if checkFileExists(f"/Users/trent/Developer/timer/downloads/{gene}.csv"):
                continue
            timer(gene)
            renameFile(gene)
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
            gene_df = filterData(gene)
            dataframes.append(gene_df)
            concat_df = pd.concat(dataframes)
            concat_df.to_csv("/Users/trent/Developer/timer/timer_output.csv")
            print(f"{gene} success")
        except FileNotFoundError as error:
            errors.append(gene)
            print(f"{gene} failed combine because: \n {error}")
    return errors

def main():
    filename = "/Users/trent/Developer/timer/timerGenes.txt"
    genes = importFile(filename)
    errors = [] #define errors so can combine downloads without querying and won't error
    errors = queryData(genes)
    errors.extend(combineDownloads(genes))
    writeErrors(errors)
    print("Success All Genes Formatted")

if __name__ == "__main__":
    main()
# end main
