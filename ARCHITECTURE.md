# Architecture du Système SONAGED

## Vue d'ensemble

Architecture en deux couches (RAW → MART) pour garantir la résilience aux modifications du formulaire Kobo.

## Schéma RAW

**Fichier** : `schema_raw.sql`

### Tables principales

- `raw_kobo.submissions` : Soumissions brutes avec JSONB complet
- `raw_kobo.circuits` : Circuits (groupe répétitif)
- `raw_kobo.personnel_apres_midi` : Personnel après-midi (groupe répétitif)
- `raw_kobo.mobilier_urbain` : Mobilier urbain (groupe répétitif)
- `raw_kobo.interventions_ponctuelles` : Interventions (groupe répétitif)
- `raw_kobo.photos_interventions` : Photos des interventions (groupe répétitif imbriqué)

### Caractéristiques

- ✅ Capture **toutes** les données brutes (JSONB)
- ✅ Structure flexible (ajoute automatiquement les nouveaux champs)
- ✅ Préservation de l'historique complet
- ✅ Pas de perte de données

## Schéma MART

**Fichier** : `schema_mart.sql`

### Tables principales

- `daily_reports` : Rapports journaliers normalisés
- `personnel_matin` : Personnel du matin
- `personnel_apres_midi` : Personnel après-midi
- `personnel_nuit` : Personnel de nuit
- `collection_circuits` : Circuits de collecte
- `mobilier_urbain` : Mobilier urbain
- `interventions_ponctuelles` : Interventions
- `photos_interventions` : Photos géolocalisées

### Caractéristiques

- ✅ Structure stable pour Streamlit
- ✅ Données normalisées et optimisées
- ✅ Vues analytiques pré-calculées
- ✅ Index pour performance

## Flux de données

```
1. Collecte Kobo → Export JSON/CSV
2. Import Kobo → RAW (import_kobo_to_raw.py)
3. Transformation RAW → MART (transform_raw_to_mart.py)
4. Visualisation MART → Streamlit Dashboard
```

## Résilience aux modifications

| Modification Kobo | Impact RAW | Impact MART | Impact Streamlit |
|-------------------|------------|-------------|------------------|
| Nouveau champ | ✅ Capturé dans JSONB | Optionnel (ajout colonne) | Aucun |
| Champ supprimé | ✅ Reste dans JSONB | Colonne NULL | Aucun |
| Nouveau repeat | ✅ Nouvelle table RAW | Nouvelle table MART | Optionnel |
| Renommage champ | ✅ Nouveau nom dans JSONB | Mapping à ajuster | Aucun |

## Scripts

### import_kobo_to_raw.py

- Parse les exports JSON/CSV de Kobo
- Insère dans RAW avec JSONB complet
- Extrait les groupes répétitifs
- Gère les erreurs et logs

### transform_raw_to_mart.py

- Lit les données RAW
- Transforme vers MART normalisé
- Gère les lookups (départements, concessionnaires, etc.)
- Marque comme importé

## Dashboard Streamlit

**Structure** : `streamlit_app/`

- `app.py` : Application principale
- `pages/` : Pages du dashboard
- `utils/database.py` : Connexion DB
- `utils/queries.py` : Requêtes SQL réutilisables

### Pages disponibles

1. Vue d'ensemble
2. Analyse temporelle
3. Analyse spatiale
4. Personnel
5. Concessionnaires

## Avantages de cette architecture

1. **Résilience** : Modifications Kobo n'affectent pas Streamlit
2. **Flexibilité** : Nouveaux champs capturés automatiquement
3. **Performance** : MART optimisé pour requêtes
4. **Historique** : RAW préserve toutes les données
5. **Maintenabilité** : Séparation claire des responsabilités
