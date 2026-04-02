"""
Requêtes SQL réutilisables pour le dashboard Streamlit
"""

# Requêtes pour la vue d'ensemble
QUERY_DAILY_SUMMARY = """
    SELECT 
        v.id,
        v.date_rapport,
        v.departement_nom,
        v.unite_communale_nom,
        v.circuits_planifies,
        v.circuits_collectes,
        v.nombre_circuits,
        v.poids_total_circuits,
        v.tonnage_total,
        v.km_balayes,
        v.nombre_interventions,
        COALESCE(SUM(pm.effectif_total), 0) AS effectif_personnel_matin,
        COALESCE(SUM(pam.effectif_total), 0) AS effectif_personnel_apm,
        COALESCE(SUM(pn.effectif_total), 0) AS effectif_personnel_nuit
    FROM v_daily_reports_summary v
    LEFT JOIN personnel_matin pm ON v.id = pm.daily_report_id
    LEFT JOIN personnel_apres_midi pam ON v.id = pam.daily_report_id
    LEFT JOIN personnel_nuit pn ON v.id = pn.daily_report_id
    WHERE v.date_rapport >= %s AND v.date_rapport <= %s
    GROUP BY v.id, v.date_rapport, v.departement_nom, v.unite_communale_nom, v.circuits_planifies, v.circuits_collectes, v.nombre_circuits, v.poids_total_circuits, v.tonnage_total, v.km_balayes, v.nombre_interventions
    ORDER BY v.date_rapport DESC
"""

QUERY_MONTHLY_STATS = """
    SELECT 
        mois,
        departement_nom,
        nombre_rapports,
        nombre_circuits,
        poids_total_circuits,
        poids_moyen_par_circuit,
        duree_totale_heures,
        circuits_termines,
        circuits_non_termines,
        circuits_panne,
        tonnage_total_rapport,
        km_balayes_total
    FROM v_monthly_stats_by_departement
    WHERE mois >= %s
    ORDER BY mois DESC, departement_nom
"""

# Requêtes pour les circuits
QUERY_CIRCUITS_DETAILS = """
    SELECT 
        date_rapport,
        departement_nom,
        unite_communale_nom,
        nom_circuit,
        camion,
        concessionnaire_nom,
        heure_debut,
        heure_fin,
        duree_collecte,
        poids_circuit,
        status_libelle
    FROM v_collection_circuits_details
    WHERE date_rapport >= %s AND date_rapport <= %s
    ORDER BY date_rapport DESC, ordre
"""

# Requêtes pour le personnel
QUERY_PERSONNEL_MATIN = """
    SELECT 
        dr.date_rapport,
        cp.libelle AS categorie,
        pm.effectif_total,
        pm.presents,
        pm.absents,
        pm.malades,
        pm.retard,
        pm.conges
    FROM personnel_matin pm
    JOIN daily_reports dr ON pm.daily_report_id = dr.id
    JOIN categories_personnel cp ON pm.categorie_id = cp.id
    WHERE dr.date_rapport >= %s AND dr.date_rapport <= %s
    ORDER BY dr.date_rapport DESC, cp.libelle
"""

QUERY_PERSONNEL_APM = """
    SELECT 
        dr.date_rapport,
        cp.libelle AS categorie,
        pam.effectif_total,
        pam.presents,
        pam.absents,
        pam.malades,
        pam.conges,
        pam.retard
    FROM personnel_apres_midi pam
    JOIN daily_reports dr ON pam.daily_report_id = dr.id
    JOIN categories_personnel cp ON pam.categorie_id = cp.id
    WHERE dr.date_rapport >= %s AND dr.date_rapport <= %s
    ORDER BY dr.date_rapport DESC, cp.libelle
"""

QUERY_PERSONNEL_NUIT = """
    SELECT 
        dr.date_rapport,
        cp.libelle AS categorie,
        pn.effectif_total,
        pn.presents,
        pn.absents,
        pn.malades,
        pn.conges,
        pn.retard
    FROM personnel_nuit pn
    JOIN daily_reports dr ON pn.daily_report_id = dr.id
    JOIN categories_personnel cp ON pn.categorie_id = cp.id
    WHERE dr.date_rapport >= %s AND dr.date_rapport <= %s
    ORDER BY dr.date_rapport DESC, cp.libelle
"""

# Requêtes pour les concessionnaires
QUERY_CONCESSIONNAIRES_PERFORMANCE = """
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
    WHERE dr.date_rapport >= %s
    GROUP BY c.id, c.nom
    ORDER BY poids_total DESC
"""

