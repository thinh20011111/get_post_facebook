from utils.base_page import BasePage
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from utils.config import Config
from selenium.webdriver.chrome.options import Options
import time
import os

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
    email_facebook = data["account_facebook"]["email"]
    password_facebook = data["account_facebook"]["password"]
    
    driver.maximize_window()
    output_file = "facebook_posts.json"
    
    try:
        driver.get(config.FACEBOOK_URL)

        # Đăng nhập Facebook (Thay thế bằng hàm đăng nhập thực tế nếu cần)
        base_page.login_facebook(email_facebook, password_facebook)
        time.sleep(60)

        # Crawl bài viết mới
        group_url = "https://www.facebook.com/tlinhww"  # Link group hoặc page cần crawl
        num_posts = 3
        existing_posts = base_page.read_existing_posts(output_file)
        new_posts = base_page.crawl_posts(group_url, num_posts, existing_posts)

        # Lưu bài viết vào file JSON
        if new_posts:
            base_page.save_to_json(group_url, new_posts, output_file)
            print(f"Đã lưu {len(new_posts)} bài viết mới vào file {output_file}.")
        else:
            print("Không có bài viết mới để lưu.")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()