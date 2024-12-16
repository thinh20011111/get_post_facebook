from utils.base_page import BasePage
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from utils.config import Config
from selenium.webdriver.chrome.options import Options
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

        # Lưu bài viết vào file CSV và thông tin ảnh vào thư mục media
        posts_with_media = []
        for post in new_posts:
            post_content = post["content"]
            media_urls = post["media"]
            
            # Map ảnh với bài viết, tạo danh sách ảnh tương ứng
            media_paths = []
            for media_url in media_urls:
                media_name = media_url.split("/")[-1]
                media_path = os.path.join(base_page.MEDIA_DIR, media_name)  # Lưu ảnh vào thư mục media
                media_paths.append(media_path)

            # Thêm thông tin vào bài viết
            posts_with_media.append({
                "Post Content": post_content,
                "Media": "; ".join(media_paths)  # Dùng dấu phân cách giữa các ảnh
            })

        # Cập nhật CSV với bài viết mới và thông tin ảnh
        base_page.save_to_csv(posts_with_media, output_file)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()