# -*- coding: utf-8 -*-
"""Cruzamento espacial especie x UC usando as 92 UCs, com o dataset INTEGRADO
(GBIF + registros válidos do speciesLink — Scripts/28-32). Mesma lógica do Scripts/19,
só troca a fonte de ocorrências. Produto usado no toggle "92 UCs" (padrão) da Parte 1
do dashboard a partir da Etapa 34.
"""
import geopandas as gpd
import pandas as pd

ocorrencias = pd.read_csv("Referencias/ocorrencias_primatas_brasil_integrado.csv")
ocorrencias = ocorrencias.dropna(subset=["decimalLatitude", "decimalLongitude"])
pontos = gpd.GeoDataFrame(
    ocorrencias,
    geometry=gpd.points_from_xy(ocorrencias["decimalLongitude"], ocorrencias["decimalLatitude"]),
    crs="EPSG:4326",
)

ucs92 = gpd.read_file("Dados/ucs_federais_92_multiespecie.gpkg")[["nome_uc", "categoria", "uf", "geometry"]]
ucs92 = ucs92.to_crs(pontos.crs)

dentro = gpd.sjoin(pontos, ucs92, how="inner", predicate="within")
print(f"Ocorrencias totais (integrado): {len(pontos)}")
print(f"Ocorrencias dentro de alguma das 92 UCs (com RR): {len(dentro)}")

matriz92 = dentro.pivot_table(index="species", columns="nome_uc", values="key", aggfunc="count", fill_value=0)
matriz92.to_csv("Referencias/matriz_especies_x_ucs92_integrado.csv", encoding="utf-8-sig")

ranking92 = dentro.groupby("species").agg(
    n_ucs_com_registro=("nome_uc", "nunique"),
    n_registros_totais=("key", "count"),
).sort_values(["n_ucs_com_registro", "n_registros_totais"], ascending=False)
ranking92.to_csv("Referencias/ranking_especies_por_incidencia_ucs92_integrado.csv", encoding="utf-8-sig")

print(f"\nEspecies com registro em pelo menos 1 das 92 UCs: {len(ranking92)}")
ranking92_gbif = pd.read_csv("Referencias/ranking_especies_por_incidencia_ucs92.csv")
print(f"(era {len(ranking92_gbif)} só com GBIF)")

especies_novas = set(ranking92.index) - set(ranking92_gbif["species"])
print(f"\nEspécies com evidência de ocorrência DENTRO das 92 UCs que só aparecem com o speciesLink: "
      f"{sorted(especies_novas) if especies_novas else '(nenhuma)'}")

print("\nSalvo: Referencias/matriz_especies_x_ucs92_integrado.csv")
print("Salvo: Referencias/ranking_especies_por_incidencia_ucs92_integrado.csv")
