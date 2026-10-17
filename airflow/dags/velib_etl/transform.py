"""T — Transform : prépare les lignes à écrire dans PostgreSQL."""
from datetime import datetime, timezone


def etat_station(en_service, velos, places):
    """Règles d'état, identiques à celles du rapport Power BI. Retourne (etat, ordre_pour_tri)."""
    if not en_service:
        return "Hors service", 5
    if velos == 0:
        return "Vide", 1
    if velos <= 2:
        return "Presque vide", 2
    if places == 0:
        return "Pleine", 4
    return "Disponible", 3


def _horodatage(ts):
    return datetime.fromtimestamp(ts, timezone.utc).isoformat() if ts else None


def transform(brut):
    """brut = sortie de extract(). Retourne {'stations': [...], 'etats': [...], 'maj_flux': iso}."""
    stations = [{
        "code": str(s["stationCode"]),
        "station_id": s["station_id"],
        "nom": s["name"],
        "capacite": s.get("capacity"),
        "lat": s["lat"],
        "lon": s["lon"],
    } for s in brut["info"]]

    etats = []
    for s in brut["statut"]:
        types = s.get("num_bikes_available_types") or []
        meca = sum(t.get("mechanical", 0) for t in types)
        elec = sum(t.get("ebike", 0) for t in types)
        places = s.get("num_docks_available", 0)
        en_service = 1 if s.get("is_installed") == 1 and s.get("is_renting") == 1 else 0
        etat, ordre = etat_station(en_service, meca + elec, places)
        etats.append({
            "code": str(s["stationCode"]),
            "velos_meca": meca, "velos_elec": elec, "velos_total": meca + elec,
            "bornes_libres": places, "en_service": en_service,
            "etat": etat, "ordre_etat": ordre,
            "derniere_maj": _horodatage(s.get("last_reported")),
        })

    return {"stations": stations, "etats": etats, "maj_flux": _horodatage(brut.get("maj_flux"))}
