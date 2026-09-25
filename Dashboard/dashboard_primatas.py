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
def carregar_dados(incluir_rr: bool):
    """
    Dois universos de UC no projeto, por motivo conceitual (ver DIARIO_DE_BORDO.md):
    - 85 UCs (AM/AC/RO): usado para o SDM do Lagothrix lagothricha - Roraima
      excluida por limite biogeografico documentado (Rio Negro/Branco).
    - 92 UCs (AM/AC/RO/RR): usado para o produto multiespecie/diversidade -
      nao ha motivo para excluir Roraima quando se trata da comunidade de
      primatas como um todo (base do debate de bonus de biodiversidade).
    """
    if incluir_rr:
        arq_uc, arq_matriz, arq_ranking = (
            "ucs_federais_92_multiespecie.gpkg",
            "matriz_especies_x_ucs92_gbif.csv",
            "ranking_especies_por_incidencia_ucs92.csv",
        )
    else:
        arq_uc, arq_matriz, arq_ranking = (
            "ucs_federais_amazonia_ocidental.gpkg",
            "matriz_especies_x_ucs_gbif.csv",
            "ranking_especies_por_incidencia_ucs.csv",
        )
    ucs = gpd.read_file(os.path.join(RAIZ, "Dados", arq_uc)).to_crs("EPSG:4326")
    matriz = pd.read_csv(os.path.join(RAIZ, "Referencias", arq_matriz)).set_index("species")
    ranking = pd.read_csv(os.path.join(RAIZ, "Referencias", arq_ranking)).set_index("species")
    ocorrencias = pd.read_csv(os.path.join(RAIZ, "Referencias", "ocorrencias_primatas_brasil_gbif.csv"))
    ocorrencias = ocorrencias.dropna(subset=["decimalLatitude", "decimalLongitude"])
    return ucs, matriz, ranking, ocorrencias

@st.cache_data
def juntar_pontos_com_uc(_ucs, ocorrencias):
    """Marca, para TODAS as ocorrencias baixadas (168 especies), se cada ponto
    cai dentro de alguma UC do recorte ativo (join geometrico real, nao por pais)."""
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

# ---------------- Cabecalho ----------------
st.title("🐒 Primatas da Pan-Amazônia x Unidades de Conservação")

incluir_rr = st.toggle(
    "Incluir Roraima (produto multiespécie — 92 UCs)",
    value=True,
    help="Ligado: 92 UCs (AM/AC/RO/RR), para o painel de diversidade multiespécie — não há "
         "motivo biogeográfico para excluir Roraima quando o assunto é a comunidade de primatas "
         "como um todo. Desligado: 85 UCs (AM/AC/RO), o mesmo recorte usado no SDM do Lagothrix "
         "lagothricha, que tem o Rio Negro/Branco como limite de distribuição documentado.",
)

ucs, matriz, ranking, ocorrencias = carregar_dados(incluir_rr)
pontos_com_uc = juntar_pontos_com_uc(ucs, ocorrencias)

@st.cache_data
def carregar_area_M():
    """Area acessivel (M) do Lagothrix lagothricha - uniao de ecorregioes
    (Scripts/20_definir_area_M.py). So referencia visual; o SDM em si ainda
    nao foi rodado (ver DIARIO_DE_BORDO.md, Etapa 11)."""
    try:
        m = gpd.read_file(os.path.join(RAIZ, "Dados", "area_M_lagothrix_dissolvido.gpkg")).to_crs("EPSG:4326")
        return m
    except Exception:
        return None

area_M = carregar_area_M()

@st.cache_data
def carregar_nomes_fotos():
    """Nome popular e foto por especie (Scripts/21) - fonte: GBIF (vernacularNames
    + occurrence media), nada inventado. Species sem foto/nome ficam em branco."""
    try:
        df = pd.read_csv(os.path.join(RAIZ, "Referencias", "especies_nomes_populares_fotos.csv"))
        return df.set_index("canonicalName").to_dict("index")
    except Exception:
        return {}

INFO_ESPECIE = carregar_nomes_fotos()

def rotulo(especie: str) -> str:
    """'Lagothrix lagothricha' -> 'Lagothrix lagothricha — Macaco-barrigudo'"""
    nome = INFO_ESPECIE.get(especie, {}).get("nome_popular", "")
    return f"{especie} — {nome}" if isinstance(nome, str) and nome else especie

