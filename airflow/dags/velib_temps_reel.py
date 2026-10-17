"""
Vélib' Live — DAG Airflow (orchestration uniquement).
Le code ETL est dans le package velib_etl/ (extract, transform, load, schema).

Toutes les 2 minutes : API Vélib' -> PostgreSQL/PostGIS -> Power BI (DirectQuery).
"""
from datetime import timedelta

import pendulum
from airflow.decorators import dag, task

from velib_etl import extract as e, load as l, schema, transform as t


@dag(
    dag_id="velib_temps_reel",
    description="API Vélib' -> PostgreSQL toutes les 2 minutes",
    schedule="*/2 * * * *",
    start_date=pendulum.datetime(2026, 10, 15, tz="Europe/Paris"),
    catchup=False,                      # pas de rattrapage des créneaux manqués (PC éteint)
    max_active_runs=1,                  # jamais deux passages en même temps
    dagrun_timeout=timedelta(minutes=5),
    default_args={"owner": "mawa", "retries": 1, "retry_delay": timedelta(seconds=30)},
    tags=["velib", "temps-reel", "portfolio"],
)
def velib_temps_reel():

    @task
    def init_base():
        return schema.init_base()

    @task
    def extract():
        return e.extract()

    @task
    def transform(brut):
        return t.transform(brut)

    @task
    def load(donnees, info):
        return l.load(donnees, postgis=info["postgis"])

    info = init_base()
    brut = extract()
    info >> brut                        # la base doit exister avant d'extraire
    load(transform(brut), info)


velib_temps_reel()
