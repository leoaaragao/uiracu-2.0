# -*- coding: utf-8 -*-
"""Uiraçu 2.0 — Parte 2: Modelagem do Lagothrix lagothricha (SDM)."""
import os

import folium
import geopandas as gpd
import matplotlib as mpl
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd
import plotly.express as px
import rasterio
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(page_title="Uiraçu 2.0 — Parte 2: Lagothrix", layout="wide")

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DADOS = os.path.join(RAIZ, "Dados")
RESULTADOS = os.path.join(RAIZ, "Resultados")

st.title("Parte 2 — Modelagem do macaco-barrigudo (*Lagothrix lagothricha*)")
st.caption("Estudo de caso aprofundado (SDM): GLM, Maxent, Random Forest, validação cruzada, incerteza — Fichas 2.6 a 2.9.")


def raster_para_rgba(caminho, cmap_nome="YlGn", vmin=0.0, vmax=1.0, opacidade=0.85):
    with rasterio.open(caminho) as src:
        arr = src.read(1).astype("float64")
        nodata = src.nodata
        bounds = src.bounds
    mascara_valida = arr != nodata if nodata is not None else ~np.isnan(arr)
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax, clip=True)
    cmap = mpl.colormaps[cmap_nome]
    rgba = cmap(norm(arr))
    rgba[..., 3] = np.where(mascara_valida, opacidade, 0.0)
    bounds_folium = [[bounds.bottom, bounds.left], [bounds.top, bounds.right]]
    return rgba, bounds_folium, arr[mascara_valida]


def mapa_base_ucs():
    m = folium.Map(location=[-7, -66], zoom_start=5, tiles="OpenStreetMap")
    try:
        ucs = gpd.read_file(os.path.join(DADOS, "ucs_federais_amazonia_ocidental.gpkg")).to_crs("EPSG:4326")
        folium.GeoJson(ucs[["nome_uc", "geometry"]], style_function=lambda x: {
            "fillColor": "transparent", "color": "#1F4E3D", "weight": 1,
        }, tooltip=folium.GeoJsonTooltip(fields=["nome_uc"])).add_to(m)
    except Exception:
        pass
    return m


c1, c2, c3, c4 = st.columns(4)
c1.metric("Pontos de calibração (rarefeitos)", 37)
c2.metric("Eixos de PCA usados (>90% variância)", 4)
c3.metric("Background (pseudo-ausência)", "5.000")
c4.metric("UCs de estudo", 85)

st.subheader("O que já foi feito")
st.markdown("""
1. Auditoria taxonômica e de ocorrências (139 → 85 registros úteis, Brasil)
2. Rarefação espacial (thinning 50 km) → 37 pontos de calibração
3. Área acessível (M): união de 11 ecorregiões — 75% Brasil, 13% Peru, 7% Bolívia, 5% Colômbia
4. Variáveis climáticas (WorldClim, 10 min de arco) recortadas para M
5. Background (5.000 pontos) + PCA (4 eixos, 91,8% da variância)
6. Ajuste dos modelos — GLM, Maxent (`elapid`), Random Forest — com validação cruzada 5-fold
7. Mapa de consenso e de incerteza
8. Explicabilidade (importância dos eixos de PCA)
9. Pós-processamento: adequabilidade × MapBiomas (Formação Florestal) × 85 UCs
""")

abas = st.tabs([
    "Mapa de consenso", "Mapa de incerteza", "Adequabilidade × Floresta (UCs)",
    "Desempenho dos modelos", "Importância das variáveis", "Pontos e área M",
])

