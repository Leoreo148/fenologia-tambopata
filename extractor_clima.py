import ee
import pandas as pd
import datetime
import argparse

def extraer_clima(lat, lon, fecha_inicio, fecha_fin, output_file):
    print("Iniciando conexión con Google Earth Engine...")
    try:
        # Intenta inicializar. Si falla, pedirá autenticación.
        ee.Initialize()
    except Exception as e:
        print("No estás autenticado. Ejecuta 'earthengine authenticate' en tu terminal primero.")
        return

    print(f"Extrayendo datos de TerraClimate para la coordenada: Lat {lat}, Lon {lon}")
    punto = ee.Geometry.Point([lon, lat])

    # Colección de TerraClimate (resolución ~4km)
    # Seleccionamos precipitación (pr), temp máxima (tmmx), temp mínima (tmmn) y presión de vapor (vap)
    coleccion = (ee.ImageCollection('IDAHO_EPSCOR/TERRACLIMATE')
                 .select(['pr', 'tmmx', 'tmmn', 'vap'])
                 .filterBounds(punto)
                 .filterDate(fecha_inicio, fecha_fin))

    # Extraer la serie de tiempo para ese punto específico (escala 4000 metros)
    info = coleccion.getRegion(punto, 4000).getInfo()

    if not info or len(info) <= 1:
        print("No se encontraron datos para esas fechas y coordenadas.")
        return

    # Convertir a Pandas DataFrame
    header = info[0]
    data = info[1:]
    df = pd.DataFrame(data, columns=header)

    # TerraClimate usa factores de escala.
    # Las temperaturas vienen multiplicadas por 10, y la presión de vapor (vap) por 1000.
    df['pr'] = pd.to_numeric(df['pr'])
    df['tmmx'] = pd.to_numeric(df['tmmx']) * 0.1
    df['tmmn'] = pd.to_numeric(df['tmmn']) * 0.1
    df['vap'] = pd.to_numeric(df['vap']) * 0.001  # Presión de vapor real en kPa
    
    import numpy as np
    # Calcular Temperatura Media
    df['tmean'] = (df['tmmx'] + df['tmmn']) / 2

    # Calcular Humedad Relativa aproximada (%) usando la fórmula de Tetens
    # 1. Presión de vapor de saturación (es) a la temperatura media (en kPa)
    es = 0.6108 * np.exp((17.27 * df['tmean']) / (df['tmean'] + 237.3))
    # 2. Humedad Relativa (RH)
    df['humidity'] = (df['vap'] / es) * 100
    df['humidity'] = df['humidity'].clip(upper=100.0) # Limitar al 100%

    # Extraer Año y Mes del ID de la imagen (ej: 201001)
    df['year'] = df['id'].str[0:4].astype(int)
    df['month'] = df['id'].str[4:6].astype(int)

    # Renombrar para que coincida con el formato del tío
    df_final = df[['year', 'month', 'pr', 'tmean', 'humidity']].copy()
    df_final.columns = ['YEAR', 'MONTH', 'RAIN', 'TEMPERATURE', 'HUMIDITY']

    # Guardar a CSV
    df_final.to_csv(output_file, index=False)
    print(f"¡Éxito! Datos guardados en {output_file}")
    print(df_final.head())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extraer datos climáticos de TerraClimate usando GEE.")
    parser.add_argument("--lat", type=float, required=True, help="Latitud")
    parser.add_argument("--lon", type=float, required=True, help="Longitud")
    parser.add_argument("--inicio", type=str, default="2010-01-01", help="Fecha inicio (YYYY-MM-DD)")
    parser.add_argument("--fin", type=str, default="2017-12-31", help="Fecha fin (YYYY-MM-DD)")
    parser.add_argument("--out", type=str, default="clima_terraclimate.csv", help="Archivo CSV de salida")
    
    args = parser.parse_args()
    extraer_clima(args.lat, args.lon, args.inicio, args.fin, args.out)
