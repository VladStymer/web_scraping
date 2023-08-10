import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService

load_dotenv()
debug_mode = os.getenv("DEBUG", "False").lower() == "true"
WARNING_COLOR = os.getenv("WARNING_COLOR").encode().decode('unicode_escape')
OK_COLOR = os.getenv("OK_COLOR").encode().decode('unicode_escape')
ERROR_COLOR = os.getenv("ERROR_COLOR").encode().decode('unicode_escape')
RESET_COLOR = os.getenv("RESET_COLOR").encode().decode('unicode_escape')


def identify_url_source(url):
    if "anibis" in url:
        return "anibis"
    elif "scout24" in url:
        return "scout24"
    else:
        return "Can't identify URL source"
    
def identify_vhc_type(url):
    if "moto" in url:
        return "bike"
    elif "auto" or "automobiles" in url:
        return "car"
    else:
        return "Can't identify vehicle type"
    
def set_driver():
    DRIVER_PATH = os.getenv("DRIVER_PATH")

    service = ChromeService(executable_path=DRIVER_PATH)

    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")
    chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--disable-gpu")
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    chrome_options.add_argument(f"user-agent={user_agent}")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver