from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import requests
import pandas as pd
from dotenv import load_dotenv
import os
from pymongo import MongoClient
import subprocess

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

# Fonction pour insérer des données dans MongoDB
def insert_data_to_mongo(collection, data, data_type):
    if data is not None:
        records = data.to_dict(orient='records')  # Convertir les DataFrames en liste de dictionnaires
        collection.insert_many(records)
        print(f"{data_type} insérées avec succès dans MongoDB.")
    else:
        print(f"Aucune donnée {data_type} à insérer.")

# Fonction principale de prétraitement
def preprocessing_task():
    # API OpenDataSoft eco2mix
    eco2mix_url = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-regional-tr/records"
    eco2mix_client = Eco2mixAPIClient(eco2mix_url)
    df_eco2mix = eco2mix_client.fetch_data(limit=20)
    df_eco2mix = eco2mix_client.clean_data(df_eco2mix)

    # Connexion à MongoDB
    mongo_collection = connect_to_mongodb()

    # Insertion des données dans MongoDB
    insert_data_to_mongo(mongo_collection, df_eco2mix, "eco2mix")

# Définir les arguments par défaut du DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 11, 1),  # Ajustez la date de début
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Définir le DAG
dag = DAG(
    'data_processing_dag',
    default_args=default_args,
    description='Traitement des données et insertion dans MongoDB',
    schedule_interval='0 */8 * * *',  # Exécution toutes les 8 heures
)

# Définir la tâche pour exécuter le script de prétraitement
preprocessing_task = PythonOperator(
    task_id='preprocessing_task',
    python_callable=preprocessing_task,
    dag=dag,
)

# Fonction pour exécuter le script sentiment_analysis.py
def run_sentiment_analysis():
    try:
        subprocess.run(['python3', '/home/santoudllo/Desktop/PROJETS/realtime-restaurant-insights/sentiment_analysis_kafka/sentiment_analysis.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution du script : {e}")

# Définir la tâche pour exécuter le script sentiment_analysis.py
run_sentiment_analysis_task = PythonOperator(
    task_id='run_sentiment_analysis',
    python_callable=run_sentiment_analysis,
    dag=dag,
)

# Définir les dépendances entre les tâches
preprocessing_task >> run_sentiment_analysis_task
