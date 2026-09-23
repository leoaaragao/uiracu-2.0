"""
Ficha simples 02 / preparacao - Rarefacao (thinning) espacial.
Reduz o efeito museu/coleta: para cada par de pontos mais proximos que
DIST_MIN_KM, mantem apenas um (o de menor incerteza de coordenada, quando
disponivel; senao, aleatorio com semente fixa para reprodutibilidade).

Baseado na orientacao da aula de 22-23/09/2026 (thinning de 50 km aplicado
ao caso da castanheira).
"""
import numpy as np
import pandas as pd
from math import radians, sin, cos, asin, sqrt

DIST_MIN_KM = 50
SEED = 42

log = pd.read_csv("Dados/FO01_04_log_auditoria.csv")
occ = pd.read_csv("Dados/FO01_03_ocorrencias_auditadas.csv")

usaveis = occ[
    occ["audit_decisao"].isin(["MANTER", "MANTER_COM_RESSALVA"])
    & occ["gbifID"].isin(log.loc[~log["c3_fora_estados_alvo"], "gbifID"])
].copy()
print(f"Registros utilizaveis antes da rarefacao: {len(usaveis)}")

def haversine_km(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * 6371 * asin(sqrt(a))

usaveis = usaveis.sort_values(
    "coordinateUncertaintyInMeters", na_position="last"
).reset_index(drop=True)  # prioriza manter os de menor incerteza

rng = np.random.default_rng(SEED)
ordem = rng.permutation(usaveis.index[usaveis["coordinateUncertaintyInMeters"].isna()])
# entre os de incerteza desconhecida, ordem aleatoria (mas reprodutivel); os
# de incerteza conhecida ja vem primeiro, priorizados

mantidos = []
for idx, row in usaveis.iterrows():
    muito_perto = False
    for j in mantidos:
        outro = usaveis.loc[j]
        d = haversine_km(row["decimalLatitude"], row["decimalLongitude"],
                          outro["decimalLatitude"], outro["decimalLongitude"])
        if d < DIST_MIN_KM:
            muito_perto = True
            break
    if not muito_perto:
        mantidos.append(idx)

rarefeitos = usaveis.loc[mantidos].copy()
print(f"Registros apos rarefacao ({DIST_MIN_KM} km): {len(rarefeitos)}")
print(f"Removidos por proximidade: {len(usaveis) - len(rarefeitos)}")

rarefeitos.to_csv("Dados/FO01_06_ocorrencias_rarefeitas.csv", index=False, encoding="utf-8-sig")

print("\nDistribuicao por estado (GBIF level1Name) antes vs depois:")
print(pd.DataFrame({
    "antes": usaveis["level1Name"].value_counts(),
    "depois": rarefeitos["level1Name"].value_counts(),
}).fillna(0).astype(int))

print("\nSalvo: Dados/FO01_06_ocorrencias_rarefeitas.csv")
