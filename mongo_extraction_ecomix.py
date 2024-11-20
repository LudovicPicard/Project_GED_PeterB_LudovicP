import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv
import pandas as pd

# Charger les variables d'environnement
load_dotenv()

# Connexion à MongoDB
def connect_to_mongodb():
    print("Connexion à MongoDB...")
    try:
        mongo_url = os.getenv("MONGO_URL").replace("<db_password>", os.getenv("MONGO_PASSWORD"))
        client = MongoClient(mongo_url)
        db = client[os.getenv("MONGO_DBNAME")]
        collection = db['Data.Data']  # Connexion à la collection 'Data.Data'
        print("Connexion à MongoDB réussie")
        return collection
    except Exception as e:
        print(f"Erreur de connexion à MongoDB : {e}")
        return None

# Nettoyage des données (sans suppression des champs location et geo_point)
def clean_data(data):
    print("Nettoyage des données...")
    for i, doc in enumerate(data):
        doc.pop("_id", None)  # Supprimer le champ _id
        doc["index"] = i  # Ajouter un identifiant unique basé sur l'index du document
    return data

# Extraction des données et sauvegarde
def extract_data_from_mongo(collection, output_file="output_data.json", output_format="json"):
    print("Extraction des données depuis MongoDB...")
    try:
        cursor = collection.find()
        data = list(cursor)
        data = clean_data(data)  # Appliquer le nettoyage des données

        # Sauvegarder les données en fonction du format
        if output_format == "json":
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"Données exportées au format JSON dans {output_file}")
        elif output_format == "csv":
            # Utiliser pandas pour convertir la liste de documents MongoDB en DataFrame
            df = pd.DataFrame(data)

            # Vérifier s'il y a des colonnes imbriquées et aplatir ces colonnes
            for col in df.columns:
                if isinstance(df[col].iloc[0], dict):  # Si la colonne contient des dictionnaires
                    df = df.join(pd.json_normalize(df[col])).drop(col, axis=1)
            
            df.to_csv(output_file, index=False, encoding="utf-8")
            print(f"Données exportées au format CSV dans {output_file}")
        else:
            print("Format de sortie non pris en charge.")
    except Exception as e:
        print(f"Erreur lors de l'extraction des données : {e}")

# Main
if __name__ == "__main__":
    # Connexion à MongoDB
    mongo_collection = connect_to_mongodb()
    if mongo_collection is None:
        print("La collection MongoDB n'a pas été trouvée.")
        exit(1)

    # Extraction des données
    output_file = "output_data_Data.csv"  # Change en "output_data.json" pour un JSON
    output_format = "csv"  # Change en "json" pour un JSON
    extract_data_from_mongo(mongo_collection, output_file, output_format)
