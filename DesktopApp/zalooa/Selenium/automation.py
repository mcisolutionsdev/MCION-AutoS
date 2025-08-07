# import pyautogui
import subprocess
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
def find_to_driver(chrome_path, user_data_dir, profile_name):


    # Khởi chạy Chrome headless bằng subprocess
    subprocess.Popen([
        chrome_path,
        '--remote-debugging-port=9222',
        f'--user-data-dir={user_data_dir}',
        f'--profile-directory={profile_name}',
        '--disable-gpu',
        '--window-size=1920,1080'
    ])

    time.sleep(2)

    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=options)
    return driver
def find_to_create_post_page(driver, timeout=10):
    driver.get("https://oa.zalo.me/manage/choose?pageid=2200579641721999206")
    time.sleep(1)
    driver.get('https://oa.zalo.me/manage/content/article/create')
    
    # Chờ phần tử có id='title_lbl' xuất hiện
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.ID, "title_lbl"))
    )


def select_datetime(driver, day, month, year, hour, minute):

    wait = WebDriverWait(driver, 10)
    btn_dat_lich = driver.find_element(
    By.XPATH,
    "//div[normalize-space()='Đặt lịch']"
    )
    btn_dat_lich.click()
    # 1. Chờ modal hiện
    wait.until(
        EC.visibility_of_element_located((By.CLASS_NAME, "modal_calender"))
    )

    # 2. Click để mở dropdown năm
    year_label = driver.find_element(By.CLASS_NAME, "xdsoft_year")
    year_label.click()

    # Chọn năm
    year_option = driver.find_element(
        By.XPATH,
        f"//div[contains(@class,'xdsoft_option') and @data-value='{year}']"
    )
    year_option.click()

    # 3. Click để mở dropdown tháng
    # Đọc tháng hiện tại
    month_label = driver.find_element(By.CLASS_NAME, "xdsoft_month")
    current_month_text = month_label.text.strip()

    thang_mapping = {
        "Tháng 1": 1,
        "Tháng 2": 2,
        "Tháng 3": 3,
        "Tháng 4": 4,
        "Tháng 5": 5,
        "Tháng 6": 6,
        "Tháng 7": 7,
        "Tháng 8": 8,
        "Tháng 9": 9,
        "Tháng 10": 10,
        "Tháng 11": 11,
        "Tháng 12": 12,
    }

    current_month_num = thang_mapping[current_month_text]

    diff = month - current_month_num

    btn_prev = driver.find_element(By.CLASS_NAME, "xdsoft_prev")
    btn_next = driver.find_element(By.CLASS_NAME, "xdsoft_next")
    import time
    if diff > 0:
        for _ in range(diff):
            btn_next.click()
            time.sleep(0.2)
    elif diff < 0:
        for _ in range(-diff):
            btn_prev.click()
            time.sleep(0.2)
    else:
        print("Tháng đã đúng!")

    # Kiểm tra lại
    month_label = driver.find_element(By.CLASS_NAME, "xdsoft_month")
    print("Tháng hiện tại sau khi chọn:", month_label.text.strip())
    # 4. Chọn ngày
    day_cell = driver.find_element(
        By.XPATH,
        f"//td[@data-date='{day}' and @data-month='{month - 1}' and @data-year='{year}']"
    )
    day_cell.click()

     # Wait block time load LẠI sau khi click ngày
    wait.until(
        EC.visibility_of_element_located((By.CLASS_NAME, "xdsoft_time_variant"))
    )

    # Tìm lại element time_div mới
    time_div = driver.find_element(
        By.XPATH,
        f"//div[contains(@class,'xdsoft_time') and @data-hour='{hour}' and @data-minute='{minute}']"
    )

    # Scroll & click
    driver.execute_script("arguments[0].scrollIntoView(true);", time_div)
    time.sleep(0.2)

    # Click nếu chưa được chọn
    if "xdsoft_current" not in time_div.get_attribute("class"):
        driver.execute_script("arguments[0].click();", time_div)
        print(f"✅ Đã click giờ {hour}:{minute:02d} bằng JS")
    else:
        print(f"→ Giờ {hour}:{minute:02d} đã được chọn sẵn.")
    # 1) Tìm và chờ cho element có class func_close và ml-10 được click được

    # Thay vì click div, gọi trực tiếp hàm click Angular
    driver.execute_script("""
        var el = document.querySelector('[ng-click="onClickSchedule($event)"]');
        if (window.angular) {
            angular.element(el).triggerHandler('click');
        } else {
            el.click();
        }
    """)

    # Đợi modal có id=alert-msg hiện ra
    try:
        alert_elem = wait.until(EC.visibility_of_element_located(
            (By.ID, "alert-msg")
        ))
        print("✅ Alert xuất hiện:", alert_elem.text)
    except:
        print("❌ Alert không xuất hiện.")

    alert_elem = wait.until(EC.visibility_of_element_located(
        (By.ID, "alert-msg")
    ))

    # Lấy text thông báo
    alert_text = alert_elem.text

    # Kiểm tra text đúng mong muốn không
    if alert_text.strip() == "Đặt lịch thành công":
        print("✅ Đặt lịch thành công!")
        return True
    else:
        print("❌ Nội dung thông báo không đúng:", alert_text)
        return False
    
