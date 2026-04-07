import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config import DB_CONFIG, SQL_FILES

DB_NAME = DB_CONFIG["dbname"]


def create_database():
    print("\n🔧 Création de la base de données...")

    conn = psycopg2.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database="postgres"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
    if not cur.fetchone():
        cur.execute(f'CREATE DATABASE "{DB_NAME}"')
        print(f"✓ Base créée : {DB_NAME}")
    else:
        print(f"✓ Base déjà existante : {DB_NAME}")

    cur.close()
    conn.close()


def setup_extensions():
    print("\n🔧 Installation des extensions...")
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    cur.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    conn.commit()
    cur.close()
    conn.close()
    print("✓ Extensions installées")


def execute_sql_file(path):
    print(f"📄 Exécution {path.name}")
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    with open(path, "r", encoding="utf-8") as f:
        cur.execute(f.read())

    conn.commit()
    cur.close()
    conn.close()
    print(f"✓ {path.name} exécuté")


def main():
    print("=" * 60)
    print("🚀 INSTALLATION BASE SONAGED")
    print("=" * 60)

    create_database()
    setup_extensions()
    execute_sql_file(SQL_FILES["raw"])
    execute_sql_file(SQL_FILES["mart"])

    print("\n✅ INSTALLATION TERMINÉE AVEC SUCCÈS")


if __name__ == "__main__":
    main()
