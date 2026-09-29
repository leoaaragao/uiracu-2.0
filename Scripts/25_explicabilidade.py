# -*- coding: utf-8 -*-
"""Uiraçu 2.0 — Parte 2, Ficha 2.9: explicabilidade (importância de variáveis).

Como os 3 modelos foram ajustados sobre eixos de PCA (não diretamente sobre
as 19 variáveis bioclimáticas), a explicabilidade é feita em duas camadas:

1. Importância de cada eixo de PCA para cada modelo (permutation importance,
   agnóstica ao algoritmo — funciona igual para GLM, Maxent e Random Forest).
2. Composição de cada eixo de PCA em termos das variáveis bioclimáticas
   originais (loadings do script 23) — para interpretar o que "PC1 alto"
   significa biologicamente.
"""
import os

import joblib
import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DADOS = os.path.join(RAIZ, "Dados")
RESULTADOS = os.path.join(RAIZ, "Resultados")
SEED = 42

NOMES_BIO = {
    "bio_1": "Temperatura média anual", "bio_2": "Amplitude diurna média",
    "bio_3": "Isotermalidade", "bio_4": "Sazonalidade da temperatura",
    "bio_5": "Temp. máxima do mês mais quente", "bio_6": "Temp. mínima do mês mais frio",
    "bio_7": "Amplitude térmica anual", "bio_8": "Temp. média do trimestre mais úmido",
    "bio_9": "Temp. média do trimestre mais seco", "bio_10": "Temp. média do trimestre mais quente",
    "bio_11": "Temp. média do trimestre mais frio", "bio_12": "Precipitação anual",
    "bio_13": "Precipitação do mês mais úmido", "bio_14": "Precipitação do mês mais seco",
    "bio_15": "Sazonalidade da precipitação", "bio_16": "Precipitação do trimestre mais úmido",
    "bio_17": "Precipitação do trimestre mais seco", "bio_18": "Precipitação do trimestre mais quente",
    "bio_19": "Precipitação do trimestre mais frio",
}

# ---------------------------------------------------------------------------
# 1) Importância dos eixos de PCA por modelo (permutation importance)
# ---------------------------------------------------------------------------
dados = pd.read_csv(os.path.join(DADOS, "lagothrix_dados_modelagem.csv"))
colunas_pc = [c for c in dados.columns if c.startswith("PC")]
X = dados[colunas_pc].values
y = dados["presenca"].values

modelos = {}
for nome in ["glm", "maxent", "randomforest"]:
    modelos[nome] = joblib.load(os.path.join(RESULTADOS, "modelos", f"{nome}.joblib"))

print("Calculando importância por permutação (agnóstica ao algoritmo)...")
importancias = {}
for nome, modelo in modelos.items():
    scorer = "roc_auc"
    r = permutation_importance(modelo, X, y, n_repeats=20, random_state=SEED, scoring=scorer, n_jobs=1)
    importancias[nome] = r.importances_mean
    print(f"  {nome}: {dict(zip(colunas_pc, np.round(r.importances_mean, 4)))}")

imp_df = pd.DataFrame(importancias, index=colunas_pc)
imp_df["media_modelos"] = imp_df.mean(axis=1)
imp_df = imp_df.sort_values("media_modelos", ascending=False)
imp_df.to_csv(os.path.join(RESULTADOS, "lagothrix_importancia_pca.csv"))
print("\nImportância média dos eixos de PCA (queda no AUC ao embaralhar o eixo):")
print(imp_df.round(4).to_string())

# ---------------------------------------------------------------------------
# 2) Composição de cada eixo em variáveis bioclimáticas originais (loadings)
# ---------------------------------------------------------------------------
loadings = pd.read_csv(os.path.join(DADOS, "lagothrix_pca_loadings.csv"), index_col=0)
loadings["variavel"] = [NOMES_BIO.get(v, v) for v in loadings.index]

resumo_interpretacao = []
for pc in colunas_pc:
    top = loadings[pc].abs().sort_values(ascending=False).head(3)
    descricao = "; ".join(
        f"{loadings.loc[var, 'variavel']} ({loadings.loc[var, pc]:+.2f})" for var in top.index
    )
    resumo_interpretacao.append({
        "eixo": pc,
        "importancia_media": round(imp_df.loc[pc, "media_modelos"], 4),
        "principais_variaveis": descricao,
    })

resumo_df = pd.DataFrame(resumo_interpretacao)
resumo_df.to_csv(os.path.join(RESULTADOS, "lagothrix_interpretacao_pca.csv"), index=False)
print("\nInterpretação biológica de cada eixo (3 variáveis de maior peso):")
print(resumo_df.to_string(index=False))

print("\nConcluído.")
