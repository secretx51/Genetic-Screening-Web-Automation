import time
import string
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Driver():
    def __init__(self, downloads) -> None:
        self._downloads = downloads

    def createDiver(self, webpage):
        options = webdriver.ChromeOptions()
        options.add_argument(f"download.default_directory={self._downloads}") # Set the download Path
        driver = webdriver.Chrome(options=options)
        driver.get(webpage)
        driver.implicitly_wait(2)
        return driver

class RegisterTide(Driver):
    def _randomString(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))

    def _sendVerification(self):
        driver = self.createDiver("http://tide.dfci.harvard.edu/login/")
        #Register
        driver.find_element(by=By.XPATH, value="//*[@id=\"app\"]/div[2]/div[1]/div/div[1]/button").click()
        time.sleep(0.5)
        #Enter email into box
        email_rand = self._randomString()
        email = email_rand + "@inboxkitten.com"
        email_box = driver.find_element(by=By.XPATH, value="//*[@id=\"app\"]/div[2]/div[1]/div/form/div/div[2]/input")
        email_box.send_keys(email)
        time.sleep(0.5)
        #Press submit
        driver.find_element(by=By.XPATH, value="//*[@id=\"app\"]/div[2]/div[1]/div/form/div/div[3]/div[2]/button").click()
        time.sleep(0.5)
        driver.quit()
        return email_rand

    def _getCode(self, email_rand):
        driver = self.createDiver("https://inboxkitten.com/")
        wait = WebDriverWait(driver, timeout=600)
        #Input email
        email_box = driver.find_element(by=By.ID, value="email-input")
        email_box.clear()
        email_box.send_keys(email_rand)
        time.sleep(0.5)
        #Press Submit
        driver.find_element(by=By.XPATH, value="//*[@id=\"app\"]/div/div[3]/div[2]/form/div[2]/input").click()
        time.sleep(2)
        #Open Email
        driver.find_element(by=By.XPATH, value="//div[@class='row-subject']").click()
        time.sleep(0.5)
        #Get verification code
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "message-content")))
        code_element = driver.find_element(by=By.XPATH, value="/html/body/p/strong")
        code = code_element.get_attribute('textContent')
        time.sleep(0.5)
        driver.quit()
        return code
        
    def _createAccount(self, email_rand, code):
        driver = self.createDiver("http://tide.dfci.harvard.edu/login/")
        #Register
        driver.find_element(by=By.XPATH, value="//*[@id=\"app\"]/div[2]/div[1]/div/div[1]/button").click()
        time.sleep(0.5)
        #Enter Names
        for i in range(1,3):
            driver.find_element(by=By.XPATH, value=f"//*[@id=\"app\"]/div[2]/div[1]/div/form/div/div[1]/div[{i}]/input")\
                .send_keys("Steve")
            time.sleep(0.5)
        #Enter email into box
        email = email_rand + "@inboxkitten.com"
        email_box = driver.find_element(by=By.XPATH, value="//*[@id=\"app\"]/div[2]/div[1]/div/form/div/div[2]/input")
        email_box.send_keys(email)
        time.sleep(0.5)
        #Enter Code
        driver.find_element(by=By.XPATH, value="//*[@id=\"app\"]/div[2]/div[1]/div/form/div/div[3]/div[1]/input")\
            .send_keys(code)
        time.sleep(0.5)
        #Institution
        for i in range(1,5):
            driver.find_element(by=By.XPATH, value=f"//*[@id=\"app\"]/div[2]/div[1]/div/form/div/div[4]/div[{i}]/input")\
                .send_keys("aaaa")
            time.sleep(0.5)
        #Checkbox
        driver.find_element(by=By.XPATH, value="//*[@id=\"app\"]/div[2]/div[1]/div/form/div/div[5]/div/div/input")\
                .click()
        time.sleep(0.5)
        #Password
        for i in range(1,3):
            driver.find_element(by=By.XPATH, value=f"//*[@id=\"app\"]/div[2]/div[1]/div/form/div/div[6]/div[{i}]/input")\
                .send_keys("password")
            time.sleep(0.5)
        #Submit
        driver.find_element(by=By.XPATH, value="//*[@id=\"app\"]/div[2]/div[1]/div/div/div[2]/h3/button")\
                .click()
        time.sleep(3.5)
        driver.quit()
        return email

    def registerTide(self):
        email_rand = self._sendVerification()
        code = self._getCode(email_rand)
        return self._createAccount(email_rand, code)

class QueryTide(Driver):
    def __init__(self, downloads, gene, email) -> None:
        super().__init__(downloads)
        self._gene = gene
        self._email = email

    def _downloadCSV(self, driver, dataType):
        for i in range(1,8):
            element = driver.find_element(by=By.ID, value=f'ui-id-{i}')
            if element.get_attribute('textContent') == dataType:
                driver.find_element(by=By.ID, value=f'ui-id-{i}').click()
                time.sleep(1)
                driver.find_element(by=By.ID, value=f'export_{i}').click()
                break
        time.sleep(1)
        alert = driver.switch_to.alert
        time.sleep(1)
        exclusion_str = "_exclusion" if dataType == "Exclusion" else ""
        alert.send_keys(self._gene + exclusion_str)
        time.sleep(1)
        alert.accept()
        time.sleep(1)

    def tideQuery(self):
        driver = self.createDiver("http://tide.dfci.harvard.edu/login/")
        #LOGIN
        driver.find_element(by=By.XPATH, value="//input[@placeholder='Email']").send_keys(self._email)
        time.sleep(0.5)
        pass_box = driver.find_element(by=By.XPATH, value="//input[@placeholder='Password']")
        pass_box.send_keys("password")
        time.sleep(0.1)
        driver.find_element(by=By.CLASS_NAME, value="button.ui.red.button").click()
        #STEP1 - cancer type
        time.sleep(1.5)
        driver.find_element(by=By.XPATH, value="//a[normalize-space()='Query Gene']").click()
        #STEP2 Enter GENE
        driver.find_element(by=By.XPATH, value="//input[@id='mainSrcInput']").send_keys(self._gene)
        time.sleep(0.5)
        driver.find_element(by=By.XPATH, value="//button[normalize-space()='Search']").click()
        #Step3 New Page
        time.sleep(1.5)
        driver.find_element(by=By.XPATH, value="//input[@name='selection']").click()
        #Step4 Expression
        time.sleep(1.5)
        self._downloadCSV(driver, "Expression")
        #Step5 Refresh and go to top of page
        driver.refresh()
        time.sleep(2)
        driver.find_element(by=By.TAG_NAME, value='html').send_keys(Keys.HOME)
        time.sleep(1)
        #Step5 Expression
        self._downloadCSV(driver, "Exclusion")

        driver.quit()
