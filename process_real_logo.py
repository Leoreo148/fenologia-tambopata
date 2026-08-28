import shutil
from pathlib import Path
from PIL import Image

logo_src = Path(r"C:\Users\lenovo\.gemini\antigravity\brain\bd68efff-98f7-4e23-937f-34bdf441ede1\.user_uploaded\media_1787873590931.png")
assets_dir = Path(r"C:\Users\lenovo\Documents\antigravity\proud-pascal\mobile-app\assets")
assets_dir.mkdir(parents=True, exist_ok=True)

# 1. Copiar logo original
dest_real = assets_dir / "macaw_logo_real.png"
shutil.copy(logo_src, dest_real)
print(f"[OK] Logo original copiado a {dest_real}")

# Cargar imagen
img = Image.open(logo_src).convert("RGBA")

# 2. Generar icon.png (1024x1024) con fondo #082b23
icon_size = (1024, 1024)
icon_bg = Image.new("RGBA", icon_size, (8, 43, 35, 255)) # #082b23
img_resized = img.resize((900, 900), Image.Resampling.LANCZOS)
icon_bg.paste(img_resized, (62, 62), img_resized)
icon_bg.save(assets_dir / "icon.png", "PNG")
print("[OK] icon.png 1024x1024 generado")

# 3. Generar adaptive-icon.png (1024x1024)
adaptive = Image.new("RGBA", icon_size, (0, 0, 0, 0))
img_adapt = img.resize((720, 720), Image.Resampling.LANCZOS)
adaptive.paste(img_adapt, (152, 152), img_adapt)
adaptive.save(assets_dir / "adaptive-icon.png", "PNG")
print("[OK] adaptive-icon.png 1024x1024 generado")

# 4. Generar splash.png (1242x2436)
splash_size = (1242, 2436)
splash = Image.new("RGBA", splash_size, (8, 43, 35, 255)) # #082b23
img_splash = img.resize((650, 650), Image.Resampling.LANCZOS)
splash.paste(img_splash, (296, 893), img_splash)
splash.save(assets_dir / "splash.png", "PNG")
print("[OK] splash.png 1242x2436 generado")

# 5. Generar favicon.png (64x64)
fav = img.resize((64, 64), Image.Resampling.LANCZOS)
fav.save(assets_dir / "favicon.png", "PNG")
print("[OK] favicon.png 64x64 generado")
