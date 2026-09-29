# -*- coding: utf-8 -*-
"""Injeta tags Open Graph no index.html do Streamlit (previa de link no
WhatsApp/Discord/Telegram). Streamlit nao gera isso nativamente. Chamado do
topo de cada pagina (Inicio.py e Dashboard/pages/*.py) para funcionar
independente de qual pagina alguem acessa primeiro."""
import os

URL_PUBLICA = "https://uiracu-jbrj.up.railway.app"

_TAGS = f"""
    <meta property="og:title" content="Uiraçu 2.0 — Biodiversidade de Primatas na Amazônia" />
    <meta property="og:description" content="Riqueza de 168 espécies em 92 UCs federais + modelagem de distribuição (SDM) de Lagothrix lagothricha em 85 UCs. Projeto ENBT/JBRJ, piloto de doutorado (IPBB)." />
    <meta property="og:image" content="{URL_PUBLICA}/app/static/og-image.jpg" />
    <meta property="og:type" content="website" />
    <meta property="og:url" content="{URL_PUBLICA}" />
    <meta name="twitter:card" content="summary_large_image" />
"""


def injetar_tags_og():
    try:
        import streamlit as st_module
        caminho = os.path.join(os.path.dirname(st_module.__file__), "static", "index.html")
        with open(caminho, encoding="utf-8") as f:
            html = f.read()
        if "og:title" in html:
            return
        html = html.replace("</head>", _TAGS + "  </head>")
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(html)
    except Exception:
        pass  # nunca deixa isso quebrar o app
