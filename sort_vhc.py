import os
import smtp_transfer
import vhc_DB
from datetime import date
from datetime import time
from datetime import datetime
from dotenv import load_dotenv
# from vhc_DB import recuperer_vehicules

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

def recuperer_vehicules_tries_par_nom_et_prix_km():
    with vhc_DB.DatabaseContext() as cursor:
        cursor.execute('''
        SELECT * FROM vehicules
        ORDER BY marque ASC, modele ASC, prix_km ASC
        ''')
        # ordre croissant == ASC ordre décroissant == DESC.
        
        # Récupérer tous les résultats
        resultats = cursor.fetchall()
        # print(f"resultats: {resultats}")
        return resultats


def max_width(data, index):
    """Retourne la largeur maximale pour une colonne donnée"""
    return max(len(str(row[index])) for row in data)

def vehicules_vers_txt():
    vehicules = recuperer_vehicules_tries_par_nom_et_prix_km()

    # Calculer la largeur maximale pour chaque colonne
    widths = [max_width(vehicules, i) for i in range(len(vehicules[0]))]

    # Ouvrir (ou créer) un fichier en mode écriture
    with open("vehicls_sorted.txt", "w", encoding="utf-8") as fichier:
        # Écrire les en-têtes de colonnes en premier
        en_tetes = ["id", "url", "ref", "marque", "modele", "annee", "couleur", 
                    "transmission", "WD", "km", "prix_km",
                    "prix", "nom_vendeur", "adresse_vendeur", "année", "CV", "carburant"]
        
        # Utilisez la méthode 'format' pour formatter les en-têtes avec les largeurs maximales
        fichier.write("".join("{:<{}}\t".format(en_tetes[i], widths[i]) for i in range(len(en_tetes))) + "\n")

        # Parcourir chaque véhicule et écrire ses détails dans le fichier
        for vehicule in vehicules:
            fichier.write("".join("{:<{}}\t".format(str(vehicule[i]), widths[i]) for i in range(len(vehicule))) + "\n")


def normalise(values):
    mean = sum(values) / len(values)
    variance = sum([(x - mean) ** 2 for x in values]) / len(values)
    std_dev = variance ** 0.5
    return [(x - mean) / std_dev for x in values]

def rank_vehicles(vehicles):
    if not vehicles:
        print("Aucun véhicule à classer.")
        return []

    # Flatten the list of vehicles
    flat_vehicles = [v for sublist in vehicles for v in sublist]

    # Extract and normalize prices and mileages
    for vehicle in flat_vehicles:
        print(f"vehicle: {vehicle}")
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




def group_vehicles_by_name_and_cylindree(vehicle):
    grouped_vehicles = {}

    # for vehicle in vehicles:
        # Récupération du nom, modèle et cylindrée
    name = vehicle.get("name", "")
    model = vehicle.get("Type", "")
    cylindree = vehicle.get("Cylindrée", "")
    carburant = vehicle.get("Type de carburant", "")

    # Générez une clé à partir du nom, modèle et cylindrée
    key = f"{name}_{model}_{cylindree}"

    # Ajout du véhicule au groupe correspondant dans le dictionnaire
    if key not in grouped_vehicles:
        grouped_vehicles[key] = []
    grouped_vehicles[key].append(vehicle)

    return grouped_vehicles




def main(extracted_data):
    print(WARNING_COLOR + "Interprétation des résultats..." + RESET_COLOR)
    print(f"extracted_data:\n{extracted_data}\n")
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

            ranked = rank_vehicles(cars_data)
            if ranked: # vérifie que la liste n'est pas vide
                first_vehicle_name = ranked[0]['name']
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
                name = v['name'][:16]
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
        grouped_by_name = group_vehicles_by_name_and_cylindree(extracted_data)
        for key, value in grouped_by_name.items():
            ranked = rank_vehicles(value)
            name = ranked[0]['name'][:16] if ranked else "default"
            print(f"vehicules_list_{name}.txt")
            with open(f'vehicules_list_{name}.txt', 'a') as file:
                    for v in ranked:
                        name = v['name'][:16]
                        dealer_name = v['Dealer Name'][:27]
                        price = f"{v['Price']}CHF"
                        mileage = f"{v['Mileage']}km"
                        email_content = f"Vehicules {v['name']} interessants:\n\n"
                        file.write(f"{name.ljust(30)} | {dealer_name.ljust(30)}\nPrix: {price.rjust(10)} | Kilométrage: {mileage.rjust(8)}\n\n")

            smtp_transfer.run_smtp_transfer("Vehicules list", email_content, "garage.titane@gmail.com", "vehicules_list.txt")

    print(OK_COLOR + "Interpretation done!" + RESET_COLOR)

def run_interpret(extracted_data):
    main(extracted_data)
