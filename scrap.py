import json
import shutil
import requests
import re
import json
import os
import time
import interpret_result
from datetime import date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service as ChromeService
from datetime import datetime


# Chemin vers le driver de Chrome que vous avez installé
DRIVER_PATH = "/opt/homebrew/bin/chromedriver" 

# def download_image(url, cars_data, today):
#     print("Téléchargement des images...")
#     # Créer un dossier pour stocker les images s'il n'existe pas déjà
#     base_dir = "downloaded_images"
#     if not os.path.exists(base_dir):
#         os.mkdir(base_dir)
    
#     # Pour chaque voiture, téléchargez toutes ses images
#     for car in cars_data:
#         # Remplacer les caractères indésirables en dehors de l'f-string
#         mileage_clean = car['Mileage'].replace(',', '').replace('\'', '')
#         # Création du nom de dossier pour chaque voiture
#         folder_name = f"{today}_{car['Dealer Name']}_{car['Price']}CHF_{mileage_clean}km"
#         folder_path = os.path.join(base_dir, folder_name)
        
#         # Créer le dossier s'il n'existe pas
#         if not os.path.exists(folder_path):
#             os.mkdir(folder_path)

#         # Télécharger les images dans le dossier spécifié
#         for index, image_url in enumerate(car["Images"]):
#             time.sleep(0.5)
#             image_name = f"{car['Name'].replace(' ', '_')}_{index}.jpg"
#             save_path = os.path.join(folder_path, image_name)
#             response = requests.get(url, stream=True, timeout=10)  # timeout après 10 secondes
#             response.raise_for_status()
#             with open(save_path, 'wb') as file:
#                 for chunk in response.iter_content(chunk_size=8192):
#                     file.write(chunk)
#             print(f"Téléchargé {image_name}")

def get_content_from_url(URL):
    service = ChromeService(executable_path=DRIVER_PATH)
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options) 
    driver.get(URL)
    try:
        element_present = EC.presence_of_element_located((By.TAG_NAME, 'script'))
        WebDriverWait(driver, 45).until(element_present)  # Attendre jusqu'à 10 secondes
    except TimeoutException:
        print("Timed out waiting for page to load")
    
    # Récupérez le code source de la page
    page_source = driver.page_source
    driver.quit()
    return page_source

def extract_data(content):
    dealer_index = 1
    soup = BeautifulSoup(content, 'html.parser')
    cars_data = []
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
                mileage = car.get('Mileage', 0)
                if isinstance(mileage, str):
                    mileage = mileage.replace(",", "").replace("'", "")  # supprimer les séparateurs de milliers
                    mileage = int(mileage)
                if mileage < 200000:
                    cars_data.append(car)

                # Ajouter un nom de concessionnaire par défaut si aucun nom n'est disponible
                dealer_name = car.get('Dealer Name')
                if not dealer_name:
                        dealer_name = f"NoName{dealer_index}"
                        dealer_index += 1
                car['Dealer Name'] = dealer_name
    return cars_data

def extract_name_from_url(url):
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
    filename = f"data_{today_str}.json"
    counter = 1 

    while os.path.exists(filename):
        # Si le fichier existe, essayez de le charger
        with open(filename, 'r') as file:
            existing_data = json.load(file)
        if get_name_from_data(existing_data) == get_name_from_data(data):
            # Si le "Name" est le même, ajoutez les nouvelles données à la fin et sauvegardez.
            existing_data.extend(data)
            with open(filename, 'w') as file:
                json.dump(existing_data, file, indent=4)
            return

        # Si le "Name" n'est pas le même, augmentez le compteur et vérifiez le fichier suivant.
        counter += 1
        filename = f"data{counter}_{today_str}.json"

    # Si on arrive ici, cela signifie qu'aucun fichier correspondant n'a été trouvé.
    # Créons donc un nouveau fichier.
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

# def delete_last_month_images():
#     today = datetime.today()
#     # Si nous sommes le 1er du mois
#     if today.day == 1:
#         last_month = today.month - 1 if today.month != 1 else 12
        
#         base_dir = "downloaded_images"
        
#         # Pour chaque dossier dans le répertoire de base
#         for folder_name in os.listdir(base_dir):
#             # Ici, nous supposons que votre nom de dossier suit le format "YYYY-MM-DD" quelque part dans le nom
#             # Par exemple, "Dealer_Name_40000CHF_12000km_2022-06-10"
#             try:
#                 date_part = folder_name.split('_')[-1]
#                 folder_date = datetime.strptime(date_part, "%Y-%m-%d")
#                 if folder_date.month == last_month:
#                     folder_path = os.path.join(base_dir, folder_name)
#                     shutil.rmtree(folder_path)
#                     print(f"Dossier {folder_name} supprimé.")
#             except:
#                 # Ici, nous ignorons les dossiers qui n'ont pas une date valide dans leur nom
#                 pass

def main(urls_to_scrape):
    print("Lancement du scrap...")
    for url in urls_to_scrape:
        # time.sleep(0.5)
        if not url:
            continue
        # Récupérez le contenu de la page
        content = get_content_from_url(url)
        # Si vous avez réussi à obtenir du contenu, extrayez les données
        if content:
            extracted_data = extract_data(content)
            save_to_json(extracted_data)
    # Lire le fichier JSON nommé par la date du jour
    today = date.today()
    file_name = f"data_{today}.json"
    with open(file_name, 'r') as file:
        cars_data = json.load(file)
    
    # Télécharger les images
    # download_image(url, cars_data, today)
    # Supprimer les images du mois dernier
    # delete_last_month_images()
    # Run interpret_result.py
    interpret_result.run_interpret()

def run_scraping(urls_to_scrape):
    main(urls_to_scrape)
