import ee
import pandas as pd
import numpy as np
import argparse

def extraer_era5_hourly(lat, lon, fecha_inicio, fecha_fin, output_file, project_id=None):
    print("Iniciando conexión con Google Earth Engine...")
    try:
        if project_id:
            ee.Initialize(project=project_id)
        else:
            ee.Initialize()
    except Exception as e:
        print(f"Error de GEE: {e}")
        print("Asegúrate de tener un proyecto de Google Cloud configurado. Pásalo con --project tu-id")
        return

    print(f"Extrayendo datos de ERA5-Land (Por Hora) para la coordenada: Lat {lat}, Lon {lon}")
    punto = ee.Geometry.Point([lon, lat])

    # Colección de ERA5-Land Hourly (resolución ~11km / 0.1°)
    # temperature_2m, dewpoint_temperature_2m, total_precipitation, volumetric_soil_water_layer_1
    coleccion = (ee.ImageCollection('ECMWF/ERA5_LAND/HOURLY')
                 .select(['temperature_2m', 'dewpoint_temperature_2m', 'total_precipitation', 'volumetric_soil_water_layer_1'])
                 .filterBounds(punto)
                 .filterDate(fecha_inicio, fecha_fin))

    # Extraer la serie de tiempo para ese punto específico (escala 11132 metros)
    print("Descargando datos (esto puede tardar unos minutos porque son muchísimos registros por hora)...")
    info = coleccion.getRegion(punto, 11132).getInfo()

    if not info or len(info) <= 1:
        print("No se encontraron datos para esas fechas y coordenadas.")
        return

    # Convertir a Pandas DataFrame
    header = info[0]
    data = info[1:]
    df = pd.DataFrame(data, columns=header)
    df = df.drop_duplicates(subset=['id', 'time'])

    # Limpieza y cálculos
    df['total_precipitation'] = pd.to_numeric(df['total_precipitation'])
    df['temperature_2m'] = pd.to_numeric(df['temperature_2m'])
    df['dewpoint_temperature_2m'] = pd.to_numeric(df['dewpoint_temperature_2m'])
    df['volumetric_soil_water_layer_1'] = pd.to_numeric(df['volumetric_soil_water_layer_1'])

    # 1. Convertir Temperatura y Punto de Rocío de Kelvin a Celsius
    df['temp_c'] = df['temperature_2m'] - 273.15
    df['dew_c'] = df['dewpoint_temperature_2m'] - 273.15
    
    # 2. Calcular Precipitación horaria real en mm (diferencial respetando el reinicio diario a las 00:00 UTC)
    precip_m = df['total_precipitation'].copy()
    diff_precip = precip_m.diff()
    hourly_rain_m = np.where(diff_precip < 0, precip_m, diff_precip)
    if len(hourly_rain_m) > 0:
        hourly_rain_m[0] = precip_m.iloc[0]
    df['rain_mm'] = np.maximum(0, hourly_rain_m) * 1000.0

    # 3. Calcular Humedad del Suelo (%)
    df['soil_moisture_percent'] = df['volumetric_soil_water_layer_1'] * 100.0

    # 4. Calcular Humedad Relativa (%) usando Magnus-Tetens
    num = np.exp((17.625 * df['dew_c']) / (243.04 + df['dew_c']))
    den = np.exp((17.625 * df['temp_c']) / (243.04 + df['temp_c']))
    df['humidity'] = (num / den) * 100.0
    df['humidity'] = df['humidity'].clip(upper=100.0)

    # 5. Timestamp exacto desde milisegundos
    df['datetime'] = pd.to_datetime(pd.to_numeric(df['time']), unit='ms')

    df_final = df[['datetime', 'rain_mm', 'temp_c', 'humidity', 'soil_moisture_percent']].copy()
    df_final.columns = ['DATETIME', 'RAIN_MM', 'TEMPERATURE_C', 'HUMIDITY_PERCENT', 'SOIL_MOISTURE_PERCENT']

    # Guardar a CSV
    df_final.to_csv(output_file, index=False)
    print(f"¡Éxito! {len(df_final)} registros guardados en {output_file}")
    print(df_final.head())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extraer datos climáticos por HORA de ERA5-Land.")
    parser.add_argument("--lat", type=float, required=True, help="Latitud")
    parser.add_argument("--lon", type=float, required=True, help="Longitud")
    parser.add_argument("--inicio", type=str, default="2025-01-01", help="Fecha inicio (YYYY-MM-DD)")
    parser.add_argument("--fin", type=str, default="2025-12-31", help="Fecha fin (YYYY-MM-DD)")
    parser.add_argument("--out", type=str, default="clima_era5_hourly.csv", help="Archivo CSV de salida")
    parser.add_argument("--project", type=str, default=None, help="Tu Google Cloud Project ID")
    
    args = parser.parse_args()
    extraer_era5_hourly(args.lat, args.lon, args.inicio, args.fin, args.out, args.project)
