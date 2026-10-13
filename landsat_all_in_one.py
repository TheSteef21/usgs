import os
import glob
import numpy as np

try:
    import rasterio
    from rasterio.plot import show
    HAS_RASTERIO = True
except ImportError:
    HAS_RASTERIO = False

EXTRACT_DIR = "landsat_extracted"

def main():
    print("=== PROCESADOR TODO EN UNO LANDSAT 9 ===")
    
    if not os.path.exists(EXTRACT_DIR):
        print(f"Error: No se encuentra la carpeta {EXTRACT_DIR}. Asegúrate de haber ejecutado la extracción.")
        return

    # Buscar archivos TIF y MTL
    tifs = glob.glob(os.path.join(EXTRACT_DIR, "*.TIF"))
    mtl_files = glob.glob(os.path.join(EXTRACT_DIR, "*_MTL.txt"))

    print(f"Total de bandas e imágenes TIF detectadas: {len(tifs)}")
    if mtl_files:
        print(f"Metadatos encontrados: {os.path.basename(mtl_files[0])}")

    # Identificar bandas clave
    band_paths = {}
    for tif in tifs:
        filename = os.path.basename(tif)
        # Extraer el identificador de banda (ej: _B4.TIF)
        for b in ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B10", "B11"]:
            if f"_{b}.TIF" in filename or f"_{b}_" in filename:
                band_paths[b] = tif

    print(f"\nBandas principales mapeadas: {list(band_paths.keys())}")

    if not HAS_RASTERIO:
        print("\n[Aviso] La librería 'rasterio' no está instalada.")
        print("Si deseas procesar matemáticamente las matrices de las bandas (como NDVI o apilado), instala rasterio con: pip install rasterio")
        return

    # Ejemplo de procesamiento rápido: Calcular estadísticas básicas de la Banda 4 (Roja) o Banda 5 (NIR)
    if "B5" in band_paths and "B4" in band_paths:
        print("\nCalculando reflectancia y análisis rápido (NDVI aproximado con bandas 5 y 4)...")
        with rasterio.open(band_paths["B5"]) as src_nir, rasterio.open(band_paths["B4"]) as src_red:
            # Leer datos como matriz flotante para evitar desbordamiento
            nir = src_nir.read(1).astype(np.float32)
            red = src_red.read(1).astype(np.float32)
            
            # Evitar división por cero
            denominator = (nir + red)
            ndvi = np.where(denominator == 0., 0., (nir - red) / denominator)
            
            print(f"-> NDVI Calculado con éxito.")
            print(f"   Valor mínimo NDVI: {np.min(ndvi):.4f}")
            print(f"   Valor máximo NDVI: {np.max(ndvi):.4f}")
            print(f"   Valor promedio NDVI: {np.mean(ndvi):.4f}")
    
    print("\n¡Proceso todo en uno finalizado con éxito!")

if __name__ == "__main__":
    main()
