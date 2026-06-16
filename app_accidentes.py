import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.express as px
import plotly.graph_objects as go
import base64, os
from datetime import datetime

# ─── CONFIGURACIÓN ────────────────────────────────────────────
st.set_page_config(
    page_title="Seguridad Vial · Sabana Occidente",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── TOKENS DE DISEÑO (Inspirados en shadcn/ui) ─────────────
BG_BASE  = "#0B1120"
BG_CARD  = "#111827"
BG_CARD2 = "#1a2236"
BORDER   = "rgba(255,255,255,0.08)"
ACCENT   = "#3B82F6"
ACCENT2  = "#6366F1"
SUCCESS  = "#10B981"
WARNING  = "#F59E0B"
DANGER   = "#EF4444"
TEXT_PRI = "#F8FAFC"
TEXT_SEC = "#94A3B8"
TEXT_MUT = "#475569"

# ─── CSS PREMIUM (Estilo shadcn/ui) ──────────────────────────
st.markdown(f"""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*, *::before, *::after {{ box-sizing: border-box; }}
html, body, .stApp, [data-testid="stAppViewContainer"] {{
    background-color: {BG_BASE} !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: {TEXT_PRI};
}}
[data-testid="stSidebar"] {{
    background: rgba(17, 24, 39, 0.95) !important;
    backdrop-filter: blur(12px) !important;
    border-right: 1px solid {BORDER} !important;
}}
[data-testid="stSidebar"] * {{ color: {TEXT_PRI} !important; }}
[data-testid="stSidebarNav"] {{ display: none; }}
[data-testid="stToolbar"], header {{ visibility: hidden; }}
#MainMenu {{ visibility: hidden; }}
footer {{ display: none !important; }}
::-webkit-scrollbar {{ width: 4px; }}
::-webkit-scrollbar-track {{ background: {BG_BASE}; }}
::-webkit-scrollbar-thumb {{ background: {BORDER}; border-radius: 2px; }}

/* Inputs estilo shadcn */
[data-baseweb="select"] > div {{
    background: rgba(30, 41, 59, 0.5) !important;
    border: 1px solid {BORDER} !important;
    border-radius: 8px !important;
    color: {TEXT_PRI} !important;
    backdrop-filter: blur(4px) !important;
}}
.stSelectbox label, .stSlider label {{
    color: {TEXT_SEC} !important;
    font-size: 11px !important;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}}
.stSlider [data-baseweb="slider"] {{
    background: {BORDER} !important;
}}

/* Botón shadcn */
.stButton > button {{
    background: linear-gradient(135deg, {ACCENT}, {ACCENT2}) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    padding: 0.5rem 1.25rem !important;
    width: 100% !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    font-family: 'Inter', sans-serif !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
}}
.stButton > button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(59,130,246,0.3) !important;
}}

/* Expander */
[data-testid="stExpander"] {{
    background: {BG_CARD} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 12px !important;
}}
hr {{ border-color: {BORDER} !important; }}

/* ── KPI Cards shadcn ── */
.kpi-card {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 20px 24px;
    position: relative;
    overflow: hidden;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    height: 120px;
    backdrop-filter: blur(8px);
}}
.kpi-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.2);
    border-color: rgba(59,130,246,0.2);
}}
.kpi-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, {ACCENT}, {ACCENT2}, transparent);
    border-radius: 12px 12px 0 0;
}}
.kpi-label {{
    font-size: 10px;
    font-weight: 600;
    color: {TEXT_MUT};
    text-transform: uppercase;
    letter-spacing: .08em;
    margin-bottom: 6px;
}}
.kpi-value {{
    font-size: 1.8rem;
    font-weight: 700;
    color: {TEXT_PRI};
    line-height: 1;
    margin-bottom: 4px;
}}
.kpi-sub {{ font-size: 11px; color: {TEXT_SEC}; }}
.kpi-icon {{
    position: absolute;
    top: 16px; right: 16px;
    font-size: 22px; opacity: 0.15;
}}

/* ── Section title ── */
.sec-title {{
    font-size: 0.95rem;
    font-weight: 600;
    color: {TEXT_PRI};
    margin-bottom: 2px;
}}
.sec-sub {{
    font-size: .75rem;
    color: {TEXT_SEC};
    margin-bottom: 12px;
}}

/* ── Hero banner shadcn ── */
.hero-banner {{
    border-radius: 16px;
    overflow: hidden;
    position: relative;
    margin-bottom: 28px;
    border: 1px solid {BORDER};
}}
.hero-overlay {{
    position: absolute; inset: 0;
    background: linear-gradient(90deg,
        rgba(11,17,32,0.95) 0%,
        rgba(11,17,32,0.7) 50%,
        rgba(11,17,32,0.2) 100%);
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 40px 48px;
}}
.hero-badge {{
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(59,130,246,0.12);
    border: 1px solid rgba(59,130,246,0.2);
    border-radius: 100px;
    padding: 4px 14px;
    font-size: 11px; font-weight: 600;
    color: {ACCENT};
    margin-bottom: 14px;
    width: fit-content;
}}
.hero-title {{
    font-size: 2.2rem;
    font-weight: 800;
    color: {TEXT_PRI};
    line-height: 1.1;
    margin-bottom: 8px;
}}
.hero-sub {{
    font-size: 0.95rem;
    color: {TEXT_SEC};
    max-width: 500px;
}}

/* ── Chart card shadcn ── */
.chart-card {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
}}

/* ── Nav items ── */
.nav-item {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 14px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 500;
    color: {TEXT_SEC};
    cursor: pointer;
    margin-bottom: 2px;
    transition: all 0.15s ease;
}}
.nav-item:hover {{
    background: rgba(255,255,255,0.05);
}}
.nav-item.active {{
    background: rgba(59,130,246,0.12);
    color: {ACCENT};
    border: 1px solid rgba(59,130,246,0.15);
}}
.divider-label {{
    font-size: 10px;
    font-weight: 600;
    color: {TEXT_MUT};
    text-transform: uppercase;
    letter-spacing: .1em;
    padding: 12px 14px 6px;
}}

/* ── Result Card shadcn ── */
.result-card {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 24px;
    text-align: center;
    min-height: 400px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}}
.result-percentage {{
    font-size: 3.5rem;
    font-weight: 800;
    color: {TEXT_PRI};
    line-height: 1;
}}
.result-label {{
    font-size: 0.85rem;
    font-weight: 600;
    margin-top: 8px;
    padding: 4px 16px;
    border-radius: 100px;
    display: inline-block;
}}
.result-sub {{
    font-size: 0.75rem;
    color: {TEXT_SEC};
    margin-top: 12px;
}}

/* ── Selector de navegación ── */
.nav-selector {{
    display: flex;
    gap: 4px;
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 4px;
    margin-bottom: 20px;
}}
.nav-option {{
    padding: 8px 16px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 500;
    color: {TEXT_SEC};
    cursor: pointer;
    transition: all 0.2s ease;
    flex: 1;
    text-align: center;
}}
.nav-option.active {{
    background: {ACCENT};
    color: white;
    box-shadow: 0 2px 8px rgba(59,130,246,0.3);
}}
.nav-option:hover:not(.active) {{
    background: rgba(255,255,255,0.05);
}}
</style>
""", unsafe_allow_html=True)


# ─── UTILIDADES ───────────────────────────────────────────────
def find_col(df, *keywords):
    cols_lower = {c.lower(): c for c in df.columns}
    for kw in keywords:
        kw_l = kw.lower()
        if kw_l in cols_lower:
            return cols_lower[kw_l]
        for cl, cr in cols_lower.items():
            if kw_l in cl:
                return cr
    return None

def img_to_b64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

def dark_layout(fig, title_color=ACCENT):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color=TEXT_SEC),
        title_font=dict(color=title_color, size=13, family="Inter", weight=600),
        margin=dict(l=8, r=8, t=32, b=8),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor=BORDER,
            font=dict(color=TEXT_SEC, size=11)
        ),
        xaxis=dict(
            gridcolor=BORDER,
            linecolor=BORDER,
            tickfont=dict(color=TEXT_MUT, size=10),
            title_font=dict(color=TEXT_SEC, size=11)
        ),
        yaxis=dict(
            gridcolor=BORDER,
            linecolor=BORDER,
            tickfont=dict(color=TEXT_MUT, size=10),
            title_font=dict(color=TEXT_SEC, size=11)
        ),
    )
    return fig


