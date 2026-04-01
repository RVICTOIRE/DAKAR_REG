# Guide d'Installation Windows

## 🚀 Installation Rapide

### Étape 1 : Installer PostgreSQL

1. Télécharger PostgreSQL depuis : https://www.postgresql.org/download/windows/
2. Installer avec PostGIS (cocher l'option lors de l'installation)
3. Noter le mot de passe du superutilisateur `postgres`

### Étape 2 : Installer Python

1. Télécharger Python 3.9+ depuis : https://www.python.org/downloads/
2. Cocher "Add Python to PATH" lors de l'installation
3. Vérifier l'installation :
   ```powershell
   python --version
   ```

### Étape 3 : Installer les dépendances Python

```powershell
pip install -r requirements.txt
```

### Étape 4 : Configurer la base de données

**Méthode simple (recommandée) :**

```powershell
python setup_database.py
```

Le script va vous demander :
- Host PostgreSQL (par défaut : localhost)
- Port (par défaut : 5432)
- User (par défaut : postgres)
- Password (celui défini lors de l'installation)
- Database name (par défaut : sonaged_db)

Le script va automatiquement :
- ✅ Créer la base de données
- ✅ Installer PostGIS et uuid-ossp
- ✅ Créer les schémas RAW et MART
- ✅ Vérifier l'installation

### Étape 5 : Configurer les variables d'environnement

Créer un fichier `.env` à la racine du projet :

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sonaged_db
DB_USER=postgres
DB_PASSWORD=votre_mot_de_passe
```

## 🔧 Dépannage

### Erreur : "psql n'est pas reconnu"

**Solution** : Utiliser le script Python `setup_database.py` au lieu de psql directement.

### Erreur : "Module 'psycopg2' not found"

**Solution** :
```powershell
pip install psycopg2-binary
```

### Erreur : "PostGIS extension not found"

**Solution** : 
1. Vérifier que PostGIS est installé avec PostgreSQL
2. Si non, installer PostGIS séparément :
   - Télécharger depuis : https://postgis.net/windows_downloads/
   - Ou réinstaller PostgreSQL en cochant PostGIS

### Erreur de connexion à la base de données

**Vérifications** :
1. PostgreSQL est-il démarré ? (Services Windows → PostgreSQL)
2. Le mot de passe est-il correct ?
3. Le port 5432 est-il libre ?

### Tester la connexion manuellement

```python
import psycopg2
conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='postgres',
    user='postgres',
    password='votre_mot_de_passe'
)
print("✓ Connexion réussie !")
conn.close()
```

## ✅ Vérification de l'installation

Après avoir exécuté `setup_database.py`, vous devriez voir :

```
✅ Installation terminée avec succès !

Prochaines étapes :
1. Configurer les variables d'environnement (.env)
2. Importer des données : python import_kobo_to_raw.py export.json
3. Transformer vers MART : python transform_raw_to_mart.py
4. Lancer Streamlit : cd streamlit_app && streamlit run app.py
```

## 📝 Prochaines Étapes

1. **Exporter des données depuis Kobo** (format JSON ou CSV)
2. **Importer vers RAW** :
   ```powershell
   python import_kobo_to_raw.py export_kobo.json
   ```
3. **Transformer vers MART** :
   ```powershell
   python transform_raw_to_mart.py
   ```
4. **Lancer Streamlit** :
   ```powershell
   cd streamlit_app
   streamlit run app.py
   ```

## 🆘 Besoin d'aide ?

- Vérifier les logs d'erreur dans la console
- Consulter la documentation PostgreSQL
- Vérifier que tous les fichiers SQL sont présents dans le répertoire
