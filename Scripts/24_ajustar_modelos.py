# -*- coding: utf-8 -*-
"""Uiraçu 2.0 — Parte 2, Fichas 2.6 a 2.8: modelos, validação cruzada, consenso.

Ajusta 3 algoritmos sobre os eixos de PCA (script 23):
  - GLM (regressão logística, sklearn)
  - Maxent (biblioteca `elapid` — substitui o software Maxent original de
    Phillips et al., declarado no relatório final como substituição de
    ferramenta)
  - Random Forest (sklearn)

Validação cruzada K-fold (5 folds, estratificada por presença/background —
conforme orientação da disciplina para amostras pequenas, sem bloqueio
espacial). Depois, ajusta cada modelo com todos os dados e prevê a
adequabilidade em toda a grade de M, gerando:
  - Resultados/lagothrix_consenso.tif   (média dos 3 modelos, 0-1)
  - Resultados/lagothrix_incerteza.tif  (desvio padrão entre os 3 modelos)
  - Resultados/lagothrix_<modelo>.tif   (predição individual de cada modelo)
"""
import json
import os

import joblib
import numpy as np
import pandas as pd
import rasterio
from elapid import MaxentModel
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DADOS = os.path.join(RAIZ, "Dados")
RESULTADOS = os.path.join(RAIZ, "Resultados")
os.makedirs(RESULTADOS, exist_ok=True)

SEED = 42
N_FOLDS = 5

# ---------------------------------------------------------------------------
# 1) Carregar dados de modelagem (presença + background, eixos de PCA)
# ---------------------------------------------------------------------------
dados = pd.read_csv(os.path.join(DADOS, "lagothrix_dados_modelagem.csv"))
colunas_pc = [c for c in dados.columns if c.startswith("PC")]
X = dados[colunas_pc].values
y = dados["presenca"].values
print(f"Dados de modelagem: {len(dados)} pontos ({y.sum()} presença, {(y==0).sum()} background), "
      f"{len(colunas_pc)} eixos de PCA: {colunas_pc}")


def novo_glm():
    return LogisticRegression(class_weight="balanced", max_iter=2000, random_state=SEED)


def novo_maxent():
    return MaxentModel(feature_types=["linear", "quadratic", "hinge"], random_state=SEED, n_cpus=4)


def novo_rf():
    return RandomForestClassifier(n_estimators=500, class_weight="balanced", random_state=SEED, n_jobs=4)


MODELOS = {"GLM": novo_glm, "Maxent": novo_maxent, "RandomForest": novo_rf}

# ---------------------------------------------------------------------------
# 2) Validação cruzada K-fold estratificada
# ---------------------------------------------------------------------------
print(f"\nValidação cruzada ({N_FOLDS}-fold estratificado)...")
skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
resultados_cv = {nome: [] for nome in MODELOS}

for fold, (idx_treino, idx_teste) in enumerate(skf.split(X, y), start=1):
    X_treino, X_teste = X[idx_treino], X[idx_teste]
    y_treino, y_teste = y[idx_treino], y[idx_teste]
    for nome, construtor in MODELOS.items():
        modelo = construtor()
        modelo.fit(X_treino, y_treino)
        if hasattr(modelo, "predict_proba"):
            pred = modelo.predict_proba(X_teste)[:, 1]
        else:
            pred = modelo.predict(X_teste)
        auc = roc_auc_score(y_teste, pred)
        resultados_cv[nome].append(auc)
        print(f"  fold {fold} · {nome:12s} AUC = {auc:.3f}")

print("\nResumo da validação cruzada (AUC médio ± desvio padrão):")
resumo_cv = []
for nome, aucs in resultados_cv.items():
    media, dp = np.mean(aucs), np.std(aucs)
    resumo_cv.append({"modelo": nome, "auc_medio": media, "auc_dp": dp})
    print(f"  {nome:12s} {media:.3f} ± {dp:.3f}")
pd.DataFrame(resumo_cv).to_csv(os.path.join(RESULTADOS, "lagothrix_cv_auc.csv"), index=False)

# ---------------------------------------------------------------------------
# 3) Ajustar cada modelo com TODOS os dados (para gerar o mapa final)
# ---------------------------------------------------------------------------
print("\nAjustando modelos finais (100% dos dados)...")
modelos_finais = {}
for nome, construtor in MODELOS.items():
    modelo = construtor()
    modelo.fit(X, y)
    modelos_finais[nome] = modelo
    print(f"  {nome} ajustado.")

os.makedirs(os.path.join(RESULTADOS, "modelos"), exist_ok=True)
for nome, modelo in modelos_finais.items():
    joblib.dump(modelo, os.path.join(RESULTADOS, "modelos", f"{nome.lower()}.joblib"))

# ---------------------------------------------------------------------------
# 4) Prever em toda a grade de M
# ---------------------------------------------------------------------------
grade = pd.read_csv(os.path.join(DADOS, "lagothrix_grade_pca.csv"))
with open(os.path.join(DADOS, "lagothrix_grade_meta.json")) as f:
    meta = json.load(f)

X_grade = grade[colunas_pc].values
altura, largura = meta["altura"], meta["largura"]
transform = rasterio.Affine(*meta["transform"])
linha_idx = grade["linha"].values
coluna_idx = grade["coluna"].values

perfil_saida = {
    "driver": "GTiff", "dtype": "float32", "count": 1,
    "height": altura, "width": largura, "transform": transform,
    "crs": meta["crs"], "nodata": -9999.0,
}

predicoes = {}
for nome, modelo in modelos_finais.items():
    if hasattr(modelo, "predict_proba"):
        pred = modelo.predict_proba(X_grade)[:, 1]
    else:
        pred = modelo.predict(X_grade)
    raster = np.full((altura, largura), -9999.0, dtype="float32")
    raster[linha_idx, coluna_idx] = pred
    predicoes[nome] = raster
    with rasterio.open(os.path.join(RESULTADOS, f"lagothrix_{nome.lower()}.tif"), "w", **perfil_saida) as dst:
        dst.write(raster, 1)
    print(f"  salvo: Resultados/lagothrix_{nome.lower()}.tif "
          f"(min={pred.min():.3f}, média={pred.mean():.3f}, máx={pred.max():.3f})")

# ---------------------------------------------------------------------------
# 5) Consenso (média) e incerteza (desvio padrão entre os 3 modelos)
# ---------------------------------------------------------------------------
pilha_pred = np.stack(list(predicoes.values()))  # (3, altura, largura)
mascara_valida = pilha_pred[0] != -9999.0

consenso = np.full((altura, largura), -9999.0, dtype="float32")
incerteza = np.full((altura, largura), -9999.0, dtype="float32")
consenso[mascara_valida] = pilha_pred[:, mascara_valida].mean(axis=0)
incerteza[mascara_valida] = pilha_pred[:, mascara_valida].std(axis=0)

with rasterio.open(os.path.join(RESULTADOS, "lagothrix_consenso.tif"), "w", **perfil_saida) as dst:
    dst.write(consenso, 1)
with rasterio.open(os.path.join(RESULTADOS, "lagothrix_incerteza.tif"), "w", **perfil_saida) as dst:
    dst.write(incerteza, 1)

print(f"\nConsenso salvo: Resultados/lagothrix_consenso.tif "
      f"(média={consenso[mascara_valida].mean():.3f})")
print(f"Incerteza salva: Resultados/lagothrix_incerteza.tif "
      f"(desvio padrão médio={incerteza[mascara_valida].mean():.3f})")
print("\nConcluído.")
