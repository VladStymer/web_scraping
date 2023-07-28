import os
import time
import scrap
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium import webdriver
from dotenv import load_dotenv

debug_mode = os.getenv("DEBUG", "False").lower() == "true"
load_dotenv()
WARNING_COLOR = os.getenv("WARNING_COLOR").encode().decode('unicode_escape')
OK_COLOR = os.getenv("OK_COLOR").encode().decode('unicode_escape')
ERROR_COLOR = os.getenv("ERROR_COLOR").encode().decode('unicode_escape')
RESET_COLOR = os.getenv("RESET_COLOR").encode().decode('unicode_escape')

URLS = {
    "URL_clio":     os.getenv("URL_CLIO"),
    "URL_tuonoV4":  os.getenv("URL_TUONO_V4")
}

def generate_url(base_url, page_number=1):
    if debug_mode:
        print(f"generate_url: base_url={base_url}, page_number={page_number}")
    if page_number == 1:
        return base_url
    else:
        return f"{base_url}&page={page_number}"

def page_exists(driver, url):
    if debug_mode:
        print(f"page_exists: url={url}")
    driver.get(url)
    # time.sleep(0.5)
    if "Aucun résultat" in driver.page_source:
        return False
    return True

def main():
    print(WARNING_COLOR + "Lancement du main..." + RESET_COLOR)    

    DRIVER_PATH = os.getenv("DRIVER_PATH")
    urls_to_scrape = []
    service = ChromeService(executable_path=DRIVER_PATH)
    # options = webdriver.ChromeOptions()
    # driver = webdriver.Chrome(service=service, options=options)

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--disable-gpu")
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    chrome_options.add_argument(f"user-agent={user_agent}")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    for key, base_url in URLS.items():
        print(WARNING_COLOR + f"Scraping {key}..." + RESET_COLOR)
        page_number = 1
        while True:
            # time.sleep(0.5)
            url = generate_url(base_url, page_number)
            if page_exists(driver, url):
                urls_to_scrape.append(url)
                page_number += 1
            else:
                break
    driver.quit()
    scrap.run_scraping(urls_to_scrape)
    print(OK_COLOR + "Main done!" + RESET_COLOR)

if __name__ == "__main__":
    main()
