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
import base64
import requests
from utils.config import Config
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
        self.config = Config()
        self.driver = driver
        self.media_dir = os.path.join(os.getcwd(), "media")
        os.makedirs(self.media_dir, exist_ok=True)
        self.output_file = "post.json"
    
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
    VIEW_DETAIL = "//a[text()='Xem bài viết']"
    CLOSE_DETAIL = "/html/body/div[1]/div/div/div[1]/div/div[2]/div[1]/a"
    MEDIA_IN_DETAIL = "/html/body/div[1]/div/div/div[1]/div/div[6]/div/div/div[2]/div/div/div/div/div/div/div/div[2]/div[2]/div/div/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[3]"
    TITLE_POST = "(//div[contains(@data-ad-comet-preview, 'message')])[{index}]"
    POST = "//div[@aria-posinset='{index}']"
    MORE_OPTION = "(//div[@aria-haspopup='menu' and contains(@class, 'x1i10hfl') and contains(@aria-label, 'Hành động với bài viết này')])[{index}]"
    SKIP_BANNER = "//div[contains(text(), 'Tiếp tục')]"
    
    def find_element(self, locator_type, locator_value):
        return self.driver.find_element(locator_type, locator_value)
    
    def login_facebook(self, username, password):
        self.input_text(self.INPUT_USERNAME, username)
        self.input_text(self.INPUT_PASSWORD, password)
        self.click_element(self.LOGIN_BUTTON) 
        time.sleep(5)
    
    def login_emso(self, username, password):
        self.driver.get(self.config.EMSO_URL)
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

            # Lấy các bài viết đã tồn tại từ group trong file
            existing_group_posts = data.get(username, [])

            # Lọc các bài viết mới, bỏ qua những bài đã tồn tại trong file
            existing_titles = {post["title"] for post in existing_group_posts}
            new_posts = [post for post in posts if post["title"] not in existing_titles]

            # Thêm bài viết mới vào danh sách cũ
            if username not in data:
                data[username] = []

            data[username].extend(new_posts)

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

            # Đảm bảo đường dẫn tuyệt đối tới thư mục 'media' và ảnh
            media_dir = os.path.join(os.getcwd(), 'media')  # Lấy đường dẫn tuyệt đối thư mục 'media'
            image_path = os.path.join(media_dir, image_name)  # Đảm bảo đường dẫn chính xác

            # In ra đường dẫn ảnh để kiểm tra
            print(f"Đường dẫn ảnh: {image_path}")

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
    def create_post(self, title, image_names):
        try:
            # Mở form tạo bài đăng
            WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, self.OPEN_FORM)))  # Ensure post loads
            self.click_element(self.OPEN_FORM)

            # Nhập tiêu đề bài đăng
            self.input_text(self.INPUT_POST, title)

            # Tải lên các ảnh (nếu có)
            if image_names:
                for image_name in image_names:
                    self.upload_image(self.INPUT_MEDIA, image_name)  # Giả sử upload_image hỗ trợ tải ảnh

            # Nhấn nút đăng bài
            self.click_element(self.CREATE_POST_BUTTON)
            time.sleep(5)  # Đợi một chút để quá trình đăng bài hoàn tất

        except Exception as e:
            print(f"Error creating post: {e}")
    
    def clear_media_folder():
        try:
            # Lấy đường dẫn thư mục 'media' trong cùng thư mục với chương trình
            current_dir = os.path.dirname(os.path.abspath(__file__))
            media_folder_path = os.path.join(current_dir, "media")
            
            # Kiểm tra nếu thư mục tồn tại
            if not os.path.exists(media_folder_path):
                print(f"Thư mục {media_folder_path} không tồn tại.")
                return

            # Xóa tất cả tệp trong thư mục
            for file_name in os.listdir(media_folder_path):
                file_path = os.path.join(media_folder_path, file_name)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            print(f"Đã xóa tất cả các tệp trong thư mục: {media_folder_path}")
        except Exception as e:
            print(f"Lỗi khi xóa thư mục media: {e}")

    # ====================================================================================================
    def scroll_to_element_and_crawl(self, username, password, nums_post, crawl_page, post_page, index_start=1):
        self.driver.get(crawl_page)
        post_data = []  # Danh sách để lưu dữ liệu của các bài post hợp lệ
        current_post_index = index_start  # Bắt đầu từ index_start

        # Đọc dữ liệu cũ nếu có từ tệp JSON
        output_file = "post.json"
        existing_data = {}
        if os.path.exists(output_file):
            try:
                with open(output_file, "r", encoding="utf-8") as json_file:
                    existing_data = json.load(json_file)
            except Exception as json_err:
                print(f"Lỗi khi đọc dữ liệu từ tệp JSON cũ: {json_err}")

        while len(post_data) < nums_post:  # Tiếp tục đến khi đủ nums_post hợp lệ
            try:
                # Tạo XPath động cho phần tử chính (post)
                post_xpath = self.POST.replace("{index}", str(current_post_index))
                
                # Đợi cho đến khi phần tử được tải xong
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, post_xpath)))
                
                # Tìm phần tử chính bằng XPath
                post_element = self.driver.find_element(By.XPATH, post_xpath)
                
                # Cuộn đến vị trí của phần tử chính
                self.driver.execute_script("arguments[0].scrollIntoView();", post_element)
                
                # Chờ để đảm bảo phần tử đã tải đầy đủ
                time.sleep(2)
                
                # Tìm các phần tử con trong element post tại vị trí index (title có thể là message đầu tiên)
                message_elements = post_element.find_elements(By.XPATH, ".//div[contains(@data-ad-comet-preview, 'message')]")
                
                # Kiểm tra nếu bài đăng có message (được coi là title)
                if not message_elements or not message_elements[0].text.strip():
                    print(f"Post {current_post_index} không có title hợp lệ, bỏ qua.")
                    current_post_index += 1
                    continue  # Bỏ qua bài đăng này và tiếp tục với bài đăng tiếp theo

                # Lấy text từ tất cả các phần tử message
                messages = [message.text for message in message_elements]

                # Kiểm tra nếu messages đã tồn tại trong dữ liệu cũ
                if any(post.get("messages") == messages for post in existing_data.get(crawl_page, [])):
                    print(f"Post {current_post_index} với messages đã tồn tại, bỏ qua.")
                    current_post_index += 1
                    continue  # Bỏ qua bài đăng này nếu messages đã tồn tại

                # Tìm các phần tử ảnh trong post
                image_elements = post_element.find_elements(By.XPATH, ".//img")
                image_urls = []

                for img in image_elements:
                    # Kiểm tra kích thước ảnh bằng naturalWidth
                    img_width = self.driver.execute_script("return arguments[0].naturalWidth;", img)
                    if img_width >= 100:
                        img_url = img.get_attribute("src")
                        if img_url:
                            image_urls.append(img_url)

                # Kiểm tra nếu không có ảnh hợp lệ
                if len(image_urls) == 0:
                    print(f"Post {current_post_index} không có ảnh hợp lệ (> 100px), bỏ qua.")
                    current_post_index += 1
                    continue  # Bỏ qua bài đăng này và tiếp tục với bài đăng tiếp theo

                # Tải xuống và lưu các ảnh vào thư mục "media"
                media_dir = "media"
                os.makedirs(media_dir, exist_ok=True)
                image_paths = []
                
                for i, img_url in enumerate(image_urls):
                    try:
                        response = requests.get(img_url, stream=True)
                        if response.status_code == 200:
                            # Lưu chỉ tên ảnh mà không phải đường dẫn đầy đủ
                            image_name = f"page_{current_post_index}_img_{i}.jpg"
                            image_path = os.path.join(media_dir, image_name)
                            with open(image_path, "wb") as img_file:
                                img_file.write(response.content)
                            image_paths.append(image_name)  # Lưu tên ảnh thay vì đường dẫn đầy đủ
                        else:
                            break  # Ngừng tải ảnh nếu có lỗi
                    except Exception:
                        print(f"Lỗi khi tải ảnh")
                        break  # Ngừng tải ảnh nếu có lỗi
                
                # Kiểm tra nếu không có ảnh hợp lệ (trong trường hợp image_paths vẫn rỗng)
                if len(image_paths) == 0:
                    print(f"Post {current_post_index} không có ảnh hợp lệ, bỏ qua.")
                    current_post_index += 1
                    continue  # Bỏ qua bài đăng này và tiếp tục với bài đăng tiếp theo
                
                # Lưu dữ liệu bài viết hợp lệ vào danh sách
                post_data.append({
                    "post_index": current_post_index,
                    "messages": messages,
                    "images": image_paths  # Lưu chỉ tên ảnh
                })
                
                print(f"Đã xử lý post {current_post_index}. Text: {messages}, Ảnh hợp lệ: {len(image_paths)}")

            except Exception as e:
                print(f"Lỗi khi xử lý phần tử tại index {current_post_index}: {e}")
            
            # Tăng index để tiếp tục cuộn và kiểm tra bài đăng tiếp theo
            current_post_index += 1

            # Kiểm tra nếu đã đủ số lượng bài hợp lệ
            if len(post_data) >= nums_post:
                print(f"Đã thu thập đủ {nums_post} bài đăng hợp lệ.")
                break  # Dừng quá trình crawl khi đã đủ số lượng bài hợp lệ

        # Sau khi crawl xong tất cả các bài, đăng bài lần lượt
        if post_data:
            try:
                # Đăng nhập một lần trước khi bắt đầu đăng bài
                self.login_emso(username, password)
                self.driver.get(post_page)
                
                # Đảm bảo trang đã được tải xong
                WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, self.OPEN_FORM)))  # Thay INPUT_POST bằng phần tử quan trọng trong form đăng bài
                
                # Vòng lặp đăng bài
                for post in post_data:
                    try:
                        # Đăng bài với tiêu đề và hình ảnh
                        self.create_post(post["messages"][0], post["images"])
                        print(f"Đã đăng bài thành công cho post {post['post_index']}")
                        self.driver.refresh()  # Làm mới trang để chuẩn bị đăng bài tiếp theo
                    except Exception as post_err:
                        # Nếu có lỗi khi đăng bài, in ra lỗi và tiếp tục với bài tiếp theo
                        print(f"Lỗi khi đăng bài {post['post_index']}: {post_err}")
                
            except Exception as login_err:
                # Nếu có lỗi trong quá trình đăng nhập, in ra và tiếp tục
                print(f"Lỗi khi đăng nhập hoặc truy cập trang đăng bài: {login_err}")
            
            finally:
                # Đăng xuất sau khi đăng xong tất cả các bài
                self.logout()
                print("Đã đăng xuất khỏi tài khoản.")

            # Lưu dữ liệu vào tệp JSON khi đã xử lý xong
            if crawl_page in existing_data:
                existing_data[crawl_page].extend(post_data)
            else:
                existing_data[crawl_page] = post_data

            try:
                with open(output_file, "w", encoding="utf-8") as json_file:
                    json.dump(existing_data, json_file, ensure_ascii=False, indent=4)
                print(f"Dữ liệu đã được lưu vào {output_file}")
            except Exception as json_err:
                print(f"Lỗi khi lưu dữ liệu vào tệp JSON: {json_err}")