"""Inspeciona de perto os casos geograficamente estranhos antes de decidir a regra de exclusao."""
import pandas as pd

pd.set_option("display.max_colwidth", 60)
df = pd.read_csv("Dados/gbif_oficial_extraido/occurrence.txt", sep="\t", quoting=3, low_memory=False)

cols = ["gbifID", "scientificName", "level1Name", "countryCode", "decimalLatitude", "decimalLongitude",
        "issue", "basisOfRecord", "institutionCode", "datasetName", "year", "locality", "stateProvince"]

print("=== Registro 'Loreto' (esperado Peru, country declarado BR) ===")
print(df[df["level1Name"] == "Loreto"][cols].to_string(index=False))

print("\n=== Estados fora da Amazonia plausivel (SP, RJ, BA, PE, SC, ES, DF) ===")
implausiveis = ["São Paulo", "Rio de Janeiro", "Bahia", "Pernambuco", "Santa Catarina", "Espírito Santo", "Distrito Federal"]
print(df[df["level1Name"].isin(implausiveis)][cols].to_string(index=False))

print("\n=== Estado ausente (nan) ===")
print(df[df["level1Name"].isna()][cols].to_string(index=False))

print("\n=== Amostra Mato Grosso (adjacente, biologicamente plausivel?) ===")
print(df[df["level1Name"] == "Mato Grosso"][cols].head(8).to_string(index=False))
