import time
import cv2
import os
import numpy as np
import pandas as pd
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#DIRECTORIES
MAIN_DIR = str(Path(__file__).resolve().parent)
DOWNLOADS = MAIN_DIR + "/downloads" 
DOWNLOAD_DIR = str(Path.home() / "Downloads") 
ERROR = 5

def linkedOmics(gene):
    options = webdriver.ChromeOptions()
    options.add_argument(f"download.default_directory={DOWNLOAD_DIR}") # Set the download Path
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, timeout=600)
    driver.set_page_load_timeout(600)

    driver.get("https://linkedomics.org/admin.php")

    title = driver.title
    #assert title == "Web form"
    driver.implicitly_wait(4)

    #LOGIN
    driver.find_element(by=By.XPATH, value="//input[@name='guestuser_submit']").click()
    time.sleep(2.5)

    #STEP1 - cancer type
    wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"(//iframe)[1]")))
    textarea = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@aria-controls='tblCancerTypes']")))
    textarea.send_keys("TCGA_OV")
    #driver.find_element(by=By.XPATH, value="//input[@aria-controls='tblCancerTypes']").send_keys("sk")
    time.sleep(0.5)
    driver.find_element(by=By.XPATH, value="//input[@name='cancer_id']").click()
    time.sleep(2)
    #STEP2 - search dataset
    driver.find_element(by=By.XPATH, value="//input[@aria-controls='tblSearchDataset']").send_keys("His")
    time.sleep(0.5)
    driver.find_element(by=By.XPATH, value="//input[@name='subcancer_id']").click()
    time.sleep(2)
    #STEP3 - gene
    driver.find_element(by=By.XPATH, value="//span[normalize-space()='Click to view']").click()
    time.sleep(1)
    text_box = driver.find_element(by=By.XPATH, value="//input[@class='chosen-search-input']")
    text_box.send_keys(gene)
    time.sleep(1)
    text_box.send_keys(Keys.ENTER)
    time.sleep(1.5)
    #STEP4 - target dataset
    driver.find_element(by=By.XPATH, value="//input[@aria-controls='tblTargetDataset']").send_keys("His")
    time.sleep(0.5)
    driver.find_element(by=By.XPATH, value="//input[@name='target_dataset']").click()
    time.sleep(2)
    #STEP5 - stat method
    stat_box = driver.find_element(by=By.ID, value="subcat5")
    Select(stat_box).select_by_value('PC')
    time.sleep(1)
    driver.find_element(by=By.XPATH, value="//input[@id='submitp1']").click()
    time.sleep(2.5)

    #STEP6 - VIEW SHEET
    dot_box = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@name='list1a']")))
    dot_box.click()
    time.sleep(1.5)
    driver.switch_to.frame("iframe-1")
    time.sleep(1)
    driver.find_element(by=By.XPATH, value="//a[normalize-space()='LinkInterpreter']").click()
    time.sleep(1)
    #STEP7 - TOOL METHOD
    wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"(//iframe)[2]")))
    tool_box = wait.until(EC.visibility_of_element_located((By.ID, "tool")))
    time.sleep(0.5)
    for tool in tool_box.find_elements(by=By.TAG_NAME, value='option'):
        if tool.text == 'gsea' or 'Gene Set Enrichment Analysis (GSEA)':
            tool.click() # select() in earlier versions of webdriver
    time.sleep(1)
    #STEP 8 Criteria
    criteria_box = driver.find_element(by=By.ID, value="method")
    for criteria in criteria_box.find_elements(by=By.TAG_NAME, value='option'):
        if criteria.text == 'FDR' or 'fdr':
            criteria.click() # select() in earlier versions of webdriver
    time.sleep(1)
    # Store the ID of the original window
    original_window = driver.current_window_handle
    time.sleep(1)
    driver.find_element(by=By.XPATH, value="//input[@id='sp2']").click()
    
    wait.until(EC.number_of_windows_to_be(2))
     # Loop through until we find a new window handle
    for window_handle in driver.window_handles:
        if window_handle != original_window:
            driver.switch_to.window(window_handle)
            break

    # Wait for the new tab to finish loading content
    time.sleep(2)
    print("Loop started")
    attemtps = 0
    while True:
        try:
            EC.frame_to_be_available_and_switch_to_it((By.XPATH,"(//iframe)[1]"))
            driver.find_element(by=By.XPATH, value="//span[normalize-space()='Table']").click()
            print("Analysis complete")
            break
        except Exception:
            failed = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/i/a")))
            driver.get_screenshot_as_file(f"{MAIN_DIR}/linkedomics_output.png")
            error = compareImages()

            if failed.get_attribute('textContent') == 'Broad Gene Set Enrichment Analysis (GSEA)' and \
            error < 0.4:
                driver.refresh()
                print(f"Refreshed \n error was {error}")
                attemtps += 1
            elif error > ERROR:
                print(f"Analysis Completed \n error was {error}")
                break
            elif attemtps > 10:
                raise TimeoutError("Attempts exceeded 10")
                break
            else:
                print(f"Continue \n error was {error}")

    time.sleep(1)
    wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"(//iframe)[1]")))
    time.sleep(8)
    table_click = wait.until(EC.visibility_of_element_located((By.XPATH, "//span[normalize-space()='Table']")))
    time.sleep(3)
    #click table expand elements
    table_click.click()

    time.sleep(2) 
    elements_box = driver.find_element(by=By.XPATH, value="//*[@id=\"wg-result-table\"]/div[2]/span/select")
    for elements in elements_box.find_elements(by=By.TAG_NAME, value='option'):
        if elements.text == '1000' or 'ALL' or 'All':
            elements.click() # select() in earlier versions of webdriver
    time.sleep(1)

    #SCRUB TABLE
    table_DF = pd.read_html(driver.page_source)[0]
    time.sleep(1)
    driver.quit()
    return table_DF