# --- Aba 1: consenso -------------------------------------------------------
with abas[0]:
    st.markdown("**Adequabilidade ambiental (0 = pouco adequado, 1 = muito adequado)** — "
                "média dos 3 modelos (GLM, Maxent, Random Forest), **ponderada pelo AUC** de cada um "
                "na validação cruzada (ensemble de consenso, conforme Araújo & New, 2007).")
    try:
        rgba, bounds, valores = raster_para_rgba(os.path.join(RESULTADOS, "lagothrix_consenso.tif"), "YlGn", 0, 1)
        m = mapa_base_ucs()
        folium.raster_layers.ImageOverlay(image=rgba, bounds=bounds, opacity=0.85, name="Consenso").add_to(m)
        st_folium(m, use_container_width=True, height=520, returned_objects=[], key="mapa_consenso")
        st.caption(f"Adequabilidade média em M: {valores.mean():.2f} · máxima: {valores.max():.2f}")
        try:
            with rasterio.open(os.path.join(RESULTADOS, "lagothrix_binario_consenso.tif")) as src_bin:
                arr_bin = src_bin.read(1)
                nod_bin = src_bin.nodata
                validos_bin = arr_bin != nod_bin
                pct_apto = 100 * (arr_bin[validos_bin] == 1).mean()
            st.caption(f"Classificando com o limiar que maximiza o TSS de cada modelo (voto majoritário, "
                       f"≥2 de 3 modelos concordando): **{pct_apto:.1f}% de M** é classificada como apta.")
        except Exception:
            pass
    except Exception as e:
        st.error(f"Não foi possível carregar o mapa de consenso: {e}")

# --- Aba 2: incerteza -------------------------------------------------------
with abas[1]:
    st.markdown("**Incerteza** = desvio padrão entre os 3 modelos. Áreas mais escuras = os algoritmos "
                "discordam mais entre si → predição menos confiável ali.")
    try:
        with rasterio.open(os.path.join(RESULTADOS, "lagothrix_incerteza.tif")) as src:
            arr_tmp = src.read(1)
            nod_tmp = src.nodata
            vmax_incerteza = float(arr_tmp[arr_tmp != nod_tmp].max())
        rgba, bounds, valores = raster_para_rgba(
            os.path.join(RESULTADOS, "lagothrix_incerteza.tif"), "Reds", 0, vmax_incerteza
        )
        m = mapa_base_ucs()
        folium.raster_layers.ImageOverlay(image=rgba, bounds=bounds, opacity=0.85, name="Incerteza").add_to(m)
        st_folium(m, use_container_width=True, height=520, returned_objects=[], key="mapa_incerteza")
        st.caption(f"Incerteza média em M: {valores.mean():.2f} · máxima: {valores.max():.2f}")
    except Exception as e:
        st.error(f"Não foi possível carregar o mapa de incerteza: {e}")

