"""
Etapa 1 do cruzamento Primatas x UCs.
Busca no backbone do GBIF todas as especies ACEITAS dentro de cada genero
de primata amazonico (evita listar nomes de memoria - risco de erro).
"""
import requests
import pandas as pd
import time

GENEROS = [
    "Alouatta", "Ateles", "Lagothrix",
    "Pithecia", "Chiropotes", "Cacajao", "Plecturocebus", "Cheracebus",
    "Cebus", "Sapajus", "Saimiri",
    "Aotus",
    "Saguinus", "Leontocebus", "Mico", "Cebuella", "Callimico", "Callibella",
]

registros = []
for genero in GENEROS:
    r = requests.get("https://api.gbif.org/v1/species/match",
                      params={"name": genero, "rank": "GENUS", "kingdom": "Animalia", "strict": False}, timeout=30)
    m = r.json()
    genus_key = m.get("usageKey")
    if not genus_key or m.get("rank") != "GENUS":
        print(f"AVISO: genero '{genero}' nao resolvido diretamente: {m.get('scientificName')}")
        continue

    offset, limit = 0, 100
    while True:
        r2 = requests.get(
            "https://api.gbif.org/v1/species/search",
            params={"highertaxonKey": genus_key, "rank": "SPECIES", "status": "ACCEPTED",
                    "limit": limit, "offset": offset},
            timeout=30,
        )
        data = r2.json()
        for sp in data["results"]:
            registros.append({
                "genero": genero,
                "genusKey": genus_key,
                "taxonKey": sp["key"],
                "canonicalName": sp.get("canonicalName"),
                "scientificName": sp.get("scientificName"),
                "family": sp.get("family"),
            })
        offset += limit
        if offset >= data["count"]:
            break
    time.sleep(0.2)
    print(f"{genero}: {len([r for r in registros if r['genero'] == genero])} especies")

df = pd.DataFrame(registros).drop_duplicates(subset="taxonKey")
df.to_csv("Referencias/especies_por_genero_gbif.csv", index=False, encoding="utf-8-sig")
print(f"\nTotal de especies (todas fontes/status ACCEPTED, pode incluir nao-amazonicas): {len(df)}")
print(df.groupby("genero").size().sort_values(ascending=False))