def create_post(driver, title, quote, author, content, call_to_action, file_path, day, month, year, hour, minute):
    # Đợi để đảm bảo trang đã tải và các phần tử cần thiết có sẵn
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[ng-model='form.title']"))
    )

    # Nhập Tiêu đề
    title_input = driver.find_element(By.CSS_SELECTOR, "textarea[ng-model='form.title']")
    title_input.clear()  # Xóa nếu có dữ liệu cũ
    title_input.send_keys(title)

    # Nhập Trích dẫn
    quote_input = driver.find_element(By.CSS_SELECTOR, "textarea[ng-model='form.desc']")
    quote_input.clear()
    quote_input.send_keys(quote)

    # Nhập Tên tác giả
    author_input = driver.find_element(By.CSS_SELECTOR, "input[ng-model='form.author']")
    author_input.clear()
    author_input.send_keys(author)

  
    iframe = driver.find_element(By.CLASS_NAME, "cke_wysiwyg_frame")
    driver.switch_to.frame(iframe)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Tìm phần tử cần điền text
    textarea = driver.find_element(By.CLASS_NAME, "cke_editable")

    # Điền văn bản vào
    textarea.send_keys(content)

    # Quay lại trang chính (nếu cần)
    driver.switch_to.default_content()
    if call_to_action:
        checkbox = driver.find_element(By.ID, "squaredFour2")

        driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)

        # Click phần tử bằng JavaScript
        driver.execute_script("arguments[0].click();", checkbox)
        time.sleep(1)
        input_content = driver.find_element(By.XPATH, "//input[@ng-model='form.actionLink.label']")
        input_content.clear()
        input_content.send_keys(call_to_action[0])

        # Điền vào trường "Đường dẫn" bằng JavaScript
        input_link = driver.find_element(By.XPATH, '//input[@ng-model="form.actionLink.link"]')
        input_link.clear()
        input_link.send_keys(call_to_action[1])
    # Tìm phần tử cần upload file
    upload_btn = driver.find_element(By.ID, "label_upload")
    upload_btn.click()
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.XPATH, "//input[@ng-model='imgUrl']")
        )
    )
    # Upload file
    file_input = driver.find_element(By.ID, "selectedFile")
    file_input.send_keys(rf"{file_path}")
    time.sleep(0.25)
    btn_crop = driver.find_element(By.ID, "cropImageBtn")
    btn_crop.click()
    time.sleep(0.25)
    select_datetime(driver, day, month, year, hour, minute)

def main(chrome_path, user_data_dir, profile_name, excel_file_path):
    max_retries = 2

    # Đọc dữ liệu Excel
    df = pd.read_excel(excel_file_path, sheet_name="Posts")
    driver = find_to_driver(chrome_path, user_data_dir, profile_name)

    # Lặp từng bài viết
    for index, row in df.iterrows():
        print(f"\n🔷 Đang xử lý bài viết số {index+1} - Tiêu đề: {row['title']}")
        
        last_exception = None

        for attempt in range(1, max_retries + 1):
            try:
                print(f"\n==============================")
                print(f"🟡 Thực hiện automation - Lần {attempt}")
                print(f"==============================")


                # Mở trang create_post
                find_to_create_post_page(driver)

                # Thực hiện create_post
                create_post(
                    driver=driver,
                    title=row["title"],
                    quote=row["quote"],
                    author=row["author"],
                    content=row["content"],
                    call_to_action=(
                        row["call_to_action_label"],
                        row["call_to_action_link"]
                    ),
                    file_path=row["file_path"],
                    day=int(row["day"]),
                    month=int(row["month"]),
                    year=int(row["year"]),
                    hour=int(row["hour"]),
                    minute=int(row["minute"])
                )

                print("✅ Bài viết đã tạo thành công!")
                break

            except Exception as e:
                print(f"❌ Lỗi ở lần chạy thứ {attempt}: {e}")
                last_exception = e
                if attempt < max_retries:
                    print("→ Thử lại sau 3 giây...")
                    time.sleep(3)
                else:
                    print("‼️ Đã thử tối đa, vẫn lỗi. Bỏ qua bài viết này.")

# if __name__ == "__main__":
#     main(
#         chrome_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
#         user_data_dir=r"C:\Users\MSI\AppData\Local\Google\Chrome\User Data",
#         profile_name="Profile 5",
#         excel_file_path=r"D:\mci\automate-socials\zalooa\Selenium\data.xlsx"
#     )
