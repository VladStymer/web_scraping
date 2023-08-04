import os
import re
import json
import smtp_transfer
import sort_vhc
import vhc_DB 
from datetime import date
from utils import set_driver
from dotenv import load_dotenv
from utils import identify_url_source
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from dotenv import load_dotenv
from utils import identify_url_source
from is_data_new import is_data_new_main
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService


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