# Requêtes spatiales
QUERY_GPS_PHOTOS = """
    SELECT 
        dr.date_rapport,
        uc.nom AS unite_communale,
        ST_X(dr.gps_photo) AS longitude,
        ST_Y(dr.gps_photo) AS latitude
    FROM daily_reports dr
    JOIN unites_communales uc ON dr.unite_communale_id = uc.id
    WHERE dr.gps_photo IS NOT NULL
    AND dr.date_rapport >= %s
"""

QUERY_GPS_INTERVENTIONS = """
    SELECT 
        dr.date_rapport,
        uc.nom AS unite_communale,
        ip.quartiers,
        pi.desc_int,
        ST_X(pi.gps_int) AS longitude,
        ST_Y(pi.gps_int) AS latitude
    FROM photos_interventions pi
    JOIN interventions_ponctuelles ip ON pi.intervention_id = ip.id
    JOIN daily_reports dr ON ip.daily_report_id = dr.id
    JOIN unites_communales uc ON dr.unite_communale_id = uc.id
    WHERE pi.gps_int IS NOT NULL
    AND dr.date_rapport >= %s
"""

# Requêtes pour les statistiques
QUERY_STATS_GENERAL = """
    SELECT 
        COUNT(DISTINCT dr.id) AS total_rapports,
        COUNT(DISTINCT cc.id) AS total_circuits,
        SUM(cc.poids_circuit) AS poids_total_circuits,
        SUM(dr.tonnage_total) AS tonnage_total_rapports,
        SUM(dr.km_balayes) AS km_balayes_total,
        AVG(cc.poids_circuit) AS poids_moyen_circuit
    FROM daily_reports dr
    LEFT JOIN collection_circuits cc ON dr.id = cc.daily_report_id
    WHERE dr.date_rapport >= %s
"""

# Requêtes pour les KPI avancés
QUERY_KPI_COVERAGE = """
    SELECT 
        uc.nom AS unite_communale,
        COUNT(dr.id) AS jours_reports,
        SUM(cc.poids_circuit) AS tonnage_total,
        COUNT(DISTINCT cc.id) AS nombre_circuits,
        ROUND(COUNT(cc.id)::numeric / 30, 2) AS circuits_par_jour_moyen
    FROM unites_communales uc
    LEFT JOIN daily_reports dr ON uc.id = dr.unite_communale_id AND dr.date_rapport >= %s
    LEFT JOIN collection_circuits cc ON dr.id = cc.daily_report_id
    GROUP BY uc.id, uc.nom
    ORDER BY tonnage_total DESC NULLS LAST
"""

QUERY_KPI_AVERAGE_DURATION = """
    SELECT 
        dr.date_rapport,
        AVG(cc.duree_collecte) AS duree_moyenne_heures,
        AVG(cc.poids_circuit) AS poids_moyen,
        SUM(cc.poids_circuit) / NULLIF(SUM(cc.duree_collecte), 0) AS tonnage_par_heure
    FROM daily_reports dr
    LEFT JOIN collection_circuits cc ON dr.id = cc.daily_report_id
    WHERE dr.date_rapport >= %s
    GROUP BY dr.date_rapport
    ORDER BY dr.date_rapport DESC
"""

QUERY_ALERTS_ANOMALIES = """
    SELECT 
        dr.date_rapport,
        dr.kobo_submission_id,
        uc.nom AS unite_communale,
        CASE
            WHEN cc.poids_circuit = 0 THEN 'Tonnage nul'
            WHEN cc.duree_collecte > 8 THEN 'Durée excessive'
            WHEN COUNT(cc.id) = 0 THEN 'Aucun circuit'
            ELSE 'Normal'
        END AS alerte_type,
        cc.poids_circuit,
        cc.duree_collecte
    FROM daily_reports dr
    LEFT JOIN unites_communales uc ON dr.unite_communale_id = uc.id
    LEFT JOIN collection_circuits cc ON dr.id = cc.daily_report_id
    WHERE dr.date_rapport >= %s
    AND (cc.poids_circuit = 0 OR cc.duree_collecte > 8 OR COUNT(cc.id) = 0)
    GROUP BY dr.id, dr.date_rapport, dr.kobo_submission_id, uc.nom, cc.poids_circuit, cc.duree_collecte
    ORDER BY dr.date_rapport DESC
"""

