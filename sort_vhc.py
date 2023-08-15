import os
import vhc_DB
import sqlite3
import export
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from collections import defaultdict
# from vhc_DB import recuperer_vehicules

load_dotenv()
MODE = int(os.getenv("MODE"))
WARNING_COLOR = os.getenv("WARNING_COLOR").encode().decode('unicode_escape')
OK_COLOR = os.getenv("OK_COLOR").encode().decode('unicode_escape')
ERROR_COLOR = os.getenv("ERROR_COLOR").encode().decode('unicode_escape')
RESET_COLOR = os.getenv("RESET_COLOR").encode().decode('unicode_escape')

def rank_vehicles(vehicles):
    if not vehicles:
        print("Aucun véhicule à classer.")
        return []

    # Flatten the list of vehicles
    flat_vehicles = [v for sublist in vehicles for v in sublist]

    # Extract and normalize prices and mileages
    for vehicle in flat_vehicles:
        # print(f"vehicle: {vehicle}")
        # Handle 'Unknown' price
        if vehicle["Price"] == 'Unknown':
            vehicle["Price"] = None
        else:
            vehicle["Price"] = float(vehicle["Price"].replace("CHF", "").strip())

        # Convert mileage to int
        vehicle["Mileage"] = int(vehicle["Mileage"].replace("'", "").replace("km", "").strip())

    # Calculate the price/km ratio directly
    for vehicle in flat_vehicles:
        if vehicle["Price"] is not None and vehicle["Mileage"] > 0:
            vehicle["prix_km"] = round(vehicle["Price"] / vehicle["Mileage"], 3)
        else:
            vehicle["prix_km"] = None

    return flat_vehicles

def vhc_sorted_by_name():
    with vhc_DB.DatabaseContext() as cursor:
        cursor.execute('''
        SELECT * FROM vehicules
        ORDER BY marque ASC, modele ASC
        ''')
        # ordre croissant == ASC ordre décroissant == DESC.
        
        # Récupérer tous les résultats
        resultats = cursor.fetchall()
        # print(f"resultats: {resultats}")
        return resultats

def normalize_model(model_name):
    # Convert to uppercase, remove spaces and hyphens
    words = model_name.upper().replace("-", " ").split()
    # Sort the words and rejoin them
    sorted_name = ''.join(sorted(words))
    return sorted_name

def extract_marque_modele(vehicle):
    marque = vehicle[1]
    modele = normalize_model(vehicle[2])
    return marque, modele

def group_vehicles_by_name():
    vehicles = vhc_sorted_by_name()
    grouped = defaultdict(list)

    for vehicle in vehicles:
        # print(f"vehicle: {vehicle}")
        marque, modele = extract_marque_modele(vehicle)
        grouped[(marque, modele)].append(vehicle)
    
    return grouped

def analyze_vehicle_groups():
    grouped_vehicles = group_vehicles_by_name()
    for key, vehicles in grouped_vehicles.items():
        marque, modele = key
        print(f"Analyzing {marque} - {modele}")
        
        vhc_type = vehicles[0][-1]  # vhc_type from the first vehicle in the list
        sort_vhc(vhc_type, vehicles)


def sort_vhc(vhc_type, vehicles):
    if vhc_type == "bike":
        segments = [
            (0, 1000),
            (1001, 2000),
            (2001, 3000),
            (3001, 4000),
            (4001, 5000),
            (5001, 6000),
            (6001, 7000),
            (7001, 8000),
            (8001, 9000),
            (9001, 10000)
        ]
    elif vhc_type == "car":
        segments = [
            (0, 10000),
            (10001, 40000),
            (40001, 70000),
            (70001, 100000),
        ]
    else:
        print("Type de véhicule inconnu!")
        return

    moyennes = []

    for start, end in segments:
        # Filtrez les véhicules du groupe actuel qui sont dans ce segment
        filtered_vehicles = [vhc for vhc in vehicles if start <= vhc[5] <= end]  # assuming kilometrage is at index 5

        # Calculez la moyenne des prix pour ces véhicules
        total_price = sum(vhc[4] for vhc in filtered_vehicles)  # assuming prix is at index 4
        avg_price = total_price / len(filtered_vehicles) if filtered_vehicles else None

        if avg_price:
            moyennes.append((start, end, avg_price))
    vhc_name = vehicles[0][1] + " " + vehicles[0][2]
    export.vehicules_vers_txt()
    draw_data(moyennes, vhc_name)

def draw_data(moyennes, vhc_name):

    # Extraire les points centraux des segments pour l'axe X
    x = [(start + end) / 2 for start, end, _ in moyennes]

    # Prix moyens pour l'axe Y
    y = [avg for _, _, avg in moyennes]

    plt.plot(x, y, marker='o')
    plt.title(f'Prix moyen des {vhc_name} en fonction du kilométrage')
    plt.xlabel('Kilomètres')
    plt.ylabel('Prix moyen CHF')
    plt.grid(True)
    plt.show()
