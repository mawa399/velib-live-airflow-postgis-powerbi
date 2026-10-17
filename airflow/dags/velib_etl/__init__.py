"""
velib_etl — code ETL de Vélib' Live, indépendant d'Airflow.

    extract.py    : appel de l'API GBFS Vélib'
    transform.py  : calcul des vélos, places libres et état de chaque station
    load.py       : écriture dans PostgreSQL (état actuel + historique au quart d'heure)
    schema.py     : création de la base, des tables et de la vue (sql/schema.sql)
    config.py     : paramètres (API, connexion PostgreSQL)

Lancement manuel d'un passage complet, sans Airflow :
    python -m velib_etl
"""
