import os
import re
import time
import json
import requests
import smtp_transfer
import interpret_result
from datetime import date
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from is_data_new import is_data_new_main
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService

load_dotenv()
DRIVER_PATH = "/opt/homebrew/bin/chromedriver"
MODE = int(os.getenv("MODE"))
debug_mode = os.getenv("DEBUG", "False").lower() == "true"
WARNING_COLOR = os.getenv("WARNING_COLOR").encode().decode('unicode_escape')
OK_COLOR = os.getenv("OK_COLOR").encode().decode('unicode_escape')
ERROR_COLOR = os.getenv("ERROR_COLOR").encode().decode('unicode_escape')
RESET_COLOR = os.getenv("RESET_COLOR").encode().decode('unicode_escape')


def get_all_direct_urls_of_vehicles(driver):
    # Utiliser un sélecteur CSS pour matcher tous les éléments similaires
    card_selectors = driver.find_elements(By.CSS_SELECTOR, '[id^="card_"] > a')
    
    # Extraire les URLs de chaque élément
    urls = [card.get_attribute('href') for card in card_selectors]
    
    return urls


def get_content_from_url(URL, source):

    service = ChromeService(executable_path=DRIVER_PATH)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--remote-debugging-port=9222")
    # chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument("--disable-gpu")
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    chrome_options.add_argument(f"user-agent={user_agent}")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(URL)
    if source == "anibis":
        urls_list = get_all_direct_urls_of_vehicles(driver)
        # Initialisez un WebDriverWait avec un timeout de 10 secondes
        wait = WebDriverWait(driver, 1)
        for url in urls_list:
            print(f"url={url}")

            driver.get(url)
            try:
                # Récupérer le prix
                price_selector = "#root > div > div:nth-child(6) > div.sc-552kic-0.bLJmgp > div > div.sc-162rti3-0.dUWcZm > div:nth-child(1) > div.e1d99g-0.sc-1155gfs-0.iMiaIt.jOflgH > div.sc-16i19r8-0.knSuBJ"
                price_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, price_selector)))
                price = price_element.text
            except TimeoutException:
                price = "Non trouvé"

            try:
                # Récupérer les autres informations
                other_info_selector = "#root > div > div:nth-child(6) > div.sc-552kic-0.bLJmgp > div > div.sc-162rti3-0.dUWcZm > div:nth-child(3) > div.e1d99g-0.sc-1155gfs-0.iMiaIt.gXyhgM > div:nth-child(1) > div.e1d99g-0.sc-1155gfs-0.iMiaIt.iOSSyT.r2utrp-0.bwzgRT > div > ul"
                other_info_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, other_info_selector)))
                other_info = other_info_element.text
            except TimeoutException:
                other_info = "Non trouvé"

            try:
                # Récupérer les kilomètres
                km_selector =   "#root > div > div:nth-child(6) > div.sc-552kic-0.bLJmgp > div > div.sc-162rti3-0.dUWcZm > div:nth-child(3) > div.e1d99g-0.sc-1155gfs-0.iMiaIt.gXyhgM > div:nth-child(1) > div.e1d99g-0.sc-1155gfs-0.iMiaIt.iOSSyT.r2utrp-0.bwzgRT > div > ul"
                km_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, km_selector)))
                kilometers = km_element.text
            except TimeoutException:
                kilometers = "Non trouvé"

            print(f"Prix: {price}\n")
            print(f"Autres informations: {other_info}\n")
            print(f"Kilomètres: {kilometers}")

        driver.quit(url)

        # return all_data


    elif source == "autoscout24":
        driver.get(URL)
        try:
            # Utilisez WebDriverWait pour attendre qu'un élément spécifique soit chargé.
            element_present = EC.presence_of_element_located((By.TAG_NAME, 'script'))
            WebDriverWait(driver, 45).until(element_present)  # Attendre jusqu'à 10 secondes
        except TimeoutException:
            print(ERROR_COLOR + "Timed out waiting for page to load" + RESET_COLOR)
        
        # Récupérez le code source de la page
        page_source = driver.page_source
        driver.quit()
        # if debug_mode:
        #     print(f"get_content_from_url: page_source={page_source}")
        return page_source

