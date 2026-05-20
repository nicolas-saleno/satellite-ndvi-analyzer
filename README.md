# Satellite Image Analyzer

Pipeline en Python para procesar imagenes satelitales reales orientado a agricultura de precision.

## MVP — v1.0: Calculo de NDVI

Carga imagenes Landsat 8 de la NASA y calcula el NDVI (Normalized Difference Vegetation Index).

```
NDVI = (NIR - Rojo) / (NIR + Rojo)    ->   valores entre -1 y 1
```

| Valor NDVI | Interpretacion           |
|------------|--------------------------|
| > 0.3      | Vegetacion sana          |
| 0.0 - 0.3  | Suelo desnudo / pastizal |
| < 0.0      | Agua, nieve, nubes       |

## Instalacion y uso

```bash
pip install -r requirements.txt
python ndvi_calculator.py
```

La primera ejecucion descarga el dataset de muestra (~40 MB) automaticamente.

## Estructura del proyecto

```
satellite-image-analyzer/
├── requirements.txt        # Dependencias
├── ndvi_calculator.py      # Script principal
└── README.md
```

## Stack

| Libreria    | Rol                                  |
|-------------|---------------------------------------|
| urllib      | Descarga del dataset (viene con Python)|
| rasterio    | Lectura de archivos GeoTIFF            |
| numpy       | Operaciones sobre arrays de pixeles    |
| matplotlib  | Visualizacion del mapa NDVI            |

## Roadmap

- [ ] v1.1 — Exportar NDVI como GeoTIFF con coordenadas reales
- [ ] v1.2 — Calcular EVI y SAVI
- [ ] v2.0 — Serie temporal: comparar NDVI de distintas fechas
- [ ] v3.0 — Clasificacion de coberturas con ML