def html_hover_especie(especie: str) -> str:
    """Span com nome cientifico+popular; se houver foto, aparece ao passar o mouse (CSS puro)."""
    info = INFO_ESPECIE.get(especie, {})
    nome = info.get("nome_popular", "") if isinstance(info.get("nome_popular"), str) else ""
    foto = info.get("foto_url", "") if isinstance(info.get("foto_url"), str) else ""
    texto = f"<i>{especie}</i>" + (f" — {nome}" if nome else "")
    if foto:
        return (
            f'<span class="tt">{texto}'
            f'<span class="tt-img"><img src="{foto}" onerror="this.parentElement.style.display=\'none\'"/></span>'
            f'</span>'
        )
    return f'<span class="tt-sem-foto">{texto}</span>'

CSS_TOOLTIP = """
<style>
.tt { position: relative; display: inline-block; cursor: help; border-bottom: 1px dotted #B08D57; }
.tt-sem-foto { color: inherit; }
.tt .tt-img {
    visibility: hidden; opacity: 0; position: absolute; z-index: 999;
    bottom: 125%; left: 0; transition: opacity 0.15s ease-in-out;
    background: #0e1117; border: 2px solid #1F4E3D; border-radius: 6px; padding: 3px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.6);
}
.tt .tt-img img { width: 180px; height: auto; border-radius: 4px; display: block; }
.tt:hover .tt-img { visibility: visible; opacity: 1; }
</style>
"""
st.markdown(CSS_TOOLTIP, unsafe_allow_html=True)

