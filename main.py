import selenium
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
import google.generativeai as genai
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
stu_id = os.getenv("NDHU_ID")
email_pwd = os.getenv("NDHU_PWD")
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not stu_id or not email_pwd or not gemini_api_key:
    raise ValueError("Please set the environment variables: NDHU_ID, NDHU_PWD, and GEMINI_API_KEY!")

genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel(model_name="gemini-2.0-flash")

def retry_on_failure(func, max_attempts=3, delay=1):
    def wrapper(*args, **kwargs):
        for attempt in range(max_attempts):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_attempts - 1:
                    print(f"Operation failed: {str(e)}")
                    raise
                print(f"Operation failed, retrying ({attempt + 1}/{max_attempts})")
                time.sleep(delay)
    return wrapper

def wait_and_find(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )

@retry_on_failure
def login(driver, stu_id, email_pwd):
    # Enter student ID
    wait_and_find(driver, By.ID, "MainContent_TxtUSERNO").send_keys(stu_id)
    # Enter email password
    wait_and_find(driver, By.ID, "MainContent_TxtPWD").send_keys(email_pwd)
    wait_and_find(driver, By.ID, "MainContent_Button1").click()

@retry_on_failure
def basic_setting(driver):
    # Click the apply button
    wait_and_find(driver, By.ID, "MainContent_Button2").click()
    # Select the court
    time.sleep(1)
    select = Select(wait_and_find(driver, By.ID, "MainContent_DropDownList1"))
    select.select_by_visible_text("BSK0C籃球場C")
    time.sleep(1)
    # Click the next week button
    wait_and_find(driver, By.ID, "MainContent_BtnNextW2").click()
    time.sleep(1)

@retry_on_failure
def borrow_court(driver):
    # Click the borrow court button
    wait_and_find(driver, By.XPATH, '//*[@id="MainContent_Table1"]/tbody/tr[16]/td[2]/button').click()
    time.sleep(1)
    # Capture the captcha image
    img = wait_and_find(driver, By.ID, "imgCaptcha")
    img.screenshot("screenshot.png")
    with open("screenshot.png", "rb") as f:
        image_data = f.read()
    response = model.generate_content([
        {"inline_data": {"mime_type": "image/png", "data": image_data}},
        "Please solve this five-letter captcha and only return the captcha text."
    ])
    text = response.text
    print(text)
    text = text.replace(" ", "")
    wait_and_find(driver, By.ID, "txtCaptchaValue").send_keys(text)
    wait_and_find(driver, By.XPATH, "/html/body/div/div/div[5]/button").click()
    time.sleep(1)
    # If not successful, repeat the step
    while "驗證碼不通過！" in driver.page_source:
        # Change to a new captcha
        wait_and_find(driver, By.XPATH, '/html/body/div/div/div[3]/button').click()
        img = wait_and_find(driver, By.ID, "imgCaptcha")
        img.screenshot("screenshot.png")
        with open("screenshot.png", "rb") as f:
            image_data = f.read()
        response = model.generate_content([
            {"inline_data": {"mime_type": "image/png", "data": image_data}},
            "Please solve this five-letter captcha and only return the captcha text."
        ])
        text = response.text
        print(text)
        text = text.replace(" ", "")
        wait_and_find(driver, By.ID, "txtCaptchaValue").send_keys(text)
        wait_and_find(driver, By.XPATH, "/html/body/div/div/div[5]/button").click()
        time.sleep(1)
    # Enter the reason for borrowing the court
    wait_and_find(driver, By.ID, "MainContent_ReasonTextBox1").send_keys("1")
    wait_and_find(driver, By.ID, "MainContent_Button4").click()
    time.sleep(10)

if __name__ == "__main__":
    driver = webdriver.Chrome()
    driver.get('https://sys.ndhu.edu.tw/gc/sportcenter/SportsFields/login.aspx')
    driver.maximize_window()
    login(driver, stu_id, email_pwd)
    basic_setting(driver)
    current_time = datetime.now()
    print(current_time)
    target_time = datetime(current_time.year, current_time.month, current_time.day,0,0,3) + timedelta(days=1)
    while current_time < target_time:
        wait_and_find(driver, By.ID, "MainContent_Button1").click()
        current_time = datetime.now()
        print(current_time)
        time.sleep(1)
    wait_and_find(driver, By.ID, "MainContent_Button1").click() 
    borrow_court(driver)
    print("success")     
