from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import requests
import pandas as pd
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from elasticsearch import Elasticsearch

# Charger les variables d'environnement
load_dotenv()

# Arguments par défaut pour le DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 11, 1),
    'retries': 3,  # Nombre de retries en cas d'échec
    'retry_delay': timedelta(minutes=5),
}

# Définition du DAG
dag = DAG(
    'Hubeau_vers_mongo_dag',  # Renommage du DAG
    default_args=default_args,
    description='Pipeline API Hubeau vers MongoDB avec vérifications et logs',
    schedule_interval='@hourly',  # Exécution toutes les heures
)

# Connexion à MongoDB
def connect_to_mongodb():
    print("Étape : Connexion à MongoDB")
    try:
        mongo_url = os.getenv("MONGO_URL").replace("<db_password>", os.getenv("MONGO_PASSWORD"))
        client = MongoClient(mongo_url)
        db = client[os.getenv("MONGO_DBNAME")]
        collection = db['Data.Data']
        print("Connexion à MongoDB réussie")
        return collection
    except Exception as e:
        print(f"Erreur de connexion à MongoDB : {e}")
        return None

# Classe pour gérer l'API Hubeau
class HubeauAPIClient:
    def __init__(self, api_url):
        self.api_url = api_url

    def fetch_data(self, codes_insee, size=50):
        print(f"Étape : Récupération des données Hubeau pour les communes INSEE : {codes_insee}")
        try:
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
        print("Étape : Nettoyage des données Hubeau")
        if df is not None:
            df.fillna(0, inplace=True)  # Remplacer les NaN par 0
            print("Données Hubeau nettoyées.")
            return df
        else:
            print("Aucune donnée Hubeau à nettoyer.")
            return None

# Insertion des données dans MongoDB
def insert_data_to_mongo(collection, data, data_type):
    print(f"Étape : Insertion des données {data_type} dans MongoDB")
    if data is not None:
        try:
            records = data.to_dict(orient='records')  # Convertir les DataFrames en liste de dictionnaires
            collection.insert_many(records)
            print(f"{data_type} insérées avec succès dans MongoDB.")
        except Exception as e:
            print(f"Erreur lors de l'insertion des données {data_type} dans MongoDB : {e}")
    else:
        print(f"Aucune donnée {data_type} à insérer.")

# Fonction principale du pipeline
def run_pipeline():
    print("Début du pipeline API vers MongoDB")

    # Connexion à MongoDB
    mongo_collection = connect_to_mongodb()
    if not mongo_collection:
        print("Erreur critique : Connexion MongoDB échouée, arrêt du pipeline.")
        return

    # Initialisation du client Hubeau
    hubeau_url = os.getenv("API_URL")
    hubeau_client = HubeauAPIClient(hubeau_url)
    codes_insee = ['35002', '35003', '35004', '35005', '35006', '35007', '35008', '35009', '35010',
                   '35011', '35012', '35013', '35014', '35015', '35016', '35017', '35018', '35019', '35020']

    # Récupération et nettoyage des données Hubeau
    df_hubeau = hubeau_client.fetch_data(codes_insee=codes_insee, size=20)
    df_hubeau = hubeau_client.clean_data(df_hubeau)

    # Insertion des données Hubeau dans MongoDB
    insert_data_to_mongo(mongo_collection, df_hubeau, "Hubeau")

    print("Pipeline terminé avec succès.")

# Définir la tâche pour exécuter le pipeline complet
run_pipeline_task = PythonOperator(
    task_id='run_pipeline',
    python_callable=run_pipeline,
    dag=dag,
)
