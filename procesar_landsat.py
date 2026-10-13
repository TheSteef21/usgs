import os
import glob
import rasterio
import numpy as np
from PIL import Image

print("--- Iniciando procesamiento Landsat en Termux (Modo Sobreescritura / Optimizado) ---")

# Buscar automáticamente las bandas B4 (Rojo), B3 (Verde) y B2 (Azul) en el directorio actual
try:
    red_file = glob.glob("*_B4.TIF")[0]
    green_file = glob.glob("*_B3.TIF")[0]
    blue_file = glob.glob("*_B2.TIF")[0]
except IndexError:
    print("Error: No se encontraron los archivos de bandas B2, B3 o B4 en este directorio.")
    print("Asegúrate de ejecutar este script en la carpeta donde descomprimiste el tar.gz.")
    exit(1)

print(f"Bandas detectadas:\n- Rojo: {red_file}\n- Verde: {green_file}\n- Azul: {blue_file}")

# Abrir archivos con rasterio y leer con reducción de escala (factor de 4) para evitar errores de memoria en Termux
with rasterio.open(red_file) as src_r, \
     rasterio.open(green_file) as src_g, \
     rasterio.open(blue_file) as src_b:
    
    scale_factor = 4  # Reducir resolución 4x para ahorrar RAM en el celular
    h = int(src_r.height / scale_factor)
    w = int(src_r.width / scale_factor)
    
    print(f"Leyendo y redimensionando a {w}x{h} píxeles...")
    
    r = src_r.read(1, out_shape=(h, w), resampling=rasterio.enums.Resampling.nearest)
    g = src_g.read(1, out_shape=(h, w), resampling=rasterio.enums.Resampling.nearest)
    b = src_b.read(1, out_shape=(h, w), resampling=rasterio.enums.Resampling.nearest)

# Función de normalización optimizada para uint8
def normalize_band(band):
    b_min, b_max = np.percentile(band, 2), np.percentile(band, 98) # Estiramiento de contraste por percentiles
    if b_max <= b_min:
        return np.zeros_like(band, dtype=np.uint8)
    normalized = np.clip((band - b_min) / (b_max - b_min) * 255, 0, 255)
    return normalized.astype(np.uint8)

print("Normalizando valores de las bandas...")
r_norm = normalize_band(r)
g_norm = normalize_band(g)
b_norm = normalize_band(b)

# Apilar en formato RGB e invertir a imagen PIL
print("Generando imagen JPG en color natural...")
rgb_array = np.dstack((r_norm, g_norm, b_norm))
img = Image.fromarray(rgb_array)

output_filename = "azuero_natural_rgb.jpg"
img.save(output_filename, "JPEG", quality=85)

print(f"¡Listo! Archivo guardado con éxito como '{output_filename}'. Ya puedes usarlo en tu web sin sobrepasar el límite de GitHub.")
