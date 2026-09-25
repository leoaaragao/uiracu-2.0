# -*- coding: utf-8 -*-
"""
Uiraçu 2.0 — Pagina inicial. Roda com: streamlit run Dashboard/Inicio.py
"""
import streamlit as st

st.set_page_config(page_title="Uiraçu 2.0", layout="wide", page_icon="🦍")

st.title("🦍 Uiraçu 2.0")
st.caption(
    "Projeto da disciplina Análise espacial da biodiversidade, mudanças globais e IA "
    "(ENBT/JBRJ 2026-2) · Piloto da Etapa 2/3 do projeto de doutorado (IPBB)"
)

st.markdown("""
O projeto tem **duas partes independentes**, cada uma respondendo a uma pergunta diferente
— use o menu à esquerda para navegar entre elas.
""")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🐒 Parte 1 — Riqueza de espécies")
    st.markdown("""
**Pergunta:** quais Unidades de Conservação da Amazônia têm mais espécies de primata?

- Todas as **168 espécies** de primata pan-amazônicas pesquisadas no GBIF
- Todas as **92 UCs federais** (Amazonas, Acre, Rondônia **e Roraima**)
- Mapa de riqueza, ranking por incidência, nome popular e foto de cada espécie
- Baseado em **evidência de ocorrência** (registros confirmados), não em modelagem

*Status: ✅ completo e interativo.*
""")

with col2:
    st.subheader("🐵 Parte 2 — Modelagem do macaco-barrigudo")
    st.markdown("""
**Pergunta:** onde estão as condições ambientais mais adequadas para *Lagothrix lagothricha*?

- Estudo de caso aprofundado de **1 espécie**, cumprindo o exercício de modelagem da disciplina
  (GLM, Maxent, Random Forest, validação cruzada, incerteza — Fichas 2.6 a 2.9)
- Escopo: **85 UCs** (Amazonas, Acre, Rondônia) — Roraima fica fora por limite biogeográfico
  documentado (Rio Negro/Branco), não por falta de dado
- Já feito: auditoria, rarefação espacial, área acessível (M) por união de ecorregiões
- Falta: variáveis climáticas (WorldClim), ajuste dos modelos, mapa de consenso e incerteza

*Status: 🔧 em andamento — ver detalhes na página.*
""")

st.divider()
st.caption("Uiraçu 2.0 · leoaaragao/uiracu-2.0 · gerado com apoio de Claude (Anthropic) — ver DIARIO_DE_BORDO.md")
