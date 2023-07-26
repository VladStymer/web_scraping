import os
import re
import json
import smtp_transfer
import interpret_result
from datetime import date
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService


# Chemin vers le driver de Chrome que vous avez installé
DRIVER_PATH = "/opt/homebrew/bin/chromedriver" 

def get_content_from_url(URL):

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

    driver.get(URL)
    try:
        # Utilisez WebDriverWait pour attendre qu'un élément spécifique soit chargé.
        element_present = EC.presence_of_element_located((By.TAG_NAME, 'script'))
        WebDriverWait(driver, 45).until(element_present)  # Attendre jusqu'à 10 secondes
    except TimeoutException:
        print("Timed out waiting for page to load")
    
    # Récupérez le code source de la page
    page_source = driver.page_source
    driver.quit()
    # if (os.getenv("DEBUG")):
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
                # Ajouter la voiture à la liste des voitures si elle a moins de 200'000 km
                # mileage = car.get('Mileage', 0)
                # if isinstance(mileage, str):
                #     mileage = mileage.replace(",", "").replace("'", "")  # supprimer les séparateurs de milliers
                #     mileage = int(mileage)
                # if mileage < 200000:
                cars_data.append(car)

                # Ajouter un nom de concessionnaire par défaut si aucun nom n'est disponible
                dealer_name = car.get('Dealer Name')
                if not dealer_name:
                        dealer_name = f"NoName{dealer_index}"
                        dealer_index += 1
                car['Dealer Name'] = dealer_name
                name = car['Name'][:16]
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
    # Obtenez la date actuelle sous forme de chaîne : "YYYY-MM-DD"
    today_str = datetime.today().strftime('%Y-%m-%d')
    counter = 1
    filename = f"{today_str}_data{counter}.json"
    
    # Tant que le fichier existe, augmentez le compteur et vérifiez le fichier suivant.
    while os.path.exists(filename):
        # Si le fichier existe, essayez de le charger
        with open(filename, 'r') as file:
            existing_data = json.load(file)
        if get_name_from_data(existing_data) == get_name_from_data(data):
            # Liste pour collecter les annonces uniques de 'data' qui ne sont pas déjà dans 'existing_data'
            unique_data = []

            # Pour chaque annonce dans 'data', vérifiez si son URL est déjà dans 'existing_data'
            for new_entry in data:
                print(f"\nexisting_data={existing_data}\nnew_entry={new_entry}\n")
                if not any(existing_entry["URL"] == new_entry["URL"] for existing_entry in existing_data):
                    unique_data.append(new_entry)

            # Ajout des annonces uniques à 'existing_data'
            existing_data.extend(unique_data)
            # Écrivez les données dans le fichier
            with open(filename, 'w') as file:
                json.dump(existing_data, file, indent=4)
            return unique_data if 'unique_data' in locals() else data

        # Si le "Name" n'est pas le même, augmentez le compteur et vérifiez le fichier suivant.
        counter += 1
        filename = f"{today_str}_data{counter}.json"

        # Si on arrive ici, cela signifie qu'aucun fichier correspondant n'a été trouvé.
        # Créons donc un nouveau fichier.
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def main(urls_to_scrape):
    print("Lancement du scrap...")
    all_new_vehicules = []
    # Pour chaque URL à scraper
    for url in urls_to_scrape:
        print(f"Scraping {url}...")
        # time.sleep(0.5)
        if not url:
            continue
        # Récupérez le contenu de la page
        content = get_content_from_url(url)
        # Si vous avez réussi à obtenir du contenu, extrayez les données
        if content:
            extracted_data = extract_data(content)
            new_vehicules = save_to_json(extracted_data)
            if new_vehicules:
                all_new_vehicules.extend(new_vehicules)
    # Si de nouveaux véhicules ont été trouvés, envoyez un e-mail
    if all_new_vehicules:
        email_content = "Voici les nouveaux véhicules trouvés:\n\n"
        for v in all_new_vehicules:
            dealer_name = v['Dealer Name'][:27]
            price = f"{v['Price']}CHF"
            mileage = f"{v['Mileage']}km"
            email_content += f"{dealer_name.ljust(25)}  |  Prix: {price.rjust(12)}  |  Kilométrage: {mileage.rjust(10)}\n"
        
        smtp_transfer.run_smtp_transfer("New vehicule found", email_content, "garage.titane@gmail.com")
        print("New vehicule found, email sent")

    # Lire le fichier JSON nommé par la date du jour
    # today = date.today()
    # file_name = f"{today}_data1.json"
    # with open(file_name, 'r') as file:
    #     cars_data = json.load(file)
    # download_image(url, cars_data, today)
    # delete_last_month_images()
    interpret_result.run_interpret()
    print("Scrap done!")

def run_scraping(urls_to_scrape):
    main(urls_to_scrape)
