# Schéma de Base de Données SONAGED - Collecte des Déchets

## 📋 Vue d'ensemble

Ce schéma PostgreSQL avec PostGIS est conçu pour stocker et analyser les données de reporting journalier des activités de collecte des déchets de la SONAGED au Sénégal. **Le schéma correspond exactement à la structure du formulaire KoboToolbox XLSForm.**

Il est optimisé pour :

- ✅ Le reporting quotidien structuré conforme au formulaire KoboToolbox
- ✅ L'analyse statistique temporelle et spatiale
- ✅ La visualisation géographique (cartes, tableaux de bord)
- ✅ L'intégration avec des outils BI (Power BI, Metabase, Superset)
- ✅ L'évolutivité et la maintenance

## 🗄️ Architecture du Schéma

### Tables de Référence (Dictionnaires)

Ces tables contiennent les données de référence réutilisables, correspondant aux choix du formulaire KoboToolbox :

| Table | Description | Valeurs du formulaire |
|-------|-------------|----------------------|
| `departements` | Départements | Dakar, Guediawaye, Pikine, Rufisque, Keur Massar |
| `unites_communales` | Unités communales | Yoff, Ngor, Médina jour/nuit, Grand Dakar, etc. |
| `categories_personnel` | Catégories de personnel | Collecteurs, Balayeurs, AP de site, AP mobile urbain, Superviseur |
| `concessionnaires` | Concessionnaires (opérateurs) | Ecotra, CDF, Keur Khadim |
| `circuit_status` | Statuts des circuits | Circuit terminé, Circuit non terminé, Panne |
| `types_mobilier` | Types de mobilier urbain | PRN, PP, Bacs de rue |
| `observations_mobilier` | Observations mobilier | Levés, Pas Levés |
| `difficultes` | Difficultés rencontrées | Manque de matériel, Manque d'effectif |
| `recommandations` | Recommandations | Renforcer le personnel, Dotation en EPI |

### Table Principale

#### `daily_reports`
Table centrale contenant les rapports journaliers avec :
- **Informations générales** : Date, département, unité communale, responsable UC
- **Collecte - Généralités** : Circuits planifiés/collectés, tonnage total, dépôts récurrents/sauvages
- **Collecte - Caisses polybennes** : Sites, nombre de caisses, caisses levées, poids
- **Nettoyage** : Circuits planifiés/balayés, kilométrage planifié/balayé/désensablé, photo GPS
- **Métadonnées** : UUID, timestamps, ID soumission KoboToolbox

**Contrainte d'unicité** : Un seul rapport par unité communale/date

### Tables pour Groupes Répétitifs

#### `personnel_matin`
Personnel du matin (groupe simple dans le formulaire) :
- Une ligne par catégorie de personnel
- Effectif total, présents, absents, malades, retard, congés
- Observations

#### `personnel_apres_midi`
Personnel de l'après-midi (groupe répétitif dans le formulaire) :
- Peut contenir plusieurs lignes (une par catégorie)
- Mêmes champs que le personnel du matin

#### `personnel_nuit`
Personnel de nuit (groupe répétitif dans le formulaire) :
- Peut contenir plusieurs lignes (une par catégorie)
- Mêmes champs que le personnel du matin et de l'après-midi

#### `collection_circuits`
Circuits de collecte des déchets (groupe répétitif) :
- Nom du circuit, numéro du camion (texte libre)
- Concessionnaire (Ecotra, CDF, Keur Khadim)
- Horaires (début, fin, durée calculée)
- Poids collecté
- Statut (terminé, non terminé, panne)
- Observations

#### `mobilier_urbain`
Mobilier urbain (groupe répétitif) :
- Type de mobilier (PRN, PP, Bacs de rue)
- Nombre de sites, nombre de bacs, bacs levés
- Observation (Levés, Pas Levés)

#### `interventions_ponctuelles`
Interventions ponctuelles (groupe répétitif) :
- Agents mobilisés, pelles mécaniques, tasseuses, camions ciel ouvert
- Quartiers d'intervention

#### `photos_interventions`
Photos des interventions (groupe répétitif dans interventions) :
- Photo avec description
- **Géolocalisation** : Point GPS (PostGIS POINT)

### Tables de Liaison Many-to-Many

#### `daily_reports_difficultes`
Liaison entre rapports et difficultés (select_multiple dans le formulaire)

#### `daily_reports_recommandations`
Liaison entre rapports et recommandations (select_multiple dans le formulaire)

## 🔗 Relations entre Tables

```
daily_reports (1) ──→ (N) personnel_matin
daily_reports (1) ──→ (N) personnel_apres_midi
daily_reports (1) ──→ (N) personnel_nuit
daily_reports (1) ──→ (N) collection_circuits
daily_reports (1) ──→ (N) mobilier_urbain
daily_reports (1) ──→ (N) interventions_ponctuelles
interventions_ponctuelles (1) ──→ (N) photos_interventions

daily_reports ──→ departements (N:1)
daily_reports ──→ unites_communales (N:1)
collection_circuits ──→ concessionnaires (N:1)
collection_circuits ──→ circuit_status (N:1)
personnel_matin ──→ categories_personnel (N:1)
personnel_apres_midi ──→ categories_personnel (N:1)
mobilier_urbain ──→ types_mobilier (N:1)
mobilier_urbain ──→ observations_mobilier (N:1)

daily_reports (N) ──→ (N) difficultes (via daily_reports_difficultes)
daily_reports (N) ──→ (N) recommandations (via daily_reports_recommandations)
```

## 📍 Utilisation de PostGIS

Les champs géographiques utilisent PostGIS avec le système de coordonnées **WGS84 (SRID 4326)** :

