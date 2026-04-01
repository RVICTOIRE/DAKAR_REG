import os
import requests
import psycopg2
from psycopg2.extras import Json
from config import DB_CONFIG, KOBO_CONFIG

# ----------------------------
# ⚡ Connexion à PostgreSQL
# ----------------------------
try:
    conn = psycopg2.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        dbname=DB_CONFIG["dbname"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"]
    )
    cur = conn.cursor()
    print("✓ Connexion à la base de données établie")
except Exception as e:
    raise Exception(f"Erreur de connexion à la DB : {e}")

# ----------------------------
# 🔗 URL API Kobo
# ----------------------------
KOBO_API = f"https://kc.kobotoolbox.org/api/v2/assets/{KOBO_CONFIG['form_uid']}/data/"

# ----------------------------
# 📥 Récupération des soumissions depuis Kobo avec pagination
# ----------------------------
submissions = []
url = KOBO_API
while url:
    try:
        response = requests.get(url, headers={"Authorization": f"Token {KOBO_CONFIG['api_key']}"} )
        response.raise_for_status()
        data = response.json()
        submissions.extend(data.get("results", []))
        url = data.get("next")  # Pagination automatique
    except Exception as e:
        raise Exception(f"Erreur API Kobo : {e}")

print(f"📊 {len(submissions)} soumission(s) récupérée(s) depuis Kobo")

# ----------------------------
# 🔄 Import dans la table RAW
# ----------------------------
imported = 0
skipped = 0
errors = 0

for sub in submissions:
    if isinstance(sub, str):
        # Parfois la liste contient des strings -> ignorer
        skipped += 1
        continue

    kobo_id = sub.get("_id")
    if not kobo_id:
        print("✗ Soumission sans _id, ignorée")
        skipped += 1
        continue

    try:
        cur.execute(
            """
            INSERT INTO raw_kobo.submissions (kobo_submission_id, form_data)
            VALUES (%s, %s)
            ON CONFLICT (kobo_submission_id) DO NOTHING
            """,
            (kobo_id, Json(sub))
        )
        imported += 1
        print(f"✓ Soumission {kobo_id} importée")
    except Exception as e:
        print(f"✗ Erreur import {kobo_id} : {e}")
        errors += 1

# ----------------------------
# ✅ Commit et fermeture
# ----------------------------
conn.commit()
cur.close()
conn.close()
print("=================================================")
print(f"✓ Import terminé : {imported} importée(s), {skipped} ignorée(s), {errors} erreur(s)")
print("=================================================")
