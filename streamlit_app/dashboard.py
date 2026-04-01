"""
Application principale Streamlit - Dashboard SONAGED
Dashboard professionnel pour la gestion des déchets municipaux
Version: 2.0 - Nouveau design
"""

import streamlit as st
from datetime import datetime, timedelta
import sys
import os
import pandas as pd

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

# ─────────────────────────────────────────────
# CONFIG PAGE
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="SONAGED Dashboard",
    page_icon="🗑️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CSS GLOBAL — CHARTE GRAPHIQUE SONAGED v2
# ─────────────────────────────────────────────
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">

<style>
/* ── VARIABLES ── */
:root {
  --navy:      #0f2235;
  --navy-mid:  #162d44;
  --green:     #22c55e;
  --blue:      #3b82f6;
  --amber:     #f59e0b;
  --teal:      #14b8a6;
  --red:       #ef4444;
  --surface:   #ffffff;
  --bg:        #f0f4f8;
  --border:    rgba(0,0,0,0.07);
  --text:      #0f172a;
  --text-2:    #64748b;
  --text-3:    #94a3b8;
  --mono:      'DM Mono', monospace;
  --sans:      'DM Sans', sans-serif;
  --radius:    10px;
  --radius-lg: 14px;
}

/* ── BASE ── */
html, body, [class*="css"] {
  font-family: 'DM Sans', sans-serif !important;
  -webkit-font-smoothing: antialiased;
}

.stApp { background: var(--bg) !important; }

/* ── MASQUER ÉLÉMENTS STREAMLIT PAR DÉFAUT ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
  padding: 1.5rem 2rem 2rem !important;
  max-width: 100% !important;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
  background: var(--navy) !important;
}
[data-testid="stSidebar"] > div:first-child {
  padding-top: 0 !important;
}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stDateInput label {
  color: rgba(255,255,255,0.55) !important;
  font-size: 11px !important;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  font-weight: 500;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
  color: var(--green) !important;
  font-size: 11px !important;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  font-weight: 500;
  border: none !important;
  margin-top: 1.2rem !important;
  margin-bottom: 0.2rem !important;
}
[data-testid="stSidebar"] [data-testid="stSelectbox"] > div,
[data-testid="stSidebar"] [data-testid="stMultiSelect"] > div {
  background: rgba(255,255,255,0.06) !important;
  border: 1px solid rgba(255,255,255,0.1) !important;
  border-radius: 8px !important;
  color: rgba(255,255,255,0.75) !important;
}
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.07) !important; }

/* ── TITRES PRINCIPAUX ── */
h1 {
  font-size: 20px !important;
  font-weight: 600 !important;
  color: var(--text) !important;
  letter-spacing: -0.3px !important;
  border: none !important;
  padding: 0 !important;
  margin-bottom: 0.25rem !important;
}
h2 {
  font-size: 13px !important;
  font-weight: 500 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.7px !important;
  color: var(--text-3) !important;
  border: none !important;
  padding-bottom: 6px !important;
  border-bottom: 1px solid var(--border) !important;
  margin-top: 1.5rem !important;
}
h3 {
  font-size: 13px !important;
  font-weight: 500 !important;
  color: var(--text) !important;
  margin-bottom: 0 !important;
}

/* ── CARTES KPI ── */
.kpi-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 16px 18px 14px;
  position: relative;
  overflow: hidden;
  transition: box-shadow 0.2s, transform 0.2s;
  height: 100%;
}
.kpi-card:hover {
  box-shadow: 0 4px 20px rgba(0,0,0,0.07);
  transform: translateY(-1px);
}
.kpi-card::before {
  content: '';
  position: absolute;
  top: 14px; bottom: 14px; left: 0;
  width: 3px;
  border-radius: 0 2px 2px 0;
}
.kpi-card.blue::before  { background: var(--blue); }
.kpi-card.green::before { background: var(--green); }
.kpi-card.amber::before { background: var(--amber); }
.kpi-card.teal::before  { background: var(--teal); }
.kpi-card.red::before   { background: var(--red); }

