# Projet Data Pipeline avec Apache Airflow et MongoDB

## Technologies Utilisées

### Langages
- ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

### Frameworks et Outils de Développement
- ![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-017CEE?style=for-the-badge&logo=apache-airflow&logoColor=white)
- ![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
- ![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)

### Bases de Données
- ![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white)
- Pour le stockage des données après ingestion et transformation.

### Conteneurisation et Déploiement
- **Docker Compose** - Pour gérer les services comme MongoDB et Airflow dans des conteneurs Docker.

### Outils de Visualisation
- **Airflow Web UI** - Pour superviser et visualiser l'exécution des pipelines.

## Objectif du Projet

Le projet a pour but de construire un **pipeline de données automatisé** qui récupère, transforme et charge des données provenant de deux APIs externes (**écomix** et **Hubeau**) dans une base de données **MongoDB**. Ce pipeline permet d'automatiser la collecte et l'intégration des données en temps réel et consolidées.

Les principaux objectifs sont :
- **Automatisation des collectes de données** : Extraction de données provenant d'APIs avec une fréquence définie (par exemple, horaire ou quotidienne) pour garantir la fraîcheur des informations.
- **Centralisation des données** : Stocker les données collectées dans **MongoDB** pour une consultation facile et une analyse ultérieure.
- **Orchestration des tâches** : Utiliser **Apache Airflow** pour gérer l'exécution et la planification des tâches dans le pipeline.

## APIs Utilisées

### 1. **API écomix (éCO2mix)**
   - **Objectif** : Fournir des données régionales "temps réel" sur la consommation et la production d'énergie en France, issues de l'application éCO2mix. Ce jeu de données est mis à jour toutes les heures et permet de suivre les mesures des télémesures des ouvrages, complétées par des forfaits et estimations.
   - **Données extraites** :
     - **Consommation réalisée** à l'échelle régionale.
     - **Production par filière énergétique** (ex. : énergies renouvelables, nucléaire, etc.).
     - **Consommation des pompes dans les Stations de Transfert d'Énergie par Pompage (STEP)**.
     - **Solde des échanges physiques avec les régions limitrophes**.
   - **Fréquence de mise à jour** : Ces données sont rafraîchies une fois par heure, mais elles sont remplacées par des données "consolidées" au mois suivant et par des données "définitives" au milieu de l'année suivante.
   - **Note importante** : Un quota de 50 000 appels API par utilisateur et par mois est en place pour limiter les demandes excessives. Les données sont disponibles via cette [API](https://opendata.reseaux-energies.fr/explore/dataset/eco2mix-regional-cons-def).

### 2. **API Hubeau (Prélèvements en Eau)**
   - **Objectif** : Fournir des données sur les prélèvements en eau en France, utilisées pour la gestion des redevances par les agences et offices de l'eau. Ces données sont essentielles pour suivre les volumes d'eau prélevés dans différents usages (agricoles, industriels, etc.).
   - **Spécifications des Données** :
     - Les volumes prélevés pour des usages exonérés de redevance ne sont **pas connus**.
     - Les petits volumes de prélèvement (inférieurs à 10 000 m³) **ne sont pas déclarés** dans le cadre des redevances pour prélèvement.
     - Pour le département de **Mayotte**, les données sont fournies par la **DEAL** (Direction de l'Environnement, de l'Aménagement et du Logement).
   - **Référentiel** :
     - Les données reposent sur un **référentiel des ouvrages et des points de prélèvement**. Un **ouvrage de prélèvement** représente un ensemble de dispositifs de captage, de stockage et de canalisation d'eau, connecté à une ressource en eau spécifique.
     - Un **point de prélèvement** désigne le lieu de connexion physique entre la ressource en eau et un dispositif de captage d'eau. Un point de prélèvement est attaché à un ouvrage spécifique.
     - Le **référentiel des communes et départements** utilisé est basé sur les données de la **BNPE** (Base Nationale des Prélèvements en Eau).
   - **Données extraites** :
     - **Volumes prélevés** pour différents usages (agriculture, industrie, etc.).
     - **Informations sur les ouvrages et les points de prélèvement** (localisation, type de prélèvement).
     - **Historique des volumes de prélèvements** sur des périodes définies.
   - **Fréquence de mise à jour** : Ces données sont mises à jour régulièrement et peuvent être récupérées pour des périodes de prélèvement spécifiques.
   - **Accès API** : [API Hubeau - Prélèvements en Eau](https://hubeau.eaufrance.fr/)

## Architecture du Projet

```
├── dags/
│   └── economix_hubeau_to_mongo.py   # Définition du pipeline Airflow
├── script/
│   └── entrypoint.sh                 # Script pour initialiser l'environnement Airflow
│   └── preprocessing.py              # Script de prétraitement des données
├── docker-compose.yml                # Configuration des services Docker (Airflow, MongoDB)
├── requirements.txt                  # Dépendances Python du projet
├── .env                              # Variables d'environnement (API, MongoDB)
```

## Prérequis

Avant de commencer, assurez-vous d'avoir installé les éléments suivants :

- **Docker**
- **Docker Compose**
- **Python 3.10+**

## Installation

1. **Clonez le dépôt** :
   ```bash
   git clone https://github.com/username/projet-airflow-mongodb.git
   cd projet-airflow-mongodb
   ```

2. **Créez un fichier `.env`** à la racine du projet et renseignez les variables nécessaires pour connecter les APIs et MongoDB.

   Exemple de contenu pour le fichier `.env` :
   ```ini
   MONGO_URI=mongodb://localhost:27017
   ECONOMIX_API_KEY="******"
   HUBEAU_API_KEY="******"
   ```

3. **Lancez les services Docker** :
   ```bash
   docker-compose up -d
   ```

   Cela démarrera **Airflow**, **MongoDB** et les autres services nécessaires.

4. **Accédez à l'interface Airflow** :  
   [http://localhost:8081](http://localhost:8081)

## Développement et Configuration des DAGs

Le fichier `economix_hubeau_to_mongo.py` définit le pipeline **Airflow** qui récupère les données des APIs **écomix** et **Hubeau**, les transforme et les insère dans **MongoDB**. Ce pipeline sera exécuté à intervalles réguliers, par exemple toutes les heures, pour assurer que les données restent fraîches.

Les tâches du pipeline incluent :
- **Extraction des données** depuis les APIs **écomix** (éCO2mix) et **Hubeau**.
- **Transformation des données** : Nettoyage et prétraitement des données extraites.
- **Chargement des données** dans **MongoDB**.

## Fonctionnalités du Projet

### Collecte des Données
Le pipeline collecte des données de deux APIs principales :
- **Données de consommation et de production d'énergie** via l'API **écomix (éCO2mix)**.
- **Données sur les prélèvements en eau** via l'API **Hubeau**.

### Transformation des Données
Les données collectées peuvent nécessiter des étapes de prétraitement, comme :
- Nettoyage des données (suppression des doublons, gestion des valeurs manquantes).
- Enrichissement des données avec des informations supplémentaires (par exemple, ajout de la date de collecte).

### Orchestration avec Airflow
**Apache Airflow** orchestre l'exécution du pipeline en gérant les dépendances entre les différentes tâches, telles que l'extraction des données, la transformation et le chargement dans MongoDB.

### Visualisation des Données
Une fois les données chargées dans **MongoDB**, des outils de visualisation peuvent être utilisés pour analyser les données, par exemple, en utilisant **Kibana** ou en effectuant des analyses directement dans des notebooks **Jupyter**.

## Déploiement avec Docker

Le projet utilise **Docker Compose** pour déployer l'ensemble des services dans des conteneurs Docker. Cela inclut **Airflow**, **MongoDB** et d'autres outils nécessaires. Le fichier `docker-compose.yml` permet de configurer et de démarrer tous les services.

---

## Conclusion

Ce projet permet de centraliser les données provenant de deux APIs : **écomix (éCO2mix)** pour les

 données de consommation et production d'énergie, et **Hubeau** pour les données sur les prélèvements en eau. Grâce à **Apache Airflow**, le pipeline de données est orchestré et automatisé, garantissant la collecte et l'insertion des données à intervalles réguliers dans **MongoDB**. Ce projet est conçu pour être extensible, permettant d'ajouter facilement de nouvelles sources de données et d'analyses au fur et à mesure des besoins.
