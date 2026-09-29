# -*- coding: utf-8 -*-
"""Uiraçu 2.0 — Parte 2, Ficha 2.4: variáveis ambientais.

Extrai as 19 variáveis bioclimáticas do WorldClim v2.1 (10 min de arco)
e recorta cada uma para a extensão da área acessível M (Lagothrix lagothricha),
já definida no script 20 (união de 11 ecorregiões).

Entrada:  Modelagem preditiva/Dados/wc2.1_10m_bio.zip
Saída:    Dados/worldclim_M/wc2.1_10m_bio_XX_M.tif  (19 rasters recortados)
"""
import os
import zipfile
import geopandas as gpd
import rasterio
from rasterio.mask import mask

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZIP_PATH = os.path.join(RAIZ, "..", "..", "Modelagem preditiva", "Dados", "wc2.1_10m_bio.zip")
RAW_DIR = os.path.join(RAIZ, "Dados", "worldclim_raw")
OUT_DIR = os.path.join(RAIZ, "Dados", "worldclim_M")
M_PATH = os.path.join(RAIZ, "Dados", "area_M_lagothrix_dissolvido.gpkg")

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

# 1) Extrair o zip (só se ainda não extraído)
tifs_existentes = [f for f in os.listdir(RAW_DIR) if f.endswith(".tif")]
if len(tifs_existentes) < 19:
    print(f"Extraindo {ZIP_PATH} ...")
    with zipfile.ZipFile(ZIP_PATH) as z:
        z.extractall(RAW_DIR)
    print("Extração concluída.")
else:
    print(f"{len(tifs_existentes)} rasters já extraídos em {RAW_DIR}, pulando extração.")

tifs = sorted(f for f in os.listdir(RAW_DIR) if f.endswith(".tif"))
print(f"{len(tifs)} rasters bioclimáticos encontrados.")

# 2) Carregar M (já em EPSG:4326, mesmo CRS do WorldClim)
area_M = gpd.read_file(M_PATH)
if area_M.crs is None or area_M.crs.to_epsg() != 4326:
    area_M = area_M.to_crs("EPSG:4326")
geom_M = [g.__geo_interface__ for g in area_M.geometry]

# 3) Recortar cada raster para a extensão de M
for nome in tifs:
    caminho_in = os.path.join(RAW_DIR, nome)
    caminho_out = os.path.join(OUT_DIR, nome.replace(".tif", "_M.tif"))
    if os.path.exists(caminho_out):
        print(f"  [ok] {nome} já recortado, pulando.")
        continue
    with rasterio.open(caminho_in) as src:
        out_image, out_transform = mask(src, geom_M, crop=True, nodata=src.nodata)
        out_meta = src.meta.copy()
        out_meta.update({
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform,
        })
    with rasterio.open(caminho_out, "w", **out_meta) as dst:
        dst.write(out_image)
    print(f"  [feito] {nome} -> {os.path.basename(caminho_out)}  shape={out_image.shape}")

print(f"\nConcluído. Rasters recortados em: {OUT_DIR}")
