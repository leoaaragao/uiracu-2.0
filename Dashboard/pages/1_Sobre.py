# -*- coding: utf-8 -*-
"""Uiraçu 2.0 — Sobre o projeto."""
import os
import sys

import streamlit as st

st.set_page_config(page_title="Uiraçu 2.0 — Sobre", layout="wide")

_DASHBOARD_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _DASHBOARD_DIR not in sys.path:
    sys.path.insert(0, _DASHBOARD_DIR)
from _seo import injetar_tags_og  # noqa: E402

injetar_tags_og()

st.title("Sobre o projeto")
st.caption(
    "Projeto da disciplina Análise espacial da biodiversidade, mudanças globais e inteligência artificial "
    "(ENBT/JBRJ, 2026-2, docente Marinez Ferreira de Siqueira) · Piloto reprodutível das "
    "Etapas 2/3 do projeto de doutorado **\"Priorização Espacial para Bônus de Biodiversidade "
    "em Unidades de Conservação da Amazônia\" (IPBB)** — Leonardo Andrade Aragão, ENBT/JBRJ, "
    "orientação do Prof. Dr. Carlos Eduardo de Viveiros Grelle."
)

st.markdown("""
**Resumo em linguagem acessível:** este projeto pergunta, de duas formas complementares, onde a
biodiversidade de primatas é maior e onde as condições ambientais são mais favoráveis a ela nas
Unidades de Conservação (UCs) federais da Amazônia Ocidental. É a mesma região e o mesmo objetivo
de fundo do projeto de doutorado do autor, que investiga como recompensar financeiramente UCs por
manterem biodiversidade (um "bônus de biodiversidade"). Este projeto de disciplina é o primeiro
piloto de dados reais dessa ideia.

**Por que "Uiraçu":** é um dos nomes populares, junto de "gavião-real", da maior ave de rapina
das Américas (*Harpia harpyja*), topo de cadeia alimentar e indicadora de floresta bem
conservada — na tese de doutorado, o painel interativo que resulta desta linha de trabalho
será batizado com esse nome.
""")

st.divider()

with st.expander("Metodologia (visão técnica)", expanded=False):
    st.markdown("""
O projeto tem duas partes independentes, ambas cobrindo os Estados da **Amazônia Ocidental**
(Amazonas, Acre, Rondônia — e Roraima quando o produto exige, ver nota abaixo), o mesmo recorte
regional do projeto de doutorado:

- **Verificação de riqueza (Parte 1):** varredura de ocorrências via API do GBIF
  (`occurrence/search`), sem restrição por país/estado declarado — associação a cada UC feita por
  geometria real (ponto dentro do polígono), não por rótulo textual, que pode estar incorreto
  (ver o caso documentado no `ROTEIRO_DO_PROJETO.md`).
- **Modelagem de distribuição — SDM (Parte 2):** GLM, Maxent (via biblioteca Python `elapid`,
  substituindo o software Maxent original de Phillips et al.) e Random Forest, ajustados sobre
  eixos de PCA das variáveis WorldClim, com validação cruzada K-fold, mapa de consenso e de
  incerteza, explicabilidade por importância de variáveis, e pós-processamento cruzando
  adequabilidade com cobertura florestal (MapBiomas, classe 3).
- **Roraima:** entra na Parte 1 (tem espécies próprias documentadas, faz parte da riqueza real da
  Amazônia Ocidental), mas fica fora da Parte 2 especificamente para *Lagothrix lagothricha*, por
  um limite biogeográfico real e documentado na literatura (barreira do Rio Negro/Branco) — não
  por falta de dado.

**Este projeto de disciplina corresponde apenas à Etapa 2 (SDM, 1 espécie) do framework de
doutorado, que tem 5 etapas no total.** As etapas seguintes, fora do escopo desta entrega, são:
diversidade funcional e filogenética para múltiplas espécies-chave/ameaçadas (Etapa 3), o Índice
de Prioridade de Bônus de Biodiversidade — IPBB, combinando SDM + diversidade + pressão antrópica
via planejamento sistemático (Etapa 4), e o protocolo de suporte à decisão (Etapa 5). A validação
dos modelos na tese também inclui cenários climáticos futuros (CMIP6) e a métrica TSS/ROC parcial
além do AUC — parte disso (TSS) já foi incorporada aqui como primeiro passo.

Processo completo, decisão por decisão, incluindo os erros e ajustes no caminho, está registrado
em [`ROTEIRO_DO_PROJETO.md`](https://github.com/leoaaragao/uiracu-2.0/blob/main/ROTEIRO_DO_PROJETO.md).
    """)

