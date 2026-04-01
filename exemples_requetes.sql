-- ============================================================================
-- EXEMPLES DE REQUÊTES POUR LA BASE DE DONNÉES SONAGED
-- Schéma conforme au formulaire KoboToolbox
-- ============================================================================

-- ============================================================================
-- 1. INSERTION DE DONNÉES DE RÉFÉRENCE
-- ============================================================================

-- Les données de référence sont déjà insérées dans le script schema_sonaged.sql
-- Vérifier les départements
SELECT * FROM departements;

-- Vérifier les unités communales
SELECT d.nom AS departement, uc.code, uc.nom AS unite_communale
FROM unites_communales uc
JOIN departements d ON uc.departement_id = d.id
ORDER BY d.nom, uc.nom;

-- Vérifier les concessionnaires
SELECT * FROM concessionnaires;

-- ============================================================================
-- 2. CRÉATION D'UN RAPPORT JOURNALIER
-- ============================================================================

-- Insérer un rapport journalier
INSERT INTO daily_reports (
    date_rapport,
    departement_id,
    unite_communale_id,
    responsable_uc,
    circuits_planifies,
    circuits_collectes,
    tonnage_total,
    depots_recurrents,
    depots_recurrents_leves,
    depots_sauvages,
    depots_sauvages_traites,
    sites_caisse,
    nb_caisses,
    caisses_levees,
    poids_caisses,
    nombre_circuits_planifies,
    circuits_balayage,
    km_planifies,
    km_balayes,
    km_desensable,
    gps_photo
) VALUES (
    '2024-01-15',
    (SELECT id FROM departements WHERE code = 'dakar'),
    (SELECT id FROM unites_communales WHERE code = 'medina'),
    'M. Amadou DIOP',
    10,
    9,
    45.5,
    5,
    4,
    3,
    2,
    8,
    120,
    115,
    12.3,
    5,
    4,
    25.5,
    20.0,
    3.5,
    ST_SetSRID(ST_MakePoint(-17.4677, 14.7167), 4326) -- GPS photo nettoyage
) RETURNING id;

-- ============================================================================
-- 3. AJOUTER LE PERSONNEL DU MATIN
-- ============================================================================

-- Insérer le personnel du matin pour chaque catégorie (remplacer 1 par l'ID du rapport)
INSERT INTO personnel_matin (
    daily_report_id,
    categorie_id,
    effectif_total,
    presents,
    absents,
    malades,
    retard,
    conges,
    observations
) VALUES
    (1, (SELECT id FROM categories_personnel WHERE code = 'collecteur'), 20, 18, 1, 0, 1, 0, 'Effectif complet'),
    (1, (SELECT id FROM categories_personnel WHERE code = 'balayeur'), 15, 14, 0, 1, 0, 0, NULL),
    (1, (SELECT id FROM categories_personnel WHERE code = 'superviseur'), 3, 3, 0, 0, 0, 0, NULL);

-- ============================================================================
-- 4. AJOUTER LE PERSONNEL DE L'APRÈS-MIDI (Groupe répétitif)
-- ============================================================================

-- Insérer le personnel de l'après-midi (remplacer 1 par l'ID du rapport)
INSERT INTO personnel_apres_midi (
    daily_report_id,
    ordre,
    categorie_id,
    effectif_total,
    presents,
    absents,
    malades,
    conges,
    retard,
    observations
) VALUES
    (1, 1, (SELECT id FROM categories_personnel WHERE code = 'collecteur'), 18, 17, 1, 0, 0, 0, NULL),
    (1, 2, (SELECT id FROM categories_personnel WHERE code = 'balayeur'), 12, 12, 0, 0, 0, 0, NULL),
    (1, 3, (SELECT id FROM categories_personnel WHERE code = 'apm'), 5, 5, 0, 0, 0, 0, NULL);

-- ============================================================================
-- 5. AJOUTER LE PERSONNEL DE NUIT (Groupe répétitif)
-- ============================================================================

