# -*- coding: utf-8 -*-
"""
Uiraçu 2.0 — Capa. Roda com: streamlit run Dashboard/Inicio.py
"""
import os
import sys
import streamlit as st

st.set_page_config(page_title="Uiraçu 2.0", layout="wide")

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))
if _DASHBOARD_DIR not in sys.path:
    sys.path.insert(0, _DASHBOARD_DIR)
from _seo import injetar_tags_og  # noqa: E402

injetar_tags_og()

caminho_foto = os.path.join(RAIZ, "Dashboard", "assets", "gaviao_real_juruena_amazonas.jpg")
if os.path.exists(caminho_foto):
    st.image(caminho_foto, use_container_width=True)
    st.caption("Gavião-real (*Harpia harpyja*), Parque Nacional do Juruena (AM) · Foto: Vinícius "
               "Pires Nogueira, CC BY-SA 4.0, via Wikimedia Commons")

st.title("Uiraçu 2.0")
st.markdown(
    "Biodiversidade de primatas nas Unidades de Conservação da Amazônia Ocidental — riqueza de "
    "espécies e modelagem preditiva, com dados abertos e código reprodutível."
)
st.caption("Use o menu à esquerda para navegar. Comece por **Sobre**, para conhecer o projeto.")

st.divider()
st.caption("Uiraçu 2.0 · [leoaaragao/uiracu-2.0](https://github.com/leoaaragao/uiracu-2.0) · gerado com Python, Claude (Anthropic), "
           "Google Antigravity e APIs do GBIF — ver ROTEIRO_DO_PROJETO.md")