# ─── CARGA DE DATOS ───────────────────────────────────────────
@st.cache_data
def load_clean_data():
    try:
        df = pd.read_csv('Archivo_Accidentes.csv', sep=None, engine='python')
        df.columns = (
            df.columns.str.strip().str.lower()
            .str.replace(r'[\s\-]+', '_', regex=True)
            .str.replace(r'[áàä]', 'a', regex=True)
            .str.replace(r'[éèë]', 'e', regex=True)
            .str.replace(r'[íìï]', 'i', regex=True)
            .str.replace(r'[óòö]', 'o', regex=True)
            .str.replace(r'[úùü]', 'u', regex=True)
            .str.replace(r'[ñ]', 'n', regex=True)
        )
        return df
    except Exception as e:
        st.error(f"⚠️ Error al cargar datos: {e}")
        return None

@st.cache_resource
def load_trained_model():
    try:
        return joblib.load('modelo_accidentes.pkl')
    except:
        return None

df_full = load_clean_data()
modelo  = load_trained_model()

if df_full is None:
    st.error("🚨 No se encontró 'Archivo_Accidentes.csv'.")
    st.stop()

# Detectar columnas
COL_EDAD   = find_col(df_full, 'edad', 'age')
COL_MUN    = find_col(df_full, 'municipio', 'ciudad', 'municipality')
COL_ZONA   = find_col(df_full, 'zona', 'zone', 'area')
COL_GENERO = find_col(df_full, 'genero', 'sexo', 'gender', 'sex')
COL_ACTOR  = find_col(df_full, 'actor_vial', 'actor', 'tipo_actor', 'clase_actor', 'victima', 'rol')
COL_GRAVE  = find_col(df_full, 'gravedad', 'severity', 'clase', 'tipo_accidente', 'clase_de_acc')
COL_FECHA  = find_col(df_full, 'fecha', 'date', 'año', 'anio', 'year', 'mes')

