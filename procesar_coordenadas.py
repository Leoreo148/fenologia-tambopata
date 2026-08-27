import pandas as pd
from pyproj import Transformer

df = pd.read_excel('COORDENADAS PARCELS_COLORADO_2026.xlsx', header=1)
df.columns = ['CODIGO', 'HABITAT', 'ESTE', 'NORTE', 'ALTURA']
df = df.dropna(subset=['CODIGO', 'ESTE', 'NORTE'])

transformer = Transformer.from_crs('EPSG:32719', 'EPSG:4326', always_xy=True)

lon_list, lat_list = [], []
for _, row in df.iterrows():
    lon, lat = transformer.transform(float(row['ESTE']), float(row['NORTE']))
    lon_list.append(round(lon, 6))
    lat_list.append(round(lat, 6))

df['LONGITUD'] = lon_list
df['LATITUD'] = lat_list
df['ALTURA_MSNM'] = df['ALTURA'].astype(float)
df['ESTE_UTM19L'] = df['ESTE'].astype(float)
df['NORTE_UTM19L'] = df['NORTE'].astype(float)

clean_df = df[['CODIGO', 'HABITAT', 'ESTE_UTM19L', 'NORTE_UTM19L', 'ALTURA_MSNM', 'LATITUD', 'LONGITUD']].sort_values(['HABITAT', 'CODIGO']).reset_index(drop=True)

clean_df.to_csv('parcelas_colorado_coordenadas.csv', index=False, encoding='utf-8')
clean_df.to_json('parcelas_colorado_coordenadas.json', orient='records', indent=2)

print(f"Exportadas {len(clean_df)} parcelas a CSV y JSON.")
print(clean_df.to_string())
