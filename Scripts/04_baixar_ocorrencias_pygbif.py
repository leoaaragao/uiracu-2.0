"""
Ficha simples 01 / Bloco B - Dados de ocorrencia (via API, reprodutivel).
Baixa ocorrencias de Lagothrix lagothricha (taxonKey 5786085, inclui subespecies)
no Brasil, com coordenadas, via API publica do GBIF (sem necessidade de login).

Principio (Protocolo 02): preservar a base bruta sem edicoes; qualquer limpeza
e feita depois, em outro arquivo, com log das decisoes.

Nota: esta e a via "script" (reprocessavel). A via oficial (gbif.org, com DOI
citavel) deve ser feita manualmente pelo aluno e salva em paralelo -- ver
instrucoes no chat / na Ficha 01.
"""
import time
import requests
import pandas as pd

TAXON_KEY = 5786085  # Lagothrix lagothricha (especie, inclui subesp. cana) - verificado no Script 02
PAIS = "BR"
OUT = "Dados/FO01_02_ocorrencias_originais_pygbif.csv"

CAMPOS = [
    "key", "scientificName", "acceptedScientificName", "taxonRank",
    "infraspecificEpithet", "decimalLatitude", "decimalLongitude",
    "coordinateUncertaintyInMeters", "eventDate", "year",
    "basisOfRecord", "institutionCode", "collectionCode", "catalogNumber",
    "recordedBy", "stateProvince", "county", "locality",
    "issues", "datasetKey", "publishingOrgKey", "license",
]

registros = []
offset = 0
limit = 300
while True:
    params = {
        "taxonKey": TAXON_KEY,
        "country": PAIS,
        "hasCoordinate": "true",
        "limit": limit,
        "offset": offset,
    }
    r = requests.get("https://api.gbif.org/v1/occurrence/search", params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    results = data["results"]
    if not results:
        break
    for rec in results:
        registros.append({c: rec.get(c) for c in CAMPOS})
    offset += limit
    print(f"  baixados: {len(registros)} / {data['count']}")
    if offset >= data["count"]:
        break
    time.sleep(0.3)  # gentil com a API publica

df = pd.DataFrame(registros)
df.to_csv(OUT, index=False, encoding="utf-8-sig")
print(f"\nTotal salvo: {len(df)} registros -> {OUT}")
print("\nResumo por taxonRank (nivel de identificacao):")
print(df["taxonRank"].value_counts())
print("\nResumo por decada:")
print((df["year"].dropna().astype(int) // 10 * 10).value_counts().sort_index())
