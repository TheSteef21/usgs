import tarfile
import os

tar_path = "landsat_scene.tar"
extract_dir = "landsat_extracted"

print("Comprobando el archivo descargado...")
if not os.path.exists(tar_path):
    print(f"Error: No se encuentra el archivo {tar_path}. Espera a que termine la descarga de wget.")
    exit(1)

print(f"Descomprimiendo '{tar_path}' en la carpeta '{extract_dir}'...")
with tarfile.open(tar_path, "r") as tar:
    tar.extractall(path=extract_dir)

print("\n¡Descompresión completada con éxito!")

# Listar las bandas espectrales y metadatos encontrados
files = os.listdir(extract_dir)
tifs = [f for f in files if f.endswith(".TIF")]
mtl = [f for f in files if "MTL" in f]

print(f"\nSe encontraron {len(tifs)} archivos GeoTIFF (bandas):")
for band in sorted(tifs):
    print(f" 🛰️ {band}")

if mtl:
    print(f"\n📄 Archivo de metadatos detectado: {mtl[0]}")
