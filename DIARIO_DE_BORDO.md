# Diário de bordo — Uiraçu 2.0

Projeto da disciplina *Análise espacial da biodiversidade, mudanças globais e inteligência artificial* (ENBT/JBRJ, 2026-2), piloto reprodutível da Etapa 2 (SDM) do projeto de doutorado (IPBB).

**Espécie foco:** *Lagothrix lagothricha* (macaco-barrigudo-cinza; subespécie predominante na região: *L. l. cana*)
**Área:** Unidades de Conservação federais do Amazonas, Acre, Rondônia e Roraima
**Autor:** Leonardo Andrade Aragão

Este arquivo é o registro cronológico de decisões, comandos executados e papel da IA em cada etapa — é a base para a Declaração de Uso de IA do projeto final e para a apresentação em slides.

## Ferramentas de IA utilizadas no projeto (linhagem completa)

O Uiraçu 2.0 não começa do zero: reaproveita dados e conceito de um protótipo anterior (Uiraçu 1.0), feito com outra ferramenta de IA. Registro as duas, com verificação humana em cada etapa, conforme Protocolo 01/02 da disciplina.

| Ferramenta | Empresa | Onde foi usada | Finalidade |
|---|---|---|---|
| **Antigravity** (IDE com assistência de IA) | Google | Uiraçu 1.0 (`Aluno/Uiraçu - Biodiversity Bonus/`), projeto pessoal anterior, fora desta disciplina | Construção do protótipo React/Vite/Tailwind original: componentes de UI, lógica de cálculo do IPBB (sliders de peso) e organização do shapefile de UCs (`ucs.zip`) que reaproveitei aqui |
| **Claude** (Claude Code, via VS Code) | Anthropic | Todo o Uiraçu 2.0 (este repositório): ambiente Python, filtro de UCs, auditoria taxonômica, coleta GBIF, documentação, versionamento e publicação no GitHub | Assistente de programação e análise, com decisões científicas e cliques finais sempre meus |
| **GitHub** (+ Git Credential Manager) | Microsoft/GitHub | Publicação e versionamento do código-fonte | Não é uma ferramenta de IA generativa — registrado aqui por transparência do fluxo de trabalho completo, não por exigência da Declaração de Uso de IA |

Se eu vier a usar GitHub Copilot ativamente para gerar código neste repositório, essa entrada será adicionada aqui também, com a mesma transparência.

---

## 2026-09-23 — Etapa 1: Ambiente, dados de UC e pergunta ecológica

### 1. Configuração do ambiente
- Criado ambiente virtual Python (`.venv`) dedicado ao projeto, isolado do resto do sistema.
- Instalado: `geopandas`, `rasterio`, `pygbif`, `scikit-learn`, `streamlit`, `folium`, `plotly`, `pandas`, `openpyxl`.
- **Papel da IA:** a IA testou a compatibilidade dos pacotes geoespaciais com a versão do Python instalada (3.14, recém-lançada) antes de eu perder tempo tentando manualmente. Resultado: 100% compatível.

### 2. Unidades de Conservação — reaproveitamento de um projeto anterior
- Reaproveitei o arquivo `ucs.zip` do meu projeto pessoal anterior (Uiraçu - Biodiversity Bonus), que continha o shapefile completo do **CNUC** (Cadastro Nacional de Unidades de Conservação, MMA/ICMBio): 3.214 UCs do Brasil.
- **Decisão humana:** usar esse dado já em mãos em vez de buscar novamente no ICMBio, após a IA confirmar que os campos (`esfera`, `uf`, `categoria`, `situacao`) eram suficientes para o filtro que eu precisava.
- Filtrado para UCs **federais**, **ativas**, que tocam **AM, AC, RO ou RR** → **92 Unidades de Conservação**.
- **Papel da IA:** a IA escreveu o script de filtro (`Scripts/01_filtrar_ucs_federais.py`), identificou os campos corretos no schema do shapefile e rodou a verificação. Eu revisei a lista de 92 UCs resultante e confirmei que fazia sentido (nomes reconhecíveis: Parna do Jaú, Resex Chico Mendes, Flona do Jamari, etc.).
- Saída: `Dados/ucs_federais_amazonia_ocidental.gpkg` + `.csv`.

