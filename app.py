import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN GLOBAL
# ─────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Fenología Tambopata | Macaw Society",
    page_icon="🦜",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para una apariencia más profesional
st.markdown("""
<style>
    /* Fondo del sidebar */
    [data-testid="stSidebar"] {
        background-color: #1a2e1a;
    }
    [data-testid="stSidebar"] * {
        color: #d4e6d4 !important;
    }
    /* Estilo general */
    .block-container { padding-top: 1.5rem; }
    /* Tarjetas de métricas */
    [data-testid="metric-container"] {
        background-color: #f0f7f0;
        border: 1px solid #c3dfc3;
        border-radius: 10px;
        padding: 12px;
    }
    /* Títulos de secciones */
    h2 { color: #1a5c1a; border-bottom: 2px solid #4CAF50; padding-bottom: 6px; }
    h3 { color: #2d7a2d; }
    /* Caja de contexto */
    .context-box {
        background: linear-gradient(135deg, #1a3d1a, #2d5c2d);
        color: white;
        border-radius: 12px;
        padding: 20px 28px;
        margin-bottom: 24px;
    }
    .context-box h1 { color: #a8e6a8; font-size: 1.6rem; margin:0 0 6px 0; }
    .context-box p  { color: #d4f0d4; margin: 0; font-size: 0.97rem; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────
# DICCIONARIOS DE APOYO
# ─────────────────────────────────────────────────────────────────────
MESES = {1:'Ene',2:'Feb',3:'Mar',4:'Abr',5:'May',6:'Jun',
          7:'Jul',8:'Ago',9:'Sep',10:'Oct',11:'Nov',12:'Dic'}

FENOLOGIA_LABELS = {
    'RF': 'Fruto Maduro (RF)',
    'D':  'Fruto Diseminado (D)',
    'F':  'Flores (F)',
    'UF': 'Fruto Verde (UF)',
    'B':  'Botones Florales (B)'
}
FENOLOGIA_COLS = list(FENOLOGIA_LABELS.keys())

ESCALA_NOTA = """
📏 **Escala de Abundancia (Macaw Society):**  
`0` = Ausente · `1` = Escaso (1-10) · `2` = Moderado (10-100) · `3` = Abundante (100+)
"""

COLORES_ROL = {
    'Estrella Comercial - Frutal':         '#e67e22',
    'Estrella Comercial - Industrial':     '#e74c3c',
    'Ingeniero del Suelo - Fijador N':     '#27ae60',
    'Ingeniero del Suelo - Pionera':       '#2ecc71',
    'Caja Fuerte - Maderable':             '#8b4513',
    'Caja Fuerte - Maderable / Fijador N': '#d35400',
}

# ─────────────────────────────────────────────────────────────────────
# CARGA DE DATOS
# ─────────────────────────────────────────────────────────────────────
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
    # Llenar nulos para evitar 'undefined' en tablas y gráficos
    cols_categoricas = ['Rol_Agroforestal', 'GENERO_limpio', 'Nombre científico', 'FAMILY', 'HABITAT']
    for col in cols_categoricas:
        if col in df.columns:
            df[col] = df[col].fillna('Desconocido')
    return df

df_original = load_data()

# ─────────────────────────────────────────────────────────────────────
# CABECERA PRINCIPAL
# ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="context-box">
  <h1>🦜 Fenología Forestal en la Reserva Nacional de Tambopata</h1>
  <p>
    Base de datos fenológica histórica <strong>2010–2017</strong> · Proyecto <strong>Macaw Society</strong><br>
    Seguimiento mensual de especies forestales clave para la alimentación de guacamayos en 'colpa colorado' y su potencial en sistemas <strong>agroforestales sintrópicos</strong>.
  </p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────
# SIDEBAR – FILTROS
# ─────────────────────────────────────────────────────────────────────
st.sidebar.title("🔬 Filtros de Análisis")

# Filtro por año
anios = sorted(df_original['YEAR'].unique().tolist())
anio_sel = st.sidebar.multiselect("📅 Año (vacío = todos)", anios)
df = df_original[df_original['YEAR'].isin(anio_sel)] if anio_sel else df_original.copy()

# Filtro por Zona (Habitat)
zonas = sorted(df['HABITAT'].dropna().unique().tolist())
zona_sel = st.sidebar.multiselect("📍 Zona (Hábitat)", zonas, default=zonas)
df = df[df['HABITAT'].isin(zona_sel)] if zona_sel else df.copy()

# Filtro por Rol
roles = df['Rol_Agroforestal'].unique().tolist()
rol_sel = st.sidebar.multiselect("🌿 Rol Agroforestal", roles, default=roles)
df_f = df[df['Rol_Agroforestal'].isin(rol_sel)] if rol_sel else df.copy()

# Filtro por Género
generos = sorted(df_f['GENERO_limpio'].dropna().unique().tolist())
gen_sel = st.sidebar.multiselect("🔬 Género", generos)
if gen_sel:
    df_f = df_f[df_f['GENERO_limpio'].isin(gen_sel)]

# Filtro por Especie
especies = sorted(df_f['Nombre científico'].dropna().unique().tolist())
esp_sel = st.sidebar.multiselect("🌱 Especie (Nombre Científico)", especies)
if esp_sel:
    df_f = df_f[df_f['Nombre científico'].isin(esp_sel)]

# Agrupación
st.sidebar.markdown("---")
agrupar_labels = {
    'Rol Agroforestal': 'Rol_Agroforestal',
    'Género':           'GENERO_limpio',
    'Especie':          'Nombre científico'
}
agrupar_label = st.sidebar.radio("📊 Agrupar gráficos por:", list(agrupar_labels.keys()))
agrupar_por   = agrupar_labels[agrupar_label]

# Variable fenológica
st.sidebar.markdown("---")
metrica_label = st.sidebar.selectbox("🍃 Variable Fenológica:", list(FENOLOGIA_LABELS.values()))
metrica_col   = [k for k,v in FENOLOGIA_LABELS.items() if v == metrica_label][0]

st.sidebar.markdown(ESCALA_NOTA)

# ─────────────────────────────────────────────────────────────────────
# KPIs – TARJETAS DE RESUMEN
# ─────────────────────────────────────────────────────────────────────
st.subheader("📊 Resumen del Dataset Filtrado")
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("🗂️ Registros",     f"{len(df_f):,}")
k2.metric("🌳 Especies",       df_f['Nombre científico'].nunique())
k3.metric("🔬 Géneros",        df_f['GENERO_limpio'].nunique())
k4.metric("🏠 Familias",       df_f['FAMILY'].nunique())
k5.metric("📅 Años de datos",  df_f['YEAR'].nunique())

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────
# SECCIÓN 1 – EVOLUCIÓN TEMPORAL (Serie de tiempo)
# ─────────────────────────────────────────────────────────────────────
st.subheader(f"📈 Evolución Temporal de {metrica_label} (2010–2017)")
st.caption("Seguimiento mensual continuo de cada árbol marcado con placa (TAG) en la Reserva.")

df_evo = df_f.groupby(['Fecha', agrupar_por])[metrica_col].mean().reset_index()

fig_evo = px.line(
    df_evo, x='Fecha', y=metrica_col, color=agrupar_por,
    color_discrete_map=COLORES_ROL,
    labels={'Fecha': 'Fecha de Observación', metrica_col: 'Índice de Abundancia (0-3)'},
    template='plotly_white'
)
fig_evo.update_traces(line_width=2)
fig_evo.update_layout(
    title=None,
    legend_title=agrupar_label,
    hovermode='x unified'
)
st.plotly_chart(fig_evo, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────
# SECCIÓN 2 – ESTACIONALIDAD MENSUAL
# ─────────────────────────────────────────────────────────────────────
st.subheader(f"📅 Estacionalidad Mensual de {metrica_label}")
st.caption("¿En qué mes ocurre el pico? Promedio histórico de 7 años, desagregado por grupo.")

df_men = df_f.groupby(['MONTH', 'MONTH_LABEL', agrupar_por])[metrica_col].mean().reset_index()
df_men = df_men.sort_values('MONTH')

fig_men = px.bar(
    df_men, x='MONTH_LABEL', y=metrica_col, color=agrupar_por, barmode='group',
    color_discrete_map=COLORES_ROL,
    labels={'MONTH_LABEL': 'Mes', metrica_col: 'Índice Promedio (0-3)'},
    category_orders={'MONTH_LABEL': list(MESES.values())},
    template='plotly_white'
)
fig_men.update_layout(title=None, legend_title=agrupar_label)
st.plotly_chart(fig_men, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────
# SECCIÓN 3 – HEATMAP FENOLÓGICO (visión de artículo científico)
# ─────────────────────────────────────────────────────────────────────
st.subheader("🗓️ Calendario Fenológico (Heatmap por Género)")
st.caption("Vista de 'Figura Científica': intensidad de la variable por género y mes.")

df_heat = df_f.groupby(['GENERO_limpio', 'MONTH'])[metrica_col].mean().reset_index()
df_heat['Mes'] = df_heat['MONTH'].map(MESES)
pivot = df_heat.pivot_table(index='GENERO_limpio', columns='Mes', values=metrica_col)
pivot = pivot[[m for m in MESES.values() if m in pivot.columns]]

fig_heat = px.imshow(
    pivot,
    color_continuous_scale='YlOrRd',
    labels={'x': 'Mes', 'y': 'Género', 'color': 'Índice Promedio'},
    aspect='auto',
    template='plotly_white'
)
fig_heat.update_layout(title=None, coloraxis_colorbar_title='Índice (0-3)')
st.plotly_chart(fig_heat, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────
# SECCIÓN 4 – FENOLOGÍA VS CLIMA (Superpuesto)
# ─────────────────────────────────────────────────────────────────────
st.subheader("🌦️ Fenología vs. Clima (Paneles Separados)")
st.caption("Para evitar que la escala de la lluvia aplane los datos, aquí comparamos la fenología contra la lluvia y la temperatura en paneles separados.")

# Agrupar tanto clima como la métrica fenológica seleccionada
df_clima = df_f.groupby('MONTH')[['RAIN', 'TEMPERATURE', metrica_col]].mean().reset_index()
df_clima['Mes'] = df_clima['MONTH'].map(MESES)

fig_clima = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.12,
    specs=[[{"secondary_y": True}],
           [{"secondary_y": True}]]
)

# --- PANEL 1: Lluvia vs Fenología ---
fig_clima.add_trace(
    go.Bar(
        x=df_clima['Mes'], y=df_clima['RAIN'],
        name='Lluvia (mm)', marker_color='lightblue', opacity=0.7
    ),
    row=1, col=1, secondary_y=False,
)
fig_clima.add_trace(
    go.Scatter(
        x=df_clima['Mes'], y=df_clima[metrica_col],
        name=metrica_label, mode='lines+markers',
        line=dict(color='forestgreen', width=3)
    ),
    row=1, col=1, secondary_y=True,
)

# --- PANEL 2: Temperatura vs Fenología ---
fig_clima.add_trace(
    go.Scatter(
        x=df_clima['Mes'], y=df_clima['TEMPERATURE'],
        name='Temperatura (°C)', mode='lines+markers',
        line=dict(color='tomato', width=3)
    ),
    row=2, col=1, secondary_y=False,
)
# (Re-dibujamos la fenología para el panel 2 sin repetir en la leyenda)
fig_clima.add_trace(
    go.Scatter(
        x=df_clima['Mes'], y=df_clima[metrica_col],
        name=metrica_label, mode='lines+markers',
        line=dict(color='forestgreen', width=3),
        showlegend=False
    ),
    row=2, col=1, secondary_y=True,
)

fig_clima.update_layout(
    height=600,
    template='plotly_white',
    hovermode='x unified',
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
    xaxis2=dict(categoryorder='array', categoryarray=list(MESES.values()))
)

# Configurar rangos y títulos
fig_clima.update_yaxes(title_text="Lluvia (mm)", row=1, col=1, secondary_y=False)
fig_clima.update_yaxes(title_text="Índice (0-3)", row=1, col=1, secondary_y=True, range=[0, 3.2])

fig_clima.update_yaxes(title_text="Temp (°C)", row=2, col=1, secondary_y=False)
fig_clima.update_yaxes(title_text="Índice (0-3)", row=2, col=1, secondary_y=True, range=[0, 3.2])

st.plotly_chart(fig_clima, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────
# SECCIÓN 5 – TABLA DE ESPECIES POR ROL
# ─────────────────────────────────────────────────────────────────────
st.subheader("🌿 Catálogo de Especies Analizadas")
st.caption("Lista de los géneros y especies identificados con su rol agroforestal y valor estratégico.")

tabla_esp = (df_f.groupby(['Rol_Agroforestal', 'GENERO_limpio', 'Nombre científico', 'FAMILY'])
             .size().reset_index(name='Nº Observaciones')
             .sort_values(['Rol_Agroforestal', 'Nº Observaciones'], ascending=[True, False]))
tabla_esp.columns = ['Rol Agroforestal', 'Género', 'Nombre Científico', 'Familia', 'Nº Observaciones']

st.dataframe(
    tabla_esp,
    use_container_width=True,
    height=350,
    hide_index=True
)

# ─────────────────────────────────────────────────────────────────────
# DATOS CRUDOS (expandible)
# ─────────────────────────────────────────────────────────────────────
with st.expander("🔎 Ver datos crudos (primeros 100 registros)"):
    st.dataframe(df_f.head(100), use_container_width=True)
