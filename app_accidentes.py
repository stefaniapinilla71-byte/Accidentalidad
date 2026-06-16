import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Centro de Control: Seguridad Vial Sabana",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PALETA DE COLORES PREMIUM ---
fondo = '#1E293B'
azul = '#38BDF8'
naranja = '#F59E0B'
verde = '#34D399'
rojo = '#F87171'
morado = '#A78BFA'
palette = [azul, naranja, verde, morado, rojo]

# --- ESTILO CSS AVANZADO (TEMÁTICA TRÁNSITO) ---
st.markdown(f"""
<style>
    .main {{ background-color: {fondo}; color: white; }}
    .stApp {{ background-color: {fondo}; }}
    
    /* Estilo para las métricas de Dashboard */
    [data-testid="stMetricValue"] {{ color: {azul}; font-size: 38px; font-weight: bold; }}
    [data-testid="stMetricLabel"] {{ color: #CBD5E1; font-size: 18px; }}
    
    /* Contenedores de Tarjetas */
    .stMetric {{
        background-color: #2D3748;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #4A5568;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }}
    
    /* Botones y Sliders */
    .stButton>button {{ 
        background-color: {azul}; 
        color: white; 
        border-radius: 10px; 
        width: 100%; 
        font-weight: bold;
        height: 3em;
    }}
    .stSlider>div>div>div {{ background-color: {azul} !important; }}
    
    /* Títulos con tipografía moderna */
    h1, h2, h3 {{ 
        color: {azul}; 
        font-family: 'Inter', sans-serif;
        letter-spacing: -0.5px;
    }}
    
    /* Sidebar personalizado */
    .css-1d391kg {{ background-color: #1E293B; }}
</style>
""", unsafe_allow_html=True)

# --- CARGA DE DATOS Y MODELO ---
@st.cache_data
def load_clean_data():
    try:
        # Intento de carga con detección de separador
        df = pd.read_csv('transito_sabana_occidente.csv', sep=None, engine='python')
        # Normalización de columnas para evitar KeyErrors
        df.columns = df.columns.str.strip().str.capitalize()
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

df = load_clean_data()
modelo = load_trained_model()

# --- VERIFICACIÓN DE ARCHIVOS ---
if df is None or modelo is None:
    st.error("🚨 Error Crítico: No se encontraron los archivos necesarios ('transito_sabana_occidente.csv' o 'modelo_accidentes.pkl').")
    st.info("Asegúrate de que ambos archivos estén en la misma carpeta que este script.")
    st.stop()

# --- HEADER PRINCIPAL ---
st.title("🛡️ Centro de Inteligencia de Seguridad Vial")
st.markdown("#### Análisis de Accidentalidad: Funza • Mosquera • Facatativá • Madrid")
st.write("---")

# --- DASHBOARD DE CONTROL (KPIs) ---
st.subheader("📊 Indicadores de Movilidad")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Incidentes Registrados", f"{len(df):,}")
with col2:
    st.metric("Edad Media Crítica", f"{df['Edad'].mean():.1f} años")
with col3:
    st.metric("Municipio con Mayor Riesgo", df['Municipio'].mode()[0])
with col4:
    st.metric("Actor Vial más Vulnerable", df['Actor_vial'].mode()[0])

st.write("---")

# --- SIMULADOR DE ESCENARIOS DE RIESGO ---
col_sim, col_res = st.columns([1, 1.2])

with col_sim:
    st.subheader("🚦 Configuración del Escenario")
    st.info("Ajusta los parámetros para evaluar la probabilidad de riesgo vial.")
    
    edad = st.slider("Edad del Actor Vial", 0, 100, 30)
    mun = st.selectbox("Municipio de Ocurrencia", sorted(df['Municipio'].unique()))
    zon = st.selectbox("Zona del Incidente", sorted(df['Zona'].dropna().unique()))
    gen = st.selectbox("Género del Involucrado", sorted(df['Genero'].dropna().unique()))
    act = st.selectbox("Tipo de Actor Vial", sorted(df['Actor_vial'].dropna().unique()))

with col_res:
    st.subheader("🔮 Predicción de Riesgo Predictivo")
    
    # Lógica de inferencia basada en el modelo serializado
    cols_mod = list(modelo.feature_names_in_)
    input_df = pd.DataFrame(0, index=[0], columns=cols_mod)
    
    if 'Edad' in input_df.columns: input_df.at[0, 'Edad'] = edad
    
    # Activación de variables One-Hot (Sincronizado con el entrenamiento)
    for val in [f'Municipio_{mun}', f'Zona_{zon}', f'Genero_{gen}', f'Actor_vial_{act}']:
        if val in input_df.columns: input_df.at[0, val] = 1
    
    # Ejecución de la predicción
    pred = modelo.predict(input_df)[0]
    probs = modelo.predict_proba(input_df)[0]
    confianza = max(probs)
    
    # Diseño visual del resultado
    color_alerta = verde if pred == 0 else rojo
    status_text = "RIESGO BAJO / CONTROLADO" if pred == 0 else "RIESGO ALTO / CRÍTICO"
    
    st.markdown(f"""
    <div style="background-color: #2D3748; padding: 35px; border-radius: 20px; border-left: 12px solid {color_alerta};">
        <h4 style="color: #CBD5E1; margin-bottom: 10px;">ESTADO DEL ESCENARIO:</h4>
        <h2 style="color: {color_alerta}; margin: 0;">{status_text}</h2>
        <hr style="border: 0.5px solid #4A5568; margin: 20px 0;">
        <p style="font-size: 22px; color: {azul}; font-weight: bold;">Confianza Estadística: {confianza:.2%}</p>
        <p style="font-size: 14px; color: #94A3B8;">*Resultado basado en patrones históricos de la Sabana de Occidente.</p>
    </div>
    """, unsafe_allow_html=True)

st.write("---")

# --- ANÁLISIS VISUAL ESTRATÉGICO ---
st.subheader("📈 Análisis Geográfico y Demográfico")
g1, g2 = st.columns(2)

with g1:
    fig_mun = px.bar(df['Municipio'].value_counts().reset_index(), 
                     x='index', y='Municipio', 
                     title="Distribución de Siniestralidad por Municipio",
                     labels={'index': 'Municipio', 'Municipio': 'N° Incidentes'},
                     color_discrete_sequence=[azul])
    fig_mun.update_layout(paper_bgcolor=fondo, plot_bgcolor=fondo, font_color="white", title_font_color=azul)
    st.plotly_chart(fig_mun, use_container_width=True)

with g2:
    fig_edad = px.histogram(df, x='Edad', 
                            title="Perfil de Edad de los Involucrados",
                            labels={'Edad': 'Rango de Edad', 'count': 'Frecuencia'},
                            color_discrete_sequence=[naranja], nbins=30)
    fig_edad.update_layout(paper_bgcolor=fondo, plot_bgcolor=fondo, font_color="white", title_font_color=naranja, bargap=0.1)
    st.plotly_chart(fig_edad, use_container_width=True)

# --- FOOTER ESTRATÉGICO ---
st.markdown(f"""
<br><hr>
<div style="text-align: center; color: #64748B; font-size: 14px;">
    <b>Estrategia de Seguridad Vial Sabana Occidente</b><br>
    Desarrollado por Senior Data Scientist • 2026
</div>
""", unsafe_allow_html=True)
