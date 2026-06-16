import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
import joblib
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64
import os
import warnings
warnings.filterwarnings('ignore')

# ─── CONFIGURACIÓN ────────────────────────────────────────────
st.set_page_config(
    page_title="Seguridad Vial · Sabana Occidente",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── ESTILOS CSS ──────────────────────────────────────────────
st.markdown("""
<style>
    /* Base */
    .stApp {
        background: #0a0a0f !important;
    }
    
    /* Ocultar elementos */
    header, footer, [data-testid="stToolbar"], #MainMenu {
        display: none !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(15, 15, 25, 0.95) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255,255,255,0.05) !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stSlider label {
        color: #94a3b8 !important;
        font-size: 10px !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
    }
    
    [data-baseweb="select"] > div {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 8px !important;
        color: #ffffff !important;
    }
    
    .stSlider [data-baseweb="slider"] {
        background: rgba(255,255,255,0.08) !important;
    }
    
    /* Cards */
    .card {
        background: rgba(20, 20, 30, 0.6);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .card:hover {
        border-color: rgba(79, 140, 247, 0.2);
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.3);
    }
    
    .card-label {
        font-size: 10px;
        font-weight: 600;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 4px;
    }
    
    .card-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #ffffff;
        line-height: 1.2;
    }
    
    .card-sub {
        font-size: 11px;
        color: #94a3b8;
        margin-top: 2px;
    }
    
    .card-icon {
        float: right;
        font-size: 22px;
        opacity: 0.15;
    }
    
    /* Hero */
    .hero {
        background: linear-gradient(135deg, rgba(79, 140, 247, 0.08), rgba(124, 109, 240, 0.05));
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 2rem 2.5rem;
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
    }
    
    .hero::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(79, 140, 247, 0.05), transparent 70%);
        border-radius: 50%;
    }
    
    .hero-badge {
        display: inline-block;
        background: rgba(79, 140, 247, 0.12);
        border: 1px solid rgba(79, 140, 247, 0.15);
        border-radius: 100px;
        padding: 4px 14px;
        font-size: 11px;
        font-weight: 600;
        color: #4f8cf7;
        margin-bottom: 10px;
    }
    
    .hero h1 {
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 4px;
        letter-spacing: -0.02em;
    }
    
    .hero p {
        color: #94a3b8;
        font-size: 0.95rem;
    }
    
    /* Títulos */
    .section-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 2px;
    }
    
    .section-sub {
        font-size: 0.75rem;
        color: #94a3b8;
        margin-bottom: 12px;
    }
    
    /* Resultado */
    .result-container {
        background: rgba(20, 20, 30, 0.6);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 1.5rem;
        min-height: 400px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        backdrop-filter: blur(10px);
    }
    
    .result-percentage {
        font-size: 3.5rem;
        font-weight: 800;
        color: #ffffff;
        line-height: 1;
    }
    
    /* Gauge */
    .gauge-container {
        position: relative;
        width: 160px;
        height: 160px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .gauge-center .number {
        font-size: 2.5rem;
        font-weight: 800;
        color: #ffffff;
        line-height: 1;
    }
    
    .gauge-center .label {
        font-size: 9px;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 2px;
    }
    
    /* Grid */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    
    @media (max-width: 768px) {
        .kpi-grid {
            grid-template-columns: repeat(2, 1fr);
        }
        .hero h1 {
            font-size: 1.4rem;
        }
        .hero {
            padding: 1.25rem;
        }
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: #0a0a0f; }
    ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 2px; }
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

def plotly_dark_layout(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#94a3b8"),
        title_font=dict(color="#ffffff", size=13),
        margin=dict(l=8, r=8, t=30, b=8),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(255,255,255,0.06)",
            font=dict(color="#94a3b8", size=11)
        ),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.04)",
            linecolor="rgba(255,255,255,0.06)",
            tickfont=dict(color="#475569", size=10),
            title_font=dict(color="#94a3b8", size=11)
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.04)",
            linecolor="rgba(255,255,255,0.06)",
            tickfont=dict(color="#475569", size=10),
            title_font=dict(color="#94a3b8", size=11)
        ),
        hoverlabel=dict(
            bgcolor="#14141e",
            font=dict(color="#ffffff", size=12)
        )
    )
    return fig

# ─── CARGA DE DATOS ───────────────────────────────────────────
@st.cache_data
def load_data():
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
def load_model():
    try:
        return joblib.load('modelo_accidentes.pkl')
    except:
        return None

@st.cache_data
def train_model(df, target_col):
    """Entrena un modelo XGBoost con los datos disponibles"""
    try:
        # Preparar datos
        features = ['edad', 'municipio', 'zona', 'genero', 'actor_vial']
        available = [f for f in features if f in df.columns]
        
        if not available or target_col not in df.columns:
            return None, None
        
        X = df[available].copy()
        y = df[target_col].copy()
        
        # Codificar variables categóricas
        le_dict = {}
        for col in X.select_dtypes(include=['object']).columns:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            le_dict[col] = le
        
        # Entrenar XGBoost
        model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            use_label_encoder=False,
            eval_metric='logloss'
        )
        model.fit(X, y)
        
        return model, le_dict
    except Exception as e:
        return None, None

df_full = load_data()
modelo = load_model()

if df_full is None:
    st.error("🚨 No se encontró 'Archivo_Accidentes.csv'.")
    st.stop()

# Detectar columnas
COL_EDAD = find_col(df_full, 'edad', 'age')
COL_MUN = find_col(df_full, 'municipio', 'ciudad', 'municipality')
COL_ZONA = find_col(df_full, 'zona', 'zone', 'area')
COL_GENERO = find_col(df_full, 'genero', 'sexo', 'gender', 'sex')
COL_ACTOR = find_col(df_full, 'actor_vial', 'actor', 'tipo_actor', 'clase_actor', 'victima', 'rol')
COL_GRAVE = find_col(df_full, 'gravedad', 'severity', 'clase', 'tipo_accidente', 'clase_de_acc')

# ─── SIDEBAR ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 20px 16px 12px;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <div style="width: 36px; height: 36px; border-radius: 10px;
                        background: linear-gradient(135deg, #4f8cf7, #7c6df0);
                        display: flex; align-items: center; justify-content: center;
                        font-size: 16px; flex-shrink: 0;">
                🚦
            </div>
            <div>
                <div style="font-weight: 700; font-size: 14px; color: #ffffff;">
                    VialAnalytics
                </div>
                <div style="font-size: 10px; color: #475569;">
                    Sabana Occidente
                </div>
            </div>
        </div>
    </div>
    <hr style="border-color: rgba(255,255,255,0.06); margin: 0 16px;">
    """, unsafe_allow_html=True)

    pagina = st.radio(
        "Navegación",
        ["🏠 Inicio · Predictor", "📊 Análisis Visual"],
        label_visibility="collapsed"
    )

    st.markdown('<hr style="border-color: rgba(255,255,255,0.06); margin: 12px 16px;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 10px; font-weight: 600; color: #475569; text-transform: uppercase; letter-spacing: 0.08em; padding: 0 16px 8px;">Filtros</div>', unsafe_allow_html=True)

    df = df_full.copy()
    if COL_MUN:
        opts_mun = ["Todos"] + sorted(df[COL_MUN].dropna().unique().tolist())
        sel_mun = st.selectbox("Municipio", opts_mun, label_visibility="collapsed")
        if sel_mun != "Todos":
            df = df[df[COL_MUN] == sel_mun]

    if COL_GENERO:
        opts_gen = ["Todos"] + sorted(df[COL_GENERO].dropna().unique().tolist())
        sel_gen = st.selectbox("Género", opts_gen, label_visibility="collapsed")
        if sel_gen != "Todos":
            df = df[df[COL_GENERO] == sel_gen]

    if COL_ACTOR:
        opts_act = ["Todos"] + sorted(df[COL_ACTOR].dropna().unique().tolist())
        sel_act = st.selectbox("Actor Vial", opts_act, label_visibility="collapsed")
        if sel_act != "Todos":
            df = df[df[COL_ACTOR] == sel_act]

    st.markdown("""
    <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06);
                border-radius: 8px; padding: 12px 16px; margin: 12px 16px 0;">
        <div style="font-size: 9px; color: #475569; text-transform: uppercase; letter-spacing: 0.08em;">
            Registros filtrados
        </div>
        <div style="font-size: 20px; font-weight: 700; color: #4f8cf7;">
            """ + f"{len(df):,}" + """
        </div>
        <div style="font-size: 10px; color: #475569;">
            de """ + f"{len(df_full):,}" + """ totales
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─── CÁLCULO KPIs ────────────────────────────────────────────
kpi_incidentes = f"{len(df):,}"
kpi_edad = f"{df[COL_EDAD].mean():.1f}" if (COL_EDAD and not df.empty and not pd.isna(df[COL_EDAD].mean())) else "N/D"
kpi_mun = df[COL_MUN].mode()[0] if (COL_MUN and not df.empty and not df[COL_MUN].mode().empty) else "N/D"
kpi_actor = df[COL_ACTOR].mode()[0] if (COL_ACTOR and not df.empty and not df[COL_ACTOR].mode().empty) else "N/D"


# ════════════════════════════════════════════════════════════════
#  PÁGINA INICIO · PREDICTOR
# ════════════════════════════════════════════════════════════════
if "Inicio" in pagina:
    # ── HERO ──────────────────────────────────────────────────
    st.markdown(f"""
    <div class="hero">
        <div class="hero-badge">🚦 Proyecto SENA · 2026</div>
        <h1>Seguridad Vial · Sabana Occidente</h1>
        <p>Análisis de accidentalidad · Facatativá • Funza • Madrid • Mosquera</p>
    </div>
    """, unsafe_allow_html=True)

    # ── KPIs ──────────────────────────────────────────────────
    st.markdown(f"""
    <div class="kpi-grid">
        <div class="card">
            <span class="card-icon">📊</span>
            <div class="card-label">Incidentes filtrados</div>
            <div class="card-value">{kpi_incidentes}</div>
            <div class="card-sub">{sel_mun if sel_mun != 'Todos' else 'Todos'} · {sel_gen if sel_gen != 'Todos' else 'Todos'}</div>
        </div>
        <div class="card">
            <span class="card-icon">📈</span>
            <div class="card-label">Edad media crítica</div>
            <div class="card-value">{kpi_edad}</div>
            <div class="card-sub">Promedio de involucrados</div>
        </div>
        <div class="card">
            <span class="card-icon">📍</span>
            <div class="card-label">Mayor siniestralidad</div>
            <div class="card-value" style="font-size: 1.3rem;">{kpi_mun}</div>
            <div class="card-sub">Municipio de mayor riesgo</div>
        </div>
        <div class="card">
            <span class="card-icon">🚶</span>
            <div class="card-label">Actor más vulnerable</div>
            <div class="card-value" style="font-size: 1.1rem;">{kpi_actor}</div>
            <div class="card-sub">Tipo de actor vial</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ─── PREDICTOR DE RIESGO ─────────────────────────────────────
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 14px;">
        <div style="width: 3px; height: 20px; background: linear-gradient(180deg, #4f8cf7, #7c6df0); border-radius: 2px;"></div>
        <div>
            <div style="font-size: 0.95rem; font-weight: 600; color: #ffffff;">Predictor de Escenario de Riesgo</div>
            <div style="font-size: 0.75rem; color: #94a3b8;">Configura los parámetros del actor vial para obtener una predicción de riesgo</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    p1, p2 = st.columns([1, 1.2], gap="medium")
    
    with p1:
        st.markdown("""
        <div style="background: rgba(20, 20, 30, 0.6);
                    border: 1px solid rgba(255,255,255,0.06);
                    border-radius: 12px;
                    padding: 1.25rem;
                    backdrop-filter: blur(10px);">
            <div style="font-size: 10px; font-weight: 600; color: #475569; 
                        text-transform: uppercase; letter-spacing: 0.08em; 
                        margin-bottom: 16px;">
                ⚙️ Parámetros del escenario
            </div>
        """, unsafe_allow_html=True)
    
        edad = st.slider("Edad del actor vial", 0, 100, 30)
        mun_sel_pred = st.selectbox("Municipio", sorted(df_full[COL_MUN].dropna().unique())) if COL_MUN else None
        zon_sel_pred = st.selectbox("Zona del incidente", sorted(df_full[COL_ZONA].dropna().unique())) if COL_ZONA else None
        gen_sel_pred = st.selectbox("Género", sorted(df_full[COL_GENERO].dropna().unique())) if COL_GENERO else None
        act_sel_pred = st.selectbox("Tipo de actor vial", sorted(df_full[COL_ACTOR].dropna().unique())) if COL_ACTOR else None
    
        st.markdown("</div>", unsafe_allow_html=True)
    
    with p2:
        if modelo is not None:
            try:
                cols_mod = list(modelo.feature_names_in_)
                inp = pd.DataFrame(0, index=[0], columns=cols_mod)
    
                # Asignar edad
                for col in ['Edad', 'edad', 'age']:
                    if col in inp.columns:
                        inp.at[0, col] = edad
                        break
    
                # Función de mapeo
                def set_feature(prefix, val):
                    if not val:
                        return
                    val_norm = str(val).lower().replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u').replace('ñ', 'n')
                    for col in inp.columns:
                        col_norm = col.lower().replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u').replace('ñ', 'n')
                        if col_norm.startswith(f"{prefix.lower()}_"):
                            feat_val = col_norm[len(prefix.lower())+1:]
                            if feat_val == val_norm or val_norm in feat_val or feat_val in val_norm:
                                inp.at[0, col] = 1
                                return
    
                set_feature('Municipio', mun_sel_pred)
                set_feature('Zona', zon_sel_pred)
                set_feature('Genero', gen_sel_pred)
    
                # Mapear actor a arma
                arma_val = 'No Reportado'
                if act_sel_pred:
                    act_lower = act_sel_pred.lower()
                    if 'moto' in act_lower:
                        arma_val = 'Moto'
                    elif 'bicicleta' in act_lower or 'ciclista' in act_lower:
                        arma_val = 'Bicicleta'
                    elif 'vehiculo' in act_lower or 'vehículo' in act_lower:
                        arma_val = 'Vehiculo'
                    elif 'peaton' in act_lower or 'peatón' in act_lower:
                        arma_val = 'Sin empleo de armas'
                set_feature('Armas_medios', arma_val)
    
                # Grupo etario
                grupo_val = 'No Reportado'
                if edad < 12:
                    grupo_val = 'Menores'
                elif edad < 18:
                    grupo_val = 'Adolescentes'
                else:
                    grupo_val = 'Adultos'
                set_feature('Grupo_etario', grupo_val)
    
                # Predicción
                pred = modelo.predict(inp)[0]
                probs = modelo.predict_proba(inp)[0]
                conf = max(probs)
                riesgo_pct = round(conf * 100, 1)
    
                # Determinar nivel
                if riesgo_pct <= 40:
                    color = "#22c55e"
                    label = "RIESGO BAJO · CONTROLADO"
                    bg = "rgba(34,197,94,0.08)"
                elif riesgo_pct <= 70:
                    color = "#f59e0b"
                    label = "RIESGO MODERADO · PRECAUCIÓN"
                    bg = "rgba(245,158,11,0.08)"
                else:
                    color = "#ef4444"
                    label = "RIESGO ALTO · CRÍTICO"
                    bg = "rgba(239,68,68,0.08)"
    
                # === NUEVO DISEÑO DEL RESULTADO ===
                st.markdown(f"""<div style="background: rgba(20, 20, 30, 0.6); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 2rem 1.5rem; min-height: 400px; backdrop-filter: blur(10px); display: flex; flex-direction: column; align-items: center; justify-content: space-between;">
                    <div style="width: 100%; text-align: left; font-size: 11px; font-weight: 700; color: #5B6D8C; text-transform: uppercase; letter-spacing: 0.1em; display: flex; align-items: center; gap: 8px;">🔮 RESULTADO DEL ANÁLISIS</div>
                    <div style="position: relative; width: 220px; height: 200px; margin-top: 10px;">
                        <svg width="220" height="200" viewBox="0 0 220 200" style="position: absolute; top:0; left:0;">
                            <circle cx="110" cy="100" r="62" stroke="#1e2d45" stroke-width="12" fill="transparent" stroke-dasharray="260 130" stroke-linecap="round" style="transform: rotate(150deg); transform-origin: 110px 100px;" />
                            <circle cx="110" cy="100" r="80" stroke="#1a2540" stroke-width="12" fill="transparent" stroke-dasharray="335 168" stroke-linecap="round" style="transform: rotate(150deg); transform-origin: 110px 100px;" />
                            <circle cx="110" cy="100" r="80" stroke="{color}" stroke-width="12" fill="transparent" stroke-dasharray="{335 * (riesgo_pct/100)} 503" stroke-linecap="round" style="transform: rotate(150deg); transform-origin: 110px 100px; transition: stroke-dasharray 0.5s ease-in-out;" />
                        </svg>
                        <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; padding-top: 55px;">
                            <div style="font-size: 2.8rem; font-weight: 800; color: {color}; line-height: 1;">{riesgo_pct}%</div>
                            <div style="font-size: 11px; color: #94a3b8; font-weight: 500; margin-top: 6px; letter-spacing: 0.02em;">Índice de riesgo estimado</div>
                        </div>
                    </div>
                    <div style="background: {bg}; border: 1px solid {color}25; border-radius: 12px; padding: 16px 20px; width: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; margin-top: 15px;">
                        <div style="width: 14px; height: 14px; border-radius: 50%; background: radial-gradient(circle at 35% 35%, #ffffff 0%, {color} 40%, {color} 100%); box-shadow: 0 0 12px {color};"></div>
                        <div style="font-size: 0.82rem; font-weight: 700; color: {color}; letter-spacing: 0.05em; text-align: center;">{label}</div>
                    </div>
                    <div style="display: flex; gap: 10px; width: 100%; margin-top: 15px; justify-content: space-between;">
                        <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 8px; padding: 6px 4px; flex: 1; text-align: center;">
                            <div style="font-size: 8px; color: #475569; text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em; margin-bottom: 2px;">Actor Vial</div>
                            <div style="font-size: 11px; font-weight: 600; color: #ffffff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{act_sel_pred if act_sel_pred else 'N/D'}</div>
                        </div>
                        <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 8px; padding: 6px 4px; flex: 1; text-align: center;">
                            <div style="font-size: 8px; color: #475569; text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em; margin-bottom: 2px;">Municipio</div>
                            <div style="font-size: 11px; font-weight: 600; color: #ffffff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{mun_sel_pred if mun_sel_pred else 'N/D'}</div>
                        </div>
                        <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 8px; padding: 6px 4px; flex: 1; text-align: center;">
                            <div style="font-size: 8px; color: #475569; text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em; margin-bottom: 2px;">Confianza</div>
                            <div style="font-size: 11px; font-weight: 600; color: #ffffff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{conf:.1%}</div>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)
    
            except Exception as e:
                st.error(f"Error en predicción: {e}")
        else:
            st.markdown("""
            <div style="background: rgba(20, 20, 30, 0.6);
                        border: 1px solid rgba(255,255,255,0.06);
                        border-radius: 12px;
                        padding: 2rem;
                        min-height: 400px;
                        backdrop-filter: blur(10px);
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                        text-align: center;">
                <div style="font-size: 40px; margin-bottom: 12px;">📦</div>
                <div style="color: #94a3b8; font-size: 13px;">
                    Modelo no disponible.<br>
                    Sube <code style="background: rgba(255,255,255,0.06); padding: 2px 8px; border-radius: 4px;">modelo_accidentes.pkl</code>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
#  PÁGINA ANÁLISIS VISUAL
# ════════════════════════════════════════════════════════════════
else:
    # ── KPIs ──────────────────────────────────────────────────
    st.markdown(f"""
    <div class="kpi-grid">
        <div class="card">
            <span class="card-icon">📊</span>
            <div class="card-label">Incidentes</div>
            <div class="card-value">{kpi_incidentes}</div>
            <div class="card-sub">Registros activos</div>
        </div>
        <div class="card">
            <span class="card-icon">📈</span>
            <div class="card-label">Edad media</div>
            <div class="card-value">{kpi_edad}</div>
            <div class="card-sub">Promedio involucrados</div>
        </div>
        <div class="card">
            <span class="card-icon">📍</span>
            <div class="card-label">Mayor riesgo</div>
            <div class="card-value" style="font-size: 1.3rem;">{kpi_mun}</div>
            <div class="card-sub">Municipio</div>
        </div>
        <div class="card">
            <span class="card-icon">🚶</span>
            <div class="card-label">Actor vulnerable</div>
            <div class="card-value" style="font-size: 1.1rem;">{kpi_actor}</div>
            <div class="card-sub">Tipo de actor vial</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── GRÁFICOS ──────────────────────────────────────────────
    c1, c2 = st.columns(2, gap="medium")

    with c1:
        st.markdown('<div class="section-title">🏙️ Siniestralidad por Municipio</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Cantidad de incidentes registrados</div>', unsafe_allow_html=True)
        if COL_MUN:
            vc = df[COL_MUN].value_counts().reset_index()
            vc.columns = ['Municipio', 'Incidentes']
            fig = px.bar(
                vc, x='Municipio', y='Incidentes',
                color='Incidentes',
                color_continuous_scale=['rgba(79,140,247,0.3)', '#4f8cf7', '#7c6df0'],
                hover_data={'Incidentes': ':,d'}
            )
            fig = plotly_dark_layout(fig)
            fig.update_layout(showlegend=False, height=320)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with c2:
        st.markdown('<div class="section-title">📉 Perfil de Edad</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Distribución etaria de los actores viales</div>', unsafe_allow_html=True)
        if COL_EDAD:
            ev = df[COL_EDAD].dropna()
            fig = px.histogram(
                ev, nbins=25,
                color_discrete_sequence=['#4f8cf7'],
                opacity=0.7,
                labels={'value': 'Edad', 'count': 'Casos'}
            )
            fig = plotly_dark_layout(fig)
            fig.update_layout(showlegend=False, height=320, bargap=0.05)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # ── FILA 2 ─────────────────────────────────────────────────
    c3, c4 = st.columns(2, gap="medium")

    with c3:
        st.markdown('<div class="section-title">🚗 Actores Viales</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Top 8 tipos de actor vial involucrado</div>', unsafe_allow_html=True)
        if COL_ACTOR:
            vc_a = df[COL_ACTOR].value_counts().head(8).reset_index()
            vc_a.columns = ['Actor', 'Cantidad']
            fig = px.bar(
                vc_a, x='Cantidad', y='Actor',
                orientation='h',
                color='Cantidad',
                color_continuous_scale=['rgba(34,197,94,0.2)', '#22c55e'],
                hover_data={'Cantidad': ':,d'}
            )
            fig = plotly_dark_layout(fig)
            fig.update_layout(showlegend=False, height=320, yaxis=dict(autorange='reversed'))
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with c4:
        st.markdown('<div class="section-title">⚧ Distribución por Género</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Proporción de involucrados por género</div>', unsafe_allow_html=True)
        if COL_GENERO:
            vc_g = df[COL_GENERO].value_counts().reset_index()
            vc_g.columns = ['Genero', 'Cantidad']
            fig = px.pie(
                vc_g, values='Cantidad', names='Genero',
                color_discrete_sequence=['#4f8cf7', '#7c6df0', '#22c55e', '#f59e0b'],
                hole=0.55,
                hover_data={'Cantidad': ':,d'}
            )
            fig = plotly_dark_layout(fig)
            fig.update_layout(showlegend=True, height=320)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # ── FILA 3 ─────────────────────────────────────────────────
    c5, c6 = st.columns(2, gap="medium")

    with c5:
        if COL_ZONA:
            st.markdown('<div class="section-title">📍 Incidentes por Zona</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-sub">Clasificación urbana vs rural</div>', unsafe_allow_html=True)
            vc_z = df[COL_ZONA].value_counts().reset_index()
            vc_z.columns = ['Zona', 'Cantidad']
            fig = px.bar(
                vc_z, x='Zona', y='Cantidad',
                color_discrete_sequence=['#f59e0b'],
                opacity=0.8,
                hover_data={'Cantidad': ':,d'}
            )
            fig = plotly_dark_layout(fig)
            fig.update_layout(showlegend=False, height=300)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with c6:
        if COL_GRAVE:
            st.markdown('<div class="section-title">⚠️ Gravedad de Accidentes</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-sub">Distribución por nivel de gravedad</div>', unsafe_allow_html=True)
            vc_gr = df[COL_GRAVE].value_counts().reset_index()
            vc_gr.columns = ['Gravedad', 'Cantidad']
            fig = px.bar(
                vc_gr, x='Gravedad', y='Cantidad',
                color='Cantidad',
                color_continuous_scale=['#f59e0b', '#ef4444'],
                hover_data={'Cantidad': ':,d'}
            )
            fig = plotly_dark_layout(fig)
            fig.update_layout(showlegend=False, height=300)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # ── MAPA DE CALOR ──────────────────────────────────────────
    if COL_MUN and COL_ACTOR:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">🗺️ Mapa de Calor: Municipio × Actor Vial</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Concentración de incidentes por combinación</div>', unsafe_allow_html=True)

        pivot = (df.groupby([COL_MUN, COL_ACTOR])
                   .size().reset_index(name='n')
                   .pivot(index=COL_MUN, columns=COL_ACTOR, values='n')
                   .fillna(0))

        fig = px.imshow(
            pivot,
            color_continuous_scale=['rgba(20,20,30,0.8)', '#4f8cf7', '#7c6df0'],
            aspect='auto',
            labels=dict(x='Actor Vial', y='Municipio', color='Casos'),
            text_auto=True
        )
        fig = plotly_dark_layout(fig)
        fig.update_layout(height=360)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


# ─── FOOTER ───────────────────────────────────────────────────
st.markdown("""
<div style="border-top: 1px solid rgba(255,255,255,0.06); padding: 16px 0; text-align: center; margin-top: 20px;">
    <span style="color: #475569; font-size: 11px; letter-spacing: 0.02em;">
        🚦 VialAnalytics · Seguridad Vial Sabana Occidente · Proyecto SENA 2026
    </span>
</div>
""", unsafe_allow_html=True)
