# Uiraçu 2.0

Priorização espacial de biodiversidade em Unidades de Conservação federais da Amazônia Ocidental (Amazonas, Acre, Rondônia), usando modelagem de distribuição de espécies (SDM) e dados abertos.

> Roraima foi avaliada e excluída do recorte: o Rio Negro/Rio Branco é um limite de distribuição documentado para a espécie foco. Ver [`DIARIO_DE_BORDO.md`](DIARIO_DE_BORDO.md#por-que-roraima-ficou-de-fora).

Projeto desenvolvido para a disciplina **Análise espacial da biodiversidade, mudanças globais e inteligência artificial** (ENBT/JBRJ, 2026-2, docente Marinez Ferreira de Siqueira), e usado como piloto reprodutível da Etapa 2 (SDM) do projeto de doutorado *"Priorização Espacial para Bônus de Biodiversidade em Unidades de Conservação da Amazônia" (IPBB)*.

> Continuação do protótipo de interface [Uiraçu - Biodiversity Bonus](../Uiraçu%20-%20Biodiversity%20Bonus), reaproveitando a base de Unidades de Conservação (CNUC) e o conceito de painel interativo, agora com dados reais e modelagem.

## Espécie foco

**_Lagothrix lagothricha_** (macaco-barrigudo-cinza; subespécie predominante na região: *L. l. cana*) — Em Perigo (IUCN, 2021), dispersora de sementes de grande porte, ocorrência documentada em Unidades de Conservação da Amazônia Ocidental.

## O que este repositório faz

1. Filtra as Unidades de Conservação **federais ativas** em AM/AC/RO a partir do CNUC (MMA/ICMBio) — 85 UCs.
2. Audita a taxonomia e coleta ocorrências da espécie no GBIF (script + download oficial com DOI).
3. *(em andamento)* Modela a adequabilidade ambiental (SDM) e cruza com as 85 UCs.
4. *(planejado)* Dashboard interativo em Streamlit para visualizar resultados.

Processo completo, decisão por decisão — incluindo onde e como a IA (Claude) ajudou — está documentado em [`DIARIO_DE_BORDO.md`](DIARIO_DE_BORDO.md).

## Dados e fontes

| Dado | Fonte | Licença/uso |
|---|---|---|
| Unidades de Conservação (CNUC) | MMA/ICMBio, via reaproveitamento do projeto Uiraçu 1.0 | Dado público |
| Ocorrências de *Lagothrix lagothricha* | GBIF.org, [doi.org/10.15468/dl.pxqmwc](https://doi.org/10.15468/dl.pxqmwc) (baixado em 23/09/2026) | GBIF Data User Agreement |
| Ocorrências de outros primatas (168 espécies, sem DOI) | GBIF.org, API `occurrence/search` (24/09/2026) | GBIF Data User Agreement |
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

### Dashboard interativo

```bash
.venv\Scripts\python.exe -m streamlit run Dashboard\dashboard_primatas.py
```

Abre em `http://localhost:8501`. Mostra o cruzamento primatas × UCs (Etapa "Referências"): mapa de riqueza por UC, ranking por incidência, e exploração filtrável por espécie ou por UC. (Use `python -m streamlit`, não o `streamlit.exe` direto — o executável do pacote está quebrado nesta instalação.)

## Estrutura

```
Uiracu-2.0/
├── Dados/              # dados brutos e derivados (grandes ficam fora do git — ver .gitignore)
├── Scripts/            # pipeline em Python, numerado por etapa
├── Resultados/         # saidas de modelo, mapas
├── Evidencias/         # capturas de tela do processo (auditoria/reprodutibilidade)
├── Referencias/         # material de apoio curado (ex.: checklist de primatas da Pan-Amazônia)
├── DIARIO_DE_BORDO.md  # registro cronológico de decisões e uso de IA
└── requirements.txt
```

## Uso de IA

Este projeto foi desenvolvido com apoio de IA generativa (Claude/Anthropic), sob supervisão humana em cada decisão científica, conforme os Protocolos 01 e 02 da disciplina. Detalhes em [`DIARIO_DE_BORDO.md`](DIARIO_DE_BORDO.md).

## Autor

Leonardo Andrade Aragão — Doutorando, ENBT/JBRJ. Orientador: Prof. Dr. Carlos Eduardo de Viveiros Grelle.
