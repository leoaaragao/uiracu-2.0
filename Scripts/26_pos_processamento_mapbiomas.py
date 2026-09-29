# -*- coding: utf-8 -*-
"""Uiraçu 2.0 — Parte 2, pós-processamento: adequabilidade × MapBiomas × 85 UCs.

Cruza o mapa de consenso (script 24) com a classe 3 (Formação Florestal) do
MapBiomas Coleção 11 (2025, Landsat 30m), e resume o resultado por UC.

Problema de escala: o SDM foi ajustado numa grade de ~18,5 km (WorldClim 10
min de arco); o MapBiomas é de 30 m. Não faz sentido "aumentar a resolução"
do SDM — em vez disso, para cada célula da grade do SDM calculamos a FRAÇÃO
de pixels MapBiomas que são floresta (classe 3), lendo o raster nacional só
nas janelas necessárias (nunca carregado inteiro na memória — 763 MB, ~21,5
bilhões de pixels no total, mas só ~1% da área cai na região das 85 UCs).
"""
import os

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.features import rasterize
from rasterio.transform import rowcol
from rasterio.windows import from_bounds

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DADOS = os.path.join(RAIZ, "Dados")
RESULTADOS = os.path.join(RAIZ, "Resultados")

MB_PATH = os.path.join(DADOS, "Mapbiomas", "brazil_coverage-col11_2025.tif")
CONSENSO_PATH = os.path.join(RESULTADOS, "lagothrix_consenso.tif")
INCERTEZA_PATH = os.path.join(RESULTADOS, "lagothrix_incerteza.tif")
UCS_PATH = os.path.join(DADOS, "ucs_federais_amazonia_ocidental.gpkg")
CLASSE_FLORESTA = 3

# ---------------------------------------------------------------------------
# 1) Carregar consenso/incerteza (grade do SDM) e as 85 UCs
# ---------------------------------------------------------------------------
with rasterio.open(CONSENSO_PATH) as src:
    consenso = src.read(1)
    transform = src.transform
    altura, largura = src.shape
    nodata = src.nodata
    perfil = src.profile.copy()

with rasterio.open(INCERTEZA_PATH) as src:
    incerteza = src.read(1)

ucs = gpd.read_file(UCS_PATH).to_crs("EPSG:4326")
minx, miny, maxx, maxy = ucs.total_bounds
print(f"Extensão das 85 UCs: lon [{minx:.2f}, {maxx:.2f}]  lat [{miny:.2f}, {maxy:.2f}]")

# Subgrade da grade do SDM que cobre a extensão das UCs (com 1 célula de folga)
row_topo, col_esq = rowcol(transform, minx, maxy)
row_base, col_dir = rowcol(transform, maxx, miny)
r0, r1 = max(row_topo - 1, 0), min(row_base + 2, altura)
c0, c1 = max(col_esq - 1, 0), min(col_dir + 2, largura)
print(f"Subgrade do SDM a processar: linhas {r0}-{r1}, colunas {c0}-{c1} "
      f"({(r1 - r0) * (c1 - c0)} células de {altura * largura} totais em M)")

# ---------------------------------------------------------------------------
# 2) Fração de floresta (classe 3) por célula da subgrade, lida do MapBiomas
# ---------------------------------------------------------------------------
fracao_floresta = np.full((altura, largura), np.nan, dtype="float32")

with rasterio.open(MB_PATH) as mb:
    total_celulas = (r1 - r0) * (c1 - c0)
    processadas = 0
    for r in range(r0, r1):
        for c in range(c0, c1):
            if consenso[r, c] == nodata:
                continue
            x_esq, y_topo = transform * (c, r)
            x_dir, y_base = transform * (c + 1, r + 1)
            janela = from_bounds(x_esq, y_base, x_dir, y_topo, transform=mb.transform)
            bloco = mb.read(1, window=janela, boundless=True, fill_value=0)
            if bloco.size == 0:
                continue
            fracao_floresta[r, c] = np.mean(bloco == CLASSE_FLORESTA)
            processadas += 1
        if (r - r0) % 20 == 0:
            print(f"  linha {r - r0}/{r1 - r0} da subgrade...", flush=True)

print(f"Células processadas com dado MapBiomas: {processadas}/{total_celulas}")

# ---------------------------------------------------------------------------
# 3) Adequabilidade ponderada por floresta + salvar rasters
# ---------------------------------------------------------------------------
adequabilidade_floresta = np.where(
    ~np.isnan(fracao_floresta) & (consenso != nodata),
    consenso * fracao_floresta,
    nodata,
).astype("float32")
fracao_saida = np.where(~np.isnan(fracao_floresta), fracao_floresta, nodata).astype("float32")

for nome_arq, array in [
    ("lagothrix_floresta_fracao.tif", fracao_saida),
    ("lagothrix_adequabilidade_floresta.tif", adequabilidade_floresta),
]:
    with rasterio.open(os.path.join(RESULTADOS, nome_arq), "w", **perfil) as dst:
        dst.write(array, 1)
print("Salvos: Resultados/lagothrix_floresta_fracao.tif, lagothrix_adequabilidade_floresta.tif")

# ---------------------------------------------------------------------------
# 4) Resumo por UC (85 UCs)
# ---------------------------------------------------------------------------
linhas_resumo = []
for _, uc in ucs.iterrows():
    mascara = rasterize(
        [(uc.geometry, 1)], out_shape=(altura, largura), transform=transform,
        all_touched=True, fill=0, dtype="uint8",
    ).astype(bool)
    validos = mascara & (consenso != nodata) & ~np.isnan(fracao_floresta)
    n_celulas = int(validos.sum())
    if n_celulas == 0:
        linhas_resumo.append({
            "nome_uc": uc["nome_uc"], "uf": uc["uf"], "ha_total": uc["ha_total"],
            "n_celulas_sdm": 0, "adequabilidade_media": np.nan,
            "fracao_floresta_media": np.nan, "adequabilidade_floresta_media": np.nan,
            "incerteza_media": np.nan,
            "obs": "UC menor que a resolução da grade do SDM (~18,5 km) — sem célula própria",
        })
        continue
    linhas_resumo.append({
        "nome_uc": uc["nome_uc"], "uf": uc["uf"], "ha_total": uc["ha_total"],
        "n_celulas_sdm": n_celulas,
        "adequabilidade_media": float(consenso[validos].mean()),
        "fracao_floresta_media": float(fracao_floresta[validos].mean()),
        "adequabilidade_floresta_media": float((consenso[validos] * fracao_floresta[validos]).mean()),
        "incerteza_media": float(incerteza[validos].mean()),
        "obs": "",
    })

resumo = pd.DataFrame(linhas_resumo).sort_values(
    "adequabilidade_floresta_media", ascending=False, na_position="last"
)
resumo.to_csv(os.path.join(RESULTADOS, "lagothrix_ranking_ucs.csv"), index=False)

n_sem_celula = (resumo["n_celulas_sdm"] == 0).sum()
print(f"\nUCs sem célula própria na grade do SDM (muito pequenas): {n_sem_celula}/{len(resumo)}")
print("\nTop 10 UCs por adequabilidade ponderada por floresta:")
print(resumo.head(10)[["nome_uc", "uf", "adequabilidade_media", "fracao_floresta_media",
                        "adequabilidade_floresta_media", "incerteza_media"]].to_string(index=False))
print("\nSalvo: Resultados/lagothrix_ranking_ucs.csv")
print("\nConcluído.")
