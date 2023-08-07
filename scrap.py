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
    



    # Récupérez le code source de la page
    page_source = driver.page_source

    # driver.quit()
    # if debug_mode:
    #     print(f"get_content_from_url: page_source={page_source}")
    # print(f"page_source == {page_source}\n end of page_source\n")

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
    try:
        Price = next(item['value'].strip() for item in details if item['name'] == "Price")
    except:
        Price = None
    
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
        "Fuel Type": Fuel_Type
    }

    return car

def extract_details_from_scout24(data):

    # Récupérer la valeur de 'listing_makeName'
    make_name = data['props']['pageProps']['listing']['make']['name']
    print(make_name)

    return make_name





def extract_data(driver, url_page, source):
    # print(f"url_page == {url_page}")
    urls_list = []
    json_list = []

    time.sleep(1)
    driver.get(url_page)
    urls = get_all_direct_urls_of_vehicles(driver, source)
    urls_list.append(urls)

    # print(f"urls_list == {urls_list}")
    for url_list in urls_list:
        for url_of_vhc in url_list:
            # print(f"urls_list == {urls_list}")
            # print(f"url_of_vhc == {url_of_vhc}\n end of url_of_vhc\n")
            try:
                time.sleep(1)
                driver.get(url_of_vhc)
            except:
                print(ERROR_COLOR + "Error while getting url_of_vhc" + RESET_COLOR)
                return
            
            script_content = driver.find_element(By.XPATH, '/html/body/script[1]').get_attribute('innerHTML')
            # print(f"script_content == {script_content}\n end of script_content\n")
            if source == "anibis":
                data_string = extract_json_from_script_anibis(script_content)
                data = json.loads(data_string)
                formated = format_anibis_to_scout24(data, url_of_vhc)
                print(f"formated == {formated}\n end of formated\n")
                json_list.append(formated)
            elif source == "scout24":
                data = json.loads(script_content)
                cleaned_script_content = extract_details_from_scout24(data)
                json_list.append(cleaned_script_content)
                
            # print(f"data:\n {data}\nend of data\n")
    # driver.quit()
    print(f"json_list:\n\n\n {json_list}\nend of json_list\n")
    return json_list

# def extract_data_scout24(driver, url_page, source):
#     # print(f"url_page == {url_page}")
#     urls_list = []
#     json_list = []

#     time.sleep(1)
#     driver.get(url_page)
#     urls = get_all_direct_urls_of_vehicles(driver, source)
#     # print(f"urls == {urls}")
#     urls_list.append(urls)

#     # print(f"urls_list == {urls_list}")
#     for url_list in urls_list:
#         for url_of_vhc in url_list:
#             # print(f"urls_list == {urls_list}")
#             # print(f"url_of_vhc == {url_of_vhc}\n end of url_of_vhc\n")
#             try:
#                 time.sleep(1)
#                 driver.get(url_of_vhc)
#             except:
#                 print(ERROR_COLOR + "Error while getting url_of_vhc" + RESET_COLOR)
#                 return
            
            
#             data = json.loads(script_content)
#             json_list.append(data)
    
#     return json_list

def add_ref(data):
    try:
        for sublist in data:
            for vehicle in sublist:
                # print(f"sublist:\n{sublist}\n")
                print(f"vehicle:\n{vehicle}\n")
                name_number = 5

                if 'Type' in vehicle and vehicle['Type']:
                    name_number = 1
                    type_part = vehicle['Type'][:3]
                else:
                    type_part = ''

                name_part = vehicle['name'][:name_number].replace(' ', '')
                mileage_part = vehicle['Mileage'].replace(' km', '').replace("'", '')

                if 'Cm3' in vehicle and vehicle['Cm3']:
                    cm3_part = vehicle['Cm3']
                else:
                    cm3_part = ''

                if 'First Registration Date' in vehicle and vehicle['First Registration Date'] and isinstance(vehicle['First Registration Date'], int):
                    registration_date = vehicle['First Registration Date']
                else:
                    registration_date = ''

                if 'Color' in vehicle and vehicle['Color']:
                    color_part = vehicle['Color']
                else:
                    color_part = ''

                ref_str = f"{name_part}{type_part}{mileage_part}{color_part}{registration_date}{cm3_part}"
                vehicle['Ref'] = ref_str
    except:
        print(ERROR_COLOR + "Error while adding ref" + RESET_COLOR)

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
    # print(f"data_prixkm:\n{data_prixkm}\n")
    vhc_DB.run_database(data_complet)
    print(OK_COLOR + "Scrap done!" + RESET_COLOR)

def run_scraping(driver, urls_to_scrape):
    main(driver, urls_to_scrape)