# Riqueza por UC (n de especies com >=1 registro) e lista de especies por UC
riqueza = (matriz > 0).sum(axis=0)  # index = nome_uc
especies_por_uc = {
    uc: sorted(matriz.index[matriz[uc] > 0].tolist())
    for uc in matriz.columns
}
ucs["riqueza_primatas"] = ucs["nome_uc"].map(riqueza).fillna(0).astype(int)

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
    rank_plot["nome_popular"] = rank_plot["species"].map(
        lambda e: INFO_ESPECIE.get(e, {}).get("nome_popular", "") or "(sem nome popular no GBIF)"
    )
    fig = px.bar(
        rank_plot, x="n_ucs_com_registro", y="species", orientation="h",
        labels={"n_ucs_com_registro": "Nº de UCs com registro", "species": ""},
        color="n_ucs_com_registro", color_continuous_scale="Greens",
        hover_data={"n_registros_totais": True, "nome_popular": True},
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
    mostrar_M = st.checkbox(
        "Sobrepor área acessível (M) do Lagothrix lagothricha",
        value=False,
        disabled=(area_M is None),
        help="União de 11 ecorregiões tocadas pelos 37 pontos de calibração rarefeitos (Brasil) — "
             "estende-se a Peru, Bolívia e Colômbia. Só camada de referência: o modelo SDM em si "
             "ainda não foi ajustado (ver DIARIO_DE_BORDO.md, Etapa 11).",
    )

    def desenhar_M(mapa):
        if mostrar_M and area_M is not None:
            folium.GeoJson(
                area_M,
                style_function=lambda x: {
                    "fillColor": "#B08D57", "color": "#B08D57", "weight": 1.5,
                    "fillOpacity": 0.08, "dashArray": "5,5",
                },
                tooltip="Área acessível (M) — Lagothrix lagothricha (união de ecorregiões, Brasil+Peru+Bolívia+Colômbia)",
            ).add_to(mapa)

    if modo_mapa == "Riqueza agregada por UC":
        st.subheader("Mapa — riqueza de primatas por UC")
        m = folium.Map(location=[-7, -65], zoom_start=5, tiles="OpenStreetMap")
        desenhar_M(m)
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
                popup_html += "<br><br>" + "<br>".join(
                    f"• <i>{e}</i>" + (f" — {INFO_ESPECIE.get(e, {}).get('nome_popular', '')}"
                                        if isinstance(INFO_ESPECIE.get(e, {}).get("nome_popular"), str)
                                        and INFO_ESPECIE.get(e, {}).get("nome_popular") else "")
                    for e in especies_lista[:15]
                )
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
            especie_mapa = st.selectbox("Espécie", especies_disponiveis, format_func=rotulo, key="especie_mapa")
        with col_b:
            mostrar_fora = st.toggle("Incluir pontos fora das UCs", value=True)

        pts_especie = pontos_com_uc[pontos_com_uc["species"] == especie_mapa]
        n_dentro = int(pts_especie["dentro_de_uc"].sum())
        n_fora = int((~pts_especie["dentro_de_uc"]).sum())
        if not mostrar_fora:
            pts_especie = pts_especie[pts_especie["dentro_de_uc"]]

        st.caption(f"**{especie_mapa}**: {n_dentro} registro(s) dentro das UCs · {n_fora} fora (mesma região de busca)")

        m2 = folium.Map(location=[-7, -65], zoom_start=5, tiles="OpenStreetMap")
        desenhar_M(m2)
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

def tabela_html_com_foto(pares_especie_registros, col2_titulo="Registros"):
    """Renderiza uma tabelinha HTML onde cada especie tem hover-tooltip com foto (CSS puro)."""
    linhas = "".join(
        f"<tr><td style='padding:4px 10px 4px 0'>{html_hover_especie(e)}</td>"
        f"<td style='padding:4px; text-align:right; opacity:0.8'>{n}</td></tr>"
        for e, n in pares_especie_registros
    )
    st.markdown(
        f"<table style='width:100%; border-collapse:collapse'>"
        f"<tr><th style='text-align:left; padding:4px 10px 4px 0'>Espécie</th>"
        f"<th style='text-align:right; padding:4px'>{col2_titulo}</th></tr>{linhas}</table>",
        unsafe_allow_html=True,
    )
    st.caption("Passe o mouse sobre uma espécie para ver a foto (quando disponível — fonte: GBIF).")

with tab_esp:
    especie_sel = st.selectbox("Escolha uma espécie", sorted(matriz.index.tolist()), format_func=rotulo, key="especie_sel_tab")
    ucs_da_especie = matriz.columns[matriz.loc[especie_sel] > 0].tolist()

    col_foto, col_info = st.columns([1, 3])
    info_sel = INFO_ESPECIE.get(especie_sel, {})
    with col_foto:
        foto_url = info_sel.get("foto_url", "")
        if isinstance(foto_url, str) and foto_url:
            st.image(foto_url, use_container_width=True)
            creditos = info_sel.get("foto_creditos", "")
            licenca = info_sel.get("foto_licenca", "")
            if isinstance(creditos, str) and creditos:
                st.caption(f"📷 {creditos} · {licenca if isinstance(licenca, str) else ''}")
        else:
            st.caption("Sem foto disponível no GBIF para esta espécie.")
    with col_info:
        nome_pop = info_sel.get("nome_popular", "")
        if isinstance(nome_pop, str) and nome_pop:
            st.markdown(f"**Nome popular:** {nome_pop}")
        st.write(f"**{especie_sel}** tem registro confirmado em **{len(ucs_da_especie)}** UC(s):")
        if ucs_da_especie:
            tabela = pd.DataFrame({
                "UC": ucs_da_especie,
                "Registros": [int(matriz.loc[especie_sel, uc]) for uc in ucs_da_especie],
            }).sort_values("Registros", ascending=False)
            st.dataframe(tabela, use_container_width=True, hide_index=True)
        else:
            st.info(f"Nenhuma ocorrência confirmada dentro das {len(ucs)} UCs para esta espécie (pode ocorrer na região, fora dos limites das UCs).")

with tab_uc:
    uc_sel = st.selectbox("Escolha uma UC", sorted(matriz.columns.tolist()))
    especies_da_uc = matriz.index[matriz[uc_sel] > 0].tolist()
    st.write(f"**{uc_sel}** tem **{len(especies_da_uc)}** espécie(s) de primata com registro confirmado:")
    if especies_da_uc:
        pares = sorted(
            ((e, int(matriz.loc[e, uc_sel])) for e in especies_da_uc),
            key=lambda x: -x[1],
        )
        tabela_html_com_foto(pares)
    else:
        st.info("Nenhuma ocorrência confirmada dentro desta UC nos dados atuais.")

st.caption("Uiraçu 2.0 · leoaaragao/uiracu-2.0 · gerado com apoio de Claude (Anthropic) — ver DIARIO_DE_BORDO.md")
