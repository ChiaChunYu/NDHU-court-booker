import selenium
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
from PIL import Image
import pytesseract


def basic_setting(driver):
    driver.get('https://sys.ndhu.edu.tw/gc/sportcenter/SportsFields/Default.aspx')
    driver.maximize_window()
    # send student_id
    driver.find_element(By.ID,"MainContent_TextBox1").send_keys(stu_id)
    # send email password
    driver.find_element(By.ID,"MainContent_TextBox2").send_keys(email_pwd)
    driver.find_element(By.ID,"MainContent_Button1").send_keys(Keys.ENTER)
    driver.find_element(By.ID,"MainContent_Button2").click()
    # click the court 
    select = Select(driver.find_element(By.ID,"MainContent_DropDownList1"))
    select.select_by_visible_text("BSK0D籃球場D")
    time.sleep(1)

def borrow_court(driver):
    # click the borrow court botton
    driver.find_element(By.XPATH, '//*[@id="MainContent_Table1"]/tbody/tr[18]/td[2]/button').click()
    time.sleep(1)
    # snapshot the captcha
    img = driver.find_element(By.ID,"imgCaptcha")
    img.screenshot("screenshot.png")
    Img = Image.open("screenshot.png")
    text = pytesseract.image_to_string(Img)
    text = text.replace(" ", "")
    print(text)
    driver.find_element(By.ID, "txtCaptchaValue").send_keys(text)
    driver.find_element(By.XPATH,"/html/body/div/div/div[5]/button").click()
    time.sleep(1)
    # if not success replit the step
    while "驗證碼不通過！" in driver.page_source:
        # change a new captcha
        driver.find_element(By.XPATH,'/html/body/div/div/div[3]/button').click()
        img = driver.find_element(By.ID,"imgCaptcha")
        img.screenshot("screenshot.png")
        Img = Image.open("screenshot.png")
        text = pytesseract.image_to_string(Img)
        text = text.replace(" ", "")
        print(text)
        driver.find_element(By.ID, "txtCaptchaValue").send_keys(text)
        driver.find_element(By.XPATH,"/html/body/div/div/div[5]/button").click()
        time.sleep(1)
    # send the reason to borrow the court
    driver.find_element(By.ID,"MainContent_ReasonTextBox1").send_keys("1")
    driver.find_element(By.ID,"MainContent_Button4").click()
    time.sleep(10)


if __name__ == "__main__":
    driver = webdriver.Chrome()
    stu_id = "Your student ID"
    email_pwd = "Your email password"
    basic_setting(driver)
    current_time = datetime.now()
    print(current_time)
    target_time = datetime(current_time.year, current_time.month, current_time.day)+timedelta(days=1)
    while current_time < target_time:
        driver.find_element(By.ID,"MainContent_Button1").click()
        current_time = datetime.now()
        print(current_time)
        time.sleep(0.5) 
    borrow_court(driver)
    print("success")     

    # timedelta(days=1)