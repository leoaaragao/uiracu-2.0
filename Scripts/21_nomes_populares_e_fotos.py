"""
Busca, para cada uma das 168 especies, o nome popular (preferencia
portugues, senao ingles) e uma foto representativa (com licenca), via API
publica do GBIF - mesma fonte de todo o projeto, nada inventado.

Salva incrementalmente (uma linha por especie, com flush) para nao perder
progresso se interrompido - mesma licao aprendida no Scripts/13.
"""
import requests
import pandas as pd
import csv
import os

OUT = "Referencias/especies_nomes_populares_fotos.csv"
CAMPOS = ["taxonKey", "canonicalName", "nome_popular", "idioma_nome",
          "foto_url", "foto_licenca", "foto_creditos"]

especies = pd.read_csv("Referencias/especies_por_genero_gbif.csv")
print(f"Especies a consultar: {len(especies)}", flush=True)

ja_feitas = set()
escrever_cabecalho = not os.path.exists(OUT)
if os.path.exists(OUT):
    prev = pd.read_csv(OUT, usecols=["taxonKey"])
    ja_feitas = set(prev["taxonKey"].unique())
    print(f"Retomando: {len(ja_feitas)} ja processadas.", flush=True)

def nome_popular(taxon_key):
    r = requests.get(f"https://api.gbif.org/v1/species/{taxon_key}/vernacularNames",
                      params={"limit": 50}, timeout=20)
    nomes = r.json().get("results", [])
    for idioma in ("por", "spa", "eng"):
        for n in nomes:
            if n.get("language") == idioma and n.get("vernacularName"):
                return n["vernacularName"], idioma
    return "", ""

def foto(taxon_key):
    r = requests.get("https://api.gbif.org/v1/occurrence/search",
                      params={"taxonKey": taxon_key, "mediaType": "StillImage", "limit": 5}, timeout=20)
    for res in r.json().get("results", []):
        for m in res.get("media", []):
            if m.get("type") == "StillImage" and m.get("identifier"):
                return m["identifier"], m.get("license", ""), m.get("rightsHolder", "") or m.get("creator", "")
    return "", "", ""

with open(OUT, "a", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=CAMPOS)
    if escrever_cabecalho:
        writer.writeheader()
        f.flush()

    for i, row in especies.iterrows():
        tk = int(row["taxonKey"])
        if tk in ja_feitas:
            continue
        try:
            nome, idioma = nome_popular(tk)
            url, lic, cred = foto(tk)
        except Exception as e:
            print(f"  ERRO em {row['canonicalName']}: {e}", flush=True)
            nome, idioma, url, lic, cred = "", "", "", "", ""
        writer.writerow({
            "taxonKey": tk, "canonicalName": row["canonicalName"],
            "nome_popular": nome, "idioma_nome": idioma,
            "foto_url": url, "foto_licenca": lic, "foto_creditos": cred,
        })
        f.flush()
        marca = f" -> {nome} ({idioma})" if nome else ""
        marca += " [foto]" if url else " [sem foto]"
        print(f"[{i+1}/{len(especies)}] {row['canonicalName']}{marca}", flush=True)

print("\nConcluido.", flush=True)
df = pd.read_csv(OUT)
print(f"Com nome popular: {(df['nome_popular'].fillna('')!='').sum()}/{len(df)}", flush=True)
print(f"Com foto: {(df['foto_url'].fillna('')!='').sum()}/{len(df)}", flush=True)
