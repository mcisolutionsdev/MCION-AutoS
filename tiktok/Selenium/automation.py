import pyperclip,subprocess
import pyautogui
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from selenium import webdriver


def find_to_driver(chrome_path,user_data_dir,profile_name):
    subprocess.Popen([
        chrome_path,
        f'--remote-debugging-port=9222',
        f'--user-data-dir={user_data_dir}',
        f'--profile-directory={profile_name}'
    ])
    time.sleep(2)
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=options)
    return driver
def find_to_tiktok(driver):
    driver.get("https://www.tiktok.com/")
    time.sleep(2)

def create_post(driver, message, video_path):
    timeout=10
    driver.get("https://www.tiktok.com/tiktokstudio/upload?from=webapp")
    time.sleep(2)
    select_video_btn = driver.find_element(By.XPATH,'/html/body/div[1]/div/div/div[2]/div[2]/div/div/div/div[1]/div/div/div[1]/div/div/div[2]/button')
    select_video_btn.click()
    time.sleep(1)
    pyperclip.copy(video_path)
    time.sleep(0.2)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.2)
    pyautogui.press('enter')
    WebDriverWait(driver, timeout*6).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.info-progress.success"))
        )
    caption_box = driver.find_element(By.CSS_SELECTOR, 'div[contenteditable="true"]')

    caption_box.click()
    time.sleep(1)
    caption_box.send_keys(Keys.CONTROL, 'a')  # hoặc Keys.COMMAND nếu bạn dùng macOS
    caption_box.send_keys(Keys.DELETE)

    # Gửi tin nhắn mới
    caption_box.send_keys(message)

    post_btn = WebDriverWait(driver, timeout).until(
        lambda d: (
            btn := d.find_element(
                By.XPATH,
                "/html/body/div[1]/div/div/div[2]/div[2]/div/div/div/div[4]/div/button[1]"
            )
        ) and btn.is_enabled() and btn.is_displayed() and btn
    )
    post_btn.click()
    time.sleep(3)
# driver = find_to_driver(r"C:\Program Files\Google\Chrome\Application\chrome.exe", r"C:\Users\MSI\AppData\Local\Google\Chrome\User Data", "Profile 5")
# create_post(driver, "Test", r"C:\Users\MSI\Videos\2025-04-17 09-11-38.mp4")