from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
import os
import logging
from PIL import Image
from io import BytesIO
import csv
import pandas as pd
import requests
import json
import time

logging.basicConfig(
    filename='error.log', 
    level=logging.ERROR, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class BasePage:
    def __init__(self, driver):
        self.driver = driver
    
    INPUT_USERNAME = "//input[@id='email']"
    INPUT_PASSWORD = "//input[@id='pass']"    
    LOGIN_BUTTON = "//button[text()='Log in']"
    CONTAIN_MEDIA = "/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[2]/div[{index}]/div/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[3]/div[2]"
    TITLE_POST = "/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[2]/div[{index}]/div/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[3]/div[1]/div/div"
    MEDIA_DIR = "media"  # Thư mục lưu ảnh
    LOGIN_EMAIL_INPUT = "//input[@id='email' and @type='text']"
    LOGIN_PWD_INPUT = "//input[@id='password' and @type='password']"
    LOGIN_SUBMIT_BTN = "//button[@id='demo-customized-button' and ./div[text()='Đăng nhập']]"
    PROFILE_ACCOUNT_ICON = "//div[@id='root']/div/div/div/div/header/div/div/div[3]/div/div[2]/div[2]/i"
    INPUT_POST = "//textarea[@name='textInputCreatePost']"
    INPUT_MEDIA = "//input[@type='file' and @accept='image/jpeg,image/png,/.glb,video/mp4,video/avi,video/quicktime,video/Ogg,video/wmv,video/mov' and @multiple and @autocomplete='off']"
    CREATE_POST_BUTTON = "//button[@id='demo-customized-button']//div[text()='Đăng']"
    OPEN_FORM = "//p[text()='Ảnh/Video']"
    LOGOUT_BTN = "//header//div[@role= 'button' and ./div/p[text()='Đăng xuất']]"
    MEDIA_TAB = "//div[@class='html-div xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x18d9i69 x6s0dn4 x9f619 x78zum5 x2lah0s x1hshjfz x1n2onr6 xng8ra x1pi30zi x1swvt13']/span[text()='Ảnh']"
    POSTS = "/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div/div/div/div/div/div[3]/div[1]/div"
    POST = "/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div/div/div/div/div/div[3]/div[1]/div[{index}]"
    VIEW_DETAIL = "//a[text()='Xem bài viết']"
    TITLE_POST_DETAIL = "//div[contains(@data-ad-preview, 'message')]"
    TITLE_POST = "/html/body/div[1]/div/div/div[1]/div/div[5]/div/div/div[3]/div[2]/div/div[3]/div[2]/div/div/div[1]/div[1]/div[1]/div[2]/span"
    CLOSE_DETAIL = "/html/body/div[1]/div/div/div[1]/div/div[2]/div[1]/a"
    MEDIA = "/html/body/div[1]/div/div/div[1]/div/div[5]/div/div/div[3]/div[2]/div/div[2]"
    MEDIA_IN_DETAIL = "/html/body/div[1]/div/div/div[1]/div/div[6]/div/div/div[2]/div/div/div/div/div/div/div/div[2]/div[2]/div/div/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[3]"
    
    def find_element(self, locator_type, locator_value):
        return self.driver.find_element(locator_type, locator_value)
    
    def login_facebook(self, username, password):
        self.input_text(self.INPUT_USERNAME, username)
        self.input_text(self.INPUT_PASSWORD, password)
        self.click_element(self.LOGIN_BUTTON) 
        time.sleep(5)
    
    def login_emso(self, url, username, password):
        self.driver.get(url)
        time.sleep(1)
        self.input_text(self.LOGIN_EMAIL_INPUT, username)
        self.input_text(self.LOGIN_PWD_INPUT, password)
        self.click_element(self.LOGIN_SUBMIT_BTN)
        self.wait_for_element_clickable(self.PROFILE_ACCOUNT_ICON)
        
    def logout(self):
        self.click_element(self.PROFILE_ACCOUNT_ICON)
        self.click_element(self.LOGOUT_BTN)
        
    def is_element_present_by_xpath(self, xpath: str) -> bool:
        try:
            # Tìm phần tử bằng XPath
            self.driver.find_element(By.XPATH, xpath)
            return True
        except NoSuchElementException:
            # Nếu không tìm thấy phần tử, trả về False
            return False
    
    def click_element(self, xpath: str, timeout=15):
        try:
            element = self.wait_for_element_clickable(xpath, timeout)
            # Cuộn đến phần tử nếu cần
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            element.click()
            # print(f"Clicked on element with XPath: {xpath}")
        except Exception as e:
            print(f"Error while clicking element with XPath '{xpath}': {e}")
            raise
        
    def wait_for_element_clickable(self, xpath: str, timeout=15):
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
        except TimeoutException:
            print(f"Element with XPath '{xpath}' not clickable after {timeout} seconds.")
            raise
 
    def input_text(self, xpath: str, text: str):
        try:
            # Chờ phần tử khả dụng
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )

            # Tìm phần tử và cuộn tới nó
            element = self.driver.find_element(By.XPATH, xpath)
            actions = ActionChains(self.driver)
            actions.move_to_element(element).perform()

            # Đảm bảo phần tử hiện hữu và không bị thay đổi trạng thái
            for _ in range(3):  # Thử tối đa 3 lần nếu có lỗi StaleElementReferenceException
                try:
                    # Chờ phần tử khả dụng lại nếu cần
                    WebDriverWait(self.driver, 3).until(EC.visibility_of(element))
                    
                    # Xóa văn bản hiện tại
                    element.click()
                    element.send_keys(Keys.CONTROL + "a")  # Chọn tất cả văn bản
                    element.send_keys(Keys.DELETE)  # Xóa văn bản cũ
                    
                    # Nhập văn bản mới
                    element.send_keys(text)
                    return  # Thành công, thoát khỏi hàm
                except StaleElementReferenceException:
                    # Reload phần tử nếu DOM thay đổi
                    element = self.driver.find_element(By.XPATH, xpath)
            raise Exception("Không thể tương tác với phần tử sau nhiều lần thử.")
        except TimeoutException:
            print("Phần tử không sẵn sàng hoặc không khả dụng trong thời gian chờ.")
        except Exception as e:
            print(f"Không thể nhập văn bản vào phần tử: {e}")
    
    def get_text_from_element(self, locator):
        text = self.driver.find_element(By.XPATH, locator).text
        return text
    
    def get_data_from_json_file(self, file_name):
        data_file = f'{file_name}.json'
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f, strict = False)
        return data

    def get_title_and_media(self):
        try:
            # Lấy title và media từ view ban đầu (không có view detail)
            title_element = self.driver.find_element(By.XPATH, self.TITLE_POST)
            media_element = self.driver.find_element(By.XPATH, self.MEDIA)

            # Lấy text của title
            title = title_element.get_attribute("innerText").strip()

            # Lấy media (hình ảnh) từ phần media
            media_elements = media_element.find_elements(By.XPATH, ".//img[contains(@src, 'fbcdn.net')]")

            # Nếu không có title hoặc media, bỏ qua
            if not title or not media_elements:
                return {"title": "", "media": []}

            # Lấy URL của các ảnh media
            images = []
            for img in media_elements:
                img_url = img.get_attribute("src")
                if img_url:
                    images.append(img_url)

            # Trả về title và media
            return {"title": title, "media": images}

        except Exception as e:
            print(f"Error extracting title and media: {e}")
            return {"title": "", "media": []}  # Nếu có lỗi, trả về title và media trống

    def crawl_posts(self, group_url, num_posts, existing_posts):
        print(f"Crawling posts from: {group_url}")
        self.driver.get(group_url)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, self.MEDIA_TAB)))  # Ensure the media tab is loaded
        self.click_element(self.MEDIA_TAB)
        time.sleep(2)

        posts = []
        while len(posts) < num_posts:
            post_elements = self.driver.find_elements(By.XPATH, self.POSTS)
            for index, post in enumerate(post_elements, start=1):
                try:
                    # Click the post (this will navigate to the post details)
                    self.click_element(self.POST.replace("{index}", str(index)))
                    WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH, self.TITLE_POST)))  # Ensure post loads

                    # Use get_title_and_media function to extract title and media
                    post_data = self.get_title_and_media()

                    # Check if the post has valid title and media
                    title = post_data["title"]
                    media = post_data["media"]
                    media_files = []  # List to store media file names

                    # Save images directly into the MEDIA_DIR
                    for i, img_url in enumerate(media):
                        try:
                            # Create filename for the image
                            img_filename = f"media_{len(posts) + 1}_{i + 1}.jpg"
                            img_path = os.path.join(self.MEDIA_DIR, img_filename)

                            # Download and save the image into MEDIA_DIR
                            response = requests.get(img_url)
                            with open(img_path, "wb") as file:
                                file.write(response.content)

                            # Save filename to the list
                            media_files.append(img_filename)
                        except Exception as e:
                            print(f"Error downloading image {i + 1}: {e}")

                    # Add post to the list
                    posts.append({"title": title, "media": media_files})
                    existing_posts[title] = True

                    if len(posts) >= num_posts:
                        break

                except Exception as e:
                    print(f"Error processing post {index}:")
                    self.driver.back()  # Ensure we go back even if an error occurs

        print(f"Crawled {len(posts)} new posts.")
        return posts

    @staticmethod
    def extract_username_from_url(url):
        """
        Trích xuất username từ URL của Facebook.
        """
        match = re.search(r"https://www\.facebook\.com/([^/]+)", url)
        if match:
            return match.group(1)
        return None

    def save_to_json(self, group_url, posts, output_file):
        try:
            # Trích xuất username từ group_url
            username = self.extract_username_from_url(group_url)

            # Nếu không trích xuất được username, dừng lại
            if not username:
                print("Invalid Facebook URL, cannot extract username.")
                return

            # Nếu file chưa tồn tại, tạo mới một dictionary rỗng
            if not os.path.exists(output_file):
                data = {}
            else:
                # Nếu file đã tồn tại, đọc dữ liệu từ file
                with open(output_file, "r", encoding="utf-8") as file:
                    try:
                        data = json.load(file)
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON from {output_file}. The file might be corrupted.")
                        return  # Nếu file bị lỗi, dừng lại

            # Lưu username vào data
            data[username] = posts

            # Lưu dữ liệu vào file JSON
            with open(output_file, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

            print(f"Data saved successfully to {output_file}.")

        except Exception as e:
            print(f"Error saving to JSON: {e}")
            
    def read_existing_posts(self, output_file):
        try:
            if os.path.exists(output_file):
                with open(output_file, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    existing_posts = {}
                    for group, posts in data.items():
                        for post in posts:
                            existing_posts[post["title"]] = True
                    return existing_posts
        except Exception as e:
            print(f"Error reading existing posts: {e}")
        return {}

    def upload_image(self, file_input_locator, image_name):
        try:
            # Kiểm tra nếu image_name là một danh sách, nếu có, lấy phần tử đầu tiên
            if isinstance(image_name, list):
                image_name = image_name[0]  # Lấy ảnh đầu tiên trong danh sách

            # Xác định đường dẫn tuyệt đối của ảnh trong thư mục media
            image_path = os.path.abspath(f"media/{image_name}")  # Thư mục media và tên tệp ảnh

            # Kiểm tra xem file có tồn tại không
            if not os.path.exists(image_path):
                print(f"File không tồn tại: {image_path}")
                return

            # Tìm phần tử input và gửi đường dẫn ảnh
            file_input = self.wait_for_element_present(file_input_locator)
            file_input.send_keys(image_path)

            print(f"Đã upload ảnh: {image_path}")

        except Exception as e:
            print(f"Error uploading image: {e}")
        
    def wait_for_element_present(self, locator, timeout=15):
        WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.XPATH, locator)))
        return self.find_element_by_locator(locator)

    def find_element_by_locator(self, locator, context=None):
        if context:
            element = context.find_element(By.XPATH, locator)
        else:
            element = self.driver.find_element(By.XPATH, locator)
        return element

    def read_accounts_from_json(self, filename):
        with open(filename, 'r') as file:
            accounts_data = json.load(file)
        return accounts_data

    # Đọc các bài viết từ file facebook_posts.json
    def read_posts_from_json(self, filename, pagename):
        with open(filename, 'r') as file:
            posts_data = json.load(file)
        return posts_data.get(pagename, [])

    # Đăng bài lên Facebook (giả định)
    def create_post(self, title, image_name):
        # Mở form tạo bài đăng
        self.click_element(self.OPEN_FORM)

        # Nhập tiêu đề bài đăng
        self.input_text(self.INPUT_POST, title)

        # Tải lên ảnh (nếu có)
        self.upload_image(self.INPUT_MEDIA, image_name)

        # Nhấn nút đăng bài
        self.click_element(self.CREATE_POST_BUTTON)
        time.sleep(5)  # Đợi một chút để quá trình đăng bài hoàn tất
    
    # Hàm chính kiểm tra và đăng bài
    def process_post(self, group_url, accounts_filename, posts_filename):
        # Trích xuất Page Name từ URL
        pagename = group_url.split("/")[-1]  # Lấy phần cuối của URL để làm page name

        # Đọc dữ liệu tài khoản từ file JSON
        accounts_data = self.read_accounts_from_json(accounts_filename)

        # Kiểm tra nếu pagename có trong tài khoản
        if pagename in accounts_data:
            print(f"Trang {pagename} có trong tài khoản, bắt đầu đăng bài.")

            # Đọc các bài viết từ file facebook_posts.json
            posts = self.read_posts_from_json(posts_filename, pagename)

            # Đăng tất cả các bài viết của trang
            for post in posts:
                # Lấy tiêu đề bài đăng
                title = post.get("title", "")

                # Lấy đường dẫn ảnh từ trường "media"
                image_paths = post.get("media", [])

                # Thực hiện đăng bài
                self.create_post(title, self.FILE_INPUT_LOCATOR, image_paths)
        else:
            print(f"Trang {pagename} không tồn tại trong tài khoản.")