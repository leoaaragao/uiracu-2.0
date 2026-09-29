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
espacial). Métricas: AUC e TSS (True Skill Statistic) — as duas citadas
explicitamente na metodologia do projeto de doutorado (Etapa 2, seção 4.3).

Depois, ajusta cada modelo com todos os dados e prevê a adequabilidade em
toda a grade de M, gerando:
  - Resultados/lagothrix_<modelo>.tif        (predição individual, 0-1)
  - Resultados/lagothrix_consenso.tif        (média ponderada pelo AUC —
    ensemble de consenso conforme Araújo & New, 2007, citado na tese)
  - Resultados/lagothrix_incerteza.tif       (desvio padrão entre os 3 modelos)
  - Resultados/lagothrix_binario_consenso.tif (apto/não apto por voto
    majoritário, usando o limiar que maximiza o TSS de cada modelo)
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
from sklearn.metrics import roc_auc_score, roc_curve
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


def prever(modelo, X_):
    if hasattr(modelo, "predict_proba"):
        return modelo.predict_proba(X_)[:, 1]
    return modelo.predict(X_)


def tss_maximo(y_verd, pred):
    """TSS = sensibilidade + especificidade - 1, no limiar que maximiza esse valor
    (regra padrão em SDM — Allouche et al. 2006)."""
    fpr, tpr, limiares = roc_curve(y_verd, pred)
    tss_por_limiar = tpr - fpr
    i = int(np.argmax(tss_por_limiar))
    return float(tss_por_limiar[i]), float(limiares[i])


# ---------------------------------------------------------------------------
# 2) Validação cruzada K-fold estratificada (AUC + TSS)
# ---------------------------------------------------------------------------
print(f"\nValidação cruzada ({N_FOLDS}-fold estratificado)...")
skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
resultados_cv = {nome: {"auc": [], "tss": []} for nome in MODELOS}

for fold, (idx_treino, idx_teste) in enumerate(skf.split(X, y), start=1):
    X_treino, X_teste = X[idx_treino], X[idx_teste]
    y_treino, y_teste = y[idx_treino], y[idx_teste]
    for nome, construtor in MODELOS.items():
        modelo = construtor()
        modelo.fit(X_treino, y_treino)
        pred = prever(modelo, X_teste)
        auc = roc_auc_score(y_teste, pred)
        tss, _ = tss_maximo(y_teste, pred)
        resultados_cv[nome]["auc"].append(auc)
        resultados_cv[nome]["tss"].append(tss)
        print(f"  fold {fold} · {nome:12s} AUC = {auc:.3f}  TSS = {tss:.3f}")

print("\nResumo da validação cruzada (média ± desvio padrão):")
resumo_cv = []
for nome, vals in resultados_cv.items():
    auc_m, auc_dp = np.mean(vals["auc"]), np.std(vals["auc"])
    tss_m, tss_dp = np.mean(vals["tss"]), np.std(vals["tss"])
    resumo_cv.append({
        "modelo": nome, "auc_medio": auc_m, "auc_dp": auc_dp,
        "tss_medio": tss_m, "tss_dp": tss_dp,
    })
    print(f"  {nome:12s} AUC {auc_m:.3f} ± {auc_dp:.3f}   TSS {tss_m:.3f} ± {tss_dp:.3f}")
resumo_cv_df = pd.DataFrame(resumo_cv)
resumo_cv_df.to_csv(os.path.join(RESULTADOS, "lagothrix_cv_metricas.csv"), index=False)

# ---------------------------------------------------------------------------
# 3) Ajustar cada modelo com TODOS os dados (para gerar o mapa final)
# ---------------------------------------------------------------------------
print("\nAjustando modelos finais (100% dos dados)...")
modelos_finais = {}
limiares_finais = {}
for nome, construtor in MODELOS.items():
    modelo = construtor()
    modelo.fit(X, y)
    modelos_finais[nome] = modelo
    pred_treino = prever(modelo, X)
    _, limiar = tss_maximo(y, pred_treino)
    limiares_finais[nome] = limiar
    print(f"  {nome} ajustado. Limiar (máx. TSS, dados completos): {limiar:.3f}")

