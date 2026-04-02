# config.py
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'dbname': os.getenv('DB_NAME', 'neondb'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),
    'options': '-c client_encoding=UTF8'
}

RAW_SCHEMA = "raw_kobo"
MART_SCHEMA = "public"

SQL_FILES = {
    "raw": BASE_DIR / "schema_raw.sql",
    "mart": BASE_DIR / "schema_mart.sql"
}

# ----------------------------
# Configuration KoboToolbox
# ----------------------------
KOBO_CONFIG = {
    "api_key": os.getenv('KOBO_API_KEY', "625acaaa5294d5a5bb447958e276eabf4f636932"),
    "form_uid": os.getenv('KOBO_FORM_UID', "aAKLQa7aKQuJZ6wANBa3iM")
}
