"""
Etapa 3 do cruzamento Primatas x UCs.
Junta espacialmente cada ocorrencia (ponto) com o poligono da UC em que cai
(join geometrico real - nao usa nenhum campo de pais/estado declarado).
Produz: matriz especie x UC (contagem) e um ranking de especies por numero
de UCs com evidencia de ocorrencia.
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

ucs = gpd.read_file("Dados/ucs_federais_amazonia_ocidental.gpkg")[["nome_uc", "categoria", "uf", "geometry"]]
ucs = ucs.to_crs(pontos.crs)  # SIRGAS2000 -> WGS84, para casar com as coordenadas do GBIF

# Join espacial real: ponto dentro do poligono da UC (sjoin "within")
dentro = gpd.sjoin(pontos, ucs, how="inner", predicate="within")
print(f"Ocorrencias totais baixadas: {len(pontos)}")
print(f"Ocorrencias que caem DENTRO de alguma das 85 UCs: {len(dentro)}")

# Matriz especie x UC (contagem de registros)
matriz = dentro.pivot_table(index="species", columns="nome_uc", values="key", aggfunc="count", fill_value=0)
matriz.to_csv("Referencias/matriz_especies_x_ucs_gbif.csv", encoding="utf-8-sig")

# Ranking: quantas UCs distintas cada especie tem evidencia, e total de registros
ranking = dentro.groupby("species").agg(
    n_ucs_com_registro=("nome_uc", "nunique"),
    n_registros_totais=("key", "count"),
).sort_values(["n_ucs_com_registro", "n_registros_totais"], ascending=False)
ranking.to_csv("Referencias/ranking_especies_por_incidencia_ucs.csv", encoding="utf-8-sig")

print("\nTop 25 especies por numero de UCs distintas com registro:")
print(ranking.head(25).to_string())

print(f"\nSalvo: Referencias/matriz_especies_x_ucs_gbif.csv")
print(f"Salvo: Referencias/ranking_especies_por_incidencia_ucs.csv")
