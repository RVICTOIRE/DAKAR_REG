# -*- coding: utf-8 -*-

import psycopg2
import json
from datetime import datetime, date
import uuid
from config import DB_CONFIG, RAW_SCHEMA, MART_SCHEMA

# =====================================================
# CLASSE TRANSFORMATEUR
# =====================================================

class RawToMartTransformer:

    def __init__(self):
        self.conn = None
        self.cur = None

    # -------------------------
    # Connexion DB
    # -------------------------
    def connect(self):
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            self.cur = self.conn.cursor()
            print("✓ Connexion à la base de données établie")
        except Exception as e:
            raise Exception(f"Erreur connexion DB : {e}")

    # -------------------------
    # Fermeture DB
    # -------------------------
    def close(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
        print("✓ Connexion fermée")

    # -------------------------
    # Parser date
    # -------------------------
    def parse_date(self, value):
        if not value:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except Exception:
            return None

    # -------------------------
    # Charger RAW Kobo
    # -------------------------
    def fetch_raw_submissions(self):
        self.cur.execute(f"""
            SELECT id, kobo_submission_id, form_data
            FROM {RAW_SCHEMA}.submissions
            WHERE transformed = false
            ORDER BY id
        """)
        return self.cur.fetchall()

    # -------------------------
    # Extraire et insérer circuits
    # -------------------------
    def _insert_circuits_data(self, daily_report_id, form_data):
        """
        Extrait les circuits depuis le tableau 'circuits' de Kobo
        et les insère dans collection_circuits
        """
        try:
            circuits = form_data.get('circuits', [])
            
            for ordre, circuit_data in enumerate(circuits, start=1):
                nom_circuit = circuit_data.get('circuits/nom_circuit')
                camion = circuit_data.get('circuits/camion')
                operateur = circuit_data.get('circuits/operateur')
                heure_debut = circuit_data.get('circuits/heure_debut')
                heure_fin = circuit_data.get('circuits/heure_fin')
                duree = float(circuit_data.get('circuits/DureeCollecte', 0) or 0)
                poids = float(circuit_data.get('circuits/poids_circuit', 0) or 0)
                statut = circuit_data.get('circuits/statut', 'non_termine')
                
                # Convertir le statut Kobo en ID de la table circuit_status
                self.cur.execute("SELECT id FROM circuit_status WHERE code = %s LIMIT 1", (statut,))
                status_row = self.cur.fetchone()
                status_id = status_row[0] if status_row else None
                
                # Récupérer ID du concessionnaire
                self.cur.execute("SELECT id FROM concessionnaires WHERE code = %s LIMIT 1", (operateur,))
                conc_row = self.cur.fetchone()
                concessionnaire_id = conc_row[0] if conc_row else None
                
                # Convertir heures (format ISO 8601 de Kobo: "HH:MM:SS.sssZ")
                if heure_debut:
                    heure_debut = heure_debut.split('.')[0]  # Enlever les millisecondes
                if heure_fin:
                    heure_fin = heure_fin.split('.')[0]
                
                # Insérer le circuit
                self.cur.execute("""
                    INSERT INTO collection_circuits (
                        daily_report_id, ordre, nom_circuit, camion,
                        concessionnaire_id, heure_debut, heure_fin,
                        duree_collecte, poids_circuit, status_id,
                        created_at, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                """, (
                    daily_report_id, ordre, nom_circuit, camion,
                    concessionnaire_id, heure_debut, heure_fin,
                    duree, poids, status_id
                ))
                
        except Exception as e:
            print(f"⚠ Erreur insertion circuits (daily_report_id={daily_report_id}): {e}")

    # -------------------------
    # Extraire et insérer données personnel
    # -------------------------
    def _insert_personnel_data(self, daily_report_id, form_data):
        """
        Extrait les effectifs matin, apm, nuit depuis form_data Kobo
        (groupes répétitifs) et insère dans les tables
        personnel_matin, personnel_apres_midi, personnel_nuit
        """
        try:
            # MATIN : repeat group_rr8mq19
            matin_rows = form_data.get("group_rr8mq19", [])
            for row in matin_rows:
                cat_code = row.get("group_rr8mq19/categorie_apm_001") or row.get("categorie_apm_001")
                effectif = int(row.get("group_rr8mq19/effectif_apm", row.get("effectif_apm", 0)) or 0)
                if effectif <= 0:
                    continue
                presents = int(row.get("group_rr8mq19/present_apm_001", row.get("present_apm_001", 0)) or 0)
                absents = int(row.get("group_rr8mq19/absent_apm", row.get("absent_apm", 0)) or 0)
                malades = int(row.get("group_rr8mq19/malade_apm", row.get("malade_apm", 0)) or 0)
                conges = int(row.get("group_rr8mq19/conge_apm", row.get("conge_apm", 0)) or 0)
                retard = int(row.get("group_rr8mq19/reserve_apm", row.get("reserve_apm", 0)) or 0)
                obs = row.get("group_rr8mq19/observation_personnel_001", row.get("observation_personnel_001"))

                categorie_id = None
                if cat_code:
                    self.cur.execute(
                        "SELECT id FROM categories_personnel WHERE code = %s LIMIT 1",
                        (cat_code,)
                    )
                    r = self.cur.fetchone()
                    if r:
                        categorie_id = r[0]

                self.cur.execute("""
                    INSERT INTO personnel_matin (
                        daily_report_id, categorie_id, effectif_total,
                        presents, absents, malades, retard, conges,
                        observations, created_at, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                """, (
                    daily_report_id, categorie_id, effectif,
                    presents, absents, malades, retard, conges, obs
                ))

            # APRÈS-MIDI : repeat personnel_apm
            apm_rows = form_data.get("personnel_apm", [])
            for ordre, row in enumerate(apm_rows, start=1):
                cat_code = row.get("personnel_apm/categorie_apm_002") or row.get("categorie_apm_002")
                effectif = int(row.get("personnel_apm/effectif_apm_001", row.get("effectif_apm_001", 0)) or 0)
                if effectif <= 0:
                    continue
                presents = int(row.get("personnel_apm/present_apm", row.get("present_apm", 0)) or 0)
                absents = int(row.get("personnel_apm/absent_apm_001_001", row.get("absent_apm_001_001", 0)) or 0)
                malades = int(row.get("personnel_apm/malade_apm_001_001", row.get("malade_apm_001_001", 0)) or 0)
                conges = int(row.get("personnel_apm/conge_apm_001", row.get("conge_apm_001", 0)) or 0)
                retard = int(row.get("personnel_apm/reserve_apm_002", row.get("reserve_apm_002", 0)) or 0)
                obs = row.get("personnel_apm/observation_personnel_002", row.get("observation_personnel_002"))

                categorie_id = None
                if cat_code:
                    self.cur.execute(
                        "SELECT id FROM categories_personnel WHERE code = %s LIMIT 1",
                        (cat_code,)
                    )
                    r = self.cur.fetchone()
                    if r:
                        categorie_id = r[0]

                self.cur.execute("""
                    INSERT INTO personnel_apres_midi (
                        daily_report_id, ordre, categorie_id, effectif_total,
                        presents, absents, malades, conges, retard,
                        observations, created_at, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                """, (
                    daily_report_id, ordre, categorie_id, effectif,
                    presents, absents, malades, conges, retard, obs
                ))

            # NUIT : repeat group_ag3nl18
            nuit_rows = form_data.get("group_ag3nl18", [])
            for ordre, row in enumerate(nuit_rows, start=1):
                cat_code = row.get("group_ag3nl18/categorie_apm") or row.get("categorie_apm")
                effectif = int(row.get("group_ag3nl18/effectif_apm_001_001", row.get("effectif_apm_001_001", 0)) or 0)
                if effectif <= 0:
                    continue
                presents = int(row.get("group_ag3nl18/present_apm_002", row.get("present_apm_002", 0)) or 0)
                absents = int(row.get("group_ag3nl18/absent_apm_001", row.get("absent_apm_001", 0)) or 0)
                malades = int(row.get("group_ag3nl18/malade_apm_001", row.get("malade_apm_001", 0)) or 0)
                conges = int(row.get("group_ag3nl18/conge_apm_001_001", row.get("conge_apm_001_001", 0)) or 0)
                retard = int(row.get("group_ag3nl18/reserve_apm_002_001", row.get("reserve_apm_002_001", 0)) or 0)
                obs = row.get("group_ag3nl18/observation_personnel", row.get("observation_personnel"))

                categorie_id = None
                if cat_code:
                    self.cur.execute(
                        "SELECT id FROM categories_personnel WHERE code = %s LIMIT 1",
                        (cat_code,)
                    )
                    r = self.cur.fetchone()
                    if r:
                        categorie_id = r[0]

                self.cur.execute("""
                    INSERT INTO personnel_nuit (
                        daily_report_id, ordre, categorie_id, effectif_total,
                        presents, absents, malades, conges, retard,
                        observations, created_at, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                """, (
                    daily_report_id, ordre, categorie_id, effectif,
                    presents, absents, malades, conges, retard, obs
                ))

        except Exception as e:
            print(f"⚠ Erreur insertion personnel (daily_report_id={daily_report_id}): {e}")

    # -------------------------
    # Extraire et insérer mobilier urbain
    # -------------------------
    def _insert_mobilier_data(self, daily_report_id, form_data):
        try:
            mobilier_list = form_data.get("mobilier", [])
            for ordre, m in enumerate(mobilier_list, start=1):
                type_code = m.get("mobilier/type_mobilier") or m.get("type_mobilier")
                nb_sites = int(m.get("mobilier/nb_sites", m.get("nb_sites", 0)) or 0)
                nb_bacs = int(m.get("mobilier/nb_bacs", m.get("nb_bacs", 0)) or 0)
                bacs_leves = int(m.get("mobilier/bacs_leves", m.get("bacs_leves", 0)) or 0)
                obs_code = m.get("mobilier/Observation") or m.get("Observation")

                type_id = None
                if type_code:
                    self.cur.execute(
                        "SELECT id FROM types_mobilier WHERE code = %s LIMIT 1",
                        (type_code,)
                    )
                    r = self.cur.fetchone()
                    if r:
                        type_id = r[0]

                observation_id = None
                if obs_code:
                    self.cur.execute(
                        "SELECT id FROM observations_mobilier WHERE code = %s LIMIT 1",
                        (obs_code,)
                    )
                    r = self.cur.fetchone()
                    if r:
                        observation_id = r[0]

                self.cur.execute("""
                    INSERT INTO mobilier_urbain (
                        daily_report_id, ordre, type_mobilier_id,
                        nb_sites, nb_bacs, bacs_leves, observation_id,
                        created_at, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                """, (
                    daily_report_id, ordre, type_id,
                    nb_sites, nb_bacs, bacs_leves, observation_id
                ))
        except Exception as e:
            print(f"⚠ Erreur insertion mobilier (daily_report_id={daily_report_id}): {e}")

    # -------------------------
    # Extraire et insérer interventions ponctuelles + photos
    # -------------------------
    def _insert_interventions_data(self, daily_report_id, form_data):
        try:
            interventions = form_data.get("group_vs5fg16", [])
            for ordre, inter in enumerate(interventions, start=1):
                agents = int(inter.get("group_vs5fg16/agents_interv", inter.get("agents_interv", 0)) or 0)
                pelles = int(inter.get("group_vs5fg16/pelles", inter.get("pelles", 0)) or 0)
                tasseuses = int(inter.get("group_vs5fg16/tasseuses", inter.get("tasseuses", 0)) or 0)
                camions = int(inter.get("group_vs5fg16/camions", inter.get("camions", 0)) or 0)
                quartiers = inter.get("group_vs5fg16/quartiers", inter.get("quartiers"))

                # Insérer l'intervention
                self.cur.execute("""
                    INSERT INTO interventions_ponctuelles (
                        daily_report_id, ordre, agents_interv, pelles,
                        tasseuses, camions, quartiers, created_at, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                    RETURNING id
                """, (
                    daily_report_id, ordre, agents, pelles,
                    tasseuses, camions, quartiers
                ))
                inter_id = self.cur.fetchone()[0]

                # Photos associées
                photos = inter.get("photos_interv", [])
                for ordre_p, p in enumerate(photos, start=1):
                    photo_file = p.get("photos_interv/photo_int") or p.get("photo_int")
                    desc = p.get("photos_interv/desc_int") or p.get("desc_int")
                    gps = p.get("photos_interv/gps_int") or p.get("gps_int")

                    # On laisse gps_int à NULL pour l'instant si on ne parse pas le point
                    self.cur.execute("""
                        INSERT INTO photos_interventions (
                            intervention_id, ordre, photo_int, desc_int,
                            created_at, updated_at
                        )
                        VALUES (%s, %s, %s, %s, NOW(), NOW())
                    """, (
                        inter_id, ordre_p, photo_file, desc
                    ))
        except Exception as e:
            print(f"⚠ Erreur insertion interventions (daily_report_id={daily_report_id}): {e}")

    # -------------------------
    # Extraire et insérer difficultés / recommandations
    # -------------------------
    def _insert_difficultes_recommandations(self, daily_report_id, form_data):
        try:
            # Difficultés (select_multiple)
            diff_val = form_data.get("group_wi6jl55/difficultes") or form_data.get("difficultes")
            if diff_val:
                if isinstance(diff_val, str):
                    codes = [c for c in diff_val.replace(",", " ").split() if c]
                elif isinstance(diff_val, list):
                    codes = diff_val
                else:
                    codes = []
                for code in codes:
                    self.cur.execute(
                        "SELECT id FROM difficultes WHERE code = %s LIMIT 1",
                        (code,)
                    )
                    r = self.cur.fetchone()
                    if not r:
                        continue
                    difficulte_id = r[0]
                    self.cur.execute("""
                        INSERT INTO daily_reports_difficultes (
                            daily_report_id, difficulte_id
                        ) VALUES (%s, %s)
                        ON CONFLICT DO NOTHING
                    """, (daily_report_id, difficulte_id))

            # Recommandations (select_multiple)
            rec_val = form_data.get("group_wi6jl55/recommandations") or form_data.get("recommandations")
            if rec_val:
                if isinstance(rec_val, str):
                    codes = [c for c in rec_val.replace(",", " ").split() if c]
                elif isinstance(rec_val, list):
                    codes = rec_val
                else:
                    codes = []
                for code in codes:
                    self.cur.execute(
                        "SELECT id FROM recommandations WHERE code = %s LIMIT 1",
                        (code,)
                    )
                    r = self.cur.fetchone()
                    if not r:
                        continue
                    recommandation_id = r[0]
                    self.cur.execute("""
                        INSERT INTO daily_reports_recommandations (
                            daily_report_id, recommandation_id
                        ) VALUES (%s, %s)
                        ON CONFLICT DO NOTHING
                    """, (daily_report_id, recommandation_id))

            # Champs texte libres
            autres_diff = form_data.get("group_wi6jl55/Autres_difficult_s") or form_data.get("Autres_difficult_s")
            autres_rec = form_data.get("group_wi6jl55/autres_rec") or form_data.get("autres_rec")

            if autres_diff or autres_rec:
                self.cur.execute("""
                    UPDATE daily_reports
                    SET autres_difficultes = COALESCE(%s, autres_difficultes),
                        autres_recommandations = COALESCE(%s, autres_recommandations)
                    WHERE id = %s
                """, (autres_diff, autres_rec, daily_report_id))

        except Exception as e:
            print(f"⚠ Erreur insertion difficultés/recommandations (daily_report_id={daily_report_id}): {e}")

    # -------------------------
    # Charger RAW Kobo
    # -------------------------
    def fetch_raw_submissions(self):
        self.cur.execute(f"""
            SELECT id, kobo_submission_id, form_data
            FROM {RAW_SCHEMA}.submissions
            WHERE transformed = false
            ORDER BY id
        """)
        return self.cur.fetchall()

    # -------------------------
    # Transformation principale
    # -------------------------
    def transform(self):
        rows = self.fetch_raw_submissions()
        print(f"📊 {len(rows)} soumission(s) en attente de transformation")

        success = 0
        errors = 0

        for row in rows:
            raw_id, kobo_id, form_data = row

            try:
                if isinstance(form_data, str):
                    form_data = json.loads(form_data)

                # -------------------------
                # EXTRACTION DES CHAMPS
                # -------------------------
                date_rapport = self.parse_date(
                    form_data.get("group_nu8sp57/date_rapport")
                )

                if not date_rapport:
                    raise Exception("Date du rapport manquante")

                departement = form_data.get("group_nu8sp57/D_partement", "inconnu")
                unite_communale_code = form_data.get("group_nu8sp57/unite")

                # Si pas d'unité communale (département != dakar), utiliser le département comme UC
                if not unite_communale_code:
                    unite_communale_code = f"{departement}_default"
                    print(f"⚠ UC manquante pour {kobo_id}, utilisation de UC par défaut: {unite_communale_code}")

                # -------------------------
                # RÉCUPÉRER / CRÉER DÉPARTEMENT
                # -------------------------
                self.cur.execute("""
                    SELECT id FROM departements
                    WHERE LOWER(nom) = LOWER(%s)
                """, (departement,))

                dep = self.cur.fetchone()

                if dep:
                    departement_id = dep[0]
                else:
                    self.cur.execute("""
                        INSERT INTO departements (nom)
                        VALUES (%s)
                        RETURNING id
                    """, (departement,))
                    departement_id = self.cur.fetchone()[0]

                # -------------------------
                # RÉCUPÉRER / CRÉER UNITÉ COMMUNALE
                # -------------------------
                self.cur.execute("""
                    SELECT id FROM unites_communales
                    WHERE code = %s OR LOWER(nom) = LOWER(%s)
                    LIMIT 1
                """, (unite_communale_code, unite_communale_code))

                uc = self.cur.fetchone()

                if uc:
                    unite_communale_id = uc[0]
                else:
                    # Créer l'UC si elle n'existe pas
                    nom_uc = unite_communale_code.replace("_default", "").title()
                    self.cur.execute("""
                        INSERT INTO unites_communales (code, nom, departement_id)
                        VALUES (%s, %s, %s)
                        RETURNING id
                    """, (unite_communale_code, nom_uc, departement_id))
                    unite_communale_id = self.cur.fetchone()[0]
                    print(f"✓ UC créée : {nom_uc} (code: {unite_communale_code})")

                # -------------------------
                # EXTRACTION COLLECTE / CAISSES / NETTOIEMENT
                # -------------------------
                circuits_planifies = int(form_data.get("group_eu7tr68/circuits_planifies", 0) or 0)
                circuits_collectes = int(form_data.get("group_eu7tr68/circuits_collectes", 0) or 0)
                tonnage_total = float(form_data.get("group_eu7tr68/tonnage_total", 0) or 0)
                depots_recurrents = int(form_data.get("group_eu7tr68/depots_recurrents", 0) or 0)
                depots_recurrents_leves = int(form_data.get("group_eu7tr68/depots_recurrents_leves", 0) or 0)
                depots_sauvages = int(form_data.get("group_eu7tr68/depots_sauvages", 0) or 0)
                depots_sauvages_traites = int(form_data.get("group_eu7tr68/depots_sauvages_traites", 0) or 0)

                sites_caisse = int(form_data.get("group_wl43a78/sites_caisse", 0) or 0)
                nb_caisses = int(form_data.get("group_wl43a78/nb_caisses", 0) or 0)
                caisses_levees = int(form_data.get("group_wl43a78/caisses_levees", 0) or 0)
                poids_caisses = float(form_data.get("group_wl43a78/poids_caisses", 0) or 0)

                # Nettoiement : certaines exports Kobo stockent les champs
                # avec ou sans préfixe de groupe, on gère donc les deux cas.
                nombre_circuits_planifies = int(
                    form_data.get("group_or03u90/Nombre_de_circuits_planifi_s",
                                  form_data.get("Nombre_de_circuits_planifi_s", 0)) or 0
                )
                circuits_balayage = int(
                    form_data.get("group_or03u90/circuits_balayage",
                                  form_data.get("circuits_balayage", 0)) or 0
                )
                km_planifies = float(
                    form_data.get("group_or03u90/km_planifies",
                                  form_data.get("km_planifies", 0)) or 0
                )
                km_balayes = float(
                    form_data.get("group_or03u90/km_balayes",
                                  form_data.get("km_balayes", 0)) or 0
                )
                km_desensable = float(
                    form_data.get("group_or03u90/km_desensable",
                                  form_data.get("km_desensable", 0)) or 0
                )

                # -------------------------
                # INSERTION DAILY_REPORTS
                # -------------------------
                self.cur.execute("""
                    INSERT INTO daily_reports (
                        uuid,
                        date_rapport,
                        departement_id,
                        unite_communale_id,
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
                        created_at,
                        updated_at,
                        kobo_submission_id
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), %s)
                    RETURNING id
                """, (
                    str(uuid.uuid4()),
                    date_rapport,
                    departement_id,
                    unite_communale_id,
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
                    kobo_id
                ))

                daily_report_id = self.cur.fetchone()[0]

                # -------------------------
                # EXTRACTION & INSERTION CIRCUITS
                # -------------------------
                self._insert_circuits_data(daily_report_id, form_data)

                # -------------------------
                # EXTRACTION & INSERTION PERSONNEL
                # -------------------------
                self._insert_personnel_data(daily_report_id, form_data)

                # -------------------------
                # EXTRACTION & INSERTION MOBILIER
                # -------------------------
                self._insert_mobilier_data(daily_report_id, form_data)

                # -------------------------
                # EXTRACTION & INSERTION INTERVENTIONS
                # -------------------------
                self._insert_interventions_data(daily_report_id, form_data)

                # -------------------------
                # EXTRACTION & INSERTION DIFFICULTÉS / RECOMMANDATIONS
                # -------------------------
                self._insert_difficultes_recommandations(daily_report_id, form_data)

                # -------------------------
                # MARQUER COMME TRANSFORMÉ
                # -------------------------
                self.cur.execute(f"""
                    UPDATE {RAW_SCHEMA}.submissions
                    SET transformed = true,
                        transformed_at = NOW()
                    WHERE id = %s
                """, (raw_id,))

                self.conn.commit()
                success += 1
                print(f"✓ Soumission {kobo_id} transformée")

            except Exception as e:
                self.conn.rollback()
                errors += 1
                import traceback
                print(f"✗ Erreur transformation {kobo_id} : {e}")
                print(traceback.format_exc())

        print(f"\n✓ Transformation terminée : {success} transformée(s), {errors} erreur(s)")

# =====================================================
# MAIN
# =====================================================

def main():
    transformer = RawToMartTransformer()
    try:
        transformer.connect()
        transformer.transform()
    except Exception as e:
        print(f"✗ Erreur fatale : {e}")
    finally:
        transformer.close()

if __name__ == "__main__":
    main()
