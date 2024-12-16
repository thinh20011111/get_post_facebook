from utils.base_page import BasePage
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from utils.config import Config
from selenium.webdriver.chrome.options import Options

def main():
   # Load cấu hình
    config = Config()
    # Khởi tạo Service với đường dẫn ChromeDriver
    service = Service(config.CHROME_DRIVER_PATH)
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")  # Chặn thông báo
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Mở trang web
    base_page = BasePage(driver)
    data = base_page.get_data_from_json_file("data") or {}
    email = data["account"]["email"]
    password = data["account"]["password"]
    
    driver.get(config.FACEBOOK_URL)
    driver.maximize_window()
    # Sử dụng BasePage để thực hiện hành động
    base_page.login(email, password)
    
    input("Nhấn Enter để đóng trình duyệt...")
    driver.quit()
    
if __name__ == "__main__":
    main()
