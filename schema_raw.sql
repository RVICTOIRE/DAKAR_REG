-- ============================================================================
-- SCHÉMA RAW : Données brutes de KoboToolbox
-- Reflète exactement la structure du formulaire XLSForm
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS raw_kobo;

-- ============================================================================
-- TABLE PRINCIPALE : Submissions brutes
-- ============================================================================

CREATE TABLE raw_kobo.submissions (
    id SERIAL PRIMARY KEY,
    kobo_submission_id VARCHAR(255) UNIQUE NOT NULL,
    submission_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Données complètes de la soumission (JSON brut)
    form_data JSONB NOT NULL,
    
    -- Métadonnées Kobo
    form_version VARCHAR(50),
    form_id VARCHAR(100),
    device_id VARCHAR(255),
    username VARCHAR(255),
    instance_id VARCHAR(255),
    
    -- Statut d'import
    imported_to_mart BOOLEAN DEFAULT FALSE,
    import_error TEXT,
    import_attempts INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index pour performance
CREATE INDEX idx_raw_submissions_kobo_id ON raw_kobo.submissions(kobo_submission_id);
CREATE INDEX idx_raw_submissions_imported ON raw_kobo.submissions(imported_to_mart);
CREATE INDEX idx_raw_submissions_date ON raw_kobo.submissions(submission_date);
CREATE INDEX idx_raw_submissions_form_data_gin ON raw_kobo.submissions USING GIN(form_data);

-- ============================================================================
-- TABLES RAW POUR GROUPES RÉPÉTITIFS
-- ============================================================================

-- Personnel de l'après-midi (repeat: personnel_apm)
CREATE TABLE raw_kobo.personnel_apres_midi (
    id SERIAL PRIMARY KEY,
    submission_id INTEGER NOT NULL REFERENCES raw_kobo.submissions(id) ON DELETE CASCADE,
    ordre INTEGER DEFAULT 0,
    personnel_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_raw_personnel_apm_submission ON raw_kobo.personnel_apres_midi(submission_id);

-- Circuits de collecte (repeat: circuits)
CREATE TABLE raw_kobo.circuits (
    id SERIAL PRIMARY KEY,
    submission_id INTEGER NOT NULL REFERENCES raw_kobo.submissions(id) ON DELETE CASCADE,
    ordre INTEGER DEFAULT 0,
    circuit_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_raw_circuits_submission ON raw_kobo.circuits(submission_id);
CREATE INDEX idx_raw_circuits_data_gin ON raw_kobo.circuits USING GIN(circuit_data);

-- Mobilier urbain (repeat: mobilier)
CREATE TABLE raw_kobo.mobilier_urbain (
    id SERIAL PRIMARY KEY,
    submission_id INTEGER NOT NULL REFERENCES raw_kobo.submissions(id) ON DELETE CASCADE,
    ordre INTEGER DEFAULT 0,
    mobilier_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_raw_mobilier_submission ON raw_kobo.mobilier_urbain(submission_id);

-- Interventions ponctuelles (repeat: group_vs5fg16)
-- Note: Ce groupe contient aussi un sous-repeat pour les photos
CREATE TABLE raw_kobo.interventions_ponctuelles (
    id SERIAL PRIMARY KEY,
    submission_id INTEGER NOT NULL REFERENCES raw_kobo.submissions(id) ON DELETE CASCADE,
    ordre INTEGER DEFAULT 0,
    intervention_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_raw_interventions_submission ON raw_kobo.interventions_ponctuelles(submission_id);

-- Photos des interventions (repeat: photos_interv, imbriqué dans interventions)
CREATE TABLE raw_kobo.photos_interventions (
    id SERIAL PRIMARY KEY,
    intervention_id INTEGER NOT NULL REFERENCES raw_kobo.interventions_ponctuelles(id) ON DELETE CASCADE,
    ordre INTEGER DEFAULT 0,
    photo_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_raw_photos_intervention ON raw_kobo.photos_interventions(intervention_id);

-- ============================================================================
-- TABLE DE SUIVI DES VERSIONS DU FORMULAIRE
-- ============================================================================

CREATE TABLE raw_kobo.form_versions (
    id SERIAL PRIMARY KEY,
    version VARCHAR(50) UNIQUE NOT NULL,
    form_id VARCHAR(100) NOT NULL,
    deployed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TABLE DE LOG DES ERREURS D'IMPORT
-- ============================================================================

CREATE TABLE raw_kobo.import_errors (
    id SERIAL PRIMARY KEY,
    submission_id INTEGER REFERENCES raw_kobo.submissions(id) ON DELETE SET NULL,
    error_type VARCHAR(100),
    error_message TEXT,
    error_details JSONB,
    occurred_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_raw_import_errors_submission ON raw_kobo.import_errors(submission_id);
CREATE INDEX idx_raw_import_errors_type ON raw_kobo.import_errors(error_type);

-- ============================================================================
-- FONCTIONS UTILITAIRES
-- ============================================================================

-- Fonction pour mettre à jour updated_at
CREATE OR REPLACE FUNCTION raw_kobo.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger pour updated_at
CREATE TRIGGER update_raw_submissions_updated_at 
    BEFORE UPDATE ON raw_kobo.submissions
    FOR EACH ROW EXECUTE FUNCTION raw_kobo.update_updated_at_column();

-- ============================================================================
-- VUES UTILITAIRES RAW
-- ============================================================================

-- Vue des submissions non importées
CREATE OR REPLACE VIEW raw_kobo.v_submissions_pending_import AS
SELECT 
    id,
    kobo_submission_id,
    submission_date,
    form_version,
    imported_to_mart,
    import_error,
    import_attempts,
    created_at
FROM raw_kobo.submissions
WHERE imported_to_mart = FALSE
ORDER BY submission_date DESC;

-- Vue des statistiques d'import
CREATE OR REPLACE VIEW raw_kobo.v_import_stats AS
SELECT 
    COUNT(*) AS total_submissions,
    COUNT(CASE WHEN imported_to_mart = TRUE THEN 1 END) AS imported_count,
    COUNT(CASE WHEN imported_to_mart = FALSE THEN 1 END) AS pending_count,
    COUNT(CASE WHEN import_error IS NOT NULL THEN 1 END) AS error_count,
    MIN(submission_date) AS oldest_submission,
    MAX(submission_date) AS newest_submission
FROM raw_kobo.submissions;

-- ============================================================================
-- COMMENTAIRES
-- ============================================================================

COMMENT ON SCHEMA raw_kobo IS 'Schéma RAW : données brutes de KoboToolbox, structure exacte du formulaire';
COMMENT ON TABLE raw_kobo.submissions IS 'Table principale des soumissions brutes Kobo';
COMMENT ON TABLE raw_kobo.circuits IS 'Circuits de collecte (groupe répétitif)';
COMMENT ON TABLE raw_kobo.personnel_apres_midi IS 'Personnel après-midi (groupe répétitif)';
COMMENT ON TABLE raw_kobo.mobilier_urbain IS 'Mobilier urbain (groupe répétitif)';
COMMENT ON TABLE raw_kobo.interventions_ponctuelles IS 'Interventions ponctuelles (groupe répétitif)';
COMMENT ON TABLE raw_kobo.photos_interventions IS 'Photos des interventions (groupe répétitif imbriqué)';

-- ============================================================================
-- FIN DU SCHÉMA RAW
-- ============================================================================
