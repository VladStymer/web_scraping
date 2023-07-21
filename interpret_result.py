import json
import time
import requests
import os
from datetime import date

def download_image(url, save_path):
    response = requests.get(url, stream=True, timeout=10)  # timeout après 10 secondes
    response.raise_for_status()
    with open(save_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

def main():
    print("Téléchargement des images...")
    # Créer un dossier pour stocker les images s'il n'existe pas déjà
    base_dir = "downloaded_images"
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)
    
    print("Chargement des données...")
    # Lire le fichier JSON nommé par la date du jour
    today = date.today()
    file_name = f"data_{today}.json"
    with open(file_name, 'r') as file:
        cars_data = json.load(file)
    
    print("Téléchargement des images...")
    # Pour chaque voiture, téléchargez toutes ses images
    for car in cars_data:
        # Remplacer les caractères indésirables en dehors de l'f-string
        mileage_clean = car['Mileage'].replace(',', '').replace('\'', '')
        # Création du nom de dossier pour chaque voiture
        folder_name = f"{car['Dealer Name']}_{car['Price']}CHF_{mileage_clean}km"
        folder_path = os.path.join(base_dir, folder_name)
        
        # Créer le dossier s'il n'existe pas
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
        
        # Télécharger les images dans le dossier spécifié
        for index, image_url in enumerate(car["Images"]):
            image_name = f"{car['Name'].replace(' ', '_')}_{index}.jpg"
            save_path = os.path.join(folder_path, image_name)
            download_image(image_url, save_path)
            print(f"Téléchargé {image_name}")

if __name__ == "__main__":
    main()
