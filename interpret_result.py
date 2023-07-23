import json
import interpret_result
import os
from datetime import date

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

def rank_vehicles(vehicles):
    # Convertir le prix et le kilométrage en float/int
    for vehicle in vehicles:
        vehicle["Price"] = float(vehicle["Price"].replace("CHF", "").strip())
        vehicle["Mileage"] = int(vehicle["Mileage"].replace("'", "").replace("km", "").strip())
    
    prices = [v['Price'] for v in vehicles]
    mileages = [v['Mileage'] for v in vehicles]
    
    norm_prices = normalise(prices)
    norm_mileages = normalise(mileages)
    
    scores = [-p - m for p, m in zip(norm_prices, norm_mileages)]
    
    ranked_vehicles = [vehicles[i] for i in sorted(range(len(scores)), key=lambda k: scores[k], reverse=True)]
    
    return ranked_vehicles

def main():
    today = date.today()
    counter = 1
    while True:
        file_name = f"data_{today}.json" if counter == 1 else f"data{counter}_{today}.json"
        # Si le fichier n'existe pas, on arrête.
        if not os.path.exists(file_name):
            break
        
        cars_data = load_file(file_name)
        if cars_data is None:
            counter += 1
            continue

        ranked = rank_vehicles(cars_data)
        if ranked: # vérifie que la liste n'est pas vide
            first_vehicle_name = ranked[0]['Name']
            print(f"====== {first_vehicle_name} ======")
            for v in ranked:
                dealer_name = v['Dealer Name'][:22]  # Limite à 27 caractères
                price = f"{v['Price']}CHF"
                mileage = f"{v['Mileage']}km"
                print(f"{dealer_name.ljust(25)}  |  Prix: {price.rjust(12)}  |  Kilométrage: {mileage.rjust(10)}")
        print("\n")
        counter += 1

    email_content = ""
    for v in ranked:
        dealer_name = v['Dealer Name'][:27]
        price = f"{v['Price']}CHF"
        mileage = f"{v['Mileage']}km"
        email_content += f"{dealer_name.ljust(25)}  |  Prix: {price.rjust(12)}  |  Kilométrage: {mileage.rjust(10)}\n"

    interpret_result.send_email("Résultats du jour", email_content, "garage.titane@gmail.com")


def run_interpret():
    main()
    print("Interprétation terminée.")
