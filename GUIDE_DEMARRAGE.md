# Guide de Démarrage Rapide - Base de Données SONAGED

## 🚀 Installation en 3 étapes

### Étape 1 : Créer la base de données

```bash
# Se connecter à PostgreSQL en tant que superutilisateur
psql -U postgres

# Créer la base de données
CREATE DATABASE sonaged_db WITH ENCODING 'UTF8' LC_COLLATE='fr_FR.UTF-8' LC_CTYPE='fr_FR.UTF-8';

# Se connecter à la nouvelle base
\c reporting_sonaged_db
```

### Étape 2 : Exécuter le script SQL

```bash
# Depuis le terminal
psql -U postgres -d sonaged_db -f schema_sonaged.sql

# Ou depuis psql
\i schema_sonaged.sql
```

### Étape 3 : Vérifier l'installation

```sql
-- Vérifier PostGIS
SELECT PostGIS_version();

-- Lister les tables créées
\dt

-- Lister les vues créées
\dv

-- Vérifier les données de référence (déjà insérées)
SELECT * FROM departements;
SELECT * FROM unites_communales;
SELECT * FROM concessionnaires;
SELECT * FROM categories_personnel;
SELECT * FROM circuit_status;
```

## 📝 Structure des Données

### Ordre d'insertion recommandé

