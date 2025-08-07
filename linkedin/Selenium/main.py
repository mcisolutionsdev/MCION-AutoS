import json
import time
import os
import logging
from typing import Dict, List, Optional
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from automation import find_to_driver

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("linkedin_automation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LinkedInPoster:
    """
    Class để tự động đăng bài lên LinkedIn từ dữ liệu JSON
    """
    def __init__(self, chrome_path: str, profile_path: str, profile_name: str):
        """
        Khởi tạo class với thông tin cấu hình trình duyệt
        """
        self.chrome_path = chrome_path
        self.profile_path = profile_path
        self.profile_name = profile_name
        self.driver = None
        self.wait = None
        self.timeout = 10  # Thời gian chờ tối đa cho các element (giây)
    
    def initialize_driver(self):
        """
        Khởi tạo trình duyệt Chrome với profile đã chỉ định
        """
        try:
            self.driver = find_to_driver(self.chrome_path, self.profile_path, self.profile_name)
            self.wait = WebDriverWait(self.driver, self.timeout)
            logger.info("Đã khởi tạo trình duyệt thành công")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi khởi tạo trình duyệt: {str(e)}")
            return False
    
    def navigate_to_linkedin(self, profile_url: str):
        """
        Điều hướng đến trang cá nhân LinkedIn
        """
        try:
            self.driver.get(profile_url)
            time.sleep(2)  # Chờ trang tải xong
            logger.info(f"Đã điều hướng đến {profile_url}")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi điều hướng đến LinkedIn: {str(e)}")
            return False
    
    def click_create_post_button(self):
        """
        Nhấp vào nút tạo bài đăng mới
        """
        try:
            create_post_btn_x_path = '/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/div[1]/div[2]/div[2]/button/span/span'
            create_post_btn = self.driver.find_element( By.XPATH, create_post_btn_x_path )
            create_post_btn.click()
            time.sleep( 2 )
            logger.info("Đã nhấp vào nút tạo bài đăng")
            return True
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"Không tìm thấy nút tạo bài đăng: {str(e)}")
            return False
    
    def enter_post_content(self, content: str):
        """
        Nhập nội dung bài đăng
        """
        try:
            editor_xpath = '//div[contains(@class, "ql-editor") and @contenteditable="true" and contains(@data-placeholder, "What do you want to talk about?")]'
            editor_div = self.wait.until(
                EC.visibility_of_element_located((By.XPATH, editor_xpath))
            )
            editor_div.click()
            
            p_tag = editor_div.find_element(By.TAG_NAME, "p")
            p_tag.send_keys(content)
            time.sleep(1)
            logger.info(f"Đã nhập nội dung bài đăng: '{content[:30]}...'")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi nhập nội dung bài đăng: {str(e)}")
            return False
    
    def upload_image(self, image_path: str):
        """
        Tải lên hình ảnh cho bài đăng
        """
        try:
            # Kiểm tra xem file hình ảnh có tồn tại không
            if not os.path.exists(image_path):
                logger.error(f"Không tìm thấy file hình ảnh: {image_path}")
                return False
                
            # Nhấp vào nút media
            media_btn_path = "/html/body/div[4]/div/div/div/div[2]/div/div[2]/div[2]/div[1]/div/section/div[2]/ul/li[2]/div/div/span/button"
            media_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, media_btn_path))
            )
            media_btn.click()
            time.sleep(2)
            
            # Chọn file hình ảnh
            input_file_id = "/html/body/div[4]/div/div/div/div[2]/div/div/div[1]/div/div[2]/input"
            input_file = self.driver.find_element(By.XPATH, input_file_id)
            input_file.send_keys(image_path)
            time.sleep(2)
            
            # Nhấp vào nút Next
            next_btn_path = '/html/body/div[4]/div/div/div/div[2]/div/div/div[2]/div/button[2]'
            next_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, next_btn_path))
            )
            next_btn.click()
            time.sleep(2)
            
            logger.info(f"Đã tải lên hình ảnh: {image_path}")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi tải lên hình ảnh: {str(e)}")
            return False
    
    def publish_post(self):
        """
        Đăng bài viết
        """
        try:
            post_btn_xpath =  "/html/body/div[4]/div/div/div/div[2]/div/div/div[2]/div[4]/div/div[2]/button"
            post_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, post_btn_xpath))
            )
            post_btn.click()
            time.sleep(3)  # Chờ bài đăng được xử lý
            logger.info("Đã đăng bài viết thành công")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi đăng bài viết: {str(e)}")
            return False
    
    def create_single_post(self, content: str, image_path: str):
        """
        Tạo một bài đăng đầy đủ với nội dung và hình ảnh
        """
        try:
            # Nhấp vào nút tạo bài đăng
            if not self.click_create_post_button():
                return False
            
            # Nhập nội dung
            if not self.enter_post_content(content):
                return False
            
            # Tải lên hình ảnh (nếu có)
            if image_path and not self.upload_image(image_path):
                return False
            
            # Nhấp nút đăng bài
            if not self.publish_post():
                return False
            
            logger.info("Đã hoàn thành đăng bài")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi tạo bài đăng: {str(e)}")
            return False
    
    def close_driver(self):
        """
        Đóng trình duyệt
        """
        try:
            if self.driver:
                self.driver.close()
                logger.info("Đã đóng trình duyệt")
        except Exception as e:
            logger.error(f"Lỗi khi đóng trình duyệt: {str(e)}")
    
    def load_posts_from_json(self, json_file_path: str) -> List[Dict]:
        """
        Đọc dữ liệu bài đăng từ file JSON
        """
        try:
            if not os.path.exists(json_file_path):
                logger.error(f"Không tìm thấy file JSON: {json_file_path}")
                return []
            
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            if not isinstance(data, list):
                logger.error("Dữ liệu JSON không phải là danh sách các bài đăng")
                return []
            
            logger.info(f"Đã đọc {len(data)} bài đăng từ file JSON")
            return data
        except Exception as e:
            logger.error(f"Lỗi khi đọc file JSON: {str(e)}")
            return []
    
    def create_multiple_posts(self, json_file_path: str, profile_url: str):
        """
        Tạo nhiều bài đăng từ dữ liệu JSON
        """
        # Đọc dữ liệu từ file JSON
        posts = self.load_posts_from_json(json_file_path)
        if not posts:
            logger.error("Không có dữ liệu bài đăng để xử lý")
            return False
        
        # Khởi tạo trình duyệt
        if not self.initialize_driver():
            return False
        
        # Điều hướng đến LinkedIn
        if not self.navigate_to_linkedin(profile_url):
            self.close_driver()
            return False
        
        # Đăng từng bài một
        success_count = 0
        for i, post in enumerate(posts):
            logger.info(f"Đang xử lý bài đăng {i+1}/{len(posts)}")
            
            # Kiểm tra dữ liệu đầu vào
            if 'content' not in post:
                logger.error(f"Bài đăng {i+1} không có nội dung, bỏ qua")
                continue
            
            # Đăng bài
            content = post['content']
            image_path = post.get('image_path', '')  # Có thể không có hình ảnh
            
            if self.create_single_post(content, image_path):
                success_count += 1
                logger.info(f"Đã đăng bài thứ {i+1} thành công")
                
                # Chờ một khoảng thời gian giữa các bài đăng để tránh bị phát hiện là bot
                if i < len(posts) - 1:
                    wait_time = 30  # 30 giây giữa các bài đăng
                    logger.info(f"Chờ {wait_time} giây trước khi đăng bài tiếp theo...")
                    time.sleep(wait_time)
            else:
                logger.error(f"Không thể đăng bài thứ {i+1}")
        
        # Đóng trình duyệt
        self.close_driver()
        
        logger.info(f"Đã đăng thành công {success_count}/{len(posts)} bài viết")
        return success_count > 0

# Hàm chính để chạy automation
def run_linkedin_automation(config_file_path: str):
    """
    Chạy tự động hóa LinkedIn từ file cấu hình JSON
    """
    try:
        # Đọc cấu hình
        with open(config_file_path, 'r', encoding='utf-8') as file:
            config = json.load(file)
        
        # Kiểm tra cấu hình
        required_fields = ['chrome_path', 'profile_path', 'profile_name', 'profile_url', 'posts_file']
        for field in required_fields:
            if field not in config:
                logger.error(f"Thiếu trường cấu hình: {field}")
                return False
        
        # Khởi tạo đối tượng LinkedInPoster
        poster = LinkedInPoster(
            chrome_path=config['chrome_path'],
            profile_path=config['profile_path'],
            profile_name=config['profile_name']
        )
        
        # Chạy automation
        return poster.create_multiple_posts(
            json_file_path=config['posts_file'],
            profile_url=config['profile_url']
        )
    except Exception as e:
        logger.error(f"Lỗi khi chạy automation: {str(e)}")
        return False

if __name__ == "__main__":
    # Chạy từ file cấu hình
    config_file = "linkedin_config.json"
    run_linkedin_automation(config_file)