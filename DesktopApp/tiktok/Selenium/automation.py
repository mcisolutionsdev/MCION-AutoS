import time, subprocess
import pandas as pd

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from selenium import webdriver

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

def find_to_tiktok(driver):
    driver.get("https://www.tiktok.com/")
    time.sleep(2)
def set_time(driver, hour, minute):
    wait = WebDriverWait(driver, 10)

    hour_int = int(hour)
    minute_int = int(minute)

    # 1. Click input
    time_input = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'input.TUXTextInputCore-input[readonly]')
        )
    )
    time_input.click()
    print("✅ Đã click input giờ")

    # 2. Wait dropdown
    wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, ".tiktok-timepicker-time-picker-container")
        )
    )
    print("✅ Dropdown hiện ra")

    # 3. Click hour bằng JS
    hour_elem = driver.find_element(
        By.XPATH,
        f'//span[contains(@class, "tiktok-timepicker-left") and text()="{hour_int:02d}"]'
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", hour_elem)
    driver.execute_script("arguments[0].click();", hour_elem)
    print(f"✅ Đã chọn giờ {hour_int}")

    time.sleep(0.2)

    # 4. Click minute bằng JS
    minute_elem = driver.find_element(
        By.XPATH,
        f'//span[contains(@class, "tiktok-timepicker-right") and text()="{minute_int:02d}"]'
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", minute_elem)
    driver.execute_script("arguments[0].click();", minute_elem)
    print(f"✅ Đã chọn phút {minute_int}")

def set_date(driver, day, month, year):
    wait = WebDriverWait(driver, 10)

    month_map = {
        "Tháng Một": 1,
        "Tháng Hai": 2,
        "Tháng Ba": 3,
        "Tháng Tư": 4,
        "Tháng Năm": 5,
        "Tháng Sáu": 6,
        "Tháng Bảy": 7,
        "Tháng Tám": 8,
        "Tháng Chín": 9,
        "Tháng Mười": 10,
        "Tháng Mười Một": 11,
        "Tháng Mười Hai": 12,
    }
    date_calendar = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, '/html/body/div[1]/div/div/div[2]/div[2]/div/div/div/div[4]/div[1]/div[4]/div[1]/div[1]/div/div[3]/div[2]/div[1]/div/div/div/div[1]')
        )
    )
    # 2. Scroll icon vào view
    driver.execute_script("arguments[0].scrollIntoView(true);", date_calendar)
    time.sleep(0.2)

    # 3. Click icon
    date_calendar.click()
    time.sleep(1)
    
    print("✅ Đã click icon calendar")
    print("✅ Đã click input ngày")

    # 2. Wait calendar
    wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, ".calendar-wrapper")
        )
    )
    print("✅ Calendar hiện ra")

    # 3. Đọc tháng năm hiện tại
    month_text = driver.find_element(
        By.CSS_SELECTOR,
        ".month-title"
    ).text.strip()

    year_text = driver.find_element(
        By.CSS_SELECTOR,
        ".year-title"
    ).text.strip()

    current_month = month_map[month_text]
    current_year = int(year_text)

    target_month = int(month)
    target_year = int(year)

    # 4. Tính chênh lệch
    diff = (target_year - current_year) * 12 + (target_month - current_month)

    if diff != 0:
        print(f"→ Cần dịch {diff} tháng")
    else:
        print("→ Tháng/năm đã đúng!")

    arrow_xpath = '(//span[contains(@class,"arrow")])[2]' if diff > 0 else '(//span[contains(@class,"arrow")])[1]'

    for _ in range(abs(diff)):
        arrow = wait.until(
            EC.element_to_be_clickable((By.XPATH, arrow_xpath))
        )
        arrow.click()
        time.sleep(0.3)

    # 5. Click ngày
    day_elem = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH,
             f'//span[contains(@class, "day") and text()="{int(day)}"]')
        )
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", day_elem)
    driver.execute_script("arguments[0].click();", day_elem)

    print(f"✅ Đã chọn ngày {day}-{month}-{year}")
    time.sleep(0.5)

