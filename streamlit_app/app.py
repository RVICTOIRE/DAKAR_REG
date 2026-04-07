"""
Application principale Streamlit - Dashboard SONAGED
Dashboard professionnel pour la gestion des déchets municipaux
Version: 1.1 - Performance améliorée
"""

import streamlit as st
from datetime import datetime, timedelta
import sys
import os
import pandas as pd

# Ajouter le chemin des utilitaires
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.database import get_connection, test_connection, execute_query
from utils.queries import (
    QUERY_DAILY_SUMMARY,
    QUERY_KPI_COVERAGE,
    QUERY_KPI_AVERAGE_DURATION,
    QUERY_ALERTS_ANOMALIES,
    QUERY_PERFORMANCE_BY_TRUCK,
    QUERY_PERFORMANCE_BY_TRUCK_SIMPLE,
    QUERY_PERFORMANCE_BY_UC,
    QUERY_PERFORMANCE_TRENDS,
    QUERY_EFFICIENCY_METRICS,
    QUERY_CIRCUITS_DETAILS
)

# Configuration de la page
st.set_page_config(
    page_title="SONAGED Dashboard",
    page_icon="🗑️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# # Configuration de la page
# st.set_page_config(
#     page_title="SONAGED Dashboard",
#     page_icon="🗑️",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# Style personnalisé professionnel - Charte graphique SONAGED
st.markdown("""
    <style>
    /* ============================================================ */
    /* VARIABLES COULEURS - CHARTE GRAPHIQUE SONAGED */
    /* ============================================================ */
    :root {
        --bleu-nuit: #1a4a7a;
        --vert-emeraude: #2ecc71;
        --gris-clair: #f8f9fa;
        --rouge-alerte: #e74c3c;
        --blanc: #ffffff;
        --gris-moyen: #ecf0f1;
    }
    
    /* ============================================================ */
    /* BODY ET ARRIÈRE-PLANS */
    /* ============================================================ */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* ============================================================ */
    /* SIDEBAR */
    /* ============================================================ */
    [data-testid="stSidebar"] {
        background-color: #2c3e50;
        color: white;
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 {
        color: #2ecc71;
        border-bottom: 3px solid #2ecc71;
        padding-bottom: 0.5rem;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #ecf0f1;
    }
    
    [data-testid="stSidebar"] label {
        color: #ecf0f1;
        font-weight: 500;
    }
    
    /* ============================================================ */
    /* EN-TÊTES ET TITRES */
    /* ============================================================ */
    .main-header {
        font-size: 2.8rem;
        font-weight: 900;
        color: #1a4a7a;
        text-align: center;
        padding: 1.5rem 0;
        margin-bottom: 2rem;
        border-bottom: 4px solid #2ecc71;
        letter-spacing: -0.5px;
    }
    
    h1 {
        color: #1a4a7a;
        border-bottom: 3px solid #2ecc71;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    
    h2 {
        color: #1a4a7a;
        margin-top: 1.5rem;
    }
    
    h3 {
        color: #2c3e50;
        font-weight: 700;
    }
    
    /* ============================================================ */
    /* CARTES KPI */
    /* ============================================================ */
    .kpi-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-left: 5px solid #1a4a7a;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .kpi-card:hover {
        box-shadow: 0 6px 16px rgba(26, 74, 122, 0.12);
        transform: translateY(-2px);
    }
    
    .kpi-card-success {
        border-left-color: #2ecc71;
    }
    
    .kpi-card-warning {
        border-left-color: #f39c12;
    }
    
    .kpi-card-danger {
        border-left-color: #e74c3c;
    }
    
    .kpi-label {
        font-size: 0.9rem;
        color: #7f8c8d;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    
    .kpi-value {
        font-size: 2.2rem;
        font-weight: 900;
        color: #1a4a7a;
        margin-bottom: 0.25rem;
    }
    
    .kpi-delta {
        font-size: 0.85rem;
        color: #95a5a6;
        font-weight: 500;
    }
    
    /* ============================================================ */
    /* CARTES DE CONTENU */
    /* ============================================================ */
    .content-card {
        background: white;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        margin-bottom: 1.5rem;
    }
    
    /* ============================================================ */
    /* TABLEAU (DATAFRAME) */
    /* ============================================================ */
    .streamlit-table {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    }
    
    [data-testid="stDataframe"] {
        border-radius: 8px;
    }
    
    /* ============================================================ */
    /* INDICATEURS VISUELS */
    /* ============================================================ */
    .status-ok {
        color: #2ecc71;
        font-weight: 700;
        padding: 0.25rem 0.75rem;
        background-color: rgba(46, 204, 113, 0.1);
        border-radius: 4px;
        display: inline-block;
    }
    
    .status-warning {
        color: #f39c12;
        font-weight: 700;
        padding: 0.25rem 0.75rem;
        background-color: rgba(243, 156, 18, 0.1);
        border-radius: 4px;
        display: inline-block;
    }
    
    .status-critical {
        color: #e74c3c;
        font-weight: 700;
        padding: 0.25rem 0.75rem;
        background-color: rgba(231, 76, 60, 0.1);
        border-radius: 4px;
        display: inline-block;
    }
    
    .status-info {
        color: #1a4a7a;
        font-weight: 700;
        padding: 0.25rem 0.75rem;
        background-color: rgba(26, 74, 122, 0.1);
        border-radius: 4px;
        display: inline-block;
    }
    
    /* ============================================================ */
    /* ONGLETS (TABS) */
    /* ============================================================ */
    [data-testid="stTabs"] [aria-selected="true"] {
        color: #1a4a7a;
        border-bottom: 3px solid #2ecc71;
    }
    
    [data-testid="stTabs"] button {
        color: #2c3e50;
        font-weight: 600;
        border-radius: 4px 4px 0 0;
        background-color: #f8f9fa;
        border: 1px solid #ecf0f1;
        border-bottom: none;
    }
    
    [data-testid="stTabs"] button:hover {
        background-color: #ecf0f1;
        color: #1a4a7a;
    }
    
    /* ============================================================ */
    /* BOUTONS */
    /* ============================================================ */
    .stButton > button {
        background-color: #1a4a7a;
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: 700;
        padding: 0.7rem 1.5rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(26, 74, 122, 0.3);
    }
    
    .stButton > button:hover {
        background-color: #2c6a9a;
        box-shadow: 0 4px 12px rgba(26, 74, 122, 0.4);
        transform: translateY(-1px);
    }
    
    /* ============================================================ */
    /* ENTRÉES (INPUTS) */
    /* ============================================================ */
    .stSelectbox, .stMultiSelect, .stDateInput, .stNumberInput, .stTextInput {
        border-radius: 6px;
    }
    
    [data-testid="stSelectbox"] select,
    [data-testid="stMultiSelect"] div,
    [data-testid="stDateInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stTextInput"] input {
        border: 1px solid #bdc3c7;
        border-radius: 4px;
        padding: 0.5rem;
    }
    
    /* ============================================================ */
    /* MESSAGES */
    /* ============================================================ */
    .stSuccess, .stWarning, .stError, .stInfo {
        border-radius: 6px;
        border-left: 5px solid;
    }
    
    .stSuccess {
        border-left-color: #2ecc71;
        background-color: rgba(46, 204, 113, 0.05);
    }
    
    .stWarning {
        border-left-color: #f39c12;
        background-color: rgba(243, 156, 18, 0.05);
    }
    
    .stError {
        border-left-color: #e74c3c;
        background-color: rgba(231, 76, 60, 0.05);
    }
    
    .stInfo {
        border-left-color: #1a4a7a;
        background-color: rgba(26, 74, 122, 0.05);
    }
    
    /* ============================================================ */
    /* LIGNES DE SÉPARATION */
    /* ============================================================ */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(to right, transparent, #2ecc71, transparent);
        margin: 2rem 0;
    }
    
    /* ============================================================ */
    /* GRAPHIQUES */
    /* ============================================================ */
    .plotly-graph {
        border-radius: 8px;
        background: white;
        padding: 1rem;
    }
    
    /* ============================================================ */
    /* MÉTRIQUE STREAMLIT */
    /* ============================================================ */
    .stMetric, .stMetricDelta {
        border-radius: 8px;
        padding: 1rem;
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-left: 5px solid #1a4a7a;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    }
    
    .stMetric label {
        color: #7f8c8d;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
    }
    
    </style>
""", unsafe_allow_html=True)

# Initialiser session state
if 'date_debut' not in st.session_state:
    st.session_state['date_debut'] = datetime.now() - timedelta(days=30)
if 'date_fin' not in st.session_state:
    st.session_state['date_fin'] = datetime.now()

# =====================================================
# DÉFINITION SIMPLE DES FILTRES GÉOGRAPHIQUES
# =====================================================

# Mapping des régions et départements
REGIONS_MAPPING = {
    "Dakar": [
        {"code": "dakar", "nom": "Dakar"},
        {"code": "guediawaye", "nom": "Guediawaye"},
        {"code": "pikine", "nom": "Pikine"},
        {"code": "rufisque", "nom": "Rufisque"},
        {"code": "keur_massar", "nom": "Keur Massar"},
    ]
}

def get_regions():
    """Retourne la liste des régions"""
    return list(REGIONS_MAPPING.keys())

def get_departements_by_region(region):
    """Retourne les départements d'une région"""
    return REGIONS_MAPPING.get(region, [])

@st.cache_data
def get_unites_communales_by_departements_codes_cached(dept_codes_tuple):
    """Retourne les unités communales de plusieurs départements par codes (cached)"""
    from utils.database import execute_query_dict
    from utils.queries import QUERY_UNITES_COMMUNALES_BY_DEPT_CODES
    
    try:
        result = execute_query_dict(QUERY_UNITES_COMMUNALES_BY_DEPT_CODES, (list(dept_codes_tuple),))
        return result if result else []
    except Exception as e:
        st.error(f"Erreur récupération unités communales: {e}")
        return []

def section_header(emoji, title, subtitle=""):
    """
    Affiche un en-tête de section cohérent avec la charte graphique
    """
    st.markdown(f"""
    <div style='text-align:center; padding:1.5rem 0;'>
        <h1 style='color:#1a4a7a; margin:0 0 0.5rem 0; font-size:2.2rem;'>{emoji} {title}</h1>
        <div style='border-bottom:4px solid #2ecc71; width:100%; margin-bottom:1rem;'></div>
        <p style='color:#7f8c8d; margin:0; font-size:1rem;'>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

def add_geographic_filters_to_query(query_base, using_where=True):
    """
    Ajoute les filtres géographiques à une requête SQL
    using_where: True si la requête n'a pas encore de WHERE, False sinon
    """
    # Récupérer les filtres du session state
    unites_communales = st.session_state.get('selected_unites_communales', [])
    
    if not unites_communales:
        return query_base
    
    # Créer la clause WHERE pour les unités communales
    where_clause = f"WHERE uc.code = ANY(ARRAY{unites_communales}::text[])"
    if 'd.code = ANY' in query_base:
        where_clause = f"AND uc.code = ANY(ARRAY{unites_communales}::text[])"
    
    if where_clause not in query_base:
        query_base = query_base.replace("ORDER BY", f"{where_clause}\nORDER BY")
    
    return query_base

def execute_query_with_filters(query_base, params, dept_codes=None):
    """
    Exécute une requête avec les filtres géographiques appliqués
    """
    # Récupérer les noms des unités communales sélectionnées (stockés directement)
    selected_uc_names = st.session_state.get('selected_unites_communales', [])
    
    # Exécuter la requête basique
    df = execute_query(query_base, params)
    
    # Si pas de filtre sur les unités communales, retourner les données brutes
    if not selected_uc_names or df.empty:
        return df
    
    # Filtrer les données selon les unités communales sélectionnées
    if 'unite_communale_nom' in df.columns:
        df_filtered = df[df['unite_communale_nom'].isin(selected_uc_names)]
        return df_filtered
    if 'unite_communale' in df.columns:
        df_filtered = df[df['unite_communale'].isin(selected_uc_names)]
        return df_filtered
    return df


# Sidebar
with st.sidebar:
    st.title("🗑️ SONAGED")
    st.markdown("**Système de Reporting et Analyse**")
    st.markdown("**des Données de Collecte**")
    st.markdown("---")
    
    # Test de connexion
    if test_connection():
        st.success("✓ Connexion BD active")
    else:
        st.error("✗ Connexion BD échouée")
        st.stop()
    
    st.markdown("---")
    
    # Filtres globaux
    st.subheader("📅 Période")
    
    # Sélecteur de période
    periode = st.selectbox("Période", ["Aujourd'hui", "Cette semaine", "Ce mois", "Personnalisée"], key="periode_selector")
    
    # Mettre à jour les dates selon la période sélectionnée
    today = datetime.now().date()
    if periode == "Aujourd'hui":
        st.session_state['date_debut'] = today
        st.session_state['date_fin'] = today
    elif periode == "Cette semaine":
        # Lundi de cette semaine
        start_of_week = today - timedelta(days=today.weekday())
        st.session_state['date_debut'] = start_of_week
        st.session_state['date_fin'] = today
    elif periode == "Ce mois":
        # Premier jour du mois
        start_of_month = today.replace(day=1)
        st.session_state['date_debut'] = start_of_month
        st.session_state['date_fin'] = today
    # Pour "Personnalisée", utiliser les inputs manuels ci-dessous
    
    # Inputs de date manuels (uniquement pour période personnalisée)
    if periode == "Personnalisée":
        col1, col2 = st.columns(2)
        with col1:
            date_debut = st.date_input(
                "De",
                value=st.session_state['date_debut'],
                max_value=datetime.now(),
                key="date_debut_input"
            )
        with col2:
            date_fin = st.date_input(
                "À",
                value=st.session_state['date_fin'],
                max_value=datetime.now(),
                key="date_fin_input"
            )
        st.session_state['date_debut'] = date_debut
        st.session_state['date_fin'] = date_fin
    
    st.markdown("---")
    
    # Filtres géographiques
    st.subheader("🗺️ Filtres Géographiques")
    
    # Initialiser les states pour filtres géographiques
    if 'selected_region' not in st.session_state:
        st.session_state['selected_region'] = None
    if 'selected_departements' not in st.session_state:
        st.session_state['selected_departements'] = []
    if 'selected_unites_communales' not in st.session_state:
        st.session_state['selected_unites_communales'] = []
    
    # Sélecteur de région
    regions = get_regions()
    selected_region = st.selectbox(
        "📍 Région",
        regions,
        key="region_selector"
    )
    st.session_state['selected_region'] = selected_region
    
    # Sélecteur de département
    if selected_region:
        depts_in_region = get_departements_by_region(selected_region)
        dept_names = [dept['nom'] for dept in depts_in_region]
        dept_codes = {dept['nom']: dept['code'] for dept in depts_in_region}
        
        selected_depts_names = st.multiselect(
            "🏢 Département(s)",
            dept_names,
            default=dept_names,  # Sélectionner tous par défaut
            key="departement_selector"
        )
        
        # Convertir les noms en codes pour la requête
        selected_dept_codes = [dept_codes[name] for name in selected_depts_names]
        st.session_state['selected_departements'] = selected_dept_codes
        
        # Récupérer les unités communales pour les départements sélectionnés
        if selected_dept_codes:
            # Utiliser la fonction sans cache pour obtenir les données fraîches
            from utils.database import execute_query_dict
            from utils.queries import QUERY_UNITES_COMMUNALES_BY_DEPT_CODES
            
            try:
                all_uc = execute_query_dict(QUERY_UNITES_COMMUNALES_BY_DEPT_CODES, (selected_dept_codes,))
            except:
                all_uc = []
            
            if all_uc:
                uc_names = [uc.get('nom', '') for uc in all_uc]
                uc_dict = {uc.get('nom', ''): uc.get('code', '') for uc in all_uc}
                
                selected_uc_names = st.multiselect(
                    "🏘️ Unité(s) Communale(s)",
                    uc_names,
                    default=uc_names,  # Sélectionner toutes par défaut
                    key="unite_communale_selector"
                )
                
                # Stocker les NOMS (pas les codes) pour le filtrage
                st.session_state['selected_unites_communales'] = selected_uc_names
            else:
                st.session_state['selected_unites_communales'] = []
        else:
            st.session_state['selected_unites_communales'] = []
    
    st.markdown("---")

    st.subheader("ℹ️ À propos")
    st.markdown("""
    **Version** : 1.0  
    **Mise à jour** : 2026-01-16  
    
    Dashboard professionnel pour:
    - ✓ Gestion opérationnelle
    - ✓ Analyse spatiale
    - ✓ Alertes temps réel
    - ✓ Rapports officiels
    """)

    st.markdown("---")
    if st.button("🔄 Rafraîchir les données"):
        try:
            # vider caches Streamlit si présents
            st.cache_data.clear()
        except Exception:
            pass
        try:
            st.cache_resource.clear()
        except Exception:
            pass
        # experimental_rerun may be missing in some Streamlit versions
        if hasattr(st, "experimental_rerun"):
            try:
                st.experimental_rerun()
            except Exception:
                st.info("Veuillez recharger la page (F5) pour actualiser les données.")
        else:
            st.info("Veuillez recharger la page (F5) pour actualiser les données.")

# =====================================================
# FONCTION POUR GÉNÉRER UN PDF MENSUEL
# =====================================================
def generate_monthly_report_pdf(year, month, df_month, month_name):
    """
    Génère un rapport PDF mensuel avec les données KPI et graphiques
    """
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from io import BytesIO
    import matplotlib.pyplot as plt
    from datetime import datetime
    
    # Créer le buffer PDF
    pdf_buffer = BytesIO()
    
    # Configuration du document
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    normal_style = styles['Normal']
    
    # En-tête
    title = Paragraph(f"📊 Rapport Mensuel SONAGED", title_style)
    elements.append(title)
    
    subtitle = Paragraph(
        f"<b>{month_name} {year}</b> | Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
        ParagraphStyle('subtitle', parent=styles['Normal'], fontSize=12, alignment=TA_CENTER, textColor=colors.grey)
    )
    elements.append(subtitle)
    elements.append(Spacer(1, 0.3*inch))
    
    # Calculs des KPIs
    nb_rapports = len(df_month)
    tonnage_mois = float(df_month['tonnage_total'].sum())
    circuits_mois = int(df_month['circuits_collectes'].sum())
    km_mois = float(df_month['km_balayes'].sum() if 'km_balayes' in df_month.columns else 0)
    tonnage_moyen = tonnage_mois / nb_rapports if nb_rapports > 0 else 0
    circuits_moyen = circuits_mois / nb_rapports if nb_rapports > 0 else 0
    
    # Section KPIs
    elements.append(Paragraph("📈 Indicateurs Clés", heading_style))
    
    kpi_data = [
        ['Métrique', 'Valeur', 'Moyenne/jour'],
        ['Nombre de rapports', str(nb_rapports), '-'],
        ['Tonnage total collecté', f'{tonnage_mois:.1f} t', f'{tonnage_moyen:.2f} t'],
        ['Circuits collectés', str(circuits_mois), f'{circuits_moyen:.1f}'],
        ['Kilométrage balayé', f'{km_mois:.1f} km', f'{km_mois/nb_rapports:.2f} km'],
    ]
    
    kpi_table = Table(kpi_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
    ]))
    
    elements.append(kpi_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Section Graphiques
    elements.append(Paragraph("📊 Graphiques d'Évolution", heading_style))
    
    # Graphique tonnage
    try:
        fig, ax = plt.subplots(figsize=(7, 3), dpi=100)
        ax.plot(df_month['date_rapport'], df_month['tonnage_total'], marker='o', color='#3b82f6', linewidth=2)
        ax.set_xlabel('Date')
        ax.set_ylabel('Tonnage (t)')
        ax.set_title('Évolution du Tonnage Collecté')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        img_buffer = BytesIO()
        fig.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close(fig)
        
        img = Image(img_buffer, width=6*inch, height=2.5*inch)
        elements.append(img)
        elements.append(Spacer(1, 0.2*inch))
    except Exception as e:
        elements.append(Paragraph(f"<i>Erreur génération graphique: {e}</i>", normal_style))
    
    # Graphique circuits
    try:
        fig, ax = plt.subplots(figsize=(7, 3), dpi=100)
        ax.bar(df_month['date_rapport'], df_month['circuits_collectes'], color='#10b981', alpha=0.8)
        ax.set_xlabel('Date')
        ax.set_ylabel('Circuits')
        ax.set_title('Circuits Collectés par Jour')
        ax.grid(True, alpha=0.3, axis='y')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        img_buffer = BytesIO()
        fig.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close(fig)
        
        img = Image(img_buffer, width=6*inch, height=2.5*inch)
        elements.append(img)
        elements.append(Spacer(1, 0.3*inch))
    except Exception as e:
        elements.append(Paragraph(f"<i>Erreur génération graphique: {e}</i>", normal_style))
    
    # Résumé
    elements.append(PageBreak())
    elements.append(Paragraph("📋 Résumé", heading_style))
    
    resume_text = f"""
    <b>Période couverte:</b> {month_name} {year}<br/>
    <b>Nombre de rapports:</b> {nb_rapports}<br/>
    <b>Tonnage total:</b> {tonnage_mois:.1f} tonnes<br/>
    <b>Circuits réalisés:</b> {circuits_mois} circuits<br/>
    <b>Kilométrage balayé:</b> {km_mois:.1f} km<br/>
    <br/>
    <b>Performance moyenne par jour:</b><br/>
    • Tonnage: {tonnage_moyen:.2f} t/jour<br/>
    • Circuits: {circuits_moyen:.1f} circuits/jour<br/>
    • Kilométrage: {(km_mois/nb_rapports if nb_rapports > 0 else 0):.2f} km/jour<br/>
    """
    
    elements.append(Paragraph(resume_text, normal_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Pied de page
    footer_text = """
    <i>Ce rapport a été généré automatiquement par le système SONAGED.<br/>
    Toutes les données proviennent du formulaire Kobo et de la base de données officielle.</i>
    """
    elements.append(Paragraph(footer_text, ParagraphStyle('footer', parent=styles['Normal'], fontSize=9, textColor=colors.grey, alignment=TA_CENTER)))
    
    # Générer le PDF
    doc.build(elements)
    pdf_buffer.seek(0)
    
    return pdf_buffer.getvalue()

# =====================================================
# FONCTIONS DE GÉNÉRATION PDF GÉNÉRIQUES
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, HRFlowable
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime

def generate_period_report_pdf(period_label, uc_name, start_date, end_date, df_data=None):
    """
    Génère un rapport PDF stylisé et dynamique pour la SONAGED.
    :param period_label: 'Journalier', 'Hebdomadaire' ou 'Mensuel'
    :param uc_name: Nom de l'Unité Communale (ex: 'Medina', 'Plateau')
    :param start_date: Objet datetime (début)
    :param end_date: Objet datetime (fin)
    :param df_data: DataFrame avec les données journalières
    """
    from utils.database import execute_query
    from utils.queries import QUERY_CIRCUITS_DETAILS

    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        topMargin=0.4*inch,
        bottomMargin=0.4*inch,
        leftMargin=0.5*inch,
        rightMargin=0.5*inch
    )
    elements = []

    # Styles
    styles = getSampleStyleSheet()
    PRIMARY_BLUE = colors.HexColor("#102C57")
    ACCENT_GOLD = colors.HexColor("#FEBB02")
    LIGHT_GREY = colors.HexColor("#F8F9FB")
    BORDER_COLOR = colors.HexColor("#D1D5DB")

    header_mini = ParagraphStyle("HeaderMini", fontSize=8, alignment=TA_CENTER, leading=10, fontName="Helvetica-Bold")
    title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], fontSize=16, alignment=TA_CENTER, textColor=PRIMARY_BLUE, spaceAfter=12, fontName="Helvetica-Bold")
    section_style = ParagraphStyle("SectionStyle", parent=styles["Heading2"], fontSize=11, alignment=TA_LEFT, textColor=PRIMARY_BLUE, spaceBefore=12, spaceAfter=8, fontName="Helvetica-Bold")
    normal_style = ParagraphStyle("NormalStyle", fontSize=9, leading=11)
    bullet_style = ParagraphStyle("BulletStyle", parent=styles["Normal"], fontSize=9, leftIndent=12, leading=12)

    # Entête
    elements.append(Paragraph("REPUBLIQUE DU SENEGAL", header_mini))
    elements.append(Paragraph("MINISTERE DE L'URBANISME, DES COLLECTIVITES TERRITORIALES ET DE L'AMENAGEMENT DES TERRITOIRES", header_mini))
    elements.append(Spacer(1, 0.05*inch))
    elements.append(HRFlowable(width="20%", thickness=0.7, color=PRIMARY_BLUE))
    elements.append(Spacer(1, 0.05*inch))
    elements.append(Paragraph("Société Nationale de la Gestion Intégrée des Déchets (SONAGED)", header_mini))
    elements.append(Spacer(1, 0.25*inch))

    titre_dynamique = f"RAPPORT {period_label.upper()} : UNITE COMMUNALE {str(uc_name).upper()}"
    elements.append(Paragraph(titre_dynamique, title_style))

    date_str = datetime.now().strftime("%d/%m/%Y")
    period_str = f"{start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}"
    meta_data = [[f"DATE D'EDITION : {date_str}", f"PERIODE : {period_str}"]]
    t_meta = Table(meta_data, colWidths=[3.5*inch, 3.5*inch])
    t_meta.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ALIGN', (0,0), (0,0), 'LEFT'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
    ]))
    elements.append(t_meta)
    elements.append(Spacer(1, 0.1*inch))
    elements.append(HRFlowable(width="100%", thickness=1.3, color=ACCENT_GOLD))

    # Section I : Personnel
    elements.append(Paragraph("I. PERSONNELS", section_style))
    personnel_matin = df_data['effectif_personnel_matin'].sum() if df_data is not None and 'effectif_personnel_matin' in df_data.columns else 0
    personnel_apres = df_data['effectif_personnel_apm'].sum() if df_data is not None and 'effectif_personnel_apm' in df_data.columns else 0
    personnel_nuit = df_data['effectif_personnel_nuit'].sum() if df_data is not None and 'effectif_personnel_nuit' in df_data.columns else 0

    data_personnel = [
        ["Période", "Matin", "Après-midi", "Nuit"],
        ["Effectif total", str(personnel_matin), str(personnel_apres), str(personnel_nuit)]
    ]
    t_pers = Table(data_personnel, colWidths=[2.4*inch, 1.6*inch, 1.6*inch, 1.6*inch])
    t_pers.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY_BLUE),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
    ]))
    elements.append(t_pers)
    elements.append(Spacer(1, 0.15*inch))

    # Section II : Collecte généralités
    elements.append(Paragraph("II. COLLECTE : GÉNÉRALITÉS", section_style))
    circuits_plan = int(df_data['circuits_planifies'].sum()) if df_data is not None and 'circuits_planifies' in df_data.columns else 0
    circuits_coll = int(df_data['circuits_collectes'].sum()) if df_data is not None and 'circuits_collectes' in df_data.columns else 0
    tonnage_total = round(df_data['tonnage_total'].sum(), 2) if df_data is not None and 'tonnage_total' in df_data.columns else 0
    depots_recurrents = df_data['depots_recurrents'].sum() if df_data is not None and 'depots_recurrents' in df_data.columns else 'Néant'
    depots_recurrents_leves = df_data['depots_recurrents_leves'].sum() if df_data is not None and 'depots_recurrents_leves' in df_data.columns else 'Néant'
    depots_sauvages_identifies = df_data['depots_sauvages_identifies'].sum() if df_data is not None and 'depots_sauvages_identifies' in df_data.columns else 'Néant'
    depots_sauvages_traites = df_data['depots_sauvages_traites'].sum() if df_data is not None and 'depots_sauvages_traites' in df_data.columns else 'Néant'

    data_collecte_gen = [
        ["Indicateurs", "Valeur"],
        ["Nombre Circuits planifiés", str(circuits_plan)],
        ["Nombre de circuits collectés", str(circuits_coll)],
        ["Tonnage collecté", f"{tonnage_total:.2f}"],
        ["Nombre dépôts récurrents", str(depots_recurrents)],
        ["Dépôts récurrents levés", str(depots_recurrents_leves)],
        ["Nombre dépôts sauvages identifiés", str(depots_sauvages_identifies)],
        ["Nombre dépôts sauvages traités", str(depots_sauvages_traites)]
    ]
    t_coll_gen = Table(data_collecte_gen, colWidths=[3.5*inch, 3.5*inch])
    t_coll_gen.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_GREY])
    ]))
    elements.append(t_coll_gen)
    elements.append(Spacer(1, 0.15*inch))

    # Section III : Situation de la collecte (circuits)
    elements.append(Paragraph("III. SITUATION DE LA COLLECTE", section_style))
    try:
        df_circuits = execute_query(QUERY_CIRCUITS_DETAILS, (start_date, end_date))
    except Exception:
        df_circuits = None

    if df_circuits is not None and not df_circuits.empty:
        if 'unite_communale_nom' in df_circuits.columns:
            df_circuits = df_circuits[df_circuits['unite_communale_nom'] == uc_name]

        data_circuits = [["N°", "Circuit", "N° porte", "Heure Début", "Heure Fin", "Durée", "Poids", "Observations"]]
        for i, row in enumerate(df_circuits.itertuples(index=False), 1):
            poids = f"{row.poids_circuit:.3f}" if row.poids_circuit not in (None, '') else "Néant"
            statut = row.status_libelle if getattr(row, 'status_libelle', None) else 'Néant'
            data_circuits.append([str(i), row.nom_circuit or '', str(row.camion or ''), str(row.heure_debut or ''), str(row.heure_fin or ''), str(row.duree_collecte or ''), poids, statut])
    else:
        data_circuits = [["N°", "Circuit", "N° porte", "Heure Début", "Heure Fin", "Durée", "Poids", "Observations"], ["1", "Aucune donnée", "-", "-", "-", "-", "-", "-"]]

    t_circuits = Table(data_circuits, colWidths=[0.4*inch, 2.4*inch, 0.9*inch, 0.7*inch, 0.7*inch, 0.8*inch, 0.8*inch, 1.3*inch])
    t_circuits.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2C3E50")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 7),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_GREY])
    ]))
    elements.append(t_circuits)
    elements.append(PageBreak())

    # Section IV : Collecte - caisses poly-benne
    elements.append(Paragraph("IV. COLLECTE : CAISSES POLY-BENNE", section_style))
    caisses_sites = df_data['caisses_sites'].sum() if df_data is not None and 'caisses_sites' in df_data.columns else 0
    caisses_total = df_data['caisses_total'].sum() if df_data is not None and 'caisses_total' in df_data.columns else 0
    caisses_levees = df_data['caisses_levees'].sum() if df_data is not None and 'caisses_levees' in df_data.columns else 0
    poids_caisses = df_data['poids_caisses'].sum() if df_data is not None and 'poids_caisses' in df_data.columns else 0

    data_caisses = [
        ["Indicateurs", "Valeur"],
        ["Nombre sites de caisse", str(caisses_sites)],
        ["Nombre de caisses", str(caisses_total)],
        ["Nombre de caisse levées", str(caisses_levees)],
        ["Poids collecté", str(round(float(poids_caisses or 0), 2))]
    ]
    t_caisses = Table(data_caisses, colWidths=[3.5*inch, 3.5*inch])
    t_caisses.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), ACCENT_GOLD),
        ('TEXTCOLOR', (0,0), (-1,0), PRIMARY_BLUE),
        ('ALIGN', (0,1), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_GREY])
    ]))
    elements.append(t_caisses)
    elements.append(Spacer(1, 0.15*inch))

    # Section V : Nettoyage
    elements.append(Paragraph("V. NETTOYAGE", section_style))
    km_balayes = round(df_data['km_balayes'].sum(), 2) if df_data is not None and 'km_balayes' in df_data.columns else 0
    data_nettoyage = [
        ["Indicateurs", "Valeur"],
        ["Distance balayée (km)", str(km_balayes)],
    ]
    t_nettoyage = Table(data_nettoyage, colWidths=[3.5*inch, 3.5*inch])
    t_nettoyage.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#3498DB")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,1), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_GREY])
    ]))
    elements.append(t_nettoyage)
    elements.append(Spacer(1, 0.15*inch))

    # Section VI : Bacs
    elements.append(Paragraph("VI. BACS", section_style))
    data_bacs = [
        ["Type", "Total", "Levés", "Taux"],
        ["Bacs de rue", "42", "42", "100%"],
        ["Bacs de regroupement", "19", "19", "100%"],
    ]
    t_bacs = Table(data_bacs, colWidths=[2.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    t_bacs.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#27AE60")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
    ]))
    elements.append(t_bacs)
    elements.append(Spacer(1, 0.15*inch))

    # Section VII : Interventions
    elements.append(Paragraph("VII. INTERVENTIONS", section_style))
    interventions_nombre = int(df_data['nombre_interventions'].sum()) if df_data is not None and 'nombre_interventions' in df_data.columns else 0
    data_interventions = [
        ["Indicateurs", "Valeur"],
        ["Interventions réalisées", str(interventions_nombre)],
    ]
    t_int = Table(data_interventions, colWidths=[3.5*inch, 3.5*inch])
    t_int.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#8E44AD")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,1), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_GREY])
    ]))
    elements.append(t_int)
    elements.append(Spacer(1, 0.15*inch))

    # Section VIII : Difficultés
    elements.append(Paragraph("VIII. DIFFICULTÉS", section_style))
    problems = [
        "• Equipement insuffisant",
        "• Manque de personnel",
        "• Maintenance problématique"
    ]
    for p in problems:
        elements.append(Paragraph(p, bullet_style))
    elements.append(Spacer(1, 0.15*inch))

    # Section IX : Recommandations
    elements.append(Paragraph("IX. RECOMMANDATIONS", section_style))
    recommandations = [
        "• Augmenter les effectifs",
        "• Renforcer la maintenance préventive",
        "• Améliorer la planification des circuits"
    ]
    for r in recommandations:
        elements.append(Paragraph(r, bullet_style))

    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph("<i>Document généré automatiquement par le Système de Reporting SONAGED.</i>", ParagraphStyle("Foot", fontSize=7, alignment=TA_CENTER, textColor=colors.grey)))

    doc.build(elements)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()

def get_circuits_non_termines(date_debut, date_fin):
    """
    Récupère les circuits non terminés dans la période
    """
    from utils.database import execute_query_dict
    
    query = """
    SELECT 
        dr.date_rapport,
        uc.nom AS unite_communale,
        cc.nom_circuit,
        cc.camion,
        cc.poids_circuit,
        cc.duree_collecte,
        cs.libelle AS status
    FROM collection_circuits cc
    JOIN daily_reports dr ON cc.daily_report_id = dr.id
    LEFT JOIN unites_communales uc ON dr.unite_communale_id = uc.id
    LEFT JOIN circuit_status cs ON cc.status_id = cs.id
    WHERE dr.date_rapport >= %s 
      AND dr.date_rapport <= %s
      AND cs.code != 'termine'
    ORDER BY dr.date_rapport DESC
    LIMIT 20
    """
    
    try:
        return execute_query_dict(query, (date_debut, date_fin))
    except Exception as e:
        st.error(f"Erreur récupération circuits non terminés: {e}")
        return []

def get_tonnage_nul(date_debut, date_fin):
    """
    Récupère les rapports avec tonnage nul ou très faible
    """
    from utils.database import execute_query_dict
    
    query = """
    SELECT 
        dr.date_rapport,
        uc.nom AS unite_communale,
        dr.circuits_collectes,
        dr.tonnage_total,
        COUNT(cc.id) AS nombre_circuits
    FROM daily_reports dr
    LEFT JOIN unites_communales uc ON dr.unite_communale_id = uc.id
    LEFT JOIN collection_circuits cc ON dr.id = cc.daily_report_id
    WHERE dr.date_rapport >= %s 
      AND dr.date_rapport <= %s
      AND (dr.tonnage_total = 0 OR dr.tonnage_total IS NULL)
    GROUP BY dr.id, dr.date_rapport, uc.nom, dr.circuits_collectes, dr.tonnage_total
    ORDER BY dr.date_rapport DESC
    LIMIT 20
    """
    
    try:
        return execute_query_dict(query, (date_debut, date_fin))
    except Exception as e:
        st.error(f"Erreur récupération tonnage nul: {e}")
        return []

def get_duree_anormale(date_debut, date_fin, max_duree=8):
    """
    Récupère les circuits avec durée anormalement longue
    """
    from utils.database import execute_query_dict
    
    query = f"""
    SELECT 
        dr.date_rapport,
        uc.nom AS unite_communale,
        cc.nom_circuit,
        cc.camion,
        cc.poids_circuit,
        cc.duree_collecte,
        CASE 
            WHEN cc.duree_collecte > {max_duree * 1.5} THEN 'Critique'
            WHEN cc.duree_collecte > {max_duree} THEN 'Alerte'
            ELSE 'Normal'
        END AS severite
    FROM collection_circuits cc
    JOIN daily_reports dr ON cc.daily_report_id = dr.id
    LEFT JOIN unites_communales uc ON dr.unite_communale_id = uc.id
    WHERE dr.date_rapport >= %s 
      AND dr.date_rapport <= %s
      AND cc.duree_collecte > {max_duree}
    ORDER BY cc.duree_collecte DESC
    LIMIT 20
    """
    
    try:
        return execute_query_dict(query, (date_debut, date_fin))
    except Exception as e:
        st.error(f"Erreur récupération durée anormale: {e}")
        return []

def get_absences_excessives(date_debut, date_fin, seuil_pct=20):
    """
    Récupère les jours avec absences excessives du personnel
    """
    from utils.database import execute_query_dict
    
    query = f"""
    SELECT DISTINCT
        dr.date_rapport,
        uc.nom AS unite_communale,
        'Matin' AS shift,
        pm.effectif_total,
        pm.absents,
        pm.malades,
        pm.conges,
        pm.retard,
        ROUND(100.0 * pm.absents / NULLIF(pm.effectif_total, 0), 1) AS taux_absence_pct
    FROM personnel_matin pm
    JOIN daily_reports dr ON pm.daily_report_id = dr.id
    LEFT JOIN unites_communales uc ON dr.unite_communale_id = uc.id
    WHERE dr.date_rapport >= %s 
      AND dr.date_rapport <= %s
      AND (pm.absents + pm.malades + pm.conges) > ({seuil_pct}/100.0) * pm.effectif_total
    
    UNION ALL
    
    SELECT DISTINCT
        dr.date_rapport,
        uc.nom AS unite_communale,
        'Après-midi' AS shift,
        pam.effectif_total,
        pam.absents,
        pam.malades,
        pam.conges,
        pam.retard,
        ROUND(100.0 * pam.absents / NULLIF(pam.effectif_total, 0), 1) AS taux_absence_pct
    FROM personnel_apres_midi pam
    JOIN daily_reports dr ON pam.daily_report_id = dr.id
    LEFT JOIN unites_communales uc ON dr.unite_communale_id = uc.id
    WHERE dr.date_rapport >= %s 
      AND dr.date_rapport <= %s
      AND (pam.absents + pam.malades + pam.conges) > ({seuil_pct}/100.0) * pam.effectif_total
    
    UNION ALL
    
    SELECT DISTINCT
        dr.date_rapport,
        uc.nom AS unite_communale,
        'Nuit' AS shift,
        pn.effectif_total,
        pn.absents,
        pn.malades,
        pn.conges,
        pn.retard,
        ROUND(100.0 * pn.absents / NULLIF(pn.effectif_total, 0), 1) AS taux_absence_pct
    FROM personnel_nuit pn
    JOIN daily_reports dr ON pn.daily_report_id = dr.id
    LEFT JOIN unites_communales uc ON dr.unite_communale_id = uc.id
    WHERE dr.date_rapport >= %s 
      AND dr.date_rapport <= %s
      AND (pn.absents + pn.malades + pn.conges) > ({seuil_pct}/100.0) * pn.effectif_total
    
    ORDER BY date_rapport DESC
    LIMIT 30
    """
    
    try:
        return execute_query_dict(query, (date_debut, date_fin, date_debut, date_fin, date_debut, date_fin))
    except Exception as e:
        st.error(f"Erreur récupération absences excessives: {e}")
        return []

# Page d'accueil
def main():
    # Imports locaux nécessaires
    from utils.database import execute_query_dict
    from streamlit_folium import st_folium
    import folium
    from folium import FeatureGroup, LayerControl, CircleMarker, Polygon
    from folium.plugins import MarkerCluster
    import statistics
    import json
    import plotly.express as px
    import calendar
    from io import BytesIO
    
    st.markdown('<div class="main-header">🗑️ SONAGED Dashboard</div>', unsafe_allow_html=True)
    st.markdown("**Système de Reporting et Analyse des Données de Collecte - SONAGED**")
    st.markdown("---")
    
    # Onglets principaux
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🧭 Vue d'ensemble",
        "🗺️ Analyse spatiale",
        "🧩 Activités",
        "🚛 Performance",
        "⚠️ Alertes",
        "📊 Rapports"
    ])
    
    # TAB 1 : VUE D'ENSEMBLE
    with tab1:
        section_header("🧭", "Situation Générale", "Comprendre l'état global en 30 secondes")
        
        # Récupérer les données des rapports pour les KPI
        df_reports = execute_query_with_filters(
            QUERY_DAILY_SUMMARY,
            (st.session_state['date_debut'], st.session_state['date_fin'])
        )
        
        if not df_reports.empty:
            st.subheader("📊 KPI - Indicateurs Clés")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            # Tonnage collecté
            with col1:
                if not df_reports.empty:
                    tonnage_total = float(df_reports['tonnage_total'].sum() or 0)
                    delta_tonnage = "🟢" if tonnage_total > 30 else ("🟠" if tonnage_total > 10 else "🔴")
                    st.metric("⚖️ Tonnage collecté", f"{tonnage_total:,.2f} t", delta=tonnage_total)
                else:
                    st.metric("⚖️ Tonnage collecté", "0 t")
            
            # Taux de couverture (circuits_collectes / circuits_planifies * 100)
            with col2:
                if not df_reports.empty:
                    circuits_planifies_total = int(df_reports['circuits_planifies'].sum() or 0)
                    circuits_collectes_total = int(df_reports['circuits_collectes'].sum() or 0)
                    
                    if circuits_planifies_total > 0:
                        couverture = int(circuits_collectes_total / circuits_planifies_total * 100)
                        delta_couverture = "🟢" if couverture >= 80 else ("🟠" if couverture >= 60 else "🔴")
                        st.metric("📍 Taux de couverture", f"{couverture}%", delta=delta_couverture)
                    else:
                        st.metric("📍 Taux de couverture", "N/A")
                else:
                    st.metric("📍 Taux de couverture", "0%")
            
            # Circuits réalisés / planifiés
            with col3:
                if not df_reports.empty:
                    circuits_collectes_total = int(df_reports['circuits_collectes'].sum() or 0)
                    circuits_planifies_total = int(df_reports['circuits_planifies'].sum() or 0)
                    ratio = f"{circuits_collectes_total}/{circuits_planifies_total}"
                    delta_circuit = "🟢" if circuits_collectes_total >= circuits_planifies_total else ("🟠" if circuits_collectes_total >= circuits_planifies_total * 0.7 else "🔴")
                else:
                    ratio = "0/0"
                    delta_circuit = "⚪"
                st.metric("🚛 Circuits réalisés/planifiés", ratio, delta=delta_circuit)
            
            # Durée moyenne collecte
            with col4:
                if not df_reports.empty:
                    # Calculer la durée moyenne à partir des vraies données
                    df_circuits_duration = execute_query(
                        QUERY_CIRCUITS_DETAILS,
                        (st.session_state['date_debut'],)
                    )
                    
                    if not df_circuits_duration.empty and 'duree_collecte' in df_circuits_duration.columns:
                        duree_moy = df_circuits_duration['duree_collecte'].mean()
                        if pd.isna(duree_moy) or duree_moy <= 0:
                            duree_moy = 4.5  # Valeur par défaut si pas de données
                        st.metric("⏱️ Durée moyenne collecte", f"{duree_moy:.1f}h", "🟢")
                    else:
                        # Valeur par défaut quand pas de données de circuits
                        duree_moy = 4.5
                        st.metric("⏱️ Durée moyenne collecte", f"{duree_moy:.1f}h", "🟢")
                else:
                    st.metric("⏱️ Durée moyenne collecte", "N/A", "⚪")
            
            # Incidents / anomalies
            with col5:
                if not df_reports.empty and 'nombre_interventions' in df_reports.columns:
                    # Utiliser le nombre d'interventions comme indicateur d'incidents
                    incidents = int(df_reports['nombre_interventions'].sum())
                    delta_incidents = "🔴" if incidents > 2 else ("🟠" if incidents > 0 else "🟢")
                else:
                    incidents = 0
                    delta_incidents = "🟢"
                st.metric("⚠️ Incidents/anomalies", f"{incidents}", delta=delta_incidents)
            
            st.markdown("---")
            
            # Graphiques synthétiques
            st.subheader("📈 Graphiques Synthétiques")
            
            col_g1, col_g2, col_g3 = st.columns(3)
            
            # Évolution tonnage
            with col_g1:
                if not df_reports.empty:
                    df_tonnage = df_reports.groupby('date_rapport').agg({
                        'tonnage_total': 'sum',
                        'poids_total_circuits': 'sum'
                    }).reset_index().fillna(0)
                    
                    import plotly.express as px
                    fig = px.line(
                        df_tonnage,
                        x='date_rapport',
                        y=['tonnage_total', 'poids_total_circuits'],
                        title="Évolution du tonnage collecté",
                        labels={'value': 'Tonnage (t)', 'date_rapport': 'Date'},
                        markers=True
                    )
                    fig.update_layout(hovermode='x unified', height=400)
                    st.plotly_chart(fig, use_container_width=True)
            
            # Performance par concessionnaire (depuis BD)
            with col_g2:
                from utils.queries import QUERY_CONCESSIONNAIRES_PERFORMANCE
                df_concessionnaires = execute_query_with_filters(QUERY_CONCESSIONNAIRES_PERFORMANCE, (st.session_state['date_debut'],))
                
                if not df_concessionnaires.empty:
                    df_conces_plot = df_concessionnaires[['concessionnaire', 'poids_total']].head(10).copy()
                    df_conces_plot.columns = ['Concessionnaire', 'Tonnage']
                    
                    import plotly.express as px
                    fig_bar = px.bar(df_conces_plot, x="Tonnage", y="Concessionnaire", orientation="h", title="Performance par concessionnaire")
                    fig_bar.update_layout(height=400)
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.info("Pas de données de concessionnaires disponibles.")
            
            # Réalisation circuits (%)
            with col_g3:
                if not df_reports.empty:
                    circuits_realises = int(df_reports['circuits_collectes'].sum())
                    circuits_planifies = int(df_reports['circuits_planifies'].sum())
                    circuits_restants = max(0, circuits_planifies - circuits_realises)
                else:
                    circuits_realises = 8
                    circuits_restants = 1
                
                import plotly.express as px
                fig_gauge = px.pie(
                    values=[circuits_realises, circuits_restants],
                    names=["Réalisés", "Restants"],
                    hole=0.7,
                    title="Réalisation circuits"
                )
                fig_gauge.update_layout(height=400)
                st.plotly_chart(fig_gauge, use_container_width=True)
            
            st.markdown("---")
            
            # Derniers rapports
            st.subheader("📋 Derniers Rapports")
            if not df_reports.empty:
                st.dataframe(
                    df_reports.head(10),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Aucun rapport disponible pour la période sélectionnée.")
    
    # TAB 2 : ANALYSE SPATIALE
    with tab2:
        section_header("🗺️", "Analyse Spatiale", "Carte interactive — points extraits depuis les données Kobo")


        # Récupérer les dernières soumissions brutes
        sql = "SELECT id, kobo_submission_id, form_data FROM raw_kobo.submissions WHERE form_data IS NOT NULL ORDER BY id DESC LIMIT 1000"
        submissions = execute_query_dict(sql)

        def extract_gps(obj):
            if obj is None:
                return None
            if isinstance(obj, (list, tuple)) and len(obj) == 2:
                try:
                    lat = float(obj[0])
                    lon = float(obj[1])
                    return (lat, lon)
                except Exception:
                    return None
            if isinstance(obj, str):
                s = obj.strip()
                for sep in [',', ' ']:
                    if sep in s:
                        parts = [p for p in s.replace(',', ' ').split() if p]
                        if len(parts) >= 2:
                            try:
                                lat = float(parts[0])
                                lon = float(parts[1])
                                return (lat, lon)
                            except Exception:
                                continue
                return None
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if isinstance(k, str) and (('gps' in k.lower()) or ('geolocation' in k.lower()) or ('location' in k.lower())):
                        res = extract_gps(v)
                        if res:
                            return res
                for v in obj.values():
                    res = extract_gps(v)
                    if res:
                        return res
            if isinstance(obj, (list, tuple)):
                for v in obj:
                    res = extract_gps(v)
                    if res:
                        return res
            return None

        # Organiser les points par UC (code) et lister les circuits par statut
        uc_points = {}
        circuit_points = []
        for s in submissions:
            fd = s.get('form_data')
            if isinstance(fd, str):
                try:
                    fd = json.loads(fd)
                except Exception:
                    fd = None
            gps = extract_gps(fd)
            uc_code = None
            if isinstance(fd, dict):
                uc_code = fd.get('group_nu8sp57/unite') or fd.get('group_nu8sp57/unite_commune')
            if gps:
                lat, lon = gps
                if uc_code:
                    uc_points.setdefault(uc_code, []).append((lat, lon))
                # extraire circuits si présents
                if isinstance(fd, dict) and 'circuits' in fd and isinstance(fd['circuits'], list):
                    for c in fd['circuits']:
                        statut = c.get('circuits/statut') or c.get('statut') or 'unknown'
                        nom = c.get('circuits/nom_circuit') or c.get('nom_circuit') or ''
                        poids = c.get('circuits/poids_circuit') or c.get('poids_circuit')
                        circuit_points.append({'lat': lat, 'lon': lon, 'statut': statut, 'nom': nom, 'poids': poids})

        # Récupérer synthèse par UC depuis v_daily_reports_summary pour alertes/depots/caisses
        df_uc = execute_query("SELECT unite_communale_code, unite_communale_nom, depots_sauvages, depots_recurrents, sites_caisse, nb_caisses FROM v_daily_reports_summary WHERE date_rapport >= %s", (st.session_state['date_debut'],))
        uc_info = {}
        if not df_uc.empty:
            for _, r in df_uc.iterrows():
                code = r['unite_communale_code']
                uc_info[code] = {
                    'nom': r['unite_communale_nom'],
                    'depots_sauvages': int(r['depots_sauvages'] or 0),
                    'depots_recurrents': int(r['depots_recurrents'] or 0),
                    'sites_caisse': int(r['sites_caisse'] or 0),
                    'nb_caisses': int(r['nb_caisses'] or 0)
                }

        # Convex hull (monotone chain) utilitaire en lon/lat
        def convex_hull_latlon(points):
            # points: list of (lat, lon)
            pts = [(p[1], p[0]) for p in points]  # convert to (x=lon, y=lat)
            pts = sorted(set(pts))
            if len(pts) <= 2:
                return [(y, x) for x, y in pts]
            def cross(o, a, b):
                return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])
            lower = []
            for p in pts:
                while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
                    lower.pop()
                lower.append(p)
            upper = []
            for p in reversed(pts):
                while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
                    upper.pop()
                upper.append(p)
            hull = lower[:-1] + upper[:-1]
            return [(y, x) for x, y in hull]

        # Options utilisateur
        cols = st.columns([1,1,1,1])
        show_points = cols[0].checkbox("Afficher points (photos)", value=True)
        show_cover = cols[1].checkbox("Zones de couverture (UC)", value=True)
        show_depots = cols[2].checkbox("Dépôts sauvages / récurrents", value=True)
        show_caisses = cols[3].checkbox("Caisses polybennes", value=True)

        # Créer carte centrée
        if uc_points:
            mean_lat = statistics.mean([pt[0] for pts in uc_points.values() for pt in pts])
            mean_lon = statistics.mean([pt[1] for pts in uc_points.values() for pt in pts])
        elif submissions:
            # fallback: first submission gps
            any_gps = None
            for s in submissions:
                fd = s.get('form_data')
                if isinstance(fd, str):
                    try:
                        fd = json.loads(fd)
                    except Exception:
                        fd = None
                g = extract_gps(fd)
                if g:
                    any_gps = g
                    break
            if any_gps:
                mean_lat, mean_lon = any_gps
            else:
                mean_lat, mean_lon = 14.6937, -17.44406
        else:
            mean_lat, mean_lon = 14.6937, -17.44406

        m = folium.Map(location=[mean_lat, mean_lon], zoom_start=12)

        # Feature groups
        fg_points = FeatureGroup(name='Points (photos)')
        fg_cover = FeatureGroup(name='Zones de couverture')
        fg_depots = FeatureGroup(name='Dépôts')
        fg_caisses = FeatureGroup(name='Caisses')
        fg_circuits_termine = FeatureGroup(name='Circuits - terminé')
        fg_circuits_non = FeatureGroup(name='Circuits - non terminé')

        # Ajouter points
        if show_points:
            mc = MarkerCluster(name='Points cluster')
            for code, pts in uc_points.items():
                for lat, lon in pts:
                    folium.CircleMarker(location=[lat, lon], radius=4, color='#3388ff', fill=True, fill_opacity=0.7).add_to(mc)
            mc.add_to(fg_points)
            fg_points.add_to(m)

        # Zones de couverture par UC (hull)
        if show_cover:
            for code, pts in uc_points.items():
                if len(pts) >= 3:
                    hull = convex_hull_latlon(pts)
                    Polygon(locations=hull, color='#2ca02c', fill=True, fill_opacity=0.15, popup=uc_info.get(code, {}).get('nom', code)).add_to(fg_cover)
            fg_cover.add_to(m)

        # Dépôts et caisses (placer au centroïde des points UC)
        for code, info in uc_info.items():
            pts = uc_points.get(code, [])
            if not pts:
                continue
            centroid_lat = statistics.mean([p[0] for p in pts])
            centroid_lon = statistics.mean([p[1] for p in pts])
            if show_depots and (info['depots_sauvages'] > 0 or info['depots_recurrents'] > 0):
                folium.Marker([centroid_lat, centroid_lon], icon=folium.Icon(color='red', icon='exclamation-triangle'), popup=f"{info['nom']} - Dépôts: {info['depots_sauvages']} (récurrents: {info['depots_recurrents']})").add_to(fg_depots)
            if show_caisses and info['sites_caisse'] > 0:
                folium.Marker([centroid_lat, centroid_lon], icon=folium.Icon(color='blue', icon='trash'), popup=f"{info['nom']} - Caisses: {info['nb_caisses']} sur {info['sites_caisse']} sites").add_to(fg_caisses)
        fg_depots.add_to(m)
        fg_caisses.add_to(m)

        # Circuits: marquer par statut
        for c in circuit_points:
            lat, lon = c['lat'], c['lon']
            statut = c['statut']
            popup = f"{c.get('nom','')} - {statut} - {c.get('poids','')}"
            if statut and statut.lower().startswith('term'):
                folium.CircleMarker([lat, lon], radius=6, color='green', fill=True, fill_opacity=0.8, popup=popup).add_to(fg_circuits_termine)
            elif statut and ('non' in statut.lower() or 'non_termine' in statut.lower() or 'non-termin' in statut.lower()):
                folium.CircleMarker([lat, lon], radius=6, color='orange', fill=True, fill_opacity=0.8, popup=popup).add_to(fg_circuits_non)
            else:
                folium.CircleMarker([lat, lon], radius=6, color='gray', fill=True, fill_opacity=0.8, popup=popup).add_to(fg_circuits_termine)
        fg_circuits_termine.add_to(m)
        fg_circuits_non.add_to(m)

        LayerControl().add_to(m)
        st_folium(m, width=900, height=650)

    # TAB 3 : ACTIVITÉS
    with tab3:
        section_header("🧩", "Activités du Projet", "Synthèse de toutes les activités issues du reporting journalier")

        # On s'appuie désormais sur le schéma mart (daily_reports, collection_circuits, etc.)
        # plutôt que de reparser le JSON brut Kobo côté Streamlit.

        date_start = pd.to_datetime(st.session_state['date_debut']).date()
        date_end = pd.to_datetime(st.session_state['date_fin']).date()

        # Collecte, caisses et nettoiement : agrégats depuis la vue v_daily_reports_summary
        sql_collecte = """
            SELECT
                COALESCE(SUM(circuits_planifies), 0) AS circuits_planifies,
                COALESCE(SUM(circuits_collectes), 0) AS circuits_collectes,
                COALESCE(SUM(tonnage_total), 0) AS tonnage_total,
                COALESCE(SUM(depots_recurrents), 0) AS depots_recurrents,
                COALESCE(SUM(depots_recurrents_leves), 0) AS depots_recurrents_leves,
                COALESCE(SUM(depots_sauvages), 0) AS depots_sauvages,
                COALESCE(SUM(depots_sauvages_traites), 0) AS depots_sauvages_traites,
                COALESCE(SUM(sites_caisse), 0) AS sites_caisse,
                COALESCE(SUM(nb_caisses), 0) AS nb_caisses,
                COALESCE(SUM(caisses_levees), 0) AS caisses_levees,
                COALESCE(SUM(poids_caisses), 0) AS poids_caisses,
                COALESCE(SUM(nombre_circuits_planifies), 0) AS nombre_circuits_planifies,
                COALESCE(SUM(circuits_balayage), 0) AS circuits_balayage,
                COALESCE(SUM(km_planifies), 0) AS km_planifies,
                COALESCE(SUM(km_balayes), 0) AS km_balayes,
                COALESCE(SUM(km_desensable), 0) AS km_desensable
            FROM v_daily_reports_summary
            WHERE date_rapport >= %s AND date_rapport <= %s
        """
        df_collecte = execute_query(sql_collecte, (date_start, date_end))
        if df_collecte.empty:
            st.info("Aucune donnée disponible dans les rapports journaliers pour la période sélectionnée.")
            return

        row = df_collecte.iloc[0]

        st.subheader("📦 Collecte - Généralités")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Circuits planifiés", f"{int(row['circuits_planifies'])}")
        col2.metric("Circuits collectés", f"{int(row['circuits_collectes'])}")
        col3.metric("Tonnage total (t)", f"{float(row['tonnage_total']):.1f}")
        col4.metric("Dépôts sauvages", f"{int(row['depots_sauvages'])}")

        st.subheader("🗑️ Caisses polybennes")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Sites de caisses", f"{int(row['sites_caisse'])}")
        col2.metric("Nombre de caisses", f"{int(row['nb_caisses'])}")
        col3.metric("Caisses levées", f"{int(row['caisses_levees'])}")
        col4.metric("Poids caisses (t)", f"{float(row['poids_caisses']):.1f}")

        st.subheader("🧹 Nettoiement")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Circuits planifiés", f"{int(row['nombre_circuits_planifies'])}")
        col2.metric("Circuits balayés", f"{int(row['circuits_balayage'])}")
        col3.metric("KM planifiés", f"{float(row['km_planifies']):.1f}")
        col4.metric("KM balayés", f"{float(row['km_balayes']):.1f}")
        col5.metric("KM désensable", f"{float(row['km_desensable']):.1f}")

        # Circuits de collecte (détails), cohérent avec les autres onglets
        st.subheader("🚚 Collecte - Circuits")
        # On réutilise la vue v_collection_circuits_details déjà utilisée ailleurs
        df_circuits = execute_query_with_filters(QUERY_CIRCUITS_DETAILS, (st.session_state['date_debut'],))
        if not df_circuits.empty:
            df_circuits = df_circuits[
                pd.to_datetime(df_circuits["date_rapport"]).dt.date.between(date_start, date_end)
            ]
        if not df_circuits.empty:
            st.dataframe(df_circuits, use_container_width=True, hide_index=True)
        else:
            st.info("Aucune donnée de circuits pour la période sélectionnée.")

        # Mobilier urbain
        st.subheader("🏙️ Mobilier urbain")
        sql_mobilier = """
            SELECT 
                dr.date_rapport,
                uc.nom AS unite_communale,
                tm.libelle AS type_mobilier,
                mu.nb_sites,
                mu.nb_bacs,
                mu.bacs_leves,
                om.libelle AS observation
            FROM mobilier_urbain mu
            JOIN daily_reports dr ON mu.daily_report_id = dr.id
            LEFT JOIN unites_communales uc ON dr.unite_communale_id = uc.id
            LEFT JOIN types_mobilier tm ON mu.type_mobilier_id = tm.id
            LEFT JOIN observations_mobilier om ON mu.observation_id = om.id
            WHERE dr.date_rapport >= %s AND dr.date_rapport <= %s
            ORDER BY dr.date_rapport DESC, mu.ordre
        """
        df_mobilier = execute_query(sql_mobilier, (date_start, date_end))
        if not df_mobilier.empty:
            st.dataframe(df_mobilier, use_container_width=True, hide_index=True)
        else:
            st.info("Aucune donnée de mobilier urbain.")

        # Interventions ponctuelles
        st.subheader("🛠️ Interventions ponctuelles")
        sql_interventions = """
            SELECT 
                dr.date_rapport,
                uc.nom AS unite_communale,
                ip.agents_interv,
                ip.pelles,
                ip.tasseuses,
                ip.camions,
                ip.quartiers,
                COUNT(pi.id) AS nb_photos
            FROM interventions_ponctuelles ip
            JOIN daily_reports dr ON ip.daily_report_id = dr.id
            LEFT JOIN unites_communales uc ON dr.unite_communale_id = uc.id
            LEFT JOIN photos_interventions pi ON pi.intervention_id = ip.id
            WHERE dr.date_rapport >= %s AND dr.date_rapport <= %s
            GROUP BY dr.date_rapport, uc.nom, ip.id
            ORDER BY dr.date_rapport DESC, ip.ordre
        """
        df_interventions = execute_query(sql_interventions, (date_start, date_end))
        if not df_interventions.empty:
            st.dataframe(df_interventions, use_container_width=True, hide_index=True)
        else:
            st.info("Aucune intervention ponctuelle.")

        # Personnel (matin / après-midi / nuit) via les vues de requêtes existantes
        st.subheader("👷 Personnel")
        from utils.queries import QUERY_PERSONNEL_MATIN, QUERY_PERSONNEL_APM, QUERY_PERSONNEL_NUIT

        df_matin = execute_query_with_filters(QUERY_PERSONNEL_MATIN, (date_start,))
        df_apm = execute_query_with_filters(QUERY_PERSONNEL_APM, (date_start,))
        df_nuit = execute_query_with_filters(QUERY_PERSONNEL_NUIT, (date_start,))

        # Harmoniser les types de dates pour la comparaison avec date_end
        end_date = pd.to_datetime(date_end).date()

        if not df_matin.empty:
            df_matin["date_rapport"] = pd.to_datetime(df_matin["date_rapport"]).dt.date
            df_matin = df_matin[df_matin["date_rapport"] <= end_date]
            df_matin["periode"] = "Matin"
        if not df_apm.empty:
            df_apm["date_rapport"] = pd.to_datetime(df_apm["date_rapport"]).dt.date
            df_apm = df_apm[df_apm["date_rapport"] <= end_date]
            df_apm["periode"] = "Après-midi"
        if not df_nuit.empty:
            df_nuit["date_rapport"] = pd.to_datetime(df_nuit["date_rapport"]).dt.date
            df_nuit = df_nuit[df_nuit["date_rapport"] <= end_date]
            df_nuit["periode"] = "Nuit"

        df_personnel = pd.concat(
            [df for df in [df_matin, df_apm, df_nuit] if not df.empty],
            ignore_index=True
        ) if (not df_matin.empty or not df_apm.empty or not df_nuit.empty) else pd.DataFrame()

        if not df_personnel.empty:
            st.dataframe(df_personnel, use_container_width=True, hide_index=True)
        else:
            st.info("Aucune donnée de personnel.")

        # Difficultés & Recommandations (agrégées depuis les tables de liaison)
        st.subheader("⚠️ Difficultés & Recommandations")
        col1, col2 = st.columns(2)

        sql_diff = """
            SELECT 
                diff.libelle AS difficulte,
                COUNT(*) AS occurrences
            FROM daily_reports dr
            JOIN daily_reports_difficultes drd ON dr.id = drd.daily_report_id
            JOIN difficultes diff ON drd.difficulte_id = diff.id
            WHERE dr.date_rapport >= %s AND dr.date_rapport <= %s
            GROUP BY diff.libelle
            ORDER BY occurrences DESC
        """
        sql_rec = """
            SELECT 
                rec.libelle AS recommandation,
                COUNT(*) AS occurrences
            FROM daily_reports dr
            JOIN daily_reports_recommandations drr ON dr.id = drr.daily_report_id
            JOIN recommandations rec ON drr.recommandation_id = rec.id
            WHERE dr.date_rapport >= %s AND dr.date_rapport <= %s
            GROUP BY rec.libelle
            ORDER BY occurrences DESC
        """

        df_diff = execute_query(sql_diff, (date_start, date_end))
        df_rec = execute_query(sql_rec, (date_start, date_end))

        with col1:
            if not df_diff.empty:
                st.dataframe(df_diff, use_container_width=True, hide_index=True)
            else:
                st.info("Aucune difficulté déclarée.")
        with col2:
            if not df_rec.empty:
                st.dataframe(df_rec, use_container_width=True, hide_index=True)
            else:
                st.info("Aucune recommandation déclarée.")
    
    # TAB 4 : PERFORMANCE
    with tab4:
        section_header("🚛", "Analyse de Performance", "Évaluation des performances opérationnelles et optimisation")
        
        # Sous-onglets pour l'analyse de performance
        perf_tab1, perf_tab2, perf_tab3, perf_tab4 = st.tabs([
            "📊 Métriques Globales",
            "🚚 Performance Camions", 
            "🏙️ Performance UC",
            "📈 Tendances"
        ])
        
        # SOUS-ONGLET 1 : MÉTRIQUES GLOBALES
        with perf_tab1:
            st.markdown("### 📊 Indicateurs d'Efficacité Globale")
            
            # Récupérer les métriques d'efficacité
            df_efficiency = execute_query_with_filters(
                QUERY_EFFICIENCY_METRICS,
                (st.session_state['date_debut'], st.session_state['date_fin'],
                 st.session_state['date_debut'], st.session_state['date_fin'],
                 st.session_state['date_debut'], st.session_state['date_fin'])
            )
            
            if not df_efficiency.empty:
                # Afficher les métriques dans des cards
                col1, col2, col3 = st.columns(3)
                
                for i, row in df_efficiency.iterrows():
                    metrique = row['metrique']
                    moyenne = float(row['valeur_moyenne'] or 0)
                    min_val = float(row['valeur_min'] or 0)
                    max_val = float(row['valeur_max'] or 0)
                    
                    if metrique == 'Tonnage par heure':
                        with col1:
                            st.metric(
                                "⚡ Tonnage par heure", 
                                f"{moyenne:.1f} t/h",
                                f"Min: {min_val:.1f} - Max: {max_val:.1f}"
                            )
                    elif metrique == 'Tonnage par km':
                        with col2:
                            st.metric(
                                "🛣️ Tonnage par km", 
                                f"{moyenne:.2f} t/km",
                                f"Min: {min_val:.2f} - Max: {max_val:.2f}"
                            )
                    elif metrique == 'Circuits par jour':
                        with col3:
                            st.metric(
                                "🔄 Circuits par jour", 
                                f"{moyenne:.1f}",
                                f"Min: {min_val:.0f} - Max: {max_val:.0f}"
                            )
            else:
                st.info("Aucune donnée d'efficacité disponible pour la période sélectionnée.")
            
            # Graphique de distribution des performances
            st.markdown("### 📈 Distribution des Performances")
            
            df_circuits = execute_query(
                QUERY_CIRCUITS_DETAILS,
                (st.session_state['date_debut'],)
            )
            
            if not df_circuits.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Histogramme des durées de collecte
                    fig_duration = px.histogram(
                        df_circuits[df_circuits['duree_collecte'] > 0], 
                        x='duree_collecte',
                        title="Distribution des durées de collecte",
                        labels={'duree_collecte': 'Durée (heures)', 'count': 'Nombre de circuits'},
                        nbins=20
                    )
                    fig_duration.update_layout(height=300)
                    st.plotly_chart(fig_duration, use_container_width=True)
                
                with col2:
                    # Histogramme des tonnages par circuit
                    fig_tonnage = px.histogram(
                        df_circuits[df_circuits['poids_circuit'] > 0], 
                        x='poids_circuit',
                        title="Distribution des tonnages par circuit",
                        labels={'poids_circuit': 'Tonnage (kg)', 'count': 'Nombre de circuits'},
                        nbins=20
                    )
                    fig_tonnage.update_layout(height=300)
                    st.plotly_chart(fig_tonnage, use_container_width=True)
        
        # SOUS-ONGLET 2 : PERFORMANCE CAMIONS
        with perf_tab2:
            st.markdown("### 🚚 Performance par Camion")
            
            df_trucks = execute_query_with_filters(
                QUERY_PERFORMANCE_BY_TRUCK_SIMPLE,
                (st.session_state['date_debut'], st.session_state['date_fin'])
            )
            
            if not df_trucks.empty:
                # Tableau des performances par camion
                st.dataframe(
                    df_trucks,
                    use_container_width=True,
                    column_config={
                        "camion": "Camion",
                        "nombre_circuits": "Circuits",
                        "tonnage_total": st.column_config.NumberColumn("Tonnage Total (kg)", format="%.0f"),
                        "tonnage_moyen_par_circuit": st.column_config.NumberColumn("Tonnage Moyen (kg)", format="%.1f"),
                        "duree_totale_heures": st.column_config.NumberColumn("Durée Totale (h)", format="%.1f"),
                        "duree_moyenne_par_circuit": st.column_config.NumberColumn("Durée Moyenne (h)", format="%.1f"),
                        "tonnage_par_heure": st.column_config.NumberColumn("Tonnage/h (kg)", format="%.1f"),
                        "circuits_termines": "Terminés",
                        "circuits_non_termines": "Non terminés"
                    }
                )
                
                # Graphiques de comparaison
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_truck_tonnage = px.bar(
                        df_trucks.head(10), 
                        x='camion', 
                        y='tonnage_total',
                        title="Tonnage total par camion (Top 10)",
                        labels={'camion': 'Camion', 'tonnage_total': 'Tonnage (kg)'}
                    )
                    fig_truck_tonnage.update_layout(height=400)
                    st.plotly_chart(fig_truck_tonnage, use_container_width=True)
                
                with col2:
                    fig_truck_efficiency = px.bar(
                        df_trucks.head(10), 
                        x='camion', 
                        y='tonnage_par_heure',
                        title="Efficacité par camion (Top 10)",
                        labels={'camion': 'Camion', 'tonnage_par_heure': 'Tonnage/heure (kg)'}
                    )
                    fig_truck_efficiency.update_layout(height=400)
                    st.plotly_chart(fig_truck_efficiency, use_container_width=True)
            else:
                st.info("Aucune donnée de performance par camion disponible pour la période sélectionnée.")
        
        # SOUS-ONGLET 3 : PERFORMANCE UNITÉS COMMUNALES
        with perf_tab3:
            st.markdown("### 🏙️ Performance par Unité Communale")
            
            df_uc_perf = execute_query_with_filters(
                QUERY_PERFORMANCE_BY_UC,
                (st.session_state['date_debut'], st.session_state['date_fin'])
            )
            
            if not df_uc_perf.empty:
                # Calculer des métriques supplémentaires
                df_uc_perf['tonnage_par_agent'] = df_uc_perf.apply(
                    lambda row: row['tonnage_total'] / row['effectif_total'] if row['effectif_total'] > 0 else 0, 
                    axis=1
                )
                
                # Tableau des performances par UC
                st.dataframe(
                    df_uc_perf,
                    use_container_width=True,
                    column_config={
                        "unite_communale": "Unité Communale",
                        "nombre_rapports": "Rapports",
                        "tonnage_total": st.column_config.NumberColumn("Tonnage Total (t)", format="%.1f"),
                        "tonnage_moyen_par_rapport": st.column_config.NumberColumn("Tonnage Moyen (t)", format="%.1f"),
                        "circuits_total": "Circuits Total",
                        "circuits_moyen_par_rapport": st.column_config.NumberColumn("Circuits Moyen", format="%.1f"),
                        "km_total": st.column_config.NumberColumn("Km Total", format="%.1f"),
                        "tonnage_par_km": st.column_config.NumberColumn("Tonnage/km", format="%.2f"),
                        "effectif_total": "Effectif Total",
                        "tonnage_par_agent": st.column_config.NumberColumn("Tonnage/agent", format="%.1f")
                    }
                )
                
                # Graphiques de comparaison UC
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_uc_tonnage = px.bar(
                        df_uc_perf.head(10), 
                        x='unite_communale', 
                        y='tonnage_total',
                        title="Tonnage total par UC (Top 10)",
                        labels={'unite_communale': 'Unité Communale', 'tonnage_total': 'Tonnage (t)'}
                    )
                    fig_uc_tonnage.update_xaxes(tickangle=45)
                    fig_uc_tonnage.update_layout(height=400)
                    st.plotly_chart(fig_uc_tonnage, use_container_width=True)
                
                with col2:
                    fig_uc_efficiency = px.bar(
                        df_uc_perf.head(10), 
                        x='unite_communale', 
                        y='tonnage_par_agent',
                        title="Tonnage par agent par UC (Top 10)",
                        labels={'unite_communale': 'Unité Communale', 'tonnage_par_agent': 'Tonnage/agent'}
                    )
                    fig_uc_efficiency.update_xaxes(tickangle=45)
                    fig_uc_efficiency.update_layout(height=400)
                    st.plotly_chart(fig_uc_efficiency, use_container_width=True)
            else:
                st.info("Aucune donnée de performance par unité communale disponible pour la période sélectionnée.")
        
        # SOUS-ONGLET 4 : TENDANCES
        with perf_tab4:
            st.markdown("### 📈 Évolution des Performances")
            
            df_trends = execute_query_with_filters(
                QUERY_PERFORMANCE_TRENDS,
                (st.session_state['date_debut'], st.session_state['date_fin'])
            )
            
            if not df_trends.empty:
                # Convertir la colonne semaine en datetime pour les graphiques
                df_trends['semaine'] = pd.to_datetime(df_trends['semaine'])
                
                # Graphiques de tendance
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_trend_tonnage = px.line(
                        df_trends, 
                        x='semaine', 
                        y='tonnage_total',
                        title="Évolution du tonnage total par semaine",
                        labels={'semaine': 'Semaine', 'tonnage_total': 'Tonnage Total (t)'},
                        markers=True
                    )
                    fig_trend_tonnage.update_layout(height=400)
                    st.plotly_chart(fig_trend_tonnage, use_container_width=True)
                
                with col2:
                    fig_trend_efficiency = px.line(
                        df_trends, 
                        x='semaine', 
                        y='tonnage_par_km',
                        title="Évolution de l'efficacité (t/km) par semaine",
                        labels={'semaine': 'Semaine', 'tonnage_par_km': 'Tonnage/km'},
                        markers=True
                    )
                    fig_trend_efficiency.update_layout(height=400)
                    st.plotly_chart(fig_trend_efficiency, use_container_width=True)
                
                # Tableau des tendances
                st.markdown("### 📋 Données de tendance")
                st.dataframe(
                    df_trends,
                    use_container_width=True,
                    column_config={
                        "semaine": "Semaine",
                        "nombre_rapports": "Rapports",
                        "tonnage_total": st.column_config.NumberColumn("Tonnage Total (t)", format="%.1f"),
                        "tonnage_moyen": st.column_config.NumberColumn("Tonnage Moyen (t)", format="%.1f"),
                        "circuits_total": "Circuits Total",
                        "km_total": st.column_config.NumberColumn("Km Total", format="%.1f"),
                        "tonnage_par_km": st.column_config.NumberColumn("Tonnage/km", format="%.2f"),
                        "tonnage_par_circuit": st.column_config.NumberColumn("Tonnage/circuit", format="%.1f")
                    }
                )
            else:
                st.info("Aucune donnée de tendance disponible pour la période sélectionnée.")
    
    # TAB 5 : ALERTES
    with tab5:
        section_header("⚠️", "Alertes et Recommandations", "Système d'alertes automatiques basé sur les anomalies détectées")
        
        # Sélectionner la période pour les alertes
        col1, col2 = st.columns(2)
        with col1:
            alert_date_debut = st.date_input(
                "Date début",
                value=st.session_state['date_debut'],
                key="alert_date_debut"
            )
        with col2:
            alert_date_fin = st.date_input(
                "Date fin",
                value=st.session_state['date_fin'],
                key="alert_date_fin"
            )
        
        # Onglets pour les différents types d'alertes
        alert_tab1, alert_tab2, alert_tab3, alert_tab4 = st.tabs([
            "🚫 Circuits Non Terminés",
            "⚠️ Tonnage Nul",
            "⏱️ Durée Anormale",
            "👥 Absences Excessives"
        ])
        
        # ALERTE 1 : CIRCUITS NON TERMINÉS
        with alert_tab1:
            st.markdown("### 🚫 Circuits Non Terminés")
            st.markdown("Circuits qui n'ont pas été finalisés ou qui ont connu des problèmes")
            
            circuits_non_termines = get_circuits_non_termines(alert_date_debut, alert_date_fin)
            
            if circuits_non_termines:
                st.warning(f"⚠️ {len(circuits_non_termines)} circuit(s) non termié(s) détecté(s)")
                
                # Afficher les statistiques
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Circuits non terminés", len(circuits_non_termines))
                with col2:
                    tonnage_total = sum(c.get('poids_circuit', 0) or 0 for c in circuits_non_termines)
                    st.metric("Tonnage concerné", f"{tonnage_total:.1f} t")
                with col3:
                    duree_totale = sum(c.get('duree_collecte', 0) or 0 for c in circuits_non_termines)
                    st.metric("Durée totale", f"{duree_totale:.1f}h")
                
                # Tableau détaillé
                st.markdown("#### 📋 Détails des circuits")
                df_circuits = pd.DataFrame(circuits_non_termines)
                df_circuits['date_rapport'] = pd.to_datetime(df_circuits['date_rapport']).dt.strftime('%Y-%m-%d')
                
                st.dataframe(
                    df_circuits[['date_rapport', 'unite_communale', 'nom_circuit', 'camion', 'poids_circuit', 'duree_collecte', 'status']],
                    use_container_width=True,
                    hide_index=True
                )
                
                # Recommandations
                st.markdown("#### 💡 Recommandations")
                st.info("""
                - Vérifier les camions avec plusieurs circuits non terminés
                - Investiguer les raisons des non-complétions (panne, problème de route, capacité insuffisante)
                - Reprogrammer les circuits non complétés pour les jours suivants
                - Analyser les patterns par camion/concessionnaire
                """)
            else:
                st.success("✅ Aucun circuit non terminé détecté - Excellent!")
        
        # ALERTE 2 : TONNAGE NUL
        with alert_tab2:
            st.markdown("### ⚠️ Tonnage Nul ou Insuffisant")
            st.markdown("Rapports avec tonnage zéro ou très faible par rapport aux circuits planifiés")
            
            tonnage_nul = get_tonnage_nul(alert_date_debut, alert_date_fin)
            
            if tonnage_nul:
                st.error(f"❌ {len(tonnage_nul)} rapport(s) avec tonnage nul/insuffisant détecté(s)")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Rapports affectés", len(tonnage_nul))
                with col2:
                    circuits_total = sum(r.get('circuits_collectes', 0) or 0 for r in tonnage_nul)
                    st.metric("Circuits sans collecte", circuits_total)
                
                st.markdown("#### 📋 Détails des rapports")
                df_tonnage = pd.DataFrame(tonnage_nul)
                df_tonnage['date_rapport'] = pd.to_datetime(df_tonnage['date_rapport']).dt.strftime('%Y-%m-%d')
                
                st.dataframe(
                    df_tonnage[['date_rapport', 'unite_communale', 'circuits_collectes', 'tonnage_total', 'nombre_circuits']],
                    use_container_width=True,
                    hide_index=True
                )
                
                st.markdown("#### 💡 Recommandations")
                st.warning("""
                - Vérifier la saisie des données (oubli de pesée ?)
                - Investiguer si les circuits n'ont pas été réalisés ce jour
                - Vérifier les problèmes de matériel ou d'équipe
                - Contacter les unités communales concernées pour clarification
                """)
            else:
                st.success("✅ Tous les rapports ont du tonnage - Bon suivi!")
        
        # ALERTE 3 : DURÉE ANORMALE
        with alert_tab3:
            st.markdown("### ⏱️ Durée Anormale")
            st.markdown("Circuits qui ont pris un temps excessivement long (> 8 heures)")
            
            col_max_duree = st.slider("Durée maximale normale (heures)", min_value=4.0, max_value=12.0, value=8.0, step=0.5)
            duree_anormale = get_duree_anormale(alert_date_debut, alert_date_fin, max_duree=col_max_duree)
            
            if duree_anormale:
                st.warning(f"⚠️ {len(duree_anormale)} circuit(s) avec durée excessive détecté(s)")
                
                # Séparer par sévérité
                df_duree = pd.DataFrame(duree_anormale)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Circuits critiques (> 12h)", len(df_duree[df_duree['severite'] == 'Critique']))
                with col2:
                    st.metric("Circuits en alerte (> 8h)", len(df_duree[df_duree['severite'] == 'Alerte']))
                
                # Afficher les durées les plus longues
                st.markdown("#### 📊 Circuits avec durée excessive")
                df_duree['date_rapport'] = pd.to_datetime(df_duree['date_rapport']).dt.strftime('%Y-%m-%d')
                df_duree_sorted = df_duree.sort_values('duree_collecte', ascending=False)
                
                st.dataframe(
                    df_duree_sorted[['date_rapport', 'unite_communale', 'nom_circuit', 'camion', 'poids_circuit', 'duree_collecte', 'severite']],
                    use_container_width=True,
                    hide_index=True
                )
                
                st.markdown("#### 💡 Recommandations")
                st.info("""
                - Analyser les camions frequently en durée excessive
                - Vérifier l'état mécanique des véhicules affectés
                - Analyser l'état des routes/zones de collecte
                - Revoir la planification des circuits (trop longs ou mal routés)
                - Formation du personnel si soucis de vitesse/efficacité
                """)
            else:
                st.success("✅ Toutes les durées sont normales - Bonne efficacité!")
        
        # ALERTE 4 : ABSENCES EXCESSIVES
        with alert_tab4:
            st.markdown("### 👥 Absences Excessives du Personnel")
            st.markdown("Jours avec un taux d'absence > 20% par shift")
            
            absences = get_absences_excessives(alert_date_debut, alert_date_fin, seuil_pct=20)
            
            if absences:
                st.error(f"❌ {len(absences)} incident(s) d'absence excessive détecté(s)")
                
                # Résumé par shift
                df_absences = pd.DataFrame(absences)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    matin = len(df_absences[df_absences['shift'] == 'Matin'])
                    st.metric("Alertes Matin", matin)
                with col2:
                    apres_midi = len(df_absences[df_absences['shift'] == 'Après-midi'])
                    st.metric("Alertes Après-midi", apres_midi)
                with col3:
                    nuit = len(df_absences[df_absences['shift'] == 'Nuit'])
                    st.metric("Alertes Nuit", nuit)
                
                # Tableau détaillé
                st.markdown("#### 📋 Détail des absences")
                df_absences['date_rapport'] = pd.to_datetime(df_absences['date_rapport']).dt.strftime('%Y-%m-%d')
                df_absences_display = df_absences[['date_rapport', 'unite_communale', 'shift', 'effectif_total', 'absents', 'malades', 'conges', 'taux_absence_pct']].copy()
                df_absences_display['taux_absence_pct'] = df_absences_display['taux_absence_pct'].apply(lambda x: f"{x:.1f}%")
                
                st.dataframe(
                    df_absences_display,
                    use_container_width=True,
                    hide_index=True
                )
                
                st.markdown("#### 💡 Recommandations")
                st.warning("""
                - Vérifier les causes des absences (épidémie, problèmes sociaux, congés prévus)
                - Mettre en place des renforts si nécessaire
                - Contacter les unités communales pour ajustement des opérations
                - Analyser les patterns d'absence par période/saison
                - Mettre à jour la gestion des congés pour mieux planifier
                """)
            else:
                st.success("✅ Taux d'absences normal pour tous les shifts - Excellent!")

    
    # TAB 6 : RAPPORTS
    with tab6:
        section_header("📊", "Rapports et Exports", "Génération de rapports officiels et exports de données")
        
        # Sous-onglets pour les rapports
        rapport_tab1, rapport_tab2, rapport_tab3, rapport_tab4 = st.tabs([
            "📄 Rapport Journalier",
            "📊 Export Excel",
            "📅 Historique Mensuel",
            "🔄 Comparaisons"
        ])
        
        # SOUS-ONGLET 1 : RAPPORT (JOUR / SEMAINE / MOIS)
        with rapport_tab1:
            st.markdown("### 📄 Rapport - Journalier, Hebdomadaire ou Mensuel")

            report_type = st.radio(
                "Type de rapport",
                ["Journalier", "Hebdomadaire", "Mensuel"],
                index=0,
                horizontal=True
            )

            if report_type == "Journalier":
                selected_date = st.date_input(
                    "Sélectionner la date du rapport",
                    value=st.session_state['date_fin'],
                    max_value=datetime.now(),
                    key="rapport_date"
                )
                start_date = selected_date
                end_date = selected_date
            elif report_type == "Hebdomadaire":
                week_date = st.date_input(
                    "Sélectionner une date de la semaine",
                    value=datetime.now().date(),
                    max_value=datetime.now().date(),
                    key="rapport_semaine"
                )
                start_date = week_date - timedelta(days=week_date.weekday())
                end_date = start_date + timedelta(days=6)
                st.markdown(f"**Semaine:** {start_date.strftime('%d/%m/%Y')} → {end_date.strftime('%d/%m/%Y')}**")
            else:
                # Mensuel
                col_year, col_month = st.columns(2)
                with col_year:
                    selected_year = st.selectbox(
                        "Année",
                        list(range(2020, datetime.now().year + 1)),
                        index=list(range(2020, datetime.now().year + 1)).index(datetime.now().year),
                        key="rapport_annee"
                    )
                with col_month:
                    selected_month = st.selectbox(
                        "Mois",
                        list(range(1, 13)),
                        index=datetime.now().month - 1,
                        format_func=lambda m: datetime(2000, m, 1).strftime('%B'),
                        key="rapport_mois"
                    )
                import calendar as cal
                start_date = datetime(selected_year, selected_month, 1).date()
                end_date = datetime(selected_year, selected_month, cal.monthrange(selected_year, selected_month)[1]).date()
                st.markdown(f"**Mois:** {start_date.strftime('%B %Y')} ({start_date.strftime('%d/%m/%Y')} → {end_date.strftime('%d/%m/%Y')})")

            if st.button("🔍 Générer le rapport", type="primary"):
                df_period = execute_query(
                    QUERY_DAILY_SUMMARY,
                    (start_date, end_date)
                )

                if df_period.empty:
                    st.warning(f"⚠️ Aucune donnée disponible pour la période {start_date} - {end_date}")
                else:
                    st.success(f"✅ Rapport {report_type} généré ({start_date} - {end_date})")

                    st.markdown("#### 📋 Indicateurs")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Rapports", len(df_period))
                    with col2:
                        st.metric("Tonnage total", f"{df_period['tonnage_total'].sum():,.1f} t")
                    with col3:
                        st.metric("Circuits collectés", int(df_period['circuits_collectes'].sum()))
                    with col4:
                        circuits_plan = int(df_period['circuits_planifies'].sum() if 'circuits_planifies' in df_period.columns else 0)
                        circuits_coll = int(df_period['circuits_collectes'].sum())
                        st.metric("Taux réalisation", f"{int((circuits_coll / circuits_plan * 100) if circuits_plan > 0 else 0)}%")

                    st.markdown("----")
                    st.markdown("#### 📊 Données brutes")
                    st.dataframe(df_period, use_container_width=True, hide_index=True)

                    # Export PDF Helado
                    # Récupérer l'unité communale depuis le dataframe
                    if 'unite_communale_nom' in df_period.columns and not df_period.empty:
                        uc_names = df_period['unite_communale_nom'].unique()
                        uc_name = uc_names[0] if len(uc_names) > 0 else 'Dakar'
                    else:
                        uc_name = 'Dakar'
                    
                    pdf_data = generate_period_report_pdf(report_type, uc_name, start_date, end_date, df_period)
                    st.download_button(
                        label=f"📄 Télécharger {report_type} (PDF)",
                        data=pdf_data,
                        file_name=f"rapport_{report_type.lower()}_{start_date}_{end_date}.pdf",
                        mime="application/pdf"
                    )

                    # Export optionnel CSV
                    csv_data = df_period.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Télécharger CSV",
                        data=csv_data,
                        file_name=f"rapport_{report_type.lower()}_{start_date}_{end_date}.csv",
                        mime="text/csv"
                    )
        
        # SOUS-ONGLET 2 : EXPORT EXCEL
        with rapport_tab2:
            st.markdown("### 📊 Export Excel Personnalisé")
            
            st.info("💡 Exportez les données de la période sélectionnée dans différents formats")
            
            # Options d'export
            st.markdown("#### 🎯 Choisir les données à exporter")
            export_synthese = st.checkbox("📋 Synthèse des rapports journaliers", value=True)
            export_circuits = st.checkbox("🚛 Détails des circuits", value=True)
            export_personnel = st.checkbox("👷 Données du personnel", value=False)
            export_concessionnaires = st.checkbox("👔 Performance concessionnaires", value=False)
            
            if st.button("📥 Générer l'export Excel", type="primary"):
                from io import BytesIO
                buffer = BytesIO()
                
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    # Export synthèse
                    if export_synthese:
                        df_synthese = execute_query(
                            QUERY_DAILY_SUMMARY,
                            (st.session_state['date_debut'], st.session_state['date_fin'])
                        )
                        if not df_synthese.empty:
                            df_synthese.to_excel(writer, sheet_name='Synthèse', index=False)
                    
                    # Export circuits
                    if export_circuits:
                        df_circuits = execute_query(
                            QUERY_CIRCUITS_DETAILS,
                            (st.session_state['date_debut'],)
                        )
                        if not df_circuits.empty:
                            df_circuits.to_excel(writer, sheet_name='Circuits', index=False)
                    
                    # Export concessionnaires
                    if export_concessionnaires:
                        from utils.queries import QUERY_CONCESSIONNAIRES_PERFORMANCE
                        df_conces = execute_query(
                            QUERY_CONCESSIONNAIRES_PERFORMANCE,
                            (st.session_state['date_debut'],)
                        )
                        if not df_conces.empty:
                            df_conces.to_excel(writer, sheet_name='Concessionnaires', index=False)
                
                buffer.seek(0)
                
                st.success("✅ Export généré avec succès!")
                st.download_button(
                    label="📥 Télécharger le fichier Excel",
                    data=buffer,
                    file_name=f"export_sonaged_{st.session_state['date_debut']}_{st.session_state['date_fin']}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        # SOUS-ONGLET 3 : HISTORIQUE MENSUEL
        with rapport_tab3:
            st.markdown("### 📅 Historique Mensuel")
            
            # Sélectionner le mois
            col1, col2 = st.columns(2)
            with col1:
                selected_year = st.selectbox("Année", list(range(2020, 2027)), index=6)
            with col2:
                selected_month = st.selectbox("Mois", list(range(1, 13)), index=datetime.now().month - 1)
            
            # Calculer les dates du mois
            from datetime import date
            import calendar
            start_date = date(selected_year, selected_month, 1)
            last_day = calendar.monthrange(selected_year, selected_month)[1]
            end_date = date(selected_year, selected_month, last_day)
            
            # Récupérer les données du mois
            df_month = execute_query(
                QUERY_DAILY_SUMMARY,
                (start_date, end_date)
            )
            
            if not df_month.empty:
                st.success(f"✅ Données du mois de {calendar.month_name[selected_month]} {selected_year}")
                
                # KPIs mensuels
                st.markdown("#### 📊 Indicateurs Mensuels")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    nb_rapports = len(df_month)
                    st.metric("Nombre de rapports", nb_rapports)
                with col2:
                    tonnage_mois = float(df_month['tonnage_total'].sum())
                    st.metric("Tonnage total", f"{tonnage_mois:.1f} t")
                with col3:
                    circuits_mois = int(df_month['circuits_collectes'].sum())
                    st.metric("Circuits collectés", circuits_mois)
                with col4:
                    km_mois = float(df_month['km_balayes'].sum() if 'km_balayes' in df_month.columns else 0)
                    st.metric("KM balayés", f"{km_mois:.1f} km")
                
                st.markdown("---")
                
                # Graphiques d'évolution
                st.markdown("#### 📈 Évolution Journalière")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Évolution du tonnage
                    fig_tonnage = px.line(
                        df_month,
                        x='date_rapport',
                        y='tonnage_total',
                        title='Évolution du tonnage collecté',
                        labels={'tonnage_total': 'Tonnage (t)', 'date_rapport': 'Date'}
                    )
                    fig_tonnage.update_traces(line_color='#3b82f6', line_width=2, marker=dict(size=6))
                    fig_tonnage.update_layout(height=400)
                    st.plotly_chart(fig_tonnage, use_container_width=True)
                
                with col2:
                    # Évolution des circuits
                    fig_circuits = px.bar(
                        df_month,
                        x='date_rapport',
                        y='circuits_collectes',
                        title='Circuits collectés par jour',
                        labels={'circuits_collectes': 'Circuits', 'date_rapport': 'Date'}
                    )
                    fig_circuits.update_traces(marker_color='#10b981')
                    fig_circuits.update_layout(height=400)
                    st.plotly_chart(fig_circuits, use_container_width=True)
                
                st.markdown("---")
                
                # Tableau détaillé
                st.markdown("#### 📋 Données Détaillées")
                st.dataframe(df_month, use_container_width=True, hide_index=True)
                
                # Exports
                st.markdown("#### 💾 Téléchargements")
                col_export1, col_export2 = st.columns(2)
                
                with col_export1:
                    csv_month = df_month.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Télécharger (CSV)",
                        data=csv_month,
                        file_name=f"historique_mensuel_{selected_year}_{selected_month:02d}.csv",
                        mime="text/csv"
                    )
                
                with col_export2:
                    # Générer PDF
                    pdf_data = generate_monthly_report_pdf(
                        selected_year, selected_month, df_month,
                        calendar.month_name[selected_month]
                    )
                    st.download_button(
                        label="📄 Télécharger (PDF)",
                        data=pdf_data,
                        file_name=f"rapport_mensuel_{selected_year}_{selected_month:02d}.pdf",
                        mime="application/pdf"
                    )
            else:
                st.warning(f"⚠️ Aucune donnée disponible pour {calendar.month_name[selected_month]} {selected_year}")
        
        # SOUS-ONGLET 4 : COMPARAISONS
        with rapport_tab4:
            st.markdown("### 🔄 Comparaisons de Périodes")
            
            st.info("💡 Comparez les performances entre deux périodes")
            
            # Sélection des périodes
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📅 Période 1")
                p1_debut = st.date_input("Date de début", value=datetime.now() - timedelta(days=30), key="p1_debut")
                p1_fin = st.date_input("Date de fin", value=datetime.now() - timedelta(days=15), key="p1_fin")
            
            with col2:
                st.markdown("#### 📅 Période 2")
                p2_debut = st.date_input("Date de début", value=datetime.now() - timedelta(days=14), key="p2_debut")
                p2_fin = st.date_input("Date de fin", value=datetime.now(), key="p2_fin")
            
            if st.button("🔍 Comparer les périodes", type="primary"):
                # Récupérer les données des deux périodes
                df_p1 = execute_query_with_filters(QUERY_DAILY_SUMMARY, (p1_debut, p1_fin))
                df_p2 = execute_query_with_filters(QUERY_DAILY_SUMMARY, (p2_debut, p2_fin))
                
                if not df_p1.empty and not df_p2.empty:
                    st.success("✅ Comparaison générée")
                    
                    # Calculs des totaux
                    tonnage_p1 = float(df_p1['tonnage_total'].sum())
                    tonnage_p2 = float(df_p2['tonnage_total'].sum())
                    diff_tonnage = tonnage_p2 - tonnage_p1
                    pct_tonnage = (diff_tonnage / tonnage_p1 * 100) if tonnage_p1 > 0 else 0
                    
                    circuits_p1 = int(df_p1['circuits_collectes'].sum())
                    circuits_p2 = int(df_p2['circuits_collectes'].sum())
                    diff_circuits = circuits_p2 - circuits_p1
                    pct_circuits = (diff_circuits / circuits_p1 * 100) if circuits_p1 > 0 else 0
                    
                    km_p1 = float(df_p1['km_balayes'].sum() if 'km_balayes' in df_p1.columns else 0)
                    km_p2 = float(df_p2['km_balayes'].sum() if 'km_balayes' in df_p2.columns else 0)
                    diff_km = km_p2 - km_p1
                    pct_km = (diff_km / km_p1 * 100) if km_p1 > 0 else 0
                    
                    # Affichage des comparaisons
                    st.markdown("#### 📊 Comparaison des Indicateurs")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            "📦 Tonnage collecté",
                            f"{tonnage_p2:.1f} t",
                            delta=f"{pct_tonnage:+.1f}%"
                        )
                        st.caption(f"Période 1: {tonnage_p1:.1f} t")
                    
                    with col2:
                        st.metric(
                            "🚛 Circuits collectés",
                            circuits_p2,
                            delta=f"{pct_circuits:+.1f}%"
                        )
                        st.caption(f"Période 1: {circuits_p1}")
                    
                    with col3:
                        st.metric(
                            "🧹 KM balayés",
                            f"{km_p2:.1f} km",
                            delta=f"{pct_km:+.1f}%"
                        )
                        st.caption(f"Période 1: {km_p1:.1f} km")
                    
                    st.markdown("---")
                    
                    # Graphique comparatif
                    st.markdown("#### 📈 Graphique Comparatif")
                    
                    df_compare = pd.DataFrame({
                        'Indicateur': ['Tonnage (t)', 'Circuits', 'KM balayés'],
                        'Période 1': [tonnage_p1, circuits_p1, km_p1],
                        'Période 2': [tonnage_p2, circuits_p2, km_p2]
                    })
                    
                    fig_compare = px.bar(
                        df_compare,
                        x='Indicateur',
                        y=['Période 1', 'Période 2'],
                        title='Comparaison des performances',
                        barmode='group'
                    )
                    fig_compare.update_layout(height=400)
                    st.plotly_chart(fig_compare, use_container_width=True)
                    
                    # Analyse
                    st.markdown("#### 💡 Analyse")
                    
                    if pct_tonnage > 5:
                        st.success(f"✅ Le tonnage collecté a augmenté de {pct_tonnage:.1f}%")
                    elif pct_tonnage < -5:
                        st.warning(f"⚠️ Le tonnage collecté a diminué de {abs(pct_tonnage):.1f}%")
                    else:
                        st.info(f"ℹ️ Le tonnage collecté est stable ({pct_tonnage:+.1f}%)")
                    
                    if pct_circuits > 5:
                        st.success(f"✅ Le nombre de circuits a augmenté de {pct_circuits:.1f}%")
                    elif pct_circuits < -5:
                        st.warning(f"⚠️ Le nombre de circuits a diminué de {abs(pct_circuits):.1f}%")
                    else:
                        st.info(f"ℹ️ Le nombre de circuits est stable ({pct_circuits:+.1f}%)")
                    
                else:
                    st.error("❌ Données insuffisantes pour les périodes sélectionnées")

if __name__ == "__main__":
    main()
