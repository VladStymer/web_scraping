import os
import json
import smtp_transfer
from datetime import date
from datetime import time
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()

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
        print(f"Le fichier {file_name} n'a pas été trouvé.")
        return None
    except json.JSONDecodeError as e:
        print(f"Erreur de décodage JSON : {e}")
        return None

def normalise(values):
    mean = sum(values) / len(values)
    variance = sum([(x - mean) ** 2 for x in values]) / len(values)
    std_dev = variance ** 0.5
    return [(x - mean) / std_dev for x in values]

def rank_vehicules(vehicules):
    # Convertir le prix et le kilométrage en float/int
    for vehicle in vehicules:
        vehicle["Price"] = float(vehicle["Price"].replace("CHF", "").strip())
        vehicle["Mileage"] = int(vehicle["Mileage"].replace("'", "").replace("km", "").strip())
    
    prices = [v['Price'] for v in vehicules]
    mileages = [v['Mileage'] for v in vehicules]
    
    norm_prices = normalise(prices)
    norm_mileages = normalise(mileages)
    
    scores = [-p - m for p, m in zip(norm_prices, norm_mileages)]
    
    ranked_vehicules = [vehicules[i] for i in sorted(range(len(scores)), key=lambda k: scores[k], reverse=True)]
    
    return ranked_vehicules

def main():
    print("Interprétation des résultats...")
    today = date.today()
    counter = 1
    while True:
        file_name = f"{today}_data.json" if counter == 1 else f"{today}_data{counter}.json"
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
            print(f"\n====== {first_vehicle_name} ======")
            for v in ranked:
                dealer_name = v['Dealer Name'][:22]  # Limite à 27 caractères
                price = f"{v['Price']}CHF"
                mileage = f"{v['Mileage']}km"
                print(f"{dealer_name.ljust(25)}  |  Prix: {price.rjust(12)}  |  Kilométrage: {mileage.rjust(10)}")
        print("\n")
        counter += 1

    with open('vehicules_list.txt', 'w') as file:
        for v in ranked:
            dealer_name = v['Dealer Name'][:27]
            price = f"{v['Price']}CHF"
            mileage = f"{v['Mileage']}km"
            email_content = "Voici les nouveaux véhicules trouvés:\n\n"
            file.write(f"{dealer_name.ljust(30)} | Prix: {price.rjust(10)} | Kilométrage: {mileage.rjust(8)}\n")

    if should_send_email():
        smtp_transfer.send_email("Vehicules list", email_content, "garage.titane@gmail.com", "vehicules_list.txt")
    else:
        print("Not the right time to send an email")
    print("Interpretation done!")

def run_interpret():
    main()
