# Projet Data Pipeline avec Apache Airflow, MongoDB et Elasticsearch

## Technologies Utilisées

### Langages
- ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

### Frameworks et Outils de Développement
- ![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-017CEE?style=for-the-badge&logo=apache-airflow&logoColor=white)
- ![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
- ![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)

### Bases de Données
- ![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white)  
  Pour le stockage des données après ingestion et transformation.
- ![Elasticsearch](https://img.shields.io/badge/Elasticsearch-005571?style=for-the-badge&logo=elasticsearch&logoColor=white)  
  Pour l'indexation et la visualisation des données collectées.

### Conteneurisation et Déploiement
- **Docker Compose** - Pour gérer les services comme MongoDB, Airflow et Elasticsearch dans des conteneurs Docker.

### Outils de Visualisation
- **Airflow Web UI** - Pour superviser et visualiser l'exécution des pipelines.
- **Kibana** - Pour créer des dashboards interactifs à partir des données indexées dans Elasticsearch.

## Objectif du Projet

Le projet a pour but de construire un **pipeline de données automatisé** qui récupère, transforme et charge des données provenant de deux APIs externes (**écomix** et **Hubeau**) dans une base de données **MongoDB**. Ces données sont ensuite exportées vers **Elasticsearch** pour permettre des analyses avancées et des visualisations interactives via **Kibana**.

Les principaux objectifs sont :
- **Automatisation des collectes de données** : Extraction de données provenant d'APIs avec une fréquence définie (par exemple, horaire ou quotidienne) pour garantir la fraîcheur des informations.
- **Centralisation des données** : Stocker les données collectées dans **MongoDB** pour une consultation facile et une analyse ultérieure.
- **Indexation et visualisation** : Importer les données dans **Elasticsearch** pour faciliter la création de dashboards et d'analyses en temps réel.
- **Orchestration des tâches** : Utiliser **Apache Airflow** pour gérer l'exécution et la planification des tâches dans le pipeline.

---

## Fonctionnalités du Projet

### Collecte des Données
Le pipeline collecte des données de deux APIs principales :
- **Données de consommation et de production d'énergie** via l'API **écomix (éCO2mix)**.
- **Données sur les prélèvements en eau** via l'API **Hubeau**.

### Transformation des Données
Les données collectées subissent des étapes de prétraitement, telles que :
- Nettoyage des données (suppression des doublons, gestion des valeurs manquantes).
- Enrichissement des données (ajout d'informations contextuelles ou calculs dérivés).

### Chargement et Indexation
1. **Chargement dans MongoDB** :  
   Après transformation, les données sont chargées dans **MongoDB**, où elles sont stockées de manière structurée.
2. **Indexation dans Elasticsearch** :  
   Les données consolidées de MongoDB sont ensuite importées dans **Elasticsearch**, où elles sont indexées pour permettre des requêtes rapides et l'analyse des données.

### Visualisation avec Kibana
Les données indexées dans **Elasticsearch** peuvent être explorées et visualisées à l'aide de **Kibana**. Cela permet de :
- Créer des dashboards interactifs.
- Suivre des tendances sur les volumes de consommation énergétique ou les prélèvements en eau.
- Effectuer des analyses comparatives et générer des rapports.

---

## Architecture du Projet

```
├── dags/
│   └── API_vers_mongo.py   # Définition du pipeline Airflow
├── script/
│   └── entrypoint.sh                 # Script pour initialiser l'environnement Airflow
│   └── preprocessing.py              # Script de prétraitement des données
│   └── mongo_to_elasticsearch.py     # Script pour l'importation des données de MongoDB vers Elasticsearch
├── docker-compose.yml                # Configuration des services Docker (Airflow, MongoDB, Elasticsearch)
├── requirements.txt                  # Dépendances Python du projet
├── .env                              # Variables d'environnement (API, MongoDB, Elasticsearch)
```

---

## Déploiement avec Docker

Le projet utilise **Docker Compose** pour déployer l'ensemble des services dans des conteneurs Docker. Cela inclut :
- **Apache Airflow** : Orchestration des pipelines.
- **MongoDB** : Stockage des données collectées.
- **Elasticsearch** : Indexation des données pour la recherche et l'analyse.
- **Kibana** : Visualisation des données indexées dans Elasticsearch.

Lancez tous les services via la commande suivante :

```bash
docker-compose up -d
```

Accédez ensuite à :
- **Interface Airflow** : [http://localhost:8081](http://localhost:8081)
- **Interface Kibana** : [http://localhost:5601](http://localhost:5601)

---

## Conclusion

Ce projet propose un pipeline robuste qui automatise la collecte, la transformation et le stockage des données dans **MongoDB**, tout en rendant ces données accessibles pour des analyses avancées via **Elasticsearch** et **Kibana**. Grâce à cette architecture, il est possible d'explorer des données complexes à travers des visualisations interactives et d'étendre facilement le pipeline pour intégrer de nouvelles sources de données.