# Requêtes pour l'analyse de performance
QUERY_PERFORMANCE_BY_TRUCK = """
    SELECT
        cc.camion,
        COUNT(*) AS nombre_circuits,
        SUM(cc.poids_circuit) AS tonnage_total,
        AVG(cc.poids_circuit) AS tonnage_moyen_par_circuit,
        SUM(cc.duree_collecte) AS duree_totale_heures,
        AVG(cc.duree_collecte) AS duree_moyenne_par_circuit,
        CASE
            WHEN SUM(cc.duree_collecte) > 0 THEN SUM(cc.poids_circuit) / SUM(cc.duree_collecte)
            ELSE 0
        END AS tonnage_par_heure,
        COUNT(CASE WHEN cc.status_libelle LIKE '%termin%' THEN 1 END) AS circuits_termines,
        COUNT(CASE WHEN cc.status_libelle NOT LIKE '%termin%' THEN 1 END) AS circuits_non_termines
    FROM collection_circuits cc
    JOIN daily_reports dr ON cc.daily_report_id = dr.id
    WHERE dr.date_rapport >= %s AND dr.date_rapport <= %s
      AND cc.camion IS NOT NULL AND cc.camion != ''
    GROUP BY cc.camion
    ORDER BY tonnage_total DESC
"""

# Version simplifiée au cas où la requête ci-dessus pose problème
# Version simplifiée pour éviter les problèmes de corruption
QUERY_PERFORMANCE_BY_TRUCK_SIMPLE = """
SELECT 
    cc.camion,
    COUNT(*) AS nombre_circuits,
    SUM(cc.poids_circuit) AS tonnage_total,
    AVG(cc.poids_circuit) AS tonnage_moyen_par_circuit,
    SUM(cc.duree_collecte) AS duree_totale_heures,
    AVG(cc.duree_collecte) AS duree_moyenne_par_circuit,

    CASE 
        WHEN SUM(cc.duree_collecte) > 0 
        THEN SUM(cc.poids_circuit) / SUM(cc.duree_collecte)
        ELSE 0 
    END AS tonnage_par_heure,

    SUM(
        CASE 
            WHEN COALESCE(cs.libelle, '') ILIKE '%%termin%%'
            THEN 1 ELSE 0
        END
    ) AS circuits_termines,

    SUM(
        CASE 
            WHEN COALESCE(cs.libelle, '') NOT ILIKE '%%termin%%'
            THEN 1 ELSE 0
        END
    ) AS circuits_non_termines

FROM collection_circuits cc
JOIN daily_reports dr ON cc.daily_report_id = dr.id
LEFT JOIN circuit_status cs ON cc.status_id = cs.id
WHERE dr.date_rapport >= %s
  AND dr.date_rapport <= %s
  AND cc.camion IS NOT NULL
  AND cc.camion <> ''
GROUP BY cc.camion
ORDER BY tonnage_total DESC;
"""


QUERY_PERFORMANCE_BY_UC = """
    SELECT 
        uc.nom AS unite_communale,
        COUNT(DISTINCT dr.id) AS nombre_rapports,
        SUM(dr.tonnage_total) AS tonnage_total,
        AVG(dr.tonnage_total) AS tonnage_moyen_par_rapport,
        SUM(dr.circuits_collectes) AS circuits_total,
        AVG(dr.circuits_collectes) AS circuits_moyen_par_rapport,
        SUM(dr.km_balayes) AS km_total,
        AVG(dr.km_balayes) AS km_moyen_par_rapport,
        CASE 
            WHEN SUM(dr.km_balayes) > 0 THEN SUM(dr.tonnage_total) / SUM(dr.km_balayes)
            ELSE 0
        END AS tonnage_par_km,
        SUM(COALESCE(pm.effectif_total, 0) + COALESCE(pam.effectif_total, 0) + COALESCE(pn.effectif_total, 0)) AS effectif_total
    FROM daily_reports dr
    LEFT JOIN unites_communales uc ON dr.unite_communale_id = uc.id
    LEFT JOIN personnel_matin pm ON dr.id = pm.daily_report_id
    LEFT JOIN personnel_apres_midi pam ON dr.id = pam.daily_report_id
    LEFT JOIN personnel_nuit pn ON dr.id = pn.daily_report_id
    WHERE dr.date_rapport >= %s AND dr.date_rapport <= %s
    GROUP BY uc.id, uc.nom
    ORDER BY tonnage_total DESC
"""

