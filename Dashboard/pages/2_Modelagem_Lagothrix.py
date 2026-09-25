# -*- coding: utf-8 -*-
"""Uiraçu 2.0 — Parte 2: Modelagem do Lagothrix lagothricha (em andamento)."""
import os
import geopandas as gpd
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Uiraçu 2.0 — Parte 2: Lagothrix", layout="wide", page_icon="🐵")

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.title("🐵 Parte 2 — Modelagem de *Lagothrix lagothricha*")
st.caption("Estudo de caso aprofundado (SDM): GLM, Maxent, Random Forest, validação cruzada, incerteza — Fichas 2.6 a 2.9.")

st.warning("🔧 **Em andamento.** Etapas de dados/área concluídas; ajuste dos modelos ainda não foi feito. "
           "Ver `DIARIO_DE_BORDO.md` para o histórico completo.")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Pontos de calibração (rarefeitos)", 37)
c2.metric("Ecorregiões em M", 11)
c3.metric("Área de M (km²)", "3.235.510")
c4.metric("UCs de estudo", 85)

st.subheader("O que já foi feito")
st.markdown("""
1. ✅ Auditoria taxonômica e de ocorrências (139 → 85 registros úteis, Brasil)
2. ✅ Rarefação espacial (thinning 50 km) → 37 pontos de calibração
3. ✅ Área acessível (M): união de 11 ecorregiões tocadas pelos pontos — 75% Brasil, 13% Peru, 7% Bolívia, 5% Colômbia
4. ⏳ Variáveis climáticas (WorldClim, 10 min de arco) — dado já disponível localmente, ainda não recortado para M
5. ⏳ Background/pseudo-ausências, PCA das variáveis
6. ⏳ Ajuste dos modelos (GLM, Maxent via `elapid`, Random Forest) + validação cruzada
7. ⏳ Mapa de consenso e de incerteza
8. ⏳ Pós-processamento (cruzar com MapBiomas × 85 UCs)
""")

st.subheader("Mapa — pontos de calibração e área M")
try:
    pontos_df = pd.read_csv(os.path.join(RAIZ, "Dados", "FO01_06_ocorrencias_rarefeitas.csv"))
    area_M = gpd.read_file(os.path.join(RAIZ, "Dados", "area_M_lagothrix_dissolvido.gpkg")).to_crs("EPSG:4326")
    ucs = gpd.read_file(os.path.join(RAIZ, "Dados", "ucs_federais_amazonia_ocidental.gpkg")).to_crs("EPSG:4326")

    m = folium.Map(location=[-7, -66], zoom_start=5, tiles="OpenStreetMap")
    folium.GeoJson(area_M, style_function=lambda x: {
        "fillColor": "#B08D57", "color": "#B08D57", "weight": 1.5, "fillOpacity": 0.10, "dashArray": "5,5",
    }, tooltip="Área acessível (M)").add_to(m)
    folium.GeoJson(ucs[["nome_uc", "geometry"]], style_function=lambda x: {
        "fillColor": "#E8F0EC", "color": "#1F4E3D", "weight": 0.5, "fillOpacity": 0.2,
    }, tooltip=folium.GeoJsonTooltip(fields=["nome_uc"])).add_to(m)
    for _, p in pontos_df.iterrows():
        folium.CircleMarker(
            location=[p["decimalLatitude"], p["decimalLongitude"]], radius=5,
            color="white", weight=1, fill=True, fill_color="#1F4E3D", fill_opacity=0.9,
            popup=f"Ano: {p.get('year', '—')}",
        ).add_to(m)
    st_folium(m, use_container_width=True, height=520, returned_objects=[])
    st.caption("Pontos verdes = 37 registros de calibração · área tracejada = M (união de ecorregiões) · polígonos verdes = 85 UCs de estudo.")
except Exception as e:
    st.error(f"Não foi possível carregar a camada: {e}")

st.divider()
st.caption("Uiraçu 2.0 · leoaaragao/uiracu-2.0 · gerado com apoio de Claude (Anthropic) — ver DIARIO_DE_BORDO.md")
