
import sys, os
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox
)
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from dotenv import load_dotenv
import socket
import keyring
import sqlite3
from keyring.backends import Windows
from app import AppWindow

keyring.set_keyring(Windows.WinVaultKeyring())

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")

env_path = os.path.join(base_path, ".env")
load_dotenv(dotenv_path=env_path)
DJANGO_API_URL = os.getenv('DJANGO_API_LOGIN_URL')
CONFIG_FILE = os.getenv('CONFIG_FILE')

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Đăng nhập")
        self.setGeometry(200, 200, 300, 200)
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")

        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        # Ví dụ: đường dẫn tới style.qss
        qss_path = os.path.join(base_path, "static", "qss", "login.qss")
        self.setStyleSheet(open(qss_path).read())
        self.db_path = os.path.join(base_path, "data", "config.db")
        self.copy_db_to_local_if_needed()
        self.init_db()
        layout = QVBoxLayout()
        self.config_file_path = os.path.join(base_path, "data", "config.json")

        self.label = QLabel("Số điện thoại:")
        self.phone_number_input = QLineEdit()
        self.label2 = QLabel("Mật khẩu:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)  # Ẩn mật khẩu
        self.label3 = QLabel("Id thiết bị:")
        self.device_id_input = QLineEdit(self.get_local_ip())
        self.device_id_input.setReadOnly(True)  # Không cho người dùng chỉnh sửa

        
        self.remember_checkbox = QCheckBox("Ghi nhớ mật khẩu")
        self.login_button = QPushButton("Đăng nhập")
        self.login_button.clicked.connect(self.login)

        layout.addWidget(self.label)
        layout.addWidget(self.phone_number_input)
        layout.addWidget(self.label2)
        layout.addWidget(self.password_input)
        layout.addWidget(self.label3)
        layout.addWidget(self.device_id_input)
        layout.addWidget(self.remember_checkbox)
        layout.addWidget(self.login_button)

        self.setLayout(layout)
        self.load_saved_credentials()
    def copy_db_to_local_if_needed(self):
        if getattr(sys, 'frozen', False):
            db_src = os.path.join(sys._MEIPASS, "data", "config.db")
            db_dest_dir = os.path.join(os.path.expanduser("~"), ".zaloapp")
            os.makedirs(db_dest_dir, exist_ok=True)
            db_dest = os.path.join(db_dest_dir, "config.db")

            if not os.path.exists(db_dest):
                import shutil
                shutil.copy2(db_src, db_dest)

            self.db_path = db_dest
        else:
            self.db_path = os.path.join(base_path, "data", "config.db")

    def init_db(self):
        # os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS credentials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone TEXT,
                remember INTEGER
            )
        """)
        conn.commit()
        conn.close()

    def save_credentials(self, phone, password, remember):
        # Ghi số điện thoại và trạng thái "ghi nhớ" vào SQLite
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM credentials")  # Chỉ lưu 1 bản ghi
        cursor.execute("INSERT INTO credentials (phone, remember) VALUES (?, ?)", (phone, int(remember)))
        conn.commit()
        conn.close()
        SERVICE_NAME = "ZaloApp"  # Tên ứng dụng để lưu trên hệ thống

        # Nếu nhớ mật khẩu, lưu vào keyring
        if remember:
            keyring.set_password(SERVICE_NAME, phone, password)
        else:
            # Nếu không nhớ nữa, xóa khỏi keyring
            try:
                keyring.delete_password(SERVICE_NAME, phone)
            except keyring.errors.PasswordDeleteError:
                pass  # Không có cũng không sao

    def load_saved_credentials(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT phone, remember FROM credentials ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        SERVICE_NAME = "ZaloApp"  # Tên ứng dụng để lưu trên hệ thống

        if row:
            phone, remember = row
            self.phone_number_input.setText(phone)
            self.remember_checkbox.setChecked(bool(remember))
            if remember:
                try:
                    password = keyring.get_password(SERVICE_NAME, phone)
                    if password:
                        self.password_input.setText(password)
                except Exception as e:
                    print("❗ Không thể lấy mật khẩu từ keyring:", e)
    
    def login(self):
        phone_number = self.phone_number_input.text()
        password = self.password_input.text()
        device_id = self.device_id_input.text()
        remember = self.remember_checkbox.isChecked()

        # Lưu thông tin đăng nhập
        self.save_credentials(phone_number, password, remember)

        # Gửi yêu cầu tới API
        data = {"phone_number": phone_number, "password": password, "device_id": device_id}
        response = requests.post(DJANGO_API_URL, json=data)

        if response.status_code == 200:
            token = response.json().get("access_token")
            session_key = response.json().get("session_key")
            self.hide()
            self.home = AppWindow(token, session_key, device_id)
            self.home.show()
        else:
            self.label.setText("Đăng nhập thất bại! Kiểm tra lại tài khoản.")



    def get_local_ip(self):
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            return local_ip

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Gán icon vào cửa sổ chính => để icon hiện trên taskbar
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    icon_path = os.path.join(base_path, "icon.ico")
    app.setWindowIcon(QIcon(icon_path))
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())

