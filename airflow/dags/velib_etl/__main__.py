"""Passage complet de l'ETL sans Airflow :  python -m velib_etl"""
from .extract import extract
from .load import load
from .schema import init_base
from .transform import transform

if __name__ == "__main__":
    info = init_base()
    print("init      :", info)
    brut = extract()
    print("extract   :", len(brut["info"]), "stations,", len(brut["statut"]), "statuts")
    donnees = transform(brut)
    print("transform :", len(donnees["etats"]), "états calculés")
    print("load      :", load(donnees, postgis=info["postgis"]))
