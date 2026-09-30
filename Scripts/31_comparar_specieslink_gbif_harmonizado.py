# -*- coding: utf-8 -*-
"""Uiraçu 2.0 — Parte 1 (tese): comparação speciesLink × GBIF, com nomes harmonizados.

Versão corrigida do Scripts/29. Ao inspecionar os 58 registros "novos e temporalmente
válidos" daquele script, ficou claro que o nome usado (`scientificname`, verbatim de cada
coleção) não é o nome aceito atual do backbone do GBIF — ex.: o speciesLink cataloga
"Lagothrix lagotricha" e "Lagothrix lugens", enquanto o dataset já usado no projeto (e o
GBIF hoje) reconhece só "Lagothrix lagothricha". Comparar pelo nome verbatim comete o MESMO
erro da Etapa 33 (falso positivo do ICMBio): duas fontes podem descrever a mesma espécie,
no mesmo lugar, com nomes de texto diferentes, e uma chave de deduplicação por nome textual
não percebe que são a mesma coisa.

Correção: toda comparação aqui usa o nome de espécie ACEITO pelo GBIF
(`Resultados/specieslink_harmonizacao_taxonomica.csv`, gerado pelo Scripts/30 via
species/match do GBIF — mesmo endpoint/parâmetros do Scripts/02), não o nome verbatim do
speciesLink. Registros sem nome de espécie resolvido (nível gênero/ordem/indeterminado,
ex. "Primates", "Cebus sp.") são descartados — não podem entrar numa matriz de riqueza por
espécie.
"""
import os

import numpy as np
import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DADOS = os.path.join(RAIZ, "Dados")
RESULTADOS = os.path.join(RAIZ, "Resultados")
os.makedirs(RESULTADOS, exist_ok=True)

ANO_MINIMO_ACEITAVEL = 1970  # normal climatica WorldClim v2.1 (worldclim.org: "1970-2000")

ESTADOS_ALVO = [
    "Acre", "Amazonas", "Roraima", "Estado de Amazonas", "Territorio Federal Amazonas",
]


def chave_tolerante(especie, lat, lon, casas=2):
    lat_r = np.round(pd.to_numeric(lat, errors="coerce"), casas)
    lon_r = np.round(pd.to_numeric(lon, errors="coerce"), casas)
    return especie.astype(str).str.strip().str.lower() + "|" + lat_r.astype(str) + "|" + lon_r.astype(str)


sl = pd.read_csv(os.path.join(DADOS, "specieslink_primatas_bruto.csv"), low_memory=False)
harmon = pd.read_csv(os.path.join(RESULTADOS, "specieslink_harmonizacao_taxonomica.csv"))
atual = pd.read_csv(os.path.join(RAIZ, "Referencias", "ocorrencias_primatas_brasil_gbif.csv"), low_memory=False)

sl = sl.merge(
    harmon[["nome_specieslink", "species_aceito_gbif", "status"]],
    left_on="scientificname", right_on="nome_specieslink", how="left",
)

n_total = len(sl)
n_sem_especie = sl["species_aceito_gbif"].isna().sum()
print(f"speciesLink, registros na caixa geográfica: {n_total}")
print(f"  Sem nome de espécie aceito resolvido (gênero/ordem/indeterminado, descartados): {n_sem_especie}")
sl = sl[sl["species_aceito_gbif"].notna()].copy()

mascara_estado = sl["stateprovince"].isin(ESTADOS_ALVO) | sl["stateprovince"].astype(str).str.startswith("Rond", na=False)
sl_br = sl[mascara_estado].copy()
print(f"  Restritos a AM/AC/RO/RR (com espécie resolvida): {len(sl_br)}")

sl_br["chave"] = chave_tolerante(sl_br["species_aceito_gbif"], sl_br["decimallatitude"], sl_br["decimallongitude"])
atual["chave"] = chave_tolerante(atual["species"], atual["decimalLatitude"], atual["decimalLongitude"])

ja_temos = set(atual["chave"])
sl_br["ja_temos_via_gbif"] = sl_br["chave"].isin(ja_temos)

n_ja_temos = int(sl_br["ja_temos_via_gbif"].sum())
n_novos = int((~sl_br["ja_temos_via_gbif"]).sum())
print(f"\nJá temos (espécie ACEITA + coordenada arred. a 2 casas, já no dataset GBIF): {n_ja_temos}")
print(f"Potencialmente novos: {n_novos}")

novos = sl_br[~sl_br["ja_temos_via_gbif"]].copy()

ano_num = pd.to_numeric(novos["yearcollected"], errors="coerce")
novos["ano_valido_temporalmente"] = ano_num >= ANO_MINIMO_ACEITAVEL
n_sem_ano = int(ano_num.isna().sum())
n_antigos = int(((~ano_num.isna()) & (ano_num < ANO_MINIMO_ACEITAVEL)).sum())
n_novos_validos = int(novos["ano_valido_temporalmente"].sum())

print(f"\n--- Filtro temporal (corte >= {ANO_MINIMO_ACEITAVEL}, normal climática WorldClim) ---")
print(f"Novos (antes do filtro temporal): {len(novos)}")
print(f"  Sem ano determinável (excluídos): {n_sem_ano}")
print(f"  Com ano < {ANO_MINIMO_ACEITAVEL} (excluídos, espécime histórico): {n_antigos}")
print(f"  Novos E temporalmente válidos (>= {ANO_MINIMO_ACEITAVEL}): {n_novos_validos}")

novos_validos = novos[novos["ano_valido_temporalmente"]].copy()
novos_validos = novos_validos.rename(columns={"species_aceito_gbif": "species"})

colunas_saida = [
    "species", "scientificname", "genus", "yearcollected", "basisofrecord",
    "country", "stateprovince", "county", "locality",
    "decimallatitude", "decimallongitude",
    "institutioncode", "collectioncode", "catalognumber", "recordedby",
]
colunas_saida = [c for c in colunas_saida if c in novos_validos.columns]
novos_validos[colunas_saida].to_csv(
    os.path.join(RESULTADOS, "specieslink_registros_novos_validos_harmonizado.csv"), index=False, encoding="utf-8-sig"
)
novos.to_csv(os.path.join(RESULTADOS, "specieslink_registros_novos_harmonizado.csv"), index=False, encoding="utf-8-sig")
sl_br.to_csv(os.path.join(RESULTADOS, "specieslink_comparacao_completa_harmonizado.csv"), index=False, encoding="utf-8-sig")

print(f"\n--- Espécies entre os {n_novos_validos} registros novos E temporalmente válidos (nome ACEITO) ---")
print(novos_validos["species"].value_counts().to_string())

print("\n--- Gênero Lagothrix (nome aceito) nos registros novos E temporalmente válidos ---")
lago = novos_validos[novos_validos["species"] == "Lagothrix lagothricha"]
print(f"Total de registros: {len(lago)}")
if len(lago):
    print(lago[["scientificname", "yearcollected", "stateprovince", "decimallatitude", "decimallongitude"]].to_string(index=False))
    localidades_unicas = lago[["decimallatitude", "decimallongitude"]].round(2).drop_duplicates()
    print(f"Localidades espacialmente únicas (coordenada arred. a 2 casas): {len(localidades_unicas)}")

print(f"\nSalvo: Resultados/specieslink_registros_novos_validos_harmonizado.csv ({len(novos_validos)} registros)")
print("Salvo: Resultados/specieslink_registros_novos_harmonizado.csv")
print("Salvo: Resultados/specieslink_comparacao_completa_harmonizado.csv")