-- Insérer le personnel de nuit (remplacer 1 par l'ID du rapport)
INSERT INTO personnel_nuit (
    daily_report_id,
    ordre,
    categorie_id,
    effectif_total,
    presents,
    absents,
    malades,
    conges,
    retard,
    observations
) VALUES
    (1, 1, (SELECT id FROM categories_personnel WHERE code = 'collecteur'), 10, 9, 1, 0, 0, 0, NULL),
    (1, 2, (SELECT id FROM categories_personnel WHERE code = 'balayeur'), 8, 8, 0, 0, 0, 0, NULL);

-- ============================================================================
-- 6. AJOUTER DES CIRCUITS DE COLLECTE
-- ============================================================================

-- Insérer des circuits de collecte (remplacer 1 par l'ID du rapport)
INSERT INTO collection_circuits (
    daily_report_id,
    ordre,
    nom_circuit,
    camion,
    concessionnaire_id,
    heure_debut,
    heure_fin,
    duree_collecte,
    poids_circuit,
    status_id,
    observation_circuit
) VALUES
    (1, 1, 'Circuit Centre-ville', 'TRUCK-001', 
     (SELECT id FROM concessionnaires WHERE code = 'ecotra'),
     '08:00:00', '12:30:00', 4.5, 8.5,
     (SELECT id FROM circuit_status WHERE code = 'termine'),
     'Circuit effectué sans incident'),
    
    (1, 2, 'Circuit Zone Nord', 'TRUCK-002',
     (SELECT id FROM concessionnaires WHERE code = 'cdf'),
     '08:30:00', '13:00:00', 4.5, 7.2,
     (SELECT id FROM circuit_status WHERE code = 'termine'),
     NULL),
    
    (1, 3, 'Circuit Zone Sud', 'TRUCK-003',
     (SELECT id FROM concessionnaires WHERE code = 'keur_khadim'),
     '09:00:00', '11:30:00', 2.5, 5.8,
     (SELECT id FROM circuit_status WHERE code = 'non_termine'),
     'Circuit interrompu - problème mécanique');

-- ============================================================================
-- 7. AJOUTER DU MOBILIER URBAIN
-- ============================================================================

-- Insérer du mobilier urbain (remplacer 1 par l'ID du rapport)
INSERT INTO mobilier_urbain (
    daily_report_id,
    ordre,
    type_mobilier_id,
    nb_sites,
    nb_bacs,
    bacs_leves,
    observation_id
) VALUES
    (1, 1, (SELECT id FROM types_mobilier WHERE code = 'prn'), 5, 25, 25,
     (SELECT id FROM observations_mobilier WHERE code = 'lev_s')),
    (1, 2, (SELECT id FROM types_mobilier WHERE code = 'pp'), 8, 40, 38,
     (SELECT id FROM observations_mobilier WHERE code = 'lev_s')),
    (1, 3, (SELECT id FROM types_mobilier WHERE code = 'bacs'), 12, 60, 55,
     (SELECT id FROM observations_mobilier WHERE code = 'pas_lev_s'));

-- ============================================================================
-- 8. AJOUTER DES INTERVENTIONS PONCTUELLES
-- ============================================================================

-- Insérer une intervention ponctuelle (remplacer 1 par l'ID du rapport)
INSERT INTO interventions_ponctuelles (
    daily_report_id,
    ordre,
    agents_interv,
    pelles,
    tasseuses,
    camions,
    quartiers
) VALUES (
    1,
    1,
    10,
    2,
    1,
    3,
    'Quartier Médina, Zone A et Zone B'
) RETURNING id;

-- Ajouter des photos à l'intervention (remplacer 1 par l'ID de l'intervention)
INSERT INTO photos_interventions (
    intervention_id,
    ordre,
    photo_int,
    desc_int,
    gps_int
) VALUES
    (1, 1, 'intervention_001.jpg', 'Avant intervention - dépôt sauvage',
     ST_SetSRID(ST_MakePoint(-17.4650, 14.7150), 4326)),
    (1, 2, 'intervention_002.jpg', 'Pendant intervention - nettoyage en cours',
     ST_SetSRID(ST_MakePoint(-17.4655, 14.7155), 4326)),
    (1, 3, 'intervention_003.jpg', 'Après intervention - zone nettoyée',
     ST_SetSRID(ST_MakePoint(-17.4660, 14.7160), 4326));

-- ============================================================================
-- 9. AJOUTER DES DIFFICULTÉS ET RECOMMANDATIONS
-- ============================================================================

-- Ajouter des difficultés (select_multiple) - remplacer 1 par l'ID du rapport
INSERT INTO daily_reports_difficultes (daily_report_id, difficulte_id) VALUES
    (1, (SELECT id FROM difficultes WHERE code = 'materiel')),
    (1, (SELECT id FROM difficultes WHERE code = 'effectif'));

-- Ajouter d'autres difficultés en texte libre
UPDATE daily_reports SET autres_difficultes = 'Manque de carburant pour certains véhicules' WHERE id = 1;

-- Ajouter des recommandations (select_multiple)
INSERT INTO daily_reports_recommandations (daily_report_id, recommandation_id) VALUES
    (1, (SELECT id FROM recommandations WHERE code = 'renfort')),
    (1, (SELECT id FROM recommandations WHERE code = 'epi'));

-- Ajouter d'autres recommandations en texte libre
UPDATE daily_reports SET autres_recommandations = 'Améliorer la maintenance préventive des véhicules' WHERE id = 1;

-- ============================================================================
-- 10. REQUÊTES D'ANALYSE
-- ============================================================================

-- Afficher tous les rapports avec résumé
SELECT * FROM v_daily_reports_summary
ORDER BY date_rapport DESC
LIMIT 10;

-- Statistiques mensuelles par département
SELECT * FROM v_monthly_stats_by_departement
WHERE mois >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '6 months')
ORDER BY mois DESC, departement_nom;

-- Détails des circuits avec concessionnaires
SELECT * FROM v_collection_circuits_details
WHERE date_rapport >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY date_rapport DESC, ordre;

-- Performance des concessionnaires (poids total par concessionnaire)
SELECT 
    c.nom AS concessionnaire,
    COUNT(cc.id) AS nombre_circuits,
    SUM(cc.poids_circuit) AS poids_total,
    AVG(cc.poids_circuit) AS poids_moyen,
    SUM(cc.duree_collecte) AS duree_totale_heures,
    AVG(cc.duree_collecte) AS duree_moyenne_heures,
    COUNT(CASE WHEN cs.code = 'termine' THEN 1 END) AS circuits_termines,
    COUNT(CASE WHEN cs.code = 'non_termine' THEN 1 END) AS circuits_non_termines,
    COUNT(CASE WHEN cs.code = 'panne' THEN 1 END) AS circuits_panne
FROM concessionnaires c
JOIN collection_circuits cc ON c.id = cc.concessionnaire_id
JOIN daily_reports dr ON cc.daily_report_id = dr.id
LEFT JOIN circuit_status cs ON cc.status_id = cs.id
WHERE dr.date_rapport >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY c.id, c.nom
ORDER BY poids_total DESC;

-- Taux de réussite des circuits par département
SELECT 
    d.nom AS departement,
    COUNT(cc.id) AS total_circuits,
    COUNT(CASE WHEN cs.code = 'termine' THEN 1 END) AS circuits_termines,
    COUNT(CASE WHEN cs.code = 'non_termine' THEN 1 END) AS circuits_non_termines,
    COUNT(CASE WHEN cs.code = 'panne' THEN 1 END) AS circuits_panne,
    ROUND(
        100.0 * COUNT(CASE WHEN cs.code = 'termine' THEN 1 END) / NULLIF(COUNT(cc.id), 0),
        2
    ) AS taux_reussite_pourcent
FROM departements d
JOIN daily_reports dr ON d.id = dr.departement_id
JOIN collection_circuits cc ON dr.id = cc.daily_report_id
LEFT JOIN circuit_status cs ON cc.status_id = cs.id
WHERE dr.date_rapport >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY d.id, d.nom
ORDER BY taux_reussite_pourcent DESC;

-- Analyse du personnel par catégorie (matin, après-midi, nuit)
SELECT 
    cp.libelle AS categorie,
    COUNT(DISTINCT pm.daily_report_id) AS nombre_rapports_matin,
    SUM(pm.effectif_total) AS effectif_total_matin,
    SUM(pm.presents) AS presents_matin,
    SUM(pm.absents) AS absents_matin,
    COUNT(DISTINCT pam.daily_report_id) AS nombre_rapports_apm,
    SUM(pam.effectif_total) AS effectif_total_apm,
    SUM(pam.presents) AS presents_apm,
    SUM(pam.absents) AS absents_apm,
    COUNT(DISTINCT pn.daily_report_id) AS nombre_rapports_nuit,
    SUM(pn.effectif_total) AS effectif_total_nuit,
    SUM(pn.presents) AS presents_nuit,
    SUM(pn.absents) AS absents_nuit
FROM categories_personnel cp
LEFT JOIN personnel_matin pm ON cp.id = pm.categorie_id
LEFT JOIN personnel_apres_midi pam ON cp.id = pam.categorie_id
LEFT JOIN personnel_nuit pn ON cp.id = pn.categorie_id
LEFT JOIN daily_reports dr_matin ON pm.daily_report_id = dr_matin.id
LEFT JOIN daily_reports dr_apm ON pam.daily_report_id = dr_apm.id
LEFT JOIN daily_reports dr_nuit ON pn.daily_report_id = dr_nuit.id
WHERE (dr_matin.date_rapport >= CURRENT_DATE - INTERVAL '30 days'
   OR dr_apm.date_rapport >= CURRENT_DATE - INTERVAL '30 days'
   OR dr_nuit.date_rapport >= CURRENT_DATE - INTERVAL '30 days')
GROUP BY cp.id, cp.libelle
ORDER BY cp.libelle;

-- Analyse du mobilier urbain par type
SELECT 
    tm.libelle AS type_mobilier,
    COUNT(DISTINCT mu.daily_report_id) AS nombre_rapports,
    SUM(mu.nb_sites) AS total_sites,
    SUM(mu.nb_bacs) AS total_bacs,
    SUM(mu.bacs_leves) AS total_bacs_leves,
    ROUND(
        100.0 * SUM(mu.bacs_leves) / NULLIF(SUM(mu.nb_bacs), 0),
        2
    ) AS taux_levage_pourcent
FROM types_mobilier tm
JOIN mobilier_urbain mu ON tm.id = mu.type_mobilier_id
JOIN daily_reports dr ON mu.daily_report_id = dr.id
WHERE dr.date_rapport >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY tm.id, tm.libelle
ORDER BY total_bacs DESC;

-- ============================================================================
-- 11. REQUÊTES SPATIALES (PostGIS)
-- ============================================================================

-- Trouver tous les rapports avec photos dans un rayon de 500 mètres d'un point
SELECT 
    dr.id,
    dr.date_rapport,
    uc.nom AS unite_communale,
    ST_Distance(
        dr.gps_photo,
        ST_SetSRID(ST_MakePoint(-17.4677, 14.7167), 4326)
    ) * 111000 AS distance_metres -- Conversion approximative en mètres
FROM daily_reports dr
JOIN unites_communales uc ON dr.unite_communale_id = uc.id
WHERE ST_DWithin(
    dr.gps_photo,
    ST_SetSRID(ST_MakePoint(-17.4677, 14.7167), 4326),
    0.0045 -- ~500 mètres en degrés
)
ORDER BY distance_metres;

-- Extraire les coordonnées GPS de toutes les photos d'intervention
SELECT 
    dr.date_rapport,
    uc.nom AS unite_communale,
    ip.quartiers,
    ST_X(pi.gps_int) AS longitude,
    ST_Y(pi.gps_int) AS latitude,
    pi.desc_int
FROM photos_interventions pi
JOIN interventions_ponctuelles ip ON pi.intervention_id = ip.id
JOIN daily_reports dr ON ip.daily_report_id = dr.id
JOIN unites_communales uc ON dr.unite_communale_id = uc.id
WHERE pi.gps_int IS NOT NULL
ORDER BY dr.date_rapport DESC;

-- Compter les interventions par zone géographique (carré de 0.01°)
SELECT 
    ST_X(ST_Centroid(ST_Collect(pi.gps_int))) AS centre_longitude,
    ST_Y(ST_Centroid(ST_Collect(pi.gps_int))) AS centre_latitude,
    COUNT(*) AS nombre_interventions
FROM photos_interventions pi
WHERE pi.gps_int IS NOT NULL
GROUP BY 
    FLOOR(ST_X(pi.gps_int) * 100) / 100, -- Arrondir à 0.01°
    FLOOR(ST_Y(pi.gps_int) * 100) / 100
ORDER BY nombre_interventions DESC;

-- ============================================================================
-- 12. REQUÊTES POUR TABLEAUX DE BORD
-- ============================================================================

-- Tableau de bord quotidien
SELECT 
    date_rapport,
    departement_nom,
    unite_communale_nom,
    circuits_planifies,
    circuits_collectes,
    nombre_circuits,
    poids_total_circuits,
    tonnage_total,
    km_balayes,
    nombre_interventions
FROM v_daily_reports_summary
WHERE date_rapport >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY date_rapport DESC, departement_nom;

-- Évolution du tonnage sur 30 jours
SELECT 
    date_rapport,
    SUM(tonnage_total) AS tonnage_journalier_total,
    SUM(poids_total_circuits) AS poids_total_circuits_journalier,
    AVG(tonnage_total) OVER (
        ORDER BY date_rapport 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS moyenne_mobile_7_jours_tonnage
FROM v_daily_reports_summary
WHERE date_rapport >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY date_rapport
ORDER BY date_rapport;

-- Top 10 des unités communales les plus productives
SELECT 
    unite_communale_nom,
    departement_nom,
    COUNT(*) AS nombre_rapports,
    SUM(tonnage_total) AS tonnage_total,
    SUM(poids_total_circuits) AS poids_total_circuits,
    ROUND(AVG(tonnage_total), 2) AS tonnage_moyen_par_rapport
FROM v_daily_reports_summary
WHERE date_rapport >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY unite_communale_nom, departement_nom
HAVING COUNT(*) >= 5
ORDER BY tonnage_total DESC
LIMIT 10;

-- Analyse des difficultés les plus fréquentes
SELECT 
    d.libelle AS difficulte,
    COUNT(*) AS nombre_occurrences,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM daily_reports WHERE date_rapport >= CURRENT_DATE - INTERVAL '30 days'), 2) AS pourcentage
FROM daily_reports_difficultes drd
JOIN difficultes d ON drd.difficulte_id = d.id
JOIN daily_reports dr ON drd.daily_report_id = dr.id
WHERE dr.date_rapport >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY d.id, d.libelle
ORDER BY nombre_occurrences DESC;

-- Analyse des recommandations les plus fréquentes
SELECT 
    r.libelle AS recommandation,
    COUNT(*) AS nombre_occurrences,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM daily_reports WHERE date_rapport >= CURRENT_DATE - INTERVAL '30 days'), 2) AS pourcentage
