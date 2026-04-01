-- ============================================================================
-- SCHÉMA MART : Données analytiques transformées
-- Base de données PostgreSQL avec PostGIS pour le reporting journalier
-- Données normalisées pour l'analyse et la visualisation Streamlit
-- Source : Transformation depuis raw_kobo
-- ============================================================================

-- Création de la base de données
-- Note: Exécuter cette commande en tant que superutilisateur PostgreSQL
-- CREATE DATABASE sonaged_db WITH ENCODING 'UTF8' LC_COLLATE='fr_FR.UTF-8' LC_CTYPE='fr_FR.UTF-8';
-- \c sonaged_db;

-- ============================================================================
-- EXTENSIONS
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- TABLES DE RÉFÉRENCE (Dictionnaires)
-- ============================================================================

-- Table des départements
CREATE TABLE departements (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    nom VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insertion des départements du formulaire
INSERT INTO departements (code, nom) VALUES
    ('dakar', 'Dakar'),
    ('guediawaye', 'Guediawaye'),
    ('pikine', 'Pikine'),
    ('rufisque', 'Rufisque'),
    ('keur_massar', 'Keur Massar');

-- Table des unités communales
CREATE TABLE unites_communales (
    id SERIAL PRIMARY KEY,
    departement_id INTEGER REFERENCES departements(id) ON DELETE RESTRICT,
    code VARCHAR(50) UNIQUE NOT NULL,
    nom VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insertion des unités communales du formulaire
INSERT INTO unites_communales (departement_id, code, nom) VALUES
    ((SELECT id FROM departements WHERE code = 'dakar'), 'medina', 'Yoff'),
    ((SELECT id FROM departements WHERE code = 'dakar'), 'ngor', 'Ngor'),
    ((SELECT id FROM departements WHERE code = 'dakar'), 'm_dina_jour', 'Médina jour'),
    ((SELECT id FROM departements WHERE code = 'dakar'), 'm_dina_nuit', 'Médina nuit'),
    ((SELECT id FROM departements WHERE code = 'dakar'), 'mermoz_sacr__coeur', 'Mermoz sacré coeur'),
    ((SELECT id FROM departements WHERE code = 'dakar'), 'grand_dakar', 'Grand Dakar'),
    ((SELECT id FROM departements WHERE code = 'dakar'), 'biscuiterie', 'Biscuiterie'),
    ((SELECT id FROM departements WHERE code = 'dakar'), 'dieuppeul_derkl', 'Dieuppeul Derklé'),
    ((SELECT id FROM departements WHERE code = 'dakar'), 'sicap_liberte', 'Sicap Liberté'),
    ((SELECT id FROM departements WHERE code = 'dakar'), 'hann_bel_air', 'Hann bel-air'),
    ((SELECT id FROM departements WHERE code = 'dakar'), 'face_colobane_gueule_tap_e', 'Face-colobane-Gueule Tapée'),
    ((SELECT id FROM departements WHERE code = 'dakar'), 'plateau_jour', 'Plateau jour'),
    ((SELECT id FROM departements WHERE code = 'dakar'), 'plateau_nuit', 'Plateau nuit');

-- Table des catégories de personnel
CREATE TABLE categories_personnel (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    libelle VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insertion des catégories du formulaire
INSERT INTO categories_personnel (code, libelle) VALUES
    ('collecteur', 'Collecteurs'),
    ('balayeur', 'Balayeurs'),
    ('aps', 'AP de site'),
    ('apm', 'AP mobile urbain'),
    ('superviseur', 'Superviseur');

-- Table des concessionnaires (opérateurs)
CREATE TABLE concessionnaires (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    nom VARCHAR(255) NOT NULL,
    description TEXT,
    actif BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insertion des concessionnaires du formulaire
INSERT INTO concessionnaires (code, nom) VALUES
    ('ecotra', 'Ecotra'),
    ('cdf', 'CDF'),
    ('keur_khadim', 'Keur Khadim');

-- Table des statuts de circuit
CREATE TABLE circuit_status (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    libelle VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insertion des statuts du formulaire
INSERT INTO circuit_status (code, libelle) VALUES
    ('termine', 'Circuit terminé'),
    ('non_termine', 'Circuit non terminé'),
    ('panne', 'Panne');

-- Table des types de mobilier urbain
CREATE TABLE types_mobilier (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    libelle VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insertion des types de mobilier du formulaire
INSERT INTO types_mobilier (code, libelle) VALUES
    ('prn', 'PRN'),
    ('pp', 'PP'),
    ('bacs', 'Bacs de rue');

-- Table des observations mobilier
CREATE TABLE observations_mobilier (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    libelle VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insertion des observations du formulaire
INSERT INTO observations_mobilier (code, libelle) VALUES
    ('lev_s', 'Levés'),
    ('pas_lev_s', 'Pas Levés');

-- Table des difficultés
CREATE TABLE difficultes (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    libelle VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insertion des difficultés du formulaire
INSERT INTO difficultes (code, libelle) VALUES
    ('materiel', 'Manque de matériel'),
    ('effectif', 'Manque d''effectif');

-- Table des recommandations
CREATE TABLE recommandations (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    libelle VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insertion des recommandations du formulaire
INSERT INTO recommandations (code, libelle) VALUES
    ('renfort', 'Renforcer le personnel'),
    ('epi', 'Dotation en EPI');

-- ============================================================================
-- TABLE PRINCIPALE : RAPPORTS JOURNALIERS
-- ============================================================================

CREATE TABLE daily_reports (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    
    -- Informations générales
    date_rapport DATE NOT NULL,
    departement_id INTEGER NOT NULL REFERENCES departements(id) ON DELETE RESTRICT,
    unite_communale_id INTEGER NOT NULL REFERENCES unites_communales(id) ON DELETE RESTRICT,
    responsable_uc VARCHAR(255),
    
    -- Collecte - Généralités
    circuits_planifies INTEGER DEFAULT 0 CHECK (circuits_planifies >= 0),
    circuits_collectes INTEGER DEFAULT 0 CHECK (circuits_collectes >= 0),
    tonnage_total DECIMAL(10, 2) DEFAULT 0 CHECK (tonnage_total >= 0),
    depots_recurrents INTEGER DEFAULT 0 CHECK (depots_recurrents >= 0),
    depots_recurrents_leves INTEGER DEFAULT 0 CHECK (depots_recurrents_leves >= 0),
    depots_sauvages INTEGER DEFAULT 0 CHECK (depots_sauvages >= 0),
    depots_sauvages_traites INTEGER DEFAULT 0 CHECK (depots_sauvages_traites >= 0),
    
    -- Collecte - Caisses polybennes
    sites_caisse INTEGER DEFAULT 0 CHECK (sites_caisse >= 0),
    nb_caisses INTEGER DEFAULT 0 CHECK (nb_caisses >= 0),
    caisses_levees INTEGER DEFAULT 0 CHECK (caisses_levees >= 0),
    poids_caisses DECIMAL(10, 2) DEFAULT 0 CHECK (poids_caisses >= 0),
    
    -- Nettoyage
    nombre_circuits_planifies INTEGER DEFAULT 0 CHECK (nombre_circuits_planifies >= 0),
    circuits_balayage INTEGER DEFAULT 0 CHECK (circuits_balayage >= 0),
    km_planifies DECIMAL(10, 2) DEFAULT 0 CHECK (km_planifies >= 0),
    km_balayes DECIMAL(10, 2) DEFAULT 0 CHECK (km_balayes >= 0),
    km_desensable DECIMAL(10, 2) DEFAULT 0 CHECK (km_desensable >= 0),
    photo_net VARCHAR(255), -- Nom du fichier photo
    gps_photo GEOMETRY(POINT, 4326), -- GPS de la photo nettoyage
    
    -- Métadonnées
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    kobo_submission_id VARCHAR(255), -- ID de soumission KoboToolbox
    raw_submission_id INTEGER REFERENCES raw_kobo.submissions(id) ON DELETE SET NULL, -- Référence au RAW
    
    -- Contrainte d'unicité : un seul rapport par unité communale et par date
    UNIQUE(date_rapport, unite_communale_id)
);

-- Index pour améliorer les performances
CREATE INDEX idx_daily_reports_date ON daily_reports(date_rapport);
CREATE INDEX idx_daily_reports_departement ON daily_reports(departement_id);
CREATE INDEX idx_daily_reports_unite ON daily_reports(unite_communale_id);
CREATE INDEX idx_daily_reports_created_at ON daily_reports(created_at);
CREATE INDEX idx_daily_reports_gps_photo ON daily_reports USING GIST(gps_photo);

-- ============================================================================
-- PERSONNEL DU MATIN (Groupe simple)
-- ============================================================================

CREATE TABLE personnel_matin (
    id SERIAL PRIMARY KEY,
    daily_report_id INTEGER NOT NULL REFERENCES daily_reports(id) ON DELETE CASCADE,
    categorie_id INTEGER REFERENCES categories_personnel(id) ON DELETE SET NULL,
    effectif_total INTEGER DEFAULT 0 CHECK (effectif_total >= 0),
    presents INTEGER DEFAULT 0 CHECK (presents >= 0),
    absents INTEGER DEFAULT 0 CHECK (absents >= 0),
    malades INTEGER DEFAULT 0 CHECK (malades >= 0),
    retard INTEGER DEFAULT 0 CHECK (retard >= 0),
    conges INTEGER DEFAULT 0 CHECK (conges >= 0),
    observations TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(daily_report_id, categorie_id)
);

CREATE INDEX idx_personnel_matin_report ON personnel_matin(daily_report_id);
CREATE INDEX idx_personnel_matin_categorie ON personnel_matin(categorie_id);

-- ============================================================================
-- PERSONNEL DE L'APRÈS-MIDI (Groupe répétitif)
-- ============================================================================

CREATE TABLE personnel_apres_midi (
    id SERIAL PRIMARY KEY,
    daily_report_id INTEGER NOT NULL REFERENCES daily_reports(id) ON DELETE CASCADE,
    ordre INTEGER DEFAULT 0,
    categorie_id INTEGER REFERENCES categories_personnel(id) ON DELETE SET NULL,
    effectif_total INTEGER DEFAULT 0 CHECK (effectif_total >= 0),
    presents INTEGER DEFAULT 0 CHECK (presents >= 0),
    absents INTEGER DEFAULT 0 CHECK (absents >= 0),
    malades INTEGER DEFAULT 0 CHECK (malades >= 0),
    conges INTEGER DEFAULT 0 CHECK (conges >= 0),
    retard INTEGER DEFAULT 0 CHECK (retard >= 0),
    observations TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_personnel_apm_report ON personnel_apres_midi(daily_report_id);
CREATE INDEX idx_personnel_apm_categorie ON personnel_apres_midi(categorie_id);

-- ============================================================================
-- PERSONNEL DE NUIT (Groupe répétitif)
-- ============================================================================

CREATE TABLE personnel_nuit (
    id SERIAL PRIMARY KEY,
    daily_report_id INTEGER NOT NULL REFERENCES daily_reports(id) ON DELETE CASCADE,
    ordre INTEGER DEFAULT 0,
    categorie_id INTEGER REFERENCES categories_personnel(id) ON DELETE SET NULL,
    effectif_total INTEGER DEFAULT 0 CHECK (effectif_total >= 0),
    presents INTEGER DEFAULT 0 CHECK (presents >= 0),
    absents INTEGER DEFAULT 0 CHECK (absents >= 0),
    malades INTEGER DEFAULT 0 CHECK (malades >= 0),
    conges INTEGER DEFAULT 0 CHECK (conges >= 0),
    retard INTEGER DEFAULT 0 CHECK (retard >= 0),
    observations TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_personnel_nuit_report ON personnel_nuit(daily_report_id);
CREATE INDEX idx_personnel_nuit_categorie ON personnel_nuit(categorie_id);

-- ============================================================================
-- CIRCUITS DE COLLECTE (Groupe répétitif)
-- ============================================================================

CREATE TABLE collection_circuits (
    id SERIAL PRIMARY KEY,
    daily_report_id INTEGER NOT NULL REFERENCES daily_reports(id) ON DELETE CASCADE,
    ordre INTEGER DEFAULT 0,
    
    -- Informations du circuit
    nom_circuit VARCHAR(255),
    camion VARCHAR(100), -- Numéro du camion (texte libre)
    concessionnaire_id INTEGER REFERENCES concessionnaires(id) ON DELETE SET NULL,
    
    -- Horaires
    heure_debut TIME,
    heure_fin TIME,
    duree_collecte DECIMAL(5, 2), -- Durée calculée en heures (depuis KoboToolbox)
    
    -- Métriques
    poids_circuit DECIMAL(10, 2) CHECK (poids_circuit >= 0),
    
    -- Statut
    status_id INTEGER REFERENCES circuit_status(id) ON DELETE SET NULL,
    
    -- Observations
    observation_circuit TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_collection_circuits_report ON collection_circuits(daily_report_id);
CREATE INDEX idx_collection_circuits_concessionnaire ON collection_circuits(concessionnaire_id);
CREATE INDEX idx_collection_circuits_status ON collection_circuits(status_id);

-- ============================================================================
-- MOBILIER URBAIN (Groupe répétitif)
-- ============================================================================

CREATE TABLE mobilier_urbain (
    id SERIAL PRIMARY KEY,
    daily_report_id INTEGER NOT NULL REFERENCES daily_reports(id) ON DELETE CASCADE,
    ordre INTEGER DEFAULT 0,
    
    type_mobilier_id INTEGER REFERENCES types_mobilier(id) ON DELETE SET NULL,
    nb_sites INTEGER DEFAULT 0 CHECK (nb_sites >= 0),
    nb_bacs INTEGER DEFAULT 0 CHECK (nb_bacs >= 0),
    bacs_leves INTEGER DEFAULT 0 CHECK (bacs_leves >= 0),
    observation_id INTEGER REFERENCES observations_mobilier(id) ON DELETE SET NULL,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_mobilier_report ON mobilier_urbain(daily_report_id);
CREATE INDEX idx_mobilier_type ON mobilier_urbain(type_mobilier_id);

-- ============================================================================
-- INTERVENTIONS PONCTUELLES (Groupe répétitif)
-- ============================================================================

CREATE TABLE interventions_ponctuelles (
    id SERIAL PRIMARY KEY,
    daily_report_id INTEGER NOT NULL REFERENCES daily_reports(id) ON DELETE CASCADE,
    ordre INTEGER DEFAULT 0,
    
    agents_interv INTEGER DEFAULT 0 CHECK (agents_interv >= 0),
    pelles INTEGER DEFAULT 0 CHECK (pelles >= 0),
    tasseuses INTEGER DEFAULT 0 CHECK (tasseuses >= 0),
    camions INTEGER DEFAULT 0 CHECK (camions >= 0),
    quartiers TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_interventions_report ON interventions_ponctuelles(daily_report_id);

-- ============================================================================
-- PHOTOS DES INTERVENTIONS (Groupe répétitif dans interventions)
-- ============================================================================

CREATE TABLE photos_interventions (
    id SERIAL PRIMARY KEY,
    intervention_id INTEGER NOT NULL REFERENCES interventions_ponctuelles(id) ON DELETE CASCADE,
    ordre INTEGER DEFAULT 0,
    
    photo_int VARCHAR(255), -- Nom du fichier photo
    desc_int TEXT, -- Description
    gps_int GEOMETRY(POINT, 4326), -- GPS de la photo
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_photos_interventions_intervention ON photos_interventions(intervention_id);
CREATE INDEX idx_photos_interventions_gps ON photos_interventions USING GIST(gps_int);

-- ============================================================================
-- DIFFICULTÉS ET RECOMMANDATIONS (Table de liaison many-to-many)
-- ============================================================================

-- Table de liaison pour les difficultés (select_multiple)
CREATE TABLE daily_reports_difficultes (
    daily_report_id INTEGER NOT NULL REFERENCES daily_reports(id) ON DELETE CASCADE,
    difficulte_id INTEGER NOT NULL REFERENCES difficultes(id) ON DELETE CASCADE,
    PRIMARY KEY (daily_report_id, difficulte_id)
);

CREATE INDEX idx_difficultes_report ON daily_reports_difficultes(daily_report_id);
CREATE INDEX idx_difficultes_type ON daily_reports_difficultes(difficulte_id);

-- Table de liaison pour les recommandations (select_multiple)
CREATE TABLE daily_reports_recommandations (
    daily_report_id INTEGER NOT NULL REFERENCES daily_reports(id) ON DELETE CASCADE,
    recommandation_id INTEGER NOT NULL REFERENCES recommandations(id) ON DELETE CASCADE,
    PRIMARY KEY (daily_report_id, recommandation_id)
);

CREATE INDEX idx_recommandations_report ON daily_reports_recommandations(daily_report_id);
CREATE INDEX idx_recommandations_type ON daily_reports_recommandations(recommandation_id);

-- Champs texte supplémentaires pour difficultés et recommandations
ALTER TABLE daily_reports ADD COLUMN autres_difficultes TEXT;
ALTER TABLE daily_reports ADD COLUMN autres_recommandations TEXT;

-- ============================================================================
-- VUES UTILITAIRES POUR L'ANALYSE ET LE REPORTING
-- ============================================================================

-- Vue récapitulative des rapports journaliers avec détails
CREATE OR REPLACE VIEW v_daily_reports_summary AS
SELECT 
    dr.id,
    dr.uuid,
    dr.date_rapport,
    d.nom AS departement_nom,
    d.code AS departement_code,
    uc.nom AS unite_communale_nom,
    uc.code AS unite_communale_code,
    dr.responsable_uc,
    
    -- Collecte généralités
    dr.circuits_planifies,
    dr.circuits_collectes,
    dr.tonnage_total,
    dr.depots_recurrents,
    dr.depots_recurrents_leves,
    dr.depots_sauvages,
    dr.depots_sauvages_traites,
    
    -- Caisses polybennes
    dr.sites_caisse,
    dr.nb_caisses,
    dr.caisses_levees,
    dr.poids_caisses,
    
    -- Nettoyage
    dr.nombre_circuits_planifies,
    dr.circuits_balayage,
    dr.km_planifies,
    dr.km_balayes,
    dr.km_desensable,
    
    -- Compteurs
    COUNT(DISTINCT pm.id) AS nombre_categories_personnel_matin,
    COUNT(DISTINCT pam.id) AS nombre_categories_personnel_apm,
    COUNT(DISTINCT pn.id) AS nombre_categories_personnel_nuit,
    COUNT(DISTINCT cc.id) AS nombre_circuits,
    COUNT(DISTINCT mu.id) AS nombre_types_mobilier,
    COUNT(DISTINCT ip.id) AS nombre_interventions,
    COALESCE(SUM(cc.poids_circuit), 0) AS poids_total_circuits,
    
    -- Difficultés et recommandations
    STRING_AGG(DISTINCT diff.libelle, ', ') AS difficultes_libelles,
    dr.autres_difficultes,
    STRING_AGG(DISTINCT rec.libelle, ', ') AS recommandations_libelles,
    dr.autres_recommandations,
    
    dr.created_at,
    dr.updated_at
FROM daily_reports dr
LEFT JOIN departements d ON dr.departement_id = d.id
LEFT JOIN unites_communales uc ON dr.unite_communale_id = uc.id
LEFT JOIN personnel_matin pm ON dr.id = pm.daily_report_id
LEFT JOIN personnel_apres_midi pam ON dr.id = pam.daily_report_id
LEFT JOIN personnel_nuit pn ON dr.id = pn.daily_report_id
LEFT JOIN collection_circuits cc ON dr.id = cc.daily_report_id
LEFT JOIN mobilier_urbain mu ON dr.id = mu.daily_report_id
LEFT JOIN interventions_ponctuelles ip ON dr.id = ip.daily_report_id
LEFT JOIN daily_reports_difficultes drd ON dr.id = drd.daily_report_id
LEFT JOIN difficultes diff ON drd.difficulte_id = diff.id
LEFT JOIN daily_reports_recommandations drr ON dr.id = drr.daily_report_id
LEFT JOIN recommandations rec ON drr.recommandation_id = rec.id
GROUP BY dr.id, d.nom, d.code, uc.nom, uc.code, diff.libelle, rec.libelle;

-- Vue des circuits avec détails complets
CREATE OR REPLACE VIEW v_collection_circuits_details AS
SELECT 
    cc.id,
    cc.daily_report_id,
    dr.date_rapport,
    d.nom AS departement_nom,
    uc.nom AS unite_communale_nom,
    cc.ordre,
    cc.nom_circuit,
    cc.camion,
    c.nom AS concessionnaire_nom,
    c.code AS concessionnaire_code,
    cc.heure_debut,
    cc.heure_fin,
    cc.duree_collecte,
    cc.poids_circuit,
    cs.libelle AS status_libelle,
    cs.code AS status_code,
    cc.observation_circuit,
    cc.created_at
FROM collection_circuits cc
JOIN daily_reports dr ON cc.daily_report_id = dr.id
LEFT JOIN departements d ON dr.departement_id = d.id
LEFT JOIN unites_communales uc ON dr.unite_communale_id = uc.id
LEFT JOIN concessionnaires c ON cc.concessionnaire_id = c.id
LEFT JOIN circuit_status cs ON cc.status_id = cs.id;

-- Vue des statistiques mensuelles par département
CREATE OR REPLACE VIEW v_monthly_stats_by_departement AS
SELECT 
    DATE_TRUNC('month', dr.date_rapport) AS mois,
    d.id AS departement_id,
    d.nom AS departement_nom,
    COUNT(DISTINCT dr.id) AS nombre_rapports,
    COUNT(DISTINCT cc.id) AS nombre_circuits,
    COALESCE(SUM(cc.poids_circuit), 0) AS poids_total_circuits,
    COALESCE(AVG(cc.poids_circuit), 0) AS poids_moyen_par_circuit,
    COALESCE(SUM(cc.duree_collecte), 0) AS duree_totale_heures,
    COALESCE(AVG(cc.duree_collecte), 0) AS duree_moyenne_heures,
    COUNT(DISTINCT CASE WHEN cs.code = 'termine' THEN cc.id END) AS circuits_termines,
    COUNT(DISTINCT CASE WHEN cs.code = 'non_termine' THEN cc.id END) AS circuits_non_termines,
    COUNT(DISTINCT CASE WHEN cs.code = 'panne' THEN cc.id END) AS circuits_panne,
    COALESCE(SUM(dr.tonnage_total), 0) AS tonnage_total_rapport,
    COALESCE(SUM(dr.km_balayes), 0) AS km_balayes_total
FROM daily_reports dr
JOIN departements d ON dr.departement_id = d.id
LEFT JOIN collection_circuits cc ON dr.id = cc.daily_report_id
LEFT JOIN circuit_status cs ON cc.status_id = cs.id
GROUP BY DATE_TRUNC('month', dr.date_rapport), d.id, d.nom;

-- ============================================================================
-- FONCTIONS UTILITAIRES
-- ============================================================================

-- Fonction pour mettre à jour automatiquement updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers pour mettre à jour automatiquement updated_at
CREATE TRIGGER update_departements_updated_at BEFORE UPDATE ON departements
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_unites_communales_updated_at BEFORE UPDATE ON unites_communales
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_concessionnaires_updated_at BEFORE UPDATE ON concessionnaires
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_daily_reports_updated_at BEFORE UPDATE ON daily_reports
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_personnel_matin_updated_at BEFORE UPDATE ON personnel_matin
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_personnel_apm_updated_at BEFORE UPDATE ON personnel_apres_midi
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_personnel_nuit_updated_at BEFORE UPDATE ON personnel_nuit
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_collection_circuits_updated_at BEFORE UPDATE ON collection_circuits
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_mobilier_urbain_updated_at BEFORE UPDATE ON mobilier_urbain
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_interventions_updated_at BEFORE UPDATE ON interventions_ponctuelles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_photos_interventions_updated_at BEFORE UPDATE ON photos_interventions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- COMMENTAIRES SUR LES TABLES ET COLONNES
-- ============================================================================

COMMENT ON TABLE daily_reports IS 'Table principale des rapports journaliers de collecte des déchets';
COMMENT ON TABLE personnel_matin IS 'Personnel du matin (groupe simple, une ligne par catégorie)';
COMMENT ON TABLE personnel_apres_midi IS 'Personnel de l''après-midi (groupe répétitif)';
COMMENT ON TABLE personnel_nuit IS 'Personnel de nuit (groupe répétitif)';
COMMENT ON TABLE collection_circuits IS 'Circuits de collecte des déchets (groupe répétitif)';
COMMENT ON TABLE mobilier_urbain IS 'Mobilier urbain (groupe répétitif)';
COMMENT ON TABLE interventions_ponctuelles IS 'Interventions ponctuelles (groupe répétitif)';
COMMENT ON TABLE photos_interventions IS 'Photos des interventions (groupe répétitif dans interventions)';
COMMENT ON TABLE concessionnaires IS 'Concessionnaires (opérateurs de collecte)';
COMMENT ON TABLE departements IS 'Dictionnaire des départements';
COMMENT ON TABLE unites_communales IS 'Dictionnaire des unités communales';

COMMENT ON COLUMN daily_reports.gps_photo IS 'Point GPS de la photo de nettoyage (PostGIS POINT)';
COMMENT ON COLUMN photos_interventions.gps_int IS 'Point GPS de la photo d''intervention (PostGIS POINT)';

-- ============================================================================
-- FIN DU SCHÉMA
-- ============================================================================
