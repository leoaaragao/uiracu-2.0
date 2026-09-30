# -*- coding: utf-8 -*-
"""Uiraçu 2.0 — Parte 1 (tese): harmonização taxonômica do speciesLink (Etapa 34).

Lição da Etapa 33 (falso positivo ICMBio): comparar por nome textual sem checar sinonímia
gera "novidade" falsa quando a mesma espécie está catalogada sob nomes diferentes em cada
fonte. O speciesLink devolve o nome tal como cada coleção o catalogou (`scientificname`),
que pode ser um sinônimo antigo, uma grafia alternativa ou um nível de subespécie — não
necessariamente o nome aceito atual do backbone do GBIF, que é o que
`Referencias/ocorrencias_primatas_brasil_gbif.csv` já usa na coluna `species`.

Aqui cada nome único do download bruto do speciesLink é resolvido contra o backbone do GBIF
(mesmo endpoint e parâmetros do Scripts/02: species/match, rank=SPECIES, strict=False),
produzindo uma tabela de harmonização auditável antes de qualquer comparação/merge.
"""
import os
import time

import pandas as pd
import requests

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DADOS = os.path.join(RAIZ, "Dados")
RESULTADOS = os.path.join(RAIZ, "Resultados")
os.makedirs(RESULTADOS, exist_ok=True)

sl = pd.read_csv(os.path.join(DADOS, "specieslink_primatas_bruto.csv"), low_memory=False)
nomes = sorted(sl["scientificname"].dropna().unique())
print(f"Nomes científicos únicos no download bruto do speciesLink: {len(nomes)}")

linhas = []
for i, nome in enumerate(nomes, 1):
    try:
        r = requests.get(
            "https://api.gbif.org/v1/species/match",
            params={"name": nome, "rank": "SPECIES", "strict": False},
            timeout=30,
        )
        r.raise_for_status()
        m = r.json()
    except Exception as e:
        m = {}
        print(f"  ERRO consultando {nome!r}: {e}")
    linhas.append({
        "nome_specieslink": nome,
        "species_aceito_gbif": m.get("species"),
        "genus_aceito_gbif": m.get("genus"),
        "status": m.get("status"),
        "matchType": m.get("matchType"),
        "confidence": m.get("confidence"),
        "rank": m.get("rank"),
        "usageKey": m.get("usageKey"),
    })
    if i % 20 == 0:
        print(f"  {i}/{len(nomes)} nomes resolvidos...", flush=True)
    time.sleep(0.1)

harmon = pd.DataFrame(linhas)
saida = os.path.join(RESULTADOS, "specieslink_harmonizacao_taxonomica.csv")
harmon.to_csv(saida, index=False, encoding="utf-8-sig")

n_sem_species = harmon["species_aceito_gbif"].isna().sum()
n_divergente = (harmon["nome_specieslink"] != harmon["species_aceito_gbif"]).sum()
print(f"\nSalvo: {saida}")
print(f"Nomes sem nome de espécie aceito resolvido (nível gênero/ordem/indeterminado): {n_sem_species}")
print(f"Nomes cujo texto difere do nome aceito pelo GBIF (sinônimo, grafia, subespécie, etc.): {n_divergente}")
print("\n--- Casos onde o nome do speciesLink difere do nome aceito no GBIF ---")
divergentes = harmon[
    harmon["species_aceito_gbif"].notna()
    & (harmon["nome_specieslink"] != harmon["species_aceito_gbif"])
]
print(divergentes[["nome_specieslink", "species_aceito_gbif", "status"]].to_string(index=False))

print("\n--- Casos SEM nome de espécie aceito (não entram na matriz de riqueza) ---")
sem_match = harmon[harmon["species_aceito_gbif"].isna()]
print(sem_match[["nome_specieslink", "status", "rank", "matchType"]].to_string(index=False))
