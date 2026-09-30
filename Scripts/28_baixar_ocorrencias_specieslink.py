# -*- coding: utf-8 -*-
"""Uiraçu 2.0 — Parte 1 (tese): ocorrências de primatas via API do speciesLink.

Segunda fonte de ocorrência (além do GBIF), avaliada na Etapa 33 do ROTEIRO_DO_PROJETO.md.
Usa a MESMA caixa geográfica do download original do GBIF (Scripts/13), para manter os dois
levantamentos comparáveis — sem restrição política, mesma lógica da Etapa 5.

Requer uma chave de API pessoal (SPECIESLINK_API_KEY), lida de um arquivo `.env` na raiz do
projeto (nunca versionado — ver .gitignore). Cadastro/chave: https://specieslink.net
"""
import csv
import os
import time

import requests

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Mesma caixa delimitadora do download original do GBIF (Scripts/13), 1 grau de folga
# em torno das 92 UCs, para os dois levantamentos serem comparáveis.
MINX, MINY, MAXX, MAXY = -74.991206773, -13.880252939231516, -54.99318558660241, 3.240947371000061
BBOX = f"{MINX} {MINY} {MAXX} {MAXY}"

BASE_URL = "https://specieslink.net/ws/1.0/search"
LIMIT = 5000
SAIDA = os.path.join(RAIZ, "Dados", "specieslink_primatas_bruto.csv")


def carregar_chave():
    chave = os.environ.get("SPECIESLINK_API_KEY")
    if chave:
        return chave
    caminho_env = os.path.join(RAIZ, ".env")
    if os.path.exists(caminho_env):
        with open(caminho_env, encoding="utf-8") as f:
            for linha in f:
                if linha.strip().startswith("SPECIESLINK_API_KEY"):
                    return linha.split("=", 1)[1].strip()
    raise RuntimeError(
        "SPECIESLINK_API_KEY não encontrada. Crie um arquivo .env na raiz do projeto com "
        "SPECIESLINK_API_KEY=<sua chave> (gerada em specieslink.net/aut/profile/apikeys)."
    )


APIKEY = carregar_chave()

params_base = {
    "apikey": APIKEY,
    "order": "Primates",
    "bbox": BBOX,
    "coordinates": "yes",
    "output": "dwc",
    "limit": LIMIT,
}

print(f"Caixa geográfica (mesma do GBIF, Scripts/13): {BBOX}")
print("Consultando speciesLink (order=Primates, com coordenada)...")

offset = 0
total_esperado = None
registros = []

while True:
    resp = requests.get(BASE_URL, params={**params_base, "offset": offset}, timeout=60)
    resp.raise_for_status()
    dados = resp.json()

    if total_esperado is None:
        total_esperado = dados.get("numberMatched", 0)
        print(f"Total de registros disponíveis (numberMatched): {total_esperado}")

    features = dados.get("features", [])
    if not features:
        break

    for feat in features:
        props = feat.get("properties", {})
        coords = feat.get("geometry", {}).get("coordinates", [None, None])
        props["decimalLongitude"], props["decimalLatitude"] = coords[0], coords[1]
        registros.append(props)

    recebidos = dados.get("numberReturned", len(features))
    offset += recebidos
    print(f"  {offset}/{total_esperado} registros baixados...", flush=True)

    if offset >= total_esperado or recebidos == 0:
        break
    time.sleep(0.5)  # gentil com o servidor

print(f"\nTotal baixado: {len(registros)} registros.")

if registros:
    colunas = sorted({chave for reg in registros for chave in reg.keys()})
    with open(SAIDA, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=colunas)
        w.writeheader()
        w.writerows(registros)
    print(f"Salvo em: {SAIDA}")
else:
    print("Nenhum registro retornado — nada foi salvo.")
