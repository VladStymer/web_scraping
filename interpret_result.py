import json
import time
import requests
import os
from datetime import date


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

# def compare_cars_by_price_per_km(cars_data):
#     # Convertir les valeurs Price et Mileage en numérique (s'ils sont stockés comme des chaînes)
#     # et calculer le rapport prix/km pour chaque voiture
#     for car in cars_data:
#         car['Price'] = float(car['Price'].replace('CHF', '').replace(',', '').strip())  # Conversion du prix en float
#         car['Mileage'] = float(car['Mileage'].replace('km', '').replace(',', '').replace('\'', '').strip())  # Conversion du kilométrage en float
#         car['Price_per_km'] = car['Price'] / car['Mileage']

#     # Trier les voitures par rapport prix/km (du plus bas au plus haut)
#     sorted_cars = sorted(cars_data, key=lambda x: x['Price_per_km'])

#     # Afficher les voitures triées par rapport prix/km
#     for car in sorted_cars:
#         print(f"{car['Name']} - Prix: {car['Price']} CHF - Kilométrage: {car['Mileage']} km - Prix/km: {car['Price_per_km']:.2f} CHF/km")

def main():
    today = date.today()
    file_name = f"data_{today}.json"
    # with open(file_name, 'r') as file:
    #     cars_data = json.load(file)
    try:
        with open(file_name, 'r') as file:
            cars_data = json.load(file)
    except FileNotFoundError:
        print(f"Le fichier {file_name} n'a pas été trouvé.")
        return
    except json.JSONDecodeError as e:
        print(f"Erreur de décodage JSON : {e}")
        return

    ranked = rank_vehicles(cars_data)
    for v in ranked:
        dealer_name = v['Dealer Name']
        price = f"{v['Price']}CHF"
        mileage = f"{v['Mileage']}km"
        # print(f"{v['Dealer Name']} - Prix: {v['Price']}CHF, Kilométrage: {v['Mileage']}km")
        print(f"{dealer_name.ljust(30)} - Prix: {price.rjust(15)}, Kilométrage: {mileage.rjust(15)}")

if __name__ == "__main__":
    main()
