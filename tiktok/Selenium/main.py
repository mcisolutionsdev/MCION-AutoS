import time
import pandas as pd
from automation import find_to_driver, create_post  # giả sử bạn đặt 2 hàm trên trong your_module.py

# 1. Cấu hình chung
CHROME_PATH     = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
USER_DATA_DIR   = r"C:\Users\MSI\AppData\Local\Google\Chrome\User Data"

# 2. Đọc file dữ liệu
# Nếu là CSV:
# df = pd.read_csv("data.csv")
# Nếu là Excel (.xlsx):
df = pd.read_excel(r"D:\mci\automate-socials\tiktok\tiktok_data.xlsx")

# File của bạn phải có các cột: 
#   number_profile  (ví dụ: 5, 6, … — tương ứng với Profile 5, Profile 6…)
#   account_tiktok_name  (nếu bạn muốn dùng tên thay cho số profile)
#   message_content
#   video_path ba
# 3. Vòng lặp xử lý từng dòng
for idx, row in df.iterrows():
    profile_id    = row["number_profile"]
    message       = row["message_content"]
    video_path    = row["video_path"]
    
    # Khởi Chrome với đúng profile
    profile_dir_name = f"Profile {profile_id}"
    driver = find_to_driver(
        CHROME_PATH,
        USER_DATA_DIR,
        profile_dir_name
    )
    
    try:
        create_post(driver, message, video_path)
        print(f"[{idx}] Posted successfully: profile={profile_dir_name}")
    except Exception as e:
        print(f"[{idx}] ERROR on profile={profile_dir_name}:", e)
    finally:
        try:
            driver.close()
            driver.quit()
        except Exception as quit_err:
            print(f"[{idx}] Error closing driver:", quit_err)

print("Done all posts.")
