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
        print(f"{dealer_name.ljust(20)}  |  Prix: {price.rjust(12)}  |  Kilométrage: {mileage.rjust(10)}")

def run_scraping():
    main()
