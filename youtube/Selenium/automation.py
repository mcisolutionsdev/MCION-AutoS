import pyperclip
import pyautogui
import subprocess
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

def find_to_driver(chrome_path,user_data_dir,profile_name):
    # chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    # user_data_dir = r"C:\Users\MSI\AppData\Local\Google\Chrome\User Data"
    # profile_name = "Profile 5"  # Hoặc xác định đúng qua chrome://version

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

def create_video_or_short(driver,post_mode, title, desciption, video_path, thumbnail_path=None, is_for_kid = False,publish_mode=""):
    if post_mode == "video":
        driver.get('https://studio.youtube.com/channel/videos/')
    elif post_mode == "short":
        driver.get('https://studio.youtube.com/channel/shorts/')
    else:
        return
    time.sleep(1)
    create_element = driver.find_element(By.XPATH, '/html/body/ytcp-app/ytcp-entity-page/div/ytcp-header/header/div/div/ytcp-button/ytcp-button-shape/button/yt-touch-feedback-shape/div/div[2]')
    create_element.click()
    time.sleep(0.25)
    create_element = driver.find_element(By.XPATH, '/html/body/ytcp-text-menu/tp-yt-paper-dialog/div/tp-yt-paper-listbox/tp-yt-paper-item[1]/ytcp-ve')
    create_element.click()
    time.sleep(0.5)
    select_video_element = driver.find_element(By.XPATH, '//*[@id="select-files-button"]/ytcp-button-shape/button/yt-touch-feedback-shape/div/div[2]')
    select_video_element.click()
    time.sleep(0.25)
    pyperclip.copy(video_path)
    time.sleep(0.25)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.25)
    pyautogui.press('enter')
    
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="textbox"]'))
    )

    # Bước 5: Nhập tiêu đề vào ô tiêu đề video
    title_element = driver.find_element(By.XPATH, '/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-ve/ytcp-video-metadata-editor/div/ytcp-video-metadata-editor-basics/div[1]/ytcp-video-title/ytcp-social-suggestions-textbox/ytcp-form-input-container/div[1]/div[2]/div/ytcp-social-suggestion-input/div')
    title_element.click()
    time.sleep(0.25)
    title_element.send_keys(Keys.CONTROL, 'a')  # hoặc Keys.COMMAND nếu bạn dùng macOS
    title_element.send_keys(Keys.DELETE)
    
    # Gửi tiêu đề
    title_element.send_keys(title)
    time.sleep(0.5)
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-ve/ytcp-video-metadata-editor/div/ytcp-video-metadata-editor-basics/div[2]/ytcp-video-description/div/ytcp-social-suggestions-textbox/ytcp-form-input-container/div[1]/div[2]/div/ytcp-social-suggestion-input/div'))
    )
    desciption_element = driver.find_element(By.XPATH, '/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-ve/ytcp-video-metadata-editor/div/ytcp-video-metadata-editor-basics/div[2]/ytcp-video-description/div/ytcp-social-suggestions-textbox/ytcp-form-input-container/div[1]/div[2]/div/ytcp-social-suggestion-input/div')
    desciption_element.click()
    time.sleep(0.25)
    desciption_element.send_keys(Keys.CONTROL, 'a')  # hoặc Keys.COMMAND nếu bạn dùng macOS
    desciption_element.send_keys(Keys.DELETE)
    
    # Gửi tiêu đề
    desciption_element.send_keys(desciption)
    time.sleep(0.25)

    if thumbnail_path is not None:
        thumbnail_element = driver.find_element(By.XPATH, '/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-ve/ytcp-video-metadata-editor/div/ytcp-video-metadata-editor-basics/div[3]/ytcp-video-thumbnail-editor/div[3]/ytcp-video-custom-still-editor/div/ytcp-thumbnail-uploader/ytcp-thumbnail-editor/div[1]/ytcp-ve/button')
        thumbnail_element.click()
        time.sleep(0.25)
        pyperclip.copy(thumbnail_path)
        time.sleep(0.25)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.25)
        pyautogui.press('enter')
    if is_for_kid:
        xpath = '/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-ve/ytcp-video-metadata-editor/div/ytcp-video-metadata-editor-basics/div[5]/ytkc-made-for-kids-select/div[4]/tp-yt-paper-radio-group/tp-yt-paper-radio-button[1]'
    else:
        xpath = '/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-ve/ytcp-video-metadata-editor/div/ytcp-video-metadata-editor-basics/div[5]/ytkc-made-for-kids-select/div[4]/tp-yt-paper-radio-group/tp-yt-paper-radio-button[2]'

    made_for_kid_element = driver.find_element(By.XPATH, xpath)
    made_for_kid_element.click()
    time.sleep(0.25)
    next_element = driver.find_element(By.XPATH,'/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[2]/div/div[2]/ytcp-button[2]/ytcp-button-shape/button')
    next_element.click()
    time.sleep(0.25)
    next_element.click()
    time.sleep(1)
    next_element.click()
    time.sleep(0.25)
    if publish_mode == "private":
        xpath = "/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-uploads-review/div[2]/div[1]/ytcp-video-visibility-select/div[2]/tp-yt-paper-radio-group/tp-yt-paper-radio-button[1]"
    elif publish_mode == "not_public":
        xpath = "/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-uploads-review/div[2]/div[1]/ytcp-video-visibility-select/div[2]/tp-yt-paper-radio-group/tp-yt-paper-radio-button[2]"
    else:
        xpath = "/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-uploads-review/div[2]/div[1]/ytcp-video-visibility-select/div[2]/tp-yt-paper-radio-group/tp-yt-paper-radio-button[3]"
    
    select_mode_element = driver.find_element(By.XPATH, xpath)
    select_mode_element.click()
    time.sleep(0.25)
    publish_element = driver.find_element(By.XPATH, "/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[2]/div/div[2]/ytcp-button[3]/ytcp-button-shape/button")
    publish_element.click()
# driver = find_to_driver(r"C:\Program Files\Google\Chrome\Application\chrome.exe", r"C:\Users\MSI\AppData\Local\Google\Chrome\User Data", "Profile 5")
# create_video_or_short(driver,"video", "Test", "Test", r"C:\Users\MSI\Videos\10.mp4",r"C:\Users\MSI\OneDrive\Hình ảnh\blog.png",False,"private")