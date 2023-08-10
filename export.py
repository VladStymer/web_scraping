import os
import sort_vhc
from dotenv import load_dotenv

load_dotenv()
MODE = int(os.getenv("MODE"))
WARNING_COLOR = os.getenv("WARNING_COLOR").encode().decode('unicode_escape')
OK_COLOR = os.getenv("OK_COLOR").encode().decode('unicode_escape')
ERROR_COLOR = os.getenv("ERROR_COLOR").encode().decode('unicode_escape')
RESET_COLOR = os.getenv("RESET_COLOR").encode().decode('unicode_escape')

def max_width(data, index):
    """Retourne la largeur maximale pour une colonne donnée"""
    return max(len(str(row[index])) for row in data)

def vehicules_vers_txt():
    vehicules = sort_vhc.recuperer_vehicules_tries_par_nom_et_prix_km()
    
    rearranged_vehicules = []
    
    for vehicule in vehicules:
        # print(f"vehicule: {vehicule}")
        vehicule = list(vehicule)
        if vehicule[2]:
            vehicule[2] = vehicule[2][:25]
        if vehicule[10]:
            vehicule[10] = vehicule[10][:25]
        # vehicule.append(vehicule.pop(1))
        rearranged_vehicules.append(vehicule)

    # Recalculate the maximum width for each column based on the rearranged data
    widths = [max_width(rearranged_vehicules, i) for i in range(len(rearranged_vehicules[0]))]

    with open("vehicls_sorted.txt", "w", encoding="utf-8") as fichier:
        # Écrire les en-têtes de colonnes en premier
        en_tetes = ["marque", "modele", "prix_km", "prix", "kilometrage", "annee", "couleur", "transmission",
                    "Roues motrices", "nom_vendeur", "adresse_vendeur", "Puissance", "Cylindrée", "carburant", "url", "ref"]
        
        # Use the 'format' method to format the headers with the maximum widths
        fichier.write("".join("{:<{}}\t".format(en_tetes[i], widths[i]) for i in range(len(en_tetes))) + "\n")

        # Write each vehicule's details to the file
        for vehicule in rearranged_vehicules:
            fichier.write("".join("{:<{}}\t".format(str(vehicule[i]), widths[i]) for i in range(len(vehicule))) + "\n")