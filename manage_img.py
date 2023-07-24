# def download_image(url, cars_data, today):
#     print("Téléchargement des images...")
#     # Créer un dossier pour stocker les images s'il n'existe pas déjà
#     base_dir = "downloaded_images"
#     if not os.path.exists(base_dir):
#         os.mkdir(base_dir)
    
#     # Pour chaque voiture, téléchargez toutes ses images
#     for car in cars_data:
#         # Remplacer les caractères indésirables en dehors de l'f-string
#         mileage_clean = car['Mileage'].replace(',', '').replace('\'', '')
#         # Création du nom de dossier pour chaque voiture
#         folder_name = f"{today}_{car['Dealer Name']}_{car['Price']}CHF_{mileage_clean}km"
#         folder_path = os.path.join(base_dir, folder_name)
        
#         # Créer le dossier s'il n'existe pas
#         if not os.path.exists(folder_path):
#             os.mkdir(folder_path)

#         # Télécharger les images dans le dossier spécifié
#         for index, image_url in enumerate(car["Images"]):
#             time.sleep(0.5)
#             image_name = f"{car['Name'].replace(' ', '_')}_{index}.jpg"
#             save_path = os.path.join(folder_path, image_name)
#             response = requests.get(url, stream=True, timeout=10)  # timeout après 10 secondes
#             response.raise_for_status()
#             with open(save_path, 'wb') as file:
#                 for chunk in response.iter_content(chunk_size=8192):
#                     file.write(chunk)
#             print(f"Téléchargé {image_name}")

# def delete_last_month_images():
#     today = datetime.today()
#     # Si nous sommes le 1er du mois
#     if today.day == 1:
#         last_month = today.month - 1 if today.month != 1 else 12
        
#         base_dir = "downloaded_images"
        
#         # Pour chaque dossier dans le répertoire de base
#         for folder_name in os.listdir(base_dir):
#             # Ici, nous supposons que votre nom de dossier suit le format "YYYY-MM-DD" quelque part dans le nom
#             # Par exemple, "Dealer_Name_40000CHF_12000km_2022-06-10"
#             try:
#                 date_part = folder_name.split('_')[-1]
#                 folder_date = datetime.strptime(date_part, "%Y-%m-%d")
#                 if folder_date.month == last_month:
#                     folder_path = os.path.join(base_dir, folder_name)
#                     shutil.rmtree(folder_path)
#                     print(f"Dossier {folder_name} supprimé.")
#             except:
#                 # Ici, nous ignorons les dossiers qui n'ont pas une date valide dans leur nom
#                 pass