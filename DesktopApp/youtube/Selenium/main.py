import openpyxl
import time
from automation import find_to_driver, create_video_or_short
def upload_videos_from_excel(excel_file, chrome_path, user_data_dir):
    # Mở file Excel
    workbook = openpyxl.load_workbook(excel_file)
    sheet = workbook.active

    # Lấy danh sách tên các cột từ dòng đầu tiên
    columns = {cell.value: idx for idx, cell in enumerate(sheet[1], start=1)}

    for row in sheet.iter_rows(min_row=2, values_only=True):  
        profile_name = row[columns['profile_name'] - 1] 
        video_path = row[columns['video_path'] - 1] 
        thumbnail_path = row[columns['thumbnail_path'] - 1]  
        title = row[columns['title'] - 1]  
        description = row[columns['description'] - 1]  
        is_for_kid = row[columns['is_for_kid'] - 1]  
        publish_mode = row[columns['publish_mode'] - 1] 
        post_mode = row[columns['post_mode'] - 1]  

        driver = find_to_driver(chrome_path, user_data_dir, profile_name)
        
        create_video_or_short(driver, post_mode, title, description, video_path, thumbnail_path, is_for_kid, publish_mode)
        time.sleep(10)
        try:
            driver.close()
            driver.quit()
        except Exception as quit_err:
            print(f" Error closing driver:", quit_err)


if __name__ == '__main__':
    upload_videos_from_excel('youtube_data.xlsx', r"C:\Program Files\Google\Chrome\Application\chrome.exe", r"C:\Users\MSI\AppData\Local\Google\Chrome\User Data")
