import pandas as pd
import re

excel_file = 'Phenology 2021 to jun 2026.xlsx'

# 1. Procesar Hoja 2: Censo Maestro de Árboles (1,939 árboles)
df_censo = pd.read_excel(excel_file, sheet_name='Hoja2')
df_censo = df_censo[['PLOP', 'SUB', 'TAG', 'Nombre científico']].dropna(subset=['PLOP', 'SUB']).copy()

# Limpiar texto de nombres científicos
def clean_scientific_name(name):
    if pd.isna(name):
        return 'Indeterminado'
    s = str(name).strip()
    s = s.replace('\t', ' ').replace('\n', ' ')
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

df_censo['Nombre_cientifico_limpio'] = df_censo['Nombre científico'].apply(clean_scientific_name)

# Extraer Género y Especie
def extract_genus(name):
    parts = name.split()
    return parts[0] if len(parts) > 0 else 'Indeterminado'

df_censo['GENERO'] = df_censo['Nombre_cientifico_limpio'].apply(extract_genus)

# Exportar censo maestro de árboles
df_censo.to_csv('arboles_censo_colorado_1939.csv', index=False, encoding='utf-8')
df_censo.to_json('arboles_censo_colorado_1939.json', orient='records', indent=2)
print(f"1. Censo maestro exportado: {len(df_censo)} árboles marcados en 25 parcelas.")

# 2. Procesar Hoja 1: Monitoreo Fenológico (2021 - 2026)
df_feno = pd.read_excel(excel_file, sheet_name='Hoja1')

# Filtrar registros válidos
df_feno['Nombre_cientifico_limpio'] = df_feno['Nombre científico'].apply(clean_scientific_name)
df_feno['GENERO'] = df_feno['Nombre_cientifico_limpio'].apply(extract_genus)

# Limpiar columnas fenológicas numéricas
for col in ['BOTÓN', 'FLOR', 'FRUTO VERDE', 'FRUTO MADURO', 'DISEMINADO']:
    df_feno[col + '_val'] = pd.to_numeric(df_feno[col], errors='coerce').fillna(0).astype(int)

df_feno.to_csv('fenologia_monitoreo_2021_2026.csv', index=False, encoding='utf-8')
print(f"2. Monitoreo fenológico exportado: {len(df_feno)} observaciones mensuales.")
