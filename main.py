from utils.base_page import BasePage
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from utils.config import Config
from selenium.webdriver.chrome.options import Options
import time
import os
import json

def main():
    # Load cấu hình
    config = Config()

    # Khởi tạo Service với đường dẫn ChromeDriver
    service = Service(config.CHROME_DRIVER_PATH)
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")  # Chặn thông báo
    chrome_options.add_argument("--headless")  # Chế độ không giao diện
    chrome_options.add_argument("--disable-gpu")  # Vô hiệu hóa GPU khi chạy headless
    chrome_options.add_argument("--window-size=1920x1080")  # Thiết lập kích thước cửa sổ để tránh một số vấn đề hiển thị
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Mở trang web
    base_page = BasePage(driver)
    accounts_filename = "account.json"  # Đọc dữ liệu tài khoản từ file account.json
    output_file = "facebook_posts.json"
    data_filename = "data.json"
    
    # Đọc dữ liệu tài khoản từ account.json
    with open(accounts_filename, 'r') as file:
        accounts_data = json.load(file)
            
    with open(data_filename, 'r') as data_file:
        data = json.load(data_file)

    driver.maximize_window()

    try:
        # Đăng nhập vào Facebook một lần
        facebook_account = data.get("account_facebook", {})
        email_facebook = facebook_account["email"]
        password_facebook = facebook_account["password"]

        driver.get(config.FACEBOOK_URL)
        base_page.login_facebook(email_facebook, password_facebook)

        # Lặp qua tất cả các tài khoản và xử lý
        for account_key, account_data in accounts_data.items():
            try:
                print(f"\nĐang xử lý tài khoản: {account_key}")

                # Lấy thông tin từ tài khoản (url1, url2, username, password)
                group_url = account_data["url2"]
                emso_username = account_data["username"]
                emso_password = account_data["password"]
                url1 = account_data["url1"]

                # Crawl bài viết mới từ Facebook group_url
                num_posts = 2
                existing_posts = base_page.read_existing_posts(output_file)
                new_posts = base_page.crawl_posts(group_url, num_posts, existing_posts)

                # Kiểm tra nếu không có bài viết mới
                if not new_posts:
                    print("Không có bài viết mới để crawl. Bỏ qua tài khoản EMSo này.")
                    continue  # Bỏ qua tài khoản EMSo này và chuyển sang tài khoản tiếp theo

                # Lưu bài viết vào file JSON nếu có bài mới
                base_page.save_to_json(group_url, new_posts, output_file)
                print(f"Đã lưu {len(new_posts)} bài viết mới vào file {output_file}.")

                base_page.login_emso(config.EMSO_URL, emso_username, emso_password)

                # Truy cập vào url1 và đăng bài
                print(f"Truy cập vào URL: {url1}")
                base_page.driver.get(url1)
                for post in new_posts:
                    title = post.get("title", "")
                    image_paths = post.get("media", "")
                    base_page.create_post(title, image_paths)
                    print(f"Đã đăng bài: {title}")
                    
                base_page.logout()

            except Exception as e:
                print(f"Đã gặp lỗi khi xử lý tài khoản {account_key}")
                PROFILE_ACCOUNT_ICON = "//div[@id='root']/div/div/div/div/header/div/div/div[3]/div/div[2]/div[2]/i"
                if base_page.is_element_present_by_xpath(PROFILE_ACCOUNT_ICON):
                    base_page.logout()
                    continue  # Tiếp tục với tài khoản tiếp theo nếu gặp lỗi`   
                else:
                    continue
        print("Hoàn tất tất cả các bài đăng.")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
