# -*- coding: utf-8 -*-
"""Uiraçu 2.0 — Parte 2, Ficha 2.5: background (pseudo-ausências) e PCA.

1. Gera pontos de background (pseudo-ausência) aleatórios dentro da área M.
2. Extrai os valores das 19 variáveis bioclimáticas (WorldClim, recortadas no
   script 22) em todas as células válidas de M, nos pontos de presença e nos
   pontos de background.
3. Ajusta um PCA sobre o espaço ambiental completo de M (todas as células
   válidas) e projeta presença/background nesse mesmo espaço — evita que o
   PCA seja enviesado pela amostragem dos pontos.
4. Seleciona os eixos que somam >90% da variância explicada.
5. Salva a tabela final (presença=1 / background=0 + escores de PCA) para uso
   direto no ajuste dos modelos (script 24).

Referência de método: aula da disciplina — variável ambiental de background
= toda a extensão de M, não apenas os pontos observados.
"""
import os
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from shapely.geometry import Point
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DADOS = os.path.join(RAIZ, "Dados")
WC_DIR = os.path.join(DADOS, "worldclim_M")
M_PATH = os.path.join(DADOS, "area_M_lagothrix_dissolvido.gpkg")
PONTOS_PATH = os.path.join(DADOS, "FO01_06_ocorrencias_rarefeitas.csv")

N_BACKGROUND = 5000
SEED = 42
np.random.seed(SEED)

BIOCLIM_VARS = [f"bio_{i}" for i in range(1, 20)]
RASTER_FILES = {f"bio_{i}": os.path.join(WC_DIR, f"wc2.1_10m_bio_{i}_M.tif") for i in range(1, 20)}

# ---------------------------------------------------------------------------
# 1) Empilhar as 19 bandas e mapear todas as células válidas dentro de M
# ---------------------------------------------------------------------------
print("Carregando rasters recortados...")
with rasterio.open(RASTER_FILES["bio_1"]) as ref:
    perfil = ref.profile
    transform = ref.transform
    altura, largura = ref.shape
    nodata = ref.nodata

pilha = np.zeros((19, altura, largura), dtype="float32")
for i in range(1, 20):
    with rasterio.open(RASTER_FILES[f"bio_{i}"]) as src:
        pilha[i - 1] = src.read(1)

mascara_valida = ~np.any(pilha == nodata, axis=0) if nodata is not None else np.all(~np.isnan(pilha), axis=0)
linhas, colunas = np.where(mascara_valida)
print(f"Células válidas dentro de M: {len(linhas)} (grade {altura}x{largura})")

# Coordenadas (centro de célula) de cada célula válida
xs, ys = rasterio.transform.xy(transform, linhas, colunas)
env_espaco = pd.DataFrame({"lon": xs, "lat": ys})
for i, var in enumerate(BIOCLIM_VARS):
    env_espaco[var] = pilha[i, linhas, colunas]

# ---------------------------------------------------------------------------
# 2) Background: sortear N_BACKGROUND células válidas dentro de M (sem repetição)
# ---------------------------------------------------------------------------
n_disponiveis = len(env_espaco)
n_amostra = min(N_BACKGROUND, n_disponiveis)
idx_bg = np.random.choice(n_disponiveis, size=n_amostra, replace=False)
background = env_espaco.iloc[idx_bg].copy().reset_index(drop=True)
background["presenca"] = 0
print(f"Background gerado: {len(background)} pontos dentro de M.")

# ---------------------------------------------------------------------------
# 3) Extrair valores das variáveis nos 37 pontos de presença
# ---------------------------------------------------------------------------
pontos_df = pd.read_csv(PONTOS_PATH)
coords = list(zip(pontos_df["decimalLongitude"], pontos_df["decimalLatitude"]))

presenca_vals = {var: [] for var in BIOCLIM_VARS}
with rasterio.open(RASTER_FILES["bio_1"]) as ref:
    for i in range(1, 20):
        with rasterio.open(RASTER_FILES[f"bio_{i}"]) as src:
            presenca_vals[f"bio_{i}"] = [v[0] for v in src.sample(coords)]

presenca = pd.DataFrame(presenca_vals)
presenca.insert(0, "lat", pontos_df["decimalLatitude"].values)
presenca.insert(0, "lon", pontos_df["decimalLongitude"].values)
presenca["presenca"] = 1