FROM daily_reports_recommandations drr
JOIN recommandations r ON drr.recommandation_id = r.id
JOIN daily_reports dr ON drr.daily_report_id = dr.id
WHERE dr.date_rapport >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY r.id, r.libelle
ORDER BY nombre_occurrences DESC;

-- ============================================================================
-- 13. REQUÊTES DE MAINTENANCE
-- ============================================================================

-- Vérifier l'intégrité des données
SELECT 
    'Rapports sans département' AS probleme,
    COUNT(*) AS nombre
FROM daily_reports
WHERE departement_id IS NULL

UNION ALL

SELECT 
    'Rapports sans unité communale' AS probleme,
    COUNT(*) AS nombre
FROM daily_reports
WHERE unite_communale_id IS NULL

UNION ALL

SELECT 
    'Circuits sans concessionnaire' AS probleme,
    COUNT(*) AS nombre
FROM collection_circuits
WHERE concessionnaire_id IS NULL

UNION ALL

SELECT 
    'Personnel matin sans catégorie' AS probleme,
    COUNT(*) AS nombre
FROM personnel_matin
WHERE categorie_id IS NULL

UNION ALL

SELECT 
    'Personnel APM sans catégorie' AS probleme,
    COUNT(*) AS nombre
FROM personnel_apres_midi
WHERE categorie_id IS NULL

UNION ALL

SELECT 
    'Personnel nuit sans catégorie' AS probleme,
    COUNT(*) AS nombre
FROM personnel_nuit
WHERE categorie_id IS NULL;

-- Statistiques sur les photos
SELECT 
    COUNT(*) AS nombre_photos_interventions,
    COUNT(CASE WHEN gps_int IS NOT NULL THEN 1 END) AS avec_gps,
    COUNT(CASE WHEN desc_int IS NOT NULL THEN 1 END) AS avec_description
FROM photos_interventions;

-- Statistiques sur les photos de nettoyage
SELECT 
    COUNT(*) AS nombre_rapports,
    COUNT(CASE WHEN gps_photo IS NOT NULL THEN 1 END) AS avec_gps_photo,
    COUNT(CASE WHEN photo_net IS NOT NULL THEN 1 END) AS avec_photo
FROM daily_reports;

-- ============================================================================
-- FIN DES EXEMPLES
-- ============================================================================
