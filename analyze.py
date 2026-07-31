import pandas as pd
import numpy as np

# Definir los roles según la información del equipo
diccionario_roles = {
    # Estrellas Comerciales - Frutales
    'Pouteria': 'Estrella Comercial - Frutal',
    'Bactris': 'Estrella Comercial - Frutal',
    'Hymenaea': 'Estrella Comercial - Frutal',
    'Theobroma': 'Estrella Comercial - Frutal',
    'Euterpe': 'Estrella Comercial - Frutal',
    
    # Estrellas Comerciales - Industriales
    'Copaifera': 'Estrella Comercial - Industrial',
    'Hevea': 'Estrella Comercial - Industrial',
    'Dipteryx': 'Estrella Comercial - Industrial',
    'Croton': 'Estrella Comercial - Industrial',
    
    # Ingenieros del Suelo - Fijadores de N
    'Inga': 'Ingeniero del Suelo - Fijador N',
    'Erythrina': 'Ingeniero del Suelo - Fijador N',
    'Tachigali': 'Ingeniero del Suelo - Fijador N',
    'Swartzia': 'Ingeniero del Suelo - Fijador N',
    
    # Ingenieros del Suelo - Pioneras
    'Cecropia': 'Ingeniero del Suelo - Pionera',
    'Jacaranda': 'Ingeniero del Suelo - Pionera',
    'Aptandra': 'Ingeniero del Suelo - Pionera',
    
    # Cajas Fuertes
    'Cedrela': 'Caja Fuerte - Maderable',
    'Brosimum': 'Caja Fuerte - Maderable',
    'Cedrelinga': 'Caja Fuerte - Maderable / Fijador N', # Doble propósito
    'Aspidosperma': 'Caja Fuerte - Maderable'
}

print("Cargando la base de datos...")
df = pd.read_excel('DATA_FENOLOGIA_2010_2017.xlsx')

print(f"Total de registros iniciales: {len(df)}")

# Limpieza básica
# Asegurar que 'GENERO' sea string, sin espacios extra y Capitalizado
df['GENERO_limpio'] = df['GENERO'].astype(str).str.strip().str.capitalize()

# Mapear el rol agroforestal
df['Rol_Agroforestal'] = df['GENERO_limpio'].map(diccionario_roles)

# Reemplazar NaN por 'Otro'
df['Rol_Agroforestal'] = df['Rol_Agroforestal'].fillna('Otro')

# Filtrar solo las especies de interés para el análisis principal
df_interes = df[df['Rol_Agroforestal'] != 'Otro']

print("\nConteo de registros por Rol Agroforestal en Tambopata (2010-2017):")
resumen = df_interes['Rol_Agroforestal'].value_counts()
print(resumen)

# Guardar un archivo procesado con esta nueva clasificación
df_interes.to_csv('Datos_Procesados_Tambopata.csv', index=False, encoding='utf-8')
print("\nArchivo 'Datos_Procesados_Tambopata.csv' generado exitosamente con", len(df_interes), "registros.")
