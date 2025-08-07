from PyQt5.QtCore import QThread, pyqtSignal
import time
import pandas as pd
import re
class SchedulePostThread(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    log = pyqtSignal(str)
    system_error = pyqtSignal(str)

    def __init__(self, chrome_path, user_data_dir, profile_name, excel_file_path, parent=None):
        super().__init__(parent)
        self.chrome_path = chrome_path
        self.user_data_dir = user_data_dir
        self.profile_name = profile_name
        self.excel_file_path = excel_file_path
        self.image_posts, self.reels_posts = self.read_excel_data(self.excel_file_path)
        self.stop_requested = False

    def stop(self):
        self.stop_requested = True

    def wait_with_stop(self, total_seconds):
        for _ in range(int(total_seconds * 10)):
            if self.stop_requested:
                self.log.emit("⛔ Thread SchedulePostThread đã bị dừng.")
                return True
            time.sleep(0.1)
        return False

    def read_excel_data(self, file_path):
        image_posts = []
        reels_posts = []

        try:
            df_image = pd.read_excel(file_path, sheet_name='IMAGE')
            for _, row in df_image.iterrows():
                raw_date = row.get('Ngày')
                if isinstance(raw_date, pd.Timestamp):
                    formatted_date = raw_date.strftime("%d/%m/%Y")
                else:
                    try:
                        parsed_date = pd.to_datetime(str(raw_date), dayfirst=True, errors='coerce')
                        formatted_date = parsed_date.strftime("%d/%m/%Y") if not pd.isna(parsed_date) else str(raw_date)
                    except Exception:
                        formatted_date = str(raw_date).strip()

                post = {
                    'message': row.get('Nội dung'),
                    'image_path': row.get('Đường dẫn ảnh'),
                    'schedule': [{
                        'date': formatted_date,
                        'hour': str(row.get('Giờ')).zfill(2),
                        'minute': str(row.get('Phút')).zfill(2),
                    }],
                    'page_ids': [
                        pid.strip() for pid in re.split(r'[;,]', str(row.get('Danh sách Fanpage'))) if pid.strip()
                    ]
                }
                image_posts.append(post)
        except Exception as e:
            self.log.emit(f"⚠️ Lỗi đọc sheet IMAGE: {str(e)}")

        try:
            df_reels = pd.read_excel(file_path, sheet_name='REELS')
            for _, row in df_reels.iterrows():
                raw_date = row.get('Ngày')
                if isinstance(raw_date, pd.Timestamp):
                    formatted_date = raw_date.strftime("%d/%m/%Y")
                else:
                    try:
                        parsed_date = pd.to_datetime(str(raw_date), dayfirst=True, errors='coerce')
                        formatted_date = parsed_date.strftime("%d/%m/%Y") if not pd.isna(parsed_date) else str(raw_date)
                    except Exception:
                        formatted_date = str(raw_date).strip()

                post = {
                    'video_path': row.get('Đường dẫn video'),
                    'thumbnail_path': row.get('Đường dẫn ảnh nền video'),
                    'address': row.get('Địa chỉ'),
                    'enable_messenger': row.get('Bật chế độ messenger') in [1, '1', 'yes', 'Yes', 'Có', True],
                    'tags': [tag.strip() for tag in str(row.get('Danh sách thẻ')).split(',') if tag.strip()],
                    'title': row.get('Tiêu đề'),
                    'description': row.get('Mô tả'),
                    'schedule': [{
                        'date': formatted_date,
                        'hour': str(row.get('Giờ')).zfill(2),
                        'minute': str(row.get('Phút')).zfill(2),
                        'share_to_newsfeed': row.get('Chia sẻ lên bản tin') in [1, '1', 'yes', 'Yes', 'Có', True]
                    }],
                    'page_ids': [
                        pid.strip() for pid in re.split(r'[;,]', str(row.get('Danh sách Fanpage'))) if pid.strip()
                    ]
                }
                reels_posts.append(post)
        except Exception as e:
            self.log.emit(f"⚠️ Lỗi đọc sheet REELS: {str(e)}")

        return image_posts, reels_posts

    def run(self):
        try:
            from utils.post_schedule.utils import (
                find_to_driver,
                find_to_meta_business_suite_page_image,
                find_to_meta_business_suite_page_reels,
                create_post,
                create_reels,
            )

            driver = find_to_driver(self.chrome_path.strip(), self.user_data_dir.strip(), self.profile_name.strip())
            self.log.emit("🟢 Đã khởi động trình duyệt")

            results = {"success": [], "failed": []}

            # Đăng IMAGE POST
            for post in self.image_posts:
                for page_id in post['page_ids']:
                    for sch in post['schedule']:
                        if self.stop_requested: driver.quit(); return
                        task_id = f"{page_id}-{sch['date']} {sch['hour']}:{sch['minute']}"
                        try:
                            print("data image",sch['date'], sch['hour'], sch['minute'])
                            find_to_meta_business_suite_page_image(driver, page_id)
                            create_post(driver, post['message'], post['image_path'], sch['date'], sch['hour'], sch['minute'])
                            self.log.emit(f"✅ [{task_id}] Đã lên lịch ảnh.")
                            results['success'].append(task_id)
                        except Exception as e:
                            self.log.emit(f"❌ [{task_id}] Lỗi IMAGE: {str(e)}")
                            results['failed'].append({"task": task_id, "error": str(e)})

                        if self.wait_with_stop(3): driver.quit(); return

            # Đăng REELS POST
            for post in self.reels_posts:
                for page_id in post['page_ids']:
                    for sch in post['schedule']:
                        if self.stop_requested: driver.quit(); return
                        task_id = f"{page_id}-{sch['date']} {sch['hour']}:{sch['minute']}"
                        try:
                            find_to_meta_business_suite_page_reels(driver, page_id)
                            print("data reels",sch['date'], sch['hour'], sch['minute'])
                            create_reels(driver, post['video_path'], post['thumbnail_path'], post['title'],
                                         post['description'], post['address'], post['enable_messenger'],
                                         post['tags'], sch['date'], sch['hour'], sch['minute'],
                                         sch.get('share_to_newsfeed', False))
                            self.log.emit(f"✅ [{task_id}] Đã lên lịch reels.")
                            results['success'].append(task_id)
                        except Exception as e:
                            self.log.emit(f"❌ [{task_id}] Lỗi REELS: {str(e)}")
                            results['failed'].append({"task": task_id, "error": str(e)})

                        if self.wait_with_stop(3): driver.quit(); return

            driver.quit()
            self.log.emit("🎉 Hoàn tất tất cả bài viết.")
            self.log.emit(f" - Thành công: {len(results['success'])}")
            self.log.emit(f" - Thất bại: {len(results['failed'])}")
            for fail in results['failed']:
                self.log.emit(f"⚠️ {fail['task']} -> {fail['error']}")
            self.finished.emit("🎯 Đã xong.")
        except Exception as e:
            self.system_error.emit(f"🚨 Lỗi hệ thống: {str(e)}")
class PostZaloOaThread(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    log = pyqtSignal(str)

    def __init__(self, chrome_path, user_data_dir, profile_name, excel_file_path):
        super().__init__()
        self.chrome_path = chrome_path
        self.user_data_dir = user_data_dir
        self.profile_name = profile_name
        self.excel_file_path = excel_file_path
        self.stop_requested = False

    def stop(self):
        self.stop_requested = True

    def run(self):
        try:
            from zalooa.Selenium.automation import main
            self.log.emit("🚀 Bắt đầu chạy Selenium cho Zalo OA...")

            # ⚠️ Không thể dừng giữa chừng trừ khi sửa hàm main()
            main(
                chrome_path=self.chrome_path,
                user_data_dir=self.user_data_dir,
                profile_name=self.profile_name,
                excel_file_path=self.excel_file_path
            )

            if self.stop_requested:
                self.log.emit("⛔ Thread PostZaloOaThread đã bị dừng sau khi main chạy xong.")

            self.finished.emit("✅ Đã chạy xong đăng bài Zalo OA.")
        except Exception as e:
            self.error.emit(f"❌ Lỗi khi chạy đăng bài Zalo OA: {str(e)}")

class PostTiktokThread(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    log = pyqtSignal(str)

    def __init__(self, chrome_path, user_data_dir, excel_file_path):
        super().__init__()
        self.chrome_path = chrome_path
        self.user_data_dir = user_data_dir
        self.excel_file_path = excel_file_path
        self.stop_requested = False

    def stop(self):
        self.stop_requested = True

    def run(self):
        try:
            from tiktok.Selenium.automation import main
            self.log.emit("🚀 Bắt đầu chạy Selenium cho TikTok...")

            # ⚠️ Không thể dừng giữa chừng trừ khi sửa hàm main()
            main(
                chrome_path=self.chrome_path,
                user_data_dir=self.user_data_dir,
                excel_file_path=self.excel_file_path
            )

            if self.stop_requested:
                self.log.emit("⛔ Thread PostTiktokThread đã bị dừng sau khi main chạy xong.")

            self.finished.emit("✅ Đã chạy xong đăng bài TikTok.")
        except Exception as e:
            self.error.emit(f"❌ Lỗi khi chạy đăng bài TikTok: {str(e)}")
