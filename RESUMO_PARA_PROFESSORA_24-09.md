# Resumo do projeto Uiraçu 2.0 — para levar para a aula de 24/09

Espécie: *Lagothrix lagothricha* (macaco-barrigudo-cinza, subespécie *cana* predominante na região) · Área: UCs federais da Amazônia Ocidental

## O que já foi feito, ponto a ponto

1. **Ambiente Python** montado (geopandas, rasterio, pygbif, scikit-learn, streamlit).
2. **Unidades de Conservação**: reaproveitei um shapefile do CNUC (MMA/ICMBio) de um projeto pessoal anterior. Filtrei para UCs federais ativas em AM/AC/RO/RR → **92 UCs**.
3. **Auditoria taxonômica**: "*Lagothrix cana*" é sinônimo no GBIF — o nome aceito é *Lagothrix lagothricha cana*, subespécie. Decidi buscar no nível de **espécie** (não subespécie), porque ~40% dos registros brasileiros só têm identificação até espécie — restringir demais descartaria dado válido.
4. **1ª coleta GBIF** (só Brasil): 139 registros, com DOI oficial (`10.15468/dl.pxqmwc`).
5. **Auditoria em 7 camadas** desses 139 registros: encontrei um padrão de coordenadas institucionais do ICMBio/SISBio (endereço da sede repetido em vez do local real de observação) e 1 espécime de zoológico — ambos corretamente excluídos. Resultado: **85 registros utilizáveis** em AM/AC/RO/RR.
6. **Roraima excluída** do recorte de UCs (92 → **85 UCs**): não por falta de dado, mas porque o Rio Negro/Rio Branco é um limite de distribuição documentado para a espécie (Roraima fica do outro lado, Escudo das Guianas). Coincide com o que você ensinou: limites naturais, não políticos.
7. **Rarefação espacial** (thinning 50 km, técnica que você ensinou na aula com a castanheira): 85 → **37 registros**, removendo aglomerações perto de cidades ("efeito museu").
8. **Publiquei o projeto no GitHub** (com uma trapalhada de conta no meio do caminho, corrigida — [github.com/leoaaragao/uiracu-2.0](https://github.com/leoaaragao/uiracu-2.0)).

## A dúvida que ficou — e onde parei

Depois da aula, entendi que a área M não deveria parar exatamente na fronteira do Brasil (você foi clara: "limites naturais, não políticos"). Então fiz uma **2ª coleta no GBIF, sem filtro de país**, para ver o que apareceria.

**O que encontrei:** a subespécie *cana* (a nossa) só aparece no Brasil nos dados do GBIF. No Peru, quem aparece é *tschudii* e *poeppigii* — subespécies diferentes. Na Colômbia/Equador, é a subespécie nominotípica e *lugens* — populações claramente separadas por outra barreira biogeográfica (região do alto Amazonas/Napo).

**A pergunta que não consegui responder sozinho:**

> Para calibrar o modelo (definir M), eu devo:
> - **(a)** Usar só os registros do Brasil (só *cana*) — mais "puro" taxonomicamente, mas é a mesma fronteira política que você disse para não usar;
> - **(b)** Incluir também o Peru (*tschudii*/*poeppigii*, subespécies vizinhas) — dá mais contraste ambiental para o modelo aprender, mas mistura subespécies diferentes;
> - **(c)** Incluir tudo (também Colômbia/Equador) — parece claramente errado, seria repetir o erro que você apontou na castanheira (misturar Mata Atlântica com Caatinga), só que com populações de outro lado de outra barreira.

Cheguei a testar a opção (b), mas fiquei em dúvida se está certo teoricamente — se a`M` deve ser definida pela espécie inteira, só pela subespécie, ou por uma lógica de ecorregião que ainda nem apliquei (a próxima ficha). **Por isso parei aqui para perguntar a você amanhã.**

## Segunda dúvida: o limiar de rarefação (50 km) sempre vale?

Pensando no thinning de 50 km que apliquei (item 7 acima), me ocorreu um contraexemplo: o **sauim-de-coleira** (*Saguinus bicolor*), endêmico de uma área de só **~7.500 km²** (partes de Manaus, Rio Preto da Eva e Itacoatiara), sobrevivendo até em fragmentos de mata **dentro da cidade de Manaus**.

Se eu aplicasse o mesmo raio de 50 km num levantamento dessa espécie, o filtro provavelmente colapsaria quase todos os registros em 1-2 pontos — porque a distribuição inteira dela cabe num raio pequeno. Nesse caso, "pontos concentrados perto da cidade" não seria viés de coleta (efeito museu) — seria o **sinal ecológico real**, já que a espécie genuinamente só existe ali.

**Minha dúvida:** o limiar de rarefação precisa ser proporcional ao tamanho da distribuição conhecida da espécie (não um valor fixo tipo "sempre 50 km")? Para o nosso macaco-barrigudo, que tem distribuição ampla (centenas de milhares de km² pela Amazônia), 50 km parece razoável — mas eu gostaria de confirmar esse raciocínio com a senhora, e entender se existe uma regra prática (ex.: limiar como fração da área de distribuição/extensão de ocorrência) ou se isso é sempre uma decisão caso a caso.

## Trabalho técnico (não executado, aguardando decisão)
Preparei o código para as três opções, mas **não rodei o passo de definição de M nem baixei o WorldClim** com nenhuma delas — está tudo pausado nesse ponto até a orientação de amanhã. Nada foi perdido nem sobrescrito de forma irreversível (histórico completo no Git).

## Aprendizados da aula de 22-23/09 já aplicados (para referência rápida)
- Rarefação espacial (thinning) ✅ aplicada
- Validação cruzada (K-fold) em vez de tabuleiro de xadrez — a aplicar na modelagem
- Área M por ecorregião/bacia hidrográfica, não por limite político — em andamento (é exatamente esta dúvida)
- PCA das variáveis bioclimáticas — a aplicar
- Regras de ouro (não esconder incerteza, não mascarar extrapolação, etc.) — guia para todas as próximas etapas

---
*Detalhe técnico completo, comando por comando: [`DIARIO_DE_BORDO.md`](DIARIO_DE_BORDO.md)*
