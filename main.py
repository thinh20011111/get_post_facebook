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
    
    driver.maximize_window()
    # Sử dụng BasePage để thực hiện hành động
    group_url = "https://www.facebook.com/tlinhww"  # Link group hoặc page cần crawl
    
    # Số lượng bài viết cần crawl
    num_posts = 10
    output_file = "facebook_posts.csv"
    
    try:
        driver.get(config.FACEBOOK_URL)
        # Đăng nhập Facebook
        base_page.login(email, password)
        
       # Crawl bài viết mới
        existing_posts = base_page.read_existing_posts(output_file)
        new_posts = base_page.crawl_posts(group_url, num_posts, existing_posts)

        # Lưu bài viết vào file CSV
        base_page.read_and_update_csv(new_posts, output_file)
    finally:
        driver.quit()
    
    input("Nhấn Enter để đóng trình duyệt...")
    driver.quit()
    
if __name__ == "__main__":
    main()