# ─── SIDEBAR ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding:16px 12px 16px;">
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:4px;">
            <div style="width:34px;height:34px;border-radius:8px;
                        background:linear-gradient(135deg,{ACCENT},{ACCENT2});
                        display:flex;align-items:center;justify-content:center;font-size:16px;">
                🚦
            </div>
            <div>
                <div style="font-weight:700;font-size:14px;color:{TEXT_PRI};">VialAnalytics</div>
                <div style="font-size:10px;color:{TEXT_MUT};">Sabana Occidente</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Selector de navegación estilo tabs
    pagina = st.radio(
        "Navegación",
        ["🏠 Inicio", "📊 Análisis"],
        label_visibility="collapsed"
    )

    st.markdown(f'<div class="divider-label">Filtros</div>', unsafe_allow_html=True)

    # Filtro municipio
    df = df_full.copy()
    if COL_MUN:
        opts_mun = ["Todos"] + sorted(df[COL_MUN].dropna().unique().tolist())
        sel_mun  = st.selectbox("Municipio", opts_mun)
        if sel_mun != "Todos":
            df = df[df[COL_MUN] == sel_mun]

    # Filtro género
    if COL_GENERO:
        opts_gen = ["Todos"] + sorted(df[COL_GENERO].dropna().unique().tolist())
        sel_gen  = st.selectbox("Género", opts_gen)
        if sel_gen != "Todos":
            df = df[df[COL_GENERO] == sel_gen]

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Contador de registros
    st.markdown(f"""
    <div style="background:rgba(30,41,59,0.5);border:1px solid {BORDER};
                border-radius:10px;padding:12px 16px;margin:0 4px;
                backdrop-filter:blur(4px);">
        <div style="font-size:9px;color:{TEXT_MUT};text-transform:uppercase;
                    letter-spacing:.08em;margin-bottom:2px;">Registros filtrados</div>
        <div style="font-size:20px;font-weight:700;color:{ACCENT};">{len(df):,}</div>
        <div style="font-size:10px;color:{TEXT_MUT};">de {len(df_full):,} totales</div>
    </div>
    """, unsafe_allow_html=True)

    # Diagnóstico opcional
    cols_faltantes = {k: v for k, v in {
        'Edad': COL_EDAD, 'Municipio': COL_MUN, 'Zona': COL_ZONA,
        'Género': COL_GENERO, 'Actor Vial': COL_ACTOR
    }.items() if v is None}
    if cols_faltantes:
        with st.expander("⚠️ Diagnóstico"):
            st.warning(f"No detectadas: {', '.join(cols_faltantes.keys())}")
            st.code(str(list(df_full.columns)))


