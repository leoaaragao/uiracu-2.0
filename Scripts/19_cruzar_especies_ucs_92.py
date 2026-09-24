"""
Cruzamento espacial especie x UC usando as 92 UCs (AM/AC/RO/RR, com Roraima)
- versao para o PRODUTO MULTIESPECIE. Reaproveita os mesmos 14.588 registros
ja baixados (Scripts/13); so muda o poligono de referencia (92, nao 85).
"""
import geopandas as gpd
import pandas as pd

ocorrencias = pd.read_csv("Referencias/ocorrencias_primatas_brasil_gbif.csv")
ocorrencias = ocorrencias.dropna(subset=["decimalLatitude", "decimalLongitude"])
pontos = gpd.GeoDataFrame(
    ocorrencias,
    geometry=gpd.points_from_xy(ocorrencias["decimalLongitude"], ocorrencias["decimalLatitude"]),
    crs="EPSG:4326",
)

ucs92 = gpd.read_file("Dados/ucs_federais_92_multiespecie.gpkg")[["nome_uc", "categoria", "uf", "geometry"]]
ucs92 = ucs92.to_crs(pontos.crs)

dentro = gpd.sjoin(pontos, ucs92, how="inner", predicate="within")
print(f"Ocorrencias totais: {len(pontos)}")
print(f"Ocorrencias dentro de alguma das 92 UCs (com RR): {len(dentro)}")

# Comparacao explicita: o que Roraima adiciona
rr = dentro[dentro["uf"].str.contains("RORAIMA", na=False)]
print(f"\nDessas, dentro de UCs que tocam Roraima: {len(rr)}")
if len(rr):
    print("Especies encontradas em UCs de Roraima:")
    print(rr.groupby(["nome_uc", "species"]).size().reset_index(name="n_registros").to_string(index=False))

matriz92 = dentro.pivot_table(index="species", columns="nome_uc", values="key", aggfunc="count", fill_value=0)
matriz92.to_csv("Referencias/matriz_especies_x_ucs92_gbif.csv", encoding="utf-8-sig")

ranking92 = dentro.groupby("species").agg(
    n_ucs_com_registro=("nome_uc", "nunique"),
    n_registros_totais=("key", "count"),
).sort_values(["n_ucs_com_registro", "n_registros_totais"], ascending=False)
ranking92.to_csv("Referencias/ranking_especies_por_incidencia_ucs92.csv", encoding="utf-8-sig")

print(f"\nEspecies com registro em pelo menos 1 das 92 UCs: {len(ranking92)}")
print(f"(era {len(pd.read_csv('Referencias/ranking_especies_por_incidencia_ucs.csv'))} com as 85 UCs, sem RR)")
print("\nSalvo: Referencias/matriz_especies_x_ucs92_gbif.csv")
print("Salvo: Referencias/ranking_especies_por_incidencia_ucs92.csv")
