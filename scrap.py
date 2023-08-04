import os
import re
import time
import json
import smtp_transfer
import interpret_result
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
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
MODE = int(os.getenv("MODE"))
debug_mode = os.getenv("DEBUG", "False").lower() == "true"
WARNING_COLOR = os.getenv("WARNING_COLOR").encode().decode('unicode_escape')
OK_COLOR = os.getenv("OK_COLOR").encode().decode('unicode_escape')
ERROR_COLOR = os.getenv("ERROR_COLOR").encode().decode('unicode_escape')
RESET_COLOR = os.getenv("RESET_COLOR").encode().decode('unicode_escape')

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

def get_all_direct_urls_of_vehicles(driver):
    try:
        # value = '/html/body/div[1]/div/div[5]/div/div/div[1]/div[2]/div/div[7]/div[1]/article/a'
        value = '//article/a'
        elements = driver.find_elements(by=webdriver.common.by.By.XPATH, value=value)
    except NoSuchElementException:
        elements = None
    # print(f"elements == {elements}\n end of elements\n")
    urls = [elem.get_attribute('href') for elem in elements]
    return urls


def get_content_from_url(URL):
    driver = set_driver()
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


def extract_json_from_script(script_content):
    start_marker = "{\"name\":"
    end_marker = ",\"geoLocation\":"
    
    start_index = script_content.find(start_marker)
    if start_index == -1:
        raise ValueError("Start marker not found.")
        
    end_index = script_content.find(end_marker, start_index)
    if end_index == -1:
        raise ValueError("End marker not found.")  


    match = re.search(r'"price":(\d+)', script_content)
    if match:
        price_value = match.group(1)
    else:
        price_value = '0'

    price_entry = {
        "name": "Prix",
        "value": price_value
    }

    json_str = script_content[start_index:end_index]
    data = '{"details":[ ' + json_str + '}}'
    print(f"data == {data}\n end of data\n")

    try:
        parsed_data = json.loads(data)
        # parsed_data["details"].insert(0, price_entry)
        formatted_json = json.dumps(parsed_data, indent=4)
        print(f"formatted_json == {formatted_json}\n end of formatted_json\n")
        return formatted_json
    except json.JSONDecodeError:
        print("The extracted sequence is not a valid JSON.")
        return None

def format_anibis_to_scout24(data, url_of_vhc):
    details = data["details"]

    # Extraire chaque détail
    try:
        Name = next(item['value'].strip() for item in details if item['name'] == "Marque")
    except:
        Name = None
    try:
        Type = next(item['value'].strip() for item in details if item['name'] == "Modèle")
    except:
        Type = None
    try:
        Color = next(item['value'].strip() for item in details if item['name'] == "Couleur extérieure")
    except:
        Color = None
    try:
        Transmission = next(item['value'].strip() for item in details if item['name'] == "Transmission")
    except:
        Transmission = None
    try:
        Wheel_Drive = next(item['value'].strip() for item in details if item['name'] == "Roues motrices")
    except:
        Wheel_Drive = None
    try:
        Mileage = next(item['value'].strip() for item in details if item['name'] == "Kilomètres")
    except:
        Mileage = None
    try:
        First_Registration_Date = next(item['value'].strip() for item in details if item['name'] == "Année")
    except:
        First_Registration_Date = None
    try:
        cm3 = next(item['value'].strip().split()[0] for item in details if item['name'] == "Cylindrée (Cm3)")
    except:
        cm3 = None
    try:
        Fuel_Type = next(item['value'].strip() for item in details if item['name'] == "Carburant")
    except:
        Fuel_Type = None
    try:
        Dealer_Name = "Private Seller" 
    except:
        Dealer_Name = None
    try:
        Dealer_Address = data["location"]["zipCity"] + ", " + ["street"]
    except:
        Dealer_Address = None

        URL = url_of_vhc
        Price = "Unknown"
    
    car = {
        "URL": URL,
        "Name": Name,
        "Type": Type,
        "Color": Color,
        "Transmission": Transmission,
        "Wheel Drive": Wheel_Drive,
        "Mileage": Mileage,
        "Price": Price,
        "Dealer Name": Dealer_Name,
        "Dealer Address": Dealer_Address,
        "First Registration Date": First_Registration_Date,
        "Cm3": cm3,
        "Fuel Type": Fuel_Type
    }

    return car




def extract_data_anibis(url_page):
    # print(f"url_page == {url_page}")
    try:
        driver = set_driver()
    except:
        print(ERROR_COLOR + "Error while setting driver" + RESET_COLOR)
        return
    urls_list = []
    json_list = []

    driver.get(url_page)
    urls = get_all_direct_urls_of_vehicles(driver)
    urls_list.append(urls)

    # print(f"urls_list == {urls_list}")
    for url_list in urls_list:
        for url_of_vhc in url_list:
            # print(f"urls_list == {urls_list}")
            # print(f"url_of_vhc == {url_of_vhc}\n end of url_of_vhc\n")
            try:
                driver.get(url_of_vhc)
            except:
                print(ERROR_COLOR + "Error while getting url_of_vhc" + RESET_COLOR)
                return
            
            script_content = driver.find_element(By.XPATH, '/html/body/script[1]').get_attribute('innerHTML')

            data_string = extract_json_from_script(script_content)
            data = json.loads(data_string)
            formated = format_anibis_to_scout24(data, url_of_vhc)
            # print(f"data:\n {data}\nend of data\n")
        json_list.append(formated)
    driver.quit()
    return json_list

def extract_data_scout24(content):
    dealer_index = 1
    soup = BeautifulSoup(content, 'html.parser')
    vhc_data = []
    counter = 1
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
    # print(vhc_data)
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
        if source == "autoscout24":
            content = get_content_from_url(url)
        
        # Si vous avez réussi à obtenir du contenu, extrayez les données
        if content:
            if MODE == 0:
                if source == "autoscout24":
                    extracted_data = extract_data_scout24(content)
                elif source == "anibis":
                    extracted_data = extract_data_anibis(url)
                new_vehicules = is_data_new_main(extracted_data)
                all_new_vehicules.extend(new_vehicules)
            if MODE == 1:
                if source == "autoscout24":
                    extracted_data = extract_data_scout24(content)
                elif source == "anibis":
                    extracted_data = extract_data_anibis(url)
            # save_to_json(extracted_data)
    if MODE == 0:
        if all_new_vehicules:
            print("New vehicule found")
            report_new_vehicles_via_email(all_new_vehicules)
        else:
            print("No new vehicule found")
    # print(f"all_new_vehicules == {all_new_vehicules}\nend of all_new_vehicules\n")
    return extracted_data         

def main(urls_to_scrape):
    print(WARNING_COLOR + "Lancement du scrap..." + RESET_COLOR)

    extracted_data = extract_and_save_vehicle_data(urls_to_scrape)
    print(f"extracted_data\n{extracted_data}\nend of extracted_data\n")
    # interpret_result.run_interpret(extracted_data)
    print(OK_COLOR + "Scrap done!" + RESET_COLOR)

def run_scraping(urls_to_scrape):
    main(urls_to_scrape)
