import threading
import requests

# URL của website hoặc endpoint n8n mà bạn muốn kiểm tra
url = "https://theodorescsa.id.vn/"

def send_request():
    response = requests.get(url)
    print(f"Response code: {response.status_code}")

def load_test(num_requests):
    threads = []
    for _ in range(num_requests):
        thread = threading.Thread(target=send_request)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

# Kiểm tra tải với 100 yêu cầu đồng thời
load_test(100)
