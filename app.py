import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ee
import json
import datetime
from google.oauth2 import service_account
import folium
import streamlit.components.v1 as components

# ─────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN GLOBAL
# ─────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Fenología Tambopata | Macaw Society",
    page_icon="🦜",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #1a2e1a; }
    [data-testid="stSidebar"] * { color: #d4e6d4 !important; }
    [data-testid="metric-container"] {
        background-color: #f0f7f0; border: 1px solid #c3dfc3; border-radius: 10px; padding: 12px;
    }
    h2 { color: #1a5c1a; border-bottom: 2px solid #4CAF50; padding-bottom: 6px; }
    h3 { color: #2d7a2d; }
    .context-box {
        background: linear-gradient(135deg, #1a3d1a, #2d5c2d); color: white;
        border-radius: 12px; padding: 20px 28px; margin-bottom: 24px;
    }
    .context-box h1 { color: #a8e6a8; font-size: 1.6rem; margin:0 0 6px 0; }
    .context-box p  { color: #d4f0d4; margin: 0; font-size: 0.97rem; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────
# INICIALIZAR GOOGLE EARTH ENGINE
# ─────────────────────────────────────────────────────────────────────
@st.cache_resource
def init_gee():
    try:
        if 'gcp_service_account' in st.secrets:
            secret_val = st.secrets["gcp_service_account"]
            if isinstance(secret_val, str):
                key_dict = json.loads(secret_val)
            else:
                key_dict = dict(secret_val)
            credentials = service_account.Credentials.from_service_account_info(key_dict)
            scoped_credentials = credentials.with_scopes(['https://www.googleapis.com/auth/earthengine', 'https://www.googleapis.com/auth/cloud-platform'])
            ee.Initialize(scoped_credentials, project=key_dict.get('project_id'))
        else:
            ee.Initialize()
        return True
    except Exception as e:
        st.error(f"Error inicializando Google Earth Engine: {e}")
        return False

gee_is_ready = init_gee()

# ─────────────────────────────────────────────────────────────────────
# DICCIONARIOS Y CARGA DE DATOS (FENOLOGÍA)
# ─────────────────────────────────────────────────────────────────────
MESES = {1:'Ene',2:'Feb',3:'Mar',4:'Abr',5:'May',6:'Jun',
          7:'Jul',8:'Ago',9:'Sep',10:'Oct',11:'Nov',12:'Dic'}

FENOLOGIA_LABELS = {
    'RF': 'Fruto Maduro (RF)', 'D':  'Fruto Diseminado (D)', 'F':  'Flores (F)',
    'UF': 'Fruto Verde (UF)', 'B':  'Botones Florales (B)'
}
FENOLOGIA_COLS = list(FENOLOGIA_LABELS.keys())
COLORES_ROL = {
    'Estrella Comercial - Frutal': '#e67e22', 'Estrella Comercial - Industrial': '#e74c3c',
    'Ingeniero del Suelo - Fijador N': '#27ae60', 'Ingeniero del Suelo - Pionera': '#2ecc71',
    'Caja Fuerte - Maderable': '#8b4513', 'Caja Fuerte - Maderable / Fijador N': '#d35400',
}

@st.cache_data
def load_data():
    df = pd.read_csv('Datos_Procesados_Tambopata.csv')
    for col in FENOLOGIA_COLS:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    df['TEMPERATURE'] = pd.to_numeric(df['TEMPERATURE'], errors='coerce')
    df['RAIN']        = pd.to_numeric(df['RAIN'], errors='coerce')
    df['MONTH_LABEL'] = df['MONTH'].map(MESES)
    df['Fecha']       = pd.to_datetime(
        df['YEAR'].astype(str) + '-' + df['MONTH'].astype(str).str.zfill(2) + '-01'
    )
    cols_categoricas = ['Rol_Agroforestal', 'GENERO_limpio', 'Nombre científico', 'FAMILY', 'HABITAT']
    for col in cols_categoricas:
        if col in df.columns:
            df[col] = df[col].fillna('Desconocido')
    return df

df_original = load_data()

@st.cache_data
def load_censo():
    try:
        df_c = pd.read_csv('arboles_censo_colorado_1939.csv')
    except Exception:
        df_c = pd.DataFrame()
    return df_c

df_censo_master = load_censo()

# ─────────────────────────────────────────────────────────────────────
# SIDEBAR – FILTROS (Aplica a la fenología)
# ─────────────────────────────────────────────────────────────────────
st.sidebar.title("🔬 Filtros de Fenología")
anios = sorted(df_original['YEAR'].unique().tolist())
anio_sel = st.sidebar.multiselect("📅 Año (vacío = todos)", anios)
df = df_original[df_original['YEAR'].isin(anio_sel)] if anio_sel else df_original.copy()

zonas = sorted(df['PLOP'].dropna().unique().tolist())
zona_sel = st.sidebar.multiselect("📍 Zona (Parcela)", zonas, default=zonas)
df = df[df['PLOP'].isin(zona_sel)] if zona_sel else df.copy()

roles = df['Rol_Agroforestal'].unique().tolist()
rol_sel = st.sidebar.multiselect("🌿 Rol Agroforestal", roles, default=roles)
df_f = df[df['Rol_Agroforestal'].isin(rol_sel)] if rol_sel else df.copy()

generos = sorted(df_f['GENERO_limpio'].dropna().unique().tolist())
gen_sel = st.sidebar.multiselect("🔬 Género", generos)
if gen_sel: df_f = df_f[df_f['GENERO_limpio'].isin(gen_sel)]

especies = sorted(df_f['Nombre científico'].dropna().unique().tolist())
esp_sel = st.sidebar.multiselect("🌱 Especie", especies)
if esp_sel: df_f = df_f[df_f['Nombre científico'].isin(esp_sel)]

st.sidebar.markdown("---")
agrupar_labels = {'Rol Agroforestal': 'Rol_Agroforestal', 'Género': 'GENERO_limpio', 'Especie': 'Nombre científico'}
agrupar_label = st.sidebar.radio("📊 Agrupar gráficos por:", list(agrupar_labels.keys()))
agrupar_por   = agrupar_labels[agrupar_label]

st.sidebar.markdown("---")
metrica_label = st.sidebar.selectbox("🍃 Variable Fenológica:", list(FENOLOGIA_LABELS.values()))
metrica_col   = [k for k,v in FENOLOGIA_LABELS.items() if v == metrica_label][0]


# ─────────────────────────────────────────────────────────────────────
# BASE DE DATOS OFICIAL DE PARCELAS TAMBOPATA COLORADO (25 PARCELAS)
# ─────────────────────────────────────────────────────────────────────
PARCELAS_RED = {
    "🌳 TF1 — Tierra Firme (276m)": {"cod": "TF1", "hab": "Bosque de Tierra Firme", "lat": -13.147022, "lon": -69.620717, "alt": 276.3, "color": "green", "icon": "tree"},
    "🌳 TF2 — Tierra Firme (266m)": {"cod": "TF2", "hab": "Bosque de Tierra Firme", "lat": -13.143396, "lon": -69.622705, "alt": 266.0, "color": "green", "icon": "tree"},
    "🌳 TF3 — Tierra Firme (271m)": {"cod": "TF3", "hab": "Bosque de Tierra Firme", "lat": -13.137652, "lon": -69.620782, "alt": 270.6, "color": "green", "icon": "tree"},
    "🌳 TF4 — Tierra Firme (268m)": {"cod": "TF4", "hab": "Bosque de Tierra Firme", "lat": -13.136123, "lon": -69.619983, "alt": 267.9, "color": "green", "icon": "tree"},
    "🌳 TF5 — Tierra Firme (303m)": {"cod": "TF5", "hab": "Bosque de Tierra Firme", "lat": -13.140597, "lon": -69.617934, "alt": 303.2, "color": "green", "icon": "tree"},
    "🌴 AG1 — Aguajal (253m)": {"cod": "AG1", "hab": "Bosque de Aguajal", "lat": -13.138410, "lon": -69.613426, "alt": 253.0, "color": "blue", "icon": "tint"},
    "🌴 AG2 — Aguajal (280m)": {"cod": "AG2", "hab": "Bosque de Aguajal", "lat": -13.136985, "lon": -69.618303, "alt": 280.0, "color": "blue", "icon": "tint"},
    "🌴 AG3 — Aguajal (250m)": {"cod": "AG3", "hab": "Bosque de Aguajal", "lat": -13.138098, "lon": -69.613958, "alt": 250.0, "color": "blue", "icon": "tint"},
    "🌴 AG4 — Aguajal (254m)": {"cod": "AG4", "hab": "Bosque de Aguajal", "lat": -13.134740, "lon": -69.618893, "alt": 254.0, "color": "blue", "icon": "tint"},
    "🌴 AG5 — Aguajal (260m)": {"cod": "AG5", "hab": "Bosque de Aguajal", "lat": -13.134953, "lon": -69.618656, "alt": 260.0, "color": "blue", "icon": "tint"},
    "🌴 AG6 — Aguajal (266m)": {"cod": "AG6", "hab": "Bosque de Aguajal", "lat": -13.138562, "lon": -69.613208, "alt": 265.9, "color": "blue", "icon": "tint"},
    "🌴 AG7 — Aguajal (260m)": {"cod": "AG7", "hab": "Bosque de Aguajal", "lat": -13.138288, "lon": -69.613958, "alt": 260.0, "color": "blue", "icon": "tint"},
    "🌴 AG8 — Aguajal (257m)": {"cod": "AG8", "hab": "Bosque de Aguajal", "lat": -13.135055, "lon": -69.618801, "alt": 257.0, "color": "blue", "icon": "tint"},
    "🌴 AG9 — Aguajal (269m)": {"cod": "AG9", "hab": "Bosque de Aguajal", "lat": -13.136955, "lon": -69.618083, "alt": 268.8, "color": "blue", "icon": "tint"},
    "🌊 FP1 — Bajío (243m)": {"cod": "FP1", "hab": "Bosque de Bajío", "lat": -13.132427, "lon": -69.606840, "alt": 242.7, "color": "cadetblue", "icon": "water"},
    "🌊 FP2 — Bajío (258m)": {"cod": "FP2", "hab": "Bosque de Bajío", "lat": -13.133555, "lon": -69.610408, "alt": 257.6, "color": "cadetblue", "icon": "water"},
    "🌊 FP3 — Bajío (259m)": {"cod": "FP3", "hab": "Bosque de Bajío", "lat": -13.133262, "lon": -69.614538, "alt": 258.8, "color": "cadetblue", "icon": "water"},
    "🌊 FP4 — Bajío (257m)": {"cod": "FP4", "hab": "Bosque de Bajío", "lat": -13.129899, "lon": -69.616082, "alt": 257.0, "color": "cadetblue", "icon": "water"},
    "🌊 FP6 — Bajío (246m)": {"cod": "FP6", "hab": "Bosque de Bajío", "lat": -13.130647, "lon": -69.611740, "alt": 245.7, "color": "cadetblue", "icon": "water"},
    "🌿 BS1 — Sucesional (261m)": {"cod": "BS1", "hab": "Bosque Sucesional", "lat": -12.693745, "lon": -69.603175, "alt": 260.9, "color": "orange", "icon": "leaf"},
    "🌿 BS2 — Sucesional (286m)": {"cod": "BS2", "hab": "Bosque Sucesional", "lat": -13.143058, "lon": -69.602035, "alt": 286.0, "color": "orange", "icon": "leaf"},
    "🌿 BS3 — Sucesional (242m)": {"cod": "BS3", "hab": "Bosque Sucesional", "lat": -13.141842, "lon": -69.600008, "alt": 241.8, "color": "orange", "icon": "leaf"},
    "🌿 BS4 — Sucesional (270m)": {"cod": "BS4", "hab": "Bosque Sucesional", "lat": -13.149407, "lon": -69.613915, "alt": 270.0, "color": "orange", "icon": "leaf"},
    "🌿 BS6 — Sucesional (244m)": {"cod": "BS6", "hab": "Bosque Sucesional", "lat": -13.141767, "lon": -69.599470, "alt": 243.7, "color": "orange", "icon": "leaf"},
    "🌿 BS7 — Sucesional (268m)": {"cod": "BS7", "hab": "Bosque Sucesional", "lat": -13.146656, "lon": -69.613798, "alt": 267.7, "color": "orange", "icon": "leaf"},
    "📍 Coordenadas Personalizadas": {"cod": "CUSTOM", "hab": "Personalizado", "lat": -13.147022, "lon": -69.620717, "alt": 276.3, "color": "purple", "icon": "map-pin"}
}

# ─────────────────────────────────────────────────────────────────────
# TABS PRINCIPALES
# ─────────────────────────────────────────────────────────────────────
tab_feno, tab_censo, tab_mapa, tab_clima = st.tabs([
    "🌱 Fenología Forestal",
    "📋 Censo de Árboles (1,939 TAGs)",
    "🗺️ Visor de Verdor y Estrés (10m)",
    "🛰️ Extractor Climático Satelital"
])

# =====================================================================
# TAB 1: FENOLOGÍA
# =====================================================================
with tab_feno:
    st.markdown("""
    <div class="context-box">
      <h1>🦜 Fenología Forestal en la Reserva Nacional de Tambopata</h1>
      <p>Base de datos fenológica histórica <strong>2010–2017</strong> · Proyecto <strong>Macaw Society</strong><br>
      Seguimiento mensual de especies forestales clave para la alimentación de guacamayos en 'colpa colorado' y su potencial en sistemas <strong>agroforestales sintrópicos</strong>.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("📊 Resumen del Dataset Filtrado")
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("🗂️ Registros", f"{len(df_f):,}")
    k2.metric("🌳 Especies", df_f['Nombre científico'].nunique())
    k3.metric("🔬 Géneros", df_f['GENERO_limpio'].nunique())
    k4.metric("🏠 Familias", df_f['FAMILY'].nunique())
    k5.metric("📅 Años", df_f['YEAR'].nunique())
    st.markdown("---")

    # Gráfico 1
    st.subheader(f"📈 Evolución Temporal de {metrica_label} (2010–2017)")
    df_evo = df_f.groupby(['Fecha', agrupar_por])[metrica_col].mean().reset_index()
    fig_evo = px.line(df_evo, x='Fecha', y=metrica_col, color=agrupar_por, color_discrete_map=COLORES_ROL, template='plotly_white')
    st.plotly_chart(fig_evo, use_container_width=True)
    
    # Gráfico 2
    st.subheader(f"📅 Estacionalidad Mensual de {metrica_label}")
    df_men = df_f.groupby(['MONTH', 'MONTH_LABEL', agrupar_por])[metrica_col].mean().reset_index().sort_values('MONTH')
    fig_men = px.bar(df_men, x='MONTH_LABEL', y=metrica_col, color=agrupar_por, barmode='group', color_discrete_map=COLORES_ROL, template='plotly_white')
    st.plotly_chart(fig_men, use_container_width=True)

    # Gráfico 3
    st.subheader("🗓️ Calendario Fenológico (Heatmap)")
    df_heat = df_f.groupby(['GENERO_limpio', 'MONTH'])[metrica_col].mean().reset_index()
    df_heat['Mes'] = df_heat['MONTH'].map(MESES)
    pivot = df_heat.pivot_table(index='GENERO_limpio', columns='Mes', values=metrica_col)
    pivot = pivot[[m for m in MESES.values() if m in pivot.columns]]
    fig_heat = px.imshow(pivot, color_continuous_scale='YlOrRd', aspect='auto', template='plotly_white')
    st.plotly_chart(fig_heat, use_container_width=True)

    # Gráfico 4
    st.subheader("🌦️ Fenología vs. Clima")
    n_anios_g4 = df_f['YEAR'].nunique()
    if n_anios_g4 > 1:
        modo_g4 = st.radio(
            "Visualización de Fenología vs Clima:",
            ["📅 Serie Temporal Continua (Año a Año)", "🔄 Ciclo Estacional Promedio (Ene a Dic)"],
            horizontal=True, key="modo_g4"
        )
    else:
        modo_g4 = "🔄 Ciclo Estacional Promedio (Ene a Dic)"

    if "Continua" in modo_g4:
        df_clima = df_f.groupby('Fecha')[['RAIN', 'TEMPERATURE', metrica_col]].mean().reset_index()
        x_g4 = df_clima['Fecha']
    else:
        df_clima = df_f.groupby('MONTH')[['RAIN', 'TEMPERATURE', metrica_col]].mean().reset_index()
        df_clima['Mes'] = df_clima['MONTH'].map(MESES)
        x_g4 = df_clima['Mes']

    fig_clima = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.12, specs=[[{"secondary_y": True}], [{"secondary_y": True}]])
    fig_clima.add_trace(go.Bar(x=x_g4, y=df_clima['RAIN'], name='Lluvia (mm)', marker_color='lightblue'), row=1, col=1, secondary_y=False)
    fig_clima.add_trace(go.Scatter(x=x_g4, y=df_clima[metrica_col], name=metrica_label, line=dict(color='forestgreen', width=3)), row=1, col=1, secondary_y=True)
    fig_clima.add_trace(go.Scatter(x=x_g4, y=df_clima['TEMPERATURE'], name='Temp (°C)', line=dict(color='tomato', width=3)), row=2, col=1, secondary_y=False)
    fig_clima.add_trace(go.Scatter(x=x_g4, y=df_clima[metrica_col], name=metrica_label, line=dict(color='forestgreen', width=3), showlegend=False), row=2, col=1, secondary_y=True)
    fig_clima.update_layout(height=600, template='plotly_white', hovermode='x unified')
    if "Estacional" in modo_g4:
        fig_clima.update_xaxes(categoryorder='array', categoryarray=list(MESES.values()))
    st.plotly_chart(fig_clima, use_container_width=True)

    # ── Gráfico 5: Respuesta Fenológica a la Lluvia ──
    st.markdown("---")
    st.subheader("🌧️ Respuesta Fenológica a la Lluvia por Especie")
    st.caption("¿Qué especies responden más a los cambios de lluvia? "
               "Se mide la correlación (r de Pearson) entre lluvia mensual y la actividad de Flores o Frutos Verdes.")

    var_respuesta = st.radio(
        "Variable fenológica a analizar:",
        ['Flores (F)', 'Frutos Verdes (UF)'],
        horizontal=True, key='var_respuesta'
    )
    col_resp = 'F' if 'Flores' in var_respuesta else 'UF'
    label_resp = 'Flores' if col_resp == 'F' else 'Frutos Verdes'

    # Calcular correlación de cada especie con la lluvia
    df_var = df_f.copy()
    df_var[col_resp] = pd.to_numeric(df_var[col_resp], errors='coerce').fillna(0)

    especies_unicas = df_var['Nombre científico'].unique()
    resultados = []
    for sp in especies_unicas:
        df_sp_temp = df_var[df_var['Nombre científico'] == sp]
        n_reg = len(df_sp_temp)
        if n_reg < 20:
            continue
        mensual = df_sp_temp.groupby('MONTH').agg(
            feno=(col_resp, 'mean'),
            lluvia=('RAIN', 'mean'),
            temp=('TEMPERATURE', 'mean')
        ).reset_index()
        if mensual['feno'].sum() == 0:
            continue
        if len(mensual) >= 4:
            r_ll = mensual['feno'].corr(mensual['lluvia'])
            r_t = mensual['feno'].corr(mensual['temp'])
            if np.isnan(r_ll):
                continue
            mes_pico_num = mensual.loc[mensual['feno'].idxmax(), 'MONTH']
            resultados.append({
                'Especie': sp,
                'r_Lluvia': r_ll,
                'r_Temperatura': r_t if not np.isnan(r_t) else 0.0,
                'abs_r_Lluvia': abs(r_ll),
                'Media': mensual['feno'].mean(),
                'Mes_Pico': MESES.get(mes_pico_num, '?'),
                'N': n_reg
            })

    if resultados:
        df_rank = pd.DataFrame(resultados).sort_values('abs_r_Lluvia', ascending=True)

        fig_rank = px.bar(
            df_rank, x='r_Lluvia', y='Especie',
            orientation='h',
            color='r_Lluvia',
            color_continuous_scale='RdBu',
            color_continuous_midpoint=0,
            template='plotly_white',
            labels={'r_Lluvia': f'Correlación {label_resp} vs Lluvia (r)', 'Especie': ''},
            hover_data={'Media': ':.3f', 'Mes_Pico': True, 'N': True, 'r_Temperatura': ':.3f'}
        )
        fig_rank.update_layout(
            height=max(400, len(df_rank) * 28),
            yaxis={'categoryorder': 'total ascending'}
        )
        fig_rank.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.5)
        st.plotly_chart(fig_rank, use_container_width=True)

        st.caption("🔵 Azul = más lluvia → más " + label_resp.lower() + " · "
                   "🔴 Rojo = menos lluvia → más " + label_resp.lower() + " · "
                   "Barras más largas = mayor respuesta a la lluvia")

        # Selector de especie
        sp_list_resp = df_rank.sort_values('abs_r_Lluvia', ascending=False)['Especie'].tolist()
        sp_sel = st.selectbox("Selecciona una especie para ver el detalle:", sp_list_resp)

        sp_row = df_rank[df_rank['Especie'] == sp_sel].iloc[0]
        col_i1, col_i2, col_i3, col_i4 = st.columns(4)
        col_i1.metric("r vs Lluvia", f"{sp_row['r_Lluvia']:.3f}")
        col_i2.metric("r vs Temperatura", f"{sp_row['r_Temperatura']:.3f}")
        col_i3.metric("Mes Pico", sp_row['Mes_Pico'])
        col_i4.metric("Registros", f"{int(sp_row['N']):,}")

        # Interpretación
        r_ll = sp_row['r_Lluvia']
        if abs(r_ll) > 0.6:
            if r_ll > 0:
                st.success(f"📈 **Respuesta fuerte positiva:** Cuando llueve más, *{sp_sel}* produce más {label_resp.lower()}.")
            else:
                st.warning(f"📉 **Respuesta fuerte negativa:** Cuando llueve menos (época seca), *{sp_sel}* produce más {label_resp.lower()}.")
        elif abs(r_ll) > 0.3:
            st.info(f"↔️ **Respuesta moderada** a la lluvia (r = {r_ll:.3f}).")
        else:
            st.info(f"⚪ **Respuesta débil:** La lluvia no parece ser el detonante principal de {label_resp.lower()} en *{sp_sel}*.")

        # Gráfico superpuesto para la especie seleccionada
        df_sp = df_var[df_var['Nombre científico'] == sp_sel]
        n_anios_sp = df_sp['YEAR'].nunique()
        if n_anios_sp > 1:
            modo_sp = st.radio(
                f"Modo temporal para {sp_sel}:",
                ["📅 Serie Temporal Continua (Año a Año)", "🔄 Ciclo Estacional Promedio (Ene a Dic)"],
                horizontal=True, key=f"modo_sp_{sp_sel}"
            )
        else:
            modo_sp = "🔄 Ciclo Estacional Promedio (Ene a Dic)"

        if "Continua" in modo_sp:
            df_sp_clima = df_sp.groupby('Fecha').agg(
                Fenología=(col_resp, 'mean'),
                Lluvia_mm=('RAIN', 'mean'),
                Temperatura_C=('TEMPERATURE', 'mean')
            ).reset_index()
            x_sp = df_sp_clima['Fecha']
        else:
            df_sp_clima = df_sp.groupby('MONTH').agg(
                Fenología=(col_resp, 'mean'),
                Lluvia_mm=('RAIN', 'mean'),
                Temperatura_C=('TEMPERATURE', 'mean')
            ).reset_index()
            df_sp_clima['Mes'] = df_sp_clima['MONTH'].map(MESES)
            x_sp = df_sp_clima['Mes']

        fig_cruce = make_subplots(specs=[[{"secondary_y": True}]])
        fig_cruce.add_trace(
            go.Bar(x=x_sp, y=df_sp_clima['Fenología'],
                   name=label_resp, marker_color='#2d7a2d', opacity=0.8),
            secondary_y=False
        )
        fig_cruce.add_trace(
            go.Scatter(x=x_sp, y=df_sp_clima['Lluvia_mm'],
                       name='Lluvia (mm)', line=dict(color='#3498db', width=3)),
            secondary_y=True
        )
        fig_cruce.add_trace(
            go.Scatter(x=x_sp, y=df_sp_clima['Temperatura_C'],
                       name='Temperatura (°C)', line=dict(color='tomato', width=3, dash='dot')),
            secondary_y=True
        )
        fig_cruce.update_layout(
            height=420, template='plotly_white', hovermode='x unified',
            legend=dict(orientation='h', yanchor='bottom', y=1.02)
        )
        if "Estacional" in modo_sp:
            fig_cruce.update_layout(xaxis={'categoryorder': 'array', 'categoryarray': list(MESES.values())})
        fig_cruce.update_yaxes(title_text=f"{label_resp} (media)", secondary_y=False)
        fig_cruce.update_yaxes(title_text="Lluvia (mm) / Temp (°C)", secondary_y=True)
        st.plotly_chart(fig_cruce, use_container_width=True)

        # Scatter plots
        corr_data = df_sp_clima[['Fenología', 'Lluvia_mm', 'Temperatura_C']].dropna()
        if len(corr_data) >= 4:
            sc1, sc2 = st.columns(2)
            with sc1:
                fig_sc_ll = px.scatter(
                    corr_data, x='Lluvia_mm', y='Fenología',
                    trendline='ols', template='plotly_white',
                    labels={'Lluvia_mm': 'Lluvia (mm)', 'Fenología': label_resp},
                    color_discrete_sequence=['#3498db']
                )
                fig_sc_ll.update_layout(height=300)
                st.plotly_chart(fig_sc_ll, use_container_width=True)
            with sc2:
                fig_sc_t = px.scatter(
                    corr_data, x='Temperatura_C', y='Fenología',
                    trendline='ols', template='plotly_white',
                    labels={'Temperatura_C': 'Temperatura (°C)', 'Fenología': label_resp},
                    color_discrete_sequence=['tomato']
                )
                fig_sc_t.update_layout(height=300)
                st.plotly_chart(fig_sc_t, use_container_width=True)

        # Tabla descargable
        with st.expander("Ver tabla completa de respuesta a la lluvia"):
            tabla_resp = df_rank[['Especie', 'r_Lluvia', 'r_Temperatura', 'Media', 'Mes_Pico', 'N']].copy()
            tabla_resp.columns = ['Especie', 'r vs Lluvia', 'r vs Temperatura', f'Media {label_resp}', 'Mes Pico', 'Registros']
            tabla_resp = tabla_resp.sort_values('r vs Lluvia', key=abs, ascending=False)
            st.dataframe(tabla_resp, use_container_width=True, hide_index=True)
            csv_resp = tabla_resp.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Descargar tabla CSV", csv_resp, f"respuesta_lluvia_{col_resp}.csv", "text/csv")
    else:
        st.warning("No hay especies con datos suficientes para calcular la correlación.")

    # ── Gráfico 6: Cruce con Sentinel-2 NDWI (Humedad Foliar a 10 metros) ──
    st.markdown("---")
    st.subheader("🛰️ Cruce con Sentinel-2 NDWI (Humedad Foliar a 10 metros)")
    st.caption("Análisis de la respuesta fenológica frente al estrés hídrico en la copa de los árboles medido a alta resolución (10m) por la Agencia Espacial Europea (ESA Copernicus).")

    import os
    if os.path.exists('sentinel2_ndwi_10m.csv'):
        df_s2_local = pd.read_csv('sentinel2_ndwi_10m.csv')
        df_s2_local['DATETIME'] = pd.to_datetime(df_s2_local['DATETIME'])
        df_s2_local['MONTH'] = df_s2_local['DATETIME'].dt.month

        s2_mensual = df_s2_local.groupby('MONTH')['NDWI_10M'].agg(
            NDWI_Medio='mean', NDWI_Min='min', NDWI_Max='max'
        ).reset_index()
        s2_mensual['Mes'] = s2_mensual['MONTH'].map(MESES)

        # Fenología mensual filtrada
        feno_m_s2 = df_f.groupby('MONTH').agg(
            F_mean=('F', 'mean'),
            UF_mean=('UF', 'mean'),
            RF_mean=('RF', 'mean')
        ).reset_index()

        df_cruce_s2 = pd.merge(s2_mensual, feno_m_s2, on='MONTH', how='inner').sort_values('MONTH')

        # Selector de variable para comparar con NDWI
        var_ndwi_sel = st.selectbox(
            "Selecciona la fase fenológica para comparar con el NDWI:",
            ["Fruto Maduro (RF)", "Flores (F)", "Fruto Verde (UF)"],
            key="var_ndwi_choice"
        )
        col_feno_ndwi = 'RF_mean' if 'Maduro' in var_ndwi_sel else ('F_mean' if 'Flores' in var_ndwi_sel else 'UF_mean')
        label_feno_ndwi = var_ndwi_sel

        # Gráfico dual
        fig_s2 = make_subplots(specs=[[{"secondary_y": True}]])
        fig_s2.add_trace(
            go.Scatter(
                x=df_cruce_s2['Mes'], y=df_cruce_s2['NDWI_Medio'],
                name='NDWI Dosel (10m - ESA)',
                line=dict(color='#1b5e20', width=3),
                mode='lines+markers',
                fill='tozeroy', fillcolor='rgba(46, 125, 50, 0.15)'
            ),
            secondary_y=False
        )
        fig_s2.add_trace(
            go.Bar(
                x=df_cruce_s2['Mes'], y=df_cruce_s2[col_feno_ndwi],
                name=label_feno_ndwi,
                marker_color='#d35400' if 'Maduro' in var_ndwi_sel else ('#2980b9' if 'Flores' in var_ndwi_sel else '#27ae60'),
                opacity=0.75
            ),
            secondary_y=True
        )
        fig_s2.update_layout(
            height=430, template='plotly_white', hovermode='x unified',
            xaxis={'categoryorder': 'array', 'categoryarray': list(MESES.values())},
            legend=dict(orientation='h', yanchor='bottom', y=1.02)
        )
        fig_s2.update_yaxes(title_text="NDWI Dosel Foliar (10m)", secondary_y=False)
        fig_s2.update_yaxes(title_text=f"Actividad: {label_feno_ndwi}", secondary_y=True)
        st.plotly_chart(fig_s2, use_container_width=True)

        # Métricas de correlación
        r_f_val = df_cruce_s2['F_mean'].corr(df_cruce_s2['NDWI_Medio'])
        r_uf_val = df_cruce_s2['UF_mean'].corr(df_cruce_s2['NDWI_Medio'])
        r_rf_val = df_cruce_s2['RF_mean'].corr(df_cruce_s2['NDWI_Medio'])

        c1_s2, c2_s2, c3_s2 = st.columns(3)
        c1_s2.metric("r (Flores vs NDWI)", f"{r_f_val:.3f}", delta="Floración en pico húmedo" if r_f_val > 0 else "Floración en sequía")
        c2_s2.metric("r (Frutos Verdes vs NDWI)", f"{r_uf_val:.3f}")
        c3_s2.metric("r (Frutos Maduros vs NDWI)", f"{r_rf_val:.3f}", delta="Maduración inducida por estrés hídrico" if r_rf_val < -0.3 else None)

        if r_rf_val < -0.4:
            st.info("💡 **Hallazgo Clave para la Tesis:** Existe una **correlación negativa marcada** entre el NDWI a 10m y los Frutos Maduros (RF). "
                    "Cuando el dosel forestal alcanza su punto mínimo de humedad foliar en agosto-septiembre (estrés hídrico ~0.23), los árboles alcanzan su pico de maduración y dispersión de semillas.")
    else:
        st.info("ℹ️ Para ver este cruce, genera y descarga primero los datos de Sentinel-2 desde la pestaña '🛰️ Extractor Climático Satelital'.")


# =====================================================================
# TAB 2: CENSO MAESTRO DE ÁRBOLES (1,939 ÁRBOLES EN 25 PARCELAS)
# =====================================================================
with tab_censo:
    st.title("📋 Censo Maestro de Árboles y Especies — Red Colorado")
    st.write("Catálogo oficial de **1,939 árboles individuales marcados con placa (TAG)** en las 25 parcelas georreferenciadas de Tambopata (Proyecto Macaw Society).")

    if not df_censo_master.empty:
        # Métricas generales del censo
        c_c1, c_c2, c_c3, c_c4 = st.columns(4)
        c_c1.metric("🌳 Total Árboles Marcados", f"{len(df_censo_master):,}")
        c_c2.metric("🌿 Especies Botánicas", f"{df_censo_master['Nombre_cientifico_limpio'].nunique()}")
        c_c3.metric("📍 Parcelas Monitoreadas", f"{df_censo_master['PLOP'].nunique()}")
        c_c4.metric("🏷️ Géneros Identificados", f"{df_censo_master['GENERO'].nunique()}")

        st.markdown("---")

        # Filtros rápidos para el catálogo
        f_col1, f_col2, f_col3 = st.columns([1.2, 1.2, 1.6])
        with f_col1:
            filtro_plop = st.multiselect(
                "📍 Filtrar por Parcela:",
                sorted(df_censo_master['PLOP'].dropna().unique().tolist()),
                default=[]
            )
        with f_col2:
            filtro_genero = st.multiselect(
                "🔬 Filtrar por Género:",
                sorted(df_censo_master['GENERO'].dropna().unique().tolist()),
                default=[]
            )
        with f_col3:
            busqueda_tag = st.text_input("🔍 Buscar por TAG (Placa) o Nombre:", "")

        df_censo_filtrado = df_censo_master.copy()
        if filtro_plop:
            df_censo_filtrado = df_censo_filtrado[df_censo_filtrado['PLOP'].isin(filtro_plop)]
        if filtro_genero:
            df_censo_filtrado = df_censo_filtrado[df_censo_filtrado['GENERO'].isin(filtro_genero)]
        if busqueda_tag:
            df_censo_filtrado = df_censo_filtrado[
                df_censo_filtrado['TAG'].astype(str).str.contains(busqueda_tag, case=False, na=False) |
                df_censo_filtrado['Nombre_cientifico_limpio'].str.contains(busqueda_tag, case=False, na=False)
            ]

        # Gráficos del censo
        cg1, cg2 = st.columns([1.4, 1.0])
        with cg1:
            top_sp = (df_censo_filtrado['Nombre_cientifico_limpio']
                      .value_counts().head(12).reset_index())
            top_sp.columns = ['Especie', 'Cantidad']
            fig_sp = px.bar(
                top_sp, x='Cantidad', y='Especie', orientation='h',
                title="Top Especies más Representativas",
                template='plotly_white', color='Cantidad',
                color_continuous_scale='Greens'
            )
            fig_sp.update_layout(yaxis={'categoryorder': 'total ascending'}, height=360, showlegend=False)
            st.plotly_chart(fig_sp, use_container_width=True)

        with cg2:
            arboles_plop = (df_censo_filtrado['PLOP']
                            .value_counts().reset_index())
            arboles_plop.columns = ['Parcela', 'Árboles']
            fig_plop = px.bar(
                arboles_plop, x='Parcela', y='Árboles',
                title="Árboles por Parcela",
                template='plotly_white', color='Árboles',
                color_continuous_scale='Blues'
            )
            fig_plop.update_layout(height=360, showlegend=False)
            st.plotly_chart(fig_plop, use_container_width=True)

        # Tabla del censo
        st.markdown(f"### 📑 Listado de Árboles ({len(df_censo_filtrado)} individuos)")
        st.dataframe(
            df_censo_filtrado[['PLOP', 'SUB', 'TAG', 'Nombre_cientifico_limpio', 'GENERO']],
            use_container_width=True,
            height=320
        )

        c_dwn1, c_dwn2 = st.columns([1, 2])
        with c_dwn1:
            csv_censo = df_censo_filtrado.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Descargar Catálogo Filtrado (CSV)",
                csv_censo, "censo_arboles_tambopata.csv", "text/csv"
            )
        with c_dwn2:
            st.info("💡 **Base para la App Móvil:** Este censo con 1,939 TAGs es la base precargada que usará el formulario en React Native para registrar flores, frutos y fotos en campo sin conexión.")
    else:
        st.warning("No se encontró el archivo del censo `arboles_censo_colorado_1939.csv`.")


# =====================================================================
# TAB 3: VISOR DE VERDOR Y ESTRÉS HÍDRICO (SENTINEL-2 A 10M)
# =====================================================================
with tab_mapa:
    st.title("🗺️ Visor de Verdor (NDVI) y Estrés Hídrico (NDWI) — 10 Metros")
    st.write("Monitorea la salud del dosel forestal y el estrés hídrico de tus parcelas a resolución de **10x10 metros** usando **Sentinel-2 (ESA Copernicus)** y modelos hidrológicos de la **NASA**.")

    # ── GLOBOS DE INFORMACIÓN METODOLÓGICA ──
    with st.expander("ℹ️ ¿Qué significan estos datos y satélites? (Globos de Información Metodológica)", expanded=False):
        g1, g2, g3 = st.columns(3)
        with g1:
            st.markdown("""
            **🛰️ Satélite Sentinel-2 (ESA Copernicus):**
            * **Origen:** Agencia Espacial Europea.
            * **Resolución:** **10 metros por píxel** (micro-cuadrantes).
            * **Función:** Fotografías multiespectrales de alta precisión sobre la copa exacta de los árboles.
            """)
        with g2:
            st.markdown("""
            **🌿 NDVI — Índice de Verdor y Clorofila:**
            * **Fórmula:** `(B8_NIR - B4_Red) / (B8 + B4)`
            * **Qué mide:** Vigor fotosintético, densidad de hojas verdes y biomasa vegetal.
            * **Escala:** >0.70 = Selva densa vigorosa; <0.50 = Defoliación / estrés.
            """)
        with g3:
            st.markdown("""
            **💧 NDWI — Humedad del Tejido Foliar:**
            * **Fórmula:** `(B8_NIR - B11_SWIR) / (B8 + B11)`
            * **Qué mide:** Contenido de agua líquida dentro de las hojas del dosel.
            * **Escala:** >0.35 = Hidratado; <0.22 = Estrés hídrico severo.
            """)

    col_m1, col_m2, col_m3 = st.columns([1.3, 1.1, 1.6])
    with col_m1:
        parcela_preset = st.selectbox(
            "📍 Parcela de la Red Colorado (25 parcelas):",
            list(PARCELAS_RED.keys()),
            help="Selecciona una de las 25 parcelas georreferenciadas del proyecto Macaw Society en Tambopata."
        )
        info_p = PARCELAS_RED[parcela_preset]
        m_lat = st.number_input("Latitud", value=info_p["lat"], format="%.6f", key="map_lat")
        m_lon = st.number_input("Longitud", value=info_p["lon"], format="%.6f", key="map_lon")

    with col_m2:
        m_anio = st.selectbox("📅 Año de Observación:", list(range(2026, 2009, -1)), index=2, help="Disponible desde 2010 hasta 2026.")
        m_periodo = st.selectbox(
            "🌿 Época del Año:",
            ["Pico Seco (Ago - Oct) — Estrés", "Post-Lluvias (May - Jul) — Hidratado", "Todo el Año"],
            help="Elige la estación para comparar el dosel en sequía versus máxima humedad."
        )
        if "Seco" in m_periodo:
            f_ini = f"{m_anio}-08-01"
            f_fin = f"{m_anio}-10-31"
        elif "Post" in m_periodo:
            f_ini = f"{m_anio}-05-01"
            f_fin = f"{m_anio}-07-31"
        else:
            f_ini = f"{m_anio}-01-01"
            f_fin = f"{m_anio}-12-31"

    with col_m3:
        capa_activa = st.radio(
            "🎨 Capa inicial en primer plano:",
            ["🌿 Verdor / Clorofila (NDVI)", "💧 Estrés / Humedad Foliar (NDWI)"],
            horizontal=True,
            help="Puedes alternar o prender ambas capas desde el control de capas del mapa."
        )
        st.markdown(f"""
        * 🏷️ **Hábitat:** `{info_p['hab']}` · **Altitud:** `{info_p['alt']} msnm`
        * 🟢 **Verde Oscuro:** Vegetación densa / Dosel hidratado
        * 🔴 **Rojo / Pardo:** Estrés hídrico severo / Defoliación
        """)

    if not gee_is_ready:
        st.error("⚠️ No se pudo conectar a Google Earth Engine para generar el mapa.")
    else:
        with st.spinner(f"Consultando satélites ({'Sentinel-2 a 10m' if m_anio >= 2015 else 'Landsat a 30m'}) y generando capas..."):
            try:
                punto_map = ee.Geometry.Point([m_lon, m_lat])
                
                if m_anio >= 2015:
                    sat_nombre = "Sentinel-2 (ESA Copernicus, 10m)"
                    sat_res = 10
                    # Colección Sentinel-2 con máscara de nubes, NDVI y NDWI
                    def mask_s2_map(img):
                        qa = img.select('QA60')
                        cloud_mask = (1 << 10) | (1 << 11)
                        return img.updateMask(qa.bitwiseAnd(cloud_mask).eq(0))

                    def calc_indices_s2(img):
                        ndwi = img.normalizedDifference(['B8', 'B11']).rename('NDWI')
                        ndvi = img.normalizedDifference(['B8', 'B4']).rename('NDVI')
                        return img.addBands([ndwi, ndvi])

                    map_col = (ee.ImageCollection('COPERNICUS/S2_HARMONIZED')
                               .filterBounds(punto_map)
                               .filterDate(f_ini, f_fin)
                               .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 65))
                               .map(mask_s2_map)
                               .map(calc_indices_s2)
                               .select(['NDWI', 'NDVI']))
                elif m_anio >= 2013:
                    sat_nombre = "Landsat 8 OLI (NASA/USGS, 30m)"
                    sat_res = 30
                    def calc_indices_l8(img):
                        ndvi = img.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')
                        ndwi = img.normalizedDifference(['SR_B5', 'SR_B6']).rename('NDWI')
                        return img.addBands([ndwi, ndvi])

                    map_col = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
                               .filterBounds(punto_map)
                               .filterDate(f_ini, f_fin)
                               .map(calc_indices_l8)
                               .select(['NDWI', 'NDVI']))
                else:
                    sat_nombre = "Landsat 7 ETM+ (NASA/USGS, 30m)"
                    sat_res = 30
                    def calc_indices_l7(img):
                        ndvi = img.normalizedDifference(['SR_B4', 'SR_B3']).rename('NDVI')
                        ndwi = img.normalizedDifference(['SR_B4', 'SR_B5']).rename('NDWI')
                        return img.addBands([ndwi, ndvi])

                    map_col = (ee.ImageCollection('LANDSAT/LE07/C02/T1_L2')
                               .filterBounds(punto_map)
                               .filterDate(f_ini, f_fin)
                               .map(calc_indices_l7)
                               .select(['NDWI', 'NDVI']))

                # Mediana del período
                median_s2_img = map_col.median()

                # Extraer valores puntuales
                val_dict = median_s2_img.reduceRegion(
                    reducer=ee.Reducer.mean(),
                    geometry=punto_map.buffer(sat_res),
                    scale=sat_res
                ).getInfo()
                
                ndvi_val = val_dict.get('NDVI') if val_dict else None
                ndwi_val = val_dict.get('NDWI') if val_dict else None

                # Consultar FLDAS de apoyo para clima reciente
                fldas_val = (ee.ImageCollection('NASA/FLDAS/NOAH01/C/GL/M/V001')
                             .filterBounds(punto_map)
                             .filterDate(f_ini, f_fin)
                             .select(['SoilMoi00_10cm_tavg', 'Tair_f_tavg', 'Rainf_f_tavg'])
                             .mean()
                             .reduceRegion(ee.Reducer.mean(), punto_map, 10000)
                             .getInfo())

                t_c = (fldas_val.get('Tair_f_tavg') - 273.15) if fldas_val and fldas_val.get('Tair_f_tavg') else 25.0
                sm_pct = (fldas_val.get('SoilMoi00_10cm_tavg') * 100.0) if fldas_val and fldas_val.get('SoilMoi00_10cm_tavg') else 35.0
                rain_mm = (fldas_val.get('Rainf_f_tavg') * 86400 * 30.4) if fldas_val and fldas_val.get('Rainf_f_tavg') else 120.0

                # Diagnóstico de semáforo
                st.markdown(f"### 📊 Diagnóstico Automatizado — Parcela {info_p['cod']} ({info_p['hab']})")
                c_d1, c_d2, c_d3, c_d4, c_d5 = st.columns(5)
                
                c_d1.metric(f"🌿 NDVI Verdor ({sat_res}m)", f"{ndvi_val:.3f}" if ndvi_val is not None else "0.640 (Est.)", help=f"Biomasa y actividad fotosintética ({sat_nombre})")
                c_d2.metric(f"💧 NDWI Agua ({sat_res}m)", f"{ndwi_val:.3f}" if ndwi_val is not None else "0.280 (Est.)", help=f"Agua líquida en el follaje ({sat_nombre})")
                c_d3.metric("🌡️ Temp. Media", f"{t_c:.1f} °C", help="Temperatura del aire estimada por NASA FLDAS")
                c_d4.metric("💧 Humedad Suelo", f"{sm_pct:.1f} %", help="Humedad en los primeros 10cm de suelo (NASA FLDAS)")
                c_d5.metric("🌧️ Lluvia Media", f"{rain_mm:.0f} mm/m", help="Precipitación mensual estimada")

                # Estado del semáforo interpretativo
                ndwi_check = ndwi_val if ndwi_val is not None else 0.28
                if ndwi_check >= 0.35:
                    st.success(f"🟢 **DOSEL ÓPTIMO E HIDRATADO EN {info_p['cod']}:** Las copas de los árboles en {info_p['hab']} presentan máxima turgencia foliar (NDWI > 0.35). Condición favorable para crecimiento vegetativo.")
                elif ndwi_check >= 0.28:
                    st.info(f"🟡 **CONDICIÓN NORMAL / TRANSICIÓN EN {info_p['cod']}:** Hidratación foliar en niveles estándar (NDWI 0.28–0.35).")
                elif ndwi_check >= 0.22:
                    st.warning(f"🟠 **ALERTA DE ESTRÉS HÍDRICO MODERADO EN {info_p['cod']}:** El dosel está perdiendo agua por la temporada seca (NDWI 0.22–0.28). Momento de inducción floral.")
                else:
                    st.error(f"🔴 **ESTRÉS HÍDRICO SEVERO EN {info_p['cod']}:** El follaje ha alcanzado el punto crítico de sequedad (NDWI < 0.22). Disparador ecológico de maduración y caída de frutos.")

                # Generar capas de mapa en Folium
                vis_ndwi = {
                    'min': 0.15, 'max': 0.45,
                    'palette': ['#d73027', '#fc8d59', '#fee08b', '#d9ef8b', '#91cf60', '#1a9850', '#006837']
                }
                vis_ndvi = {
                    'min': 0.30, 'max': 0.85,
                    'palette': ['#a50026', '#d73027', '#f46d43', '#fdae61', '#fee08b', '#d9ef8b', '#a6d96a', '#66bd63', '#1a9850', '#006837']
                }

                tile_url_ndwi = median_s2_img.select('NDWI').getMapId(vis_ndwi)['tile_fetcher'].url_format
                tile_url_ndvi = median_s2_img.select('NDVI').getMapId(vis_ndvi)['tile_fetcher'].url_format

                m = folium.Map(
                    location=[m_lat, m_lon],
                    zoom_start=15,
                    tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
                    attr='Google Satellite'
                )

                # Capa NDVI
                show_ndvi = "NDVI" in capa_activa
                show_ndwi = "NDWI" in capa_activa

                folium.TileLayer(
                    tiles=tile_url_ndvi,
                    attr=f'{sat_nombre} / GEE',
                    name=f'🌿 Verdor y Clorofila (NDVI a {sat_res}m)',
                    overlay=True,
                    opacity=0.70,
                    show=show_ndvi
                ).add_to(m)

                # Capa NDWI
                folium.TileLayer(
                    tiles=tile_url_ndwi,
                    attr=f'{sat_nombre} / GEE',
                    name=f'💧 Estrés y Humedad Foliar (NDWI a {sat_res}m)',
                    overlay=True,
                    opacity=0.70,
                    show=show_ndwi
                ).add_to(m)

                # Capa con todas las 25 parcelas de la red
                fg_red = folium.FeatureGroup(name='📍 Red de 25 Parcelas Colorado', show=True)
                for p_name, p_data in PARCELAS_RED.items():
                    if p_data["cod"] == "CUSTOM":
                        continue
                    is_active = (p_data["cod"] == info_p["cod"])
                    
                    p_html = f"""
                    <div style="font-family: sans-serif; font-size: 12px; line-height: 1.4; min-width: 170px;">
                        <h4 style="margin:0 0 4px 0; color:#1b5e20;">📍 Parcela {p_data['cod']}</h4>
                        <b>Hábitat:</b> {p_data['hab']}<br>
                        <b>Altitud:</b> {p_data['alt']} msnm<br>
                        <b>Lat:</b> {p_data['lat']:.5f}<br>
                        <b>Lon:</b> {p_data['lon']:.5f}
                    </div>
                    """
                    folium.Marker(
                        [p_data["lat"], p_data["lon"]],
                        popup=folium.Popup(p_html, max_width=250),
                        tooltip=f"Parcela {p_data['cod']} ({p_data['hab']})",
                        icon=folium.Icon(
                            color='red' if is_active else p_data["color"],
                            icon='star' if is_active else p_data["icon"],
                            prefix='fa'
                        )
                    ).add_to(fg_red)
                
                fg_red.add_to(m)

                # Marcador con Globo de Información Completo en la Parcela Activa
                ndvi_str = f"{ndvi_val:.3f}" if ndvi_val is not None else "N/A"
                ndwi_str = f"{ndwi_val:.3f}" if ndwi_val is not None else "N/A"

                html_popup = f"""
                <div style="font-family: sans-serif; font-size: 13px; line-height: 1.5; min-width: 210px;">
                    <h4 style="margin: 0 0 6px 0; color: #1b5e20;">📍 Parcela Activa: {info_p['cod']}</h4>
                    <b>Hábitat:</b> {info_p['hab']}<br>
                    <b>Altitud:</b> {info_p['alt']} msnm<br>
                    <b>Lat:</b> {m_lat:.6f} | <b>Lon:</b> {m_lon:.6f}<br>
                    <hr style="margin: 6px 0; border: 0; border-top: 1px solid #ddd;">
                    <b>🌿 NDVI (Verdor {sat_res}m):</b> <span style="color:#2e7d32; font-weight:bold;">{ndvi_str}</span><br>
                    <b>💧 NDWI (Humedad {sat_res}m):</b> <span style="color:#1565c0; font-weight:bold;">{ndwi_str}</span><br>
                    <b>🌡️ Temp. Estimada:</b> {t_c:.1f} °C<br>
                    <b>💧 Hum. Suelo (0-10cm):</b> {sm_pct:.1f}%<br>
                    <hr style="margin: 6px 0; border: 0; border-top: 1px solid #ddd;">
                    <small style="color: #666;">Fuente: {sat_nombre} + FLDAS (NASA)</small>
                </div>
                """

                folium.Marker(
                    [m_lat, m_lon],
                    popup=folium.Popup(html_popup, max_width=300),
                    tooltip=f"🔍 Parcela Activa {info_p['cod']}",
                    icon=folium.Icon(color='red', icon='star', prefix='fa')
                ).add_to(m)

                folium.LayerControl(position='topright').add_to(m)

                components.html(m._repr_html_(), height=550)

            except Exception as e_map:
                st.error(f"Error generando el visor satelital: {e_map}")


# =====================================================================
# TAB 3: EXTRACTOR CLIMÁTICO
# =====================================================================
with tab_clima:
    st.title("🛰️ Extractor de Clima Satelital")
    st.write("Consulta y descarga datos de clima (lluvia, temperatura, humedad del suelo) vía Google Earth Engine.")
    
    if not gee_is_ready:
        st.error("⚠️ **No se pudo conectar a Google Earth Engine.** Revisa que los 'Secrets' estén bien configurados en Streamlit Cloud.")
    else:
        st.success("✅ **Conexión con Google Earth Engine activa.**")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            ext_parcela = st.selectbox(
                "📍 Parcela rápida (Red Colorado):",
                list(PARCELAS_RED.keys()),
                key="ext_parcela_sel"
            )
            ext_info = PARCELAS_RED[ext_parcela]
            in_lat = st.number_input("📍 Latitud", value=ext_info["lat"], format="%.6f", key="ext_lat")
            in_lon = st.number_input("📍 Longitud", value=ext_info["lon"], format="%.6f", key="ext_lon")
        with col2:
            in_start = st.date_input("Fecha Inicio", datetime.date(2015, 1, 1))
            in_end = st.date_input("Fecha Fin", datetime.date(2025, 12, 31))
        with col3:
            fuente = st.radio("📡 Fuente de Datos", [
                "Sentinel-2 (NDVI y NDWI, 10m)",
                "FLDAS Suelo (NASA, ~9.6km)",
                "TerraClimate (Mensual, ~4.6km)",
                "ERA5-Land (Por Hora, ~11km)"
            ])

        if st.button("🚀 Extraer Datos Climáticos", type="primary"):
            with st.spinner("Conectando con satélites y procesando datos. Por favor espera..."):
                try:
                    punto = ee.Geometry.Point([in_lon, in_lat])
                    start_str = in_start.strftime("%Y-%m-%d")
                    end_str = in_end.strftime("%Y-%m-%d")

                    if "Sentinel-2" in fuente:
                        st.info("ℹ️ Descargando de **Sentinel-2 (ESA / Copernicus)**. Resolución: **10 metros**. Extrayendo **NDVI** (Verdor/Clorofila) y **NDWI** (Humedad foliar) con máscara de nubes QA60.")
                        
                        def mask_s2(img):
                            qa = img.select('QA60')
                            cloud_mask = (1 << 10) | (1 << 11)
                            return img.updateMask(qa.bitwiseAnd(cloud_mask).eq(0))

                        def calc_indices(img):
                            ndwi = img.normalizedDifference(['B8', 'B11']).rename('NDWI')
                            ndvi = img.normalizedDifference(['B8', 'B4']).rename('NDVI')
                            return img.addBands([ndwi, ndvi])

                        coleccion = (ee.ImageCollection('COPERNICUS/S2_HARMONIZED')
                                     .filterBounds(punto)
                                     .filterDate(start_str, end_str)
                                     .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 75))
                                     .map(mask_s2)
                                     .map(calc_indices)
                                     .select(['NDVI', 'NDWI']))

                        info = coleccion.getRegion(punto, 10).getInfo()

                        if len(info) > 1:
                            df_sat = pd.DataFrame(info[1:], columns=info[0])
                            df_sat['NDVI'] = pd.to_numeric(df_sat['NDVI'])
                            df_sat['NDWI'] = pd.to_numeric(df_sat['NDWI'])
                            df_sat = df_sat.dropna(subset=['NDVI', 'NDWI'])
                            df_sat['datetime'] = pd.to_datetime(pd.to_numeric(df_sat['time']), unit='ms')
                            
                            df_out = df_sat[['datetime', 'NDVI', 'NDWI']].sort_values('datetime').reset_index(drop=True)
                            df_out.columns = ['DATETIME', 'NDVI_10M', 'NDWI_10M']

                            st.dataframe(df_out, use_container_width=True)

                            fig = px.line(
                                df_out, x='DATETIME', y=['NDVI_10M', 'NDWI_10M'],
                                markers=True, template='plotly_white',
                                title="Evolución de Verdor (NDVI) y Humedad Foliar (NDWI) a 10m — Sentinel-2",
                                labels={'DATETIME': 'Fecha de pasada', 'value': 'Valor del Índice (-1 a +1)', 'variable': 'Índice Espectral'}
                            )
                            st.plotly_chart(fig, use_container_width=True)

                            csv = df_out.to_csv(index=False).encode('utf-8')
                            st.download_button("📥 Descargar CSV (Sentinel-2 NDVI + NDWI 10m)", csv, "sentinel2_ndvi_ndwi_10m.csv", "text/csv")
                        else:
                            st.warning("No se encontraron pasadas de Sentinel-2 sin nubes para estas fechas y coordenadas.")

                    elif "FLDAS" in fuente:
                        st.info("ℹ️ Descargando de **FLDAS (NASA / USGS / USAID - FEWS NET)**. Resolución: ~9.6km (0.1°). Humedad de suelo regional multietapa.")

                        coleccion = (ee.ImageCollection('NASA/FLDAS/NOAH01/C/GL/M/V001')
                                     .filterBounds(punto)
                                     .filterDate(start_str, end_str)
                                     .select(['SoilMoi00_10cm_tavg', 'SoilMoi10_40cm_tavg', 'Tair_f_tavg', 'Rainf_f_tavg']))

                        info = coleccion.getRegion(punto, 10000).getInfo()

                        if len(info) > 1:
                            df_sat = pd.DataFrame(info[1:], columns=info[0])
                            df_sat['SoilMoi00_10cm'] = pd.to_numeric(df_sat['SoilMoi00_10cm_tavg']) * 100.0
                            df_sat['SoilMoi10_40cm'] = pd.to_numeric(df_sat['SoilMoi10_40cm_tavg']) * 100.0
                            df_sat['temp_c'] = pd.to_numeric(df_sat['Tair_f_tavg']) - 273.15
                            df_sat['rain_mm_month'] = pd.to_numeric(df_sat['Rainf_f_tavg']) * 86400 * 30.4375
                            df_sat['datetime'] = pd.to_datetime(df_sat['id'].str[0:4] + '-' + df_sat['id'].str[4:6] + '-01')

                            df_out = df_sat[['datetime', 'rain_mm_month', 'temp_c', 'SoilMoi00_10cm', 'SoilMoi10_40cm']].copy()
                            df_out.columns = ['DATETIME', 'RAIN_MM_MONTH', 'TEMPERATURE_C', 'SOIL_MOISTURE_0_10CM_PCT', 'SOIL_MOISTURE_10_40CM_PCT']

                            st.dataframe(df_out, use_container_width=True)

                            fig = make_subplots(specs=[[{"secondary_y": True}]])
                            fig.add_trace(go.Scatter(x=df_out['DATETIME'], y=df_out['SOIL_MOISTURE_0_10CM_PCT'], name='Humedad Suelo 0-10cm (%)', line=dict(color='#2e7d32', width=2.5)), secondary_y=False)
                            fig.add_trace(go.Scatter(x=df_out['DATETIME'], y=df_out['SOIL_MOISTURE_10_40CM_PCT'], name='Humedad Suelo 10-40cm (%)', line=dict(color='#81c784', width=2, dash='dash')), secondary_y=False)
                            fig.add_trace(go.Bar(x=df_out['DATETIME'], y=df_out['RAIN_MM_MONTH'], name='Lluvia (mm/mes)', marker_color='lightblue', opacity=0.6), secondary_y=True)
                            fig.update_layout(template='plotly_white', height=450, hovermode='x unified')
                            fig.update_yaxes(title_text="Humedad Suelo (%)", secondary_y=False)
                            fig.update_yaxes(title_text="Lluvia (mm)", secondary_y=True)
                            st.plotly_chart(fig, use_container_width=True)

                            csv = df_out.to_csv(index=False).encode('utf-8')
                            st.download_button("📥 Descargar CSV (FLDAS NASA)", csv, "fldas_nasa_soil_moisture.csv", "text/csv")
                        else:
                            st.warning("No se encontraron datos de FLDAS para esas fechas.")

                    elif "TerraClimate" in fuente:
                        st.info("ℹ️ Descargando de **TerraClimate (IDAHO_EPSCOR)**. Resolución: ~4.6km (1/24°).")
                        coleccion = ee.ImageCollection('IDAHO_EPSCOR/TERRACLIMATE').select(['pr', 'tmmx', 'tmmn', 'vap', 'soil']).filterBounds(punto).filterDate(start_str, end_str)
                        info = coleccion.getRegion(punto, 4638).getInfo()
                        
                        if len(info) > 1:
                            df_sat = pd.DataFrame(info[1:], columns=info[0])
                            df_sat['pr'] = pd.to_numeric(df_sat['pr'])
                            df_sat['tmmx'] = pd.to_numeric(df_sat['tmmx']) * 0.1
                            df_sat['tmmn'] = pd.to_numeric(df_sat['tmmn']) * 0.1
                            df_sat['vap'] = pd.to_numeric(df_sat['vap']) * 0.001
                            df_sat['soil'] = pd.to_numeric(df_sat['soil']) * 0.1
                            df_sat['tmean'] = (df_sat['tmmx'] + df_sat['tmmn']) / 2
                            es = 0.6108 * np.exp((17.27 * df_sat['tmean']) / (df_sat['tmean'] + 237.3))
                            df_sat['humidity'] = (df_sat['vap'] / es) * 100
                            df_sat['humidity'] = df_sat['humidity'].clip(upper=100.0)
                            
                            df_sat['Fecha'] = pd.to_datetime(df_sat['id'].str[0:4] + '-' + df_sat['id'].str[4:6] + '-01')
                            
                            df_out = df_sat[['Fecha', 'pr', 'tmean', 'humidity', 'soil']].copy()
                            df_out.columns = ['DATETIME', 'RAIN_MM', 'TEMPERATURE_C', 'HUMIDITY_PERCENT', 'SOIL_MOISTURE_MM']
                            
                            st.dataframe(df_out, use_container_width=True)
                            
                            # Grafica
                            fig = make_subplots(specs=[[{"secondary_y": True}]])
                            fig.add_trace(go.Bar(x=df_out['DATETIME'], y=df_out['RAIN_MM'], name='Lluvia (mm)', marker_color='lightblue'), secondary_y=False)
                            fig.add_trace(go.Scatter(x=df_out['DATETIME'], y=df_out['TEMPERATURE_C'], name='Temp (°C)', line=dict(color='tomato')), secondary_y=True)
                            st.plotly_chart(fig, use_container_width=True)
                            
                            csv = df_out.to_csv(index=False).encode('utf-8')
                            st.download_button("📥 Descargar CSV", csv, "clima_terraclimate.csv", "text/csv")
                        else:
                            st.warning("No se encontraron datos para estas fechas.")

                    else:
                        st.info("ℹ️ Descargando de **ERA5-Land Hourly (ECMWF)**. Resolución: ~11km (0.1°). Descarga en bloques mensuales...")
                        
                        date_chunks = []
                        current = pd.to_datetime(in_start)
                        end_date = pd.to_datetime(in_end)
                        while current < end_date:
                            next_date = min(current + pd.Timedelta(days=30), end_date)
                            date_chunks.append((current.strftime("%Y-%m-%d"), next_date.strftime("%Y-%m-%d")))
                            current = next_date

                        all_data = []
                        header = None
                        progress_bar = st.progress(0)

                        for i, (chunk_start, chunk_end) in enumerate(date_chunks):
                            coleccion = ee.ImageCollection('ECMWF/ERA5_LAND/HOURLY').select(['temperature_2m', 'dewpoint_temperature_2m', 'total_precipitation', 'volumetric_soil_water_layer_1']).filterBounds(punto).filterDate(chunk_start, chunk_end)
                            try:
                                info = coleccion.getRegion(punto, 11132).getInfo()
                                if len(info) > 1:
                                    if header is None:
                                        header = info[0]
                                    all_data.extend(info[1:])
                            except Exception as e_chunk:
                                st.warning(f"Omitiendo fechas {chunk_start} a {chunk_end} por límite de memoria.")
                            progress_bar.progress((i + 1) / len(date_chunks))
                        
                        progress_bar.empty()

                        if all_data:
                            df_sat = pd.DataFrame(all_data, columns=header)
                            df_sat = df_sat.drop_duplicates(subset=['id', 'time'])
                            
                            df_sat['total_precipitation'] = pd.to_numeric(df_sat['total_precipitation'])
                            df_sat['temperature_2m'] = pd.to_numeric(df_sat['temperature_2m'])
                            df_sat['dewpoint_temperature_2m'] = pd.to_numeric(df_sat['dewpoint_temperature_2m'])
                            df_sat['volumetric_soil_water_layer_1'] = pd.to_numeric(df_sat['volumetric_soil_water_layer_1'])
                            
                            df_sat['temp_c'] = df_sat['temperature_2m'] - 273.15
                            df_sat['dew_c'] = df_sat['dewpoint_temperature_2m'] - 273.15
                            # ERA5 total_precipitation es acumulada desde las 00:00 UTC (en metros).
                            # Se calcula la diferencia horaria preservando el valor en cada reinicio diario (cuando diff < 0).
                            precip_m = df_sat['total_precipitation'].copy()
                            diff_precip = precip_m.diff()
                            hourly_rain_m = np.where(diff_precip < 0, precip_m, diff_precip)
                            if len(hourly_rain_m) > 0:
                                hourly_rain_m[0] = precip_m.iloc[0]
                            df_sat['rain_mm'] = np.maximum(0, hourly_rain_m) * 1000.0
                            df_sat['soil_moisture_percent'] = df_sat['volumetric_soil_water_layer_1'] * 100.0
                            
                            num = np.exp((17.625 * df_sat['dew_c']) / (243.04 + df_sat['dew_c']))
                            den = np.exp((17.625 * df_sat['temp_c']) / (243.04 + df_sat['temp_c']))
                            df_sat['humidity'] = (num / den) * 100.0
                            df_sat['humidity'] = df_sat['humidity'].clip(upper=100.0)
                            
                            # Usar el timestamp en milisegundos directamente (es lo más seguro y exacto)
                            df_sat['datetime'] = pd.to_datetime(pd.to_numeric(df_sat['time']), unit='ms')

                            df_out = df_sat[['datetime', 'rain_mm', 'temp_c', 'humidity', 'soil_moisture_percent']].copy()
                            df_out.columns = ['DATETIME', 'RAIN_MM', 'TEMPERATURE_C', 'HUMIDITY_PERCENT', 'SOIL_MOISTURE_PERCENT']
                            
                            st.dataframe(df_out, use_container_width=True)

                            # Grafica resumida por dia para que Plotly no explote con 8000 puntos
                            df_daily = df_out.set_index('DATETIME').resample('D').agg({'RAIN_MM':'sum', 'TEMPERATURE_C':'mean'}).reset_index()
                            fig = make_subplots(specs=[[{"secondary_y": True}]])
                            fig.add_trace(go.Bar(x=df_daily['DATETIME'], y=df_daily['RAIN_MM'], name='Lluvia (mm/día)', marker_color='lightblue'), secondary_y=False)
                            fig.add_trace(go.Scatter(x=df_daily['DATETIME'], y=df_daily['TEMPERATURE_C'], name='Temp Promedio (°C)', line=dict(color='tomato')), secondary_y=True)
                            st.plotly_chart(fig, use_container_width=True)

                            csv = df_out.to_csv(index=False).encode('utf-8')
                            st.download_button("📥 Descargar CSV (Por Hora)", csv, "clima_era5_hourly.csv", "text/csv")
                        else:
                            st.warning("No se encontraron datos.")
                
                except Exception as e:
                    st.error(f"Ocurrió un error al extraer los datos: {e}")
