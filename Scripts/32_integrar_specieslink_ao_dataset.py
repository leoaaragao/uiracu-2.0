# -*- coding: utf-8 -*-
"""Uiraçu 2.0 — Parte 1 (tese): integra os registros válidos do speciesLink ao dataset principal.

Cria `Referencias/ocorrencias_primatas_brasil_integrado.csv` = dataset original (só GBIF,
`ocorrencias_primatas_brasil_gbif.csv`, intocado) + os registros do speciesLink que sobreviveram
a TODOS os filtros (Scripts/28-31): espécie com nome aceito resolvido no GBIF, região-alvo,
genuinamente não duplicado (nome aceito + coordenada) e temporalmente válido (>= 1970).

Decisão de manter dois arquivos separados (em vez de sobrescrever o `_gbif.csv`): preserva a
proveniência — o arquivo original continua sendo só GBIF (para qualquer reprodução/auditoria que
precise disso), e o integrado é usado só na Parte 1 (riqueza/ranking multiespécie). A Parte 2
(SDM de *Lagothrix lagothricha*) NÃO usa este arquivo — decisão explícita, ver ROTEIRO_DO_PROJETO.md
Etapa 34: o ganho de dados ali é pequeno demais (1 ponto) para justificar reprocessar rarefação/
área M/ensemble.
"""
import os

import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFERENCIAS = os.path.join(RAIZ, "Referencias")
RESULTADOS = os.path.join(RAIZ, "Resultados")

gbif = pd.read_csv(os.path.join(REFERENCIAS, "ocorrencias_primatas_brasil_gbif.csv"), low_memory=False)
novos = pd.read_csv(os.path.join(RESULTADOS, "specieslink_registros_novos_validos_harmonizado.csv"), low_memory=False)
harmon = pd.read_csv(os.path.join(RESULTADOS, "specieslink_harmonizacao_taxonomica.csv"))

novos = novos.merge(
    harmon[["nome_specieslink", "usageKey"]],
    left_on="scientificname", right_on="nome_specieslink", how="left",
)

CAMPOS = ["genero_consultado", "key", "scientificName", "species", "taxonKey", "speciesKey",
          "decimalLatitude", "decimalLongitude", "coordinateUncertaintyInMeters",
          "year", "basisOfRecord", "datasetName", "level1Name", "countryCode"]

integrado_novos = pd.DataFrame({
    "genero_consultado": novos["genus"],
    "key": ["specieslink_" + str(cn) for cn in novos.get("catalognumber", novos.index)],
    "scientificName": novos["scientificname"],
    "species": novos["species"],
    "taxonKey": novos["usageKey"],
    "speciesKey": novos["usageKey"],
    "decimalLatitude": novos["decimallatitude"],
    "decimalLongitude": novos["decimallongitude"],
    "coordinateUncertaintyInMeters": pd.NA,
    "year": novos["yearcollected"],
    "basisOfRecord": novos["basisofrecord"],
    "datasetName": "speciesLink (CRIA)",
    "level1Name": novos["stateprovince"],
    "countryCode": "BR",
})[CAMPOS]

integrado = pd.concat([gbif[CAMPOS], integrado_novos], ignore_index=True)
saida = os.path.join(REFERENCIAS, "ocorrencias_primatas_brasil_integrado.csv")
integrado.to_csv(saida, index=False, encoding="utf-8-sig")

print(f"Dataset original (GBIF): {len(gbif)} registros, {gbif['species'].nunique()} espécies")
print(f"Registros adicionados do speciesLink: {len(integrado_novos)}")
print(f"Dataset integrado: {len(integrado)} registros, {integrado['species'].nunique()} espécies")
print(f"\nEspécies novas no dataset integrado (não existiam no GBIF sozinho):")
novas_especies = set(integrado["species"].dropna()) - set(gbif["species"].dropna())
print(sorted(novas_especies) if novas_especies else "  (nenhuma — todas as espécies do speciesLink já tinham pelo menos 1 registro via GBIF)")
print(f"\nSalvo: {saida}")
