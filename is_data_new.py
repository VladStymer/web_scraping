import re
import os
import json
import glob
from dotenv import load_dotenv


debug_mode = os.getenv("DEBUG", "False").lower() == "true"
load_dotenv()
WARNING_COLOR = os.getenv("WARNING_COLOR").encode().decode('unicode_escape')
OK_COLOR = os.getenv("OK_COLOR").encode().decode('unicode_escape')
ERROR_COLOR = os.getenv("ERROR_COLOR").encode().decode('unicode_escape')
RESET_COLOR = os.getenv("RESET_COLOR").encode().decode('unicode_escape')

def extract_vehicle_id(vehicle):
    """Extrait le numéro ID du véhicule depuis l'URL de la première image."""
    image_url = vehicle["Images"][0]  # prendre la première image
    match = re.search(r"/(\d{7,9})/", image_url)  # recherche d'un nombre composé de 7 à 9 chiffres
    if debug_mode:
        print(f"extract_vehicle_id: image_url={image_url}, match={match.group(1)}")
    if not match:
        print(ERROR_COLOR + f"Couldn't extract vehicle ID from image URL: {image_url}" + RESET_COLOR)
    return match.group(1) if match else None

def is_new(id_existing_data, id_new_data):
    # Conserve uniquement les ID qui ne sont pas dans id_existing_data
    id_data = set(id_new_data)
    id_data.difference_update(id_existing_data)
    return id_data
    


def is_data_new_main(extracted_data):
    print(WARNING_COLOR + "Lancement de is_data_new_main..." + RESET_COLOR)
    matching_files = sorted(glob.glob(f"*.json"))
    all_existing_data = set()
    new_data = set()
    new_vehicles = []

    # Extrait les id de tous les fichiers
    for filename in matching_files:
        with open(filename, 'r') as file:
            existing_data = json.load(file)
            if isinstance(existing_data, list):
                for vehicle in existing_data:
                    vehicle_id = extract_vehicle_id(vehicle)
                    if vehicle_id:
                        all_existing_data.add(vehicle_id)
    # Extrait les id de extracted_data
    for vehicle in extracted_data:
        vehicle_id = extract_vehicle_id(vehicle)
        if vehicle_id:
            new_data.add(vehicle_id)
    # Cherche les nouveaux id
    new_vehicles_id = is_new(all_existing_data, new_data)
    # Cherche dans extracted_data si un id de new_vehicles_id correspond, si oui, ajoute le véhicule à new_vehicles
    for vehicle in extracted_data:
        vehicle_id = extract_vehicle_id(vehicle)
        if vehicle_id in new_vehicles_id:
            new_vehicles.append(vehicle)
    return new_vehicles
