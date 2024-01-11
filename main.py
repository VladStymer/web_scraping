import os
import sys
import time
import scrap
import random
import vhc_DB
import sort_vhc
from vhc_DB import init_db
from utils import set_driver
from dotenv import load_dotenv
from utils import identify_url_source





load_dotenv()
debug_mode = os.getenv("DEBUG", "False").lower() == "true"
WARNING_COLOR = os.getenv("WARNING_COLOR").encode().decode('unicode_escape')
OK_COLOR = os.getenv("OK_COLOR").encode().decode('unicode_escape')
ERROR_COLOR = os.getenv("ERROR_COLOR").encode().decode('unicode_escape')
RESET_COLOR = os.getenv("RESET_COLOR").encode().decode('unicode_escape')


URLS = {
    "URL_clio":     os.getenv("URL_CLIO"),
    "URL_tuonoV4":  os.getenv("URL_TUONO_V4"),
    # "URL_195CV":    os.getenv("URL_195CV"),
    "URL_scout24_bike": os.getenv("URL_scout24_bike"),
    "URL_anibis_bike": os.getenv("URL_anibis_bike"),
    "URL_anibis_test": os.getenv("URL_anibis_test"),
    "URL_scout24_test": os.getenv("URL_scout24_test"),
    "MT-09": os.getenv("MT-09"),
    "MT-09_anibis" : os.getenv("MT-09_anibis"),
    "NEW_MT_anibis" : os.getenv("NEW_MT_anibis"),
    "NEW_MT" : os.getenv("NEW_MT"),
}

def generate_url(base_url, source, page_number=1):
    if source == "anibis":
        page="&pi="
    elif source == "scout24":
        page="&page="
    else:
        sys.exit(f"generate_url() -> Can't identify URL source: {source}")
    if page in base_url:
        if page_number == 1:
            return base_url.split(page)[0]
    if debug_mode:
        print(f"generate_url: base_url={base_url}, page_number={page_number}")
    if page_number == 1:
        return base_url
    else:
        return f"{base_url}{page}{page_number}"

def page_exists(driver, url, source):
    time.sleep(random.uniform(0.1, 0.8))
    driver.get(url)
    if source == "anibis":
        if "4qsc3d" in driver.page_source:
            return True
        else:
            return False
    elif source == "scout24":
        if "Aucun résultat" in driver.page_source:
            return False
        else:
            return True
    else:
        print(ERROR_COLOR + "page_exists() -> Source inconnue: " + source + RESET_COLOR)
        sys.exit(1)

def collect_urls_to_scrape(driver, URLS):
    if not URLS:
            print(ERROR_COLOR + "No URLS found in .env file" + RESET_COLOR)
            return
    urls_to_scrape = []
    for key, base_url in URLS.items():
        print(WARNING_COLOR + f"Generate url {key}..." + RESET_COLOR)
        page_number = 1
        if not base_url:
            print(ERROR_COLOR + f"URL {key} not found in .env file" + RESET_COLOR)
            continue
        source = identify_url_source(base_url)
        while True:
            url = generate_url(base_url, source, page_number)
            if page_exists(driver, url, source):
                print(f"page_number == {page_number}")
                urls_to_scrape.append(url)
                page_number += 1
            else:
                break
    return urls_to_scrape

def main():
    print(WARNING_COLOR + "Lancement du main..." + RESET_COLOR)
    init_db()
    
    while True:  # Boucle infinie
        print("\nOptions disponibles :")
        print("1. run all the program")
        print("2. print_db")
        print("3. sort")
        print("5. export_in_txt")
        print("666. quitter")
        
        choice = input("Entrez votre choix : ")

        if choice == "run all the program" or choice == "1":
            try:
                driver = set_driver()
            except:
                print(ERROR_COLOR + "Can't set driver" + RESET_COLOR)
                sys.exit(1)
            urls_to_scrape = collect_urls_to_scrape(driver, URLS)
            scrap.run_scraping(driver, urls_to_scrape)
            driver.quit()
            print(OK_COLOR + "Main done!" + RESET_COLOR)
        elif choice == "print_db" or choice == "2":
            print(vhc_DB.recuperer_vehicules())
        elif choice == "sort" or choice == "3":
            sort_vhc.analyze_vehicle_groups()
        elif choice == "export_in_txt" or choice == "5":
            sort_vhc.vehicules_vers_txt()
        elif choice == "quitter" or choice == "666":
            break
        else:
            print(ERROR_COLOR + "Choix invalide." + RESET_COLOR)

if __name__ == "__main__":
    main()
