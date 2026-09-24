"""
Extrai as coordenadas de TODAS as ocorrencias (dentro E fora das UCs) das
especies que tiveram pelo menos 1 registro confirmado dentro de alguma das
85 UCs de estudo. Ou seja: distribuicao geral conhecida (nesta consulta),
nao so os pontos que caem dentro do poligono.
"""
import geopandas as gpd
import pandas as pd

ranking = pd.read_csv("Referencias/ranking_especies_por_incidencia_ucs.csv")
especies_identificadas = set(ranking["species"])
print(f"Especies identificadas em pelo menos 1 UC: {len(especies_identificadas)}")

ocorrencias = pd.read_csv("Referencias/ocorrencias_primatas_brasil_gbif.csv")
ocorrencias = ocorrencias.dropna(subset=["decimalLatitude", "decimalLongitude"])
sub = ocorrencias[ocorrencias["species"].isin(especies_identificadas)].copy()
print(f"Total de ocorrencias (dentro + fora das UCs) dessas especies: {len(sub)}")

pontos = gpd.GeoDataFrame(
    sub, geometry=gpd.points_from_xy(sub["decimalLongitude"], sub["decimalLatitude"]), crs="EPSG:4326"
)
ucs = gpd.read_file("Dados/ucs_federais_amazonia_ocidental.gpkg")[["nome_uc", "geometry"]].to_crs("EPSG:4326")

juncao = gpd.sjoin(pontos, ucs, how="left", predicate="within")
juncao["dentro_de_uc"] = juncao["nome_uc"].notna()
juncao["nome_uc"] = juncao["nome_uc"].fillna("(fora das UCs de estudo)")

saida = juncao[[
    "species", "decimalLatitude", "decimalLongitude", "dentro_de_uc", "nome_uc",
    "countryCode", "level1Name", "year", "basisOfRecord", "coordinateUncertaintyInMeters",
    "datasetName", "key",
]].rename(columns={
    "species": "especie", "decimalLatitude": "latitude", "decimalLongitude": "longitude",
    "nome_uc": "UC (se aplicavel)", "countryCode": "pais", "level1Name": "estado_departamento",
    "year": "ano", "basisOfRecord": "tipo_registro", "coordinateUncertaintyInMeters": "incerteza_m",
    "datasetName": "dataset_origem", "key": "gbifID",
}).sort_values(["especie", "dentro_de_uc"], ascending=[True, False])

saida.to_csv("Referencias/Coordenadas_Especies_Identificadas_UCs.csv", index=False, encoding="utf-8-sig")

print(f"\nDentro de alguma UC: {saida['dentro_de_uc'].sum()}")
print(f"Fora das UCs (mesma especie, outros pontos da distribuicao): {(~saida['dentro_de_uc']).sum()}")
print(f"\nSalvo: Referencias/Coordenadas_Especies_Identificadas_UCs.csv")
