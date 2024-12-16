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
import pandas as pd
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

    def find_element(self, locator_type, locator_value):
        return self.driver.find_element(locator_type, locator_value)
    
    def login(self, username, password):
        self.input_text(self.INPUT_USERNAME, username)
        self.input_text(self.INPUT_PASSWORD, password)
        self.click_element(self.LOGIN_BUTTON) 
        time.sleep(5)
        
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

    def read_existing_posts(self, filename):
        """
        Đọc danh sách bài viết đã tồn tại từ file CSV. Nếu file không tồn tại, trả về tập hợp rỗng.
        """
        try:
            if not os.path.exists(filename):
                print(f"File {filename} không tồn tại, tạo file mới.")
                return set()  # Nếu file không tồn tại, tạo tập hợp rỗng

            # Đọc file CSV
            existing_df = pd.read_csv(filename, encoding='utf-8-sig')
            existing_posts = set(existing_df["Post Content"].tolist())
            print(f"Đã tải {len(existing_posts)} bài viết từ file {filename}.")
            return existing_posts
        except pd.errors.ParserError:
            print(f"Lỗi phân tích cú pháp khi đọc file {filename}. Kiểm tra định dạng file.")
            return set()  # Nếu có lỗi khi đọc, trả về tập hợp rỗng
        except Exception as e:
            print(f"Lỗi không xác định khi đọc file {filename}: {e}")
            return set()  # Nếu gặp lỗi khác, trả về tập hợp rỗng

    def crawl_posts(self, group_url, num_posts, existing_posts):
        """
        Crawl bài viết từ group hoặc trang Facebook, bỏ qua bài viết trùng lặp.
        """
        print(f"Đang crawl bài viết từ: {group_url}")
        self.driver.get(group_url)
        time.sleep(5)  # Chờ trang tải

        posts = []
        scroll_pause_time = 3  # Thời gian chờ mỗi lần scroll
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while len(posts) < num_posts:
            # Lấy các bài viết
            post_elements = self.driver.find_elements(By.XPATH, "//div[contains(@data-ad-preview, 'message')]")
            for post in post_elements:
                try:
                    content = post.text.strip()
                    if content and content not in posts and content not in existing_posts:  # Tránh trùng lặp
                        posts.append(content)
                        print(f"Thu thập bài viết: {content[:30]}...")  # Hiển thị 30 ký tự đầu
                    if len(posts) >= num_posts:
                        break
                except Exception as e:
                    print(f"Lỗi khi lấy bài viết: {e}")

            # Scroll xuống
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)

            # Kiểm tra nếu không scroll được nữa
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("Không thể tải thêm bài viết.")
                break
            last_height = new_height
        
        print(f"Đã crawl được {len(posts)} bài viết mới.")
        return posts

    def read_and_update_csv(self, new_data, filename):
        """
        Đọc dữ liệu từ file CSV, loại bỏ dữ liệu trùng lặp, và ghi dữ liệu mới vào.
        """
        # Đọc bài viết hiện có từ file CSV
        existing_posts = self.read_existing_posts(filename)

        # Loại bỏ bài viết trùng lặp
        filtered_data = [post for post in new_data if post not in existing_posts]
        if not filtered_data:
            print("Không có bài viết mới để thêm vào file.")
            return

        # Ghi dữ liệu mới vào file CSV
        new_df = pd.DataFrame(filtered_data, columns=["Post Content"])

        # Kiểm tra xem file đã tồn tại chưa, nếu chưa thì tạo mới và ghi header
        if not os.path.exists(filename):
            new_df.to_csv(filename, mode='w', index=False, encoding="utf-8-sig")
        else:
            new_df.to_csv(filename, mode='a', index=False, encoding="utf-8-sig", header=False)
        
        print(f"Đã thêm {len(filtered_data)} bài viết mới vào file {filename}.")