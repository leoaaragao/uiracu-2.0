# -*- coding: utf-8 -*-
"""
Uiraçu 2.0 — Dashboard interativo: Primatas da Pan-Amazônia x UCs federais

Roda com:  streamlit run Dashboard/dashboard_primatas.py
"""
import os
import geopandas as gpd
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
import plotly.express as px

st.set_page_config(page_title="Uiraçu 2.0 — Primatas x UCs", layout="wide", page_icon="🐒")

# Raiz do projeto = pasta pai de Dashboard/ — resolvido pelo caminho do proprio
# arquivo, para funcionar independente de onde o streamlit for iniciado.
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------- Dados ----------------
@st.cache_data
def carregar_dados():
    ucs = gpd.read_file(os.path.join(RAIZ, "Dados", "ucs_federais_amazonia_ocidental.gpkg")).to_crs("EPSG:4326")
    matriz = pd.read_csv(os.path.join(RAIZ, "Referencias", "matriz_especies_x_ucs_gbif.csv")).set_index("species")
    ranking = pd.read_csv(os.path.join(RAIZ, "Referencias", "ranking_especies_por_incidencia_ucs.csv")).set_index("species")
    ocorrencias = pd.read_csv(os.path.join(RAIZ, "Referencias", "ocorrencias_primatas_brasil_gbif.csv"))
    ocorrencias = ocorrencias.dropna(subset=["decimalLatitude", "decimalLongitude"])
    return ucs, matriz, ranking, ocorrencias

@st.cache_data
def juntar_pontos_com_uc(_ucs, ocorrencias):
    """Marca, para TODAS as ocorrencias baixadas (168 especies), se cada ponto
    cai dentro de alguma das 85 UCs (join geometrico real, nao por pais)."""
    pontos = gpd.GeoDataFrame(
        ocorrencias,
        geometry=gpd.points_from_xy(ocorrencias["decimalLongitude"], ocorrencias["decimalLatitude"]),
        crs="EPSG:4326",
    )
    uc_slim = _ucs[["nome_uc", "geometry"]]
    j = gpd.sjoin(pontos, uc_slim, how="left", predicate="within")
    j["dentro_de_uc"] = j["nome_uc"].notna()
    j["nome_uc"] = j["nome_uc"].fillna("(fora das UCs de estudo)")
    return j.drop(columns="geometry")

ucs, matriz, ranking, ocorrencias = carregar_dados()
pontos_com_uc = juntar_pontos_com_uc(ucs, ocorrencias)

# Riqueza por UC (n de especies com >=1 registro) e lista de especies por UC
riqueza = (matriz > 0).sum(axis=0)  # index = nome_uc
especies_por_uc = {
    uc: sorted(matriz.index[matriz[uc] > 0].tolist())
    for uc in matriz.columns
}
ucs["riqueza_primatas"] = ucs["nome_uc"].map(riqueza).fillna(0).astype(int)