os.makedirs(os.path.join(RESULTADOS, "modelos"), exist_ok=True)
for nome, modelo in modelos_finais.items():
    joblib.dump(modelo, os.path.join(RESULTADOS, "modelos", f"{nome.lower()}.joblib"))

# Pesos do ensemble = AUC médio da validação cruzada, normalizado (Araújo & New, 2007)
pesos = {nome: resumo_cv_df.set_index("modelo").loc[nome, "auc_medio"] for nome in MODELOS}
soma_pesos = sum(pesos.values())
pesos = {nome: w / soma_pesos for nome, w in pesos.items()}
print(f"\nPesos do ensemble (AUC médio normalizado): "
      + ", ".join(f"{n}={w:.3f}" for n, w in pesos.items()))

pd.DataFrame([
    {"modelo": nome, "peso_ensemble_auc": pesos[nome], "limiar_max_tss": limiares_finais[nome]}
    for nome in MODELOS
]).to_csv(os.path.join(RESULTADOS, "lagothrix_pesos_limiares.csv"), index=False)

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
binarios = {}
for nome, modelo in modelos_finais.items():
    pred = prever(modelo, X_grade)
    raster = np.full((altura, largura), -9999.0, dtype="float32")
    raster[linha_idx, coluna_idx] = pred
    predicoes[nome] = raster

    binario = np.full((altura, largura), -9999.0, dtype="float32")
    binario[linha_idx, coluna_idx] = (pred >= limiares_finais[nome]).astype("float32")
    binarios[nome] = binario

    with rasterio.open(os.path.join(RESULTADOS, f"lagothrix_{nome.lower()}.tif"), "w", **perfil_saida) as dst:
        dst.write(raster, 1)
    print(f"  salvo: Resultados/lagothrix_{nome.lower()}.tif "
          f"(min={pred.min():.3f}, média={pred.mean():.3f}, máx={pred.max():.3f})")

# ---------------------------------------------------------------------------
# 5) Consenso ponderado, incerteza e mapa binário (voto majoritário)
# ---------------------------------------------------------------------------
pilha_pred = np.stack(list(predicoes.values()))  # (3, altura, largura)
pesos_array = np.array([pesos[nome] for nome in predicoes.keys()]).reshape(-1, 1, 1)
mascara_valida = pilha_pred[0] != -9999.0

consenso = np.full((altura, largura), -9999.0, dtype="float32")
incerteza = np.full((altura, largura), -9999.0, dtype="float32")
consenso[mascara_valida] = (pilha_pred * pesos_array).sum(axis=0)[mascara_valida]
incerteza[mascara_valida] = pilha_pred[:, mascara_valida].std(axis=0)

pilha_bin = np.stack(list(binarios.values()))
binario_consenso = np.full((altura, largura), -9999.0, dtype="float32")
votos = pilha_bin[:, mascara_valida].sum(axis=0)  # 0 a 3 modelos concordando
binario_consenso[mascara_valida] = (votos >= 2).astype("float32")  # maioria (>=2 de 3)

for nome_arq, array in [
    ("lagothrix_consenso.tif", consenso),
    ("lagothrix_incerteza.tif", incerteza),
    ("lagothrix_binario_consenso.tif", binario_consenso),
]:
    with rasterio.open(os.path.join(RESULTADOS, nome_arq), "w", **perfil_saida) as dst:
        dst.write(array, 1)

area_apta_pct = 100 * (binario_consenso[mascara_valida] == 1).mean()
print(f"\nConsenso ponderado salvo: Resultados/lagothrix_consenso.tif "
      f"(média={consenso[mascara_valida].mean():.3f})")
print(f"Incerteza salva: Resultados/lagothrix_incerteza.tif "
      f"(desvio padrão médio={incerteza[mascara_valida].mean():.3f})")
print(f"Mapa binário salvo: Resultados/lagothrix_binario_consenso.tif "
      f"({area_apta_pct:.1f}% de M classificada como apta por maioria dos modelos)")
print("\nConcluído.")