QUERY_PERFORMANCE_TRENDS = """
    SELECT 
        DATE_TRUNC('week', dr.date_rapport) AS semaine,
        COUNT(DISTINCT dr.id) AS nombre_rapports,
        SUM(dr.tonnage_total) AS tonnage_total,
        AVG(dr.tonnage_total) AS tonnage_moyen,
        SUM(dr.circuits_collectes) AS circuits_total,
        SUM(dr.km_balayes) AS km_total,
        CASE 
            WHEN SUM(dr.km_balayes) > 0 THEN SUM(dr.tonnage_total) / SUM(dr.km_balayes)
            ELSE 0
        END AS tonnage_par_km,
        CASE 
            WHEN SUM(dr.circuits_collectes) > 0 THEN SUM(dr.tonnage_total) / SUM(dr.circuits_collectes)
            ELSE 0
        END AS tonnage_par_circuit
    FROM daily_reports dr
    WHERE dr.date_rapport >= %s AND dr.date_rapport <= %s
    GROUP BY DATE_TRUNC('week', dr.date_rapport)
    ORDER BY semaine
"""

QUERY_EFFICIENCY_METRICS = """
    SELECT 
        'Tonnage par heure' AS metrique,
        AVG(CASE WHEN cc.duree_collecte > 0 THEN cc.poids_circuit / cc.duree_collecte ELSE 0 END) AS valeur_moyenne,
        MIN(CASE WHEN cc.duree_collecte > 0 THEN cc.poids_circuit / cc.duree_collecte ELSE NULL END) AS valeur_min,
        MAX(CASE WHEN cc.duree_collecte > 0 THEN cc.poids_circuit / cc.duree_collecte ELSE NULL END) AS valeur_max
    FROM collection_circuits cc
    JOIN daily_reports dr ON cc.daily_report_id = dr.id
    WHERE dr.date_rapport >= %s AND dr.date_rapport <= %s AND cc.duree_collecte > 0
    
    UNION ALL
    
    SELECT 
        'Tonnage par km' AS metrique,
        AVG(CASE WHEN dr.km_balayes > 0 THEN dr.tonnage_total / dr.km_balayes ELSE 0 END) AS valeur_moyenne,
        MIN(CASE WHEN dr.km_balayes > 0 THEN dr.tonnage_total / dr.km_balayes ELSE NULL END) AS valeur_min,
        MAX(CASE WHEN dr.km_balayes > 0 THEN dr.tonnage_total / dr.km_balayes ELSE NULL END) AS valeur_max
    FROM daily_reports dr
    WHERE dr.date_rapport >= %s AND dr.date_rapport <= %s AND dr.km_balayes > 0
    
    UNION ALL
    
    SELECT 
        'Circuits par jour' AS metrique,
        AVG(dr.circuits_collectes) AS valeur_moyenne,
        MIN(dr.circuits_collectes) AS valeur_min,
        MAX(dr.circuits_collectes) AS valeur_max
    FROM daily_reports dr
    WHERE dr.date_rapport >= %s AND dr.date_rapport <= %s
"""

# =====================================================
# Requêtes pour les filtres géographiques
# =====================================================

QUERY_DEPARTEMENTS = """
    SELECT DISTINCT
        d.id,
        d.code,
        d.nom
    FROM departements d
    ORDER BY d.nom
"""

QUERY_UNITES_COMMUNALES_BY_DEPT = """
    SELECT DISTINCT
        uc.id,
        uc.code,
        uc.nom,
        uc.departement_id
    FROM unites_communales uc
    WHERE uc.departement_id = %s
    ORDER BY uc.nom
"""

QUERY_UNITES_COMMUNALES_BY_DEPTS = """
    SELECT DISTINCT
        uc.id,
        uc.code,
        uc.nom,
        uc.departement_id
    FROM unites_communales uc
    WHERE uc.departement_id = ANY(%s::integer[])
    ORDER BY uc.nom
"""

QUERY_UNITES_COMMUNALES_BY_DEPT_CODE = """
    SELECT DISTINCT
        uc.id,
        uc.code,
        uc.nom,
        uc.departement_id
    FROM unites_communales uc
    JOIN departements d ON uc.departement_id = d.id
    WHERE d.code = %s
    ORDER BY uc.nom
"""

QUERY_UNITES_COMMUNALES_BY_DEPT_CODES = """
    SELECT DISTINCT
        uc.id,
        uc.code,
        uc.nom,
        uc.departement_id,
        d.code AS dept_code,
        d.nom AS dept_nom
    FROM unites_communales uc
    JOIN departements d ON uc.departement_id = d.id
    WHERE d.code = ANY(%s::text[])
    ORDER BY d.nom, uc.nom
"""
