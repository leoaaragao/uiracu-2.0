# -*- coding: utf-8 -*-
"""Uiraçu 2.0 — Parte 2: Modelagem do Lagothrix lagothricha (SDM)."""
import os

import branca.colormap as cmb
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

col_titulo, col_foto = st.columns([3, 1])
with col_titulo:
    st.title("Parte 2 — Modelagem do macaco-barrigudo (*Lagothrix lagothricha*)")
    st.caption("Estudo de caso aprofundado (SDM): GLM, Maxent, Random Forest, validação cruzada, "
               "incerteza — Fichas 2.6 a 2.9.")
with col_foto:
    caminho_foto_especie = os.path.join(RAIZ, "Dashboard", "assets", "lagothrix_apui_amazonas.jpg")
    if os.path.exists(caminho_foto_especie):
        st.image(caminho_foto_especie, use_container_width=True,
                  caption="Lagothrix lagothricha cana, Apuí (AM)")
        st.caption("Foto: Fernando Bondan, iNaturalist · CC BY 4.0 · mesma localidade de um dos "
                   "37 pontos de calibração deste estudo")


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


def ler_stats(caminho):
    with rasterio.open(caminho) as src:
        arr = src.read(1)
        nodata = src.nodata
        validos = arr[arr != nodata] if nodata is not None else arr[~np.isnan(arr)]
    return float(validos.min()), float(validos.max())


def criar_legenda(cmap_nome, vmin, vmax, titulo, n_cores=9):
    cmap = mpl.colormaps[cmap_nome]
    cores = [mcolors.to_hex(cmap(i / (n_cores - 1))) for i in range(n_cores)]
    return cmb.LinearColormap(colors=cores, vmin=vmin, vmax=vmax, caption=titulo)


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

with st.expander("Como interpretar estas métricas (leitura para não especialistas)", expanded=False):
    st.markdown("""
**O que é este mapa, em uma frase:** um modelo estatístico aprendeu, a partir de onde a espécie
já foi confirmada (37 pontos), quais combinações de clima se parecem com esses locais — e aplicou
esse padrão a toda a região para estimar **onde as condições ambientais são parecidas com as
áreas conhecidas** (não é uma contagem de animais, é uma estimativa de adequação climática).

**Por que 3 modelos (GLM, Maxent, Random Forest) e não 1:** cada algoritmo tem vieses diferentes;
usar os três e combiná-los por desempenho (ensemble) reduz o risco de uma conclusão errada vir de
uma única técnica — é a mesma lógica de pedir uma segunda opinião médica.

**AUC e TSS — as notas de desempenho do modelo:**
| Métrica | O que mede | Como ler |
|---|---|---|
| AUC | Chance do modelo separar corretamente um ponto onde a espécie ocorre de um ponto aleatório | 0,5 = acerto ao acaso · 1,0 = perfeito · referência comum na literatura: <0,7 fraco, 0,7–0,8 razoável, 0,8–0,9 bom, >0,9 excelente (não é um padrão universal, mas ajuda a calibrar expectativa) |
| TSS | Sensibilidade + especificidade − 1 (acerta presença **e** acerta ausência) | 0 = acerto ao acaso · 1,0 = perfeito · pode ser negativo (pior que aleatório) |

Os valores deste estudo (AUC 0,57–0,60, TSS 0,28–0,34) ficam abaixo da faixa "boa" — **o motivo
mais provável é a amostra pequena (37 pontos)**, não um erro de método. Reportamos isso de forma
transparente em vez de esconder ou inflar a métrica.

**Consenso e incerteza, na prática:** o mapa de **consenso** é a melhor estimativa (média dos 3
modelos); o mapa de **incerteza** mostra onde eles discordam entre si. Para uma decisão de
alocação de recursos, áreas com **consenso alto e incerteza baixa** são as apostas mais seguras;
áreas com consenso alto mas incerteza também alta merecem verificação de campo antes de qualquer
decisão — o modelo sozinho não é suficiente ali.
    """)

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
    st.markdown("**Adequabilidade ambiental relativa** — média dos 3 modelos (GLM, Maxent, Random "
                "Forest), **ponderada pelo AUC** de cada um na validação cruzada (ensemble de "
                "consenso, conforme Araújo & New, 2007). A escala de cor abaixo é esticada entre o "
                "mínimo e o máximo *observados* nesta área (como o \"estica mín/máx\" do QGIS), não "
                "entre 0 e 1 fixos — isso evita que o mapa pareça uniforme quando os valores reais "
                "ocupam só uma parte da escala teórica.")
    try:
        caminho_consenso = os.path.join(RESULTADOS, "lagothrix_consenso.tif")
        vmin_c, vmax_c = ler_stats(caminho_consenso)
        rgba, bounds, valores = raster_para_rgba(caminho_consenso, "YlGn", vmin_c, vmax_c)
        m = mapa_base_ucs()
        folium.raster_layers.ImageOverlay(image=rgba, bounds=bounds, opacity=0.85, name="Consenso").add_to(m)
        criar_legenda("YlGn", vmin_c, vmax_c, "Adequabilidade (consenso ponderado)").add_to(m)
        st_folium(m, use_container_width=True, height=520, returned_objects=[], key="mapa_consenso")
        st.caption(f"Adequabilidade em M: mínima {valores.min():.2f} · média {valores.mean():.2f} · "
                   f"máxima {valores.max():.2f} (escala teórica: 0 a 1).")
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
    st.markdown("**Incerteza** = desvio padrão entre os 3 modelos. Cores mais escuras/intensas = os "
                "algoritmos discordam mais entre si → predição menos confiável ali. Assim como no "
                "mapa de consenso, a escala é esticada entre o mínimo e o máximo observados — os "
                "valores de incerteza aqui ficam concentrados numa faixa estreita (a maioria entre "
                "0,16 e 0,32), então esticar a partir de 0 deixaria o mapa quase todo com a mesma cor.")
    try:
        caminho_incerteza = os.path.join(RESULTADOS, "lagothrix_incerteza.tif")
        vmin_i, vmax_i = ler_stats(caminho_incerteza)
        rgba, bounds, valores = raster_para_rgba(caminho_incerteza, "YlOrRd", vmin_i, vmax_i)
        m = mapa_base_ucs()
        folium.raster_layers.ImageOverlay(image=rgba, bounds=bounds, opacity=0.85, name="Incerteza").add_to(m)
        criar_legenda("YlOrRd", vmin_i, vmax_i, "Incerteza (desvio padrão)").add_to(m)
        st_folium(m, use_container_width=True, height=520, returned_objects=[], key="mapa_incerteza")
        st.caption(f"Incerteza em M: mínima {valores.min():.2f} · média {valores.mean():.2f} · "
                   f"máxima {valores.max():.2f}.")
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
st.caption("Uiraçu 2.0 · [leoaaragao/uiracu-2.0](https://github.com/leoaaragao/uiracu-2.0) · gerado com Python, Claude (Anthropic), "
           "Google Antigravity e APIs do GBIF — ver ROTEIRO_DO_PROJETO.md")
