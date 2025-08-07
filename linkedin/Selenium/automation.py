import pyperclip
# import pyautogui
import subprocess
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def find_to_driver(chrome_path,user_data_dir,profile_name):
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    user_data_dir = r"C:\Users\MSI\AppData\Local\Google\Chrome\User Data"
    profile_name = "Profile 5"  # Hoặc xác định đúng qua chrome://version

    # Khởi chạy Chrome bằng subprocess
    subprocess.Popen([
        chrome_path,
        f'--remote-debugging-port=9222',
        f'--user-data-dir={user_data_dir}',
        f'--profile-directory={profile_name}'
    ])

    # Chờ vài giây cho Chrome khởi động xong
    time.sleep(2)

    # Kết nối với Chrome đã mở
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=options)
    return driver

def find_to_youtube(driver, timeout=10):
    driver.get('https://www.youtube.com/')
    time.sleep(1)

