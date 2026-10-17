-- Vélib' Live — schéma de la base (exécuté à chaque passage : tout est idempotent)

-- Référentiel des stations (la colonne geom est ajoutée par schema.py si PostGIS est disponible)
CREATE TABLE IF NOT EXISTS stations (
    code            text PRIMARY KEY,
    station_id      bigint,
    nom             text,
    capacite        int,
    lat             double precision,
    lon             double precision,
    maj_referentiel timestamptz
);

-- Dernier état connu de chaque station (écrasé toutes les 2 minutes)
CREATE TABLE IF NOT EXISTS etat_actuel (
    code          text PRIMARY KEY,
    velos_meca    int,
    velos_elec    int,
    velos_total   int,
    bornes_libres int,
    en_service    int,
    etat          text,
    ordre_etat    int,
    derniere_maj  timestamptz,   -- dernier signal de la borne
    maj_flux      timestamptz,   -- date de publication du flux par Vélib'
    releve_le     timestamptz    -- date d'écriture par l'ETL
);

-- Historique : un relevé par quart d'heure, jamais écrasé
CREATE TABLE IF NOT EXISTS historique (
    releve_le     timestamptz,
    code          text,
    velos_meca    int,
    velos_elec    int,
    bornes_libres int,
    en_service    int,
    PRIMARY KEY (releve_le, code)
);
CREATE INDEX IF NOT EXISTS historique_code ON historique (code);

-- Vue lue par Power BI en DirectQuery (heures converties en heure de Paris)
CREATE OR REPLACE VIEW v_stations_live AS
SELECT s.code,
       s.station_id::text AS station_id,
       s.nom, s.lat, s.lon, s.capacite,
       e.velos_meca, e.velos_elec, e.velos_total, e.bornes_libres, e.en_service,
       (e.derniere_maj AT TIME ZONE 'Europe/Paris') AS derniere_maj,
       e.etat, e.ordre_etat,
       (e.maj_flux AT TIME ZONE 'Europe/Paris') AS maj_flux
FROM stations s
JOIN etat_actuel e USING (code);
