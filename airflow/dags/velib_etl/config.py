"""Paramètres de l'ETL. Les identifiants viennent des variables d'environnement
(fichier parametres.txt chargé par docker-compose)."""
import os

import psycopg2

API_BASE = "https://velib-metropole-opendata.smovengo.cloud/opendata/Velib_Metropole/"
API_HEADERS = {"User-Agent": "Mozilla/5.0 (Airflow - Velib Live)"}
API_TIMEOUT = 30          # secondes

HISTORIQUE_PAS_MIN = 15   # un relevé conservé toutes les 15 minutes


def connect(dbname=None):
    """Connexion à PostgreSQL. dbname=None -> base du projet (PG_DB)."""
    return psycopg2.connect(
        host=os.environ["PG_HOST"],
        port=os.environ.get("PG_PORT", "5432"),
        user=os.environ["PG_USER"],
        password=os.environ["PG_PASSWORD"],
        dbname=dbname or os.environ["PG_DB"],
        connect_timeout=10,
    )
