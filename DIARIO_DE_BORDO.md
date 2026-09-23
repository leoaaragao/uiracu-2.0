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

## Próximos passos (ainda não feitos)
- [x] Auditoria completa dos registros (geografia, precisão, tempo, viés amostral — camadas 3 a 7 da Ficha 01).
- [ ] Definir área acessível (M) e baixar/recortar WorldClim.
- [ ] Background / pseudo-ausências.
- [ ] Ajuste do(s) modelo(s) (GLM e/ou Random Forest) e validação espacial.
- [ ] Mapa de incerteza e explicabilidade (importância de variáveis).
- [ ] Dashboard em Streamlit (mapa das 92 UCs + score + fotos das ocorrências).
- [ ] Publicar repositório no GitHub.
- [ ] Montar apresentação em PPT a partir deste diário.
