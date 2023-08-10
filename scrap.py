import os
import re
import time
import json
import utils 
import vhc_DB
import sort_vhc
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()
MODE = int(os.getenv("MODE"))
debug_mode = os.getenv("DEBUG", "False").lower() == "true"
WARNING_COLOR = os.getenv("WARNING_COLOR").encode().decode('unicode_escape')
OK_COLOR = os.getenv("OK_COLOR").encode().decode('unicode_escape')
ERROR_COLOR = os.getenv("ERROR_COLOR").encode().decode('unicode_escape')
RESET_COLOR = os.getenv("RESET_COLOR").encode().decode('unicode_escape')

def get_all_direct_urls_of_vehicles(driver, source):
    try:
        if source == "anibis":
            value = '//article/a'
        if source == "scout24":
            value = '//article/div[2]/div/a'
        elements = driver.find_elements(by=webdriver.common.by.By.XPATH, value=value)
    except NoSuchElementException:
        elements = None
    urls = [elem.get_attribute('href') for elem in elements]
    return urls


def get_content_from_url(driver, URL):
    time.sleep(1)
    driver.get(URL)

    try:
        # Utilisez WebDriverWait pour attendre qu'un élément spécifique soit chargé.
        element_present = EC.presence_of_element_located((By.TAG_NAME, 'script'))
        WebDriverWait(driver, 45).until(element_present)  # Attendre jusqu'à 10 secondes
    except TimeoutException:
        print(ERROR_COLOR + "Timed out waiting for page to load" + RESET_COLOR)
    
    page_source = driver.page_source


    return page_source
    

def extract_json_from_script_anibis(script_content):
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
        "name": "Price",
        "value": price_value
    }

    json_str = script_content[start_index:end_index]
    data = '{"details":[ ' + json_str + '}}'
    # print(f"data == {data}\n end of data\n")

    try:
        parsed_data = json.loads(data)
        parsed_data["details"].insert(0, price_entry)
        formatted_json = json.dumps(parsed_data, indent=4)
        # print(f"formatted_json == {formatted_json}\n end of formatted_json\n")
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
        Name = "No_value"
    try:
        Type = next(item['value'].strip() for item in details if item['name'] == "Modèle")
    except:
        Type = "No_value"
    try:
        Color = next(item['value'].strip() for item in details if item['name'] == "Couleur extérieure")
    except:
        Color = "No_value"
    try:
        Transmission = next(item['value'].strip() for item in details if item['name'] == "Transmission")
    except:
        Transmission = "No_value"
    try:
        Wheel_Drive = next(item['value'].strip() for item in details if item['name'] == "Roues motrices")
    except:
        Wheel_Drive = "No_value"
    try:
        Mileage = next(item['value'].strip() for item in details if item['name'] == "Kilomètres")
    except:
        Mileage = "No_value"
    try:
        First_Registration_Date = next(item['value'].strip() for item in details if item['name'] == "Année")
    except:
        First_Registration_Date = "No_value"
    try:
        cm3 = next(item['value'].strip().split()[0] for item in details if item['name'] == "Cylindrée (Cm3)")
    except:
        cm3 = "No_value"
    try:
        Fuel_Type = next(item['value'].strip() for item in details if item['name'] == "Carburant")
    except:
        Fuel_Type = "No_value"
    try:
        Dealer_Name = "Private Seller" 
    except:
        Dealer_Name = "No_value"
    try:
        Dealer_Address = data["location"]["zipCity"] + ", " + ["street"]
    except:
        Dealer_Address = "No_value"

        URL = url_of_vhc
    try:
        Price = next(item['value'].strip() for item in details if item['name'] == "Price")
    except:
        Price = "No_value"
    
    car = {
        "URL": URL,
        "name": Name,
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
        "Fuel Type": Fuel_Type,
        "vhc_type": utils.identify_vhc_type(url_of_vhc)

    }

    return car

def extract_details_from_scout24(data, url_of_vhc):

    URL = url_of_vhc
    Name = data['props']['pageProps']['listing']['make']['name']
    Type = data['props']['pageProps']['listing']['model']['name']
    Color = data['props']['pageProps']['listing']['bodyColor']
    Transmission = data['props']['pageProps']['listing']['transmissionType']
    Wheel_Drive = data['props']['pageProps']['listing']['driveType']
    Mileage = str(data['props']['pageProps']['listing']['mileage'])
    Price = str(data['props']['pageProps']['listing']['price'])
    Dealer_Name = data['props']['pageProps']['seller']['name']
    try:
        Dealer_Address = data['props']['pageProps']['seller']['address'] + ", " + data['props']['pageProps']['seller']['city']
    except:
        Dealer_Address = "Inconnue"
    First_Registration_Date = data['props']['pageProps']['listing']['firstRegistrationDate']
    cm3 = data['props']['pageProps']['listing']['cubicCapacity']
    Fuel_Type = data['props']['pageProps']['listing']['fuelType']

    car = {
        "URL": URL,
        "name": Name,
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
        "Fuel Type": Fuel_Type,
        "vhc_type": utils.identify_vhc_type(url_of_vhc)
    }

    return car





