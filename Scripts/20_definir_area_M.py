"""
Ficha simples 02 / Bloco B - Definicao da area acessivel (M).
Metodo: uniao das ecorregioes (WWF, via material da disciplina) que tocam
os pontos de ocorrencia rarefeitos de Lagothrix lagothricha (37 pontos,
Brasil, pos-rarefacao - Etapa 4). Mesmo metodo usado pela professora em
aula para o caso da Ocotea/Brosimum (limite_M.shp), so que aqui aplicado
as ecorregioes amazonicas.

Por que isso resolve a pendencia do escopo de M sem misturar subespecies:
ecorregioes nao respeitam fronteira politica. Se os pontos (puros, so
cana/Brasil) tocam uma ecorregiao que se estende ao Peru/Bolivia, o
poligono de M resultante acompanha a ecorregiao - nao precisamos importar
ocorrencias de outras subespecies (tschudii/poeppigii) para isso.
"""
import geopandas as gpd
import pandas as pd

pontos_df = pd.read_csv("Dados/FO01_06_ocorrencias_rarefeitas.csv")
pontos = gpd.GeoDataFrame(
    pontos_df,
    geometry=gpd.points_from_xy(pontos_df["decimalLongitude"], pontos_df["decimalLatitude"]),
    crs="EPSG:4326",
)
print(f"Pontos de calibracao (rarefeitos, Brasil, so cana/especie): {len(pontos)}")

eco = gpd.read_file("Dados/ecoregioes_bruto/Neotropics_ecoregions.shp")
if eco.crs is None:
    eco = eco.set_crs("EPSG:4326")
eco = eco.to_crs("EPSG:4326")
print(f"Ecorregioes carregadas: {len(eco)}")
print(f"Colunas disponiveis: {[c for c in eco.columns if c != 'geometry']}")

# Ecorregioes tocadas pelos pontos
tocadas = gpd.sjoin(pontos, eco, how="inner", predicate="within")
nomes_col = "ECO_NAME" if "ECO_NAME" in eco.columns else eco.columns[eco.columns.str.contains("NAME", case=False)][0]
ecorregioes_tocadas = tocadas[nomes_col].dropna().unique().tolist()
print(f"\nEcorregioes tocadas pelos {len(pontos)} pontos: {len(ecorregioes_tocadas)}")
for e in sorted(ecorregioes_tocadas):
    print(f"  - {e}")

M = eco[eco[nomes_col].isin(ecorregioes_tocadas)].copy()
M_dissolvido = M.dissolve()
M_dissolvido["nome"] = "Area acessivel M - Lagothrix lagothricha (uniao de ecorregioes)"

M.to_file("Dados/area_M_lagothrix_ecorregioes.gpkg", driver="GPKG")
M_dissolvido[["nome", "geometry"]].to_file("Dados/area_M_lagothrix_dissolvido.gpkg", driver="GPKG")

area_km2 = M_dissolvido.to_crs("EPSG:5880").area.sum() / 1e6
print(f"\nArea total de M: {area_km2:,.0f} km2")

# Quanto de M cai em cada pais
paises = gpd.read_file("Dados/paises_referencia/CNTRY.SHP").set_crs("EPSG:4326")
paises_relevantes = paises[paises["CNTRY_NAME"].isin(["Brazil", "Peru", "Bolivia", "Colombia"])]
M_paises = gpd.overlay(M_dissolvido.to_crs("EPSG:4326"), paises_relevantes[["CNTRY_NAME", "geometry"]], how="intersection")
M_paises["area_km2"] = M_paises.to_crs("EPSG:5880").area / 1e6
print("\nDistribuicao de M por pais:")
print(M_paises.groupby("CNTRY_NAME")["area_km2"].sum().sort_values(ascending=False).round(0).to_string())

print("\nSalvo: Dados/area_M_lagothrix_ecorregioes.gpkg (ecorregioes individuais)")
print("Salvo: Dados/area_M_lagothrix_dissolvido.gpkg (poligono unico de M)")
