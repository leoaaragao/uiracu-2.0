"""
Ficha simples 01 / Bloco B - preparacao dos dados de UC.
Filtra o CNUC (ucs.shp, fonte: projeto Uiracu, dados oficiais MMA/ICMBio)
para as Unidades de Conservacao FEDERAIS que tocam AM, AC, RO ou RR.

Principio (Protocolo 02): preservar o dado original intocado, gerar copia derivada.
"""
import geopandas as gpd

SRC = "Dados/ucs_cnuc_bruto/ucs.shp"
OUT_GPKG = "Dados/ucs_federais_amazonia_ocidental.gpkg"
OUT_CSV = "Dados/ucs_federais_amazonia_ocidental_atributos.csv"

ESTADOS_ALVO = ["AMAZONAS", "ACRE", "RONDÔNIA", "RONDONIA", "RORAIMA"]

gdf = gpd.read_file(SRC)
print("Total de UCs no Brasil:", len(gdf))

gdf["esfera"] = gdf["esfera"].astype(str).str.strip()
gdf["uf"] = gdf["uf"].astype(str)
gdf["situacao"] = gdf["situacao"].astype(str).str.strip()

is_federal = gdf["esfera"].str.upper() == "FEDERAL"
is_ativo = gdf["situacao"].str.upper() == "ATIVO"
is_alvo = gdf["uf"].str.upper().apply(lambda s: any(e in s for e in ESTADOS_ALVO))

sel = gdf[is_federal & is_ativo & is_alvo].copy()
print("UCs federais ativas em AM/AC/RO/RR:", len(sel))
print()
print(sel[["nome_uc", "categoria", "grupo", "uf", "ha_total", "cat_iucn"]].sort_values("nome_uc").to_string(index=False))

sel.to_file(OUT_GPKG, driver="GPKG")
sel.drop(columns="geometry").to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
print()
print("Salvo:", OUT_GPKG)
print("Salvo:", OUT_CSV)