.kpi-label {
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  color: var(--text-2);
  margin-bottom: 8px;
}
.kpi-value {
  font-size: 26px;
  font-weight: 600;
  color: var(--text);
  letter-spacing: -0.5px;
  font-family: 'DM Mono', monospace;
  line-height: 1;
  margin-bottom: 8px;
}
.kpi-value small {
  font-size: 14px;
  font-weight: 400;
  color: var(--text-2);
  font-family: 'DM Sans', sans-serif;
  margin-left: 2px;
}
.kpi-footer {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: var(--text-3);
}
.tag {
  display: inline-flex;
  align-items: center;
  font-size: 10.5px;
  font-weight: 500;
  padding: 2px 7px;
  border-radius: 20px;
  line-height: 1.5;
}
.tag.up   { background: #dcfce7; color: #15803d; }
.tag.down { background: #fee2e2; color: #b91c1c; }
.tag.info { background: #dbeafe; color: #1d4ed8; }
.tag.warn { background: #fef3c7; color: #b45309; }
.tag.neu  { background: #f1f5f9; color: #475569; }

/* ── BANDEAU ALERTE ── */
.alert-strip {
  background: var(--surface);
  border: 1px solid rgba(245,158,11,0.3);
  background: rgba(245,158,11,0.03);
  border-radius: var(--radius-lg);
  padding: 13px 18px;
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}
.alert-chips { display: flex; gap: 7px; flex-wrap: wrap; }
.chip {
  font-size: 11px;
  font-weight: 500;
  padding: 4px 11px;
  border-radius: 20px;
}
.chip.err  { background: #fee2e2; color: #991b1b; }
.chip.warn { background: #fef3c7; color: #92400e; }
.chip.ok   { background: #dcfce7; color: #166534; }

/* ── CARTE GÉNÉRIQUE ── */
.content-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 18px 20px;
  margin-bottom: 0;
}

/* ── BOUTONS STREAMLIT ── */
.stButton > button {
  background: var(--navy) !important;
  color: #fff !important;
  border: none !important;
  border-radius: var(--radius) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-weight: 500 !important;
  font-size: 13px !important;
  padding: 0.55rem 1.2rem !important;
  transition: background 0.15s !important;
}
.stButton > button:hover {
  background: #1e3a52 !important;
}

/* ── MÉTRIQUES STREAMLIT (st.metric) ── */
[data-testid="stMetric"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-lg) !important;
  padding: 14px 16px !important;
}
[data-testid="stMetricLabel"] {
  font-size: 11px !important;
  text-transform: uppercase !important;
  letter-spacing: 0.5px !important;
  font-weight: 500 !important;
  color: var(--text-2) !important;
}
[data-testid="stMetricValue"] {
  font-size: 22px !important;
  font-weight: 600 !important;
  font-family: 'DM Mono', monospace !important;
  color: var(--text) !important;
}

/* ── ONGLETS ── */
[data-testid="stTabs"] [role="tablist"] {
  border-bottom: 1px solid var(--border) !important;
  gap: 4px !important;
}
[data-testid="stTabs"] [role="tab"] {
  font-size: 13px !important;
  font-weight: 400 !important;
  color: var(--text-2) !important;
  border-radius: 0 !important;
  border-bottom: 2px solid transparent !important;
  background: none !important;
  padding: 8px 14px !important;
  transition: all 0.15s !important;
}
[data-testid="stTabs"] [role="tab"]:hover { color: var(--text) !important; }
[data-testid="stTabs"] [aria-selected="true"] {
  color: var(--blue) !important;
  border-bottom-color: var(--blue) !important;
  font-weight: 500 !important;
}

/* ── DATAFRAME ── */
[data-testid="stDataFrame"] {
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-lg) !important;
  overflow: hidden !important;
}

/* ── MESSAGES ── */
.stSuccess, .stWarning, .stError, .stInfo {
  border-radius: var(--radius) !important;
  font-size: 13px !important;
}

/* ── SELECTBOX / INPUT ── */
[data-testid="stSelectbox"] > div,
[data-testid="stDateInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input {
  border-radius: var(--radius) !important;
  border: 1px solid rgba(0,0,0,0.12) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 13px !important;
}

/* ── CARTE RÉSUMÉ BLEU NUIT ── */
.summary-card {
  background: var(--navy);
  border-radius: var(--radius-lg);
  padding: 20px;
  color: rgba(255,255,255,0.55);
  font-size: 12px;
}
.summary-card .big { font-size: 28px; font-weight: 600; color: #fff; font-family: 'DM Mono', monospace; letter-spacing: -0.5px; }
.summary-card .divider { border-color: rgba(255,255,255,0.08); margin: 10px 0; }
.summary-card .row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.summary-card .val { font-family: 'DM Mono', monospace; font-size: 13px; color: rgba(255,255,255,0.85); }

/* ── STATUT DOT ── */
.status-dot { display: inline-flex; align-items: center; gap: 5px; font-size: 12px; }
.dot { width: 7px; height: 7px; border-radius: 50%; display: inline-block; flex-shrink: 0; }
.dot.green { background: #22c55e; }
.dot.amber { background: #f59e0b; }
.dot.red   { background: #ef4444; }

/* ── PROGRESS BAR ── */
.prog-wrap { display: flex; align-items: center; gap: 8px; }
.prog-bar  { flex: 1; height: 5px; background: #f1f5f9; border-radius: 3px; overflow: hidden; }
.prog-fill { height: 100%; border-radius: 3px; }

/* ── ANIMATIONS ── */
@keyframes fade-up {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}
.kpi-card { animation: fade-up 0.35s ease both; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if 'date_debut' not in st.session_state:
    st.session_state['date_debut'] = datetime.now() - timedelta(days=30)
if 'date_fin' not in st.session_state:
    st.session_state['date_fin'] = datetime.now()

# ─────────────────────────────────────────────
# MAPPING GÉOGRAPHIQUE
# ─────────────────────────────────────────────
REGIONS_MAPPING = {
    "Dakar": [
        {"code": "dakar",       "nom": "Dakar"},
        {"code": "guediawaye",  "nom": "Guediawaye"},
        {"code": "pikine",      "nom": "Pikine"},
        {"code": "rufisque",    "nom": "Rufisque"},
        {"code": "keur_massar", "nom": "Keur Massar"},
    ]
}

def get_regions():
    return list(REGIONS_MAPPING.keys())

def get_departements_by_region(region):
    return REGIONS_MAPPING.get(region, [])

def execute_query_with_filters(query_base, params):
    selected_uc_names = st.session_state.get('selected_unites_communales', [])
    df = execute_query(query_base, params)
    if not selected_uc_names or df.empty:
        return df
    # prioriser la colonne exactement présente dans le DataFrame
    if 'unite_communale_nom' in df.columns:
        df_filtered = df[df['unite_communale_nom'].isin(selected_uc_names)]
        return df_filtered
    if 'unite_communale' in df.columns:
        df_filtered = df[df['unite_communale'].isin(selected_uc_names)]
        return df_filtered
    return df

# ─────────────────────────────────────────────
# HELPERS UI
# ─────────────────────────────────────────────
def kpi_card(color, label, value, unit="", footer_tag="", footer_tag_type="neu", footer_text=""):
    """Génère une carte KPI HTML avec accent coloré."""
    tag_html = f'<span class="tag {footer_tag_type}">{footer_tag}</span>' if footer_tag else ""
    return f"""
    <div class="kpi-card {color}">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}<small>{unit}</small></div>
      <div class="kpi-footer">{tag_html} {footer_text}</div>
    </div>
    """

def section_header(emoji, title, subtitle=""):
    st.markdown(f"""
    <div style='margin-bottom:1rem;'>
      <h1>{emoji} {title}</h1>
      <p style='color:var(--text-3);font-size:13px;margin-top:2px;'>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

def alert_strip(items):
    """Bandeau d'alertes : items = liste de (label, type) avec type in err/warn/ok"""
    chips = "".join(f'<span class="chip {t}">{l}</span>' for l, t in items)
    count = sum(1 for _, t in items if t in ('err', 'warn'))
    return f"""
    <div class="alert-strip">
      <span style="font-size:16px;">{'⚠️' if count else '✅'}</span>
      <span style="font-size:13px;font-weight:500;color:var(--text);">
        {'Alertes actives' if count else 'Aucune alerte'}
      </span>
      <span style="font-size:12px;color:var(--text-2);">Période sélectionnée</span>
      <div class="alert-chips" style="margin-left:auto;">{chips}</div>
    </div>
    """

# ─────────────────────────────────────────────
# FONCTIONS DE GÉNÉRATION PDF (inchangées)
# ─────────────────────────────────────────────
def generate_monthly_report_pdf(year, month, df_month, month_name):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from io import BytesIO
    import matplotlib.pyplot as plt

    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('T', parent=styles['Heading1'], fontSize=20, alignment=TA_CENTER,
                                  textColor=colors.HexColor('#0f2235'))
    heading_style = ParagraphStyle('H', parent=styles['Heading2'], fontSize=13,
                                    textColor=colors.HexColor('#0f2235'))
    normal_style = styles['Normal']

    elements.append(Paragraph(f"Rapport Mensuel SONAGED", title_style))
    elements.append(Paragraph(
        f"<b>{month_name} {year}</b> | Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
        ParagraphStyle('s', parent=normal_style, fontSize=11, alignment=TA_CENTER,
                       textColor=colors.grey)
    ))
    elements.append(Spacer(1, 0.3*inch))

    nb_rapports  = len(df_month)
    tonnage_mois = float(df_month['tonnage_total'].sum())
    circuits_mois = int(df_month['circuits_collectes'].sum())
    km_mois = float(df_month['km_balayes'].sum() if 'km_balayes' in df_month.columns else 0)
    tonnage_moyen  = tonnage_mois  / nb_rapports if nb_rapports else 0
    circuits_moyen = circuits_mois / nb_rapports if nb_rapports else 0

    elements.append(Paragraph("Indicateurs Clés", heading_style))
    kpi_data = [
        ['Métrique', 'Valeur', 'Moyenne/jour'],
        ['Nombre de rapports', str(nb_rapports), '-'],
        ['Tonnage total collecté', f'{tonnage_mois:.1f} t', f'{tonnage_moyen:.2f} t'],
        ['Circuits collectés', str(circuits_mois), f'{circuits_moyen:.1f}'],
        ['Kilométrage balayé', f'{km_mois:.1f} km',
         f'{(km_mois/nb_rapports if nb_rapports else 0):.2f} km'],
    ]
    kpi_table = Table(kpi_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f2235')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f0f4f8')])
    ]))
    elements.append(kpi_table)
    elements.append(Spacer(1, 0.3*inch))

    try:
        fig, ax = plt.subplots(figsize=(7, 3), dpi=100)
        ax.plot(df_month['date_rapport'], df_month['tonnage_total'],
                marker='o', color='#3b82f6', linewidth=2)
        ax.set_xlabel('Date'); ax.set_ylabel('Tonnage (t)')
        ax.set_title('Évolution du Tonnage Collecté'); ax.grid(True, alpha=0.3)
        plt.tight_layout()
        img_buf = BytesIO(); fig.savefig(img_buf, format='png', dpi=100, bbox_inches='tight')
        img_buf.seek(0); plt.close(fig)
        elements.append(Image(img_buf, width=6*inch, height=2.5*inch))
        elements.append(Spacer(1, 0.2*inch))
    except Exception as e:
        elements.append(Paragraph(f"<i>Erreur graphique: {e}</i>", normal_style))

    elements.append(PageBreak())
    elements.append(Paragraph("Résumé", heading_style))
    elements.append(Paragraph(f"""
    <b>Période:</b> {month_name} {year}<br/>
    <b>Rapports:</b> {nb_rapports}<br/>
    <b>Tonnage:</b> {tonnage_mois:.1f} t<br/>
    <b>Circuits:</b> {circuits_mois}<br/>
    <b>KM balayés:</b> {km_mois:.1f} km
    """, normal_style))

    elements.append(Paragraph(
        "<i>Rapport généré automatiquement par le système SONAGED.</i>",
        ParagraphStyle('f', parent=normal_style, fontSize=9,
                       textColor=colors.grey, alignment=TA_CENTER)
    ))
    doc.build(elements)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()


def generate_period_report_pdf(period_label, start_date, end_date, df_data):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from io import BytesIO

    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('T', parent=styles['Title'], fontSize=18, alignment=TA_CENTER,
                                  textColor=colors.HexColor('#0f2235'))

    elements.append(Paragraph(f"Rapport {period_label} SONAGED", title_style))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(f"Période: {start_date} → {end_date}", styles['Normal']))
    elements.append(Paragraph(f"Généré le: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))

    kpi_data = [["KPI", "Valeur"]]
    if not df_data.empty:
        if 'tonnage_total'      in df_data.columns: kpi_data.append(["Tonnage total",      f"{float(df_data['tonnage_total'].sum()):,.2f} t"])
        if 'circuits_collectes' in df_data.columns: kpi_data.append(["Circuits collectés", str(int(df_data['circuits_collectes'].sum()))])
        if 'circuits_planifies' in df_data.columns: kpi_data.append(["Circuits planifiés", str(int(df_data['circuits_planifies'].sum()))])
        if 'km_balayes'         in df_data.columns: kpi_data.append(["Kilométrage balayé", f"{float(df_data['km_balayes'].sum()):,.2f} km"])

    if len(kpi_data) > 1:
        kpi_table = Table(kpi_data, colWidths=[3*inch, 3*inch])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#22c55e')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ]))
        elements.append(kpi_table)
        elements.append(Spacer(1, 0.3*inch))

    if not df_data.empty:
        elements.append(Paragraph("Données (20 premières lignes)", styles['Heading3']))
        table_data = [list(df_data.columns)]
        for row in df_data.head(20).itertuples(index=False):
            table_data.append([str(getattr(row, col, '')) for col in df_data.columns])
        table = Table(table_data, repeatRows=1, colWidths=[1.0*inch for _ in df_data.columns])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f2235')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f0f4f8')]),
            ('GRID', (0,0), (-1,-1), 0.25, colors.lightgrey),
        ]))
        elements.append(table)

    doc.build(elements)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()

# ─────────────────────────────────────────────
# FONCTIONS ALERTES (inchangées)
# ─────────────────────────────────────────────
def get_circuits_non_termines(date_debut, date_fin):
    from utils.database import execute_query_dict
    query = """
    SELECT dr.date_rapport, uc.nom AS unite_communale,
           cc.nom_circuit, cc.camion, cc.poids_circuit,
           cc.duree_collecte, cs.libelle AS status
    FROM collection_circuits cc
    JOIN daily_reports dr ON cc.daily_report_id = dr.id
    LEFT JOIN unites_communales uc ON dr.unite_communale_id = uc.id
    LEFT JOIN circuit_status cs ON cc.status_id = cs.id
    WHERE dr.date_rapport >= %s AND dr.date_rapport <= %s
      AND cs.code != 'termine'
    ORDER BY dr.date_rapport DESC LIMIT 20
    """
    try:
        return execute_query_dict(query, (date_debut, date_fin))
    except Exception as e:
        st.error(f"Erreur: {e}"); return []

def get_tonnage_nul(date_debut, date_fin):
    from utils.database import execute_query_dict
    query = """
    SELECT dr.date_rapport, uc.nom AS unite_communale,
           dr.circuits_collectes, dr.tonnage_total,
           COUNT(cc.id) AS nombre_circuits
    FROM daily_reports dr
    LEFT JOIN unites_communales uc ON dr.unite_communale_id = uc.id
    LEFT JOIN collection_circuits cc ON dr.id = cc.daily_report_id
    WHERE dr.date_rapport >= %s AND dr.date_rapport <= %s
      AND (dr.tonnage_total = 0 OR dr.tonnage_total IS NULL)
    GROUP BY dr.id, dr.date_rapport, uc.nom, dr.circuits_collectes, dr.tonnage_total
    ORDER BY dr.date_rapport DESC LIMIT 20
    """
    try:
        return execute_query_dict(query, (date_debut, date_fin))
    except Exception as e:
        st.error(f"Erreur: {e}"); return []

def get_duree_anormale(date_debut, date_fin, max_duree=8):
    from utils.database import execute_query_dict
    query = f"""
    SELECT dr.date_rapport, uc.nom AS unite_communale,
           cc.nom_circuit, cc.camion, cc.poids_circuit,
           cc.duree_collecte,
           CASE WHEN cc.duree_collecte > {max_duree*1.5} THEN 'Critique'
                WHEN cc.duree_collecte > {max_duree} THEN 'Alerte'
                ELSE 'Normal' END AS severite
    FROM collection_circuits cc
    JOIN daily_reports dr ON cc.daily_report_id = dr.id
    LEFT JOIN unites_communales uc ON dr.unite_communale_id = uc.id
    WHERE dr.date_rapport >= %s AND dr.date_rapport <= %s
      AND cc.duree_collecte > {max_duree}
    ORDER BY cc.duree_collecte DESC LIMIT 20
    """
    try:
        return execute_query_dict(query, (date_debut, date_fin))
    except Exception as e:
        st.error(f"Erreur: {e}"); return []

def get_absences_excessives(date_debut, date_fin, seuil_pct=20):
    from utils.database import execute_query_dict
    query = f"""
    SELECT DISTINCT dr.date_rapport, uc.nom AS unite_communale,
           'Matin' AS shift, pm.effectif_total, pm.absents,
           pm.malades, pm.conges, pm.retard,
           ROUND(100.0*pm.absents/NULLIF(pm.effectif_total,0),1) AS taux_absence_pct
    FROM personnel_matin pm
    JOIN daily_reports dr ON pm.daily_report_id = dr.id
    LEFT JOIN unites_communales uc ON dr.unite_communale_id = uc.id
    WHERE dr.date_rapport >= %s AND dr.date_rapport <= %s
      AND (pm.absents+pm.malades+pm.conges) > ({seuil_pct}/100.0)*pm.effectif_total
    UNION ALL
    SELECT DISTINCT dr.date_rapport, uc.nom, 'Après-midi',
           pam.effectif_total, pam.absents, pam.malades, pam.conges, pam.retard,
           ROUND(100.0*pam.absents/NULLIF(pam.effectif_total,0),1)
    FROM personnel_apres_midi pam
    JOIN daily_reports dr ON pam.daily_report_id = dr.id
    LEFT JOIN unites_communales uc ON dr.unite_communale_id = uc.id
    WHERE dr.date_rapport >= %s AND dr.date_rapport <= %s
      AND (pam.absents+pam.malades+pam.conges) > ({seuil_pct}/100.0)*pam.effectif_total
    UNION ALL
    SELECT DISTINCT dr.date_rapport, uc.nom, 'Nuit',
           pn.effectif_total, pn.absents, pn.malades, pn.conges, pn.retard,
           ROUND(100.0*pn.absents/NULLIF(pn.effectif_total,0),1)
    FROM personnel_nuit pn
    JOIN daily_reports dr ON pn.daily_report_id = dr.id
    LEFT JOIN unites_communales uc ON dr.unite_communale_id = uc.id
    WHERE dr.date_rapport >= %s AND dr.date_rapport <= %s
      AND (pn.absents+pn.malades+pn.conges) > ({seuil_pct}/100.0)*pn.effectif_total
    ORDER BY date_rapport DESC LIMIT 30
    """
    try:
        return execute_query_dict(query,
            (date_debut, date_fin, date_debut, date_fin, date_debut, date_fin))
    except Exception as e:
        st.error(f"Erreur: {e}"); return []


# ═══════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='display:flex;align-items:center;gap:10px;padding:18px 0 16px;
                border-bottom:1px solid rgba(255,255,255,0.07);margin-bottom:4px;'>
      <div style='width:34px;height:34px;background:#22c55e;border-radius:8px;
                  display:flex;align-items:center;justify-content:center;font-size:16px;'>🗑</div>
      <div>
        <div style='font-size:15px;font-weight:600;color:#fff;line-height:1.2;'>SONAGED</div>
        <div style='font-size:10px;color:rgba(255,255,255,0.35);text-transform:uppercase;letter-spacing:0.3px;'>
          Reporting & Analyse</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Connexion BD
    if test_connection():
        st.markdown("""
        <div style='display:flex;align-items:center;gap:7px;padding:8px 0 4px;'>
          <div style='width:7px;height:7px;border-radius:50%;background:#22c55e;
                      box-shadow:0 0 0 2px rgba(34,197,94,0.25);'></div>
          <span style='font-size:11px;color:rgba(255,255,255,0.4);'>Base de données active</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error("✗ Connexion BD échouée")
        st.stop()

    st.markdown("---")

    # ── PÉRIODE ──
    st.subheader("Période")
    periode = st.selectbox("",
        ["Aujourd'hui", "Cette semaine", "Ce mois", "Personnalisée"],
        key="periode_selector", label_visibility="collapsed")

    today = datetime.now().date()
    if periode == "Aujourd'hui":
        st.session_state['date_debut'] = today
        st.session_state['date_fin']   = today
    elif periode == "Cette semaine":
        st.session_state['date_debut'] = today - timedelta(days=today.weekday())
        st.session_state['date_fin']   = today
    elif periode == "Ce mois":
        st.session_state['date_debut'] = today.replace(day=1)
        st.session_state['date_fin']   = today

    if periode == "Personnalisée":
        col1, col2 = st.columns(2)
        with col1:
            d1 = st.date_input("De", value=st.session_state['date_debut'],
                               max_value=datetime.now(), key="dd_input")
        with col2:
            d2 = st.date_input("À",  value=st.session_state['date_fin'],
                               max_value=datetime.now(), key="df_input")
        st.session_state['date_debut'] = d1
        st.session_state['date_fin']   = d2

    st.markdown("---")

    # ── FILTRES GÉO ──
    st.subheader("Filtres géographiques")

    if 'selected_region' not in st.session_state:
        st.session_state['selected_region'] = None
    if 'selected_departements' not in st.session_state:
        st.session_state['selected_departements'] = []
    if 'selected_unites_communales' not in st.session_state:
        st.session_state['selected_unites_communales'] = []

    selected_region = st.selectbox("Région", get_regions(), key="region_selector")
    st.session_state['selected_region'] = selected_region

    if selected_region:
        depts = get_departements_by_region(selected_region)
        dept_names = [d['nom'] for d in depts]
        dept_codes = {d['nom']: d['code'] for d in depts}

        selected_depts_names = st.multiselect("Département(s)", dept_names,
                                               default=dept_names, key="dept_selector")
        selected_dept_codes = [dept_codes[n] for n in selected_depts_names]
        st.session_state['selected_departements'] = selected_dept_codes

        if selected_dept_codes:
            from utils.database import execute_query_dict
            from utils.queries import QUERY_UNITES_COMMUNALES_BY_DEPT_CODES
            try:
                all_uc = execute_query_dict(QUERY_UNITES_COMMUNALES_BY_DEPT_CODES,
                                            (selected_dept_codes,))
            except:
                all_uc = []

            if all_uc:
                uc_names = [u.get('nom', '') for u in all_uc]
                selected_uc_names = st.multiselect("Unité(s) Communale(s)", uc_names,
                                                    default=uc_names, key="uc_selector")
                st.session_state['selected_unites_communales'] = selected_uc_names
            else:
                st.session_state['selected_unites_communales'] = []
        else:
            st.session_state['selected_unites_communales'] = []

    st.markdown("---")

    if st.button("🔄 Rafraîchir"):
        try: st.cache_data.clear()
        except: pass
        try: st.cache_resource.clear()
        except: pass
        st.rerun()

    st.markdown(f"""
    <div style='font-size:10px;color:rgba(255,255,255,0.25);margin-top:8px;line-height:1.8;'>
      Version 2.0 · 2026-01-16<br>
      {st.session_state['date_debut']} → {st.session_state['date_fin']}
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════
def main():
    from utils.database import execute_query_dict
    from streamlit_folium import st_folium
    import folium
    from folium import FeatureGroup, LayerControl, CircleMarker, Polygon
    from folium.plugins import MarkerCluster
    import statistics, json, calendar
    import plotly.express as px
    from io import BytesIO

    # En-tête page
    col_title, col_period = st.columns([3, 2])
    with col_title:
        st.markdown(f"""
        <h1>🗑️ Vue d'ensemble</h1>
        <p style='color:var(--text-3);font-size:13px;margin-top:2px;'>
          Situation générale · {st.session_state['date_debut']} → {st.session_state['date_fin']}
        </p>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── ONGLETS ──
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🧭 Vue d'ensemble",
        "🗺️ Analyse spatiale",
        "🧩 Activités",
        "🚛 Performance",
        "⚠️ Alertes",
        "📊 Rapports"
    ])

    # ═══════════════════════════════════════════════════════
    # TAB 1 : VUE D'ENSEMBLE
    # ═══════════════════════════════════════════════════════
    with tab1:

        # ── Données réelles ──
        df_reports = execute_query_with_filters(
            QUERY_DAILY_SUMMARY,
            (st.session_state['date_debut'], st.session_state['date_fin'])
        )

        # ── Calculs KPI ──
        tonnage_total      = float(df_reports['tonnage_total'].sum())      if not df_reports.empty else 0
        circuits_planifies = int(df_reports['circuits_planifies'].sum())   if not df_reports.empty else 0
        circuits_collectes = int(df_reports['circuits_collectes'].sum())   if not df_reports.empty else 0
        incidents          = int(df_reports['nombre_interventions'].sum()) if (not df_reports.empty and 'nombre_interventions' in df_reports.columns) else 0
        couverture         = int(circuits_collectes / circuits_planifies * 100) if circuits_planifies > 0 else 0

        df_circuits_dur = execute_query(QUERY_CIRCUITS_DETAILS, (st.session_state['date_debut'],))
        duree_moy = 0
        if not df_circuits_dur.empty and 'duree_collecte' in df_circuits_dur.columns:
            d = df_circuits_dur['duree_collecte'].mean()
            duree_moy = round(d, 1) if not pd.isna(d) else 0

        # ── Bandeau alertes ──
        alert_items = []
        if circuits_planifies > 0 and couverture < 80:
            alert_items.append((f"Couverture {couverture}% < 80%", "warn"))
        if incidents > 0:
            alert_items.append((f"{incidents} incident(s)", "err" if incidents > 2 else "warn"))
        if not alert_items:
            alert_items.append(("Tous les indicateurs conformes ✓", "ok"))

        st.markdown(alert_strip(alert_items), unsafe_allow_html=True)
        st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)

        # ── KPI CARDS ──
        st.markdown("<h2>Indicateurs clés</h2>", unsafe_allow_html=True)

        c1, c2, c3, c4, c5 = st.columns(5)

        with c1:
            tag = "up" if tonnage_total > 30 else ("warn" if tonnage_total > 10 else "down")
            st.markdown(kpi_card(
                "blue", "Tonnage collecté",
                f"{tonnage_total:,.1f}", "t",
                "Période sélectionnée", "info"
            ), unsafe_allow_html=True)

        with c2:
            tag = "up" if couverture >= 80 else ("warn" if couverture >= 60 else "down")
            tag_lbl = f"{'▲' if couverture >= 80 else '▼'} {couverture}%"
            st.markdown(kpi_card(
                "green", "Taux de couverture",
                f"{couverture}", "%",
                "Objectif 80%" if couverture >= 80 else f"En dessous objectif",
                "up" if couverture >= 80 else "down"
            ), unsafe_allow_html=True)

        with c3:
            tag = "up" if circuits_collectes >= circuits_planifies else ("warn" if circuits_collectes >= circuits_planifies * 0.7 else "down")
            st.markdown(kpi_card(
                "teal", "Circuits réalisés",
                f"{circuits_collectes}", f"/{circuits_planifies}",
                f"{max(0, circuits_planifies - circuits_collectes)} restants",
                "info"
            ), unsafe_allow_html=True)

        with c4:
            tag = "neu" if duree_moy <= 8 else "warn"
            st.markdown(kpi_card(
                "amber", "Durée moy. collecte",
                f"{duree_moy}", "h",
                "Normal" if duree_moy <= 8 else "Dépasse seuil",
                "neu" if duree_moy <= 8 else "down"
            ), unsafe_allow_html=True)

        with c5:
            st.markdown(kpi_card(
                "red", "Incidents / anomalies",
                f"{incidents}", "",
                "À traiter" if incidents > 0 else "Aucun incident",
                "down" if incidents > 0 else "up"
            ), unsafe_allow_html=True)

        st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)

        # ── GRAPHIQUES ──
        st.markdown("<h2>Graphiques synthétiques</h2>", unsafe_allow_html=True)

        if not df_reports.empty:
            cg1, cg2, cg3 = st.columns(3)

            with cg1:
                df_t = df_reports.groupby('date_rapport').agg(
                    tonnage_total=('tonnage_total', 'sum'),
                    poids_total_circuits=('poids_total_circuits', 'sum')
                ).reset_index().fillna(0)
                fig = px.area(df_t, x='date_rapport', y='tonnage_total',
                              title="Tonnage collecté",
                              labels={'tonnage_total': 'Tonnage (t)', 'date_rapport': 'Date'},
                              color_discrete_sequence=['#3b82f6'])
                fig.update_traces(fill='tozeroy', line_width=1.5)
                fig.update_layout(height=300, margin=dict(l=10,r=10,t=40,b=10),
                                  paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                  font_family="DM Sans",
                                  xaxis=dict(showgrid=False),
                                  yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)'))
                st.plotly_chart(fig, use_container_width=True)

            with cg2:
                from utils.queries import QUERY_CONCESSIONNAIRES_PERFORMANCE
                df_conces = execute_query_with_filters(
                    QUERY_CONCESSIONNAIRES_PERFORMANCE, (st.session_state['date_debut'],))
                if not df_conces.empty:
                    df_cp = df_conces[['concessionnaire', 'poids_total']].head(8).copy()
                    df_cp.columns = ['Concessionnaire', 'Tonnage']
                    fig2 = px.bar(df_cp, x='Tonnage', y='Concessionnaire', orientation='h',
                                  title="Par concessionnaire",
                                  color_discrete_sequence=['#22c55e'])
                    fig2.update_layout(height=300, margin=dict(l=10,r=10,t=40,b=10),
                                       paper_bgcolor='rgba(0,0,0,0)',
                                       plot_bgcolor='rgba(0,0,0,0)',
                                       font_family="DM Sans",
                                       yaxis=dict(showgrid=False),
                                       xaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)'))
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.info("Pas de données concessionnaires.")

            with cg3:
                restants = max(0, circuits_planifies - circuits_collectes)
                fig3 = px.pie(
                    values=[circuits_collectes, restants],
                    names=["Réalisés", "Restants"],
                    hole=0.65,
                    title="Réalisation circuits",
                    color_discrete_sequence=['#3b82f6', '#f1f5f9']
                )
                fig3.update_layout(height=300, margin=dict(l=10,r=10,t=40,b=10),
                                   paper_bgcolor='rgba(0,0,0,0)', font_family="DM Sans",
                                   legend=dict(orientation='h', y=-0.1))
                fig3.update_traces(textinfo='percent')
                st.plotly_chart(fig3, use_container_width=True)

        # ── DERNIERS RAPPORTS ──
        st.markdown("<h2>Derniers rapports</h2>", unsafe_allow_html=True)
        if not df_reports.empty:
            st.dataframe(df_reports.head(15), use_container_width=True, hide_index=True)
        else:
            st.info("Aucun rapport pour la période sélectionnée.")

    # ═══════════════════════════════════════════════════════
    # TAB 2 : ANALYSE SPATIALE  (identique à l'original)
    # ═══════════════════════════════════════════════════════
    with tab2:
        section_header("🗺️", "Analyse Spatiale",
                        "Carte interactive — points extraits depuis les données Kobo")

        sql = ("SELECT id, kobo_submission_id, form_data FROM raw_kobo.submissions "
               "WHERE form_data IS NOT NULL ORDER BY id DESC LIMIT 1000")
        submissions = execute_query_dict(sql)

        def extract_gps(obj):
            if obj is None: return None
            if isinstance(obj, (list, tuple)) and len(obj) == 2:
                try: return (float(obj[0]), float(obj[1]))
                except: return None
            if isinstance(obj, str):
                parts = [p for p in obj.replace(',', ' ').split() if p]
                if len(parts) >= 2:
                    try: return (float(parts[0]), float(parts[1]))
                    except: pass
                return None
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if isinstance(k, str) and any(x in k.lower() for x in ('gps','geolocation','location')):
                        r = extract_gps(v)
                        if r: return r
                for v in obj.values():
                    r = extract_gps(v)
                    if r: return r
            if isinstance(obj, (list, tuple)):
                for v in obj:
                    r = extract_gps(v)
                    if r: return r
            return None

        uc_points = {}; circuit_points = []
        for s in submissions:
            fd = s.get('form_data')
            if isinstance(fd, str):
                try: fd = json.loads(fd)
                except: fd = None
            gps = extract_gps(fd)
            uc_code = None
            if isinstance(fd, dict):
                uc_code = fd.get('group_nu8sp57/unite') or fd.get('group_nu8sp57/unite_commune')
            if gps:
                lat, lon = gps
                if uc_code: uc_points.setdefault(uc_code, []).append((lat, lon))
                if isinstance(fd, dict) and 'circuits' in fd and isinstance(fd['circuits'], list):
                    for c in fd['circuits']:
                        statut = c.get('circuits/statut') or c.get('statut') or 'unknown'
                        circuit_points.append({'lat': lat, 'lon': lon, 'statut': statut,
                                               'nom': c.get('circuits/nom_circuit',''),
                                               'poids': c.get('circuits/poids_circuit')})

        df_uc = execute_query(
            "SELECT unite_communale_code, unite_communale_nom, depots_sauvages, "
            "depots_recurrents, sites_caisse, nb_caisses FROM v_daily_reports_summary "
            "WHERE date_rapport >= %s", (st.session_state['date_debut'],))
        uc_info = {}
        if not df_uc.empty:
            for _, r in df_uc.iterrows():
                uc_info[r['unite_communale_code']] = {
                    'nom': r['unite_communale_nom'],
                    'depots_sauvages': int(r['depots_sauvages'] or 0),
                    'depots_recurrents': int(r['depots_recurrents'] or 0),
                    'sites_caisse': int(r['sites_caisse'] or 0),
                    'nb_caisses': int(r['nb_caisses'] or 0)
                }

        def convex_hull_latlon(points):
            pts = sorted(set((p[1], p[0]) for p in points))
            if len(pts) <= 2: return [(y,x) for x,y in pts]
            def cross(o,a,b): return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
            lower = []
            for p in pts:
                while len(lower)>=2 and cross(lower[-2],lower[-1],p)<=0: lower.pop()
                lower.append(p)
            upper = []
            for p in reversed(pts):
                while len(upper)>=2 and cross(upper[-2],upper[-1],p)<=0: upper.pop()
                upper.append(p)
            hull = lower[:-1]+upper[:-1]
            return [(y,x) for x,y in hull]

        cols = st.columns([1,1,1,1])
        show_points  = cols[0].checkbox("Points (photos)", value=True)
        show_cover   = cols[1].checkbox("Zones UC",        value=True)
        show_depots  = cols[2].checkbox("Dépôts",          value=True)
        show_caisses = cols[3].checkbox("Caisses",         value=True)

        if uc_points:
            mean_lat = statistics.mean([pt[0] for pts in uc_points.values() for pt in pts])
            mean_lon = statistics.mean([pt[1] for pts in uc_points.values() for pt in pts])
        else:
            mean_lat, mean_lon = 14.6937, -17.44406

        m = folium.Map(location=[mean_lat, mean_lon], zoom_start=12)
        fg_pts = FeatureGroup(name='Points')
        fg_cov = FeatureGroup(name='Couverture UC')
        fg_dep = FeatureGroup(name='Dépôts')
        fg_cai = FeatureGroup(name='Caisses')
        fg_ok  = FeatureGroup(name='Circuits terminés')
        fg_nok = FeatureGroup(name='Circuits non terminés')

        if show_points:
            mc = MarkerCluster()
            for code, pts in uc_points.items():
                for lat, lon in pts:
                    folium.CircleMarker([lat,lon], radius=4, color='#3b82f6',
                                        fill=True, fill_opacity=0.7).add_to(mc)
            mc.add_to(fg_pts); fg_pts.add_to(m)

        if show_cover:
            for code, pts in uc_points.items():
                if len(pts) >= 3:
                    Polygon(locations=convex_hull_latlon(pts), color='#22c55e',
                            fill=True, fill_opacity=0.12,
                            popup=uc_info.get(code,{}).get('nom', code)).add_to(fg_cov)
            fg_cov.add_to(m)

        for code, info in uc_info.items():
            pts = uc_points.get(code, [])
            if not pts: continue
            clat = statistics.mean([p[0] for p in pts])
            clon = statistics.mean([p[1] for p in pts])
            if show_depots and (info['depots_sauvages'] > 0 or info['depots_recurrents'] > 0):
                folium.Marker([clat,clon], icon=folium.Icon(color='red', icon='exclamation-triangle'),
                    popup=f"{info['nom']} – Dépôts: {info['depots_sauvages']} "
                          f"(récurrents: {info['depots_recurrents']})").add_to(fg_dep)
            if show_caisses and info['sites_caisse'] > 0:
                folium.Marker([clat,clon], icon=folium.Icon(color='blue', icon='trash'),
                    popup=f"{info['nom']} – Caisses: {info['nb_caisses']} / {info['sites_caisse']} sites").add_to(fg_cai)
        fg_dep.add_to(m); fg_cai.add_to(m)

        for c in circuit_points:
            popup = f"{c.get('nom','')} – {c['statut']} – {c.get('poids','')}"
            fg = fg_ok if c['statut'].lower().startswith('term') else fg_nok
            color = 'green' if c['statut'].lower().startswith('term') else 'orange'
            folium.CircleMarker([c['lat'],c['lon']], radius=6, color=color,
                                fill=True, fill_opacity=0.8, popup=popup).add_to(fg)
        fg_ok.add_to(m); fg_nok.add_to(m)
        LayerControl().add_to(m)
        st_folium(m, width=900, height=650)

    # ═══════════════════════════════════════════════════════
    # TAB 3 : ACTIVITÉS  (identique à l'original)
    # ═══════════════════════════════════════════════════════
    with tab3:
        section_header("🧩", "Activités du Projet",
                        "Synthèse de toutes les activités issues du reporting journalier")

        date_start = pd.to_datetime(st.session_state['date_debut']).date()
        date_end   = pd.to_datetime(st.session_state['date_fin']).date()

        sql_collecte = """
            SELECT
              COALESCE(SUM(circuits_planifies),0)        AS circuits_planifies,
              COALESCE(SUM(circuits_collectes),0)        AS circuits_collectes,
              COALESCE(SUM(tonnage_total),0)             AS tonnage_total,
              COALESCE(SUM(depots_recurrents),0)         AS depots_recurrents,
              COALESCE(SUM(depots_recurrents_leves),0)   AS depots_recurrents_leves,
              COALESCE(SUM(depots_sauvages),0)           AS depots_sauvages,
              COALESCE(SUM(depots_sauvages_traites),0)   AS depots_sauvages_traites,
              COALESCE(SUM(sites_caisse),0)              AS sites_caisse,
              COALESCE(SUM(nb_caisses),0)                AS nb_caisses,
              COALESCE(SUM(caisses_levees),0)            AS caisses_levees,
              COALESCE(SUM(poids_caisses),0)             AS poids_caisses,
              COALESCE(SUM(nombre_circuits_planifies),0) AS nombre_circuits_planifies,
              COALESCE(SUM(circuits_balayage),0)         AS circuits_balayage,
              COALESCE(SUM(km_planifies),0)              AS km_planifies,
              COALESCE(SUM(km_balayes),0)                AS km_balayes,
              COALESCE(SUM(km_desensable),0)             AS km_desensable
            FROM v_daily_reports_summary
            WHERE date_rapport >= %s AND date_rapport <= %s
        """
        df_collecte = execute_query(sql_collecte, (date_start, date_end))
        if df_collecte.empty:
            st.info("Aucune donnée pour la période."); return

        row = df_collecte.iloc[0]

        st.markdown("<h2>Collecte – Généralités</h2>", unsafe_allow_html=True)
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Circuits planifiés",  int(row['circuits_planifies']))
        c2.metric("Circuits collectés",  int(row['circuits_collectes']))
        c3.metric("Tonnage total (t)",   f"{float(row['tonnage_total']):.1f}")
        c4.metric("Dépôts sauvages",     int(row['depots_sauvages']))

        st.markdown("<h2>Caisses polybennes</h2>", unsafe_allow_html=True)
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Sites de caisses",   int(row['sites_caisse']))
        c2.metric("Nombre de caisses",  int(row['nb_caisses']))
        c3.metric("Caisses levées",      int(row['caisses_levees']))
        c4.metric("Poids caisses (t)",   f"{float(row['poids_caisses']):.1f}")

        st.markdown("<h2>Nettoiement</h2>", unsafe_allow_html=True)
        c1,c2,c3,c4,c5 = st.columns(5)
        c1.metric("Circuits planifiés",  int(row['nombre_circuits_planifies']))
        c2.metric("Circuits balayés",    int(row['circuits_balayage']))
        c3.metric("KM planifiés",        f"{float(row['km_planifies']):.1f}")
        c4.metric("KM balayés",          f"{float(row['km_balayes']):.1f}")
        c5.metric("KM désensable",       f"{float(row['km_desensable']):.1f}")

        st.markdown("<h2>Circuits de collecte</h2>", unsafe_allow_html=True)
        df_circ = execute_query_with_filters(QUERY_CIRCUITS_DETAILS, (st.session_state['date_debut'],))
        if not df_circ.empty:
            df_circ = df_circ[pd.to_datetime(df_circ["date_rapport"]).dt.date.between(date_start, date_end)]
        if not df_circ.empty:
            st.dataframe(df_circ, use_container_width=True, hide_index=True)
        else:
            st.info("Aucun circuit.")

        st.markdown("<h2>Mobilier urbain</h2>", unsafe_allow_html=True)
        df_mob = execute_query("""
            SELECT dr.date_rapport, uc.nom AS unite_communale,
                   tm.libelle AS type_mobilier, mu.nb_sites, mu.nb_bacs,
                   mu.bacs_leves, om.libelle AS observation
            FROM mobilier_urbain mu
            JOIN daily_reports dr ON mu.daily_report_id = dr.id
            LEFT JOIN unites_communales uc ON dr.unite_communale_id = uc.id
            LEFT JOIN types_mobilier tm ON mu.type_mobilier_id = tm.id
            LEFT JOIN observations_mobilier om ON mu.observation_id = om.id
            WHERE dr.date_rapport >= %s AND dr.date_rapport <= %s
            ORDER BY dr.date_rapport DESC, mu.ordre
        """, (date_start, date_end))
        if not df_mob.empty:
            st.dataframe(df_mob, use_container_width=True, hide_index=True)
        else:
            st.info("Aucune donnée de mobilier urbain.")

        st.markdown("<h2>Interventions ponctuelles</h2>", unsafe_allow_html=True)
        df_interv = execute_query("""
            SELECT dr.date_rapport, uc.nom AS unite_communale,
                   ip.agents_interv, ip.pelles, ip.tasseuses, ip.camions,
                   ip.quartiers, COUNT(pi.id) AS nb_photos
            FROM interventions_ponctuelles ip
            JOIN daily_reports dr ON ip.daily_report_id = dr.id
            LEFT JOIN unites_communales uc ON dr.unite_communale_id = uc.id
            LEFT JOIN photos_interventions pi ON pi.intervention_id = ip.id
            WHERE dr.date_rapport >= %s AND dr.date_rapport <= %s
            GROUP BY dr.date_rapport, uc.nom, ip.id
            ORDER BY dr.date_rapport DESC, ip.ordre
        """, (date_start, date_end))
        if not df_interv.empty:
            st.dataframe(df_interv, use_container_width=True, hide_index=True)
        else:
            st.info("Aucune intervention.")

        st.markdown("<h2>Personnel</h2>", unsafe_allow_html=True)
        from utils.queries import QUERY_PERSONNEL_MATIN, QUERY_PERSONNEL_APM, QUERY_PERSONNEL_NUIT
        end_d = pd.to_datetime(date_end).date()
        frames = []
        for q, label in [(QUERY_PERSONNEL_MATIN,"Matin"),(QUERY_PERSONNEL_APM,"Après-midi"),(QUERY_PERSONNEL_NUIT,"Nuit")]:
            df_p = execute_query_with_filters(q, (date_start,))
            if not df_p.empty:
                df_p["date_rapport"] = pd.to_datetime(df_p["date_rapport"]).dt.date
                df_p = df_p[df_p["date_rapport"] <= end_d]
                df_p["periode"] = label
                frames.append(df_p)
        df_personnel = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
        if not df_personnel.empty:
            st.dataframe(df_personnel, use_container_width=True, hide_index=True)
        else:
            st.info("Aucune donnée de personnel.")

        st.markdown("<h2>Difficultés & Recommandations</h2>", unsafe_allow_html=True)
        cd1, cd2 = st.columns(2)
        df_diff = execute_query("""
            SELECT diff.libelle AS difficulte, COUNT(*) AS occurrences
            FROM daily_reports dr
            JOIN daily_reports_difficultes drd ON dr.id = drd.daily_report_id
            JOIN difficultes diff ON drd.difficulte_id = diff.id
            WHERE dr.date_rapport >= %s AND dr.date_rapport <= %s
            GROUP BY diff.libelle ORDER BY occurrences DESC
        """, (date_start, date_end))
        df_rec = execute_query("""
            SELECT rec.libelle AS recommandation, COUNT(*) AS occurrences
            FROM daily_reports dr
            JOIN daily_reports_recommandations drr ON dr.id = drr.daily_report_id
            JOIN recommandations rec ON drr.recommandation_id = rec.id
            WHERE dr.date_rapport >= %s AND dr.date_rapport <= %s
            GROUP BY rec.libelle ORDER BY occurrences DESC
        """, (date_start, date_end))
        with cd1:
            if not df_diff.empty: st.dataframe(df_diff, use_container_width=True, hide_index=True)
            else: st.info("Aucune difficulté.")
        with cd2:
            if not df_rec.empty: st.dataframe(df_rec, use_container_width=True, hide_index=True)
            else: st.info("Aucune recommandation.")

    # ═══════════════════════════════════════════════════════
    # TAB 4 : PERFORMANCE  (identique à l'original)
    # ═══════════════════════════════════════════════════════
    with tab4:
        section_header("🚛", "Analyse de Performance",
                        "Évaluation des performances opérationnelles")

        pt1, pt2, pt3, pt4 = st.tabs([
            "📊 Métriques globales",
            "🚚 Performance camions",
            "🏙️ Performance UC",
            "📈 Tendances"
        ])

        with pt1:
            st.markdown("### Indicateurs d'efficacité globale")
            df_eff = execute_query_with_filters(QUERY_EFFICIENCY_METRICS, (
                st.session_state['date_debut'], st.session_state['date_fin'],
                st.session_state['date_debut'], st.session_state['date_fin'],
                st.session_state['date_debut'], st.session_state['date_fin']
            ))
            if not df_eff.empty:
                c1,c2,c3 = st.columns(3)
                for _, r in df_eff.iterrows():
                    m = r['metrique']; moy = float(r['valeur_moyenne'] or 0)
                    mn = float(r['valeur_min'] or 0); mx = float(r['valeur_max'] or 0)
                    if m == 'Tonnage par heure':
                        c1.metric("⚡ Tonnage/heure", f"{moy:.1f} t/h", f"Min {mn:.1f} – Max {mx:.1f}")
                    elif m == 'Tonnage par km':
                        c2.metric("🛣️ Tonnage/km",   f"{moy:.2f} t/km", f"Min {mn:.2f} – Max {mx:.2f}")
                    elif m == 'Circuits par jour':
                        c3.metric("🔄 Circuits/jour", f"{moy:.1f}",      f"Min {mn:.0f} – Max {mx:.0f}")
            else:
                st.info("Aucune donnée d'efficacité pour la période.")

            df_circ2 = execute_query(QUERY_CIRCUITS_DETAILS, (st.session_state['date_debut'],))
            if not df_circ2.empty:
                c1,c2 = st.columns(2)
                with c1:
                    fig = px.histogram(df_circ2[df_circ2['duree_collecte']>0], x='duree_collecte',
                                       title="Distribution durées", nbins=20,
                                       color_discrete_sequence=['#3b82f6'])
                    fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)',
                                      plot_bgcolor='rgba(0,0,0,0)', font_family="DM Sans")
                    st.plotly_chart(fig, use_container_width=True)
                with c2:
                    fig = px.histogram(df_circ2[df_circ2['poids_circuit']>0], x='poids_circuit',
                                       title="Distribution tonnages", nbins=20,
                                       color_discrete_sequence=['#22c55e'])
                    fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)',
                                      plot_bgcolor='rgba(0,0,0,0)', font_family="DM Sans")
                    st.plotly_chart(fig, use_container_width=True)

        with pt2:
            st.markdown("### Performance par camion")
            df_trucks = execute_query_with_filters(QUERY_PERFORMANCE_BY_TRUCK_SIMPLE, (
                st.session_state['date_debut'], st.session_state['date_fin']))
            if not df_trucks.empty:
                st.dataframe(df_trucks, use_container_width=True,
                    column_config={
                        "camion": "Camion",
                        "nombre_circuits": "Circuits",
                        "tonnage_total": st.column_config.NumberColumn("Tonnage (kg)", format="%.0f"),
                        "tonnage_moyen_par_circuit": st.column_config.NumberColumn("Moy/circuit (kg)", format="%.1f"),
                        "duree_totale_heures": st.column_config.NumberColumn("Durée totale (h)", format="%.1f"),
                        "duree_moyenne_par_circuit": st.column_config.NumberColumn("Durée moy (h)", format="%.1f"),
                        "tonnage_par_heure": st.column_config.NumberColumn("Tonnage/h (kg)", format="%.1f"),
                        "circuits_termines": "Terminés",
                        "circuits_non_termines": "Non terminés"
                    })
                c1,c2 = st.columns(2)
                with c1:
                    fig = px.bar(df_trucks.head(10), x='camion', y='tonnage_total',
                                 title="Tonnage total (Top 10)", color_discrete_sequence=['#3b82f6'])
                    fig.update_layout(height=380, paper_bgcolor='rgba(0,0,0,0)',
                                      plot_bgcolor='rgba(0,0,0,0)', font_family="DM Sans")
                    st.plotly_chart(fig, use_container_width=True)
                with c2:
                    fig = px.bar(df_trucks.head(10), x='camion', y='tonnage_par_heure',
                                 title="Efficacité (Top 10)", color_discrete_sequence=['#14b8a6'])
                    fig.update_layout(height=380, paper_bgcolor='rgba(0,0,0,0)',
                                      plot_bgcolor='rgba(0,0,0,0)', font_family="DM Sans")
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Aucune donnée camion pour la période.")

        with pt3:
            st.markdown("### Performance par unité communale")
            df_uc_p = execute_query_with_filters(QUERY_PERFORMANCE_BY_UC, (
                st.session_state['date_debut'], st.session_state['date_fin']))
            if not df_uc_p.empty:
                df_uc_p['tonnage_par_agent'] = df_uc_p.apply(
                    lambda r: r['tonnage_total']/r['effectif_total'] if r['effectif_total']>0 else 0, axis=1)
                st.dataframe(df_uc_p, use_container_width=True)
                c1,c2 = st.columns(2)
                with c1:
                    fig = px.bar(df_uc_p.head(10), x='unite_communale', y='tonnage_total',
                                 title="Tonnage total par UC", color_discrete_sequence=['#3b82f6'])
                    fig.update_xaxes(tickangle=45)
                    fig.update_layout(height=380, paper_bgcolor='rgba(0,0,0,0)',
                                      plot_bgcolor='rgba(0,0,0,0)', font_family="DM Sans")
                    st.plotly_chart(fig, use_container_width=True)
                with c2:
                    fig = px.bar(df_uc_p.head(10), x='unite_communale', y='tonnage_par_agent',
                                 title="Tonnage/agent par UC", color_discrete_sequence=['#22c55e'])
                    fig.update_xaxes(tickangle=45)
                    fig.update_layout(height=380, paper_bgcolor='rgba(0,0,0,0)',
                                      plot_bgcolor='rgba(0,0,0,0)', font_family="DM Sans")
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Aucune donnée UC pour la période.")

        with pt4:
            st.markdown("### Évolution des performances")
            df_trends = execute_query_with_filters(QUERY_PERFORMANCE_TRENDS, (
                st.session_state['date_debut'], st.session_state['date_fin']))
            if not df_trends.empty:
                df_trends['semaine'] = pd.to_datetime(df_trends['semaine'])
                c1,c2 = st.columns(2)
                with c1:
                    fig = px.line(df_trends, x='semaine', y='tonnage_total',
                                  title="Tonnage total/semaine", markers=True,
                                  color_discrete_sequence=['#3b82f6'])
                    fig.update_layout(height=380, paper_bgcolor='rgba(0,0,0,0)',
                                      plot_bgcolor='rgba(0,0,0,0)', font_family="DM Sans")
                    st.plotly_chart(fig, use_container_width=True)
                with c2:
                    fig = px.line(df_trends, x='semaine', y='tonnage_par_km',
                                  title="Efficacité t/km par semaine", markers=True,
                                  color_discrete_sequence=['#14b8a6'])
                    fig.update_layout(height=380, paper_bgcolor='rgba(0,0,0,0)',
                                      plot_bgcolor='rgba(0,0,0,0)', font_family="DM Sans")
                    st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df_trends, use_container_width=True)
            else:
                st.info("Aucune donnée de tendance.")

    # ═══════════════════════════════════════════════════════
    # TAB 5 : ALERTES  (identique à l'original)
    # ═══════════════════════════════════════════════════════
    with tab5:
        section_header("⚠️", "Alertes et Recommandations",
                        "Système d'alertes automatiques basé sur les anomalies détectées")

        col1, col2 = st.columns(2)
        with col1:
            alert_dd = st.date_input("Date début", value=st.session_state['date_debut'], key="al_dd")
        with col2:
            alert_df = st.date_input("Date fin",   value=st.session_state['date_fin'],   key="al_df")

        at1, at2, at3, at4 = st.tabs([
            "🚫 Circuits non terminés",
            "⚠️ Tonnage nul",
            "⏱️ Durée anormale",
            "👥 Absences excessives"
        ])

        with at1:
            st.markdown("### Circuits non terminés")
            data = get_circuits_non_termines(alert_dd, alert_df)
            if data:
                st.warning(f"⚠️ {len(data)} circuit(s) non terminé(s)")
                c1,c2,c3 = st.columns(3)
                c1.metric("Circuits", len(data))
                c2.metric("Tonnage concerné", f"{sum(c.get('poids_circuit',0) or 0 for c in data):.1f} t")
                c3.metric("Durée totale", f"{sum(c.get('duree_collecte',0) or 0 for c in data):.1f}h")
                df_ = pd.DataFrame(data)
                df_['date_rapport'] = pd.to_datetime(df_['date_rapport']).dt.strftime('%Y-%m-%d')
                st.dataframe(df_[['date_rapport','unite_communale','nom_circuit','camion',
                                  'poids_circuit','duree_collecte','status']],
                             use_container_width=True, hide_index=True)
                st.info("💡 Vérifier les camions concernés, investiguer les causes, reprogrammer les circuits.")
            else:
                st.success("✅ Aucun circuit non terminé — Excellent!")

        with at2:
            st.markdown("### Tonnage nul ou insuffisant")
            data = get_tonnage_nul(alert_dd, alert_df)
            if data:
                st.error(f"❌ {len(data)} rapport(s) avec tonnage nul")
                c1,c2 = st.columns(2)
                c1.metric("Rapports affectés", len(data))
                c2.metric("Circuits sans collecte", sum(r.get('circuits_collectes',0) or 0 for r in data))
                df_ = pd.DataFrame(data)
                df_['date_rapport'] = pd.to_datetime(df_['date_rapport']).dt.strftime('%Y-%m-%d')
                st.dataframe(df_[['date_rapport','unite_communale','circuits_collectes',
                                  'tonnage_total','nombre_circuits']],
                             use_container_width=True, hide_index=True)
                st.warning("💡 Vérifier la saisie des données et contacter les UC concernées.")
            else:
                st.success("✅ Tous les rapports ont du tonnage!")

        with at3:
            st.markdown("### Durée anormale")
            max_dur = st.slider("Durée maximale normale (h)", 4.0, 12.0, 8.0, 0.5)
            data = get_duree_anormale(alert_dd, alert_df, max_duree=max_dur)
            if data:
                st.warning(f"⚠️ {len(data)} circuit(s) avec durée excessive")
                df_ = pd.DataFrame(data)
                c1,c2 = st.columns(2)
                c1.metric("Critiques (>12h)", len(df_[df_['severite']=='Critique']))
                c2.metric("Alertes (>8h)",    len(df_[df_['severite']=='Alerte']))
                df_['date_rapport'] = pd.to_datetime(df_['date_rapport']).dt.strftime('%Y-%m-%d')
                st.dataframe(df_[['date_rapport','unite_communale','nom_circuit','camion',
                                  'poids_circuit','duree_collecte','severite']].sort_values(
                                  'duree_collecte', ascending=False),
                             use_container_width=True, hide_index=True)
                st.info("💡 Vérifier l'état mécanique et revoir la planification.")
            else:
                st.success("✅ Toutes les durées sont normales!")

        with at4:
            st.markdown("### Absences excessives (> 20%)")
            data = get_absences_excessives(alert_dd, alert_df)
            if data:
                st.error(f"❌ {len(data)} incident(s) d'absence excessive")
                df_ = pd.DataFrame(data)
                c1,c2,c3 = st.columns(3)
                c1.metric("Alertes Matin",      len(df_[df_['shift']=='Matin']))
                c2.metric("Alertes Après-midi", len(df_[df_['shift']=='Après-midi']))
                c3.metric("Alertes Nuit",        len(df_[df_['shift']=='Nuit']))
                df_['date_rapport'] = pd.to_datetime(df_['date_rapport']).dt.strftime('%Y-%m-%d')
                df_show = df_[['date_rapport','unite_communale','shift','effectif_total',
                               'absents','malades','conges','taux_absence_pct']].copy()
                df_show['taux_absence_pct'] = df_show['taux_absence_pct'].apply(lambda x: f"{x:.1f}%")
                st.dataframe(df_show, use_container_width=True, hide_index=True)
                st.warning("💡 Vérifier les causes, mettre en place des renforts si nécessaire.")
            else:
                st.success("✅ Taux d'absences normal pour tous les shifts!")

    # ═══════════════════════════════════════════════════════
    # TAB 6 : RAPPORTS  (identique à l'original)
    # ═══════════════════════════════════════════════════════
    with tab6:
        section_header("📊", "Rapports et Exports",
                        "Génération de rapports officiels et exports de données")

        rt1, rt2, rt3, rt4 = st.tabs([
            "📄 Rapport période",
            "📊 Export Excel",
            "📅 Historique mensuel",
            "🔄 Comparaisons"
        ])

        # ── Rapport période ──
        with rt1:
            st.markdown("### Rapport journalier / hebdomadaire / mensuel")
            rtype = st.radio("Type", ["Journalier","Hebdomadaire","Mensuel"], horizontal=True)

            if rtype == "Journalier":
                sel_date = st.date_input("Date", value=st.session_state['date_fin'],
                                         max_value=datetime.now(), key="rp_date")
                start_d = end_d = sel_date
            elif rtype == "Hebdomadaire":
                wdate = st.date_input("Une date de la semaine", value=datetime.now().date(),
                                      max_value=datetime.now().date(), key="rp_sem")
                start_d = wdate - timedelta(days=wdate.weekday())
                end_d   = start_d + timedelta(days=6)
                st.caption(f"Semaine : {start_d:%d/%m/%Y} → {end_d:%d/%m/%Y}")
            else:
                import calendar as cal
                cy, cm = st.columns(2)
                with cy: yr = st.selectbox("Année", list(range(2020, datetime.now().year+1)),
                                            index=list(range(2020, datetime.now().year+1)).index(datetime.now().year))
                with cm: mo = st.selectbox("Mois", list(range(1,13)),
                                            index=datetime.now().month-1,
                                            format_func=lambda m: datetime(2000,m,1).strftime('%B'))
                start_d = datetime(yr, mo, 1).date()
                end_d   = datetime(yr, mo, cal.monthrange(yr, mo)[1]).date()
                st.caption(f"{start_d:%B %Y} : {start_d:%d/%m/%Y} → {end_d:%d/%m/%Y}")

            if st.button("🔍 Générer", type="primary"):
                df_p = execute_query(QUERY_DAILY_SUMMARY, (start_d, end_d))
                if df_p.empty:
                    st.warning(f"Aucune donnée du {start_d} au {end_d}.")
                else:
                    st.success(f"✅ Rapport {rtype} ({start_d} – {end_d})")
                    c1,c2,c3,c4 = st.columns(4)
                    c1.metric("Rapports",          len(df_p))
                    c2.metric("Tonnage total",      f"{df_p['tonnage_total'].sum():,.1f} t")
                    c3.metric("Circuits collectés", int(df_p['circuits_collectes'].sum()))
                    cp = int(df_p['circuits_planifies'].sum() if 'circuits_planifies' in df_p.columns else 0)
                    cc = int(df_p['circuits_collectes'].sum())
                    c4.metric("Taux réalisation",  f"{int(cc/cp*100 if cp else 0)}%")
                    st.dataframe(df_p, use_container_width=True, hide_index=True)
                    pdf_data = generate_period_report_pdf(rtype, start_d, end_d, df_p)
                    st.download_button(f"📄 PDF {rtype}", pdf_data,
                        f"rapport_{rtype.lower()}_{start_d}_{end_d}.pdf", "application/pdf")
                    st.download_button("📥 CSV", df_p.to_csv(index=False).encode('utf-8'),
                        f"rapport_{rtype.lower()}_{start_d}_{end_d}.csv", "text/csv")

        # ── Export Excel ──
        with rt2:
            st.markdown("### Export Excel personnalisé")
            ex_synth  = st.checkbox("Synthèse rapports journaliers", value=True)
            ex_circ   = st.checkbox("Détails circuits",              value=True)
            ex_pers   = st.checkbox("Données personnel",             value=False)
            ex_conces = st.checkbox("Performance concessionnaires",  value=False)

            if st.button("📥 Générer l'export", type="primary"):
                buf = BytesIO()
                with pd.ExcelWriter(buf, engine='openpyxl') as writer:
                    if ex_synth:
                        df_ = execute_query(QUERY_DAILY_SUMMARY,
                                            (st.session_state['date_debut'], st.session_state['date_fin']))
                        if not df_.empty: df_.to_excel(writer, sheet_name='Synthèse', index=False)
                    if ex_circ:
                        df_ = execute_query(QUERY_CIRCUITS_DETAILS, (st.session_state['date_debut'],))
                        if not df_.empty: df_.to_excel(writer, sheet_name='Circuits', index=False)
                    if ex_conces:
                        from utils.queries import QUERY_CONCESSIONNAIRES_PERFORMANCE
                        df_ = execute_query(QUERY_CONCESSIONNAIRES_PERFORMANCE,
                                            (st.session_state['date_debut'],))
                        if not df_.empty: df_.to_excel(writer, sheet_name='Concessionnaires', index=False)
                buf.seek(0)
                st.success("✅ Export prêt!")
                st.download_button("📥 Télécharger Excel", buf,
                    f"export_sonaged_{st.session_state['date_debut']}_{st.session_state['date_fin']}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        # ── Historique mensuel ──
        with rt3:
            st.markdown("### Historique mensuel")
            import calendar as cal
            c1,c2 = st.columns(2)
            with c1: yr = st.selectbox("Année", list(range(2020,2027)), index=6, key="hm_yr")
            with c2: mo = st.selectbox("Mois",  list(range(1,13)),
                                        index=datetime.now().month-1, key="hm_mo",
                                        format_func=lambda m: datetime(2000,m,1).strftime('%B'))
            start_d = datetime(yr, mo, 1).date()
            end_d   = datetime(yr, mo, cal.monthrange(yr, mo)[1]).date()
            df_m = execute_query(QUERY_DAILY_SUMMARY, (start_d, end_d))

            if not df_m.empty:
                st.success(f"✅ {cal.month_name[mo]} {yr}")
                c1,c2,c3,c4 = st.columns(4)
                c1.metric("Rapports",    len(df_m))
                c2.metric("Tonnage",     f"{float(df_m['tonnage_total'].sum()):.1f} t")
                c3.metric("Circuits",    int(df_m['circuits_collectes'].sum()))
                c4.metric("KM balayés", f"{float(df_m['km_balayes'].sum() if 'km_balayes' in df_m.columns else 0):.1f} km")

                c1,c2 = st.columns(2)
                with c1:
                    fig = px.line(df_m, x='date_rapport', y='tonnage_total',
                                  title='Tonnage quotidien', markers=True,
                                  color_discrete_sequence=['#3b82f6'])
                    fig.update_layout(height=350, paper_bgcolor='rgba(0,0,0,0)',
                                      plot_bgcolor='rgba(0,0,0,0)', font_family="DM Sans")
                    st.plotly_chart(fig, use_container_width=True)
                with c2:
                    fig = px.bar(df_m, x='date_rapport', y='circuits_collectes',
                                 title='Circuits par jour',
                                 color_discrete_sequence=['#22c55e'])
                    fig.update_layout(height=350, paper_bgcolor='rgba(0,0,0,0)',
                                      plot_bgcolor='rgba(0,0,0,0)', font_family="DM Sans")
                    st.plotly_chart(fig, use_container_width=True)

                st.dataframe(df_m, use_container_width=True, hide_index=True)
                c1,c2 = st.columns(2)
                with c1:
                    st.download_button("📥 CSV",
                        df_m.to_csv(index=False).encode('utf-8'),
                        f"historique_{yr}_{mo:02d}.csv", "text/csv")
                with c2:
                    pdf_data = generate_monthly_report_pdf(yr, mo, df_m, cal.month_name[mo])
                    st.download_button("📄 PDF",
                        pdf_data, f"rapport_mensuel_{yr}_{mo:02d}.pdf", "application/pdf")
            else:
                st.warning(f"Aucune donnée pour {cal.month_name[mo]} {yr}.")

        # ── Comparaisons ──
        with rt4:
            st.markdown("### Comparaison de deux périodes")
            c1,c2 = st.columns(2)
            with c1:
                st.markdown("**Période 1**")
                p1_d = st.date_input("Début", value=datetime.now()-timedelta(days=30), key="p1d")
                p1_f = st.date_input("Fin",   value=datetime.now()-timedelta(days=15), key="p1f")
            with c2:
                st.markdown("**Période 2**")
                p2_d = st.date_input("Début", value=datetime.now()-timedelta(days=14), key="p2d")
                p2_f = st.date_input("Fin",   value=datetime.now(),                    key="p2f")

            if st.button("🔍 Comparer", type="primary"):
                df1 = execute_query_with_filters(QUERY_DAILY_SUMMARY, (p1_d, p1_f))
                df2 = execute_query_with_filters(QUERY_DAILY_SUMMARY, (p2_d, p2_f))

                if not df1.empty and not df2.empty:
                    t1 = float(df1['tonnage_total'].sum()); t2 = float(df2['tonnage_total'].sum())
                    c1 = int(df1['circuits_collectes'].sum()); c2v = int(df2['circuits_collectes'].sum())
                    k1 = float(df1['km_balayes'].sum() if 'km_balayes' in df1.columns else 0)
                    k2 = float(df2['km_balayes'].sum() if 'km_balayes' in df2.columns else 0)

                    pct_t = (t2-t1)/t1*100 if t1 else 0
                    pct_c = (c2v-c1)/c1*100 if c1 else 0
                    pct_k = (k2-k1)/k1*100 if k1 else 0

                    ca,cb,cc = st.columns(3)
                    ca.metric("Tonnage",  f"{t2:.1f} t",  f"{pct_t:+.1f}%")
                    cb.metric("Circuits", c2v,             f"{pct_c:+.1f}%")
                    cc.metric("KM",       f"{k2:.1f} km", f"{pct_k:+.1f}%")

                    df_cmp = pd.DataFrame({
                        'Indicateur': ['Tonnage (t)', 'Circuits', 'KM balayés'],
                        'Période 1':  [t1, c1, k1],
                        'Période 2':  [t2, c2v, k2]
                    })
                    fig = px.bar(df_cmp, x='Indicateur', y=['Période 1','Période 2'],
                                 barmode='group', title='Comparaison',
                                 color_discrete_sequence=['#94a3b8','#3b82f6'])
                    fig.update_layout(height=380, paper_bgcolor='rgba(0,0,0,0)',
                                      plot_bgcolor='rgba(0,0,0,0)', font_family="DM Sans")
                    st.plotly_chart(fig, use_container_width=True)

                    if pct_t > 5:   st.success(f"✅ Tonnage en hausse de {pct_t:.1f}%")
                    elif pct_t < -5: st.warning(f"⚠️ Tonnage en baisse de {abs(pct_t):.1f}%")
                    else:            st.info(f"Tonnage stable ({pct_t:+.1f}%)")
                else:
                    st.error("Données insuffisantes pour l'une des périodes.")


if __name__ == "__main__":
    main()