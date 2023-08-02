import os
import sys
import time
import scrap
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium import webdriver
from dotenv import load_dotenv

load_dotenv()
debug_mode = os.getenv("DEBUG", "False").lower() == "true"
WARNING_COLOR = os.getenv("WARNING_COLOR").encode().decode('unicode_escape')
OK_COLOR = os.getenv("OK_COLOR").encode().decode('unicode_escape')
ERROR_COLOR = os.getenv("ERROR_COLOR").encode().decode('unicode_escape')
RESET_COLOR = os.getenv("RESET_COLOR").encode().decode('unicode_escape')

URLS = {
    "URL_clio":     os.getenv("URL_CLIO"),
    # "URL_tuonoV4":  os.getenv("URL_TUONO_V4"),
    # "URL_195CV":    os.getenv("URL_195CV"),
    "URL_anibis_bike": os.getenv("URL_anibis_bike"),
}

def generate_url(base_url, source, page_number=1):
    if source == "anibis":
        page="&pi="
    elif source == "autoscout24":
        page="&page="
    else:
        sys.exit(f"generate_url() -> Can't identify URL source: {source}")
    if debug_mode:
        print(f"generate_url: base_url={base_url}, page_number={page_number}")
    if page_number == 1:
        print("page_number == 1")
        return base_url
    else:
        print(f"page_number == {page_number}")
        return f"{base_url}{page}{page_number}"

def page_exists(driver, url, source):
    driver.get(url)
    if source == "anibis":
        if "4qsc3d" in driver.page_source:
            return True
        else:
            return False
    elif source == "autoscout24":
        if "Aucun résultat" in driver.page_source:
            return False
        else:
            return True
    else:
        print(ERROR_COLOR + "page_exists() -> Source inconnue: " + source + RESET_COLOR)
        sys.exit(1)

def identify_url_source(url):
    if "anibis" in url:
        return "anibis"
    elif "autoscout24" in url:
        return "autoscout24"
    else:
        return "Can't identify URL source"

def collect_urls_to_scrape(driver, URLS):
    urls_to_scrape = []
    for key, base_url in URLS.items():
        source = identify_url_source(base_url)
        if not URLS:
            print(ERROR_COLOR + "No URLS found in .env file" + RESET_COLOR)
            return
        print(WARNING_COLOR + f"Scraping {key}..." + RESET_COLOR)
        page_number = 1
        while True:
            url = generate_url(base_url, source, page_number)
            if page_exists(driver, url, source):
                urls_to_scrape.append(url)
                page_number += 1
            else:
                break
    return urls_to_scrape

def set_driver():
    DRIVER_PATH = os.getenv("DRIVER_PATH")

    service = ChromeService(executable_path=DRIVER_PATH)

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
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

def main():
    print(WARNING_COLOR + "Lancement du main..." + RESET_COLOR)

    driver = set_driver()
    urls_to_scrape = collect_urls_to_scrape(driver, URLS)
    scrap.run_scraping(urls_to_scrape)
    driver.quit()
    print(OK_COLOR + "Main done!" + RESET_COLOR)

if __name__ == "__main__":
    main()
