"""L — Load : écrit les données transformées dans PostgreSQL."""
from datetime import datetime, timezone

import psycopg2.extras

from .config import HISTORIQUE_PAS_MIN, connect

SQL_STATIONS = """
INSERT INTO stations (code, station_id, nom, capacite, lat, lon{geom_col}, maj_referentiel)
VALUES (%(code)s, %(station_id)s, %(nom)s, %(capacite)s, %(lat)s, %(lon)s{geom_val}, now())
ON CONFLICT (code) DO UPDATE SET
    nom = EXCLUDED.nom, capacite = EXCLUDED.capacite,
    lat = EXCLUDED.lat, lon = EXCLUDED.lon{geom_set}, maj_referentiel = now()
"""

SQL_ETATS = """
INSERT INTO etat_actuel (code, velos_meca, velos_elec, velos_total, bornes_libres, en_service,
                         etat, ordre_etat, derniere_maj, maj_flux, releve_le)
VALUES (%(code)s, %(velos_meca)s, %(velos_elec)s, %(velos_total)s, %(bornes_libres)s, %(en_service)s,
        %(etat)s, %(ordre_etat)s, %(derniere_maj)s, %(maj_flux)s, %(releve_le)s)
ON CONFLICT (code) DO UPDATE SET
    velos_meca = EXCLUDED.velos_meca, velos_elec = EXCLUDED.velos_elec,
    velos_total = EXCLUDED.velos_total, bornes_libres = EXCLUDED.bornes_libres,
    en_service = EXCLUDED.en_service, etat = EXCLUDED.etat, ordre_etat = EXCLUDED.ordre_etat,
    derniere_maj = EXCLUDED.derniere_maj, maj_flux = EXCLUDED.maj_flux, releve_le = EXCLUDED.releve_le
"""

SQL_HISTORIQUE = """
INSERT INTO historique (releve_le, code, velos_meca, velos_elec, bornes_libres, en_service)
VALUES (%(quart)s, %(code)s, %(velos_meca)s, %(velos_elec)s, %(bornes_libres)s, %(en_service)s)
ON CONFLICT DO NOTHING
"""


def _quart_heure(t):
    """(est_un_quart_d_heure, horodatage arrondi). Tolérance de 2 min car l'ETL tourne toutes les 2 min."""
    arrondi = t.replace(minute=(t.minute // HISTORIQUE_PAS_MIN) * HISTORIQUE_PAS_MIN, second=0, microsecond=0)
    return t.minute % HISTORIQUE_PAS_MIN < 2, arrondi


def load(donnees, postgis=False, maintenant=None):
    """donnees = sortie de transform(). Retourne le nombre de lignes écrites."""
    maintenant = maintenant or datetime.now(timezone.utc)
    if postgis:
        geo = {"geom_col": ", geom",
               "geom_val": ", ST_SetSRID(ST_MakePoint(%(lon)s, %(lat)s), 4326)",
               "geom_set": ", geom = EXCLUDED.geom"}
    else:
        geo = {"geom_col": "", "geom_val": "", "geom_set": ""}

    etats = [{**e, "maj_flux": donnees["maj_flux"], "releve_le": maintenant} for e in donnees["etats"]]
    est_quart, quart = _quart_heure(maintenant)

    cx = connect()
    with cx, cx.cursor() as c:                      # une seule transaction
        psycopg2.extras.execute_batch(c, SQL_STATIONS.format(**geo), donnees["stations"], page_size=500)
        psycopg2.extras.execute_batch(c, SQL_ETATS, etats, page_size=500)
        if est_quart:
            psycopg2.extras.execute_batch(c, SQL_HISTORIQUE, [{**e, "quart": quart} for e in etats], page_size=500)
    cx.close()
    return {"stations": len(donnees["stations"]), "etats": len(etats),
            "historique": len(etats) if est_quart else 0}
