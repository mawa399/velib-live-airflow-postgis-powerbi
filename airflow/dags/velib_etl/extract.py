"""E — Extract : télécharge le référentiel et les disponibilités depuis l'API GBFS."""
import requests

from .config import API_BASE, API_HEADERS, API_TIMEOUT


def _get(fichier):
    r = requests.get(API_BASE + fichier, headers=API_HEADERS, timeout=API_TIMEOUT)
    r.raise_for_status()          # erreur HTTP -> la tâche échoue et Airflow la relance
    return r.json()


def extract():
    """Retourne {'info': [...], 'statut': [...], 'maj_flux': <timestamp unix>}."""
    info = _get("station_information.json")
    statut = _get("station_status.json")
    return {
        "info": info["data"]["stations"],
        "statut": statut["data"]["stations"],
        "maj_flux": statut.get("lastUpdatedOther"),
    }
