import requests
import pandas as pd
from dotenv import load_dotenv
import os
from pymongo import MongoClient
 
# Charger les variables d'environnement
load_dotenv()
 
# Connexion à MongoDB
def connect_to_mongodb():
    mongo_url = os.getenv("MONGO_URL").replace("<db_password>", os.getenv("MONGO_PASSWORD"))
    client = MongoClient(mongo_url)
    db = client[os.getenv("MONGO_DBNAME")]
    collection = db['Data.Data']
    return collection
 
# Classe pour gérer l'API eco2mix
class Eco2mixAPIClient:
    def __init__(self, api_url):
        self.api_url = api_url
 
    def fetch_data(self, limit=20, region="Bretagne"):
        try:
            print(f"Récupération des données eco2mix pour la région {region} avec une limite de {limit}")
            params = {'limit': limit, 'refine': f"libelle_region:{region}"}
            response = requests.get(self.api_url, params=params)
            if response.status_code == 200:
                data = response.json()
                if 'results' in data:
                    df = pd.json_normalize(data['results'])
                    print("Données eco2mix récupérées avec succès !")
                    return df
                else:
                    print("Aucun enregistrement trouvé pour eco2mix.")
                    return None
            else:
                print(f"Erreur lors de la récupération des données eco2mix : {response.status_code}")
                return None
        except Exception as e:
            print(f"Erreur lors de la récupération des données eco2mix : {e}")
            return None
 
    def clean_data(self, df):
        if df is not None:
            df.fillna(0, inplace=True)  # Remplacer les NaN par 0
            print("Données eco2mix nettoyées.")
            return df
        else:
            print("Aucune donnée eco2mix à nettoyer.")
            return None
 
 
# Classe pour gérer l'API Hubeau
class HubeauAPIClient:
    def __init__(self, api_url):
        self.api_url = api_url
 
    def fetch_data(self, codes_insee, size=20):
        try:
            print(f"Récupération des données Hubeau pour les communes INSEE : {codes_insee}")
            params = {
                'code_commune_insee': ','.join(codes_insee),
                'size': size,
                'format': 'json',
                'pretty': 'true'
            }
            response = requests.get(self.api_url, params=params)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    df = pd.json_normalize(data['data'])
                    print("Données Hubeau récupérées avec succès !")
                    return df
                else:
                    print("Aucun enregistrement trouvé pour Hubeau.")
                    return None
            else:
                print(f"Erreur lors de la récupération des données Hubeau : {response.status_code}")
                return None
        except Exception as e:
            print(f"Erreur lors de la récupération des données Hubeau : {e}")
            return None
 
    def clean_data(self, df):
        if df is not None:
            df.fillna(0, inplace=True)  # Remplacer les NaN par 0
            print("Données Hubeau nettoyées.")
            return df
        else:
            print("Aucune donnée Hubeau à nettoyer.")
            return None
 
# Fonction pour insérer des données dans MongoDB
def insert_data_to_mongo(collection, data, data_type):
    if data is not None:
        records = data.to_dict(orient='records')  # Convertir les DataFrames en liste de dictionnaires
        collection.insert_many(records)
        print(f"{data_type} insérées avec succès dans MongoDB.")
    else:
        print(f"Aucune donnée {data_type} à insérer.")
 
# Fonction principale
def main():
    # API OpenDataSoft eco2mix
    eco2mix_url = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-regional-tr/records"
    eco2mix_client = Eco2mixAPIClient(eco2mix_url)
    df_eco2mix = eco2mix_client.fetch_data(limit=20)
    df_eco2mix = eco2mix_client.clean_data(df_eco2mix)
 
    # API Hubeau - Prélevements d'eau
    hubeau_url = os.getenv("API_URL")
    hubeau_client = HubeauAPIClient(hubeau_url)
    codes_insee = ['35002', '35003', '35004', '35005', '35006', '35007', '35008', '35009', '35010',
                   '35011', '35012', '35013', '35014', '35015', '35016', '35017', '35018', '35019', '35020']
    df_hubeau = hubeau_client.fetch_data(codes_insee=codes_insee, size=20)
    df_hubeau = hubeau_client.clean_data(df_hubeau)
 
    # Connexion à MongoDB
    mongo_collection = connect_to_mongodb()
 
    # Insertion des données dans MongoDB
    insert_data_to_mongo(mongo_collection, df_eco2mix, "eco2mix")
    insert_data_to_mongo(mongo_collection, df_hubeau, "Hubeau")
 
 
if __name__ == "__main__":
    main()
 
 