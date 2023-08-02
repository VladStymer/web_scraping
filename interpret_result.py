import os
import json
import smtp_transfer
from datetime import date
from datetime import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
MODE = int(os.getenv("MODE"))
WARNING_COLOR = os.getenv("WARNING_COLOR").encode().decode('unicode_escape')
OK_COLOR = os.getenv("OK_COLOR").encode().decode('unicode_escape')
ERROR_COLOR = os.getenv("ERROR_COLOR").encode().decode('unicode_escape')
RESET_COLOR = os.getenv("RESET_COLOR").encode().decode('unicode_escape')

def time_from_env(key):
    """Convertit une chaîne HH:MM depuis .env en un objet time."""
    hours, minutes = map(int, os.getenv(key).split(":"))
    return time(hours, minutes)

def should_send_email():
    current_time = datetime.now().time()  # Obtient l'heure actuelle
    
    # Récupérer les heures de début et de fin depuis le fichier .env
    morning_start = time_from_env('MORNING_START')
    morning_end = time_from_env('MORNING_END')
    evening_start = time_from_env('EVENING_START')
    evening_end = time_from_env('EVENING_END')

    # Vérifier si l'heure actuelle se situe dans une des plages horaires
    return morning_start <= current_time <= morning_end or evening_start <= current_time <= evening_end


def load_file(file_name):
    try:
        with open(file_name, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(ERROR_COLOR + f"Le fichier {file_name} n'a pas été trouvé." + RESET_COLOR)
        return None
    except json.JSONDecodeError as e:
        print(ERROR_COLOR + f"Erreur de décodage JSON : {e}" + RESET_COLOR)
        return None

def normalise(values):
    mean = sum(values) / len(values)
    variance = sum([(x - mean) ** 2 for x in values]) / len(values)
    std_dev = variance ** 0.5
    return [(x - mean) / std_dev for x in values]

def rank_vehicules(vehicules):
    print(WARNING_COLOR + "Ranking vehicules..." + RESET_COLOR)
    if not vehicules:
        print(ERROR_COLOR + "Aucun véhicule à classer." + RESET_COLOR)
        return []
    for vehicle in vehicules:
        # Convertir le prix en float si ce n'est pas déjà un float
        if not isinstance(vehicle["Price"], float):
            vehicle["Price"] = float(vehicle["Price"].replace("CHF", "").strip())
        # Convertir le kilométrage en int si ce n'est pas déjà un int
        if not isinstance(vehicle["Mileage"], int):
            vehicle["Mileage"] = int(vehicle["Mileage"].replace("'", "").replace("km", "").strip())
    
    print(WARNING_COLOR + "Calcul des scores..." + RESET_COLOR)
    prices = [v['Price'] for v in vehicules]
    mileages = [v['Mileage'] for v in vehicules]
    
    norm_prices = normalise(prices)
    norm_mileages = normalise(mileages)
    
    scores = [-p - m for p, m in zip(norm_prices, norm_mileages)]
    
    ranked_vehicules = [vehicules[i] for i in sorted(range(len(scores)), key=lambda k: scores[k], reverse=True)]
    
    return ranked_vehicules



def group_vehicles_by_name(vehicles_list):
    grouped_vehicles = {}
    
    for vehicle in vehicles_list:
        name = vehicle["Name"]
        if name in grouped_vehicles:
            grouped_vehicles[name].append(vehicle)
        else:
            grouped_vehicles[name] = [vehicle]
            
    return grouped_vehicles



def main(extracted_data):
    print(WARNING_COLOR + "Interprétation des résultats..." + RESET_COLOR)
    if MODE == 0:
        today = date.today()
        counter = 1
        while True:
            file_name = f"{today}_data{counter}.json"
            # Si le fichier n'existe pas, on arrête.
            if not os.path.exists(file_name):
                break
            
            cars_data = load_file(file_name)
            if cars_data is None:
                counter += 1
                continue

            ranked = rank_vehicules(cars_data)
            if ranked: # vérifie que la liste n'est pas vide
                first_vehicle_name = ranked[0]['Name']
                # print(f"\n====== {first_vehicle_name} ======")
                for v in ranked:
                    dealer_name = v['Dealer Name'][:22]  # Limite à 27 caractères
                    price = f"{v['Price']}CHF"
                    mileage = f"{v['Mileage']}km"
                    # print(f"{dealer_name.ljust(25)}  |  Prix: {price.rjust(12)}  |  Kilométrage: {mileage.rjust(10)}")
            # print("\n")
            counter += 1

        with open('vehicules_list.txt', 'a') as file:
            for v in ranked:
                name = v['Name'][:16]
                dealer_name = v['Dealer Name'][:27]
                price = f"{v['Price']}CHF"
                mileage = f"{v['Mileage']}km"
                email_content = "Vehicules interessants:\n\n"
                file.write(f"{name.ljust(30)} | {dealer_name.ljust(30)}\nPrix: {price.rjust(10)} | Kilométrage: {mileage.rjust(8)}\n\n")

        if should_send_email():
            smtp_transfer.run_smtp_transfer("Vehicules list", email_content, "garage.titane@gmail.com", "vehicules_list.txt")
        else:
            print("Not the right time to send an email")
    elif MODE == 1:
        grouped_by_name = group_vehicles_by_name(extracted_data)
        for key, value in grouped_by_name.items():
            ranked = rank_vehicules(value)
            name = ranked[0]['Name'][:16] if ranked else "default"
            print(f"vehicules_list_{name}.txt")
            with open(f'vehicules_list_{name}.txt', 'a') as file:
                    for v in ranked:
                        name = v['Name'][:16]
                        dealer_name = v['Dealer Name'][:27]
                        price = f"{v['Price']}CHF"
                        mileage = f"{v['Mileage']}km"
                        email_content = f"Vehicules {v['Name']} interessants:\n\n"
                        file.write(f"{name.ljust(30)} | {dealer_name.ljust(30)}\nPrix: {price.rjust(10)} | Kilométrage: {mileage.rjust(8)}\n\n")

            smtp_transfer.run_smtp_transfer("Vehicules list", email_content, "garage.titane@gmail.com", "vehicules_list.txt")

    print(OK_COLOR + "Interpretation done!" + RESET_COLOR)

def run_interpret(extracted_data):
    main(extracted_data)
