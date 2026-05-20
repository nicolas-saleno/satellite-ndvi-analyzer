# satellite_image_analyzer / ndvi_calculator.py
#
# Pipeline minimo para calcular NDVI a partir de imagenes Landsat 8 reales.
#
# Formula:  NDVI = (NIR - Red) / (NIR + Red)
#   - NIR  = banda infrarroja cercana (banda 5 en Landsat 8)
#   - Red  = banda roja visible       (banda 4 en Landsat 8)
#   - Resultado entre -1 y 1:
#       > 0.3  -> vegetacion sana
#       0-0.3  -> suelo desnudo
#       < 0    -> agua o nubes
#
# Datos: imagen real de la NASA del incendio Cold Springs (Colorado, 2016)


# 1. IMPORTACIONES 
import urllib.request   # Descarga archivos por HTTP  -- viene con Python
import zipfile          # Descomprime archivos .zip   -- viene con Python
import numpy as np          # Operaciones matematicas sobre arrays de pixeles
import matplotlib.pyplot as plt  # Visualizacion del mapa NDVI
import rasterio             # Lectura de archivos GeoTIFF (imagenes satelitales)
from pathlib import Path    # Manejo de rutas de archivos


# 2. DESCARGA DE DATOS escargamos el dataset directamente desde figshare (servidor publico y gratuito).

DATA_URL = "https://ndownloader.figshare.com/files/10960109"
DATA_DIR = Path.home() / "earth-analytics" / "data"
ZIP_PATH = Path.home() / "earth-analytics" / "cold-springs-fire.zip"

if not DATA_DIR.exists():
    print("Descargando datos de muestra (~40 MB, solo la primera vez)...")
    ZIP_PATH.parent.mkdir(parents=True, exist_ok=True)

    # reporthook funcion que se llama cuando que llega un bloque de datos.
    # La usamos para mostrar el progreso de descarga en la consola.
    def mostrar_progreso(count, block_size, total):
        mb_descargados = count * block_size / 1_000_000
        mb_total = total / 1_000_000
        print(f"  {mb_descargados:.1f} / {mb_total:.1f} MB", end="\r")

    urllib.request.urlretrieve(DATA_URL, ZIP_PATH, reporthook=mostrar_progreso)
    print("\n  Descarga completa. Descomprimiendo...")

    with zipfile.ZipFile(ZIP_PATH, "r") as z:
        z.extractall(Path.home() / "earth-analytics" / "data")

    ZIP_PATH.unlink()  # Borra el .zip, ya no lo necesitamos
    print("  Listo.")
else:
    print("Datos ya descargados, usando copia local.")


# 3. RUTAS A LAS BANDAS # Los archivos Landsat 8 tienen una banda por archivo .tif.
# Usamos glob para encontrarlos sin importar el nombre exacto del archivo.

landsat_dir = (DATA_DIR / "landsat_collect"
               / "LC080340322016072301T1-SC20180214145802" / "crop")

path_red = sorted(landsat_dir.glob("*band4_crop.tif"))[0]
path_nir = sorted(landsat_dir.glob("*band5_crop.tif"))[0]

print(f"\nBanda roja (B4): {path_red.name}")
print(f"Banda NIR  (B5): {path_nir.name}")


# 4. LECTURA DE BANDAS asterio.open() abre el GeoTIFF como si fuera un archivo de texto.
# .read(1) devuelve la primera capa como un array 2D de NumPy.
# .astype("float32") convierte los enteros a decimales para que la
# division del NDVI no se trunque.

print("\nCargando bandas...")

with rasterio.open(path_red) as src:
    red_band = src.read(1).astype("float32")

with rasterio.open(path_nir) as src:
    nir_band = src.read(1).astype("float32")

print(f"  Tamano: {red_band.shape[0]} filas x {red_band.shape[1]} columnas")
print(f"  Total de pixeles: {red_band.size:,}")


# 5. MASCARA DE NO DATA # Landsat 8 usa el valor 0 para indicar "sin datos" (bordes, nubes, etc.).
# Los reemplazamos con NaN para que NumPy y matplotlib los ignoren.

NO_DATA = 0
mask = (red_band != NO_DATA) & (nir_band != NO_DATA)
red_band[~mask] = np.nan
nir_band[~mask] = np.nan

print(f"  Pixeles validos: {mask.sum():,}  ({mask.mean()*100:.1f}%)")


# 6. CALCULO DEL NDVI NumPy aplica la formula a todos los pixeles a la vez, sin bucle for.
# np.errstate suprime el warning de 0/0 en zonas de NaN.

print("\nCalculando NDVI...")

with np.errstate(divide="ignore", invalid="ignore"):
    ndvi = (nir_band - red_band) / (nir_band + red_band)

print(f"  Minimo:  {np.nanmin(ndvi):.3f}")
print(f"  Maximo:  {np.nanmax(ndvi):.3f}")
print(f"  Media:   {np.nanmean(ndvi):.3f}")

vegetacion_pct = (ndvi > 0.3).sum() / mask.sum() * 100
print(f"  Vegetacion sana (NDVI > 0.3): {vegetacion_pct:.1f}%")


# 7. VISUALIZACION res paneles: banda roja, banda NIR, y el mapa NDVI con escala de colores.

print("\nGenerando visualizacion...")

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle("Satellite Image Analyzer — NDVI · Landsat 8 · Cold Springs Fire",
             fontsize=13, fontweight="bold")

axes[0].imshow(red_band, cmap="Reds_r")
axes[0].set_title("Banda 4 — Rojo visible")
axes[0].set_xlabel("Columnas (pixeles)")
axes[0].set_ylabel("Filas (pixeles)")

axes[1].imshow(nir_band, cmap="Greys_r")
axes[1].set_title("Banda 5 — Infrarrojo cercano (NIR)")
axes[1].set_xlabel("Columnas (pixeles)")

im = axes[2].imshow(ndvi, cmap="RdYlGn", vmin=-0.5, vmax=0.9)
axes[2].set_title("NDVI calculado\n(Verde = vegetacion sana)")
axes[2].set_xlabel("Columnas (pixeles)")
fig.colorbar(im, ax=axes[2], fraction=0.046, pad=0.04).set_label("Valor NDVI")

plt.tight_layout()

output_path = Path("ndvi_resultado.png")
plt.savefig(output_path, dpi=150, bbox_inches="tight")
print(f"\nListo! Imagen guardada en: {output_path.resolve()}")
plt.show()
