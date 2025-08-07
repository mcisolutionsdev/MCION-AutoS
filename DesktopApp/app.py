import sys, os, json
import threading
import requests
from PyQt5.QtCore import pyqtSignal,QUrl, Qt, QDate, QTime
from PyQt5.QtGui import QDesktopServices,QPixmap, QIcon
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTextEdit, QTabWidget,
    QLabel, QFileDialog, QListWidget, QListWidgetItem, QCheckBox,
    QMessageBox, QHBoxLayout, QTimeEdit, QDateEdit,QLineEdit,QDialog,
    QFormLayout,QTableWidget,QTableWidgetItem,QComboBox
)
from threads import PostTiktokThread, PostZaloOaThread, SchedulePostThread
import requests
from PyQt5.QtWidgets import QMessageBox
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
# thêm đầu file
from pathlib import Path
import shutil, logging, traceback

# ---- THƯ MỤC LƯU DỮ LIỆU NGƯỜI DÙNG -----------------
APPDIR = Path(os.getenv("LOCALAPPDATA", Path.home())) / "ScheduleAutoTool"
APPDIR.mkdir(exist_ok=True)

HISTORY_DB_PATH = APPDIR / "history_run_sessions.db"
LOG_PATH = APPDIR / "app.log"

logging.basicConfig(filename=LOG_PATH, level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")

def excepthook(exc_type, exc_value, exc_tb):
    logging.error("Uncaught exception",
                  exc_info=(exc_type, exc_value, exc_tb))
    QMessageBox.critical(None, "Lỗi",
        f"Đã xảy ra lỗi: {exc_value}\nXem {LOG_PATH} để biết chi tiết.")
sys.excepthook = excepthook

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")

env_path = os.path.join(base_path, ".env")
load_dotenv(dotenv_path=env_path)
import sqlite3
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
    exe_dir = os.path.dirname(sys.executable)
else:
    base_path = os.path.abspath(".")
    exe_dir = base_path

HISTORY_DB_PATH = os.path.join(exe_dir, "history_run_sessions.db")


class AppWindow(QWidget):
    tokens_received = pyqtSignal(str, str)

    def __init__(self,token, session_key, device_id):
        self.token_mci = token
        self.session_key = session_key
        self.device_id = device_id
        super().__init__()
        self.setWindowTitle("Schedule Auto Tool")
        self.showMaximized()
        self.access_token = None
        self.page_data = []
        self.image_path = None

        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")

        icon_path = os.path.join(base_path, "icon.ico")
        self.setWindowIcon(QIcon(icon_path))  # 👈 Gán icon cho cửa sổ
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        # Ví dụ: đường dẫn tới style.qss
        qss_path = os.path.join(base_path, "static", "qss", "style.qss")
        self.setStyleSheet(open(qss_path).read())

        self.tabs = QTabWidget()
        self.init_tab_home()

        self.init_tab_setting_for_schedule_post()
        self.init_tab_status_for_schedule_post()
        self.init_tab_setting_for_post_zalo_oa()
        self.init_tab_status_for_post_zalo_oa()
        self.init_tab_setting_for_post_tiktok()
        self.init_tab_status_for_post_tiktok()
        
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        self.create_history_table()

    def create_history_table(self):
        conn = sqlite3.connect(HISTORY_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS run_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_type TEXT,
                chrome_path TEXT,
                chrome_user_data_dir TEXT,
                profile_name TEXT,
                excel_file_path TEXT,
                started_at TEXT
            )
        """)
        conn.commit()
        conn.close()
    def init_tab_home(self):
        self.tab_home = QWidget()

        layout = QVBoxLayout()
        button_style = """
            QPushButton {
                font-size: 18px;
                padding: 12px;
                border-radius: 10px;
                background-color: #4A90E2;
                color: white;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
            QPushButton:pressed {
                background-color: #2C5F9E;
            }
        """
        
        self.schedule_post_btn = QPushButton("📢 Lên lịch đăng bài (Tự động Facebook Web)")
        self.schedule_post_btn.setStyleSheet(button_style)
        self.schedule_post_btn.clicked.connect(lambda: self.show_schedule_post_element())
        
        self.post_zalo_oa_btn = QPushButton("📢 Lên lịch đăng bài trên (Tự động Zalo OA)")
        self.post_zalo_oa_btn.setStyleSheet(button_style)
        self.post_zalo_oa_btn.clicked.connect(lambda: self.show_post_zalo_oa_element())
        
        self.post_tiktok_btn = QPushButton("📢 Lên lịch đăng bài trên (Tự động Tiktok)")
        self.post_tiktok_btn.setStyleSheet(button_style)
        self.post_tiktok_btn.clicked.connect(lambda: self.show_post_tiktok_element())
        layout.setSpacing(15)  # khoảng cách giữa các nút
        layout.setContentsMargins(50, 70, 50, 70)  # padding lề cho đẹp
        
        layout.addWidget(self.schedule_post_btn)
        layout.addWidget(self.post_zalo_oa_btn)
        layout.addWidget(self.post_tiktok_btn)

        self.tab_home.setLayout(layout)
        self.tabs.addTab(self.tab_home, "Trang chủ")
        self.tabs.tabBar().setExpanding(True)

    def init_tab_setting_for_schedule_post(self):
        self.tab_schedule_post_setting = QWidget()
        layout = QFormLayout()

        self.run_session_dropdown_schedule_post = QComboBox()
        self.run_session_dropdown_schedule_post.addItem("📂 Chọn phiên chạy đã lưu:")
        layout.addWidget(self.run_session_dropdown_schedule_post)

        self.chrome_path_input = QLineEdit()
        self.user_data_dir_input = QLineEdit()
        self.profile_name_input = QLineEdit()

        self.chrome_path_input.setPlaceholderText("Đường dẫn Chrome")
        self.user_data_dir_input.setPlaceholderText("User Data Dir")
        self.profile_name_input.setPlaceholderText("Profile Name")

        self.sheet_selector = QComboBox()
        self.sheet_selector.addItem("📄 Chọn sheet")  # Placeholder
        self.sheet_selector.currentIndexChanged.connect(self.load_sheet_data)

        self.post_table = QTableWidget()
        self.post_table.setMinimumHeight(200)

        self.select_post_file_btn = QPushButton("📂 Chọn file Excel chứa bài viết")
        self.select_post_file_btn.clicked.connect(self.select_post_file)

        self.download_template_btn = QPushButton("📥 Tải file Excel mẫu")
        self.download_template_btn.clicked.connect(lambda: self.download_excel_template("facebook"))

        self.run_schedule_btn = QPushButton("🚀 Chạy lên lịch bài viết")
        self.run_schedule_btn.clicked.connect(self.run_schedule_posting)

        layout.addRow("🛠️ Đường dẫn Chrome:", self.chrome_path_input)
        layout.addRow("📁 Thư mục User Data:", self.user_data_dir_input)
        layout.addRow("👤 Tên profile:", self.profile_name_input)
        layout.addRow(self.select_post_file_btn)
        layout.addRow("📑 Chọn sheet:", self.sheet_selector)
        layout.addRow(self.download_template_btn)
        layout.addRow(self.run_schedule_btn)
        layout.addRow(self.post_table)

        self.tab_schedule_post_setting.setLayout(layout)

        self.run_session_dropdown_schedule_post.currentIndexChanged.connect(
            lambda index: self.on_run_selected(index, self.run_session_dropdown_schedule_post)
        )

        latest_session = self.load_run_sessions("facebook", self.run_session_dropdown_schedule_post)
        if latest_session:
            self.chrome_path_input.setText(latest_session.get("chrome_path", ""))
            self.user_data_dir_input.setText(latest_session.get("chrome_user_data_dir", ""))
            self.profile_name_input.setText(latest_session.get("profile_name", ""))



    def init_tab_status_for_schedule_post(self):
        self.tab_schedule_post_status = QWidget()
        layout = QHBoxLayout()

        self.status_text_schedule = QTextEdit()
        self.status_text_schedule.setReadOnly(True)
        self.status_text_schedule.setPlaceholderText("📋 Trạng thái vòng lặp các bài...")

        self.error_text_schedule = QTextEdit()
        self.error_text_schedule.setReadOnly(True)
        self.error_text_schedule.setPlaceholderText("❌ Lỗi hệ thống...")

        layout.addWidget(self.status_text_schedule)
        layout.addWidget(self.error_text_schedule)

        self.tab_schedule_post_status.setLayout(layout)
    
    def init_tab_setting_for_post_zalo_oa(self):
        self.tab_post_zalo_oa_setting = QWidget()
        layout = QFormLayout()

        self.run_session_dropdown_post_zalo_oa = QComboBox()
        self.run_session_dropdown_post_zalo_oa.addItem("📂 Chọn phiên chạy đã lưu:")
        layout.addWidget(self.run_session_dropdown_post_zalo_oa)

        self.chrome_path_input_zalo = QLineEdit()
        self.chrome_path_input_zalo.setPlaceholderText("Đường dẫn Chrome")

        self.user_data_dir_input_zalo = QLineEdit()
        self.user_data_dir_input_zalo.setPlaceholderText("User Data Dir")

        self.profile_name_input_zalo = QLineEdit()
        self.profile_name_input_zalo.setPlaceholderText("Profile Name")

        self.post_table_zalo = QTableWidget()
        self.post_table_zalo.setColumnCount(12)
        self.post_table_zalo.setHorizontalHeaderLabels([
            "Title",
            "Quote",
            "Author",
            "Content",
            "CTA Label",
            "CTA Link",
            "File Path",
            "Day",
            "Month",
            "Year",
            "Hour",
            "Minute"
        ])

        self.post_table_zalo.setMinimumHeight(200)

        self.select_post_file_btn_zalo = QPushButton("📂 Chọn file Excel bài viết Zalo OA")
        self.select_post_file_btn_zalo.clicked.connect(self.select_post_file_zalo)

        self.download_template_btn_zalo = QPushButton("📥 Tải file Excel mẫu")
        self.download_template_btn_zalo.clicked.connect(
            lambda: self.download_excel_template("zalooa")
        )

        self.run_post_zalo_btn = QPushButton("🚀 Chạy đăng bài Zalo OA")
        self.run_post_zalo_btn.clicked.connect(self.run_post_zalo_oa)

        layout.addRow("🛠️ Đường dẫn Chrome:", self.chrome_path_input_zalo)
        layout.addRow("📁 Thư mục User Data:", self.user_data_dir_input_zalo)
        layout.addRow("👤 Tên profile:", self.profile_name_input_zalo)
        layout.addRow(self.select_post_file_btn_zalo)
        layout.addRow(self.download_template_btn_zalo)
        layout.addRow(self.run_post_zalo_btn)
        layout.addRow(self.post_table_zalo)

        self.tab_post_zalo_oa_setting.setLayout(layout)

        latest_session = self.load_run_sessions("zalooa", self.run_session_dropdown_post_zalo_oa)
        if latest_session:
            self.chrome_path_input_zalo.setText(latest_session.get("chrome_path", ""))
            self.user_data_dir_input_zalo.setText(latest_session.get("chrome_user_data_dir", ""))
            self.profile_name_input_zalo.setText(latest_session.get("profile_name", ""))
        else:
            self.chrome_path_input_zalo.setText("")
            self.user_data_dir_input_zalo.setText("")
            self.profile_name_input_zalo.setText("")

        self.run_session_dropdown_post_zalo_oa.currentIndexChanged.connect(
            lambda index: self.on_run_selected_post_zalo(index, self.run_session_dropdown_post_zalo_oa)
        )

    def init_tab_status_for_post_zalo_oa(self):
        self.tab_post_zalo_oa_status = QWidget()
        layout = QHBoxLayout()

        self.status_text_zalo = QTextEdit()
        self.status_text_zalo.setReadOnly(True)
        self.status_text_zalo.setPlaceholderText("📋 Trạng thái vòng lặp các bài...")

        self.error_text_zalo = QTextEdit()
        self.error_text_zalo.setReadOnly(True)
        self.error_text_zalo.setPlaceholderText("❌ Lỗi hệ thống...")

        layout.addWidget(self.status_text_zalo)
        layout.addWidget(self.error_text_zalo)

        self.tab_post_zalo_oa_status.setLayout(layout)

    
    def init_tab_setting_for_post_tiktok(self):
        self.tab_post_tiktok_setting = QWidget()
        layout = QFormLayout()

        self.run_session_dropdown_post_tiktok = QComboBox()
        self.run_session_dropdown_post_tiktok.addItem("📂 Chọn phiên chạy đã lưu:")
        layout.addWidget(self.run_session_dropdown_post_tiktok)

        self.chrome_path_input_tiktok = QLineEdit()
        self.chrome_path_input_tiktok.setPlaceholderText("Đường dẫn Chrome")

        self.user_data_dir_input_tiktok = QLineEdit()
        self.user_data_dir_input_tiktok.setPlaceholderText("User Data Dir")


        self.post_table_tiktok = QTableWidget()
        self.post_table_tiktok.setColumnCount(9)
        self.post_table_tiktok.setHorizontalHeaderLabels([
            "message",
            "address",
            "video_path",
            "hour",
            "minute",
            "day",
            "month",
            "year",
            "profile"
        ])

        self.post_table_tiktok.setMinimumHeight(200)

        self.select_post_file_btn_tiktok = QPushButton("📂 Chọn file Excel bài viết tiktok")
        self.select_post_file_btn_tiktok.clicked.connect(self.select_post_file_tiktok)

        self.download_template_btn_tiktok = QPushButton("📥 Tải file Excel mẫu")
        self.download_template_btn_tiktok.clicked.connect(
            lambda: self.download_excel_template("tiktok")
        )

        self.run_post_tiktok_btn = QPushButton("🚀 Chạy đăng bài tiktok")
        self.run_post_tiktok_btn.clicked.connect(self.run_post_tiktok)

        layout.addRow("🛠️ Đường dẫn Chrome:", self.chrome_path_input_tiktok)
        layout.addRow("📁 Thư mục User Data:", self.user_data_dir_input_tiktok)
        layout.addRow(self.select_post_file_btn_tiktok)
        layout.addRow(self.download_template_btn_tiktok)
        layout.addRow(self.run_post_tiktok_btn)
        layout.addRow(self.post_table_tiktok)

        self.tab_post_tiktok_setting.setLayout(layout)

        latest_session = self.load_run_sessions("tiktok", self.run_session_dropdown_post_tiktok)
        if latest_session:
            self.chrome_path_input_tiktok.setText(latest_session.get("chrome_path", ""))
            self.user_data_dir_input_tiktok.setText(latest_session.get("chrome_user_data_dir", ""))
        else:
            self.chrome_path_input_tiktok.setText("")
            self.user_data_dir_input_tiktok.setText("")

        self.run_session_dropdown_post_tiktok.currentIndexChanged.connect(
            lambda index: self.on_run_selected_tiktok(index, self.run_session_dropdown_post_tiktok)
        )

    def init_tab_status_for_post_tiktok(self):
        self.tab_post_tiktok_status = QWidget()
        layout = QHBoxLayout()

        self.status_text_tiktok = QTextEdit()
        self.status_text_tiktok.setReadOnly(True)
        self.status_text_tiktok.setPlaceholderText("📋 Trạng thái vòng lặp các bài...")

        self.error_text_tiktok = QTextEdit()
        self.error_text_tiktok.setReadOnly(True)
        self.error_text_tiktok.setPlaceholderText("❌ Lỗi hệ thống...")

        layout.addWidget(self.status_text_tiktok)
        layout.addWidget(self.error_text_tiktok)

        self.tab_post_tiktok_status.setLayout(layout)

    def show_schedule_post_element(self):
        self.tabs.clear()
        self.tabs.addTab(self.tab_home, "Trang chủ")
        self.tabs.addTab(self.tab_schedule_post_setting, "Cài đặt")
        self.tabs.addTab(self.tab_schedule_post_status, "Trạng thái")
        self.tabs.setCurrentWidget(self.tab_schedule_post_setting)
    def show_post_zalo_oa_element(self):
        self.tabs.clear()
        self.tabs.addTab(self.tab_home, "Trang chủ")
        self.tabs.addTab(self.tab_post_zalo_oa_setting, "Cài đặt Zalo OA")
        self.tabs.addTab(self.tab_post_zalo_oa_status, "Trạng thái Zalo OA")
        self.tabs.setCurrentWidget(self.tab_post_zalo_oa_setting)

    def show_post_tiktok_element(self):
        self.tabs.clear()
        self.tabs.addTab(self.tab_home, "Trang chủ")
        self.tabs.addTab(self.tab_post_tiktok_setting, "Cài đặt Tiktok")
        self.tabs.addTab(self.tab_post_tiktok_status, "Trạng thái Tiktok")
        self.tabs.setCurrentWidget(self.tab_post_tiktok_setting)
    def load_run_sessions(self, run_type=None, dropdown=None):
        """
        Load lịch sử từ SQLite và nhét vào dropdown.
        Trả về latest_session (dict) hoặc None.
        """
        latest_session = None
        try:
            conn = sqlite3.connect(HISTORY_DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT run_type, chrome_path, chrome_user_data_dir, profile_name,
                    excel_file_path, started_at
                FROM run_sessions
                WHERE run_type = ?
                ORDER BY started_at DESC
            """, (run_type,))
            rows = cursor.fetchall()
            conn.close()
        except Exception as e:
            print("❌ Lỗi truy vấn history:", e)
            rows = []

        dropdown.clear()
        dropdown.addItem("📂 Chọn phiên chạy đã lưu:", userData=None)

        print(f"▶️ load_run_sessions('{run_type}') tìm thấy {len(rows)} bản ghi.")

        for row in rows:
            session = {
                "run_type": row[0],
                "chrome_path": row[1],
                "chrome_user_data_dir": row[2],
                "profile_name": row[3],
                "excel_file_path": row[4],
                "started_at": row[5]
            }
            # cố parse datetime, nếu fail dùng thẳng string
            try:
                dt = datetime.strptime(session["started_at"], "%Y-%m-%dT%H:%M:%S.%f")
                label_time = dt.strftime("%d/%m %H:%M")
            except Exception:
                label_time = session["started_at"]

            label = f"[{label_time}] {os.path.basename(session['excel_file_path'])}"
            dropdown.addItem(label, userData=session)

            if not latest_session:
                latest_session = session

        return latest_session


    def on_run_selected(self, index, dropdown=None):
        session = dropdown.itemData(index)
        if session:
            self.run_type = session.get("run_type", "")
            self.chrome_path = session.get("chrome_path", "")
            self.user_data_dir = session.get("chrome_user_data_dir", "")
            self.profile_name = session.get("profile_name", "")
            self.excel_file_path = session.get("excel_file_path", "")

            self.chrome_path_input.setText(self.chrome_path)
            self.user_data_dir_input.setText(self.user_data_dir)
            self.profile_name_input.setText(self.profile_name)
        else:
            # Nếu chọn dòng đầu tiên (None) thì clear input
            self.chrome_path_input.setText("")
            self.user_data_dir_input.setText("")
            self.profile_name_input.setText("")

    def on_run_selected_post_zalo(self, index, dropdown=None):
        session = dropdown.itemData(index)
        if session:
            chrome_path = session.get("chrome_path", "")
            user_data_dir = session.get("chrome_user_data_dir", "")
            profile_name = session.get("profile_name", "")

            self.chrome_path_input_zalo.setText(chrome_path)
            self.user_data_dir_input_zalo.setText(user_data_dir)
            self.profile_name_input_zalo.setText(profile_name)
        else:
            self.chrome_path_input_zalo.setText("")
            self.user_data_dir_input_zalo.setText("")
            self.profile_name_input_zalo.setText("")
    def on_run_selected_tiktok(self, index, dropdown=None):
        session = dropdown.itemData(index)
        if session:
            self.run_type = session.get("run_type", "")
            self.chrome_path = session.get("chrome_path", "")
            self.user_data_dir = session.get("chrome_user_data_dir", "")
            self.excel_file_path = session.get("excel_file_path", "")

            self.chrome_path_input_tiktok.setText(self.chrome_path)
            self.user_data_dir_input_tiktok.setText(self.user_data_dir)
        else:
            self.chrome_path_input_tiktok.setText("")
            self.user_data_dir_input_tiktok.setText("")


    def download_excel_template(self, run_type=None):
        from PyQt5.QtWidgets import QFileDialog
        import os
        import sys
        import shutil

        try:
            base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
            if run_type == "facebook":
                source_path = os.path.join(base_path, "data", "lenlichdangbaifacebook.xlsx")
            elif run_type == "tiktok":
                source_path = os.path.join(base_path, "data","lenlichdangbaitiktok.xlsx")
            elif run_type == "zalooa":
                source_path = os.path.join(base_path, "data","lenlichdangbaizalooa.xlsx")
            else:
                print("❌ Không xác định được loại run_type hoặc không hỗ trợ.")
                return

            if not os.path.exists(source_path):
                print(f"❌ Không tìm thấy file mẫu tại: {source_path}")
                return

            # Chọn nơi lưu file
            save_path, _ = QFileDialog.getSaveFileName(
                self, "Lưu file Excel mẫu", os.path.basename(source_path), "Excel Files (*.xlsx)"
            )
            if not save_path:
                return

            shutil.copyfile(source_path, save_path)
            print(f"✅ Đã lưu file mẫu tại: {save_path}")

        except Exception as e:
            print("❌ Lỗi khi sao chép file:", str(e))
    def run_schedule_posting(self):
        chrome_path = self.chrome_path_input.text()
        user_data_dir = self.user_data_dir_input.text()
        profile_name = self.profile_name_input.text()
        excel_file_path = self.excel_file_path

        # 1) Lưu lịch sử
        self.save_run_session_facebook_zalooa(
            run_type="facebook",
            chrome_path=chrome_path,
            user_data_dir=user_data_dir,
            profile_name=profile_name,
            excel_file_path=excel_file_path
        )
        # 2) Refresh dropdown liền
        latest = self.load_run_sessions("facebook", self.run_session_dropdown_schedule_post)
        # 3) Nếu có phiên mới, chọn nó luôn
        if latest:
            idx = self.run_session_dropdown_schedule_post.count() - 1
            # tìm index của latest bằng userData
            for i in range(self.run_session_dropdown_schedule_post.count()):
                if self.run_session_dropdown_schedule_post.itemData(i) == latest:
                    idx = i
                    break
            self.run_session_dropdown_schedule_post.setCurrentIndex(idx)

        # 4) Chạy thread
        self.schedule_thread = SchedulePostThread(chrome_path, user_data_dir, profile_name, self.excel_file_path)
        self.schedule_thread.finished.connect(self.status_text_schedule.append)
        self.schedule_thread.error.connect(self.error_text_schedule.append)
        self.schedule_thread.log.connect(self.status_text_schedule.append)
        self.schedule_thread.system_error.connect(self.error_text_schedule.append)
        self.schedule_thread.start()

    def run_post_zalo_oa(self):
        chrome_path = self.chrome_path_input_zalo.text()
        user_data_dir = self.user_data_dir_input_zalo.text()
        profile_name = self.profile_name_input_zalo.text()
        excel_file_path = self.excel_file_path_zalo

        if not hasattr(self, "posts_data_zalo"):
            self.error_text_zalo.append("⚠️ Chưa nạp dữ liệu bài viết Zalo OA!")
            return

        # 1) Lưu lịch sử
        self.save_run_session_facebook_zalooa(
            run_type="zalooa",
            chrome_path=chrome_path,
            user_data_dir=user_data_dir,
            profile_name=profile_name,
            excel_file_path=excel_file_path
        )
        # 2) Reload dropdown Zalo OA
        latest = self.load_run_sessions("zalooa", self.run_session_dropdown_post_zalo_oa)
        # 3) Auto-select phiên mới
        if latest:
            for i in range(self.run_session_dropdown_post_zalo_oa.count()):
                if self.run_session_dropdown_post_zalo_oa.itemData(i) == latest:
                    self.run_session_dropdown_post_zalo_oa.setCurrentIndex(i)
                    break

        # 4) Start thread
        self.thread_zalo = PostZaloOaThread(
            chrome_path=chrome_path,
            user_data_dir=user_data_dir,
            profile_name=profile_name,
            excel_file_path=excel_file_path
        )
        self.thread_zalo.finished.connect(self.status_text_zalo.append)
        self.thread_zalo.error.connect(self.error_text_zalo.append)
        self.thread_zalo.log.connect(self.status_text_zalo.append)
        self.thread_zalo.start()


    def run_post_tiktok(self):
        chrome_path = self.chrome_path_input_tiktok.text()
        user_data_dir = self.user_data_dir_input_tiktok.text()
        excel_file_path = self.excel_file_path_tiktok

        if not hasattr(self, "posts_data_tiktok"):
            self.error_text_tiktok.append("⚠️ Chưa nạp dữ liệu bài viết TikTok!")
            return

        # 1) Lưu lịch sử
        self.save_run_session_tiktok(
            run_type="tiktok",
            chrome_path=chrome_path,
            user_data_dir=user_data_dir,
            excel_file_path=excel_file_path
        )
        # 2) Reload dropdown TikTok
        latest = self.load_run_sessions("tiktok", self.run_session_dropdown_post_tiktok)
        # 3) Auto-select phiên mới
        if latest:
            for i in range(self.run_session_dropdown_post_tiktok.count()):
                if self.run_session_dropdown_post_tiktok.itemData(i) == latest:
                    self.run_session_dropdown_post_tiktok.setCurrentIndex(i)
                    break

        # 4) Start thread
        self.thread_tiktok = PostTiktokThread(
            chrome_path=chrome_path,
            user_data_dir=user_data_dir,
            excel_file_path=excel_file_path
        )
        self.thread_tiktok.finished.connect(self.status_text_tiktok.append)
        self.thread_tiktok.error.connect(self.error_text_tiktok.append)
        self.thread_tiktok.log.connect(self.status_text_tiktok.append)
        self.thread_tiktok.start()
    # Run block end here
    
    # Select file block start here
    def select_post_file(self):
        self.excel_file_path, _ = QFileDialog.getOpenFileName(self, "Chọn file Excel bài viết", "", "Excel Files (*.xlsx *.xls)")
        if self.excel_file_path:
            try:
                excel_file = pd.ExcelFile(self.excel_file_path)
                self.sheet_selector.clear()
                self.sheet_selector.addItems(excel_file.sheet_names)
            except Exception as e:
                self.error_text_schedule.append(f"❌ Lỗi khi đọc file Excel: {str(e)}")


    
    def select_post_file_zalo(self):
        self.excel_file_path_zalo, _ = QFileDialog.getOpenFileName(
            self, "Chọn file Excel bài viết Zalo OA", "", "Excel Files (*.xlsx *.xls)"
        )
        if self.excel_file_path_zalo:
            try:
                df = pd.read_excel(self.excel_file_path_zalo)
                self.posts_data_zalo = []
                self.post_table_zalo.setRowCount(0)

                for i, row in df.iterrows():
                    title = str(row.get("title", "")).strip()
                    quote = str(row.get("quote", "")).strip()
                    author = str(row.get("author", "")).strip()
                    content = str(row.get("content", "")).strip()
                    call_to_action_label = str(row.get("call_to_action_label", "")).strip()
                    call_to_action_link = str(row.get("call_to_action_link", "")).strip()
                    file_path = str(row.get("file_path", "")).strip()

                    day = int(row.get("day", 1))
                    month = int(row.get("month", 1))
                    year = int(row.get("year", 2023))
                    hour = int(row.get("hour", 0))
                    minute = int(row.get("minute", 0))

                    post = {
                        "title": title,
                        "quote": quote,
                        "author": author,
                        "content": content,
                        "call_to_action_label": call_to_action_label,
                        "call_to_action_link": call_to_action_link,
                        "file_path": file_path,
                        "schedule": {
                            "day": day,
                            "month": month,
                            "year": year,
                            "hour": hour,
                            "minute": minute
                        }
                    }

                    self.posts_data_zalo.append(post)

                    # Đổ dữ liệu lên table
                    self.post_table_zalo.insertRow(i)
                    self.post_table_zalo.setItem(i, 0, QTableWidgetItem(title))
                    self.post_table_zalo.setItem(i, 1, QTableWidgetItem(quote))
                    self.post_table_zalo.setItem(i, 2, QTableWidgetItem(author))
                    self.post_table_zalo.setItem(i, 3, QTableWidgetItem(content))
                    self.post_table_zalo.setItem(i, 4, QTableWidgetItem(call_to_action_label))
                    self.post_table_zalo.setItem(i, 5, QTableWidgetItem(call_to_action_link))
                    self.post_table_zalo.setItem(i, 6, QTableWidgetItem(file_path))
                    self.post_table_zalo.setItem(i, 7, QTableWidgetItem(str(day)))
                    self.post_table_zalo.setItem(i, 8, QTableWidgetItem(str(month)))
                    self.post_table_zalo.setItem(i, 9, QTableWidgetItem(str(year)))
                    self.post_table_zalo.setItem(i, 10, QTableWidgetItem(str(hour)))
                    self.post_table_zalo.setItem(i, 11, QTableWidgetItem(str(minute)))

                self.status_text_zalo.append(
                    f"📥 Đã nạp {len(self.posts_data_zalo)} bài viết Zalo OA từ Excel."
                )

            except Exception as e:
                self.error_text_zalo.append(f"❌ Lỗi khi đọc file Excel: {str(e)}")
    def select_post_file_tiktok(self):
        self.excel_file_path_tiktok, _ = QFileDialog.getOpenFileName(
            self, "Chọn file Excel bài viết Tiktok", "", "Excel Files (*.xlsx *.xls)"
        )
        if self.excel_file_path_tiktok:
            try:
                df = pd.read_excel(self.excel_file_path_tiktok)
                self.posts_data_tiktok = []
                self.post_table_tiktok.setRowCount(0)

                for i, row in df.iterrows():
                    message = str(row.get("message", "")).strip()
                    address = str(row.get("address", "")).strip()
                    video_path = str(row.get("video_path", "")).strip()
                    hour = int(row.get("hour", 0))
                    minute = int(row.get("minute", 0))
                    day = int(row.get("day", 1))
                    month = int(row.get("month", 1))
                    year = int(row.get("year", 2023))
                    profile = str(row.get("profile", "")).strip()

                    post = {
                        "message": message,
                        "address": address,
                        "video_path": video_path,
                        "profile": profile,
                        "schedule": {
                            "day": day,
                            "month": month,
                            "year": year,
                            "hour": hour,
                            "minute": minute
                        }
                    }
                    
                    self.posts_data_tiktok.append(post)

                    self.post_table_tiktok.insertRow(i)
                    self.post_table_tiktok.setItem(i, 0, QTableWidgetItem(message))
                    self.post_table_tiktok.setItem(i, 1, QTableWidgetItem(address))
                    self.post_table_tiktok.setItem(i, 2, QTableWidgetItem(video_path))
                    self.post_table_tiktok.setItem(i, 3, QTableWidgetItem(str(hour)))
                    self.post_table_tiktok.setItem(i, 4, QTableWidgetItem(str(minute)))
                    self.post_table_tiktok.setItem(i, 5, QTableWidgetItem(str(day)))
                    self.post_table_tiktok.setItem(i, 6, QTableWidgetItem(str(month)))
                    self.post_table_tiktok.setItem(i, 7, QTableWidgetItem(str(year)))
                    self.post_table_tiktok.setItem(i, 8, QTableWidgetItem(profile))

                self.status_text_tiktok.append(
                    f"📥 Đã nạp {len(self.posts_data_tiktok)} bài viết TikTok từ Excel."
                )

            except Exception as e:
                self.error_text_tiktok.append(f"❌ Lỗi khi đọc file Excel: {str(e)}")

    # Select file block end here
    def save_run_session_facebook_zalooa(self, run_type, chrome_path, user_data_dir,profile_name, excel_file_path):
        conn = sqlite3.connect(HISTORY_DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO run_sessions (run_type, chrome_path, chrome_user_data_dir, profile_name, excel_file_path, started_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            run_type,
            chrome_path,
            user_data_dir,
            profile_name,
            excel_file_path,
            datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
        ))
        conn.commit()

        # Xóa các bản ghi dư nếu > 20
        cursor.execute("""
            DELETE FROM run_sessions
            WHERE run_type = ?
            AND id NOT IN (
                SELECT id
                FROM run_sessions
                WHERE run_type = ?
                ORDER BY started_at DESC
                LIMIT 20
            )
        """, (run_type, run_type))
        conn.commit()

        conn.close()
        print("✅ Đã lưu phiên chạy vào SQLite.")
    def save_run_session_tiktok(self, run_type, chrome_path, user_data_dir, excel_file_path):
        conn = sqlite3.connect(HISTORY_DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO run_sessions (run_type, chrome_path, chrome_user_data_dir, excel_file_path, started_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            run_type,
            chrome_path,
            user_data_dir,
            excel_file_path,
            datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
        ))
        conn.commit()

        # Xóa các bản ghi dư nếu > 20
        cursor.execute("""
            DELETE FROM run_sessions
            WHERE run_type = ?
            AND id NOT IN (
                SELECT id
                FROM run_sessions
                WHERE run_type = ?
                ORDER BY started_at DESC
                LIMIT 20
            )
        """, (run_type, run_type))
        conn.commit()

        conn.close()
        print("✅ Đã lưu phiên chạy vào SQLite.")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.stop_all_threads()
    

    def stop_all_threads(self):
        # Facebook
        if hasattr(self, "schedule_thread") and self.schedule_thread.isRunning():
            self.schedule_thread.stop()
            self.status_text_schedule.append("⛔ Đã yêu cầu dừng SchedulePostThread.")

        # Zalo
        if hasattr(self, "thread_zalo") and self.thread_zalo.isRunning():
            self.thread_zalo.stop()
            self.status_text_zalo.append("⛔ Đã yêu cầu dừng PostZaloOaThread.")

        # Tiktok
        if hasattr(self, "thread_tiktok") and self.thread_tiktok.isRunning():
            self.thread_tiktok.stop()
            self.status_text_tiktok.append("⛔ Đã yêu cầu dừng PostTiktokThread.")
    def load_sheet_data(self):
        sheet_name = self.sheet_selector.currentText()
        if sheet_name in ["IMAGE", "REELS"]:
            try:
                df = pd.read_excel(self.excel_file_path, sheet_name=sheet_name)
                self.post_table.setRowCount(0)
                self.posts_data = []

                if sheet_name == "IMAGE":
                    self.post_table.setColumnCount(6)
                    self.post_table.setHorizontalHeaderLabels(["Nội dung", "Đường dẫn ảnh", "Danh sách fanpage", "Ngày", "Giờ", "Phút"])
                    for i, row in df.iterrows():
                        self.post_table.insertRow(i)
                        self.post_table.setItem(i, 0, QTableWidgetItem(str(row.get("Nội dung", "")).strip()))
                        self.post_table.setItem(i, 1, QTableWidgetItem(str(row.get("Đường dẫn ảnh", "")).strip()))
                        self.post_table.setItem(i, 2, QTableWidgetItem(str(row.get("Danh sách Fanpage", "")).strip()))
                        self.post_table.setItem(i, 3, QTableWidgetItem(str(row.get("Ngày", "")).strip()))
                        self.post_table.setItem(i, 4, QTableWidgetItem(str(row.get("Giờ", "00")).zfill(2)))
                        self.post_table.setItem(i, 5, QTableWidgetItem(str(row.get("Phút", "00")).zfill(2)))

                elif sheet_name == "REELS":
                    self.post_table.setColumnCount(10)
                    self.post_table.setHorizontalHeaderLabels([
                        "Video", "Ảnh nền", "Địa chỉ", "Bật Messenger", "Tags",
                        "Tiêu đề", "Mô tả", "Ngày", "Giờ", "Phút"
                    ])
                    for i, row in df.iterrows():
                        self.post_table.insertRow(i)
                        for col_index, key in enumerate([
                            "Đường dẫn video", "Đường dẫn ảnh nền video", "Địa chỉ", "Bật chế độ messenger",
                            "Danh sách thẻ", "Tiêu đề", "Mô tả", "Ngày", "Giờ", "Phút"
                        ]):
                            value = str(row.get(key, "")).strip()
                            if key in ["Giờ", "Phút"]:
                                value = value.zfill(2)
                            self.post_table.setItem(i, col_index, QTableWidgetItem(value))

                self.status_text_schedule.append(f"📥 Đã nạp dữ liệu từ sheet '{sheet_name}'.")

            except Exception as e:
                self.error_text_schedule.append(f"❌ Lỗi khi load sheet '{sheet_name}': {str(e)}")