def create_post(driver, message, video_path,address,hour, minute,day,month,year, timeout=10):
    
    driver.get("https://www.tiktok.com/tiktokstudio/upload?from=webapp")
    wait = WebDriverWait(driver, 10)

    # Đợi trang load, có nút Chọn video xuất hiện
    wait.until(EC.presence_of_element_located((
        By.CSS_SELECTOR,
        '[data-e2e="select_video_button"]'
    )))
    print("✅ Trang upload đã load")

    # Tìm input hidden
    input_file = driver.find_element(
        By.CSS_SELECTOR,
        'input[type="file"][accept="video/*"]'
    )

    # Upload video
    input_file.send_keys(video_path)
    print("✅ Đã gửi path video vào input")
    WebDriverWait(driver, 200).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.info-progress.success"))
    )
    wait = WebDriverWait(driver, 10)

    caption_box = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'div[contenteditable="true"]')
        )
    )
    caption_box = driver.find_element(By.CSS_SELECTOR, 'div[contenteditable="true"]')

    caption_box.click()
    time.sleep(1)
    caption_box.send_keys(Keys.CONTROL, 'a')  # hoặc Keys.COMMAND nếu bạn dùng macOS
    caption_box.send_keys(Keys.DELETE)

    # Gửi tin nhắn mới
    caption_box.send_keys(message)
    try:
        search_input = wait.until(
        EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[placeholder="Tìm kiếm vị trí"]')
            )
        )
        search_input.click()
        search_input.clear()
        search_input.send_keys(address)
        print("✅ Đã nhập text tìm kiếm:", address)
            
        # Chờ phần tử đầu tiên xuất hiện
        first_option = wait.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, 'div[role="option"]')
            )
        )
        print("✅ Phát hiện phần tử đầu tiên:", first_option.text)

        # Click phần tử đầu tiên
        first_option.click()
        print("✅ Đã click phần tử đầu tiên.")
    except:
      print('An exception occurred')

    label = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, '//label[.//span[text()="Lên lịch"]]')
        )
    )

    # 2. Scroll đến label
    driver.execute_script(
        "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
        label
    )
    print("✅ Đã scroll đến radio Lên lịch")

    # 3. Chờ click được
    wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//label[.//span[text()="Lên lịch"]]')
    )).click()

    print("✅ Đã click radio Lên lịch")

    # Chờ đến khi input thời gian hiện ra và có thể click
    wait = WebDriverWait(driver, 10)
    time_input = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'input.TUXTextInputCore-input[readonly]')
        )
    )
    time_input.click()
    print("✅ Đã click input giờ")

    # 2. Đợi dropdown hiện ra
    wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, ".tiktok-timepicker-time-picker-container")
        )
    )
    print("✅ Dropdown hiện ra")

    set_time(driver, hour, minute)
    set_date(driver, day, month, year)
    try:
        # Chờ spinner biến mất (nếu có)
        wait.until_not(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '.Button__spinner--loading-true')
            )
        )
    except:
        print("⚠️ Spinner không biến mất. Tiếp tục click nút.")
    try:
        # Chờ tối đa 10 giây để phần tử xuất hiện và có thể click
        switch_wrapper = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                "div.Switch__content--checked-true"
            ))
        )
        
        switch_wrapper.click()
        print("✅ Đã tắt switch (unchecked)")
    except Exception as e:
        print("❌ Không thể click để tắt switch:", str(e))
    # Tìm nút Lên lịch
    schedule_btn = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, '[data-e2e="post_video_button"]')
        )
    )

    # Scroll vào view và click
    driver.execute_script("arguments[0].scrollIntoView(true);", schedule_btn)
    time.sleep(0.2)
    driver.execute_script("arguments[0].click();", schedule_btn)
    print("✅ Đã click nút Lên lịch.")
    time.sleep(3)

def run_one_post(driver, row):
    create_post(
        driver=driver,
        message=row["message"],
        video_path=row["video_path"],
        address=row["address"],
        hour=str(row["hour"]),
        minute=str(row["minute"]),
        day=str(row["day"]),
        month=str(row["month"]),
        year=str(row["year"]),
    )

def main(chrome_path, user_data_dir, excel_file_path):
    df = pd.read_excel(excel_file_path)

    for idx, row in df.iterrows():
        profile_name = row["profile"]
        print(f"\n=== Đang chạy bài số {idx+1}: {row['message']} trên profile {profile_name} ===")

        driver = find_to_driver(
            chrome_path=chrome_path,
            user_data_dir=user_data_dir,
            profile_name=profile_name
        )
        
        max_retry = 2
        last_exception = None

        for attempt in range(1, max_retry + 1):
            try:
                run_one_post(driver, row)
                print(f"✅ Bài số {idx+1} chạy thành công trên profile {profile_name}!")
                break

            except Exception as e:
                print(f"❌ Lỗi ở lần chạy thứ {attempt} của bài {idx+1} trên profile {profile_name}: {e}")
                last_exception = e

                if attempt < max_retry:
                    print("→ Thử chạy lại sau 3 giây...")
                    time.sleep(3)
                else:
                    print("‼️ Đã thử tối đa. Bỏ qua bài này.")
            finally:
                if driver:
                    driver.quit()

    print("✅ Đã hoàn thành tất cả các bài đăng.")
