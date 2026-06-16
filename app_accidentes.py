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

# ─── TOKENS DE DISEÑO ─────────────────────────────────────────
BG_BASE  = "#0B1120"
BG_CARD  = "#111827"
BG_CARD2 = "#1a2236"
BORDER   = "#1E2D45"
ACCENT   = "#3B82F6"
ACCENT2  = "#6366F1"
SUCCESS  = "#10B981"
WARNING  = "#F59E0B"
DANGER   = "#EF4444"
TEXT_PRI = "#F1F5F9"
TEXT_SEC = "#94A3B8"
TEXT_MUT = "#475569"

# ─── CSS PREMIUM ──────────────────────────────────────────────
st.markdown(f"""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*, *::before, *::after {{ box-sizing: border-box; }}
html, body, .stApp, [data-testid="stAppViewContainer"] {{
    background-color: {BG_BASE} !important;
    font-family: 'Inter', sans-serif !important;
    color: {TEXT_PRI};
}}
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #0d1526 0%, #0B1120 100%) !important;
    border-right: 1px solid {BORDER} !important;
}}
[data-testid="stSidebar"] * {{ color: {TEXT_PRI} !important; }}
[data-testid="stSidebarNav"] {{ display: none; }}
[data-testid="stToolbar"], header {{ visibility: hidden; }}
#MainMenu {{ visibility: hidden; }}
footer {{ display: none !important; }}
::-webkit-scrollbar {{ width: 6px; }}
::-webkit-scrollbar-track {{ background: {BG_BASE}; }}
::-webkit-scrollbar-thumb {{ background: {BORDER}; border-radius: 3px; }}

/* Inputs */
[data-baseweb="select"] > div {{
    background: {BG_CARD2} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 10px !important;
    color: {TEXT_PRI} !important;
}}
.stSelectbox label, .stSlider label {{
    color: {TEXT_SEC} !important;
    font-size: 12px !important;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}}

/* Botón */
.stButton > button {{
    background: linear-gradient(135deg, {ACCENT}, {ACCENT2}) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.5rem !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
    font-family: 'Inter', sans-serif !important;
}}
.stButton > button:hover {{
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 20px rgba(59,130,246,0.35) !important;
}}

/* Expander */
[data-testid="stExpander"] {{
    background: {BG_CARD} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 12px !important;
}}
hr {{ border-color: {BORDER} !important; }}

/* ── KPI Cards ── */
.kpi-card {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 16px;
    padding: 22px 24px;
    position: relative;
    overflow: hidden;
    transition: transform .2s ease, box-shadow .2s ease;
    height: 130px;
}}
.kpi-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 12px 32px rgba(0,0,0,.4);
}}
.kpi-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, {ACCENT}, {ACCENT2});
    border-radius: 16px 16px 0 0;
}}
.kpi-label {{
    font-size: 10px;
    font-weight: 600;
    color: {TEXT_MUT};
    text-transform: uppercase;
    letter-spacing: .1em;
    margin-bottom: 8px;
}}
.kpi-value {{
    font-size: 1.9rem;
    font-weight: 700;
    color: {TEXT_PRI};
    line-height: 1;
    margin-bottom: 4px;
}}
.kpi-sub {{ font-size: 12px; color: {TEXT_SEC}; }}
.kpi-icon {{
    position: absolute;
    top: 18px; right: 18px;
    font-size: 26px; opacity: .2;
}}

/* ── Section title ── */
.sec-title {{
    font-size: 1rem;
    font-weight: 600;
    color: {TEXT_PRI};
    margin-bottom: 2px;
}}
.sec-sub {{
    font-size: .8rem;
    color: {TEXT_SEC};
    margin-bottom: 16px;
}}

/* ── Hero banner ── */
.hero-banner {{
    border-radius: 20px;
    overflow: hidden;
    position: relative;
    margin-bottom: 28px;
    border: 1px solid {BORDER};
}}
.hero-overlay {{
    position: absolute; inset: 0;
    background: linear-gradient(90deg,
        rgba(11,17,32,.95) 0%,
        rgba(11,17,32,.7)  50%,
        rgba(11,17,32,.2)  100%);
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 40px 48px;
}}
.hero-badge {{
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(59,130,246,.15);
    border: 1px solid rgba(59,130,246,.3);
    border-radius: 100px;
    padding: 6px 16px;
    font-size: 12px; font-weight: 600;
    color: {ACCENT};
    margin-bottom: 16px;
    width: fit-content;
}}
.hero-title {{
    font-size: 2.4rem;
    font-weight: 800;
    color: {TEXT_PRI};
    line-height: 1.15;
    margin-bottom: 10px;
}}
.hero-sub {{
    font-size: 1rem;
    color: {TEXT_SEC};
    max-width: 500px;
}}

/* ── Chart card ── */
.chart-card {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
}}

/* ── Nav items ── */
.nav-item {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 14px;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 500;
    color: {TEXT_SEC};
    cursor: pointer;
    margin-bottom: 4px;
}}
.nav-item.active {{
    background: rgba(59,130,246,.15);
    color: {ACCENT};
    border: 1px solid rgba(59,130,246,.2);
}}
.divider-label {{
    font-size: 10px;
    font-weight: 600;
    color: {TEXT_MUT};
    text-transform: uppercase;
    letter-spacing: .12em;
    padding: 14px 14px 6px;
}}

/* ── Result Card mejorada ── */
.result-card {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    min-height: 420px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}}
.result-percentage {{
    font-size: 4rem;
    font-weight: 800;
    color: {TEXT_PRI};
    line-height: 1;
}}
.result-label {{
    font-size: 0.9rem;
    font-weight: 600;
    margin-top: 8px;
    padding: 6px 16px;
    border-radius: 100px;
    display: inline-block;
}}
.result-sub {{
    font-size: 0.8rem;
    color: {TEXT_SEC};
    margin-top: 12px;
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
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def dark_layout(fig, title_color=ACCENT):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color=TEXT_SEC),
        title_font=dict(color=title_color, size=14, family="Inter"),
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=BORDER, font=dict(color=TEXT_SEC)),
        xaxis=dict(gridcolor=BORDER, linecolor=BORDER, tickfont=dict(color=TEXT_MUT)),
        yaxis=dict(gridcolor=BORDER, linecolor=BORDER, tickfont=dict(color=TEXT_MUT)),
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


# ═══════════════════════════════════════════════════════════════
#  SIDEBAR — navegación
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div style="padding:20px 14px 20px;">
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
            <div style="width:38px;height:38px;border-radius:10px;
                        background:linear-gradient(135deg,{ACCENT},{ACCENT2});
                        display:flex;align-items:center;justify-content:center;font-size:18px;">
                🚦
            </div>
            <div>
                <div style="font-weight:700;font-size:15px;color:{TEXT_PRI};">VialAnalytics</div>
                <div style="font-size:11px;color:{TEXT_MUT};">Sabana Occidente</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    pagina = st.radio(
        "Navegación",
        ["🏠  Inicio · Predictor", "📊  Análisis Visual"],
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
    st.markdown(f"""
    <div style="background:{BG_CARD2};border:1px solid {BORDER};
                border-radius:12px;padding:14px;margin:0 4px;">
        <div style="font-size:10px;color:{TEXT_MUT};text-transform:uppercase;
                    letter-spacing:.08em;margin-bottom:4px;">Registros filtrados</div>
        <div style="font-size:22px;font-weight:700;color:{ACCENT};">{len(df):,}</div>
        <div style="font-size:11px;color:{TEXT_MUT};">de {len(df_full):,} totales</div>
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
#  CALCULAR KPIs dinámicos
# ═══════════════════════════════════════════════════════════════
kpi_incidentes = f"{len(df):,}"
kpi_edad  = f"{df[COL_EDAD].mean():.1f}"  if (COL_EDAD and not df.empty and not pd.isna(df[COL_EDAD].mean())) else "N/D"
kpi_mun   = df[COL_MUN].mode()[0]               if (COL_MUN and not df.empty and not df[COL_MUN].mode().empty) else "N/D"
kpi_actor = df[COL_ACTOR].mode()[0]             if (COL_ACTOR and not df.empty and not df[COL_ACTOR].mode().empty) else "N/D"


# ════════════════════════════════════════════════════════════════
#  PÁGINA 1 — INICIO · PREDICTOR
# ════════════════════════════════════════════════════════════════
if "Inicio" in pagina:

    # ── HERO BANNER ──────────────────────────────────────────
    img_path = "imagen_principal.jpeg"
    if os.path.exists(img_path):
        b64 = img_to_b64(img_path)
        st.markdown(f"""
        <div class="hero-banner">
            <img src="data:image/jpeg;base64,{b64}"
                 style="width:100%; height:340px; object-fit:cover; object-position:center; display:block;">
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
                    border:1px solid {BORDER}; border-radius:20px;
                    padding:48px; margin-bottom:28px; text-align:center;">
            <div style="font-size:3rem; margin-bottom:12px;">🚦</div>
            <div style="font-size:2rem; font-weight:800; color:{TEXT_PRI};">
                Seguridad Vial · Sabana Occidente
            </div>
            <div style="color:{TEXT_SEC}; margin-top:8px;">
                Análisis de accidentalidad · Facatativá • Funza • Madrid • Mosquera
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── KPIs DINÁMICOS ───────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">🚨</div>
            <div class="kpi-label">Incidentes filtrados</div>
            <div class="kpi-value">{kpi_incidentes}</div>
            <div class="kpi-sub">{sel_mun if sel_mun != 'Todos' else 'Todos los municipios'} · {sel_gen if sel_gen != 'Todos' else 'Todos los géneros'}</div>
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">🎂</div>
            <div class="kpi-label">Edad media crítica</div>
            <div class="kpi-value">{kpi_edad} años</div>
            <div class="kpi-sub">Promedio de involucrados</div>
        </div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">📍</div>
            <div class="kpi-label">Mayor siniestralidad</div>
            <div class="kpi-value" style="font-size:1.5rem;">{kpi_mun}</div>
            <div class="kpi-sub">Municipio de mayor riesgo</div>
        </div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">🚶</div>
            <div class="kpi-label">Actor más vulnerable</div>
            <div class="kpi-value" style="font-size:1.35rem;">{kpi_actor}</div>
            <div class="kpi-sub">Tipo de actor vial</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── PREDICTOR DE RIESGO ──────────────────────────────────
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:20px;">
        <div style="width:4px;height:28px;background:linear-gradient(180deg,{ACCENT},{ACCENT2});border-radius:2px;"></div>
        <div>
            <div style="font-size:1.1rem;font-weight:700;color:{TEXT_PRI};">Predictor de Escenario de Riesgo</div>
            <div style="font-size:.82rem;color:{TEXT_SEC};">Configura los parámetros del actor vial para obtener una predicción de riesgo</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    p1, p2 = st.columns([1, 1.1])

    with p1:
        st.markdown(f"""
        <div style="background:{BG_CARD};border:1px solid {BORDER};
                    border-radius:16px;padding:24px;">
            <div style="font-size:12px;font-weight:600;color:{TEXT_MUT};
                        text-transform:uppercase;letter-spacing:.08em;margin-bottom:20px;">
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

                # 1. Asignar Edad
                if 'Edad' in inp.columns:
                    inp.at[0, 'Edad'] = edad

                # 2. Función de mapeo robusto a características del modelo (insensible a mayúsculas/minúsculas y acentos)
                def set_feature_val(prefix, val):
                    if not val:
                        return
                    # Normalizar cadenas para comparación
                    val_norm = str(val).lower().replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u').replace('ñ', 'n')
                    prefix_norm = prefix.lower()
                    
                    for col in inp.columns:
                        col_norm = col.lower().replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u').replace('ñ', 'n')
                        if col_norm.startswith(f"{prefix_norm}_"):
                            feat_val = col_norm[len(prefix_norm)+1:]
                            # Eliminar caracteres no alfanuméricos para comparación robusta de codificación
                            feat_val_clean = ''.join(c for c in feat_val if c.isalnum())
                            val_clean = ''.join(c for c in val_norm if c.isalnum())
                            if feat_val_clean == val_clean or val_clean in feat_val_clean or feat_val_clean in val_clean:
                                inp.at[0, col] = 1
                                return

                set_feature_val('Municipio', mun_sel)
                set_feature_val('Zona', zon_sel)
                set_feature_val('Genero', gen_sel)

                # 3. Mapear Actor Vial a Armas_medios
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

                # 4. Mapear Edad a Grupo_etario
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
                is_danger = pred != 0
                
                # Determinar nivel de riesgo (0-100)
                riesgo_pct = round(conf * 100, 1)
                
                # Determinar color y etiqueta según el nivel
                if riesgo_pct <= 40:
                    color_riesgo = SUCCESS
                    label_riesgo = "RIESGO BAJO · CONTROLADO"
                    icon_riesgo = "🟢"
                    bg_riesgo = "rgba(16,185,129,.08)"
                elif riesgo_pct <= 70:
                    color_riesgo = WARNING
                    label_riesgo = "RIESGO MODERADO · PRECAUCIÓN"
                    icon_riesgo = "🟡"
                    bg_riesgo = "rgba(245,158,11,.08)"
                else:
                    color_riesgo = DANGER
                    label_riesgo = "RIESGO ALTO · CRÍTICO"
                    icon_riesgo = "🔴"
                    bg_riesgo = "rgba(239,68,68,.08)"

                # Mostrar resultado estilo imagen
                st.markdown(f"""
                <div style="background:{BG_CARD};border:1px solid {BORDER};
                            border-radius:16px;padding:24px;min-height:420px;">
                    <div style="font-size:12px;font-weight:600;color:{TEXT_MUT};
                                text-transform:uppercase;letter-spacing:.08em;margin-bottom:16px;">
                        🔮 Resultado del análisis
                    </div>
                    <div style="text-align:center;">
                        <div style="font-size:4rem;font-weight:800;color:{color_riesgo};">
                            {riesgo_pct}%
                        </div>
                        <div style="font-size:0.9rem;font-weight:600;color:{TEXT_SEC};margin-top:4px;">
                            Índice de riesgo estimado
                        </div>
                        <div style="margin:16px 0;display:flex;justify-content:center;">
                            <div style="background:{bg_riesgo};border:1px solid {color_riesgo}40;
                                        border-radius:100px;padding:6px 20px;">
                                <span style="font-size:1.2rem;font-weight:700;color:{color_riesgo};">
                                    {icon_riesgo} {label_riesgo}
                                </span>
                            </div>
                        </div>
                        <div style="display:flex;justify-content:center;gap:12px;margin-top:16px;flex-wrap:wrap;">
                            <div style="background:{BG_CARD2};border-radius:8px;padding:8px 16px;">
                                <div style="font-size:10px;color:{TEXT_MUT};text-transform:uppercase;">Actor Vial</div>
                                <div style="font-size:14px;font-weight:600;color:{TEXT_PRI};">{act_sel if act_sel else 'N/D'}</div>
                            </div>
                            <div style="background:{BG_CARD2};border-radius:8px;padding:8px 16px;">
                                <div style="font-size:10px;color:{TEXT_MUT};text-transform:uppercase;">Municipio</div>
                                <div style="font-size:14px;font-weight:600;color:{TEXT_PRI};">{mun_sel if mun_sel else 'N/D'}</div>
                            </div>
                            <div style="background:{BG_CARD2};border-radius:8px;padding:8px 16px;">
                                <div style="font-size:10px;color:{TEXT_MUT};text-transform:uppercase;">Confianza</div>
                                <div style="font-size:14px;font-weight:600;color:{TEXT_PRI};">{conf:.1%}</div>
                            </div>
                        </div>
                        <div style="margin-top:16px;font-size:11px;color:{TEXT_MUT};">
                            Proyecto SENA · 2026
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error en predicción: {e}")
        else:
            st.markdown(f"""
            <div style="background:{BG_CARD};border:1px solid {BORDER};
                        border-radius:16px;padding:24px;min-height:420px;text-align:center;">
                <div style="font-size:12px;font-weight:600;color:{TEXT_MUT};
                            text-transform:uppercase;letter-spacing:.08em;margin-bottom:16px;">
                    🔮 Resultado del análisis
                </div>
                <div style="padding:48px 20px;">
                    <div style="font-size:40px;margin-bottom:12px;">📦</div>
                    <div style="color:{TEXT_SEC};font-size:14px;">
                        Modelo no disponible.<br>
                        Sube <code>modelo_accidentes.pkl</code> al repositorio.
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
#  PÁGINA 2 — ANÁLISIS VISUAL
# ════════════════════════════════════════════════════════════════
else:

    # Encabezado de sección
    st.markdown(f"""
    <div style="padding:8px 0 24px;">
        <h1 style="font-size:1.7rem;font-weight:700;color:{TEXT_PRI};margin:0 0 4px;">
            📊 Análisis de Accidentalidad
        </h1>
        <p style="color:{TEXT_SEC};font-size:.9rem;margin:0;">
            Facatativá &nbsp;•&nbsp; Funza &nbsp;•&nbsp; Madrid &nbsp;•&nbsp; Mosquera
            &nbsp;·&nbsp; {len(df):,} registros filtrados
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── KPIs (resumen rápido) ─────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-icon">🚨</div>
            <div class="kpi-label">Incidentes</div>
            <div class="kpi-value">{kpi_incidentes}</div>
            <div class="kpi-sub" style="color:{SUCCESS};">● Dataset activo</div>
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-icon">🎂</div>
            <div class="kpi-label">Edad media</div>
            <div class="kpi-value">{kpi_edad} años</div>
            <div class="kpi-sub">Promedio involucrados</div>
        </div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-icon">📍</div>
            <div class="kpi-label">Mayor riesgo</div>
            <div class="kpi-value" style="font-size:1.4rem;">{kpi_mun}</div>
            <div class="kpi-sub">Municipio</div>
        </div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-icon">🚶</div>
            <div class="kpi-label">Actor vulnerable</div>
            <div class="kpi-value" style="font-size:1.2rem;">{kpi_actor}</div>
            <div class="kpi-sub">Tipo actor vial</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── FILA 1: Municipio + Edad ──────────────────────────────
    c1, c2 = st.columns(2)

    with c1:
        st.markdown(f"""
        <div class="sec-title">🏙️ Siniestralidad por Municipio</div>
        <div class="sec-sub">Cantidad de incidentes registrados por localidad</div>
        """, unsafe_allow_html=True)
        if COL_MUN:
            vc = df[COL_MUN].value_counts().reset_index()
            vc.columns = ['Municipio', 'Incidentes']
            fig = go.Figure(go.Bar(
                x=vc['Municipio'], y=vc['Incidentes'],
                marker=dict(
                    color=vc['Incidentes'],
                    colorscale=[[0,"#1E3A5F"],[.5,ACCENT],[1,ACCENT2]],
                    line=dict(width=0)
                ),
                hovertemplate="<b>%{x}</b><br>Incidentes: %{y:,}<extra></extra>"
            ))
            fig = dark_layout(fig)
            fig.update_layout(showlegend=False, height=320)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with c2:
        st.markdown(f"""
        <div class="sec-title">📉 Perfil de Edad de los Involucrados</div>
        <div class="sec-sub">Distribución etaria de los actores viales</div>
        """, unsafe_allow_html=True)
        if COL_EDAD:
            ev = df[COL_EDAD].dropna()
            counts, bins = np.histogram(ev, bins=25)
            centers = (bins[:-1] + bins[1:]) / 2
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=centers, y=counts,
                marker=dict(color=ACCENT, opacity=.75, line=dict(width=0)),
                hovertemplate="Edad %{x:.0f}: %{y} casos<extra></extra>"
            ))
            fig2.add_trace(go.Scatter(
                x=centers, y=counts,
                fill='tozeroy', fillcolor="rgba(99,102,241,.18)",
                line=dict(color=ACCENT2, width=2), hoverinfo='skip'
            ))
            fig2 = dark_layout(fig2)
            fig2.update_layout(showlegend=False, height=320, barmode='overlay')
            st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
