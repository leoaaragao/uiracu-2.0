# Uiraçu 2.0

Duas partes independentes, biodiversidade de primatas na Amazônia Ocidental, usando dados abertos e IA.

Projeto desenvolvido para a disciplina **Análise espacial da biodiversidade, mudanças globais e inteligência artificial** (ENBT/JBRJ, 2026-2, docente Marinez Ferreira de Siqueira), e usado como piloto reprodutível das Etapas 2/3 do projeto de doutorado *"Priorização Espacial para Bônus de Biodiversidade em Unidades de Conservação da Amazônia" (IPBB)*.

> Continuação do protótipo de interface [Uiraçu - Biodiversity Bonus](../Uiraçu%20-%20Biodiversity%20Bonus), reaproveitando a base de Unidades de Conservação (CNUC) e o conceito de painel interativo, agora com dados reais.

## Parte 1 — Riqueza de primatas nas UCs (✅ completa)

**Pergunta:** quais Unidades de Conservação federais da Amazônia têm mais espécies de primata?

- **168 espécies** pan-amazônicas (todos os gêneros de primata), **92 UCs** (Amazonas, Acre, Rondônia **e Roraima** — não há motivo biogeográfico para excluir Roraima quando o assunto é a comunidade toda; ver `ROTEIRO_DO_PROJETO.md`).
- Baseado em evidência de ocorrência (GBIF), com nome popular e foto por espécie.
- Dashboard interativo pronto (mapa de riqueza, ranking, exploração por espécie/UC).

## Parte 2 — Modelagem de *Lagothrix lagothricha* (✅ modelagem completa)

**Pergunta:** onde estão as condições mais adequadas para o macaco-barrigudo-cinza?

Estudo de caso aprofundado de **1 espécie**, cumprindo o exercício de modelagem da disciplina (SDM: GLM, Maxent, Random Forest, validação cruzada, incerteza — Fichas 2.6 a 2.9). Escopo: **85 UCs** (Amazonas, Acre, Rondônia) — Roraima fica fora por limite biogeográfico documentado (Rio Negro/Branco), diferente da Parte 1.

Pipeline completo: auditoria taxonômica → rarefação espacial (37 pontos de calibração) → área acessível M (3,24 milhões km², união de 11 ecorregiões) → variáveis climáticas (WorldClim, recortadas para M) → background (5.000 pontos) + PCA (4 eixos, 91,8% da variância) → **GLM, Maxent (`elapid`) e Random Forest**, com validação cruzada 5-fold (AUC 0,57–0,60 e TSS 0,28–0,34 — amostra pequena, resultado reportado com transparência) → consenso ponderado pelo AUC de cada modelo + mapa de incerteza + mapa binário apto/não apto → explicabilidade (importância dos eixos de PCA) → pós-processamento cruzando adequabilidade × MapBiomas (Formação Florestal) × 85 UCs. Tudo integrado ao dashboard interativo.

**Escopo desta entrega vs. a tese de doutorado:** este projeto corresponde à Etapa 2 (SDM) de um framework de 5 etapas. Aqui, o SDM cobre **1 espécie** (*Lagothrix lagothricha*). Na tese, o mesmo método será aplicado a **múltiplas espécies-chave e ameaçadas**, combinado com **diversidade funcional** (riqueza, equabilidade, divergência funcional) e **diversidade filogenética** (índice de Faith, distinção evolutiva) — Etapa 3 — para compor o Índice de Prioridade de Bônus de Biodiversidade (IPBB) — Etapa 4. Essas etapas seguintes estão fora do escopo desta disciplina.

Processo completo, decisão por decisão — incluindo onde e como a IA (Claude) ajudou — está documentado em [`ROTEIRO_DO_PROJETO.md`](ROTEIRO_DO_PROJETO.md).

## Dados e fontes

