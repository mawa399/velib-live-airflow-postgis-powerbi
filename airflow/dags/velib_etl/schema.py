"""Création (idempotente) de la base, des tables et de la vue lue par Power BI."""
import os
from pathlib import Path

import psycopg2

from .config import connect

SQL_SCHEMA = Path(__file__).parent / "sql" / "schema.sql"


def init_base():
    """Crée la base PG_DB si besoin, active PostGIS si disponible, crée tables et vue.
    Retourne {'postgis': bool}."""
    base = os.environ["PG_DB"]

    # 1. la base elle-même (connexion à la base système "postgres")
    cx = connect("postgres"); cx.autocommit = True
    with cx.cursor() as c:
        c.execute("SELECT 1 FROM pg_database WHERE datname = %s", (base,))
        if not c.fetchone():
            c.execute(f'CREATE DATABASE "{base}"')
    cx.close()

    # 2. extension spatiale, tables, vue
    cx = connect(); cx.autocommit = True
    with cx.cursor() as c:
        try:
            c.execute("CREATE EXTENSION IF NOT EXISTS postgis")
            postgis = True
        except psycopg2.Error:
            postgis = False
        c.execute(SQL_SCHEMA.read_text(encoding="utf-8"))
        if postgis:
            c.execute("ALTER TABLE stations ADD COLUMN IF NOT EXISTS geom geometry(Point, 4326)")
    cx.close()
    return {"postgis": postgis}