def extract_data(driver, url_page, source):
    # print(f"url_page == {url_page}")
    urls_list = []
    json_list = []
    # wait = WebDriverWait(driver, 20)

    time.sleep(0.5)
    driver.get(url_page)
    time.sleep(0.5)
    urls = get_all_direct_urls_of_vehicles(driver, source)
    urls_list.append(urls)

    # print(f"urls_list == {urls_list}")
    for url_list in urls_list:
        for url_of_vhc in url_list:
            # print(f"urls_list == {urls_list}")
            # print(f"url_of_vhc == {url_of_vhc}\n end of url_of_vhc\n")
            print(WARNING_COLOR + "URL of vhc " + RESET_COLOR + url_of_vhc)
            try:
                driver.get(url_of_vhc)
                # wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/script[1]')))
                script_content = driver.find_element(By.XPATH, '/html/body/script[1]').get_attribute('innerHTML')
            except (NoSuchElementException, TimeoutException) as e:
                print(ERROR_COLOR + "Error while getting script_content: " + str(e) + RESET_COLOR)
                return
            # print(f"script_content == {script_content}\n end of script_content\n")
            if source == "anibis":
                data_string = extract_json_from_script_anibis(script_content)
                data = json.loads(data_string)
                formated = format_anibis_to_scout24(data, url_of_vhc)
                # if int(formated.get("cylinder", 0)) > 600 or not formated.get("cylinder", 0):
                if formated:
                    json_list.append(formated)
            elif source == "scout24":
                data = json.loads(script_content)
                cleaned_script_content = extract_details_from_scout24(data, url_of_vhc)
                # if int(cleaned_script_content.get("cylinder", 0)) > 600:
                if cleaned_script_content:
                    json_list.append(cleaned_script_content)
            # print(f"data:\n {data}\nend of data\n")
    return json_list

def add_ref(data):
    for sublist in data:
        for vehicle in sublist:
            # print(f"sublist:\n{sublist}\n")
            # print(f"vehicle:\n{vehicle}\n")
            name_number = 5

            if 'Type' in vehicle and vehicle['Type']:
                name_number = 1
                type_part = vehicle['Type'][:3]
            else:
                type_part = ''
                print(f"no type for {vehicle['name']}")

            name_part = vehicle['name'][:name_number].replace(' ', '')
            mileage_part = vehicle['Mileage'].replace(' km', '').replace("'", '')

            if 'Cm3' in vehicle and vehicle['Cm3']:
                cm3_part = vehicle['Cm3']
            else:
                cm3_part = ''
                print(f"no cm3 for {vehicle['name']}")

            if 'First Registration Date' in vehicle and vehicle['First Registration Date'] and isinstance(vehicle['First Registration Date'], int):
                registration_date = vehicle['First Registration Date']
            else:
                registration_date = ''

            if 'Color' in vehicle and vehicle['Color']:
                color_part = vehicle['Color']
            else:
                color_part = ''
                print(f"no color for {vehicle['name']}")

            ref_str = f"{name_part}{type_part}{mileage_part}{color_part}{registration_date}{cm3_part}"
            # print(f"ref_str == {ref_str}\n end of ref_str\n")
            try:
                vehicle['Ref'] = ref_str
            except:
                print(ERROR_COLOR + f"Error while adding ref to {vehicle['name']},\n vehicle == {vehicle}" + RESET_COLOR)
    return data

def add_prixkm(data):
    # grouped_vhc = sort_vhc.group_vehicles_by_name_and_cylindree(vehicle)
    # ranked_vhc = sort_vhc.rank_vehicules(grouped_vhc)
    data_prixkm = sort_vhc.rank_vehicles(data)
    # vhc_DB
    return data_prixkm

def extract_vehicle_data(driver, urls_to_scrape):
    all_data = []
    for url in urls_to_scrape:
        print(WARNING_COLOR + "Scraping "  + RESET_COLOR + f"{url}...")
        if not url:
            continue
        source = utils.identify_url_source(url)
        extracted_data = extract_data(driver, url, source)
        # print(f"extracted_data:\n{extracted_data}\n")
        if extracted_data:
            all_data.append(extracted_data)
        print(OK_COLOR + "Scraped" + RESET_COLOR)
    return all_data

def main(driver, urls_to_scrape):
    print(WARNING_COLOR + "Lancement du scrap..." + RESET_COLOR)
    if not urls_to_scrape:
        print(ERROR_COLOR + "No URLS found in .env file" + RESET_COLOR)
        return
    extracted_data = extract_vehicle_data(driver, urls_to_scrape)
    # print(f"extracted_data:\n{extracted_data}\n")
    data_ref = add_ref(extracted_data)
    # print(f"data_ref:\n{data_ref}\n")
    data_complet = add_prixkm(data_ref)
    # print(f"data_complet:\n{data_complet}\n")
    vhc_DB.run_database(data_complet)
    print(OK_COLOR + "Scrap done!" + RESET_COLOR)

def run_scraping(driver, urls_to_scrape):
    main(driver, urls_to_scrape)
