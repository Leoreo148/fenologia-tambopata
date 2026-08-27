from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

assets_dir = Path('mobile-app/assets')
assets_dir.mkdir(parents=True, exist_ok=True)

# 1. Crear icon.png (1024x1024)
icon_size = (1024, 1024)
icon = Image.new('RGBA', icon_size, color='#0f382c')
draw = ImageDraw.Draw(icon)

# Círculo exterior dorado/verde
draw.ellipse([160, 160, 864, 864], fill='#1b5e20', outline='#f1c40f', width=20)
draw.ellipse([220, 220, 804, 804], fill='#0d2b1d', outline='#4caf50', width=10)

# Dibujar silueta estilizada de Guacamayo / Palmera
# Alas rojas y amarillas
draw.polygon([(512, 280), (320, 520), (512, 640)], fill='#e74c3c')
draw.polygon([(512, 280), (704, 520), (512, 640)], fill='#2980b9')
draw.polygon([(420, 480), (512, 380), (604, 480)], fill='#f1c40f')
# Cola larga
draw.polygon([(470, 620), (512, 820), (554, 620)], fill='#c0392b')

icon.save(assets_dir / 'icon.png', 'PNG')
print("[OK] icon.png creado (1024x1024)")

# 2. Crear adaptive-icon.png (1024x1024)
adaptive_icon = Image.new('RGBA', icon_size, (0, 0, 0, 0))
draw_ad = ImageDraw.Draw(adaptive_icon)
draw_ad.ellipse([200, 200, 824, 824], fill='#1b5e20', outline='#f1c40f', width=18)
draw_ad.polygon([(512, 300), (340, 520), (512, 620)], fill='#e74c3c')
draw_ad.polygon([(512, 300), (684, 520), (512, 620)], fill='#2980b9')
draw_ad.polygon([(430, 480), (512, 390), (594, 480)], fill='#f1c40f')
draw_ad.polygon([(480, 600), (512, 800), (544, 600)], fill='#c0392b')

adaptive_icon.save(assets_dir / 'adaptive-icon.png', 'PNG')
print("[OK] adaptive-icon.png creado (1024x1024)")

# 3. Crear splash.png (1242x2436)
splash_size = (1242, 2436)
splash = Image.new('RGBA', splash_size, color='#0f382c')
draw_sp = ImageDraw.Draw(splash)

# Centro con logo
draw_sp.ellipse([421, 800, 821, 1200], fill='#1b5e20', outline='#f1c40f', width=16)
draw_sp.polygon([(621, 870), (480, 1020), (621, 1100)], fill='#e74c3c')
draw_sp.polygon([(621, 870), (762, 1020), (621, 1100)], fill='#2980b9')
draw_sp.polygon([(540, 980), (621, 920), (702, 980)], fill='#f1c40f')
draw_sp.polygon([(580, 1080), (621, 1220), (662, 1080)], fill='#c0392b')

splash.save(assets_dir / 'splash.png', 'PNG')
print("[OK] splash.png creado (1242x2436)")

# 4. Crear favicon.png (64x64)
fav = icon.resize((64, 64), Image.Resampling.LANCZOS)
fav.save(assets_dir / 'favicon.png', 'PNG')
print("[OK] favicon.png creado (64x64)")