# --- Aba 3: pós-processamento MapBiomas × UCs ------------------------------
with abas[2]:
    caminho_ranking = os.path.join(RESULTADOS, "lagothrix_ranking_ucs.csv")
    if not os.path.exists(caminho_ranking):
        st.warning("Pós-processamento ainda em andamento (cruzamento com MapBiomas, arquivo pesado "
                   "processado em segundo plano). Volte em instantes.")
    else:
        ranking = pd.read_csv(caminho_ranking)
        st.markdown("Adequabilidade média **ponderada pela fração de Formação Florestal (MapBiomas, classe 3)** "
                    "dentro de cada UC — uma UC muito adequada climaticamente mas já desmatada pontua mais baixo aqui.")
        com_celula = ranking[ranking["n_celulas_sdm"] > 0]
        sem_celula = ranking[ranking["n_celulas_sdm"] == 0]
        top15 = com_celula.head(15).sort_values("adequabilidade_floresta_media")
        fig = px.bar(
            top15, x="adequabilidade_floresta_media", y="nome_uc", orientation="h",
            labels={"adequabilidade_floresta_media": "Adequabilidade × fração floresta", "nome_uc": ""},
            title="Top 15 UCs — adequabilidade ponderada por floresta",
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(
            com_celula[["nome_uc", "uf", "ha_total", "adequabilidade_media", "fracao_floresta_media",
                        "adequabilidade_floresta_media", "incerteza_media"]].round(3),
            use_container_width=True, hide_index=True,
        )
        if len(sem_celula) > 0:
            st.caption(f"{len(sem_celula)} UCs são menores que a resolução da grade do SDM (~18,5 km) "
                       "e não têm célula própria — não entram no ranking acima.")

# --- Aba 4: desempenho dos modelos -----------------------------------------
with abas[3]:
    try:
        cv = pd.read_csv(os.path.join(RESULTADOS, "lagothrix_cv_metricas.csv"))
        col_auc, col_tss = st.columns(2)
        with col_auc:
            fig_auc = px.bar(
                cv, x="modelo", y="auc_medio", error_y="auc_dp",
                labels={"auc_medio": "AUC médio (5-fold)", "modelo": ""},
                title="AUC (discriminação)", range_y=[0, 1],
            )
            fig_auc.add_hline(y=0.5, line_dash="dash", line_color="gray", annotation_text="0,5 = aleatório")
            st.plotly_chart(fig_auc, use_container_width=True)
        with col_tss:
            fig_tss = px.bar(
                cv, x="modelo", y="tss_medio", error_y="tss_dp",
                labels={"tss_medio": "TSS médio (5-fold)", "modelo": ""},
                title="TSS (sensibilidade + especificidade - 1)", range_y=[0, 1],
            )
            fig_tss.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="0 = aleatório")
            st.plotly_chart(fig_tss, use_container_width=True)
        st.info("**Leitura honesta:** os valores de AUC (0,57–0,60) e TSS (0,28–0,34) são moderados, não "
                "excelentes. Isso é esperado com uma amostra pequena (37 pontos de calibração) — é uma "
                "limitação do dado disponível, não um erro de ajuste. Reportar isso com transparência é "
                "parte do método.")
        st.dataframe(cv.round(3), use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Não foi possível carregar os resultados da validação cruzada: {e}")

# --- Aba 5: importância das variáveis ---------------------------------------
with abas[4]:
    try:
        interpretacao = pd.read_csv(os.path.join(RESULTADOS, "lagothrix_interpretacao_pca.csv"))
        fig = px.bar(
            interpretacao.sort_values("importancia_media"), x="importancia_media", y="eixo", orientation="h",
            labels={"importancia_media": "Importância (queda no AUC ao embaralhar)", "eixo": ""},
            title="Importância de cada eixo de PCA (média dos 3 modelos)",
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("**O que cada eixo representa biologicamente** (3 variáveis bioclimáticas de maior peso):")
        for _, row in interpretacao.iterrows():
            st.markdown(f"- **{row['eixo']}** (importância {row['importancia_media']:.3f}): {row['principais_variaveis']}")
        st.caption("PC3 e PC4 (precipitação e sazonalidade) foram os eixos mais importantes — coerente com "
                   "*Lagothrix lagothricha* ser uma espécie de floresta úmida sensível a regime de chuva.")
    except Exception as e:
        st.error(f"Não foi possível carregar a importância das variáveis: {e}")

# --- Aba 6: pontos e área M (mapa original) ---------------------------------
with abas[5]:
    try:
        pontos_df = pd.read_csv(os.path.join(DADOS, "FO01_06_ocorrencias_rarefeitas.csv"))
        area_M = gpd.read_file(os.path.join(DADOS, "area_M_lagothrix_dissolvido.gpkg")).to_crs("EPSG:4326")
        ucs = gpd.read_file(os.path.join(DADOS, "ucs_federais_amazonia_ocidental.gpkg")).to_crs("EPSG:4326")

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
        st_folium(m, use_container_width=True, height=520, returned_objects=[], key="mapa_pontos_M")
        st.caption("Pontos verdes = 37 registros de calibração · área tracejada = M (união de ecorregiões) · "
                   "polígonos verdes = 85 UCs de estudo.")
    except Exception as e:
        st.error(f"Não foi possível carregar a camada: {e}")

st.divider()
st.caption("Uiraçu 2.0 · leoaaragao/uiracu-2.0 · gerado com apoio de Claude (Anthropic) — ver ROTEIRO_DO_PROJETO.md")
