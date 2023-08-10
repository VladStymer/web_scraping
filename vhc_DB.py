import os
import export
import sqlite3
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()
debug_mode = os.getenv("DEBUG", "False").lower() == "true"
WARNING_COLOR = os.getenv("WARNING_COLOR").encode().decode('unicode_escape')
OK_COLOR = os.getenv("OK_COLOR").encode().decode('unicode_escape')
ERROR_COLOR = os.getenv("ERROR_COLOR").encode().decode('unicode_escape')
RESET_COLOR = os.getenv("RESET_COLOR").encode().decode('unicode_escape')

class DatabaseContext:
    def __enter__(self):
        self.conn = sqlite3.connect('vehicules.db')
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.conn.commit()
        else:
            pass
        self.conn.close()

def init_db():
     with DatabaseContext() as cursor:
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicules (
            id INTEGER PRIMARY KEY,
            marque TEXT,
            modele TEXT,
            prix_km INTEGER,
            prix INTEGER,
            kilometrage INTEGER,
            annee INTEGER,
            couleur TEXT,
            transmission TEXT,
            Roues_motrices TEXT,
            nom_vendeur TEXT,
            adresse_vendeur TEXT,
            Puissance TEXT,
            Cylindrée INTEGER,
            carburant TEXT,
            url TEXT,
            ref TEXT,
            vhc_type TEXT
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS historique (
            id INTEGER PRIMARY KEY,
            vehicule_id INTEGER,
            prix INTEGER,
            km INTEGER,
            date TEXT,
            FOREIGN KEY (vehicule_id) REFERENCES vehicules(id)
        )
        ''')

def vehicle_exists(ref):
    with DatabaseContext() as cursor:
        cursor.execute('SELECT * FROM vehicules WHERE ref=?', (ref,))
        return cursor.fetchone() is not None

def ajouter_historique(vehicule_id, prix, km, date):
    with DatabaseContext() as cursor:
        cursor.execute('''
        INSERT INTO historique (vehicule_id, prix, km, date)
        VALUES (?, ?, ?, ?)
        ''', (vehicule_id, prix, km, date))

def ajouter_vehicule(data):

    marque = data["name"]
    try:
        modele = data["Type"][:25]
    except:
        modele = None
    prix_km = data["prix_km"]
    prix = data["Price"]
    km = data["Mileage"]
    année = data["First Registration Date"]
    color = data["Color"]
    transmission = data["Transmission"]
    wheel_drive = data["Wheel Drive"]
    nom_vendeur = data["Dealer Name"]
    adresse_vendeur = data["Dealer Address"]
    # puissance = data["Engine Power"]
    puissance = "9"
    Cylindrée = data["Cm3"]
    carburant = data["Fuel Type"]
    url = data["URL"]
    ref = data["Ref"]

    with DatabaseContext() as cursor:
        cursor.execute('''
        INSERT INTO vehicules (marque, modele, prix_km, prix, kilometrage, annee, couleur, transmission, Roues_motrices, nom_vendeur, adresse_vendeur, Puissance, Cylindrée, carburant, url, ref)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (marque, modele, prix_km, prix, km, année, color, transmission, wheel_drive, nom_vendeur, adresse_vendeur, puissance, Cylindrée, carburant, url, ref))

def recuperer_vehicules():
    with DatabaseContext() as cursor:
        cursor.execute('SELECT * FROM vehicules')
        tous_les_vehicules = cursor.fetchall()

        return tous_les_vehicules


def compare_data_of_same_vhc(data):
    date = datetime.today().strftime('%Y-%m-%d')
    with DatabaseContext() as cursor:
        cursor.execute('SELECT id, ref FROM vehicules WHERE ref=?', (data["Ref"],))
        vehicule = cursor.fetchone()

        if vehicule:
            ajouter_historique(vehicule[0], data["Price"], data["Mileage"], date)

def main(one_page_of_vhc_data):
    print(WARNING_COLOR + "Lancement de vhc_DB..." + RESET_COLOR)
    init_db()
    if not one_page_of_vhc_data:
        print(ERROR_COLOR + "vhc_DB.py -> one_page_of_vhc_data is empty" + RESET_COLOR)
        return
    # print(f"DATA: {one_page_of_vhc_data}")
    for data in one_page_of_vhc_data:
        # print(f"vhc_DB.py -> data: {data}")
        if vehicle_exists(data["Ref"]):
            # print("vehicle_exists")
            compare_data_of_same_vhc(data)
        else:
            # print("ajouter_vehicule")
            ajouter_vehicule(data)
    # print(recuperer_vehicules())
    # print(recuperer_vehicules()[1])
    # print(recuperer_vehicules()[2][0])

    export.vehicules_vers_txt()
    print(OK_COLOR + "vhc_DB done!" + RESET_COLOR)

def run_database(one_page_of_vhc_data):
    main(one_page_of_vhc_data)

if __name__ == "__main__":
    main()
