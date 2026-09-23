"""
Ficha simples 01 / suficiencia amostral preliminar.
Compara o volume de registros no GBIF em dois niveis taxonomicos:
  - especie:    Lagothrix lagothricha (taxonKey 5786085) - inclui todas as subespecies
  - subespecie: Lagothrix lagothricha cana (taxonKey 5786086)
E cruza com presenca de coordenadas e pais = Brasil, para dimensionar a decisao.
"""
import requests

CHAVES = {
    "especie (L. lagothricha, todas subesp.)": 5786085,
    "subespecie (L. l. cana)": 5786086,
}

def contar(taxon_key, **extra):
    params = {"taxonKey": taxon_key, "limit": 0, **extra}
    r = requests.get("https://api.gbif.org/v1/occurrence/search", params=params, timeout=30)
    return r.json()["count"]

for label, key in CHAVES.items():
    total = contar(key)
    com_coord = contar(key, hasCoordinate="true")
    brasil = contar(key, hasCoordinate="true", country="BR")
    print(f"{label}  [taxonKey={key}]")
    print(f"   total de registros GBIF:              {total}")
    print(f"   com coordenadas:                      {com_coord}")
    print(f"   com coordenadas e pais = Brasil:       {brasil}")
    print()
