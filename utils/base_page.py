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
    