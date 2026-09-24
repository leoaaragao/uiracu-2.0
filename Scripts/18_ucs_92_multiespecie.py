"""
Gera o recorte de 92 UCs (AM/AC/RO/RR, Roraima incluida) para o PRODUTO
MULTIESPECIE (riqueza/diversidade funcional e filogenetica de primatas).

Motivo da divergencia em relacao ao recorte de 85 usado para o SDM do
Lagothrix: a exclusao de Roraima foi uma decisao ESPECIFICA daquela especie
(Rio Negro/Branco como limite documentado de distribuicao). Para o produto
multiespecie - que e sobre a comunidade de primatas como um todo, base do
debate de bonus de biodiversidade (diversidade funcional e filogenetica) do
projeto de doutorado - nao ha motivo biogeografico para excluir Roraima:
outras especies de primata podem ocorrer la. Ver DIARIO_DE_BORDO.md.

NAO sobrescreve o arquivo de 85 UCs (usado pelo Lagothrix) - gera um
arquivo separado.
"""
import geopandas as gpd

SRC = "Dados/ucs_cnuc_bruto/ucs.shp"
OUT_GPKG = "Dados/ucs_federais_92_multiespecie.gpkg"
OUT_CSV = "Dados/ucs_federais_92_multiespecie_atributos.csv"

ESTADOS_ALVO = ["AMAZONAS", "ACRE", "RONDÔNIA", "RONDONIA", "RORAIMA"]

gdf = gpd.read_file(SRC)
gdf["esfera"] = gdf["esfera"].astype(str).str.strip()
gdf["uf"] = gdf["uf"].astype(str)
gdf["situacao"] = gdf["situacao"].astype(str).str.strip()

is_federal = gdf["esfera"].str.upper() == "FEDERAL"
is_ativo = gdf["situacao"].str.upper() == "ATIVO"
is_alvo = gdf["uf"].str.upper().apply(lambda s: any(e in s for e in ESTADOS_ALVO))

sel = gdf[is_federal & is_ativo & is_alvo].copy()
print(f"UCs federais ativas em AM/AC/RO/RR (produto multiespecie): {len(sel)}")

sel.to_file(OUT_GPKG, driver="GPKG")
sel.drop(columns="geometry").to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
print(f"Salvo: {OUT_GPKG}")
print(f"Salvo: {OUT_CSV}")
