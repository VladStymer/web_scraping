import json
import time
import requests
import os
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

def download_image(url, save_path):
    response = requests.get(url, stream=True, timeout=10)  # timeout après 10 secondes
    response.raise_for_status()
    with open(save_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

def get_content_from_url(URL):
    # Configuration pour Chrome afin de le lancer en mode sans tête (headless) 
    # (c'est-à-dire sans ouvrir une fenêtre de navigateur)

    service = ChromeService(executable_path=DRIVER_PATH)
    options = webdriver.ChromeOptions()

    # options.headless = True
    # options.add_argument("--headless")
    
    # Démarrage du navigateur Chrome avec les options définies
    driver = webdriver.Chrome(service=service, options=options) 

        # Accédez à l'URL spécifiée
    driver.get(URL)
        
        # Utilisez WebDriverWait pour attendre qu'un élément spécifique soit chargé.
        # Dans cet exemple, je suppose qu'il y a un élément avec la balise 'script' sur la page.
        # Ici, nous attendons qu'un élément avec le nom de balise 'script' soit présent sur la page.
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

    # Variable pour suivre le numéro de "NoName" à attribuer
    dealer_index = 1

    # Utilisez BeautifulSoup pour analyser le contenu de la page
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

def save_to_json(data):
    # Obtenez la date actuelle sous forme de chaîne : "YYYY-MM-DD"
    today_str = datetime.today().strftime('%Y-%m-%d')
    filename = f"data_{today_str}.json"

    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def main():
    # Récupérez les URLs depuis os.environ
    urls_to_scrape = [os.environ.get(key) for key in os.environ if 'URL_' in key]
    
    for url in urls_to_scrape:
        if not url:  # pour éviter les valeurs None
            continue
        print(f"Scraping {url} ...")
        
    # Récupérez le contenu de la page
    content = get_content_from_url(url)
    # Si vous avez réussi à obtenir du contenu, extrayez les données
    if content:
        extracted_data = extract_data(content)
        save_to_json(extracted_data)
        print("Données extraites avec succès !")
    print("Téléchargement des images...")
    # Créer un dossier pour stocker les images s'il n'existe pas déjà
    base_dir = "downloaded_images"
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)
    
    print("Chargement des données...")
    # Lire le fichier JSON nommé par la date du jour
    today = date.today()
    file_name = f"data_{today}.json"
    with open(file_name, 'r') as file:
        cars_data = json.load(file)
    
    print("Téléchargement des images...")
    # Pour chaque voiture, téléchargez toutes ses images
    for car in cars_data:
        # Remplacer les caractères indésirables en dehors de l'f-string
        mileage_clean = car['Mileage'].replace(',', '').replace('\'', '')
        # Création du nom de dossier pour chaque voiture
        folder_name = f"{car['Dealer Name']}_{car['Price']}CHF_{mileage_clean}km"
        folder_path = os.path.join(base_dir, folder_name)
        
        # Créer le dossier s'il n'existe pas
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
        
        # Télécharger les images dans le dossier spécifié
        for index, image_url in enumerate(car["Images"]):
            image_name = f"{car['Name'].replace(' ', '_')}_{index}.jpg"
            save_path = os.path.join(folder_path, image_name)
            download_image(image_url, save_path)
            print(f"Téléchargé {image_name}")
    # Run interpret_result.py
    interpret_result.run_scraping()

def run_scraping():
    main()