- `daily_reports.gps_photo` : Point GPS de la photo de nettoyage
- `photos_interventions.gps_int` : Point GPS des photos d'intervention

### Exemples de requêtes spatiales

```sql
-- Trouver tous les rapports avec photos dans un rayon de 1 km
SELECT * FROM daily_reports
WHERE ST_DWithin(
    gps_photo,
    ST_SetSRID(ST_MakePoint(-17.4677, 14.7167), 4326), -- Point de référence
    0.01 -- ~1 km en degrés
);

-- Extraire les coordonnées GPS des photos d'intervention
SELECT 
    pi.id,
    ST_X(pi.gps_int) AS longitude,
    ST_Y(pi.gps_int) AS latitude,
    pi.desc_int
FROM photos_interventions pi
WHERE pi.gps_int IS NOT NULL;
```

## 📊 Vues Utilitaires

Le schéma inclut des vues pré-calculées pour faciliter l'analyse :

### `v_daily_reports_summary`
Vue récapitulative des rapports avec agrégations :
- Informations département et unité communale
- Compteurs de circuits, mobilier, interventions
- Poids total des circuits
- Difficultés et recommandations agrégées

### `v_collection_circuits_details`
Vue détaillée des circuits avec toutes les informations jointes :
- Détails du concessionnaire
- Statut et métriques

### `v_monthly_stats_by_departement`
Statistiques mensuelles agrégées par département :
- Nombre de rapports et circuits
- Poids total et moyen
- Durée totale et moyenne
- Répartition des statuts de circuits
- Kilométrage balayé

## 🔧 Fonctionnalités Automatiques

### Mise à jour automatique des timestamps
Toutes les tables avec `updated_at` ont un trigger qui met à jour automatiquement ce champ lors des modifications.

## 📈 Optimisations pour l'Analyse

### Index créés
- Index sur les dates pour les requêtes temporelles
- Index sur les clés étrangères pour les jointures
- **Index GIST** sur tous les champs PostGIS pour les requêtes spatiales rapides
- Index composites pour les requêtes fréquentes

### Bonnes pratiques appliquées
- ✅ Normalisation 3NF (troisième forme normale)
- ✅ Contraintes d'intégrité référentielle
- ✅ Contraintes de validation (CHECK)
- ✅ Noms en `snake_case`
- ✅ UUID pour l'identification unique externe
- ✅ Timestamps avec timezone
- ✅ Support multilingue (UTF-8)
- ✅ Correspondance exacte avec le formulaire KoboToolbox

## 🚀 Utilisation avec les Outils BI

### Power BI
1. Connecter à PostgreSQL
2. Utiliser les vues (`v_daily_reports_summary`, `v_monthly_stats_by_departement`)
3. Utiliser les colonnes PostGIS pour les visualisations cartographiques

### Metabase / Superset
1. Se connecter à la base PostgreSQL
2. Les vues sont automatiquement disponibles comme "tables"
3. Utiliser les fonctions PostGIS pour les requêtes spatiales

### Exemple de requête pour tableau de bord

```sql
-- Performance quotidienne par département
SELECT 
    date_rapport,
    departement_nom,
    nombre_circuits,
    poids_total_circuits,
    tonnage_total,
    km_balayes
FROM v_daily_reports_summary
WHERE date_rapport >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY date_rapport DESC, poids_total_circuits DESC;
```

## 🔄 Correspondance avec le Formulaire KoboToolbox

| Groupe Formulaire | Table PostgreSQL | Type |
|-------------------|------------------|------|
| `group_nu8sp57` (Informations générales) | `daily_reports` | Champs directs |
| `group_rr8mq19` (Personnel du matin) | `personnel_matin` | Groupe simple |
| `personnel_apm` (Personnel après-midi) | `personnel_apres_midi` | Groupe répétitif |
| Personnel de nuit | `personnel_nuit` | Groupe répétitif |
| `group_eu7tr68` (Collecte-Généralités) | `daily_reports` | Champs directs |
| `circuits` (Collecte-Circuits) | `collection_circuits` | Groupe répétitif |
| `group_wl43a78` (Caisses polybennes) | `daily_reports` | Champs directs |
| `group_or03u90` (Nettoyage) | `daily_reports` | Champs directs |
| `mobilier` (Mobilier urbain) | `mobilier_urbain` | Groupe répétitif |
| `group_vs5fg16` (Interventions ponctuelles) | `interventions_ponctuelles` | Groupe répétitif |
| `photos_interv` (Photos interventions) | `photos_interventions` | Groupe répétitif dans interventions |
| `group_wi6jl55` (Difficultés/Recommandations) | `daily_reports` + tables de liaison | Select_multiple |

## 📝 Installation

1. **Créer la base de données** (en tant que superutilisateur) :
   ```sql
   CREATE DATABASE sonaged_db WITH ENCODING 'UTF8';
   \c sonaged_db;
   ```

2. **Exécuter le script SQL** :
   ```bash
   psql -U postgres -d sonaged_db -f schema_sonaged.sql
   ```

3. **Vérifier l'installation** :
   ```sql
   SELECT PostGIS_version(); -- Vérifier PostGIS
   \dt -- Lister les tables
   \dv -- Lister les vues
   ```

## 🔐 Sécurité et Permissions

Il est recommandé de créer un utilisateur dédié avec des permissions limitées :

```sql
CREATE USER sonaged_app WITH PASSWORD 'mot_de_passe_securise';
GRANT CONNECT ON DATABASE sonaged_db TO sonaged_app;
GRANT USAGE ON SCHEMA public TO sonaged_app;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO sonaged_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO sonaged_app;
```

## 📞 Support

Pour toute question ou modification du schéma, consulter la documentation PostgreSQL et PostGIS :
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [PostGIS Documentation](https://postgis.net/documentation/)
