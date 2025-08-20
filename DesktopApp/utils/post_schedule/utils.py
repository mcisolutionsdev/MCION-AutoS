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
import pygetwindow as gw
import time
def remove_non_bmp_characters(text):
    return ''.join(char for char in text if ord(char) <= 0xFFFF)
def focus_chrome_window(title_keywords=["Meta Business Suite", "Facebook", "Chrome"]):
    try:
        for keyword in title_keywords:
            windows = gw.getWindowsWithTitle(keyword)
            if windows:
                win = windows[0]
                win.activate()  # Đưa cửa sổ ra foreground
                time.sleep(0.5)
                return True
    except Exception as e:
        print("⚠️ Không thể focus vào cửa sổ Chrome:", e)
    return False

def find_add_image_button(driver):
    xpaths = [
        "//div[@role='button' and .//div[text()='Thêm ảnh/video']]",  # Giao diện cũ
        "//a[.//div[contains(text(), 'Thêm ảnh')]]",                   # Giao diện thẻ <a>
        "//div[@aria-label='Chọn thêm ảnh.']//a"                      # Giao diện mới
    ]

    for xpath in xpaths:
        try:
            btn = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            print(f"✅ Tìm thấy nút theo XPath: {xpath}")
            return btn
        except:
            continue
    raise Exception("❌ Không tìm thấy nút 'Thêm ảnh' với bất kỳ XPath nào.")
