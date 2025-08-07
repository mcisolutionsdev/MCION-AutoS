import pyperclip
import pyautogui
import subprocess
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

def remove_emoji(text):
    emoji_pattern = re.compile(
        "[" u"\U00010000-\U0010FFFF"  # ký tự ngoài BMP
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def find_to_driver(chrome_path,user_data_dir,profile_name):
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