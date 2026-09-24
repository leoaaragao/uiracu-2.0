"""Mapa diagnostico: ocorrencias coloridas por SUBESPECIE (infraspecificEpithet)."""
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import pandas as pd

df = pd.read_csv("Dados/gbif_oficial_extraido/occurrence.txt", sep="\t", quoting=3, low_memory=False)
df = df.dropna(subset=["decimalLatitude", "decimalLongitude"])
df["subesp"] = df["infraspecificEpithet"].fillna("(sem subespécie)")
pontos = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df["decimalLongitude"], df["decimalLatitude"]), crs="EPSG:4326")

ucs = gpd.read_file("Dados/ucs_federais_amazonia_ocidental.gpkg")
paises = gpd.read_file("Dados/paises_referencia/CNTRY.SHP").set_crs("EPSG:4326")
am_sul = paises[paises["CNTRY_NAME"].isin([
    "Brazil", "Peru", "Colombia", "Ecuador", "Bolivia", "Venezuela",
    "Paraguay", "Guyana", "Suriname", "French Guiana", "Chile", "Argentina", "Panama",
])]

CORES_SUB = {
    "cana": "#1F4E3D",
    "poeppigii": "#E69F00",
    "tschudii": "#B08D57",
    "lagothricha": "#4477AA",
    "lugens": "#CC6677",
    "defleri": "#882255",
    "sapiens": "#000000",
    "(sem subespécie)": "#BBBBBB",
}

fig, ax = plt.subplots(figsize=(11, 12))
am_sul.plot(ax=ax, color="#FAFAF7", edgecolor="#888888", linewidth=0.6, zorder=0)
ucs.plot(ax=ax, color="#E8F0EC", edgecolor="#1F4E3D", linewidth=0.5, zorder=1)

for sub, cor in CORES_SUB.items():
    pts = pontos[pontos["subesp"] == sub]
    if len(pts) == 0:
        continue
    z = 4 if sub not in ("(sem subespécie)",) else 2
    s = 22 if sub not in ("(sem subespécie)",) else 10
    ax.scatter(pts.geometry.x, pts.geometry.y, s=s, color=cor, alpha=0.8,
               edgecolor="white", linewidth=0.3, zorder=z)

ax.set_xlim(-82, -35)
ax.set_ylim(-25, 8)
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.set_title(
    "Lagothrix lagothricha — ocorrências GBIF por SUBESPÉCIE (infraspecificEpithet)\n"
    "cinza = identificado só até espécie (sem subespécie registrada)",
    fontsize=12,
)

legend_pontos = [
    Line2D([0], [0], marker="o", color="w", markerfacecolor=cor, markeredgecolor="white", markersize=9,
           label=f"{sub} (n={len(pontos[pontos['subesp'] == sub])})")
    for sub, cor in CORES_SUB.items() if len(pontos[pontos["subesp"] == sub]) > 0
]
legend_areas = [
    Patch(facecolor="#E8F0EC", edgecolor="#1F4E3D", linewidth=0.5, label="UCs federais de estudo (85, AM/AC/RO)"),
    Patch(facecolor="#FAFAF7", edgecolor="#888888", linewidth=0.6, label="Limites de países (América do Sul)"),
]
leg1 = ax.legend(handles=legend_pontos, loc="lower left", fontsize=9, framealpha=0.95,
                  title="Subespécie (GBIF)", title_fontsize=9)
ax.add_artist(leg1)
ax.legend(handles=legend_areas, loc="upper right", fontsize=9, framealpha=0.95)
ax.grid(alpha=0.15)

plt.tight_layout()
plt.savefig("Evidencias/mapa_ocorrencias_subespecies.png", dpi=150)
print("Salvo: Evidencias/mapa_ocorrencias_subespecies.png")