def remove_emoji(text):
    emoji_pattern = re.compile(
        "[" u"\U00010000-\U0010FFFF"  # ký tự ngoài BMP
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def find_to_driver(chrome_path, user_data_dir, profile_name):
    import subprocess
    import time
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options

    # Build lệnh
    chrome_cmd = [
        chrome_path,
        '--remote-debugging-port=9222',
        f'--user-data-dir={user_data_dir}',
        f'--profile-directory={profile_name}'
    ]

    print("🚀 Đang chạy Chrome với lệnh:")
    print(" ".join(chrome_cmd))

    proc = subprocess.Popen(chrome_cmd)
    time.sleep(3)

    if proc.poll() is not None:
        raise Exception("❌ Chrome không khởi động được.")

    # Kết nối selenium
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    driver = webdriver.Chrome(options=options)
    return driver
def find_to_meta_business_suite_page_image(driver, page_id, timeout=10):
        driver.get(f"https://business.facebook.com/latest/composer/?asset_id={page_id}&context_ref=HOME&nav_ref=internal_nav&ref=biz_web_home_create_post")
        print("đã tìm đến image")

def find_to_meta_business_suite_page_reels(driver, page_id, timeout=10):

        driver.get(f"https://business.facebook.com/latest/reels_composer?asset_id={page_id}&ref=biz_web_home_create_reel")
        print("đã tìm đến reels")
def create_reels(driver,video_path,small_image_path,title, description, address, add_message_mode, tags, schedule_date, hour, minute, share_to_newsfeed=True):
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
        wait_upload = WebDriverWait(driver, 180)   # max 120 giây
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
    wait = WebDriverWait(driver, 1)
    try:
        title_input = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//input[@placeholder='Thêm tiêu đề cho thước phim']")
        )
        )
        driver.execute_script("arguments[0].click();", title_input)

        title_input.clear()
        title_input.send_keys(title)  # biến title chứa nội dung bạn muốn nhập
    except:
      print('An exception occurred')
    wait = WebDriverWait(driver, 1)
      
    try:
        desc_box = wait.until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//div[@role='textbox' and @aria-label='Hãy viết vào ô hộp thoại để thêm văn bản vào bài viết.']"
        ))
        )
        print("desc_box1",desc_box)
        time.sleep(0.5)
    except Exception as e:
        desc_box = wait.until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//div[@role='textbox' and @aria-label='Mô tả thước phim của bạn để mọi người biết nội dung thước phim']"
        ))
        )
        print("desc_box2",desc_box)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", desc_box)
        time.sleep(0.5)
    try:
        desc_box.click()
    except Exception as e:
        print("⚠️ Click bị chặn, dùng JS để click:", e)
        driver.execute_script("arguments[0].click();", desc_box)

    try:
        # Click mô tả
        try:
            desc_box.click()
        except Exception as e:
            print("⚠️ Click bị chặn, dùng JS để click:", e)
            driver.execute_script("arguments[0].click();", desc_box)

        time.sleep(0.2)
        print("desc_box3",desc_box)

        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", desc_box)
        time.sleep(0.3)
        print("desc_box dùng auto",desc_box)
        # desc_box.send_keys(remove_non_bmp_characters(description))
        # time.sleep(0.5)
        box = desc_box
        box_location = box.location
        box_size = box.size

        box_center_x = box_location['x'] + box_size['width'] / 2
        box_center_y = box_location['y'] + box_size['height'] / 2

        # 5. Lấy vị trí cửa sổ trình duyệt
        window_position = driver.get_window_position()
        window_x = window_position['x']
        window_y = window_position['y']

        # ⚡️ Quan trọng: offset ~120-150px để bù trừ thanh address bar, header Chrome
        offset_y = 210  # Nếu cần, bạn có thể tinh chỉnh

        # Tính toán vị trí thực tế
        absolute_x = window_x + box_center_x
        absolute_y = window_y + box_center_y + offset_y

        # 6. Click thật sự vào message box
        pyautogui.moveTo(absolute_x, absolute_y)
        pyautogui.click()
        time.sleep(0.25)
        # 4. Gõ nội dung bài viết

        desc_box.click()
        time.sleep(0.25)

        # 7. Copy nội dung vào clipboard
        focus_chrome_window()
        pyperclip.copy(description)

        # 8. Paste vào
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(1)
        pyautogui.click()
        time.sleep(0.25)


        print("✅ Đã nhập mô tả reels.")
    except Exception as e:
        print("❌ Không thể nhập mô tả:", e)

    # Click nút Vị trí
    try:
        location_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and @aria-label='Vị trí']"))
        )
        location_button.click()
        print("✅ Đã click nút Vị trí")
        is_location_button_clickable = True
    except Exception as e:
        print("❌ Không tìm thấy hoặc click được nút 'Vị trí':", e)
        is_location_button_clickable = False
        
    if is_location_button_clickable:
            
        # Nhập vị trí
        try:
            time.sleep(2)
            location_input = wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Nhập vị trí']"))
            )
            location_input.click()
            location_input.send_keys(address)
            time.sleep(1)
            location_input.send_keys(Keys.ENTER)
            print("✅ Đã nhập và chọn địa điểm:", address)
        except Exception as e:
            print("❌ Không thể nhập địa điểm:", e)

        # Click nút Lưu
        try:
            save_button = WebDriverWait(driver, 2).until(
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
        except Exception as e:
            print("❌ Không thể click nút 'Lưu':", e)

        # Thu hút tin nhắn
        if add_message_mode:
            try:
                message_btn = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and @aria-label='Thu hút tin nhắn']"))
                )
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", message_btn)
                time.sleep(0.3)
                try:
                    message_btn.click()
                except Exception as e:
                    print("⚠️ Click thường bị chặn, dùng JS:", e)
                    driver.execute_script("arguments[0].click();", message_btn)

                print("✅ Đã click nút Thu hút tin nhắn")
            except Exception as e:
                print("❌ Không thể bật 'Thu hút tin nhắn':", e)

    wait = WebDriverWait(driver, 10)
    upload_btn = wait.until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//div[contains(text(), 'Tải hình ảnh lên')]"
        ))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", upload_btn)
    time.sleep(0.5)
    print("Tìm thấy nút Tải hình ảnh lên (div).")
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
    try:
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
    except:
      print('An exception occurred')
    try:
        # Gửi từng tag
        for tag in tags:
            tag_input.send_keys(tag)
            time.sleep(1)
            tag_input.send_keys(Keys.ENTER)
            print(f"✅ Đã thêm tag: {tag}")
            time.sleep(0.7)

    except Exception as e:
        print("⚠️ Khoáng thể tìm thấy nút 'Tiếp' hoặc không thể click:", e)
    # Scroll và click an toàn
    next_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//div[text()='Tiếp']"))
    )
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
                time.sleep(5)
                print("✅ Đã bật tùy chọn 'Chia sẻ lên tin của bạn'")
            else:
                print("ℹ️ Tùy chọn đã được bật trước đó.")

        except Exception as e:
            print("❌ Không thể bật radio 'Chia sẻ lên tin của bạn':", e)
    

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

