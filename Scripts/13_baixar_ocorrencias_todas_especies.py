"""
Etapa 2 do cruzamento Primatas x UCs.
Baixa ocorrencias de cada especie via API publica do GBIF, usando um filtro
GEOGRAFICO puro (bounding box ao redor das 85 UCs, + margem de seguranca) -
DELIBERADAMENTE sem filtro de country=BR. Motivo: o campo countryCode do
GBIF pode estar errado (caso "Loreto"). A decisao real de "esta dentro da UC"
e feita depois, geometricamente (Etapa 3 - Scripts/14).

Robustez: salva incrementalmente (append por especie) e mostra progresso em
tempo real (flush=True) - se for interrompido, nada se perde; pode retomar
de onde parou (pula especies ja salvas no CSV de saida).
"""
import requests
import pandas as pd
import csv
import os
import sys

OUT = "Referencias/ocorrencias_primatas_brasil_gbif.csv"

especies = pd.read_csv("Referencias/especies_por_genero_gbif.csv")
total = len(especies)
print(f"Especies a consultar: {total}", flush=True)

MINX, MINY, MAXX, MAXY = -74.991206773, -13.880252939231516, -54.99318558660241, 3.240947371000061
GEOMETRIA_WKT = f"POLYGON(({MINX} {MINY}, {MAXX} {MINY}, {MAXX} {MAXY}, {MINX} {MAXY}, {MINX} {MINY}))"

CAMPOS = ["genero_consultado", "key", "scientificName", "species", "taxonKey", "speciesKey",
          "decimalLatitude", "decimalLongitude", "coordinateUncertaintyInMeters",
          "year", "basisOfRecord", "datasetName", "level1Name", "countryCode"]

# Retomada: especies ja processadas (se o arquivo ja existir de uma tentativa anterior)
ja_feitas = set()
escrever_cabecalho = not os.path.exists(OUT)
if os.path.exists(OUT):
    try:
        prev = pd.read_csv(OUT, usecols=["taxonKey"])
        ja_feitas = set(prev["taxonKey"].unique())
        print(f"Retomando: {len(ja_feitas)} especies ja processadas em execucao anterior.", flush=True)
    except Exception:
        pass

with open(OUT, "a", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=CAMPOS)
    if escrever_cabecalho:
        writer.writeheader()
        f.flush()

    for i, row in especies.iterrows():
        taxon_key = int(row["taxonKey"])
        if taxon_key in ja_feitas:
            continue
        offset, limit = 0, 300
        n_especie = 0
        while True:
            params = {"taxonKey": taxon_key, "geometry": GEOMETRIA_WKT, "hasCoordinate": "true",
                      "limit": limit, "offset": offset}
            try:
                r = requests.get("https://api.gbif.org/v1/occurrence/search", params=params, timeout=30)
                r.raise_for_status()
                data = r.json()
            except Exception as e:
                print(f"  ERRO em {row['canonicalName']} (offset {offset}): {e} - pulando resto desta especie", flush=True)
                break
            for rec in data["results"]:
                linha = {c: rec.get(c) for c in CAMPOS if c != "genero_consultado"}
                linha["genero_consultado"] = row["genero"]
                writer.writerow(linha)
            n_especie += len(data["results"])
            offset += limit
            if offset >= data["count"] or len(data["results"]) == 0:
                break
        f.flush()
        marca = f" <-- {n_especie} registros" if n_especie else ""
        print(f"[{i+1}/{total}] {row['genero']} {row['canonicalName']}{marca}", flush=True)

print("\nConcluido.", flush=True)
df_final = pd.read_csv(OUT)
print(f"Total de registros no arquivo: {len(df_final)}", flush=True)
print(f"Especies com pelo menos 1 registro na caixa geografica: {df_final['speciesKey'].nunique()}", flush=True)
