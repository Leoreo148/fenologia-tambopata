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
# TABS PRINCIPALES
# ─────────────────────────────────────────────────────────────────────
tab_feno, tab_clima = st.tabs(["🌱 Fenología Forestal", "🛰️ Extractor Climático Satelital"])

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
    st.subheader("🌦️ Fenología vs. Clima (Promedio Histórico Mensual)")
    df_clima = df_f.groupby('MONTH')[['RAIN', 'TEMPERATURE', metrica_col]].mean().reset_index()
    df_clima['Mes'] = df_clima['MONTH'].map(MESES)
    fig_clima = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.12, specs=[[{"secondary_y": True}], [{"secondary_y": True}]])
    fig_clima.add_trace(go.Bar(x=df_clima['Mes'], y=df_clima['RAIN'], name='Lluvia (mm)', marker_color='lightblue'), row=1, col=1, secondary_y=False)
    fig_clima.add_trace(go.Scatter(x=df_clima['Mes'], y=df_clima[metrica_col], name=metrica_label, line=dict(color='forestgreen', width=3)), row=1, col=1, secondary_y=True)
    fig_clima.add_trace(go.Scatter(x=df_clima['Mes'], y=df_clima['TEMPERATURE'], name='Temp (°C)', line=dict(color='tomato', width=3)), row=2, col=1, secondary_y=False)
    fig_clima.add_trace(go.Scatter(x=df_clima['Mes'], y=df_clima[metrica_col], name=metrica_label, line=dict(color='forestgreen', width=3), showlegend=False), row=2, col=1, secondary_y=True)
    fig_clima.update_layout(height=600, template='plotly_white', hovermode='x unified')
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
        df_sp_clima = df_sp.groupby('MONTH').agg(
            Fenología=(col_resp, 'mean'),
            Lluvia_mm=('RAIN', 'mean'),
            Temperatura_C=('TEMPERATURE', 'mean')
        ).reset_index()
        df_sp_clima['Mes'] = df_sp_clima['MONTH'].map(MESES)

        fig_cruce = make_subplots(specs=[[{"secondary_y": True}]])
        fig_cruce.add_trace(
            go.Bar(x=df_sp_clima['Mes'], y=df_sp_clima['Fenología'],
                   name=label_resp, marker_color='#2d7a2d', opacity=0.8),
            secondary_y=False
        )
        fig_cruce.add_trace(
            go.Scatter(x=df_sp_clima['Mes'], y=df_sp_clima['Lluvia_mm'],
                       name='Lluvia (mm)', line=dict(color='#3498db', width=3)),
            secondary_y=True
        )
        fig_cruce.add_trace(
            go.Scatter(x=df_sp_clima['Mes'], y=df_sp_clima['Temperatura_C'],
                       name='Temperatura (°C)', line=dict(color='tomato', width=3, dash='dot')),
            secondary_y=True
        )
        fig_cruce.update_layout(
            height=420, template='plotly_white', hovermode='x unified',
            xaxis={'categoryorder': 'array', 'categoryarray': list(MESES.values())},
            legend=dict(orientation='h', yanchor='bottom', y=1.02)
        )
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


# =====================================================================
# TAB 2: EXTRACTOR CLIMÁTICO
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
            in_lat = st.number_input("📍 Latitud", value=-12.83, format="%.5f")
            in_lon = st.number_input("📍 Longitud", value=-69.29, format="%.5f")
        with col2:
            in_start = st.date_input("Fecha Inicio", datetime.date(2025, 1, 1))
            in_end = st.date_input("Fecha Fin", datetime.date(2025, 12, 31))
        with col3:
            fuente = st.radio("📡 Fuente de Datos", ["TerraClimate (Mensual, ~4.6km)", "ERA5-Land (Por Hora, ~11km)"])

        if st.button("🚀 Extraer Datos Climáticos", type="primary"):
            with st.spinner("Conectando con satélites y descargando datos. Por favor espera..."):
                try:
                    punto = ee.Geometry.Point([in_lon, in_lat])
                    start_str = in_start.strftime("%Y-%m-%d")
                    end_str = in_end.strftime("%Y-%m-%d")

                    if "TerraClimate" in fuente:
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