### 3. Auditoria taxonômica (antes de baixar qualquer ocorrência)
- Consultei o *backbone* taxonômico do GBIF para "Lagothrix cana": descobri que é **sinônimo**; o nome aceito é **Lagothrix lagothricha cana**, subespécie de *Lagothrix lagothricha*.
- **Decisão humana:** usar o nível de **espécie** (*L. lagothricha*, taxonKey 5786085) na busca de ocorrências, e não o de subespécie — porque a comparação de volume mostrou que ~40% dos registros brasileiros só têm identificação até espécie (perderíamos dados válidos restringindo demais). A precisão geográfica é resolvida depois, filtrando espacialmente pelos 4 estados, não pelo nome da subespécie.
- Verifiquei também o status na IUCN Red List: **Em Perigo (Endangered)**, avaliação de 2021, queda populacional de ~50% em 45 anos.
- **Papel da IA:** a IA consultou a API pública do GBIF (`species/match`, `species/{key}/synonyms`) e fez uma busca na web para confirmar o status IUCN com fonte (Wikipedia citando a avaliação oficial). Eu decidi qual nível taxonômico usar, com base nos números que a IA levantou — a IA não decidiu sozinha.
- Scripts: `Scripts/02_verificar_taxonomia_gbif.py`, `Scripts/03_checar_volume_registros.py`.

### 4. Pergunta ecológica (Ficha 01, Bloco A)
- Rascunho da pergunta elaborado com apoio da IA, a partir do template da Ficha 01 da disciplina, incorporando os achados acima (incerteza taxonômica de subespécie, defasagem temporal ocorrências×clima).
- **Decisão humana:** revisei e validei a pergunta antes de prosseguir.

### 5. Coleta de dados de ocorrência (GBIF) — dupla via
- **Via script (pygbif/API):** 139 registros (Brasil, com coordenada, taxonKey 5786085) baixados via `Scripts/04_baixar_ocorrencias_pygbif.py` → `Dados/FO01_02_ocorrencias_originais_pygbif.csv`. Reprodutível, mas sem DOI direto.
- **Via download oficial gbif.org (com DOI citável):**
  - Filtros: Scientific name = *Lagothrix lagothricha*; Country = Brazil; Has coordinate = Yes; Has geospatial issues = Either (não pré-filtrado — auditoria fica para depois, em código); Occurrence status = Present.
  - Formato: Darwin Core Archive; Taxonomia: **GBIF Backbone Taxonomy** (trocado do padrão "Catalogue of Life" para ficar consistente com a auditoria taxonômica feita acima).
  - Extensões incluídas: **Multimedia** (47 registros com foto/vídeo/áudio) — para usar no dashboard.
  - **Citação oficial:** GBIF.org (23 September 2026) GBIF Occurrence Download `https://doi.org/10.15468/dl.pxqmwc`
- **Papel da IA:** a IA me guiou filtro a filtro na interface do gbif.org (evitando erros como deixar a taxonomia em COL, que ficaria inconsistente com a auditoria), explicou a diferença entre as extensões disponíveis e por que "Multimedia" era a certa para fotos (não "Audiovisual", que é um padrão mais raro). Todas as decisões de filtro e o clique final de confirmação foram meus.

### 6. Conferência cruzada
- O download oficial trouxe **139 ocorrências** — número idêntico ao da coleta via `pygbif`. As duas vias (API e download oficial) concordam, o que dá confiança de que o filtro foi aplicado de forma consistente nos dois casos.
- O arquivo trouxe também **107 itens de mídia** (fotos/áudio/vídeo) ligados a 47 registros, com licenças variadas (CC0, CC-BY, CC-BY-NC) registradas em `rights.txt` — a checar individualmente antes de exibir cada foto no dashboard (crédito obrigatório nas CC-BY/CC-BY-NC).
- Arquivo original preservado intacto em `Dados/FO01_02_ocorrencias_originais_gbif_oficial_DOI-10.15468-dl.pxqmwc.zip`; conteúdo extraído (não editado) em `Dados/gbif_oficial_extraido/`.

