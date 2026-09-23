"""
Filtra a base multi-pais (2.631 registros, download DOI 10.15468/dl.r8eynx)
para Brasil + Peru, apos o diagnostico ter mostrado que Colombia/Equador
sao dominados pela subespecie nominotipica e por L. l. lugens - populacoes
biogeograficamente distintas (fora do escopo deste estudo).

DECISAO (2026-09-23): manter Brasil (cana) + Peru (tschudii/poeppigii) como
"populacao vizinha" para dar mais contraste ambiental ao modelo. Isso mistura
subespecies - registrado explicitamente como limitacao metodologica no
diario de bordo.
"""
import pandas as pd

SRC = "Dados/gbif_oficial_extraido/occurrence.txt"
OUT = "Dados/FO01_02b_ocorrencias_brasil_peru.csv"

df = pd.read_csv(SRC, sep="\t", quoting=3, low_memory=False)
print("Total original (todos os paises):", len(df))

sel = df[df["countryCode"].isin(["BR", "PE"])].copy()
print("Brasil + Peru:", len(sel))
print(sel["countryCode"].value_counts())
print("\nPor subespecie:")
print(sel["infraspecificEpithet"].fillna("(so especie)").value_counts())

sel.to_csv(OUT, index=False, encoding="utf-8-sig")
print(f"\nSalvo: {OUT}")