# ---------------- Cabecalho ----------------
st.title("🐒 Primatas da Pan-Amazônia x Unidades de Conservação")
st.caption(
    "Projeto Uiraçu 2.0 — disciplina Análise espacial da biodiversidade, mudanças globais e IA (ENBT/JBRJ 2026-2) · "
    "Piloto da Etapa 2/3 do projeto de doutorado (IPBB)"
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("UCs de estudo", len(ucs))
c2.metric("Espécies pesquisadas", 168)
c3.metric("Espécies com registro na região", int((matriz.sum(axis=1) > 0).sum()))
c4.metric("Ocorrências confirmadas dentro de UCs", int(matriz.values.sum()))

with st.expander("⚠️ Nota metodológica — leia antes de interpretar os números"):
    st.markdown("""
- **Fonte:** GBIF.org, via API de busca (`occurrence/search`) — **não é um dataset com DOI**, é uma varredura
  exploratória. Ver `Referencias/Primatas_x_UCs_GBIF.xlsx`, aba "Resumo e metodologia", para o processo completo.
- **Sem restrição política:** os pontos foram filtrados por uma caixa geográfica ao redor das UCs, não pelo país
  declarado no GBIF (que pode estar incorreto — ver caso "Loreto" no `DIARIO_DE_BORDO.md`). A associação a cada
  UC é feita por geometria real (ponto dentro do polígono).
- **Ausência de registro ≠ ausência da espécie.** Baixa incidência pode refletir esforço de amostragem, não
  biologia. Não usar este painel como prova definitiva de ocorrência/não ocorrência.
    """)

st.divider()

# ---------------- Layout principal ----------------
col_mapa, col_lateral = st.columns([2, 1])

with col_lateral:
    st.subheader("Ranking por incidência")
    top_n = st.slider("Mostrar top N espécies", 5, 50, 20)
    rank_plot = ranking.sort_values("n_ucs_com_registro", ascending=False).head(top_n).reset_index()
    fig = px.bar(
        rank_plot, x="n_ucs_com_registro", y="species", orientation="h",
        labels={"n_ucs_com_registro": "Nº de UCs com registro", "species": ""},
        color="n_ucs_com_registro", color_continuous_scale="Greens",
        hover_data={"n_registros_totais": True},
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=max(400, top_n * 22),
                       coloraxis_showscale=False, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig, use_container_width=True)

with col_mapa:
    modo_mapa = st.radio(
        "Modo do mapa",
        ["Riqueza agregada por UC", "Pontos de uma espécie (dentro/fora das UCs)"],
        horizontal=True,
    )

    if modo_mapa == "Riqueza agregada por UC":
        st.subheader("Mapa — riqueza de primatas por UC")
        m = folium.Map(location=[-7, -65], zoom_start=5, tiles="OpenStreetMap")
        maxr = max(int(ucs["riqueza_primatas"].max()), 1)

        def cor(r):
            if r == 0:
                return "#DDDDDD"
            frac = r / maxr
            g = int(230 - frac * 140)
            return f"#{g:02x}{int(120-frac*60):02x}{g-40:02x}"

        for _, row in ucs.iterrows():
            especies_lista = especies_por_uc.get(row["nome_uc"], [])
            popup_html = f"<b>{row['nome_uc']}</b><br>Categoria: {row['categoria']}<br>" \
                          f"Riqueza de primatas (evidência GBIF): <b>{row['riqueza_primatas']}</b>"
            if especies_lista:
                popup_html += "<br><br>" + "<br>".join(f"• <i>{e}</i>" for e in especies_lista[:15])
                if len(especies_lista) > 15:
                    popup_html += f"<br>... e mais {len(especies_lista)-15}"
            folium.GeoJson(
                row["geometry"],
                style_function=lambda x, c=cor(row["riqueza_primatas"]): {
                    "fillColor": c, "color": "#1F4E3D", "weight": 0.8, "fillOpacity": 0.75,
                },
                tooltip=f"{row['nome_uc']} — {row['riqueza_primatas']} espécies",
                popup=folium.Popup(popup_html, max_width=300),
            ).add_to(m)

        st_folium(m, use_container_width=True, height=560, returned_objects=[])

    else:
        st.subheader("Mapa — ocorrências de uma espécie")
        especies_disponiveis = sorted(pontos_com_uc["species"].dropna().unique().tolist())
        col_a, col_b = st.columns([2, 1])
        with col_a:
            especie_mapa = st.selectbox("Espécie", especies_disponiveis, key="especie_mapa")
        with col_b:
            mostrar_fora = st.toggle("Incluir pontos fora das UCs", value=True)

        pts_especie = pontos_com_uc[pontos_com_uc["species"] == especie_mapa]
        n_dentro = int(pts_especie["dentro_de_uc"].sum())
        n_fora = int((~pts_especie["dentro_de_uc"]).sum())
        if not mostrar_fora:
            pts_especie = pts_especie[pts_especie["dentro_de_uc"]]

        st.caption(f"**{especie_mapa}**: {n_dentro} registro(s) dentro das UCs · {n_fora} fora (mesma região de busca)")

        m2 = folium.Map(location=[-7, -65], zoom_start=5, tiles="OpenStreetMap")
        # UCs como contorno de referencia, sem preenchimento por riqueza
        folium.GeoJson(
            ucs[["nome_uc", "geometry"]],
            style_function=lambda x: {"fillColor": "#E8F0EC", "color": "#1F4E3D", "weight": 0.6, "fillOpacity": 0.25},
            tooltip=folium.GeoJsonTooltip(fields=["nome_uc"]),
        ).add_to(m2)

        for _, p in pts_especie.iterrows():
            dentro = bool(p["dentro_de_uc"])
            folium.CircleMarker(
                location=[p["decimalLatitude"], p["decimalLongitude"]],
                radius=5 if dentro else 4,
                color="white", weight=1,
                fill=True, fill_color=("#1F4E3D" if dentro else "#B08D57"), fill_opacity=0.85,
                popup=folium.Popup(
                    f"<b>{especie_mapa}</b><br>"
                    f"{'Dentro de: ' + p['nome_uc'] if dentro else 'Fora das UCs de estudo'}<br>"
                    f"Ano: {p.get('year', '—')}<br>Tipo: {p.get('basisOfRecord', '—')}",
                    max_width=260,
                ),
            ).add_to(m2)

        st.markdown(
            "🟢 dentro de UC &nbsp;&nbsp; 🟤 fora das UCs de estudo",
            unsafe_allow_html=False,
        )
        st_folium(m2, use_container_width=True, height=520, returned_objects=[])

st.divider()

# ---------------- Explorar por especie ou por UC ----------------
tab_esp, tab_uc = st.tabs(["🔍 Explorar por espécie", "🔍 Explorar por UC"])

with tab_esp:
    especie_sel = st.selectbox("Escolha uma espécie", sorted(matriz.index.tolist()))
    ucs_da_especie = matriz.columns[matriz.loc[especie_sel] > 0].tolist()
    st.write(f"**{especie_sel}** tem registro confirmado em **{len(ucs_da_especie)}** UC(s):")
    if ucs_da_especie:
        tabela = pd.DataFrame({
            "UC": ucs_da_especie,
            "Registros": [int(matriz.loc[especie_sel, uc]) for uc in ucs_da_especie],
        }).sort_values("Registros", ascending=False)
        st.dataframe(tabela, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma ocorrência confirmada dentro das 85 UCs para esta espécie (pode ocorrer na região, fora dos limites das UCs).")

with tab_uc:
    uc_sel = st.selectbox("Escolha uma UC", sorted(matriz.columns.tolist()))
    especies_da_uc = matriz.index[matriz[uc_sel] > 0].tolist()
    st.write(f"**{uc_sel}** tem **{len(especies_da_uc)}** espécie(s) de primata com registro confirmado:")
    if especies_da_uc:
        tabela2 = pd.DataFrame({
            "Espécie": especies_da_uc,
            "Registros": [int(matriz.loc[e, uc_sel]) for e in especies_da_uc],
        }).sort_values("Registros", ascending=False)
        st.dataframe(tabela2, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma ocorrência confirmada dentro desta UC nos dados atuais.")

st.caption("Uiraçu 2.0 · leoaaragao/uiracu-2.0 · gerado com apoio de Claude (Anthropic) — ver DIARIO_DE_BORDO.md")
