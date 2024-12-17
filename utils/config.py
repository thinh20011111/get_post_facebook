from webdriver_manager.chrome import ChromeDriverManager

class Config:
    BASE_URL = "https://www.google.com"  # URL trang bạn muốn truy cập
    CHROME_DRIVER_PATH = ChromeDriverManager().install()  # Đường dẫn đến tệp chromedriver
    FACEBOOK_URL = "https://www.facebook.com/"
    EMSO_URL = "https://staging-fe.emso.vn/"
