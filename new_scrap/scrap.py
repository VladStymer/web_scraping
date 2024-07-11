from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def fetch_vehicle_urls(base_url):
    # Configuration du pilote Chrome avec des options pour l'exécution sans tête
    options = Options()
    options.headless = True
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    all_urls = []
    max_pages = 6000  # Nombre maximum de pages à scraper
    for page in range(1, max_pages + 1):
        print("In the while loop")
        first_url = f"{base_url}"
        current_url = f"{base_url}&pagination%5Bpage%5D={page}"
        if page == 1:
            current_url = first_url
        driver.get(current_url)
        
        # Utiliser Selenium pour extraire les URLs
        elements = driver.find_elements_by_xpath('//*[@id="__next"]/div/div[2]/div[1]/main/ul/li/article/a')
        if not elements:
            print(f"No URLs found on page {page}")
            break
        
        for element in elements:
            url = element.get_attribute('href')
            print(f"Found URL: {url}")
            all_urls.append(url)

        time.sleep(1)  # Delay pour simuler le comportement humain

    driver.quit()
    return all_urls

def main():
    print("Starting the scrap.py script...")
    base_url = 'https://www.autoscout24.ch/fr/s?hadNoAccidentOnly=true&fuelTypes%5B0%5D=petrol&fuelTypes%5B1%5D=hev-petrol&fuelTypes%5B2%5D=mhev-petrol&fuelTypes%5B3%5D=phev-petrol&fuelTypes%5B4%5D=electric&horsePowerFrom=100&cubicCapacityFrom=1000'
    # url page 1: https://www.autoscout24.ch/fr/s?hadNoAccidentOnly=true&fuelTypes%5B0%5D=petrol&fuelTypes%5B1%5D=hev-petrol&fuelTypes%5B2%5D=mhev-petrol&fuelTypes%5B3%5D=phev-petrol&fuelTypes%5B4%5D=electric&horsePowerFrom=100&cubicCapacityFrom=1000
    # url page 2: https://www.autoscout24.ch/fr/s?hadNoAccidentOnly=true&fuelTypes%5B0%5D=petrol&fuelTypes%5B1%5D=hev-petrol&fuelTypes%5B2%5D=mhev-petrol&fuelTypes%5B3%5D=phev-petrol&fuelTypes%5B4%5D=electric&horsePowerFrom=100&cubicCapacityFrom=1000&pagination%5Bpage%5D=1
    # url page 3: https://www.autoscout24.ch/fr/s?hadNoAccidentOnly=true&fuelTypes%5B0%5D=petrol&fuelTypes%5B1%5D=hev-petrol&fuelTypes%5B2%5D=mhev-petrol&fuelTypes%5B3%5D=phev-petrol&fuelTypes%5B4%5D=electric&horsePowerFrom=100&cubicCapacityFrom=1000&pagination%5Bpage%5D=2
    
    vehicle_urls = fetch_vehicle_urls(base_url)
    for url in vehicle_urls:
        print(url)

if __name__ == "__main__":
    main()