# Remover presenças que caíram em célula nodata (fora da máscara de M, ex.: borda)
antes = len(presenca)
presenca = presenca[(presenca[BIOCLIM_VARS] != nodata).all(axis=1)].reset_index(drop=True) if nodata is not None else presenca.dropna().reset_index(drop=True)
print(f"Presenças com dados ambientais válidos: {len(presenca)}/{antes}")

# ---------------------------------------------------------------------------
# 4) PCA ajustado sobre TODO o espaço ambiental de M, projetado em presença+background
# ---------------------------------------------------------------------------
scaler = StandardScaler().fit(env_espaco[BIOCLIM_VARS])
env_padronizado = scaler.transform(env_espaco[BIOCLIM_VARS])

pca_completo = PCA(n_components=len(BIOCLIM_VARS), random_state=SEED).fit(env_padronizado)
variancia_acumulada = np.cumsum(pca_completo.explained_variance_ratio_)
n_eixos = int(np.searchsorted(variancia_acumulada, 0.90) + 1)
print(f"PCA: {n_eixos} eixos explicam {variancia_acumulada[n_eixos-1]*100:.1f}% da variância "
      f"(critério: >90%).")

pca = PCA(n_components=n_eixos, random_state=SEED).fit(env_padronizado)
colunas_pca = [f"PC{i+1}" for i in range(n_eixos)]

def projetar(df):
    padronizado = scaler.transform(df[BIOCLIM_VARS])
    escores = pca.transform(padronizado)
    for i, col in enumerate(colunas_pca):
        df[col] = escores[:, i]
    return df

presenca = projetar(presenca)
background = projetar(background)
env_espaco = projetar(env_espaco)  # toda a grade válida de M, para gerar o mapa contínuo depois

# ---------------------------------------------------------------------------
# 5) Salvar saídas
# ---------------------------------------------------------------------------
dados_modelagem = pd.concat([
    presenca[["lon", "lat", "presenca"] + BIOCLIM_VARS + colunas_pca],
    background[["lon", "lat", "presenca"] + BIOCLIM_VARS + colunas_pca],
], ignore_index=True)
dados_modelagem.to_csv(os.path.join(DADOS, "lagothrix_dados_modelagem.csv"), index=False)
print(f"Salvo: Dados/lagothrix_dados_modelagem.csv ({len(dados_modelagem)} linhas: "
      f"{len(presenca)} presença + {len(background)} background)")

# Loadings do PCA (para a etapa de explicabilidade)
loadings = pd.DataFrame(
    pca.components_.T, index=BIOCLIM_VARS, columns=colunas_pca
)
loadings.to_csv(os.path.join(DADOS, "lagothrix_pca_loadings.csv"))

variancia_df = pd.DataFrame({
    "componente": [f"PC{i+1}" for i in range(len(BIOCLIM_VARS))],
    "variancia_explicada": pca_completo.explained_variance_ratio_,
    "variancia_acumulada": variancia_acumulada,
})
variancia_df.to_csv(os.path.join(DADOS, "lagothrix_pca_variancia.csv"), index=False)

# Grade completa projetada no PCA (para prever a superfície contínua no script 24)
env_espaco[["lon", "lat"] + colunas_pca].assign(linha=linhas, coluna=colunas).to_csv(
    os.path.join(DADOS, "lagothrix_grade_pca.csv"), index=False
)
import json
with open(os.path.join(DADOS, "lagothrix_grade_meta.json"), "w") as f:
    json.dump({
        "altura": altura, "largura": largura,
        "transform": list(transform)[:6],
        "crs": "EPSG:4326",
        "n_eixos_pca": n_eixos,
    }, f, indent=2)

# Background como camada espacial (para o dashboard / conferência visual)
bg_gdf = gpd.GeoDataFrame(
    background, geometry=[Point(xy) for xy in zip(background["lon"], background["lat"])], crs="EPSG:4326"
)
bg_gdf[["presenca", "geometry"]].to_file(os.path.join(DADOS, "lagothrix_background.gpkg"), driver="GPKG")

print("\nResumo do PCA:")
print(variancia_df.head(n_eixos + 1).to_string(index=False))
print("\nConcluído.")
