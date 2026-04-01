"""
Script d'import des données KoboToolbox vers le schéma RAW
Supporte les formats JSON et CSV d'export Kobo
"""

import json
import csv
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
from typing import Dict, List, Any, Optional
import sys
import os
from pathlib import Path
from config import DB_CONFIG

DB_NAME = DB_CONFIG["database"]

# Configuration de la base de données
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'sonaged_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '')
}


class KoboRawImporter:
    """Importe les données Kobo vers le schéma RAW"""
    
    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config
        self.conn = None
        
    def connect(self):
        """Établit la connexion à la base de données"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.conn.autocommit = False
            print("✓ Connexion à la base de données établie")
        except Exception as e:
            print(f"✗ Erreur de connexion : {e}")
            raise
    
    def close(self):
        """Ferme la connexion"""
        if self.conn:
            self.conn.close()
            print("✓ Connexion fermée")
    
    def parse_geopoint(self, geopoint_str: Optional[str]) -> Optional[Dict[str, float]]:
        """
        Parse un géopoint Kobo au format "latitude longitude altitude accuracy"
        Retourne un dict avec lat, lon, alt, acc
        """
        if not geopoint_str or geopoint_str.strip() == '':
            return None
        
        try:
            parts = geopoint_str.strip().split()
            if len(parts) >= 2:
                return {
                    'latitude': float(parts[0]),
                    'longitude': float(parts[1]),
                    'altitude': float(parts[2]) if len(parts) > 2 else None,
                    'accuracy': float(parts[3]) if len(parts) > 3 else None
                }
        except (ValueError, IndexError):
            pass
        
        return None
    
    def extract_repeat_groups(self, submission_data: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """
        Extrait les groupes répétitifs de la soumission Kobo
        Format Kobo : les repeats sont dans des colonnes séparées avec index
        """
        repeat_groups = {
            'personnel_apm': [],
            'circuits': [],
            'mobilier': [],
            'interventions': []
        }
        
        # Détecter les groupes répétitifs par préfixe
        personnel_apm_fields = {}
        circuits_fields = {}
        mobilier_fields = {}
        interventions_fields = {}
        
        for key, value in submission_data.items():
            if key.startswith('personnel_apm') or key.startswith('categorie_apm'):
                # Personnel après-midi
                base_key = key.replace('personnel_apm/', '').replace('categorie_apm/', '')
                if '/' in key:
                    # Format avec index : groupe/index/champ
                    parts = key.split('/')
                    if len(parts) >= 3:
                        index = int(parts[1]) if parts[1].isdigit() else 0
                        field_name = '/'.join(parts[2:])
                        if index not in personnel_apm_fields:
                            personnel_apm_fields[index] = {}
                        personnel_apm_fields[index][field_name] = value
                else:
                    # Format simple
                    if 0 not in personnel_apm_fields:
                        personnel_apm_fields[0] = {}
                    personnel_apm_fields[0][base_key] = value
            
            elif key.startswith('circuits/') or key.startswith('nom_circuit') or key.startswith('camion'):
                # Circuits
                base_key = key.replace('circuits/', '')
                if '/' in key and key.count('/') >= 2:
                    parts = key.split('/')
                    index = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
                    field_name = '/'.join(parts[2:]) if len(parts) > 2 else base_key
                    if index not in circuits_fields:
                        circuits_fields[index] = {}
                    circuits_fields[index][field_name] = value
                else:
                    if 0 not in circuits_fields:
                        circuits_fields[0] = {}
                    circuits_fields[0][base_key] = value
            
            elif key.startswith('mobilier/'):
                # Mobilier urbain
                base_key = key.replace('mobilier/', '')
                if '/' in key and key.count('/') >= 2:
                    parts = key.split('/')
                    index = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
                    field_name = '/'.join(parts[2:]) if len(parts) > 2 else base_key
                    if index not in mobilier_fields:
                        mobilier_fields[index] = {}
                    mobilier_fields[index][field_name] = value
            
            elif key.startswith('group_vs5fg16/') or key.startswith('interventions/'):
                # Interventions ponctuelles
                base_key = key.replace('group_vs5fg16/', '').replace('interventions/', '')
                if '/' in key and key.count('/') >= 2:
                    parts = key.split('/')
                    index = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
                    field_name = '/'.join(parts[2:]) if len(parts) > 2 else base_key
                    if index not in interventions_fields:
                        interventions_fields[index] = {}
                    interventions_fields[index][field_name] = value
        
        # Convertir en listes
        repeat_groups['personnel_apm'] = [
            {'ordre': idx, 'data': data} 
            for idx, data in sorted(personnel_apm_fields.items())
        ]
        repeat_groups['circuits'] = [
            {'ordre': idx, 'data': data} 
            for idx, data in sorted(circuits_fields.items())
        ]
        repeat_groups['mobilier'] = [
            {'ordre': idx, 'data': data} 
            for idx, data in sorted(mobilier_fields.items())
        ]
        repeat_groups['interventions'] = [
            {'ordre': idx, 'data': data} 
            for idx, data in sorted(interventions_fields.items())
        ]
        
        return repeat_groups
    
    def import_json_submission(self, submission: Dict[str, Any]) -> Optional[int]:
        """
        Importe une soumission JSON dans RAW
        Retourne l'ID de la soumission RAW créée
        """
        cursor = self.conn.cursor()
        
        try:
            # Extraire les métadonnées
            kobo_submission_id = submission.get('_id') or submission.get('_uuid') or submission.get('meta/instanceID')
            form_version = submission.get('_version') or submission.get('__version__')
            form_id = submission.get('_xform_id_string')
            device_id = submission.get('_device_id')
            username = submission.get('_submitted_by')
            instance_id = submission.get('meta/instanceID')
            
            # Date de soumission
            submission_date_str = submission.get('_submission_time') or submission.get('_submitted_date')
            if submission_date_str:
                try:
                    submission_date = datetime.fromisoformat(submission_date_str.replace('Z', '+00:00'))
                except:
                    submission_date = datetime.now()
            else:
                submission_date = datetime.now()
            
            # Vérifier si la soumission existe déjà
            cursor.execute("""
                SELECT id FROM raw_kobo.submissions 
                WHERE kobo_submission_id = %s
            """, (kobo_submission_id,))
            
            existing = cursor.fetchone()
            if existing:
                print(f"  ⚠ Soumission {kobo_submission_id} déjà importée (ID: {existing[0]})")
                return existing[0]
            
            # Insérer la soumission principale
            cursor.execute("""
                INSERT INTO raw_kobo.submissions (
                    kobo_submission_id, submission_date, form_data,
                    form_version, form_id, device_id, username, instance_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                kobo_submission_id,
                submission_date,
                json.dumps(submission),
                form_version,
                form_id,
                device_id,
                username,
                instance_id
            ))
            
            submission_id = cursor.fetchone()[0]
            
            # Extraire et insérer les groupes répétitifs
            repeat_groups = self.extract_repeat_groups(submission)
            
            # Personnel après-midi
            for item in repeat_groups['personnel_apm']:
                cursor.execute("""
                    INSERT INTO raw_kobo.personnel_apres_midi 
                    (submission_id, ordre, personnel_data)
                    VALUES (%s, %s, %s)
                """, (submission_id, item['ordre'], json.dumps(item['data'])))
            
            # Circuits
            for item in repeat_groups['circuits']:
                cursor.execute("""
                    INSERT INTO raw_kobo.circuits 
                    (submission_id, ordre, circuit_data)
                    VALUES (%s, %s, %s)
                """, (submission_id, item['ordre'], json.dumps(item['data'])))
            
            # Mobilier urbain
            for item in repeat_groups['mobilier']:
                cursor.execute("""
                    INSERT INTO raw_kobo.mobilier_urbain 
                    (submission_id, ordre, mobilier_data)
                    VALUES (%s, %s, %s)
                """, (submission_id, item['ordre'], json.dumps(item['data'])))
            
            # Interventions ponctuelles (avec photos imbriquées)
            for item in repeat_groups['interventions']:
                cursor.execute("""
                    INSERT INTO raw_kobo.interventions_ponctuelles 
                    (submission_id, ordre, intervention_data)
                    VALUES (%s, %s, %s)
                    RETURNING id
                """, (submission_id, item['ordre'], json.dumps(item['data'])))
                
                intervention_id = cursor.fetchone()[0]
                
                # Extraire les photos de cette intervention
                intervention_data = item['data']
                photos_data = intervention_data.get('photos_interv', [])
                if isinstance(photos_data, list):
                    for photo_idx, photo_item in enumerate(photos_data):
                        cursor.execute("""
                            INSERT INTO raw_kobo.photos_interventions 
                            (intervention_id, ordre, photo_data)
                            VALUES (%s, %s, %s)
                        """, (intervention_id, photo_idx, json.dumps(photo_item)))
            
            self.conn.commit()
            print(f"  ✓ Soumission {kobo_submission_id} importée (ID: {submission_id})")
            return submission_id
            
        except Exception as e:
            self.conn.rollback()
            print(f"  ✗ Erreur lors de l'import : {e}")
            
            # Logger l'erreur
            try:
                cursor.execute("""
                    INSERT INTO raw_kobo.import_errors 
                    (submission_id, error_type, error_message, error_details)
                    VALUES (%s, %s, %s, %s)
                """, (
                    submission_id if 'submission_id' in locals() else None,
                    type(e).__name__,
                    str(e),
                    json.dumps({'submission': kobo_submission_id})
                ))
                self.conn.commit()
            except:
                pass
            
            return None
        finally:
            cursor.close()
    
    def import_json_file(self, json_file: str):
        """Importe un fichier JSON d'export Kobo"""
        print(f"\n📥 Import du fichier : {json_file}")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Kobo export peut être une liste ou un dict avec une clé 'results'
        if isinstance(data, dict):
            submissions = data.get('results', [data])
        else:
            submissions = data if isinstance(data, list) else [data]
        
        print(f"  📊 {len(submissions)} soumission(s) trouvée(s)")
        
        imported = 0
        errors = 0
        
        for submission in submissions:
            result = self.import_json_submission(submission)
            if result:
                imported += 1
            else:
                errors += 1
        
        print(f"\n✓ Import terminé : {imported} importée(s), {errors} erreur(s)")
        return imported, errors
    
    def import_csv_file(self, csv_file: str):
        """Importe un fichier CSV d'export Kobo"""
        print(f"\n📥 Import du fichier CSV : {csv_file}")
        
        # CSV Kobo nécessite un traitement spécial
        # Les groupes répétitifs sont dans des colonnes séparées
        # Format: groupe/index/champ
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        print(f"  📊 {len(rows)} ligne(s) trouvée(s)")
        
        # Convertir chaque ligne CSV en format JSON pour traitement uniforme
        imported = 0
        errors = 0
        
        for row in rows:
            # Convertir la ligne CSV en dict JSON-like
            submission_dict = dict(row)
            
            # Ajouter les métadonnées si présentes
            if '_id' not in submission_dict:
                submission_dict['_id'] = submission_dict.get('_uuid') or submission_dict.get('meta/instanceID')
            
            result = self.import_json_submission(submission_dict)
            if result:
                imported += 1
            else:
                errors += 1
        
        print(f"\n✓ Import terminé : {imported} importée(s), {errors} erreur(s)")
        return imported, errors


def main():
    """Point d'entrée principal"""
    if len(sys.argv) < 2:
        print("Usage: python import_kobo_to_raw.py <fichier_json_ou_csv> [fichier2] ...")
        print("\nExemples:")
        print("  python import_kobo_to_raw.py export_kobo.json")
        print("  python import_kobo_to_raw.py export_kobo.csv")
        print("  python import_kobo_to_raw.py *.json")
        sys.exit(1)
    
    importer = KoboRawImporter(DB_CONFIG)
    
    try:
        importer.connect()
        
        for file_path in sys.argv[1:]:
            path = Path(file_path)
            if not path.exists():
                print(f"✗ Fichier non trouvé : {file_path}")
                continue
            
            if path.suffix.lower() == '.json':
                importer.import_json_file(str(path))
            elif path.suffix.lower() == '.csv':
                importer.import_csv_file(str(path))
            else:
                print(f"✗ Format non supporté : {file_path}")
        
    except Exception as e:
        print(f"✗ Erreur fatale : {e}")
        sys.exit(1)
    finally:
        importer.close()


if __name__ == '__main__':
    main()
