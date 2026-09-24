"""
Verifica quais das UCs federais da Amazonia Ocidental (recorte de 85, sem RR)
tocam ou ficam proximas da fronteira internacional (Peru, Colombia, Bolivia,
Venezuela) - para embasar a decisao do escopo geografico de M com dados
reais, nao suposicao.
"""
import geopandas as gpd

ucs = gpd.read_file("Dados/ucs_federais_amazonia_ocidental.gpkg").to_crs("EPSG:4326")
paises = gpd.read_file("Dados/paises_referencia/CNTRY.SHP").set_crs("EPSG:4326")

vizinhos = paises[paises["CNTRY_NAME"].isin(["Peru", "Colombia", "Bolivia", "Venezuela"])]
# CRS metrico (SIRGAS2000 / UTM generico para America do Sul) para medir distancia em km com precisao razoavel
ucs_m = ucs.to_crs("EPSG:5880")  # SIRGAS 2000 / Brazil Polyconic - metros
vizinhos_m = vizinhos.to_crs("EPSG:5880")
fronteira_unica = vizinhos_m.union_all()

ucs_m["dist_fronteira_km"] = ucs_m.geometry.distance(fronteira_unica) / 1000
ucs_m["toca_fronteira"] = ucs_m.geometry.intersects(fronteira_unica)

resultado = ucs_m[["nome_uc", "uf", "dist_fronteira_km", "toca_fronteira"]].sort_values("dist_fronteira_km")
resultado.to_csv("Referencias/ucs_distancia_fronteira.csv", index=False, encoding="utf-8-sig")

print("=== UCs que TOCAM a fronteira internacional (Peru/Colombia/Bolivia/Venezuela) ===")
tocam = resultado[resultado["toca_fronteira"]]
print(tocam.to_string(index=False))

print(f"\n=== UCs a menos de 50 km da fronteira (mas sem tocar) ===")
proximas = resultado[(~resultado["toca_fronteira"]) & (resultado["dist_fronteira_km"] < 50)]
print(proximas.to_string(index=False))

print(f"\nTotal de UCs que tocam a fronteira: {len(tocam)}")
print(f"Total de UCs a menos de 50 km (sem tocar): {len(proximas)}")
print(f"Total de UCs a mais de 50 km da fronteira: {(resultado['dist_fronteira_km'] >= 50).sum()}")
print("\nSalvo: Referencias/ucs_distancia_fronteira.csv")
