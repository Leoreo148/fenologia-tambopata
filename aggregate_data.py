import pandas as pd
import numpy as np

# Cargar los datos filtrados
df = pd.read_csv('Datos_Procesados_Tambopata.csv')

# Verificar los valores únicos de fenología para entender cómo están medidos
print("Valores únicos en la columna RF (Frutos Maduros):", df['RF'].unique())
print("Valores únicos en la columna D (Caída de hojas):", df['D'].unique())

# Asegurar que las columnas sean numéricas para poder promediar o sumar
cols_fenologia = ['B', 'F', 'UF', 'RF', 'D']
for col in cols_fenologia:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

df['TEMPERATURE'] = pd.to_numeric(df['TEMPERATURE'], errors='coerce')
df['RAIN'] = pd.to_numeric(df['RAIN'], errors='coerce')

# 1. Promedio mensual del CLIMA a lo largo de los 7 años
clima_mensual = df.groupby('MONTH')[['TEMPERATURE', 'RAIN']].mean().reset_index()

# 2. Promedio mensual de FENOLOGÍA por ROL AGROFORESTAL
# ¿Cuándo fructifican las estrellas comerciales y cuándo botan hojas los ingenieros del suelo?
fenologia_mensual = df.groupby(['MONTH', 'Rol_Agroforestal'])[cols_fenologia].mean().reset_index()

# Pivotear la tabla para que sea fácil de leer: Filas=Meses, Columnas=RF de Frutales, D de Fijadores, etc.
tabla_final = clima_mensual.copy()

# Extraer el RF (Fructificación) para las Estrellas Comerciales
frutales = fenologia_mensual[fenologia_mensual['Rol_Agroforestal'] == 'Estrella Comercial - Frutal']
tabla_final = pd.merge(tabla_final, frutales[['MONTH', 'RF']].rename(columns={'RF': 'RF_Frutales'}), on='MONTH', how='left')

industriales = fenologia_mensual[fenologia_mensual['Rol_Agroforestal'] == 'Estrella Comercial - Industrial']
tabla_final = pd.merge(tabla_final, industriales[['MONTH', 'RF']].rename(columns={'RF': 'RF_Industriales'}), on='MONTH', how='left')

# Extraer la Caída de Hojas (D) para los Ingenieros del Suelo (Fijadores N)
fijadores_n = fenologia_mensual[fenologia_mensual['Rol_Agroforestal'] == 'Ingeniero del Suelo - Fijador N']
tabla_final = pd.merge(tabla_final, fijadores_n[['MONTH', 'D']].rename(columns={'D': 'D_Fijadores_N'}), on='MONTH', how='left')

# Imprimir la tabla resultante
print("\n--- TABLA ORDENADA: CLIMA VS FENOLOGÍA POR MES ---")
print(tabla_final.round(2).to_string(index=False))

# Guardar la tabla resumen
tabla_final.round(3).to_csv('Resumen_Mensual_Fenologia.csv', index=False)
print("\nArchivo 'Resumen_Mensual_Fenologia.csv' guardado. ¡Listo para graficar!")
