# -*- coding: utf-8 -*-
"""Uiraçu 2.0 — Roteiro do projeto (renderizado direto no dashboard)."""
import os
import re

import streamlit as st

st.set_page_config(page_title="Uiraçu 2.0 — Roteiro do Projeto", layout="wide")

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CAMINHO_ROTEIRO = os.path.join(RAIZ, "ROTEIRO_DO_PROJETO.md")

st.title("Roteiro do Projeto")
st.caption("Registro cronológico de decisões, erros e ajustes — a mesma fonte usada para o "
           "relatório final. Renderizado direto do arquivo do repositório, sempre atualizado.")

try:
    with open(CAMINHO_ROTEIRO, encoding="utf-8") as f:
        texto = f.read()
except Exception as e:
    st.error(f"Não foi possível carregar o roteiro: {e}")
    st.stop()

# Divide o documento em seções por cabeçalho de nível 2 ("## ..."), preservando
# o texto de abertura (antes do primeiro "## ") como uma seção própria.
partes = re.split(r"(?m)^(## .+)$", texto)
secoes = {"Documento completo": texto}
if partes[0].strip():
    secoes["Abertura"] = partes[0]
for i in range(1, len(partes), 2):
    titulo = partes[i].lstrip("# ").strip()
    corpo = partes[i] + (partes[i + 1] if i + 1 < len(partes) else "")
    secoes[titulo] = corpo

secao_escolhida = st.selectbox("Ir para a seção:", list(secoes.keys()))
st.divider()
st.markdown(secoes[secao_escolhida])

st.divider()
st.caption("Uiraçu 2.0 · [leoaaragao/uiracu-2.0](https://github.com/leoaaragao/uiracu-2.0) · "
           "versão completa e histórico de commits no "
           "[ROTEIRO_DO_PROJETO.md](https://github.com/leoaaragao/uiracu-2.0/blob/main/ROTEIRO_DO_PROJETO.md) "
           "no GitHub")
