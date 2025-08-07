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
import pygetwindow as gw, time, win32gui, win32con
import time

def focus_chrome_window(
        title_keywords=("Meta Business Suite", "Facebook", "Chrome"),
        wait=0.3,
):
    all_titles = [t for t in gw.getAllTitles() if t.strip()]
    print("⚙️ Danh sách cửa sổ:", all_titles)

    for kw in title_keywords:
        wins = gw.getWindowsWithTitle(kw)
        if not wins:
            continue

        win = wins[0]          # lấy cửa sổ đầu tiên khớp keyword
        hwnd = win._hWnd

        # Lấy trạng thái hiện tại
        placement = win32gui.GetWindowPlacement(hwnd)
        show_cmd = placement[1]   # 1 = normal, 2 = minimized, 3 = maximized …

        # 1️⃣ Khôi phục nếu đang minimized
        if show_cmd == win32con.SW_SHOWMINIMIZED:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        # 2️⃣ Nếu đã normal/maximized chỉ cần bảo đảm hiển thị
        else:
            win32gui.ShowWindow(hwnd, win32con.SW_SHOW)

        # Đưa ra foreground
        try:
            win.activate()                       # pygetwindow wrapper
        except OSError:
            win32gui.SetForegroundWindow(hwnd)   # fallback thấp cấp

        time.sleep(wait)
        return True

    print("⚠️ Không tìm thấy cửa sổ Chrome phù hợp.")
    return False
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
def find_to_meta_business_suite_page(driver, page_id, post_type, timeout=10):
    
    if post_type == "image" or "video":
        driver.get(f"https://business.facebook.com/latest/composer/?asset_id={page_id}&context_ref=HOME&nav_ref=internal_nav&ref=biz_web_home_create_post")
        print("đã tìm đến")
    elif post_type == "reels":
        driver.get(f"https://business.facebook.com/latest/reels_composer?asset_id={page_id}&ref=biz_web_home_create_reel")

def create_video(driver,video_path,title, description, schedule_date, hour, minute):
    screen_width, screen_height = pyautogui.size()

    # Tính toán vị trí chính giữa màn hình
    center_x = screen_width // 2
    center_y = screen_height // 2

    # Click vào vị trí chính giữa
    pyautogui.click(center_x, center_y)
    # 2. Click nút "Thêm ảnh"
    
    print("image_path in create_post", video_path)
  # Tìm nút 'Thêm ảnh/video' dạng div
    wait = WebDriverWait(driver, 10)
    element = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//div[contains(text(), 'Thêm video')]")
        )
    )
    element.click()
    time.sleep(0.25)
    pyautogui.press('enter')

    time.sleep(2)
    
    pyperclip.copy(video_path)
    pyautogui.hotkey('ctrl', 'v')

    time.sleep(0.25)
    pyautogui.press('enter')
    focus_chrome_window()
    try:
        wait_upload = WebDriverWait(driver, 120)   # max 120 giây
        wait_upload.until(
            EC.presence_of_element_located(
                (By.XPATH, "//span[text()='100%']")
            )
        )
        print("Upload video xong 100%!")
    except Exception as e:
        print("Timeout đợi upload video 100%", e)
        return
    wait = WebDriverWait(driver, 10)
    title_input = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//input[@placeholder='Thêm tiêu đề cho video']")
        )
    )
    # Click để focus
    title_input.click()
    # Xoá giá trị cũ nếu có
    title_input.clear()
    # Gõ text mới
    title_input.send_keys(title)

    desc_box = wait.until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//div[@role='textbox' and @aria-label='Hãy viết vào ô hộp thoại để thêm văn bản vào bài viết.']"
        ))
    )

    # Click để focus
    desc_box.click()

    # Gửi text
    desc_box.send_keys(description)
    focus_chrome_window()

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
user_data_dir = r"E:\User data"
profile_name = "Profile 50"
page_id = "625358260661885"
driver = find_to_driver(chrome_path,user_data_dir,profile_name)
find_to_meta_business_suite_page(driver,page_id,"reels")
video_path = r"C:\Users\MSI\Videos\Captures\6807044196471.mp4"
title = "test"
description = "test"
schedule_date = "25/08/2023"
hour = "17"
minute = "32"
create_video(driver,video_path,title,description,schedule_date,hour,minute)

