import os
import re
import json
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


# Chemin vers le driver de Chrome que vous avez installé
DRIVER_PATH = "/opt/homebrew/bin/chromedriver"
debug_mode = os.getenv("DEBUG", "False").lower() == "true"
load_dotenv()
WARNING_COLOR = os.getenv("WARNING_COLOR").encode().decode('unicode_escape')
OK_COLOR = os.getenv("OK_COLOR").encode().decode('unicode_escape')
ERROR_COLOR = os.getenv("ERROR_COLOR").encode().decode('unicode_escape')
RESET_COLOR = os.getenv("RESET_COLOR").encode().decode('unicode_escape')


def get_content_from_url(URL):

    service = ChromeService(executable_path=DRIVER_PATH)

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

def extract_data(content):
    dealer_index = 1
    soup = BeautifulSoup(content, 'html.parser')
    cars_data = []
    counter = 1
    # Trouver l'élément 'link' avec l'attribut 'rel' défini sur 'canonical'
    canonical_link = soup.find('link', rel='canonical')
    # Si l'élément a été trouvé, extrayez la valeur de l'attribut 'href'
    canonical_url = canonical_link['href'] if canonical_link else None
    # Trouver tous les scripts sur la page
    scripts = soup.find_all('script')
    for script in scripts:
        # Vérifiez si le script contient les données structurées que nous recherchons
        if script.string and '"@context": "https://schema.org"' in script.string:
            # Charger les données structurées depuis le script en utilisant `json.loads`
            data = json.loads(script.string)
            # Parcourir les données structurées pour extraire les informations des véhicules
            for item in data.get('itemListElement', []):
                vehicle = item.get('item', {})
                # Extraire les détails du véhicule souhaités (nom, transmission, kilométrage, prix, etc.)
                car = {
                    "URL": vehicle.get('url', canonical_url),
                    "Name": vehicle.get('name'),
                    "Transmission": vehicle.get('vehicleTransmission'),
                    "Mileage": vehicle.get('mileageFromOdometer', {}).get('value'),
                    "Price": vehicle.get('offers', {}).get('price'),
                    "Dealer Name": vehicle.get('offers', {}).get('seller', {}).get('name'),
                    "Dealer Address": vehicle.get('offers', {}).get('seller', {}).get('address'),
                    "First Registration Date": vehicle.get('dateVehicleFirstRegistered'),
                    "Images": vehicle.get('image'),
                    "Engine Power": vehicle.get('vehicleEngine', {}).get('enginePower', {}).get('value'),
                    "Fuel Type": vehicle.get('fuelType'),
                    # "Vehicle Configuration": vehicle.get('vehicleConfiguration')
                }
                cars_data.append(car)
                # Ajouter un nom de concessionnaire par défaut si aucun nom n'est disponible
                dealer_name = car.get('Dealer Name')
                if not dealer_name:
                        dealer_name = f"NoName{dealer_index}"
                        dealer_index += 1
                car['Dealer Name'] = dealer_name
                name = car['Name'][:16]
                if debug_mode:
                    print(f"Vehicule {name:<16} n° {counter} extracted")
                counter += 1
    return cars_data

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

def main(urls_to_scrape):
    print(WARNING_COLOR + "Lancement du scrap..." + RESET_COLOR)
    all_new_vehicules = []
    # Pour chaque URL à scraper
    for url in urls_to_scrape:
        print(WARNING_COLOR + "Scraping "  + RESET_COLOR + f"{url}...")
        # time.sleep(0.5)
        if not url:
            continue
        # Récupérez le contenu de la page
        content = get_content_from_url(url)
        # Si vous avez réussi à obtenir du contenu, extrayez les données
        if content:
            extracted_data = extract_data(content)
            new_vehicules = is_data_new_main(extracted_data)
            all_new_vehicules.extend(new_vehicules)
            save_to_json(extracted_data)
    # Si de nouveaux véhicules ont été trouvés, envoyez un e-mail
    if all_new_vehicules:
        print("New vehicule found")
        with open('new_vehicules_list.txt', 'w') as file:
            email_content = "Voici les nouveaux véhicules trouvés:\n\n"
            for v in all_new_vehicules:
                vehicle_name = v['Name'][:16]
                dealer_name = v['Dealer Name'][:27]
                price = f"{v['Price']}CHF"
                mileage = f"{v['Mileage']}km"
                file.write(f"{vehicle_name} | {dealer_name.ljust(30)} | Prix: {price.rjust(10)} | Kilométrage: {mileage.rjust(8)}\n")
        
        smtp_transfer.run_smtp_transfer("New vehicule found", email_content, "garage.titane@gmail.com", "new_vehicules_list.txt")
    else:
        print("No new vehicule found")
            
    # Lire le fichier JSON nommé par la date du jour
    # today = date.today()
    # file_name = f"{today}_data1.json"
    # with open(file_name, 'r') as file:
    #     cars_data = json.load(file)
    # download_image(url, cars_data, today)
    # delete_last_month_images()
    interpret_result.run_interpret()
    print(OK_COLOR + "Scrap done!" + RESET_COLOR)

def run_scraping(urls_to_scrape):
    main(urls_to_scrape)