def extract_data(content, source):
    dealer_index = 1
    soup = BeautifulSoup(content, 'html.parser')
    vhc_data = []
    counter = 1
    if source == "autoscout24":
        canonical_link = soup.find('link', rel='canonical')
        canonical_url = canonical_link['href'] if canonical_link else None
        scripts = soup.find_all('script')

        for script in scripts:
            if script.string and '"@context": "https://schema.org"' in script.string:
                data = json.loads(script.string)
                for item in data.get('itemListElement', []):
                    vehicle = item.get('item', {})
                    car = {
                        "URL": vehicle.get('url', canonical_url),
                        "Name": vehicle.get('name'),
                        "Transmission": vehicle.get('vehicleTransmission'),
                        "Mileage": vehicle.get('mileageFromOdometer', {}).get('value'),
                        "Price": vehicle.get('offers', {}).get('price'),
                        "Dealer Name": vehicle.get('offers', {}).get('seller', {}).get('name'),
                        "Dealer Address": vehicle.get('offers', {}).get('seller', {}).get('address'),
                        "First Registration Date": vehicle.get('dateVehicleFirstRegistered'),
                        # "Images": vehicle.get('image'),
                        "Engine Power": vehicle.get('vehicleEngine', {}).get('enginePower', {}).get('value'),
                        "Fuel Type": vehicle.get('fuelType'),
                        # "Vehicle Configuration": vehicle.get('vehicleConfiguration')
                    }
                    vhc_data.append(car)
                    dealer_name = car.get('Dealer Name')
                    if not dealer_name:
                            dealer_name = f"Private_seller_{dealer_index}"
                            dealer_index += 1
                    car['Dealer Name'] = dealer_name
                    name = car['Name'][:16]
                    if debug_mode:
                        print(f"Vehicule {name:<16} n° {counter} extracted")
                    counter += 1

    elif source == "anibis":
        for data in content:
            description = data.get("detail", {}).get("description", "")
            details = data.get("detail", {}).get("details", [])
            
            vhc_details = {}
            vhc_details["Description"] = description

            for detail in details:
                name = detail.get("name", "")
                value = detail.get("value", "")
                vhc_details[name] = value

            vhc_data.append(vhc_details)

    return vhc_data

def extract_name_from_url(url):
    if not url:
        return None
    match = re.search(r'(voitures|motos)/([^?]+)', url, re.IGNORECASE)
    if match:
        return match.group(2)
    return None

def get_name_from_data(data):
    first_url = get_first_url(data)
    return extract_name_from_url(first_url)


def get_first_url(data):
    if isinstance(data, list) and len(data) > 0:
        if isinstance(data[0], dict) and 'URL' in data[0]:
            return data[0]['URL']
    return None

def save_to_json(data):
    today_str = datetime.today().strftime('%Y-%m-%d')
    counter = 1
    filename = f"{today_str}_data{counter}.json"
    # Tant que le fichier existe, augmentez le compteur et vérifiez le fichier suivant.
    while os.path.exists(filename):
        with open(filename, 'r') as file:
            existing_data = json.load(file)

        if get_name_from_data(existing_data) == get_name_from_data(data):
            # Filtrer les éléments de `data` qui ne sont pas déjà dans `existing_data`
            new_data_to_add = [item for item in data if item not in existing_data]
            
            # Ajouter les nouvelles données filtrées à existing_data
            combined_data = existing_data + new_data_to_add
            try:
                with open(filename, 'w') as file:
                    json.dump(data, file, indent=4)
            except Exception as e:
                print(f"Error while writing to file: {e}")
            return
        # Si le "Name" n'est pas le même, augmentez le compteur et vérifiez le fichier suivant.
        counter += 1
        filename = f"{today_str}_data{counter}.json"
    # Si on arrive ici, cela signifie qu'aucun fichier correspondant n'a été trouvé.
    # Créons donc un nouveau fichier.
    try:
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error while writing to file: {e}")



def report_new_vehicles_via_email(all_new_vehicules):
    with open('new_vehicules_list.txt', 'a') as file:
        email_content = "Voici les nouveaux véhicules trouvés:\n\n"
        for v in all_new_vehicules:
            vehicle_name = v['Name'][:16]
            dealer_name = v['Dealer Name'][:27]
            price = f"{v['Price']}CHF"
            mileage = f"{v['Mileage']}km"
            file.write(f"{vehicle_name} | {dealer_name.ljust(30)} | Prix: {price.rjust(10)} | Kilométrage: {mileage.rjust(8)}\n\n")
    
    smtp_transfer.run_smtp_transfer("New vehicule found", email_content, "garage.titane@gmail.com", "new_vehicules_list.txt")

def identify_url_source(url):
    if "anibis" in url:
        return "anibis"
    elif "autoscout24" in url:
        return "autoscout24"
    else:
        return "Can't identify URL source"

def extract_and_save_vehicle_data(urls_to_scrape):
    all_new_vehicules = []
    # Pour chaque URL à scraper
    for url in urls_to_scrape:
        print(WARNING_COLOR + "Scraping "  + RESET_COLOR + f"{url}...")
        if not url:
            continue
        source = identify_url_source(url)
        content = get_content_from_url(url, source)
        
        # Si vous avez réussi à obtenir du contenu, extrayez les données
        if content:
            if MODE == 0:
                extracted_data = extract_data(content, source)
                new_vehicules = is_data_new_main(extracted_data)
                all_new_vehicules.extend(new_vehicules)
                save_to_json(extracted_data)   
            if MODE == 1:
                extracted_data = extract_data(content, source)
    if MODE == 0:
        if all_new_vehicules:
            print("New vehicule found")
            report_new_vehicles_via_email(all_new_vehicules)
        else:
            print("No new vehicule found")
    return extracted_data         

def main(urls_to_scrape):
    print(WARNING_COLOR + "Lancement du scrap..." + RESET_COLOR)

    extracted_data = extract_and_save_vehicle_data(urls_to_scrape)

    interpret_result.run_interpret(extracted_data)
    print(OK_COLOR + "Scrap done!" + RESET_COLOR)

def run_scraping(urls_to_scrape):
    main(urls_to_scrape)
