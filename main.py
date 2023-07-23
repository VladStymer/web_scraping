from selenium.webdriver.chrome.service import Service as ChromeService
from selenium import webdriver
import scrap
import time

URLS = {
    "URL_clio":     "https://www.autoscout24.ch/fr/voitures/renault--clio?hpfrom=170&hpto=185&make=66&model=460&vehtyp=10",
    "URL_tuonoV4":  "https://www.motoscout24.ch/fr/motos/aprilia--tuono?kmto=10000&ccmfrom=1000&make=93&model=1259&typename=fact"
}

DRIVER_PATH = "/opt/homebrew/bin/chromedriver" 

def generate_url(base_url, page_number=1):
    if page_number == 1:
        return base_url
    else:
        return f"{base_url}&page={page_number}"

def page_exists(driver, url):
    driver.get(url)
    if "Aucun résultat" in driver.page_source:
        return False
    return True

def main():
    print("Lancement du main...")
    urls_to_scrape = []
    service = ChromeService(executable_path=DRIVER_PATH)
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options) 
    for key, base_url in URLS.items():
        page_number = 1
        while True:
            time.sleep(0.5)
            url = generate_url(base_url, page_number)
            if page_exists(driver, url):
                urls_to_scrape.append(url)
                page_number += 1
            else:
                break
    driver.quit()
    scrap.run_scraping(urls_to_scrape)

if __name__ == "__main__":
    main()