| Dado | Fonte | Licença/uso |
|---|---|---|
| Unidades de Conservação (CNUC) | MMA/ICMBio, via reaproveitamento do projeto Uiraçu 1.0 | Dado público |
| Ocorrências de *Lagothrix lagothricha* | GBIF.org, [doi.org/10.15468/dl.pxqmwc](https://doi.org/10.15468/dl.pxqmwc) (23/09/2026) | GBIF Data User Agreement |
| Ocorrências de outros primatas (168 espécies, sem DOI) | GBIF.org, API `occurrence/search` (24/09/2026) | GBIF Data User Agreement |
| Nomes populares e fotos | GBIF (`vernacularNames` + `occurrence` media) | Variável por registro — ver `Referencias/especies_nomes_populares_fotos.csv` |
| Ecorregiões (base para a área M) | WWF Terrestrial Ecoregions (Olson et al. 2001), via material da disciplina | Dado público |
| Fronteiras internacionais | ESRI World Countries, via material da disciplina | Dado público |
| Variáveis climáticas | WorldClim v2.1 (10 min de arco), via material da disciplina | Recortadas para M |
| Cobertura da terra (Formação Florestal) | MapBiomas Brasil, Coleção 11 (2025, Landsat 30m), download público oficial | CC BY 4.0 |

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

## Publicar o dashboard (Railway)

O repositório já está pronto para deploy no [Railway](https://railway.app) — inclui `Procfile` e
`.python-version`. Não há nenhum arquivo `.env` nem dado sensível no projeto (sem chaves de API:
o GBIF é consultado via API pública, sem autenticação).

Passo a passo:
1. Em [railway.app](https://railway.app), **New Project → Deploy from GitHub repo** e selecione
   `leoaaragao/uiracu-2.0` (login com sua conta GitHub).
2. O Railway detecta o `Procfile` automaticamente e builda com Nixpacks — nenhuma configuração
   extra é necessária.
3. Em **Settings → Networking**, clique em **Generate Domain** para obter a URL pública
   (`algo.up.railway.app`).
4. Pronto — o app sobe direto do repositório público; não precisa subir nenhum arquivo à parte.

**Nota sobre dados grandes:** os rasters brutos do WorldClim e do MapBiomas (centenas de MB) ficam
fora do git (`.gitignore`) porque são reobteníveis pela fonte documentada acima — o dashboard **não
depende deles em tempo de execução**, só dos resultados já processados (`Resultados/`, `Dados/*.csv`,
`.gpkg`), que são pequenos e estão versionados. O deploy funciona sem eles.

## Estrutura

```
Uiracu-2.0/
├── Dados/               # dados brutos e derivados (grandes ficam fora do git — ver .gitignore)
├── Scripts/             # pipeline em Python, numerado por etapa
├── Dashboard/           # app Streamlit multi-página (Inicio.py + pages/)
├── Resultados/          # saidas de modelo, mapas
├── Evidencias/          # capturas de tela do processo (auditoria/reprodutibilidade)
├── Referencias/         # material de apoio curado (checklist de primatas, cruzamentos, nomes/fotos)
├── ROTEIRO_DO_PROJETO.md   # registro cronológico de decisões e uso de IA
├── Procfile              # comando de start para deploy (Railway/Nixpacks)
├── .python-version       # versao do Python para o build de deploy
└── requirements.txt
```

## Uso de IA e ferramentas

Este projeto (Uiraçu 2.0) foi desenvolvido com apoio de IA generativa (Claude/Anthropic), sob supervisão humana em cada decisão científica, conforme os Protocolos 01 e 02 da disciplina. O protótipo anterior, Uiraçu 1.0 — cuja interface e conceito de painel foram reaproveitados aqui —, foi desenvolvido com apoio do Google Antigravity. Todos os dados de ocorrência vêm diretamente das APIs do GBIF (`occurrence/search` e `occurrence/download`), sem intermediários. Detalhes completos, decisão por decisão, em [`ROTEIRO_DO_PROJETO.md`](ROTEIRO_DO_PROJETO.md).

## Autor

Leonardo Andrade Aragão — Doutorando, ENBT/JBRJ. Orientador: Prof. Dr. Carlos Eduardo de Viveiros Grelle.
