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
    output_file = "facebook_posts.csv"
    
    try:
        driver.get(config.FACEBOOK_URL)
        
        # Đăng nhập Facebook
        base_page.login_facebook(email_facebook, password_facebook)
        
        # Crawl bài viết mới
        group_url = "https://www.facebook.com/tlinhww"  # Link group hoặc page cần crawl
        num_posts = 3
        existing_posts = base_page.read_existing_posts(output_file)
        new_posts = base_page.crawl_posts(group_url, num_posts, existing_posts)

        # Lưu bài viết vào file CSV và thông tin ảnh vào thư mục media
        posts_with_media = []
        for post in new_posts:
            post_content = post.get("Post Content", "")  # Lấy nội dung bài viết
            media_urls = post.get("Media", [])          # Lấy danh sách media

            if post_content and media_urls:  # Chỉ lưu bài viết có tiêu đề và media
                posts_with_media.append({
                    "Post Content": post_content,
                    "Media": "; ".join(media_urls)  # Dùng dấu phân cách giữa các ảnh
                })

        # Kiểm tra dữ liệu trước khi lưu
        if posts_with_media:
            print(f"Đang lưu {len(posts_with_media)} bài viết vào file CSV.")
            base_page.save_to_csv(posts_with_media, output_file)
        else:
            print("Không có bài viết nào để lưu vào CSV.")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()