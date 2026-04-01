# Projet SONAGED - Système de Reporting et Analyse des Données de Collecte

Architecture complète pour la collecte, le stockage et la visualisation des données de collecte des déchets de la SONAGED au Sénégal.

## 🏗️ Architecture

```
Kobo Toolbox → RAW (PostgreSQL) → MART (PostgreSQL) → Streamlit Dashboard
```

### Composants

1. **Schéma RAW** (`schema_raw.sql`) : Données brutes de KoboToolbox
2. **Schéma MART** (`schema_mart.sql`) : Données analytiques normalisées
3. **Import Kobo → RAW** (`import_kobo_via_api.py`) : Script d'import
4. **Transformation RAW → MART** (`transform_raw_to_mart.py`) : Script de transformation
5. **Dashboard Streamlit** (`streamlit_app/`) : Application de visualisation

## 📋 Prérequis

- PostgreSQL 14+ avec PostGIS 3+
- Python 3.9+
- Accès à KoboToolbox (pour exporter les données)

## 🚀 Installation

### 1. Installation de PostgreSQL et PostGIS

```bash
# Sur Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib postgis

# Sur Windows
# Télécharger depuis https://www.postgresql.org/download/windows/
```

### 2. Création de la base de données

```sql
CREATE DATABASE reporting_sonaged_db WITH ENCODING 'UTF8';
\c sonaged_db;
CREATE EXTENSION postgis;
CREATE EXTENSION "uuid-ossp";
```

### 3. Installation des schémas

**Option A : Script Python (recommandé sur Windows)**

```bash
python setup_database.py
```

Le script va :
- Créer la base de données si elle n'existe pas
- Installer les extensions (PostGIS, uuid-ossp)
- Exécuter les schémas RAW et MART
- Vérifier l'installation

**Option B : psql (si disponible dans le PATH)**

```bash
# Schéma RAW
psql -U postgres -d sonaged_db -f schema_raw.sql

# Schéma MART
psql -U postgres -d sonaged_db -f schema_mart.sql
```

### 4. Installation des dépendances Python

```bash
pip install -r requirements.txt
```

### 5. Configuration

Créer un fichier `.env` ou configurer les variables d'environnement :

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sonaged_db
DB_USER=postgres
DB_PASSWORD=votre_mot_de_passe
```

Pour Streamlit, créer `streamlit_app/.streamlit/secrets.toml` :

```toml
[db]
host = "localhost"
port = 5432
database = "sonaged_db"
user = "postgres"
password = "votre_mot_de_passe"
```

## 📥 Import des données

### Export depuis KoboToolbox

1. Se connecter à KoboToolbox
2. Aller dans "Data" → "Downloads"
3. Exporter au format JSON ou CSV

### Import vers RAW

```bash
#import  via apiKobo
import_kobo_via_api

# Format JSON
python import_kobo_to_raw.py export_kobo.json

# Format CSV
python import_kobo_to_raw.py export_kobo.csv

# Plusieurs fichiers
python import_kobo_to_raw.py *.json
```

### Transformation vers MART

```bash
# Transformer toutes les soumissions en attente
python transform_raw_to_mart.py

# Transformer une soumission spécifique
python transform_raw_to_mart.py 123
```

## 🎨 Lancement du Dashboard Streamlit

```bash
cd streamlit_app
streamlit run app.py
```

Le dashboard sera accessible sur `http://localhost:8501`

## 📊 Structure des Fichiers

```
DAKAR_REG/
├── schema_raw.sql              # Schéma RAW
├── schema_mart.sql            # Schéma MART
├── import_kobo_to_raw.py      # Import Kobo → RAW
├── transform_raw_to_mart.py   # Transformation RAW → MART
├── requirements.txt            # Dépendances Python
├── README.md                   # Ce fichier
│
├── streamlit_app/
│   ├── app.py                 # Application principale
│   ├── pages/                 # Pages du dashboard
│   │   ├── 1_Vue_d_ensemble.py
│   │   ├── 2_Analyse_temporelle.py
│   │   ├── 3_Analyse_spatiale.py
│   │   ├── 4_Personnel.py
│   │   └── 5_Concessionnaires.py
│   └── utils/
│       ├── database.py        # Connexion DB
│       └── queries.py         # Requêtes SQL
│
└── form_structure.json        # Structure du formulaire (généré)
```

## 🔄 Workflow Complet

1. **Collecte** : Données collectées via KoboToolbox sur le terrain
2. **Export** : Export des données depuis KoboToolbox (JSON/CSV)
3. **Import RAW** : `python import_kobo_to_raw.py export.json`
4. **Transformation MART** : `python transform_raw_to_mart.py`
5. **Visualisation** : Accéder au dashboard Streamlit

## 🛠️ Maintenance

### Vérifier les soumissions en attente

```sql
SELECT * FROM raw_kobo.v_submissions_pending_import;
```

### Statistiques d'import

```sql
SELECT * FROM raw_kobo.v_import_stats;
```

### Erreurs d'import

```sql
SELECT * FROM raw_kobo.import_errors 
ORDER BY occurred_at DESC;
```

## 📝 Notes

- Le schéma RAW capture **toutes** les données brutes, même les nouveaux champs
- Le schéma MART reste stable pour Streamlit
- Les modifications du formulaire Kobo n'affectent que la transformation RAW → MART
- Les données RAW sont préservées pour retraitement si nécessaire

## 🔐 Sécurité

- Ne jamais commiter les fichiers `.env` ou `secrets.toml`
- Utiliser des variables d'environnement en production
- Créer un utilisateur PostgreSQL dédié avec permissions limitées

## 📞 Support

Pour toute question ou problème, consulter la documentation PostgreSQL et PostGIS.
