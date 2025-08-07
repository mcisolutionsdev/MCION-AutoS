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
    if post_type in ["image", "video"]:
        driver.get(f"https://business.facebook.com/latest/composer/?asset_id={page_id}&context_ref=HOME&nav_ref=internal_nav&ref=biz_web_home_create_post")
        print("đã tìm đến image")
    elif post_type == "reels":
        driver.get(f"https://business.facebook.com/latest/reels_composer?asset_id={page_id}&ref=biz_web_home_create_reel")
        print("đã tìm đến reels")
def create_reels(driver,video_path,small_image_path, title, description, address, add_message_mode, tags, schedule_date, hour, minute, share_to_newsfeed=True):
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
    focus_chrome_window()
    wait = WebDriverWait(driver, 10)

    title_input = wait.until(
    EC.presence_of_element_located(
        (By.XPATH, "//input[@placeholder='Thêm tiêu đề cho thước phim']")
    )
    )
    title_input.click()
    title_input.clear()
    title_input.send_keys(title)  # biến title chứa nội dung bạn muốn nhập
    desc_box = wait.until(
    EC.element_to_be_clickable((
        By.XPATH,
        "//div[@role='textbox' and @aria-label='Hãy viết vào ô hộp thoại để thêm văn bản vào bài viết.']"
    ))
    )
    print("desc_box",desc_box)
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", desc_box)
    time.sleep(0.5)

    try:
        desc_box.click()
    except Exception as e:
        print("⚠️ Click bị chặn, dùng JS để click:", e)
        driver.execute_script("arguments[0].click();", desc_box)

    desc_box.send_keys(description)
    wait = WebDriverWait(driver, 10)
    location_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and @aria-label='Vị trí']"))
    )
    location_button.click()
    print("✅ Đã click nút Vị trí")

    # Step 2: Chờ input "Nhập vị trí" xuất hiện
    location_input = wait.until(
        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Nhập vị trí']"))
    )

    # Step 3: Nhập địa điểm
    location_input.click()
    location_input.send_keys(address)
    print("✅ Đã nhập địa điểm: Hà Nội")

    # Step 4: Chờ gợi ý hiện ra và chọn
    # Có thể cần delay 1 chút để danh sách gợi ý hiện ra
    time.sleep(1)
    location_input.send_keys(Keys.ENTER)
    print("✅ Đã chọn gợi ý đầu tiên")
    save_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Lưu')]"))
    )

    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", save_button)
    time.sleep(0.3)
    try:
        save_button.click()
    except Exception as e:
        print("⚠️ Nút Lưu bị che, dùng JS click:", e)
        driver.execute_script("arguments[0].click();", save_button)

    print("✅ Đã click nút Lưu")
    if add_message_mode:
        message_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and @aria-label='Thu hút tin nhắn']"))
        )

        # Scroll nếu cần
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", message_btn)
        time.sleep(0.3)

        # Click bằng JS nếu bị che
        try:
            message_btn.click()
        except Exception as e:
            print("⚠️ Click thường bị chặn, dùng JS:", e)
            driver.execute_script("arguments[0].click();", message_btn)

    print("✅ Đã click nút Thu hút tin nhắn")
    upload_btn = wait.until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//div[contains(text(), 'Tải hình ảnh lên')]"
        ))
    )
    upload_btn.click()
    print("Đã click nút Tải hình ảnh lên (div).")

    # Đợi thẻ <a> Tải hình ảnh lên xuất hiện
    upload_link = wait.until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//a[contains(text(), 'Tải hình ảnh lên')]"
        ))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", upload_link)
    time.sleep(0.5)
    try:
        upload_link.click()
    except Exception as e:
        print("⚠️ Click bị chặn, dùng JS để click:", e)
        driver.execute_script("arguments[0].click();", upload_link)
    print("Đã click link Tải hình ảnh lên (a).")

    # Dán đường dẫn ảnh bằng pyautogui
    time.sleep(1)  # Chờ hộp chọn file hiện ra
    pyperclip.copy(small_image_path)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.25)
    pyautogui.press('enter')
    print("Đã dán và chọn ảnh.")
    tag_input = wait.until(
        EC.presence_of_element_located((
            By.XPATH,
            "//input[@placeholder='Thêm từ khóa liên quan để mọi người dễ tìm thấy thước phim của bạn']"
        ))
    )

    # Scroll vào giữa màn hình
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tag_input)
    time.sleep(0.3)

    # Dùng JS để click
    try:
        tag_input.click()
    except Exception as e:
        print("⚠️ Không thể click trực tiếp, dùng JS:", e)
        driver.execute_script("arguments[0].click();", tag_input)

    # Gửi từng tag
    for tag in tags:
        tag_input.send_keys(tag)
        time.sleep(0.5)
        tag_input.send_keys(Keys.ENTER)
        print(f"✅ Đã thêm tag: {tag}")
        time.sleep(0.3)
    next_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//div[text()='Tiếp']"))
    )

    # Scroll và click an toàn
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
    time.sleep(0.3)
    try:
        next_button.click()
    except Exception as e:
        print("⚠️ Click thường bị chặn, dùng JS:", e)
        driver.execute_script("arguments[0].click();", next_button)
    try:
        try:
            next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[text()='Tiếp']"))
            )

            next_button.click()
        except Exception as e:
            print("⚠️ Click thường bị chặn, dùng JS:", e)
            driver.execute_script("arguments[0].click();", next_button)
    except Exception as e:
        print("⏳ Nút 'Cắt' không xuất hiện sau khi bấm 'Tiếp' hoặc không thể click:", e)
        # Bạn có thể `return` hoặc tiếp tục nếu không cần 'Cắt'
    try:
        schedule_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[text()='Lên lịch']"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", schedule_button)
        time.sleep(0.3)
        schedule_button.click()
        print("✅ Đã click nút Lên lịch.")
    except Exception as e:
        print("❌ Không thể click nút Lên lịch:", e)
    
        # 6. Click vào khung chứa input ngày để hiển thị
    wait = WebDriverWait(driver, 10)
    
    # Tìm input ngày theo placeholder (ổn định hơn ID)
    date_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder='dd/mm/yyyy']")))
    driver.execute_script("arguments[0].click();", date_input)
    time.sleep(0.3)
    date_input.send_keys(Keys.CONTROL, 'a')
    date_input.send_keys(schedule_date)
    date_input.send_keys(Keys.ENTER)
    time.sleep(0.5)

    hour_input = driver.find_element(By.CSS_SELECTOR, 'input[aria-label="giờ"]')
    driver.execute_script("arguments[0].click();", hour_input)
    time.sleep(0.3)
    hour_input.send_keys(Keys.CONTROL, 'a')
    hour_input.send_keys(hour)

    # Tìm input phút
    minute_input = driver.find_element(By.CSS_SELECTOR, 'input[aria-label="phút"]')
    driver.execute_script("arguments[0].click();", minute_input)
    time.sleep(0.3)
    minute_input.send_keys(Keys.CONTROL, 'a')
    minute_input.send_keys(minute)
    if share_to_newsfeed:
        try:
            share_switch = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@type='checkbox' and @aria-label='Chia sẻ lên tin của bạn']"))
            )
            
            # Scroll to element (đảm bảo không bị che)
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", share_switch)
            time.sleep(0.3)

            # Nếu chưa bật thì click
            if not share_switch.is_selected():
                share_switch.click()
                print("✅ Đã bật tùy chọn 'Chia sẻ lên tin của bạn'")
            else:
                print("ℹ️ Tùy chọn đã được bật trước đó.")

        except Exception as e:
            print("❌ Không thể bật radio 'Chia sẻ lên tin của bạn':", e)
    
    time.sleep(5)
    # schedule_btn = WebDriverWait(driver, 15).until(
    #     EC.presence_of_element_located((
    #         By.XPATH,
    #         "//div[@role='button' and .//div[text()='Lên lịch']]"
    #     ))
    # )
    schedule_btn = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((
            By.XPATH,
            "/html/body/div[1]/div/div[1]/div/div[2]/div/div/div[1]/span/div/div/div[1]/div[1]/div/div[2]/div/div/div/div/div/div/div/div/div/div[2]/div/div[1]/div/div/div[2]/div/div/div/div[2]/div/div/div[2]/div/div/span/div/div/div"
        ))
    )

    # Scroll rồi click
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", schedule_btn)
    schedule_btn.click()
    print("✅ Đã click đúng nút 'Lên lịch'.")
    try:
        # Click nút "Lên lịch" trước đó (đảm bảo đã thực hiện thành công)
        # schedule_btn.click()

        # Sau khi click, chờ xuất hiện thông báo thành công
        success_msg = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='heading' and text()='Đã lên lịch đăng thước phim']"))
        )
        print("✅ Đã xác nhận: Thước phim đã được lên lịch thành công.")
    except Exception as e:
        print("❌ Không thấy thông báo 'Đã lên lịch đăng thước phim' sau khi click:", e)
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
user_data_dir = r"E:\User data"
profile_name = "Profile 50"
page_id = "625358260661885"
driver = find_to_driver(chrome_path,user_data_dir,profile_name)
find_to_meta_business_suite_page(driver, page_id ,"reels")
video_path = r"C:\Users\MSI\Videos\Captures\6807044196471.mp4"
small_image_path = r"C:\Users\MSI\OneDrive\Hình ảnh\meo.jpg"
title = "test"
description = "test"
address = "Hà Nội"
tags = ["du lịch", "ẩm thực", "hà nội"]
create_reels(driver,video_path,small_image_path,title,description, address,False, tags,schedule_date="15/08/2025", hour="15", minute="45", share_to_newsfeed=True)

