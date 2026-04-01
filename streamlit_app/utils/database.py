"""
Module de connexion à la base de données PostgreSQL
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
import os
import streamlit as st


@st.cache_resource
def get_connection():
    """
    Obtient une connexion à la base de données PostgreSQL
    Utilise le cache de Streamlit pour réutiliser la connexion
    """
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', st.secrets.get('db_host', 'localhost')),
            port=os.getenv('DB_PORT', st.secrets.get('db_port', '5432')),
            database=os.getenv('DB_NAME', st.secrets.get('db_name', 'reporting_sonaged_db')),
            user=os.getenv('DB_USER', st.secrets.get('db_user', 'postgres')),
            password=os.getenv('DB_PASSWORD', st.secrets.get('db_password', ''))
        )
        return conn
    except Exception as e:
        st.error(f"Erreur de connexion à la base de données : {e}")
        st.stop()


def execute_query(query: str, params: tuple = None) -> pd.DataFrame:
    """
    Exécute une requête SQL et retourne un DataFrame pandas
    """
    conn = get_connection()
    try:
        df = pd.read_sql_query(query, conn, params=params)
        return df
    except Exception as e:
        st.error(f"Erreur lors de l'exécution de la requête : {e}")
        st.error(f"Requête : {query[:200]}...")
        return pd.DataFrame()


def execute_query_dict(query: str, params: tuple = None) -> list:
    """
    Exécute une requête SQL et retourne une liste de dictionnaires
    """
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
    except Exception as e:
        st.error(f"Erreur lors de l'exécution de la requête : {e}")
        return []


def test_connection() -> bool:
    """
    Teste la connexion à la base de données
    """
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
        return True
    except:
        return False