def create_post(driver, message, image_path, schedule_date="15/06/2025", hour="15", minute="45"):
    # 2. Click nút "Thêm ảnh"
    
    print("jsadjadjsa")
    screen_width, screen_height = pyautogui.size()

    # Tính toán vị trí chính giữa màn hình
    center_x = screen_width // 2
    center_y = screen_height // 2

    # Click vào vị trí chính giữa
    pyautogui.click(center_x, center_y)
    # 2. Click nút "Thêm ảnh"
    
    print("image_path in create_post", image_path)
  # Tìm nút 'Thêm ảnh/video' dạng div

    try:
        add_image_btn = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//div[@role='button' and .//div[text()='Thêm ảnh/video']]"
                ))
            )
        try:
            add_image_btn.click()
            time.sleep(1)
        except Exception as e:
            print("❌ Không click được nút 'Thêm ảnh/video' (dạng div):", e)
    except:
        try:
            add_image_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//div[@aria-label='Chọn thêm ảnh.']//a[.//div[normalize-space()='Thêm ảnh']]"
                ))
            )
            print("Tìm lần 2", add_image_btn)

            # Nếu nút 'Thêm ảnh' đã sẵn sàng
            driver.execute_script("arguments[0].scrollIntoView(true);", add_image_btn)

            try:
                add_image_btn.click()  # Thử click
            except Exception:
                driver.execute_script("arguments[0].click();", add_image_btn)  # Dùng JS click nếu không thành công

            time.sleep(1)

        except Exception as e:
            print("❌ Không click được nút 'Thêm ảnh' (dạng a):", e)

    pyperclip.copy(image_path)
    pyautogui.hotkey('ctrl', 'v')

    time.sleep(0.25)
    pyautogui.press('enter')
    focus_chrome_window()


    time.sleep(4)
    message_box = driver.find_element(By.XPATH,
    "//div[@contenteditable='true' and contains(@aria-label,'thêm văn bản vào bài viết')]")
    box = message_box
    box_location = box.location
    box_size = box.size

    box_center_x = box_location['x'] + box_size['width'] / 2
    box_center_y = box_location['y'] + box_size['height'] / 2

    # 5. Lấy vị trí cửa sổ trình duyệt
    window_position = driver.get_window_position()
    window_x = window_position['x']
    window_y = window_position['y']

    # ⚡️ Quan trọng: offset ~120-150px để bù trừ thanh address bar, header Chrome
    offset_y = 210  # Nếu cần, bạn có thể tinh chỉnh

    # Tính toán vị trí thực tế
    absolute_x = window_x + box_center_x
    absolute_y = window_y + box_center_y + offset_y

    # 6. Click thật sự vào message box
    pyautogui.moveTo(absolute_x, absolute_y)
    pyautogui.click()
    time.sleep(0.25)
    # 4. Gõ nội dung bài viết

    message_box.click()
    time.sleep(0.25)

    # 7. Copy nội dung vào clipboard
    focus_chrome_window()
    pyperclip.copy(message)

    # 8. Paste vào
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(1)
    pyautogui.click()
    time.sleep(0.25)
    checkbox_schedule = driver.find_element(By.CSS_SELECTOR, 'input[aria-label="Đặt ngày và giờ"]')
    checkbox_schedule.click()
    time.sleep(2)  # ⚠️ thêm dòng này

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

    # 9. Click nút "Lên lịch"
    schedule_button = driver.find_element(By.XPATH, "//div[@role='button' and .//div[text()='Lên lịch']]")
    driver.execute_script("arguments[0].click();", schedule_button)
    time.sleep(2)

