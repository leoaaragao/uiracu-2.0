"""
Mapa diagnostico rapido: todos os pontos de ocorrencia (todos os paises)
coloridos por pais/subespecie, com as 85 UCs de estudo como referencia.
Gerado para apoiar a decisao do escopo de M com a professora.
"""
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import pandas as pd

df = pd.read_csv("Dados/gbif_oficial_extraido/occurrence.txt", sep="\t", quoting=3, low_memory=False)
df = df.dropna(subset=["decimalLatitude", "decimalLongitude"])
pontos = gpd.GeoDataFrame(
    df, geometry=gpd.points_from_xy(df["decimalLongitude"], df["decimalLatitude"]), crs="EPSG:4326"
)

ucs = gpd.read_file("Dados/ucs_federais_amazonia_ocidental.gpkg")

# Limites politicos (fonte: material da disciplina, Modelagem preditiva/Dados/world_country - ESRI world countries)
paises = gpd.read_file("Dados/paises_referencia/CNTRY.SHP")
paises = paises.set_crs("EPSG:4326")
am_sul = paises[paises["CNTRY_NAME"].isin([
    "Brazil", "Peru", "Colombia", "Ecuador", "Bolivia", "Venezuela",
    "Paraguay", "Guyana", "Suriname", "French Guiana", "Chile", "Argentina", "Panama",
])]

NOME_PAIS = {"BR": "Brasil", "PE": "Peru", "CO": "Colômbia", "EC": "Equador", "US": "Estados Unidos", "PY": "Paraguai"}
CORES_PAIS = {"BR": "#1F4E3D", "PE": "#B08D57", "CO": "#4477AA", "EC": "#CC6677", "US": "#999999", "PY": "#663399"}

fig, ax = plt.subplots(figsize=(11, 12))

am_sul.plot(ax=ax, color="#FAFAF7", edgecolor="#888888", linewidth=0.6, zorder=0)
ucs.plot(ax=ax, color="#E8F0EC", edgecolor="#1F4E3D", linewidth=0.5, zorder=1)

for pais, cor in CORES_PAIS.items():
    sub = pontos[pontos["countryCode"] == pais]
    if len(sub) == 0:
        continue
    ax.scatter(sub.geometry.x, sub.geometry.y, s=16, color=cor, alpha=0.75,
               edgecolor="white", linewidth=0.3, zorder=3)

ax.set_xlim(-82, -35)
ax.set_ylim(-25, 8)
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.set_title(
    "Lagothrix lagothricha — ocorrências GBIF por país de registro\n"
    "(cor = countryCode do GBIF; fundo cinza = fronteiras políticas da América do Sul)",
    fontsize=12,
)

legend_pontos = [
    Line2D([0], [0], marker="o", color="w", markerfacecolor=cor, markeredgecolor="white",
           markersize=9, label=f"{NOME_PAIS[pais]} (n={len(pontos[pontos['countryCode'] == pais])})")
    for pais, cor in CORES_PAIS.items() if len(pontos[pontos["countryCode"] == pais]) > 0
]
legend_areas = [
    Patch(facecolor="#E8F0EC", edgecolor="#1F4E3D", linewidth=0.5, label="UCs federais de estudo (85, AM/AC/RO)"),
    Patch(facecolor="#FAFAF7", edgecolor="#888888", linewidth=0.6, label="Limites de países (América do Sul)"),
]
leg1 = ax.legend(handles=legend_pontos, loc="lower left", fontsize=9, framealpha=0.95,
                  title="Ocorrências por país (fonte GBIF)", title_fontsize=9)
ax.add_artist(leg1)
ax.legend(handles=legend_areas, loc="upper right", fontsize=9, framealpha=0.95)

ax.grid(alpha=0.15)

plt.tight_layout()
plt.savefig("Evidencias/mapa_ocorrencias_multipais.png", dpi=150)
print("Salvo: Evidencias/mapa_ocorrencias_multipais.png")
