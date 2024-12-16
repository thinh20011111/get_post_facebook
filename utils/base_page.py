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
    TITLE_POST = "/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[2]/div[{index}]/div/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[3]/div[1]/div/div/div/div/span"
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

    def read_existing_posts(self, output_file):
        existing_posts = {}
        
        # Kiểm tra nếu file CSV tồn tại
        if os.path.exists(output_file):
            with open(output_file, mode="r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                
                # Kiểm tra xem file CSV có chứa tiêu đề không
                if "Post Content" not in reader.fieldnames:
                    print(f"Warning: The CSV file does not contain the expected header 'Post Content'.")
                    return existing_posts
                
                # Đọc từng dòng dữ liệu và lưu lại nội dung bài viết
                for row in reader:
                    # Kiểm tra nếu "Post Content" có trong dòng dữ liệu
                    if "Post Content" in row:
                        existing_posts[row["Post Content"]] = True
        
        return existing_posts
    
    def extract_media_from_post(self, index):
        try:
            media_element = self.driver.find_element(By.XPATH, self.CONTAIN_MEDIA.replace("{index}", str(index)))
            image_elements = media_element.find_elements(By.XPATH, ".//img[contains(@src, 'fbcdn.net')]")  # Tìm các ảnh
            video_elements = media_element.find_elements(By.XPATH, ".//video")  # Tìm các video

            # Nếu có video thì bỏ qua và không lấy media
            if video_elements:
                return {"images": [], "videos": []}

            filtered_images = []
            for img in image_elements:
                img_url = img.get_attribute("src")
                if img_url:
                    try:
                        width = self.driver.execute_script("return arguments[0].naturalWidth;", img)
                        if width >= 100:  # Kiểm tra kích thước ảnh
                            filtered_images.append(img_url)
                    except Exception as e:
                        print(f"Lỗi khi kiểm tra kích thước ảnh: {e}")

            return {"images": filtered_images, "videos": []}
        except Exception as e:
            print(f"Lỗi khi trích xuất media từ bài viết thứ {index}: {e}")
            return {"images": [], "videos": []}
    
    def extract_title_from_post(self, index):
        try:
            title_element = self.driver.find_element(By.XPATH, self.TITLE_POST.replace("{index}", str(index)))
            return title_element.text.strip() if title_element else ""
        except Exception as e:
            print(f"Lỗi khi trích xuất tiêu đề từ bài viết thứ {index}: {e}")
            return ""

    def crawl_posts(self, group_url, num_posts, existing_posts):
        print(f"Đang crawl bài viết từ: {group_url}")
        self.driver.get(group_url)
        time.sleep(5)

        posts = []
        scroll_pause_time = 3
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while len(posts) < num_posts:
            post_elements = self.driver.find_elements(By.XPATH, "//div[contains(@data-ad-preview, 'message')]")
            for index, post in enumerate(post_elements, start=1):
                try:
                    title = self.extract_title_from_post(index)  # Lấy tiêu đề từ bài viết
                    if title and title not in existing_posts:  # Chỉ lấy bài có tiêu đề và chưa tồn tại
                        media = self.extract_media_from_post(index)  # Lấy media từ bài viết

                        if media["images"]:  # Nếu có ảnh thì xử lý
                            post_id = len(posts) + 1
                            post_folder = os.path.join(self.MEDIA_DIR, f"post_{post_id}")
                            os.makedirs(post_folder, exist_ok=True)

                            for i, img_url in enumerate(media["images"]):
                                try:
                                    response = requests.get(img_url)
                                    img_path = os.path.join(post_folder, f"image_{i + 1}.jpg")
                                    with open(img_path, "wb") as file:
                                        file.write(response.content)
                                except Exception as e:
                                    print(f"Lỗi khi tải ảnh {i + 1}: {e}")

                            posts.append({
                                "Post Content": title,  # Lưu tiêu đề
                                "Media": [os.path.join(post_folder, f"image_{i + 1}.jpg") for i in range(len(media["images"]))],  # Lưu ảnh
                            })

                            existing_posts[title] = True  # Đánh dấu bài viết đã lấy

                    if len(posts) >= num_posts:
                        break
                except Exception as e:
                    print(f"Lỗi khi lấy bài viết thứ {index}: {e}")

            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("Không thể tải thêm bài viết.")
                break
            last_height = new_height

        print(f"Đã crawl được {len(posts)} bài viết mới.")
        return posts

    def save_to_csv(self, posts_with_media, output_file):
        # Kiểm tra xem file có tồn tại không, nếu không thì tạo mới
        try:
            with open(output_file, mode='a', newline='', encoding='utf-8') as file:
                fieldnames = ["Post Content", "Media"]  # Các cột trong CSV

                # Nếu file chưa có dữ liệu thì ghi tiêu đề cột
                writer = csv.DictWriter(file, fieldnames=fieldnames)

                # Ghi tiêu đề cột chỉ một lần khi file mới
                if file.tell() == 0:  # Kiểm tra nếu file trống
                    writer.writeheader()

                # Ghi từng bài post vào file
                for post in posts_with_media:
                    writer.writerow(post)
        except Exception as e:
            print(f"Lỗi khi lưu vào CSV: {e}")
            
    def read_existing_posts(self, filename):
        import csv
        existing_posts = {}
        try:
            with open(filename, mode='r', encoding="utf-8-sig") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    existing_posts[row["Post Content"]] = True
        except FileNotFoundError:
            print(f"File {filename} không tồn tại, tạo mới...")
        return existing_posts