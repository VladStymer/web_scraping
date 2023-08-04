import sqlite3
import sort_vhc

def vehicle_exists(conn, ref):
    """Vérifie si un véhicule existe déjà dans la base de données."""
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM vehicules WHERE ref=?', (ref,))
    return cursor.fetchone() is not None

def prix_km():
    # Connexion à la base de données
    conn = sqlite3.connect('vehicules.db')

    # Récupération des données du véhicule  
    data = recuperer_vehicules()

    # Vérification de l'existence du véhicule dans la base de données
    if not vehicle_exists(conn, data["ref"]):
        # Calcul du rapport prix/km
        price_per_km = sort_vhc.run_interpret(data)
        data["price_per_km"] = price_per_km

        # Insertion du véhicule
        ajouter_vehicule(conn, data)

        # Calcul et mise à jour de la moyenne générale
        # average = calculate_average_for_model(conn, data["brand"], data["model"])
        # update_average_for_model(conn, data["brand"], data["model"], average)



def ajouter_vehicule(data):
    ref = data["Ref"]
    marque = data["marque"]
    modele = data["modele"]
    annee = data["annee"]
    couleur = data["couleur"]
    prix_km = data["prix_km"]
    prix = data["prix"]

    conn = sqlite3.connect('vehicules.db')
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO vehicules (ref, marque, modele, annee, couleur, prix_km, prix)
    VALUES (?, ?, ?, ?)
    ''', (ref, marque, modele, annee, couleur, prix_km, prix))

    conn.commit()
    conn.close()

def mettre_a_jour_vehicule(data):
    if not vehicle_exists():
        print(f"Le véhicule {data['Ref']} n'existe pas dans la base de données.")
        return
    ref = data["Ref"]
    marque = data["marque"]
    modele = data["modele"]
    annee = data["annee"]
    couleur = data["couleur"]
    prix_km = data["prix_km"]
    prix = data["prix"]

    conn = sqlite3.connect('vehicules.db')
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE vehicules
    SET marque = ?, modele = ?, annee = ?, couleur = ?, prix_km = ?, prix = ?
    WHERE ref = ?
    ''', (marque, modele, annee, couleur, prix_km, prix, ref))

    conn.commit()
    conn.close()


def recuperer_vehicules():
    conn = sqlite3.connect('vehicules.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM vehicules')
    tous_les_vehicules = cursor.fetchall()

    conn.close()
    return tous_les_vehicules

def init_db():
    # Connecter à la base de données (ou la créer si elle n'existe pas)
    conn = sqlite3.connect('vehicules.db')
    cursor = conn.cursor()

    # Créer une table pour les véhicules
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vehicules (
        id INTEGER PRIMARY KEY,
        ref TEXT,
        marque TEXT,
        modele TEXT,
        annee INTEGER,
        couleur TEXT,
        transmission TEXT,
        Roues motrices TEXT,
        kilometrage INTEGER,
        prix_km INTEGER,
        prix INTEGER,
        Nom du vendeur TEXT,
        Adresse du vendeur TEXT,
        Première mise en circulation TEXT,
        Cylindrée INTEGER,
        Type de carburant TEXT
    )
    ''')

    conn.commit()
    conn.close()

def main(one_page_of_vhc_data):
    init_db()
    for data in one_page_of_vhc_data:
        if vehicle_exists(data["Ref"]):
            mettre_a_jour_vehicule(data)
        else:
            ajouter_vehicule(data)
    print(recuperer_vehicules())




if __name__ == "__main__":
    main()