### 7. Evidências
- Prints do processo de download no gbif.org salvos em `Evidencias/` (filtros aplicados, escolha de taxonomia, tela final com o DOI) — servem tanto como prova de reprodutibilidade quanto como material para a apresentação final.

### 7b. Publicação no GitHub — erros de conta (registrado por transparência)
Publicar o repositório não saiu certo de primeira, e isso fica registrado porque também é parte do processo real:

1. **Primeiro erro:** criei o repositório em `github.com/leonardoaragaobemol/uiracu-2.0` sem perceber que essa é minha conta de trabalho (Bemol), não a pessoal. O `git push` falhou (`403 Permission denied to leoaaragao`) porque o navegador estava autenticado com a conta pessoal (`leoaaragao`), que não tinha permissão nesse repositório.
2. **Tentativa de correção:** limpamos a credencial salva (`git credential-manager erase`) para forçar um novo login — o erro se repetiu, porque o navegador já estava com sessão ativa em `leoaaragao` e o GitHub não perguntou qual conta usar.
3. **Diagnóstico e decisão final:** identifiquei que `leonardoaragaobemol` era a conta errada para este projeto (trabalho ≠ acadêmico/pessoal) e decidi migrar tudo para `leoaaragao`. Apaguei o repositório vazio na conta errada (nada foi perdido — o push nunca tinha completado) e criei um novo em `github.com/leoaaragao/uiracu-2.0`.
4. **Resultado:** publicado com sucesso na conta certa. Ver commits em [github.com/leoaaragao/uiracu-2.0](https://github.com/leoaaragao/uiracu-2.0).

**Lição:** ao trabalhar em máquina com múltiplas contas Google/GitHub logadas (pessoal + trabalho), sempre confirmar qual sessão está ativa no navegador *antes* de criar o repositório, não depois.

---

## 2026-09-23 — Etapa 2: Auditoria dos registros (Ficha 01, Bloco C)

### 8. Auditoria em 7 camadas
Script `Scripts/05_auditoria_ocorrencias.py`, aplicado aos 139 registros do download oficial. Cada registro recebeu uma decisão (MANTER / MANTER_COM_RESSALVA / REVISAR / EXCLUIR) com justificativa registrada — nada foi excluído silenciosamente.

**Achado principal:** só 62% dos registros (86/139) estão de fato em AM, AC, RO ou RR segundo a geocodificação do GBIF. O resto se distribui por todo o Brasil, incluindo estados fora da distribuição conhecida da espécie (São Paulo, Bahia, Rio de Janeiro, Pernambuco, Santa Catarina, Espírito Santo, Distrito Federal).

**Padrão identificado (Prática 1 do programa: "a IA encontrou um padrão — ele é ecológico?"):** boa parte desses registros fora do lugar vêm do dataset ICMBio/SISBio e compartilham **coordenadas idênticas entre registros de datas diferentes**, batendo exatamente com o centro de capitais (Brasília, São Paulo, Rio, Salvador). Conclusão: não é o animal que está lá — é o endereço da instituição que registrou a autorização de pesquisa no sistema, usado como coordenada de plantão. Regra criada para sinalizar esse padrão especificamente (coordenada repetida + fora da Amazônia plausível), em vez de simplesmente descartar tudo que caía fora dos 4 estados.

Também encontrado: 1 espécime do Espírito Santo com localidade "Zoo Park da Montanha" e observação de campo "nascido em cativeiro" — corretamente sinalizado para exclusão (busca textual na localidade/observações, não só no campo estruturado `establishmentMeans`, que estava vazio nesse registro).

**Decisão humana:** 1 registro na fronteira Brasil/Peru ("Loreto" segundo a geocodificação, mas com localidade descrita como "ilha no rio Amazonas, a montante de Benjamin Constant/AM") foi avaliado manualmente e mantido com ressalva — é uma ambiguidade de fronteira, não um erro.

**Depuração:** durante a construção do script, uma verificação de cativeiro por texto não estava funcionando — `pandas.Series.astype(str)` não converteu corretamente valores ausentes em colunas totalmente vazias (comportamento inesperado no pandas 3.0.6, versão recém-lançada). Diagnosticado testando célula por célula até isolar a coluna problemática; corrigido trocando `.astype(str)` por `.fillna("")`. Fica registrado como lição: sempre testar a regra em um caso conhecido antes de confiar no resultado agregado — exatamente o que o Protocolo 02 pede ("comparar ao menos um resultado com cálculo independente ou expectativa ecológica").

### 9. Resultado final da auditoria

| Decisão | N | % |
|---|---|---|
| MANTER | 33 | 23,7% |
| MANTER_COM_RESSALVA | 87 | 62,6% |
| REVISAR | 8 | 5,8% |
| EXCLUIR | 11 | 7,9% |

**Registros utilizáveis dentro da área de estudo (AM/AC/RO/RR): 85**
- Amazonas: 61 · Rondônia: 22 · Acre: 2 · **Roraima: 0**

**Limitação a carregar adiante:** Roraima não tem nenhuma ocorrência nos dados coletados. Qualquer resultado do modelo para as UCs de Roraima será **extrapolação**, não interpolação — precisa aparecer explicitamente no mapa de incerteza final (Ponto de Parada 6 da Ficha 2.1).

Saídas: `Dados/FO01_04_log_auditoria.csv` (log completo por registro), `Dados/FO01_03_ocorrencias_auditadas.csv` (base + decisão), `Dados/FO01_05_sintese_auditoria.md`.

---

## 2026-09-23 — Etapa 3: Por que Roraima ficou de fora

### Pergunta que motivou isso
Depois da auditoria, notamos que nenhum dos 139 registros do GBIF caiu em Roraima. Antes de simplesmente aceitar isso, verificamos: é falta de dado (viés de amostragem) ou a espécie realmente não ocorre lá?

### O que descobrimos
O **Rio Negro é um limite de distribuição documentado** para *Lagothrix lagothricha*: a literatura (Handbook of the Mammals of the World, via Zenodo) descreve a espécie ocorrendo a oeste/norte do Rio Negro, alcançando o alto Rio Negro até a fronteira com a Venezuela. Roraima fica do **outro lado** dessa fronteira natural — é drenada pelo Rio Branco, um afluente do Negro, numa região geológica diferente (Escudo das Guianas, floresta de transição Negro-Branco), com uma fauna de primatas historicamente distinta da porção sul/oeste da Amazônia onde nossa espécie (e a subespécie *cana* em particular) se concentra.

Isso bate com o que a professora ensinou na aula de hoje: **"seres vivos obedecem a limites naturais, não políticos"** — a área acessível (M) de uma espécie deve ser definida por hipótese biogeográfica (rios, ecorregiões, relevo), nunca por fronteira de estado. E também conecta diretamente com a fundamentação teórica do seu próprio projeto de doutorado, que já cita Nelson (1992): grandes calhas fluviais isolam centros de endemismo e criam padrões descontínuos de diversidade na Amazônia — o Rio Negro é um exemplo-livro-texto disso.

### Diferença importante entre duas afirmações
- ❌ "Não achamos dados em Roraima, então tiramos" (decisão estatística/preguiçosa)
- ✅ "Roraima provavelmente fica fora da área biogeograficamente acessível a essa espécie, e a ausência de registros é consistente com essa hipótese" (decisão ecológica, com fonte)

A segunda é cientificamente defensável; a primeira não seria (confundiria ausência de amostragem com ausência real — exatamente o erro que a Ficha 01 pede para nunca cometer).

### Decisão e ação
Removidas as UCs cuja `uf` é exclusivamente Roraima (7 das 9 que tocavam o estado; 2 que também tocam o Amazonas foram mantidas). **92 → 85 Unidades de Conservação** na área de estudo (Amazonas, Acre, Rondônia).

**Ressalva registrada:** este corte foi feito por estado (proxy administrativo), por simplicidade nesta etapa. O corte definitivo da área acessível M (próxima ficha) será feito por ecorregião/bacia hidrográfica, não por limite político — pode refinar ainda mais essa lista (inclusive as 2 UCs Amazonas/Roraima remanescentes podem ter só uma fração relevante, a ser verificada com o polígono de M).

**Script atualizado:** `Scripts/01_filtrar_ucs_federais.py` (comentário no cabeçalho documenta o motivo).

---

## 2026-09-23 — Aprendizados da aula de hoje (Modelagem, remoto) aplicáveis ao projeto

A aula do dia (estudo de caso da castanheira/*Bertholletia excelsa* e de *Brosimum glaziovii*, com a professora Marinez) trouxe orientações diretamente reaproveitáveis aqui. Registrando para aplicar nos próximos passos:

1. **Rarefação espacial (thinning)** — antes de modelar, remover registros muito próximos entre si (ex.: 50 km) para reduzir o "efeito museu" (excesso de pontos perto de cidades/herbários). A turma reduziu 4.512 registros de castanheira para 151 dessa forma. **Vamos aplicar isso aos nossos 85 registros antes da modelagem.**
2. **Área M por ecorregião, nunca por limite político** — usar união de ecorregiões que tocam os pontos de ocorrência (hipótese ampla) como primeira tentativa; testar interseção estrita só se o modelo não conseguir distinguir bem as áreas. Rios/bacias hidrográficas (ANA, nível 2) quando funcionam como barreira — é exatamente o caso do Rio Negro para nós.
3. **Validação cruzada (K-fold)**, não tabuleiro de xadrez nem só bootstrap — mais robusta com poucos pontos, recomendação explícita da professora "para o contexto brasileiro".
4. **Resolução climática**: 10 minutos de arco quando os dados não passaram por auditoria muito rigorosa (nosso caso, com 85 pontos) — resoluções mais finas podem inserir erro artificial.
5. **PCA das 19 variáveis bioclimáticas** em vez de escolher variáveis manualmente — usar os eixos que somam >90% da variância, respeitando a regra prática de ~10 pontos por dimensão do modelo.
6. **Maxent não deve ser balanceado 50/50** manualmente — ele compara presença contra todo o background, diferente de GLM/Random Forest.
7. **Cuidado com "ausências verdadeiras"** de campo (locais onde a espécie já existiu mas foi extinta localmente) — podem confundir o modelo; melhor deixar pseudo-ausências aleatórias no M, a menos que a ausência real esteja muito bem documentada.
8. **Threshold de binarização**: otimizar sensibilidade + especificidade; justificar a escolha na redação (ex.: 0,7 para orçamento restrito de conservação).
9. **Mapa de incerteza é obrigatório junto do mapa de consenso** (desvio padrão entre algoritmos) — nunca esconder a discordância. Desvio padrão alto não significa modelo errado, significa um alerta real que deve aparecer no produto final.
10. **Nunca misturar cenários climáticos futuros distintos** (ex. otimista SSP1-2.6 com pessimista SSP5-8.5); ao apresentar para tomador de decisão, mostrar o pior cenário.
11. **Pós-processamento com MapBiomas (classe 3, formação florestal) + Unidades de Conservação** dá mais segurança para projeções futuras do que só o mapa climático — UC tem menor chance de deixar de existir até o fim do século do que um fragmento florestal fora dela. É exatamente a etapa final do nosso pipeline (cruzar adequabilidade × as 85 UCs).
12. **Níveis hierárquicos do resultado** (a professora foi clara sobre isso): Nível 1 = dado bruto; Nível 2 = modelagem; **Nível 3 = distribuição potencial dentro de M (nosso alvo realista)**; Nível 4 = distribuição realizada (precisa de dados de interação/barreira que não temos); Nível 5 = resposta demográfica. **Vamos comunicar o resultado como Nível 3, sem prometer mais que isso.**
13. **Regras de ouro (checklist para todo o resto do projeto):**
    - Não converter "sem dado" em zero
    - Não igualar pseudo-ausência a ausência ecológica real
    - Nunca interpretar adequabilidade como probabilidade absoluta de presença
    - Não ocultar a discordância entre algoritmos
    - Não mascarar áreas de extrapolação

---

## 2026-09-23 — Etapa 4: Rarefação espacial

Aplicado o thinning de 50 km ensinado na aula (`Scripts/07_rarefacao_espacial.py`): para cada par de pontos mais próximo que 50 km, mantido apenas um (priorizando o de menor incerteza de coordenada; entre incertezas desconhecidas, sorteio com semente fixa para reprodutibilidade).

**85 → 37 registros** (56% removidos por proximidade excessiva — sinal de quanto o "efeito museu" estava presente nos dados, especialmente no Amazonas: 61 → 28).

| Estado | Antes | Depois |
|---|---|---|
| Amazonas | 61 | 28 |
| Rondônia | 22 | 8 |
| Acre | 2 | 1 |

**Limitação a carregar adiante:** Acre ficou com apenas 1 ponto após a rarefação — qualquer resultado para as UCs do Acre terá pouquíssimo suporte direto de dados (soma-se à limitação já registrada de Roraima).

Saída: `Dados/FO01_06_ocorrencias_rarefeitas.csv`.

### Pendência em aberto: escopo geográfico de M
Discutido: a área de calibração (M) deveria, a rigor, seguir a biologia da subespécie *cana*, que também ocorre no Peru e na Bolívia — não faz sentido cortar M exatamente na fronteira política do Brasil. Os dados atuais (37 pontos) são só do Brasil (`country=BR` no filtro original do GBIF). Decisão de buscar ou não ocorrências do Peru/Bolívia para enriquecer M fica para a próxima etapa (ficha da área acessível). Já está definido, independentemente disso, que o **dashboard final será recortado nas 85 UCs federais brasileiras** — a distinção "M ecológico x recorte político no pós-processamento" é a mesma que a professora ensinou na aula.

---

## 2026-09-23 — Etapa 5: Segunda coleta GBIF, sem filtro de país (em andamento)

### Motivo
A área de calibração (M) deve seguir a biologia, não a fronteira do Brasil (ver Etapa 4, "pendência em aberto"). A subespécie *cana* também ocorre no Peru e na Bolívia. Decidido buscar ocorrências desses países também, para ter uma base mais completa na hora de desenhar M.

### Filtros usados (mesmos de antes, tirando o país)
- Scientific name: *Lagothrix lagothricha* (espécie — mesma opção 1 de sempre, taxonKey 5786085)
- ~~Country: Brazil~~ **removido**
- Has coordinate: Yes
- Occurrence status: Present
- Has geospatial issues: Either
- Taxonomic reference: **GBIF Backbone Taxonomy** (não Catalogue of Life — mesma correção de antes, para manter consistência com a auditoria taxonômica)
- Extensões: Multimedia

**Erro evitado por repetição de checklist:** ao reabrir o fluxo de download, a taxonomia voltava a aparecer como "Catalogue of Life" por padrão (é o default do GBIF) — reconferido e trocado de novo para GBIF Backbone Taxonomy antes de continuar. Vale de lição: o GBIF não lembra a escolha anterior a cada novo download, então essa checagem precisa ser feita **toda vez**.

**Resultado:** 2.631 registros (mundo todo, sem filtro de país). DOI oficial: `https://doi.org/10.15468/dl.r8eynx`. **Faltou o filtro "Occurrence status: Present"** desta vez (o GBIF não reaplica escolhas anteriores) — adicionada checagem automática no script de auditoria para pegar isso (camada 1).

**Nota de processo:** o arquivo do primeiro download (só Brasil, DOI `dl.pxqmwc`) foi removido da pasta de trabalho a pedido meu, para não conviver com o novo. Continua recuperável pelo histórico do Git a qualquer momento, se precisar.

### Diagnóstico: a base mundial trouxe outra subespécie junto
Antes de usar os 2.631 registros direto, cruzei país × subespécie (`infraspecificEpithet`):

| País | *cana* | *poeppigii* | *tschudii* | nominotípica | *lugens* | sem subespécie |
|---|---|---|---|---|---|---|
| Brasil | **48** | 5 | 0 | 2 | 0 | 84 |
| Colômbia | 0 | 2 | 0 | 124 | 49 | 876 |
| Equador | 0 | 184 | 0 | 140 | 0 | 602 |
| Peru | **0** | 108 | **158** | 7 | 0 | 227 |

**Achado:** a subespécie *cana* só aparece no Brasil. Colômbia/Equador são dominados pela nominotípica e por *lugens* — população separada por outra barreira biogeográfica (alto Amazonas/Napo), o mesmo tipo de caso que a Roraima (Etapa 3). Peru é um meio-termo: geograficamente próximo, mas taxonomicamente é outra subespécie (*tschudii*/*poeppigii*), não *cana*.

Testei filtrar para Brasil + Peru (`Scripts/09_filtrar_brasil_peru.py` → 639 registros; script de auditoria `05` atualizado para lidar com departamentos peruanos) e rodei a auditoria: **599 registros utilizáveis no total (120 BR + 479 PE)**, com os mesmos **85 registros brasileiros de sempre** dentro da área de estudo do projeto (número idêntico ao da Etapa 2 — bom sinal de consistência).

### ⏸️ PAUSADO — decisão pendente para 24/09/2026
Cheguei numa pergunta que não tenho segurança para decidir sozinho: **a área de calibração M deve usar só Brasil (só *cana*), Brasil+Peru (mistura *cana* com *tschudii*/*poeppigii*), ou existe uma terceira abordagem mais correta (ex.: delimitar por ecorregião e deixar a biologia decidir naturalmente quais pontos entram)?**

Decisão: **parar aqui e perguntar à professora na aula de amanhã**, em vez de seguir com uma escolha que eu mesmo tenho dúvida se está certa. Resumo específico para essa conversa em [`RESUMO_PARA_PROFESSORA_24-09.md`](RESUMO_PARA_PROFESSORA_24-09.md).

**Nada foi executado além da auditoria/diagnóstico acima** — a rarefação, definição de M e download do WorldClim continuam pendentes até a decisão. O script de rarefação (`07`) já foi ajustado para rodar sobre o conjunto maior quando a decisão sair, mas **não foi executado**.

### Segunda dúvida levantada (mesma categoria de problema): o limiar de rarefação é sempre 50 km?
Questionamento levantado durante a conversa: a rarefação espacial (Etapa 4) não distingue "pontos próximos por viés de coleta" de "pontos próximos porque a espécie realmente só existe numa área pequena". Contraexemplo real: *Saguinus bicolor* (sauim-de-coleira) é endêmico de ~7.500 km² em torno de Manaus (partes de Manaus, Rio Preto da Eva e Itacoatiara), sobrevivendo em fragmentos de mata **dentro da própria cidade** ([Revista Amazônia](https://revistaamazonia.com.br/sauim-de-coleira-sobrevive-em-fragmentos-de-mata-dentro-de-manaus-e-se-torna-o-primata-amazonico-com-a-menor-area-de-ocorrencia-do-brasil-nn/); [FAPEAM](https://www.fapeam.am.gov.br/pesquisa-analisa-a-distribuicao-geografica-e-saude-do-sauim-de-coleira/)). Um thinning de 50 km aplicado a essa espécie colapsaria quase toda a distribuição conhecida em 1-2 pontos, apagando sinal ecológico real, não removendo viés.

**Conclusão provisória (a confirmar com a professora):** o limiar de rarefação deve ser proporcional ao tamanho da distribuição conhecida da espécie, não um valor fixo reaplicado entre casos de estudo diferentes. Para *Lagothrix lagothricha* (distribuição de centenas de milhares de km²), 50 km é uma fração pequena da extensão e parece adequado — mas isso precisa ser uma verificação explícita, não um copiar-e-colar do exemplo da castanheira. Adicionado como segunda pergunta no resumo para a aula de 24/09.

---

## 2026-09-24 — Etapa 6: Conversa com a professora (em andamento) + material de apoio

### Mapas diagnósticos gerados para a discussão
Com a professora presente na conversa, gerei dois mapas para apoiar a decisão pendente (escopo de M):
- `Scripts/10_mapa_pontos_multipais.py` → `Evidencias/mapa_ocorrencias_multipais.png`: todas as 2.631 ocorrências coloridas por país (BR/PE/CO/EC/US/PY), com fronteiras políticas da América do Sul (reaproveitadas de `Modelagem preditiva/Dados/world_country`, material da disciplina — copiado para `Dados/paises_referencia/`) e as 85 UCs de estudo. Mostra visualmente que Colômbia/Equador formam um bloco geograficamente desconectado.
- `Scripts/11_mapa_subespecies.py` → `Evidencias/mapa_ocorrencias_subespecies.png`: mesmos pontos, coloridos por subespécie (`infraspecificEpithet`). Confirma visualmente a segregação geográfica clara entre *cana* (Brasil), *poeppigii* (Peru/Equador), *tschudii* (sul do Peru) e nominotípica+*lugens* (Colômbia).

### Pergunta adicional levantada: tratar subespécies separadamente?
Discutido se a decisão de M deveria envolver um teste formal de **equivalência de nicho** entre subespécies, em vez de decisão só qualitativa/biogeográfica. Referência indicada: Warren, D.L., Glor, R.E., Turelli, M. (2008). *Environmental niche equivalency versus conservatism: quantitative approaches to niche evolution.* Evolution, 62(11), 2868–2883 (implementado no pacote `ENMTools`; ver também Broennimann et al. 2012, Global Ecology and Biogeography, para sobreposição de nicho via PCA ambiental). **Limitação registrada:** com apenas 48 pontos de *cana*, o teste pode ter pouco poder estatístico — considerado, mas não necessariamente decisivo sozinho.

### Checklist de primatas da Pan-Amazônia
A pedido, produzida uma lista curada de primatas amazônicos (134 espécies, 18 gêneros, fonte: Primate Specialist Group/IUCN e Mammal Diversity Database) — salva em [`Referencias/Primatas_Pan-Amazonia_Checklist.md`](Referencias/Primatas_Pan-Amazonia_Checklist.md). Útil para a Etapa 3 do projeto de doutorado (diversidade funcional/filogenética) e documenta que a instabilidade taxonômica encontrada em *Lagothrix* é comum a vários outros gêneros amazônicos (*Plecturocebus*, *Cheracebus*, *Leontocebus*, *Mico*).

**Decisão do escopo de M com a professora: aguardando registro do resultado da conversa.**

---

## Próximos passos (ainda não feitos)
- [x] Auditoria completa dos registros (geografia, precisão, tempo, viés amostral — camadas 3 a 7 da Ficha 01).
- [x] Excluir Roraima do recorte de estudo (motivo ecológico) — 92 → 85 UCs.
- [x] Publicar repositório no GitHub.
- [x] Rarefação espacial dos registros (thinning 50 km) — 85 → 37 (sobre a base só-Brasil; a refazer conforme decisão abaixo).
- [x] Segunda coleta GBIF sem filtro de país + diagnóstico (achado: mistura de subespécies).
- [ ] **⏸️ Decidir com a professora (24/09): escopo geográfico de M** — Brasil / Brasil+Peru / outra abordagem.
- [ ] Definir área acessível (M) por ecorregião/bacia hidrográfica (não por estado) e baixar/recortar WorldClim (10 min de arco).
- [ ] Refazer rarefação espacial sobre a base final decidida.
- [ ] PCA das variáveis bioclimáticas (eixos com >90% da variância).
- [ ] Background / pseudo-ausências aleatórias em M.
- [ ] Ajuste dos modelos (GLM, Maxent, Random Forest) com validação cruzada (K-fold).
- [ ] Mapa de consenso + mapa de incerteza (desvio padrão entre algoritmos) — nunca um sem o outro.
- [ ] Explicabilidade (importância de variáveis).
- [ ] Pós-processamento: cruzar adequabilidade × MapBiomas (classe 3) × as 85 UCs.
- [ ] Dashboard em Streamlit (mapa das 85 UCs + score + fotos das ocorrências).
- [ ] Montar apresentação em PPT a partir deste diário.

## Documentos de apoio
- [Anotações da aula (Gemini), 22-23/09/2026](https://drive.google.com/drive/folders/1RgYTo5Ki5dCN0r64YvgQBRm3Cfrw0HHj) — referenciadas na seção "Aprendizados da aula" acima.
