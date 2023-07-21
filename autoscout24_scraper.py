import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service as ChromeService
from datetime import datetime



# URL du site que vous souhaitez scraper
URL = "https://www.autoscout24.ch/fr/voitures/renault--clio?hpfrom=170&hpto=185&make=66&model=460&vehtyp=10"
# Chemin vers le driver de Chrome que vous avez installé
DRIVER_PATH = "/opt/homebrew/bin/chromedriver" 

def get_content_from_url():
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
                    "Vehicle Configuration": vehicle.get('vehicleConfiguration')
                }
                cars_data.append(car)
                
    return cars_data

def save_to_json(data):
    # Obtenez la date actuelle sous forme de chaîne : "YYYY-MM-DD"
    today_str = datetime.today().strftime('%Y-%m-%d')
    filename = f"data_{today_str}.json"

    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def main():
    # Récupérez le contenu de la page
    content = get_content_from_url()
    # Si vous avez réussi à obtenir du contenu, extrayez les données
    if content:
        extracted_data = extract_data(content)
        print(extracted_data)  # Afficher les données extraites
        save_to_json(extracted_data)

if __name__ == "__main__":
    main()