def compareImages():
    og_img = cv2.imread(f"{MAIN_DIR}/linkedomics_output_failed.png")
    new_img = cv2.imread(f"{MAIN_DIR}/linkedomics_output.png")

    og_img = cv2.cvtColor(og_img, cv2.COLOR_BGR2GRAY)
    new_img = cv2.cvtColor(new_img, cv2.COLOR_BGR2GRAY)

    error = mse(og_img, new_img)

    return error

def mse(img1, img2):
    h, w = img1.shape
    h2, w2 = img2.shape
    img1 = cv2.resize(img1, (w2, h2))

    diff = cv2.subtract(img1, img2)
    err = np.sum(diff**2)
    mse = err/(float(h*w))
    return mse

def filterData(gene, terms):
    df = pd.read_csv(f"{DOWNLOADS}/{gene}.csv")
    columns_to_remove = [0,3,4,5,7] # List of column indices to remove
    df = df.drop(df.columns[columns_to_remove], axis=1) # Remove the specified columns
    df["Gene"] = gene

    filtered_df = df[df['Gene Set'].isin(terms)] #Remove all rows that don't match GO terms
    return filtered_df

def importFile(filename):
    with open(filename, 'r') as file:
        data = file.read()
    # Split the data based on commas and store the strings in a list
    string_list = [string.strip() for string in data.split(',')]
    # Print the list of strings
    file.close()
    return string_list

def writeErrors(errors: list):
    with open(f"{MAIN_DIR}/linkedomicsErrors.txt", 'w') as file:
            file.truncate(0)
            for error in errors:
                file.write(f'{error},')
    file.close()

def createDownloadsDir():
    if not os.path.exists(DOWNLOADS):
        os.makedirs(DOWNLOADS)    

def checkFileExists(filename):
    return filename in os.listdir(DOWNLOADS)

def queryData(genes):
    errors = []
    for gene in genes:
        try:
            if checkFileExists(f"{gene}.csv"):
                    continue
            df = linkedOmics(gene) #obtain db webpage
            df.to_csv(f"{DOWNLOADS}/{gene}.csv")
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
            terms = importFile(f"{MAIN_DIR}/GeneOntology/output_GO_terms.txt") #Import saved terms
            gene_df = filterData(gene, terms) #filter the db
            dataframes.append(gene_df) #append to the dataframe list
            concat_df = pd.concat(dataframes, ignore_index=True) #concat all dataframes in list
            concat_df.to_csv(f"{MAIN_DIR}/linkedomics_output.csv", index=False) #write concat df to csv
            print(f"{gene} success")
        except FileNotFoundError as error:
            errors.append(gene)
            print(f"{gene} failed combine because: \n {error}")
    return errors

def countGenes(column):
    df = pd.read_csv(f"{MAIN_DIR}/linkedomics_output.csv")
    return df[column].value_counts()

def sortColumns(filename):
    df = pd.read_csv(filename)
    og_columns = ["Gene Set", "Size", "P Value", "Description", "Gene"]
    if len(df.columns) != len(og_columns):
        difference = len(df.columns) - len(og_columns)
        for missing in range(difference):
            og_columns.append(str(missing))
    df.columns = og_columns
    return df.sort_values('Gene')

def save_excel_sheet(df, filepath, sheetname, index=False):
    # Create file if it does not exist
    if not os.path.exists(filepath):
        df.to_excel(filepath, sheet_name=sheetname, index=index)
    # Otherwise, add a sheet. Overwrite if there exists one with the same name.
    else:
        with pd.ExcelWriter(filepath, engine='openpyxl', if_sheet_exists='replace', mode='a') as writer:
            df.to_excel(writer, sheet_name=sheetname, index=index)

def formatData(value):
    df_sorted = sortColumns(f"{MAIN_DIR}/linkedomics_output.csv")
    columns = countGenes("Gene Set").index #Get a list of all unique GO Terms
    genes = []
    complete_rows = []
    current_row = np.zeros(len(columns))
    
    for i, row in df_sorted.iterrows(): #For each row, need i to get row
        current_gene = row['Gene']
        if len(genes) != 0:
            if current_gene != genes[-1]:
                append_row = current_row.tolist() #Convert array to list
                append_row[0] = genes[-1] #Add gene names to list
                complete_rows.append(append_row) #Append list to completed rows
                current_row = np.zeros(len(columns)) #Reset current row to array

        for index, column in enumerate(columns):
            if row['Gene Set'] == column:
                if str(row[value]).find('<') != -1: #If has < character
                    row[value] = float(str(row[value]).split('<')[1]) #Delete < character and convert to float
                current_row[index] = row[value]

        genes.append(current_gene)
    
    output_df = pd.DataFrame(complete_rows, columns=columns) #Dataframe of all the completed rows
    output_df.replace(to_replace = 0, value = '', inplace=True) #Replace all zeroes from array to empty
    save_excel_sheet(output_df, f"{MAIN_DIR}/linkedomics_output_formatted.xlsx", value)

def main():
    genes = importFile(f"{MAIN_DIR}/linkedomicsGenes.txt")
    errors = [] #define errors so can combine downloads without querying and won't error
    createDownloadsDir()

    # errors = queryData(genes)
    errors.extend(combineDownloads(genes))
    countGenes("Gene").to_csv(f"{MAIN_DIR}/linkedomics_counts.csv") #Output a count file
    
    formatData("P Value")
    formatData("Description")
    writeErrors(errors)
    print("Success All Genes Formatted")

if __name__ == "__main__":
    main()
# end main
