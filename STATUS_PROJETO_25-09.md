# Status do projeto Uiraçu 2.0 — 25/09/2026

Disciplina: Análise espacial da biodiversidade, mudanças globais e IA (ENBT/JBRJ 2026-2) · Aluno: Leonardo Andrade Aragão · **Entrega: 02/10/2026**

Repositório público: [github.com/leoaaragao/uiracu-2.0](https://github.com/leoaaragao/uiracu-2.0)

## O projeto tem duas partes independentes

### Parte 1 — Riqueza de primatas nas UCs da Amazônia · ✅ **completa**

**Pergunta:** quais Unidades de Conservação federais têm mais espécies de primata?

- **168 espécies** de primata pan-amazônicas (todos os gêneros da região), buscadas diretamente no GBIF
- **92 UCs federais** (Amazonas, Acre, Rondônia e Roraima)
- Cruzamento **geométrico real** (ponto dentro do polígono da UC — não por país/estado declarado, que pode estar errado)
- **792 → 825 ocorrências confirmadas** dentro das UCs (68 espécies com pelo menos 1 registro)
- Dashboard interativo: mapa de riqueza por UC, ranking, exploração por espécie ou por UC, nome popular e foto de cada espécie (hover)

**Por que Roraima entra aqui:** encontramos 8 espécies próprias documentadas em UCs de Roraima (*Alouatta macconnelli*, *Ateles paniscus* etc.), distintas da fauna do resto da região — faz parte da riqueza real, não excluir.

### Parte 2 — Modelagem de distribuição (SDM) de *Lagothrix lagothricha* · 🔧 **em andamento**

**Pergunta:** onde estão as condições ambientais mais adequadas para o macaco-barrigudo-cinza?

Estudo de caso aprofundado de **1 espécie**, cumprindo o exercício de modelagem da disciplina (Fichas 2.1 a 2.9).

**Já concluído:**
1. Auditoria taxonômica (*Lagothrix cana* → sinônimo; nome aceito *L. lagothricha cana*)
2. Coleta e auditoria de ocorrências (139 → 85 registros úteis no Brasil, em 7 camadas de auditoria)
3. Rarefação espacial (thinning 50 km) → **37 pontos de calibração**
4. Área acessível (M): união de **11 ecorregiões** tocadas pelos pontos → **3.235.510 km²**, distribuídos em Brasil (75%), Peru (13%), Bolívia (7%), Colômbia (5%) — resolvido sem misturar subespécies vizinhas na calibração

**Por que Roraima fica fora aqui (diferente da Parte 1):** o Rio Negro/Rio Branco é um limite de distribuição documentado na literatura para essa espécie — não é falta de dado, é biogeografia real.

**Ainda falta:**
- Recortar variáveis climáticas (WorldClim, 10 min de arco) para a extensão de M
- Background/pseudo-ausências + PCA das variáveis
- Ajustar os modelos: **GLM, Maxent (via biblioteca `elapid` em Python), Random Forest**
- Validação cruzada (K-fold) e seleção de modelos
- Mapa de consenso + mapa de incerteza
- Pós-processamento (cruzar com MapBiomas × 85 UCs)

## Ferramentas e método

Todo o pipeline em **Python** (sem QGIS, sem R, sem software Maxent original — substituído pela biblioteca `elapid`, o que será declarado explicitamente no relatório final). Todos os dados vêm de fontes públicas rastreáveis (GBIF, WWF Ecoregions, WorldClim), com scripts numerados e reprodutíveis.

## Uso de IA

Assistência de IA (Claude/Anthropic) em todas as etapas — programação, organização de dados, auditoria assistida — com decisão científica e verificação sempre humanas, conforme Protocolos 01 e 02 da disciplina. Registro completo, decisão por decisão, em [`DIARIO_DE_BORDO.md`](DIARIO_DE_BORDO.md).

## Resumo visual

| | Parte 1 (Riqueza) | Parte 2 (SDM Lagothrix) |
|---|---|---|
| Status | ✅ Completa | 🔧 ~40% (dados/área prontos, falta modelagem) |
| UCs | 92 (com Roraima) | 85 (sem Roraima) |
| Espécies | 168 pesquisadas, 68 confirmadas | 1 (foco) |
| Produto | Dashboard interativo | Dashboard de status (modelo final pendente) |
