# -*- coding: utf-8 -*-
"""Uiraçu 2.0 — Parte 1 (tese): comparação speciesLink × GBIF (deduplicação).

Compara os registros baixados via speciesLink (Scripts/28) com o dataset já usado no projeto
(via GBIF), para identificar registros genuinamente novos, não apenas reharvesteados da mesma
fonte primária — lição aprendida na Etapa 33 (o caso ICMBio/SISBio, onde uma comparação por
coordenada EXATA deu falso positivo de "tudo novo", por diferença de precisão entre provedores).

Método de deduplicação: chave = espécie (minúsculo) + coordenada arredondada a 2 casas decimais
(~1 km de tolerância) — deliberadamente frouxo, para não repetir o erro anterior, às custas de
uma pequena chance de sub-contar coincidências reais muito próximas de registros distintos.
"""
import os

import numpy as np
import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DADOS = os.path.join(RAIZ, "Dados")
RESULTADOS = os.path.join(RAIZ, "Resultados")
os.makedirs(RESULTADOS, exist_ok=True)

# Corte temporal: WorldClim v2.1 (usado no projeto) representa a normal climatica de
# ~1970-2000. Especimes coletados antes disso (ou sem data determinavel) nao tem
# correspondencia confiavel com o clima que o SDM usa como referencia -- registrar
# a especie ali em 1810 nao diz nada sobre adequabilidade sob o clima atual, ainda mais
# depois de 2 seculos de mudanca de uso da terra. Orientacao confirmada com a professora.
ANO_MINIMO_ACEITAVEL = 1970

ESTADOS_ALVO = [
    "Acre", "Amazonas", "Roraima", "Estado de Amazonas", "Territorio Federal Amazonas",
]


def chave_tolerante(especie, lat, lon, casas=2):
    lat_r = np.round(pd.to_numeric(lat, errors="coerce"), casas)
    lon_r = np.round(pd.to_numeric(lon, errors="coerce"), casas)
    return especie.astype(str).str.strip().str.lower() + "|" + lat_r.astype(str) + "|" + lon_r.astype(str)


sl = pd.read_csv(os.path.join(DADOS, "specieslink_primatas_bruto.csv"), low_memory=False)
atual = pd.read_csv(os.path.join(RAIZ, "Referencias", "ocorrencias_primatas_brasil_gbif.csv"), low_memory=False)

mascara_estado = sl["stateprovince"].isin(ESTADOS_ALVO) | sl["stateprovince"].astype(str).str.startswith("Rond", na=False)
sl_br = sl[mascara_estado].copy()
print(f"speciesLink, registros na caixa geográfica: {len(sl)}")
print(f"speciesLink, restritos a AM/AC/RO/RR: {len(sl_br)}")

sl_br["chave"] = chave_tolerante(sl_br["scientificname"], sl_br["decimallatitude"], sl_br["decimallongitude"])
atual["chave"] = chave_tolerante(atual["species"], atual["decimalLatitude"], atual["decimalLongitude"])

ja_temos = set(atual["chave"])
sl_br["ja_temos_via_gbif"] = sl_br["chave"].isin(ja_temos)

n_ja_temos = int(sl_br["ja_temos_via_gbif"].sum())
n_novos = int((~sl_br["ja_temos_via_gbif"]).sum())
print(f"\nJá temos (espécie + coordenada arred. a 2 casas, já no dataset GBIF): {n_ja_temos}")
print(f"Potencialmente novos: {n_novos}")

novos = sl_br[~sl_br["ja_temos_via_gbif"]].copy()

# Filtro temporal (orientação da professora, Etapa 34): descarta espécimes históricos de
# museu, cuja data de coleta antecede a normal climática do WorldClim (~1970-2000), e
# descarta também os registros SEM ano determinável, por não ser possível verificar se
# são compatíveis -- não dá para presumir "recente" na ausência de dado.
ano_num = pd.to_numeric(novos["yearcollected"], errors="coerce")
novos["ano_valido_temporalmente"] = ano_num >= ANO_MINIMO_ACEITAVEL

n_novos_bruto = len(novos)
n_sem_ano = int(ano_num.isna().sum())
n_antigos = int(((~ano_num.isna()) & (ano_num < ANO_MINIMO_ACEITAVEL)).sum())
n_novos_validos = int(novos["ano_valido_temporalmente"].sum())

novos.to_csv(os.path.join(RESULTADOS, "specieslink_registros_novos.csv"), index=False)
sl_br.to_csv(os.path.join(RESULTADOS, "specieslink_comparacao_completa.csv"), index=False)

print("\n--- Distribuição de ano (registros já existentes vs. novos) ---")
print("Já tínhamos (mediana):", sl_br[sl_br["ja_temos_via_gbif"]]["yearcollected"].median())
print("Novos, bruto (mediana):", novos["yearcollected"].median())
print("Dataset atual, ano mediano geral:", atual["year"].median())

print(f"\n--- Filtro temporal (corte >= {ANO_MINIMO_ACEITAVEL}, normal climática WorldClim) ---")
print(f"Novos (antes do filtro temporal): {n_novos_bruto}")
print(f"  Sem ano determinável (excluídos, indeterminável): {n_sem_ano}")
print(f"  Com ano < {ANO_MINIMO_ACEITAVEL} (excluídos, espécime histórico): {n_antigos}")
print(f"  Novos E temporalmente válidos (>= {ANO_MINIMO_ACEITAVEL}): {n_novos_validos}")

novos_validos = novos[novos["ano_valido_temporalmente"]].copy()
novos_validos.to_csv(os.path.join(RESULTADOS, "specieslink_registros_novos_validos.csv"), index=False)

print("\n--- Top 15 espécies dos registros novos E temporalmente válidos ---")
print(novos_validos["scientificname"].value_counts().head(15).to_string())

print("\n--- Gênero Lagothrix nos registros novos E temporalmente válidos (relevante para a Parte 2) ---")
lago = novos_validos[novos_validos["scientificname"].str.contains("Lagothrix", case=False, na=False)]
print(lago["scientificname"].value_counts().to_string())
if len(lago):
    print(lago[["scientificname", "yearcollected", "stateprovince", "decimallatitude", "decimallongitude"]].to_string(index=False))

print(f"\nSalvo: Resultados/specieslink_registros_novos.csv ({len(novos)} registros — novos, SEM filtro temporal, com coluna ano_valido_temporalmente)")
print(f"Salvo: Resultados/specieslink_registros_novos_validos.csv ({len(novos_validos)} registros — novos E temporalmente válidos)")
print("Salvo: Resultados/specieslink_comparacao_completa.csv (todos os 1.028, com a flag ja_temos_via_gbif)")
print("\nNota: estes registros NÃO foram integrados ao dataset principal do projeto (Referencias/"
      "ocorrencias_primatas_brasil_gbif.csv) nem ao pipeline da Parte 2 — decisão pendente, ver "
      "ROTEIRO_DO_PROJETO.md, Etapa 34.")