1. **Données de référence** ✅ **DÉJÀ INSÉRÉES** dans le script
   - `departements` (Dakar, Guediawaye, Pikine, Rufisque, Keur Massar)
   - `unites_communales` (Yoff, Ngor, Médina jour/nuit, etc.)
   - `categories_personnel` (Collecteurs, Balayeurs, AP de site, etc.)
   - `concessionnaires` (Ecotra, CDF, Keur Khadim)
   - `circuit_status` (Circuit terminé, non terminé, Panne)
   - `types_mobilier` (PRN, PP, Bacs de rue)
   - `observations_mobilier` (Levés, Pas Levés)
   - `difficultes` (Manque de matériel, Manque d'effectif)
   - `recommandations` (Renforcer le personnel, Dotation en EPI)

2. **Rapport journalier**
   - `daily_reports` (une ligne par rapport)

3. **Données liées au rapport** (dans l'ordre)
   - `personnel_matin` (une ligne par catégorie)
   - `personnel_apres_midi` (plusieurs lignes possibles)
   - `personnel_nuit` (plusieurs lignes possibles)
   - `collection_circuits` (plusieurs circuits par rapport)
   - `mobilier_urbain` (plusieurs types par rapport)
   - `interventions_ponctuelles` (plusieurs interventions par rapport)
   - `photos_interventions` (plusieurs photos par intervention)
   - `daily_reports_difficultes` (liaison many-to-many)
   - `daily_reports_recommandations` (liaison many-to-many)

## 🔑 Points Clés

### Correspondance avec le formulaire KoboToolbox

Le schéma correspond **exactement** à la structure du formulaire XLSForm :

- ✅ **Départements** : Dakar, Guediawaye, Pikine, Rufisque, Keur Massar
- ✅ **Unités communales** : Dépendent du département sélectionné
- ✅ **Concessionnaires** : Ecotra, CDF, Keur Khadim (pas d'opérateurs individuels)
- ✅ **Personnel du matin** : Groupe simple (une ligne par catégorie)
- ✅ **Personnel après-midi** : Groupe répétitif (plusieurs lignes possibles)
- ✅ **Personnel de nuit** : Groupe répétitif (plusieurs lignes possibles)
- ✅ **Circuits** : Groupe répétitif avec concessionnaire, camion, horaires, poids
- ✅ **Mobilier urbain** : Groupe répétitif avec type (PRN, PP, Bacs)
- ✅ **Interventions ponctuelles** : Groupe répétitif avec photos géolocalisées
- ✅ **Difficultés/Recommandations** : Select_multiple (tables de liaison)

### Géolocalisation
- Les champs GPS utilisent **PostGIS POINT** avec SRID 4326 (WGS84)
- Format d'insertion : `ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)`
- Exemple : `ST_SetSRID(ST_MakePoint(-17.4677, 14.7167), 4326)` pour Dakar
- Champs géolocalisés :
  - `daily_reports.gps_photo` : GPS de la photo de nettoyage
  - `photos_interventions.gps_int` : GPS des photos d'intervention

### Calcul automatique
- La durée des circuits (`duree_collecte`) est calculée dans KoboToolbox et importée
- Les timestamps `updated_at` sont mis à jour automatiquement

### Contraintes importantes
- Un seul rapport par unité communale/date (contrainte UNIQUE)
- Les photos d'intervention doivent être liées à une intervention
- Les difficultés et recommandations utilisent des tables de liaison (select_multiple)

## 📊 Utilisation avec les Outils BI

### Power BI
1. **Nouvelle source de données** → PostgreSQL
2. **Sélectionner les vues** :
   - `v_daily_reports_summary`
   - `v_monthly_stats_by_departement`
   - `v_collection_circuits_details`
3. **Pour les cartes** : Utiliser les colonnes `longitude` et `latitude` des requêtes PostGIS

### Metabase / Superset
1. **Ajouter une base de données** → PostgreSQL
2. Les vues apparaissent comme des tables normales
3. Utiliser les requêtes SQL personnalisées pour les analyses complexes

## 🔍 Requêtes Utiles

### Voir tous les rapports récents
```sql
SELECT * FROM v_daily_reports_summary
ORDER BY date_rapport DESC
LIMIT 20;
```

### Statistiques mensuelles par département
```sql
SELECT * FROM v_monthly_stats_by_departement
WHERE mois >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '3 months')
ORDER BY mois DESC;
```

### Performance des concessionnaires
```sql
SELECT 
    c.nom AS concessionnaire,
    COUNT(*) AS circuits,
    SUM(cc.poids_circuit) AS poids_total
FROM concessionnaires c
JOIN collection_circuits cc ON c.id = cc.concessionnaire_id
JOIN daily_reports dr ON cc.daily_report_id = dr.id
WHERE dr.date_rapport >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY c.id, c.nom
ORDER BY poids_total DESC;
```

### Analyse du personnel
```sql
-- Personnel par période (matin, après-midi, nuit)
SELECT 
    cp.libelle AS categorie,
    SUM(pm.effectif_total) AS effectif_total_matin,
    SUM(pam.effectif_total) AS effectif_total_apm,
    SUM(pn.effectif_total) AS effectif_total_nuit
FROM categories_personnel cp
LEFT JOIN personnel_matin pm ON cp.id = pm.categorie_id
LEFT JOIN personnel_apres_midi pam ON cp.id = pam.categorie_id
LEFT JOIN personnel_nuit pn ON cp.id = pn.categorie_id
LEFT JOIN daily_reports dr_matin ON pm.daily_report_id = dr_matin.id
LEFT JOIN daily_reports dr_apm ON pam.daily_report_id = dr_apm.id
LEFT JOIN daily_reports dr_nuit ON pn.daily_report_id = dr_nuit.id
WHERE (dr_matin.date_rapport >= CURRENT_DATE - INTERVAL '7 days'
   OR dr_apm.date_rapport >= CURRENT_DATE - INTERVAL '7 days'
   OR dr_nuit.date_rapport >= CURRENT_DATE - INTERVAL '7 days')
GROUP BY cp.id, cp.libelle;
```

## 📁 Fichiers Fournis

- **`schema_sonaged.sql`** : Script principal de création du schéma (conforme au formulaire KoboToolbox)
- **`README_SCHEMA.md`** : Documentation complète du schéma
- **`exemples_requetes.sql`** : Exemples de requêtes SQL avec données de test
- **`GUIDE_DEMARRAGE.md`** : Ce fichier

## ⚠️ Notes Importantes

1. **Sauvegarde** : Toujours faire des sauvegardes régulières
   ```bash
   pg_dump -U postgres sonaged_db > backup_$(date +%Y%m%d).sql
   ```

2. **Permissions** : Créer un utilisateur dédié pour l'application (voir README_SCHEMA.md)

3. **Performance** : Les index sont déjà créés, mais surveiller les performances sur de gros volumes

4. **PostGIS** : Nécessite l'extension PostGIS installée sur le serveur PostgreSQL

5. **Données de référence** : Toutes les données de référence sont déjà insérées dans le script SQL

## 🆘 Dépannage

### Erreur "extension postgis does not exist"
```sql
-- Installer PostGIS (nécessite les droits superutilisateur)
CREATE EXTENSION postgis;
```

### Erreur "relation does not exist"
- Vérifier que vous êtes connecté à la bonne base de données
- Vérifier que le script SQL a été exécuté complètement

### Erreur de contrainte UNIQUE
- Un rapport existe déjà pour cette unité communale/date
- Vérifier avec : `SELECT * FROM daily_reports WHERE date_rapport = '2024-01-15' AND unite_communale_id = 1;`

### Erreur "concessionnaire does not exist"
- Les concessionnaires sont déjà insérés : Ecotra, CDF, Keur Khadim
- Vérifier avec : `SELECT * FROM concessionnaires;`

## 📞 Prochaines Étapes

1. ✅ Vérifier que toutes les données de référence sont présentes
2. ✅ Tester l'insertion d'un rapport journalier complet (voir `exemples_requetes.sql`)
3. ✅ Configurer la connexion depuis votre application/KoboToolbox
4. ✅ Créer vos premiers tableaux de bord

## 🔄 Import depuis KoboToolbox

Pour importer les données depuis KoboToolbox :

1. Exporter les données au format CSV depuis KoboToolbox
2. Mapper les colonnes du CSV vers les tables PostgreSQL
3. Insérer les données en respectant l'ordre :
   - `daily_reports` d'abord
   - Puis les tables liées (personnel, circuits, mobilier, interventions, etc.)

**Note** : Les noms de colonnes dans le schéma correspondent aux `name` du formulaire XLSForm (ex: `date_rapport`, `D_partement`, `unite`, `operateur`, etc.)

Pour plus de détails, consultez `README_SCHEMA.md`.
