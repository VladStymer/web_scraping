import os
import vhc_DB
import sqlite3
import matplotlib.pyplot as plt
from dotenv import load_dotenv
# from vhc_DB import recuperer_vehicules

load_dotenv()
MODE = int(os.getenv("MODE"))
WARNING_COLOR = os.getenv("WARNING_COLOR").encode().decode('unicode_escape')
OK_COLOR = os.getenv("OK_COLOR").encode().decode('unicode_escape')
ERROR_COLOR = os.getenv("ERROR_COLOR").encode().decode('unicode_escape')
RESET_COLOR = os.getenv("RESET_COLOR").encode().decode('unicode_escape')


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

def group_vehicles_by_name():
    vehicles = vhc_sorted_by_name()
    grouped_vehicles = {}

    for vehicle in vehicles:
        key = (vehicle[1], vehicle[2])  # marque, modele
        if key not in grouped_vehicles:
            grouped_vehicles[key] = []
        grouped_vehicles[key].append(vehicle)
    
    return grouped_vehicles

def analyze_vehicle_groups():
    grouped_vehicles = group_vehicles_by_name()
    for key, vehicles in grouped_vehicles.items():
        marque, modele = key
        print(f"Analyzing {marque} - {modele}")
        
        vhc_type = vehicles[0][-1]  # vhc_type from the first vehicle in the list
        sort_vhc(vhc_type, vehicles)

def sort_vhc(vhc_type, vehicles):
    segments_bike = [
    (0, 1000),
    (1001, 4000),
    (4001, 7000),
    (7001, 10000),
    ]
    segments_car = [
    (0, 10000),
    (10001, 40000),
    (40001, 70000),
    (70001, 100000),
    ]

    if vhc_type == "bike":
        segments = segments_bike
    elif vhc_type == "car":
        segments = segments_car
    conn = sqlite3.connect('vehicules.db')
    cursor = conn.cursor()

    moyennes = []

    for start, end in segments:
        query = """
                SELECT AVG(prix) FROM vehicules 
                WHERE kilometrage BETWEEN ? AND ? AND vhc_type = ?
                """
        cursor.execute(query, (start, end, vhc_type))
        avg_price = cursor.fetchone()[0]
        if avg_price:
            moyennes.append((start, end, avg_price))
    draw_data(moyennes)

def draw_data(moyennes):

    # Extraire les points centraux des segments pour l'axe X
    x = [(start + end) / 2 for start, end, _ in moyennes]

    # Prix moyens pour l'axe Y
    y = [avg for _, _, avg in moyennes]

    plt.plot(x, y, marker='o')
    plt.title('Dépréciation des voitures en fonction du kilométrage')
    plt.xlabel('Kilomètres')
    plt.ylabel('Prix moyen (€)')
    plt.grid(True)
    plt.show()
    