# ═══════════════════════════════════════════════════════════════
#  CALCULAR KPIs
# ═══════════════════════════════════════════════════════════════
kpi_incidentes = f"{len(df):,}"
kpi_edad  = f"{df[COL_EDAD].mean():.1f}"  if (COL_EDAD and not df.empty and not pd.isna(df[COL_EDAD].mean())) else "N/D"
kpi_mun   = df[COL_MUN].mode()[0]               if (COL_MUN and not df.empty and not df[COL_MUN].mode().empty) else "N/D"
kpi_actor = df[COL_ACTOR].mode()[0]             if (COL_ACTOR and not df.empty and not df[COL_ACTOR].mode().empty) else "N/D"


# ════════════════════════════════════════════════════════════════
#  PÁGINA 1 — INICIO
# ════════════════════════════════════════════════════════════════
if "Inicio" in pagina:

    # ── HERO BANNER ──────────────────────────────────────────
    img_path = "imagen_principal.jpeg"
    if os.path.exists(img_path):
        b64 = img_to_b64(img_path)
        if b64:
            st.markdown(f"""
            <div class="hero-banner">
                <img src="data:image/jpeg;base64,{b64}"
                     style="width:100%; height:280px; object-fit:cover; object-position:center; display:block;">
                <div class="hero-overlay">
                    <div class="hero-badge">🚦 Proyecto SENA · 2026</div>
                    <div class="hero-title">Seguridad Vial<br>Sabana Occidente</div>
                    <div class="hero-sub">
                        Análisis de accidentalidad &nbsp;·&nbsp;
                        Facatativá &nbsp;•&nbsp; Funza &nbsp;•&nbsp; Madrid &nbsp;•&nbsp; Mosquera
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,{BG_CARD},{BG_CARD2});
                        border:1px solid {BORDER}; border-radius:16px;
                        padding:40px; margin-bottom:24px; text-align:center;">
                <div style="font-size:2.8rem; margin-bottom:10px;">🚦</div>
                <div style="font-size:1.8rem; font-weight:800; color:{TEXT_PRI};">
                    Seguridad Vial · Sabana Occidente
                </div>
                <div style="color:{TEXT_SEC}; margin-top:6px; font-size:0.9rem;">
                    Análisis de accidentalidad · Facatativá • Funza • Madrid • Mosquera
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── KPIs ──────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">📊</div>
            <div class="kpi-label">Incidentes filtrados</div>
            <div class="kpi-value">{kpi_incidentes}</div>
            <div class="kpi-sub">{sel_mun if sel_mun != 'Todos' else 'Todos'} · {sel_gen if sel_gen != 'Todos' else 'Todos'}</div>
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">📈</div>
            <div class="kpi-label">Edad media crítica</div>
            <div class="kpi-value">{kpi_edad}</div>
            <div class="kpi-sub">Promedio de involucrados</div>
        </div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">📍</div>
            <div class="kpi-label">Mayor siniestralidad</div>
            <div class="kpi-value" style="font-size:1.4rem;">{kpi_mun}</div>
            <div class="kpi-sub">Municipio de mayor riesgo</div>
        </div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">🚶</div>
            <div class="kpi-label">Actor más vulnerable</div>
            <div class="kpi-value" style="font-size:1.2rem;">{kpi_actor}</div>
            <div class="kpi-sub">Tipo de actor vial</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── PREDICTOR DE RIESGO ──────────────────────────────────
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;">
        <div style="width:3px;height:24px;background:linear-gradient(180deg,{ACCENT},{ACCENT2});border-radius:2px;"></div>
        <div>
            <div style="font-size:1rem;font-weight:700;color:{TEXT_PRI};">Predictor de Escenario de Riesgo</div>
            <div style="font-size:.75rem;color:{TEXT_SEC};">Configura los parámetros del actor vial para obtener una predicción</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    p1, p2 = st.columns([1, 1.1])

    with p1:
        st.markdown(f"""
        <div style="background:{BG_CARD};border:1px solid {BORDER};border-radius:12px;padding:20px;">
            <div style="font-size:10px;font-weight:600;color:{TEXT_MUT};text-transform:uppercase;letter-spacing:.08em;margin-bottom:16px;">
                ⚙️ Parámetros del escenario
            </div>
        """, unsafe_allow_html=True)

        edad = st.slider("Edad del actor vial", 0, 100, 30)
        mun_sel  = st.selectbox("Municipio", sorted(df_full[COL_MUN].dropna().unique()))   if COL_MUN    else None
        zon_sel  = st.selectbox("Zona del incidente", sorted(df_full[COL_ZONA].dropna().unique()))  if COL_ZONA   else None
        gen_sel  = st.selectbox("Género", sorted(df_full[COL_GENERO].dropna().unique()))   if COL_GENERO else None
        act_sel  = st.selectbox("Tipo de actor vial", sorted(df_full[COL_ACTOR].dropna().unique())) if COL_ACTOR  else None

        st.markdown("</div>", unsafe_allow_html=True)

    with p2:
        if modelo is not None:
            try:
                cols_mod = list(modelo.feature_names_in_)
                inp      = pd.DataFrame(0, index=[0], columns=cols_mod)

                # Asignar Edad
                if 'Edad' in inp.columns:
                    inp.at[0, 'Edad'] = edad
                elif 'edad' in inp.columns:
                    inp.at[0, 'edad'] = edad

                # Función de mapeo robusto
                def set_feature_val(prefix, val):
                    if not val:
                        return
                    val_norm = str(val).lower().replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u').replace('ñ', 'n')
                    prefix_norm = prefix.lower()
                    
                    for col in inp.columns:
                        col_norm = col.lower().replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u').replace('ñ', 'n')
                        if col_norm.startswith(f"{prefix_norm}_"):
                            feat_val = col_norm[len(prefix_norm)+1:]
                            feat_val_clean = ''.join(c for c in feat_val if c.isalnum())
                            val_clean = ''.join(c for c in val_norm if c.isalnum())
                            if feat_val_clean == val_clean or val_clean in feat_val_clean or feat_val_clean in val_clean:
                                inp.at[0, col] = 1
                                return

                set_feature_val('Municipio', mun_sel)
                set_feature_val('Zona', zon_sel)
                set_feature_val('Genero', gen_sel)

                # Mapear Actor Vial a Armas_medios
                arma_val = 'No Reportado'
                if act_sel:
                    act_lower = act_sel.lower()
                    if 'moto' in act_lower:
                        arma_val = 'Moto'
                    elif 'bicicleta' in act_lower or 'ciclista' in act_lower:
                        arma_val = 'Bicicleta'
                    elif 'vehiculo' in act_lower or 'vehículo' in act_lower or 'conductor' in act_lower:
                        arma_val = 'Vehiculo'
                    elif 'peaton' in act_lower or 'peatón' in act_lower or 'peat' in act_lower:
                        arma_val = 'Sin empleo de armas'
                set_feature_val('Armas_medios', arma_val)

                # Mapear Edad a Grupo_etario
                grupo_val = 'No Reportado'
                if edad < 12:
                    grupo_val = 'Menores'
                elif edad < 18:
                    grupo_val = 'Adolescentes'
                else:
                    grupo_val = 'Adultos'
                set_feature_val('Grupo_etario', grupo_val)

                pred      = modelo.predict(inp)[0]
                probs     = modelo.predict_proba(inp)[0]
                conf      = max(probs)
                riesgo_pct = round(conf * 100, 1)
                
                # Determinar color y etiqueta
                if riesgo_pct <= 40:
                    color_riesgo = SUCCESS
                    label_riesgo = "RIESGO BAJO · CONTROLADO"
                    icon_riesgo = "🟢"
                    bg_riesgo = "rgba(16,185,129,0.08)"
                elif riesgo_pct <= 70:
                    color_riesgo = WARNING
                    label_riesgo = "RIESGO MODERADO · PRECAUCIÓN"
                    icon_riesgo = "🟡"
                    bg_riesgo = "rgba(245,158,11,0.08)"
                else:
                    color_riesgo = DANGER
                    label_riesgo = "RIESGO ALTO · CRÍTICO"
                    icon_riesgo = "🔴"
                    bg_riesgo = "rgba(239,68,68,0.08)"

                # Mostrar resultado con gauge circular
                st.markdown(f"""
                <div style="background:{BG_CARD};border:1px solid {BORDER};border-radius:12px;padding:20px;min-height:380px;display:flex;flex-direction:column;justify-content:space-between;align-items:center;">
                    <div style="width:100%;text-align:left;font-size:10px;font-weight:600;color:{TEXT_MUT};text-transform:uppercase;letter-spacing:.08em;margin-bottom:12px;">
                        🔮 Resultado del análisis
                    </div>
                    <div style="position:relative;width:140px;height:140px;display:flex;justify-content:center;align-items:center;">
                        <svg width="140" height="140" viewBox="0 0 140 140" style="transform: rotate(-90deg); position: absolute; top:0; left:0;">
                            <circle cx="70" cy="70" r="55" stroke="{BG_CARD2}" stroke-width="8" fill="transparent" />
                            <circle cx="70" cy="70" r="55" stroke="{color_riesgo}" stroke-width="8" fill="transparent"
                                    stroke-dasharray="345.58" stroke-dashoffset="{345.58 * (1 - riesgo_pct/100)}"
                                    stroke-linecap="round" />
                        </svg>
                        <div style="text-align:center;z-index:2;">
                            <div style="font-size:2.4rem;font-weight:800;color:{TEXT_PRI};line-height:1;">
                                {riesgo_pct}%
                            </div>
                            <div style="font-size:9px;color:{TEXT_SEC};margin-top:2px;font-weight:500;text-transform:uppercase;letter-spacing:0.05em;">
                                Riesgo
                            </div>
                        </div>
                    </div>
                    <div style="text-align:center;width:100%;margin-top:12px;">
                        <div style="display:flex;justify-content:center;margin-bottom:10px;">
                            <div style="background:{bg_riesgo};border:1px solid {color_riesgo}30;border-radius:100px;padding:4px 16px;display:flex;align-items:center;gap:6px;">
                                <span style="width:8px;height:8px;border-radius:50%;background-color:{color_riesgo};display:inline-block;"></span>
                                <span style="font-size:0.8rem;font-weight:700;color:{color_riesgo};letter-spacing:0.02em;">
                                    {label_riesgo}
                                </span>
                            </div>
                        </div>
                        <div style="display:flex;justify-content:center;gap:8px;flex-wrap:wrap;">
                            <div style="background:{BG_CARD2};border-radius:6px;padding:4px 10px;border:1px solid {BORDER};">
                                <div style="font-size:8px;color:{TEXT_MUT};text-transform:uppercase;font-weight:600;">Actor</div>
                                <div style="font-size:11px;font-weight:600;color:{TEXT_PRI};">{act_sel if act_sel else 'N/D'}</div>
                            </div>
                            <div style="background:{BG_CARD2};border-radius:6px;padding:4px 10px;border:1px solid {BORDER};">
                                <div style="font-size:8px;color:{TEXT_MUT};text-transform:uppercase;font-weight:600;">Municipio</div>
                                <div style="font-size:11px;font-weight:600;color:{TEXT_PRI};">{mun_sel if mun_sel else 'N/D'}</div>
                            </div>
                            <div style="background:{BG_CARD2};border-radius:6px;padding:4px 10px;border:1px solid {BORDER};">
                                <div style="font-size:8px;color:{TEXT_MUT};text-transform:uppercase;font-weight:600;">Confianza</div>
                                <div style="font-size:11px;font-weight:600;color:{TEXT_PRI};">{conf:.1%}</div>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error en predicción: {e}")
        else:
            st.markdown(f"""
            <div style="background:{BG_CARD};border:1px solid {BORDER};border-radius:12px;padding:24px;min-height:380px;text-align:center;display:flex;flex-direction:column;justify-content:center;align-items:center;">
                <div style="font-size:40px;margin-bottom:12px;">📦</div>
                <div style="color:{TEXT_SEC};font-size:13px;">
                    Modelo no disponible.<br>
                    Sube <code style="background:{BG_CARD2};padding:2px 8px;border-radius:4px;">modelo_accidentes.pkl</code>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
#  PÁGINA 2 — ANÁLISIS VISUAL
# ════════════════════════════════════════════════════════════════
else:
    # ── KPIs ──────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-icon">📊</div>
            <div class="kpi-label">Incidentes</div>
            <div class="kpi-value">{kpi_incidentes}</div>
            <div class="kpi-sub">Registros activos</div>
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-icon">📈</div>
            <div class="kpi-label">Edad media</div>
            <div class="kpi-value">{kpi_edad}</div>
            <div class="kpi-sub">Promedio involucrados</div>
        </div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-icon">📍</div>
            <div class="kpi-label">Mayor riesgo</div>
            <div class="kpi-value" style="font-size:1.3rem;">{kpi_mun}</div>
            <div class="kpi-sub">Municipio</div>
        </div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-icon">🚶</div>
            <div class="kpi-label">Actor vulnerable</div>
            <div class="kpi-value" style="font-size:1.1rem;">{kpi_actor}</div>
            <div class="kpi-sub">Tipo de actor vial</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── GRÁFICOS ──────────────────────────────────────────────
    c1, c2 = st.columns(2)

    with c1:
        st.markdown(f"""
        <div class="sec-title">🏙️ Siniestralidad por Municipio</div>
        <div class="sec-sub">Cantidad de incidentes registrados</div>
        """, unsafe_allow_html=True)
        if COL_MUN:
            vc = df[COL_MUN].value_counts().reset_index()
            vc.columns = ['Municipio', 'Incidentes']
            fig = go.Figure(go.Bar(
                x=vc['Municipio'], y=vc['Incidentes'],
                marker=dict(
                    color=vc['Incidentes'],
                    colorscale=[[0,"#1E3A5F"],[0.5,ACCENT],[1,ACCENT2]],
                    line=dict(width=0)
                ),
                hovertemplate="<b>%{x}</b><br>Incidentes: %{y:,}<extra></extra>"
            ))
            fig = dark_layout(fig)
            fig.update_layout(showlegend=False, height=300)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with c2:
        st.markdown(f"""
        <div class="sec-title">📉 Perfil de Edad</div>
        <div class="sec-sub">Distribución etaria de los actores viales</div>
        """, unsafe_allow_html=True)
        if COL_EDAD:
            ev = df[COL_EDAD].dropna()
            counts, bins = np.histogram(ev, bins=25)
            centers = (bins[:-1] + bins[1:]) / 2
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=centers, y=counts,
                marker=dict(color=ACCENT, opacity=0.7, line=dict(width=0)),
                hovertemplate="Edad %{x:.0f}: %{y} casos<extra></extra>"
            ))
            fig2.add_trace(go.Scatter(
                x=centers, y=counts,
                fill='tozeroy', fillcolor="rgba(99,102,241,0.15)",
                line=dict(color=ACCENT2, width=2), hoverinfo='skip'
            ))
            fig2 = dark_layout(fig2)
            fig2.update_layout(showlegend=False, height=300, barmode='overlay')
            st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

    # ── FILA 2 ─────────────────────────────────────────────────
    c3, c4 = st.columns(2)

    with c3:
        st.markdown(f"""
        <div class="sec-title">🚗 Actores Viales</div>
        <div class="sec-sub">Top 8 tipos de actor vial involucrado</div>
        """, unsafe_allow_html=True)
        if COL_ACTOR:
            vc_a = df[COL_ACTOR].value_counts().head(8).reset_index()
            vc_a.columns = ['Actor', 'Cantidad']
            fig3 = go.Figure(go.Bar(
                x=vc_a['Cantidad'], y=vc_a['Actor'],
                orientation='h',
                marker=dict(
                    color=vc_a['Cantidad'],
                    colorscale=[[0,"#1a2236"],[1,SUCCESS]],
                    line=dict(width=0)
                ),
                hovertemplate="<b>%{y}</b>: %{x:,} casos<extra></extra>"
            ))
            fig3 = dark_layout(fig3)
            fig3.update_layout(showlegend=False, height=300,
                               yaxis=dict(autorange='reversed'))
            st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})

    with c4:
        st.markdown(f"""
        <div class="sec-title">⚧ Distribución por Género</div>
        <div class="sec-sub">Proporción de involucrados por género</div>
        """, unsafe_allow_html=True)
        if COL_GENERO:
            vc_g = df[COL_GENERO].value_counts().reset_index()
            vc_g.columns = ['Genero', 'Cantidad']
            fig4 = go.Figure(go.Pie(
                labels=vc_g['Genero'], values=vc_g['Cantidad'],
                hole=0.55,
                marker=dict(
                    colors=[ACCENT, ACCENT2, SUCCESS, WARNING],
                    line=dict(color=BG_BASE, width=2)
                ),
                hovertemplate="<b>%{label}</b><br>%{value:,} casos (%{percent})<extra></extra>"
            ))
            fig4 = dark_layout(fig4)
            fig4.update_layout(showlegend=True, height=300)
            st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False})

    # ── FILA 3 ─────────────────────────────────────────────────
    c5, c6 = st.columns(2)

    with c5:
        if COL_ZONA:
            st.markdown(f"""
            <div class="sec-title">📍 Incidentes por Zona</div>
            <div class="sec-sub">Clasificación urbana vs rural</div>
            """, unsafe_allow_html=True)
            vc_z = df[COL_ZONA].value_counts().reset_index()
            vc_z.columns = ['Zona', 'Cantidad']
            fig5 = go.Figure(go.Bar(
                x=vc_z['Zona'], y=vc_z['Cantidad'],
                marker=dict(color=WARNING, opacity=0.8, line=dict(width=0)),
                hovertemplate="<b>%{x}</b>: %{y:,}<extra></extra>"
            ))
            fig5 = dark_layout(fig5, title_color=WARNING)
            fig5.update_layout(showlegend=False, height=280)
            st.plotly_chart(fig5, use_container_width=True, config={'displayModeBar': False})

    with c6:
        if COL_GRAVE:
            st.markdown(f"""
            <div class="sec-title">⚠️ Gravedad de Accidentes</div>
            <div class="sec-sub">Distribución por nivel de gravedad</div>
            """, unsafe_allow_html=True)
            vc_gr = df[COL_GRAVE].value_counts().reset_index()
            vc_gr.columns = ['Gravedad', 'Cantidad']
            fig6 = go.Figure(go.Bar(
                x=vc_gr['Gravedad'], y=vc_gr['Cantidad'],
                marker=dict(
                    color=vc_gr['Cantidad'],
                    colorscale=[[0, WARNING],[1, DANGER]],
                    line=dict(width=0)
                ),
                hovertemplate="<b>%{x}</b>: %{y:,}<extra></extra>"
            ))
            fig6 = dark_layout(fig6, title_color=DANGER)
            fig6.update_layout(showlegend=False, height=280)
            st.plotly_chart(fig6, use_container_width=True, config={'displayModeBar': False})

    # ── MAPA DE CALOR ──────────────────────────────────────────
    if COL_MUN and COL_ACTOR:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="sec-title">🗺️ Mapa de Calor: Municipio × Actor Vial</div>
        <div class="sec-sub">Concentración de incidentes por combinación</div>
        """, unsafe_allow_html=True)

        pivot = (df.groupby([COL_MUN, COL_ACTOR])
                   .size().reset_index(name='n')
                   .pivot(index=COL_MUN, columns=COL_ACTOR, values='n')
                   .fillna(0))

        fig7 = go.Figure(go.Heatmap(
            z=pivot.values,
            x=[str(c) for c in pivot.columns],
            y=[str(r) for r in pivot.index],
            colorscale=[[0, BG_CARD2],[0.5, ACCENT],[1, ACCENT2]],
            hovertemplate="Municipio: <b>%{y}</b><br>Actor: <b>%{x}</b><br>Casos: %{z:,}<extra></extra>",
            showscale=True,
            colorbar=dict(tickfont=dict(color=TEXT_MUT, size=10), bgcolor=BG_CARD)
        ))
        fig7 = dark_layout(fig7)
        fig7.update_layout(height=340)
        st.plotly_chart(fig7, use_container_width=True, config={'displayModeBar': False})


# ─── FOOTER ───────────────────────────────────────────────────
st.markdown(f"""
<br>
<div style="border-top:1px solid {BORDER};padding:14px 0;text-align:center;">
    <span style="color:{TEXT_MUT};font-size:11px;letter-spacing:0.02em;">
        🚦 VialAnalytics · Seguridad Vial Sabana Occidente · Proyecto SENA 2026
    </span>
</div>
""", unsafe_allow_html=True)