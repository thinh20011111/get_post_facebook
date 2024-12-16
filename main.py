from utils.base_page import BasePage
from selenium import webdriver
from utils.config import Config

def main():
    # Load cấu hình
    config = Config()
    driver = webdriver.Chrome(executable_path=config.CHROME_DRIVER_PATH)
    
    # Mở trang web
    driver.get(config.BASE_URL)
    print(f"Đang mở: {config.BASE_URL}")
    
    # Sử dụng BasePage để thực hiện hành động
    base_page = BasePage(driver)
    base_page.print_title()
    
    driver.quit()

if __name__ == "__main__":
    main()
