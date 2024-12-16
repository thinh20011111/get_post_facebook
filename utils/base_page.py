from selenium.webdriver.common.by import By

class BasePage:
    def __init__(self, driver):
        self.driver = driver

    def find_element(self, locator_type, locator_value):
        return self.driver.find_element(locator_type, locator_value)

    def print_title(self):
        print(f"Title hiện tại: {self.driver.title}")
