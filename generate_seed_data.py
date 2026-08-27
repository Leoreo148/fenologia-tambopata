import json
from pathlib import Path

out_dir = Path('mobile-app/src/database')
out_dir.mkdir(parents=True, exist_ok=True)

# Cargar parcelas
with open('parcelas_colorado_coordenadas.json', 'r', encoding='utf-8') as f:
    parcelas = json.load(f)

# Cargar árboles
with open('arboles_censo_colorado_1939.json', 'r', encoding='utf-8') as f:
    arboles = json.load(f)

# Mapear prefijo de hábitat para la nomenclatura CSV
prefijos_habitat = {
    'BOSQUE DE BAJÍO': 'BB',
    'BOSQUE DE BAJIO': 'BB',
    'BOSQUE DE TIERRA FIRME': 'BTF',
    'BOSQUE DE AGUAJAL': 'BAG',
    'BOSQUE SUCESIONAL': 'BS'
}

for p in parcelas:
    p['prefijo_nomenclatura'] = prefijos_habitat.get(p['HABITAT'].upper(), 'B')

# Empaquetar seed data
seed_data = {
    'version': '2026.1',
    'total_parcelas': len(parcelas),
    'total_arboles': len(arboles),
    'parcelas': parcelas,
    'arboles': arboles
}

seed_path = out_dir / 'seedData.json'
with open(seed_path, 'w', encoding='utf-8') as f:
    json.dump(seed_data, f, ensure_ascii=False, indent=2)

print(f"Seed data creado con éxito en {seed_path}: {len(parcelas)} parcelas y {len(arboles)} árboles.")
