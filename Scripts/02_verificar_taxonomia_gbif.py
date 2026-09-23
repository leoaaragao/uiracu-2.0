"""
Ficha simples 01 / Bloco C - Camada 2 (Taxonomia).
Consulta o backbone taxonomico do GBIF para o nome cientifico de interesse,
para confirmar nome aceito, status e sinonimos ANTES de baixar ocorrencias.
Nao inventa nem assume: usa a fonte diretamente (species/match + species/{key}/synonyms).
"""
import requests
import json

NOME_CONSULTADO = "Lagothrix cana"

r = requests.get(
    "https://api.gbif.org/v1/species/match",
    params={"name": NOME_CONSULTADO, "rank": "SPECIES", "strict": False},
    timeout=30,
)
match = r.json()
print("=== species/match para:", NOME_CONSULTADO, "===")
print(json.dumps(match, indent=2, ensure_ascii=False))

accepted_key = match.get("acceptedUsageKey") or match.get("usageKey")
print("\n=== Detalhe do taxon aceito (usageKey =", accepted_key, ") ===")
r2 = requests.get(f"https://api.gbif.org/v1/species/{accepted_key}", timeout=30)
detail = r2.json()
campos = ["scientificName", "canonicalName", "authorship", "taxonomicStatus",
          "rank", "kingdom", "phylum", "class", "order", "family", "genus"]
for c in campos:
    print(f"  {c}: {detail.get(c)}")

print("\n=== Sinonimos registrados no GBIF ===")
r3 = requests.get(f"https://api.gbif.org/v1/species/{accepted_key}/synonyms", timeout=30)
for s in r3.json().get("results", []):
    print(" -", s.get("scientificName"), "| status:", s.get("taxonomicStatus"))
