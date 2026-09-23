"""Diagnostico rapido da nova base multi-pais antes de redesenhar a auditoria."""
import pandas as pd
df = pd.read_csv("Dados/gbif_oficial_extraido/occurrence.txt", sep="\t", quoting=3, low_memory=False)
print("Total:", len(df))
print("\nPor pais (countryCode):")
print(df["countryCode"].value_counts())
print("\nPor taxonRank:")
print(df["taxonRank"].value_counts())
print("\nEstados/departamentos em BR/PE/BO (level1Name), top 20:")
core = df[df["countryCode"].isin(["BR", "PE", "BO"])]
print(core["level1Name"].value_counts().head(20))
print("\nAmostra de outros paises (fora BR/PE/BO):")
outros = df[~df["countryCode"].isin(["BR", "PE", "BO"])]
print(outros["countryCode"].value_counts())
