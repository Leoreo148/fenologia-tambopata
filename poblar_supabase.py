import json
import urllib.request
import urllib.error

SUPABASE_URL = "https://eidmtyounanssoxpzpqd.supabase.co"
SUPABASE_KEY = "sb_publishable_Ecc2NdqkACCq5QhZYKUeoA_6_jDaea7"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

# 1. Cargar Seed Data
with open('mobile-app/src/database/seedData.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

parcelas = data['parcelas']
arboles = data['arboles']

print(f"Preparando subida a Supabase ({SUPABASE_URL}):")
print(f"• {len(parcelas)} Parcelas")
print(f"• {len(arboles)} Árboles")

# 2. Subir Parcelas
payload_parcelas = []
for p in parcelas:
    payload_parcelas.append({
        "codigo": p["CODIGO"],
        "habitat": p["HABITAT"],
        "este_utm": p["ESTE_UTM19L"],
        "norte_utm": p["NORTE_UTM19L"],
        "altura_msnm": p["ALTURA_MSNM"],
        "latitud": p["LATITUD"],
        "longitud": p["LONGITUD"],
        "prefijo_nomenclatura": p["prefijo_nomenclatura"]
    })

try:
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/parcelas",
        data=json.dumps(payload_parcelas).encode('utf-8'),
        headers=headers,
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        print("[OK] 25 Parcelas sincronizadas exitosamente en Supabase!")
except urllib.error.HTTPError as e:
    print(f"[WARN] Error subiendo parcelas ({e.code}): {e.read().decode()}")

# 3. Subir Árboles en lotes de 200
payload_arboles = []
for a in arboles:
    payload_arboles.append({
        "plop": a["PLOP"],
        "sub": str(a["SUB"]),
        "tag": int(a["TAG"]) if a["TAG"] and str(a["TAG"]).isdigit() else 0,
        "nombre_cientifico": a["Nombre_cientifico_limpio"],
        "genero": a["GENERO"],
        "estado_vital": "Normal"
    })

batch_size = 200
for i in range(0, len(payload_arboles), batch_size):
    batch = payload_arboles[i:i+batch_size]
    try:
        req = urllib.request.Request(
            f"{SUPABASE_URL}/rest/v1/arboles",
            data=json.dumps(batch).encode('utf-8'),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req) as resp:
            print(f"[OK] Lote de arboles {i+1} a {min(i+batch_size, len(payload_arboles))} sincronizado.")
    except urllib.error.HTTPError as e:
        print(f"[WARN] Error subiendo lote {i} ({e.code}): {e.read().decode()}")

