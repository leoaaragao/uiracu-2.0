# Uiraçu 2.0

Duas partes independentes, biodiversidade de primatas na Amazônia Ocidental, usando dados abertos e IA.

Projeto desenvolvido para a disciplina **Análise espacial da biodiversidade, mudanças globais e inteligência artificial** (ENBT/JBRJ, 2026-2, docente Marinez Ferreira de Siqueira), e usado como piloto reprodutível das Etapas 2/3 do projeto de doutorado *"Priorização Espacial para Bônus de Biodiversidade em Unidades de Conservação da Amazônia" (IPBB)*.

> Continuação do protótipo de interface [Uiraçu - Biodiversity Bonus](../Uiraçu%20-%20Biodiversity%20Bonus), reaproveitando a base de Unidades de Conservação (CNUC) e o conceito de painel interativo, agora com dados reais.

## Parte 1 — Riqueza de primatas nas UCs (✅ completa)

**Pergunta:** quais Unidades de Conservação federais da Amazônia têm mais espécies de primata?

- **168 espécies** pan-amazônicas (todos os gêneros de primata), **92 UCs** (Amazonas, Acre, Rondônia **e Roraima** — não há motivo biogeográfico para excluir Roraima quando o assunto é a comunidade toda; ver `DIARIO_DE_BORDO.md`).
- Baseado em evidência de ocorrência (GBIF), com nome popular e foto por espécie.
- Dashboard interativo pronto (mapa de riqueza, ranking, exploração por espécie/UC).

## Parte 2 — Modelagem de *Lagothrix lagothricha* (🔧 em andamento)

**Pergunta:** onde estão as condições mais adequadas para o macaco-barrigudo-cinza?

Estudo de caso aprofundado de **1 espécie**, cumprindo o exercício de modelagem da disciplina (SDM: GLM, Maxent, Random Forest, validação cruzada, incerteza — Fichas 2.6 a 2.9). Escopo: **85 UCs** (Amazonas, Acre, Rondônia) — Roraima fica fora por limite biogeográfico documentado (Rio Negro/Branco), diferente da Parte 1.

Já feito: auditoria taxonômica, rarefação espacial (37 pontos de calibração), área acessível (M, 3,24 milhões km², por união de ecorregiões). Falta: variáveis climáticas, ajuste dos modelos, mapas de consenso/incerteza.

Processo completo, decisão por decisão — incluindo onde e como a IA (Claude) ajudou — está documentado em [`DIARIO_DE_BORDO.md`](DIARIO_DE_BORDO.md).

## Dados e fontes

| Dado | Fonte | Licença/uso |
|---|---|---|
| Unidades de Conservação (CNUC) | MMA/ICMBio, via reaproveitamento do projeto Uiraçu 1.0 | Dado público |
| Ocorrências de *Lagothrix lagothricha* | GBIF.org, [doi.org/10.15468/dl.pxqmwc](https://doi.org/10.15468/dl.pxqmwc) (23/09/2026) | GBIF Data User Agreement |
| Ocorrências de outros primatas (168 espécies, sem DOI) | GBIF.org, API `occurrence/search` (24/09/2026) | GBIF Data User Agreement |
| Nomes populares e fotos | GBIF (`vernacularNames` + `occurrence` media) | Variável por registro — ver `Referencias/especies_nomes_populares_fotos.csv` |
| Ecorregiões (base para a área M) | WWF Terrestrial Ecoregions (Olson et al. 2001), via material da disciplina | Dado público |
| Fronteiras internacionais | ESRI World Countries, via material da disciplina | Dado público |
| Variáveis climáticas | WorldClim v2.1 (10 min de arco), via material da disciplina | *(a integrar)* |

## Como reproduzir

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Scripts em ordem de execução em `Scripts/` (numerados). Cada um documenta, no cabeçalho, a qual bloco da Ficha operacional da disciplina corresponde.

### Dashboard interativo (2 páginas)

```bash
.venv\Scripts\python.exe -m streamlit run Dashboard\Inicio.py
```

Abre em `http://localhost:8501`, com navegação no menu lateral: **Riqueza de Espécies** (Parte 1) e **Modelagem Lagothrix** (Parte 2). Use `python -m streamlit`, não o `streamlit.exe` direto — o executável do pacote está quebrado nesta instalação.

## Estrutura

```
Uiracu-2.0/
├── Dados/               # dados brutos e derivados (grandes ficam fora do git — ver .gitignore)
├── Scripts/             # pipeline em Python, numerado por etapa
├── Dashboard/           # app Streamlit multi-página (Inicio.py + pages/)
├── Resultados/          # saidas de modelo, mapas
├── Evidencias/          # capturas de tela do processo (auditoria/reprodutibilidade)
├── Referencias/         # material de apoio curado (checklist de primatas, cruzamentos, nomes/fotos)
├── DIARIO_DE_BORDO.md   # registro cronológico de decisões e uso de IA
└── requirements.txt
```

## Uso de IA

Este projeto foi desenvolvido com apoio de IA generativa (Claude/Anthropic), sob supervisão humana em cada decisão científica, conforme os Protocolos 01 e 02 da disciplina. Detalhes em [`DIARIO_DE_BORDO.md`](DIARIO_DE_BORDO.md).

## Autor

Leonardo Andrade Aragão — Doutorando, ENBT/JBRJ. Orientador: Prof. Dr. Carlos Eduardo de Viveiros Grelle.
