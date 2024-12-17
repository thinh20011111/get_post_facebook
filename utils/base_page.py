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
    TITLE_POST = "/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[2]/div[{index}]/div/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[3]"
    MEDIA_DIR = "media"  # Thư mục lưu ảnh
    LOGIN_EMAIL_INPUT = "//input[@id='email' and @type='text']"
    LOGIN_PWD_INPUT = "//input[@id='password' and @type='password']"
    LOGIN_SUBMIT_BTN = "//button[@id='demo-customized-button' and ./div[text()='Đăng nhập']]"
    PROFILE_ACCOUNT_ICON = "//div[@id='root']/div/div/div/div/header/div/div/div[3]/div/div[2]/div[2]/i"
    INPUT_POST = "//textarea[@name='textInputCreatePost']"
    INPUT_MEDIA = "//input[@type='file' and @accept='image/jpeg,image/png,/.glb,video/mp4,video/avi,video/quicktime,video/Ogg,video/wmv,video/mov' and @multiple and @autocomplete='off']"
    CREATE_POST_BUTTON = "//button[@id='demo-customized-button' and @disabled]//div[text()='Đăng']"
    OPEN_FORM = "//p[text()='Ảnh/Video']"

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

    def extract_media_from_post(self, index):
        try:
            media_element = self.driver.find_element(By.XPATH, self.CONTAIN_MEDIA.replace("{index}", str(index)))
            image_elements = media_element.find_elements(By.XPATH, ".//img[contains(@src, 'fbcdn.net')]")

            if not image_elements:
                return []

            images = []
            for img in image_elements:
                img_url = img.get_attribute("src")
                if img_url:
                    try:
                        width = self.driver.execute_script("return arguments[0].naturalWidth;", img)
                        if width >= 100:
                            images.append(img_url)
                    except Exception as e:
                        print(f"Error checking image size: {e}")
            return images
        except Exception as e:
            print(f"Error extracting media: {e}")
            return []

    def extract_title_from_post(self, index):
        try:
            # Tìm phần tử bằng XPath
            title_element = self.driver.find_element(By.XPATH, self.TITLE_POST.replace("{index}", str(index)))
            
            # Lấy toàn bộ văn bản bao gồm cả các thẻ con
            title = title_element.get_attribute("innerText").strip()
            
            # Trả về văn bản đã loại bỏ các ký tự không hợp lệ (nếu có)
            return title.encode("utf-8", "ignore").decode("utf-8")
        except Exception as e:
            print(f"Error extracting title: {e}")
            return ""

    def crawl_posts(self, group_url, num_posts, existing_posts):
        print(f"Crawling posts from: {group_url}")
        self.driver.get(group_url)
        time.sleep(5)

        posts = []
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while len(posts) < num_posts:
            post_elements = self.driver.find_elements(By.XPATH, "//div[contains(@data-ad-preview, 'message')]")
            for index, post in enumerate(post_elements, start=1):
                try:
                    title = self.extract_title_from_post(index)
                    if not title or title in existing_posts:
                        continue

                    media = self.extract_media_from_post(index)
                    if not media:
                        continue

                    media_files = []  # List to store media file names

                    # Lưu các hình ảnh trực tiếp vào thư mục MEDIA_DIR
                    for i, img_url in enumerate(media):
                        try:
                            # Tạo tên file cho hình ảnh
                            img_filename = f"media_{len(posts) + 1}_{i + 1}.jpg"
                            img_path = os.path.join(self.MEDIA_DIR, img_filename)

                            # Tải và lưu hình ảnh vào thư mục MEDIA_DIR
                            response = requests.get(img_url)
                            with open(img_path, "wb") as file:
                                file.write(response.content)

                            # Lưu tên file vào danh sách
                            media_files.append(img_filename)
                        except Exception as e:
                            print(f"Error downloading image {i + 1}: {e}")

                    # Thêm bài viết vào danh sách
                    posts.append({"title": title, "media": media_files})
                    existing_posts[title] = True

                    if len(posts) >= num_posts:
                        break
                except Exception as e:
                    print(f"Error processing post {index}: {e}")

            # Cuộn trang để tải thêm bài viết
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("No more posts to load.")
                break
            last_height = new_height

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