"""Inspeciona o schema do shapefile de UCs (CNUC) sem carregar tudo em memoria."""
import geopandas as gpd
import pyogrio

path = "Dados/ucs_cnuc_bruto/ucs.shp"

info = pyogrio.read_info(path)
print("CRS:", info["crs"])
print("Numero de feicoes:", info["features"])
print("Geometria:", info["geometry_type"])
print("Campos:")
for name, dtype in zip(info["fields"], info["dtypes"]):
    print(f"  - {name} ({dtype})")

print("\nAmostra (5 primeiras linhas, sem geometria):")
gdf = gpd.read_file(path, rows=5)
print(gdf.drop(columns="geometry").to_string())