st.markdown("Use o menu à esquerda para navegar: **Riqueza de Espécies** e **Modelagem Lagothrix** "
            "mostram os resultados de cada parte; **Roteiro do Projeto** traz o registro completo "
            "de decisões, direto aqui no site, sem precisar abrir o GitHub.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Parte 1 — Riqueza de espécies")
    st.markdown("""
**Pergunta:** quais Unidades de Conservação da Amazônia Ocidental têm mais espécies de primata?

- Todas as **168 espécies** de primata pan-amazônicas pesquisadas no GBIF
- Todas as **92 UCs federais** (Amazonas, Acre, Rondônia **e Roraima**)
- Mapa de riqueza, ranking por incidência, nome popular e foto de cada espécie
- Baseado em **evidência de ocorrência** (registros confirmados), não em modelagem

*Status: completo e interativo.*
""")

with col2:
    st.subheader("Parte 2 — Modelagem do macaco-barrigudo (Lagothrix lagothricha)")
    st.markdown("""
**Pergunta:** onde estão as condições ambientais mais adequadas para o macaco-barrigudo-cinza?

- Estudo de caso aprofundado de **1 espécie**, cumprindo o exercício de modelagem da disciplina
  (GLM, Maxent, Random Forest, validação cruzada, incerteza — Fichas 2.6 a 2.9)
- Escopo: **85 UCs** (Amazonas, Acre, Rondônia) — Roraima fica fora por limite biogeográfico
  documentado (Rio Negro/Branco), não por falta de dado
- Modelos ajustados e validados, mapas de consenso/incerteza, explicabilidade e cruzamento com
  cobertura florestal (MapBiomas) por UC

*Status: completo — ver detalhes na página.*

> Este piloto cobre **1 espécie** e a dimensão de adequabilidade ambiental (SDM). Na tese de
> doutorado, o mesmo framework será aplicado a **múltiplas espécies-chave e ameaçadas** (não só
> primatas), e somado a **métricas de diversidade funcional** (riqueza, equabilidade e divergência
> funcional) e **filogenética** (índice de Faith, distinção evolutiva) — o SDM aqui é a primeira
> das quatro camadas de informação que compõem o IPBB.
""")

st.divider()
with st.expander("Ferramentas e uso de IA"):
    st.markdown("""
**IA:**
- **Claude (Anthropic):** assistência de programação, organização de dados e auditoria assistida
  nesta fase do projeto (Uiraçu 2.0), com decisão científica e verificação sempre humanas,
  conforme os Protocolos 01 e 02 da disciplina.
- **Google Antigravity:** usado no protótipo anterior, Uiraçu 1.0 (interface e conceito de painel
  reaproveitados aqui).

**Dados:**
- **APIs do GBIF** (`occurrence/search` e `occurrence/download`, esta com DOI): fonte direta de
  todos os dados de ocorrência de primatas, sem intermediários.
- **WorldClim v2.1** (variáveis bioclimáticas) e **MapBiomas Coleção 11** (cobertura da terra).

**Python — todo o pipeline (sem QGIS, sem R, sem software Maxent original):**
- **geopandas, shapely, pyproj, rasterio** — dados espaciais (vetor e raster)
- **pandas, numpy** — manipulação de dados
- **scikit-learn** — GLM (regressão logística), Random Forest, PCA, validação cruzada,
  importância por permutação
- **elapid** — reimplementação do algoritmo Maxent, usada no lugar do software original de
  Phillips et al. — declarado aqui como substituição de ferramenta
- **streamlit, streamlit-folium, folium, plotly, matplotlib** — este dashboard interativo
- **pygbif** — acesso programático à API do GBIF

Lista completa e versões exatas em [`requirements.txt`](https://github.com/leoaaragao/uiracu-2.0/blob/main/requirements.txt).
Detalhes completos, decisão por decisão, em [`ROTEIRO_DO_PROJETO.md`](https://github.com/leoaaragao/uiracu-2.0/blob/main/ROTEIRO_DO_PROJETO.md).
    """)

st.caption("Uiraçu 2.0 · [leoaaragao/uiracu-2.0](https://github.com/leoaaragao/uiracu-2.0) · gerado com Python, Claude (Anthropic), "
           "Google Antigravity e APIs do GBIF — ver ROTEIRO_DO_PROJETO.md")
