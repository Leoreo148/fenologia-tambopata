import pandas as pd
df = pd.read_csv('Datos_Procesados_Tambopata.csv')
# Tomar el primer TAG (Individuo/Planta) que aparezca
tree = df['TAG'].dropna().iloc[0]
tree_data = df[df['TAG'] == tree].sort_values(['YEAR', 'MONTH'])

print(f"Planta (Placa TAG): {tree}")
print(f"Especie: {tree_data.iloc[0]['Nombre científico']}")
print(f"Total de visitas a este árbol: {len(tree_data)}")
print(f"Años en los que se observó: {tree_data['YEAR'].unique().tolist()}")

print("\nVisitas por año y mes (Agrupado por Año):")
conteo = tree_data.groupby('YEAR')['MONTH'].count()
print(conteo)

print("\nFechas exactas del año 2011 para este árbol:")
print(tree_data[tree_data['YEAR'] == 2011][['MONTH', 'DATE']].to_string(index=False))
