# Catálogo de áudios por fase — continuidade temporária

Documento de passagem para uma nova sessão do Codex. Atualizado em 2026-10-21.
Este arquivo é temporário: pode ser substituído por documentação definitiva após a implementação.

**Estado atual:** catálogo completo implementado após a validação do piloto: 219 fases do mapa com áudio, 71 audiologs do mundo, 1.412 gravações compartilhadas em MP3. A documentação definitiva está em [AUDIO_CATALOG.md](AUDIO_CATALOG.md); as seções abaixo preservam o histórico da investigação e podem descrever etapas antigas. Servidor de revisão disponível em `http://localhost:8765`. Manter tudo **sem commit e sem push**. Não descartar arquivos modificados ou não rastreados ao retomar.

## Estado e escopo autorizado

- Fork: https://github.com/rhenandias/ootss (`origin`).
- Projeto original: https://github.com/joric/ootss (`upstream`).
- Branch desta passagem: `plan/audio-catalog`.
- Base local ao criar a branch: `f70500c` (`main`).
- O PR anterior de previews de fases já foi aprovado/mesclado: o histórico local inclui `eff37fe`, merge do PR #10, e `25fba2b`, adição de imagens.
- No levantamento inicial foram feitas inspeções e análises. Um piloto foi implementado posteriormente; consultar a seção final deste documento para o estado atual.
- O usuário pediu agora uma branch e este documento para continuar em outra sessão. A implementação do site é o trabalho futuro.
- A árvore de trabalho estava limpa antes da criação desta branch.

## Objetivo e decisões do usuário

Ao abrir a visualização/popup de uma fase, apresentar também uma área ou popup com os nomes dos áudios, botões de play e transcrições em inglês e PT-BR. O usuário deve poder escolher o que ouvir e em que sequência.

Decisões confirmadas:

1. Os áudios devem estar organizados na ordem adequada da fase/conversa.
2. Não é necessário reproduzir gatilhos do jogo: início, checkpoint, conclusão, condições etc.
3. Não é necessário mostrar esses gatilhos na interface.
4. Podemos usar os dados dos gatilhos como evidência para associação/ordenação, sem implementar sua execução no site.
5. A limpeza das legendas deve ser reproduzível por script, com o mesmo resultado em execuções equivalentes.
6. Não basta ordenar WAVs alfabeticamente: a numeração costuma ser local à conversa e existem variantes.

Proposta técnica discutida, ainda não implementada: fase → conversa/evento → arquivos ordenados. Onde a ordem entre conversas não estiver explícita nos dados, manter um ajuste revisado manualmente em metadados versionados. O usuário não definiu nomes finais de arquivos, formato do catálogo, codec de publicação ou layout exato.

## Caminhos e acesso

Workspace (WSL):

```text
/mnt/c/Users/rhena/OneDrive/Documentos/ootss
```

Instalação original confirmada pelo usuário e acessada nesta sessão:

```text
Windows: C:\Program Files (x86)\Steam\steamapps\common\Order of the Sinking Star
WSL: /mnt/c/Program Files (x86)/Steam/steamapps/common/Order of the Sinking Star
Pacote de níveis: <instalação>/data/levels.package
```

Extração anterior:

```text
Raiz: /mnt/c/Users/rhena/OneDrive/Documentos/reverse-order
Saídas: /mnt/c/Users/rhena/OneDrive/Documentos/reverse-order/extraidos

Áudios:
extraidos/audio/data/sound/GeneratedSoundBanks/Windows/ExternalSources/English

Legendas:
extraidos/legendas/data/strings/subtitles/en.subtitles.txt
extraidos/legendas/data/strings/subtitles/en.subtitles.json
extraidos/legendas/data/strings/subtitles/pt-br.subtitles.txt
extraidos/legendas/data/strings/subtitles/pt-br.subtitles.json

Texturas/previews anteriores:
extraidos/texturas/data-pc

Conversor anterior:
reverse-order/conversores.py
Documentação da extração:
reverse-order/COMO-EXTRAIR.md
```

Outras fontes disponíveis: `extraidos/originais/data/strings`, `extraidos/originais/data/sound/GeneratedSoundBanks/Windows`, `extraidos/textos/data/strings`, `extraidos/resumo.json`, `extraidos/manifesto.json`, `extraidos/manifesto.sqlite3`.

Os caminhos da instalação contêm espaços: usar argumentos estruturados ou aspas adequadas. `python` não está disponível neste ambiente; `python3` está (a importação gerou bytecode de Python 3.14). Nenhuma dependência adicional foi instalada.

## Estrutura atual do site

- Site estático, sem `package.json` identificado na raiz.
- `data/markers.json`: GeoJSON com propriedades `type`, `area`, `name`; 920 nomes únicos com `type == "level"` na versão inspecionada.
- `data/regions.json`: regiões e títulos.
- `data/images.txt` e `images/levels/<nome>.webp`: previews das fases.
- `index.html`: interface do mapa, galeria e popup. A construção do conteúdo do popup fica aproximadamente nas linhas 940–949; carregamento de `data/images.txt` por volta de 1478–1487. As linhas podem mudar.
- `play.html` e `js/solution_player.js`: reprodução de soluções de puzzles; não confundir com o futuro player de áudio.
- `scripts/simp_tool.py`: leitor existente do `levels.package`, entidades e metadados do mapa.

## Inventário e vínculo áudio ↔ legenda

No diretório `ExternalSources/English`:

- 1.412 arquivos WAV.
- Tamanho total: 1.332.467.740 bytes, aproximadamente 1,33 GB decimal.
- Duração total medida pelos cabeçalhos: aproximadamente 3,76044 horas (3h46).
- Todos os WAVs foram abertos com o módulo `wave` sem erros de formato.
- 1.402 são mono e 10 são estéreo; todos PCM, 16 bits, 48 kHz.
- Não foi feita escuta integral nem validação perceptual de todos os áudios.
- Há áudio inglês; legendas PT-BR não significam que haja dublagem PT-BR neste diretório.

Todos os 1.412 WAVs puderam ser associados a pelo menos um bloco de legenda inglês:

- 1.406 pela convenção de nome: ID do bloco seguido, em geral, de `_N__personagem`, ou nome exatamente igual ao ID.
- Os seis restantes têm referências explícitas `! nome_do_audio` em comandos `=` das legendas.
- Existem sufixos como `_6a__acting` e personagens com `_alt` ou números; não usar uma regex que aceite somente inteiros e personagens sem underscore.
- Existem reutilizações explícitas de arquivos entre blocos; não presumir relação um-para-um.
- O vínculo ao bloco foi verificado; o alinhamento completo de cada trecho de texto com cada WAV ainda não foi implementado/validado.

Exceções resolvidas por referência explícita:

| WAV sem extensão | Bloco inglês |
| --- | --- |
| `all_heroes_thief_wizard_compartments` | `heroes2_thief_wizard_priestess_compartments_mid` |
| `heroes2_compartments_you__thief` | `heroes2_thief_wizard_priestess_compartments` |
| `heroes2_compartments_you__wizard` | `heroes2_thief_wizard_priestess_compartments` |
| `victory_lap_composite_you` | `heroes3_victory_lap` |
| `warrior_heroes1_start_1__warrior` | `heroes_mouse` |
| `warrior_heroes1_what_1__warrior` | `heroes_mouse` |

Foram encontrados 33 nomes distintos em referências explícitas `!` no inglês; todos existem como WAV no diretório inspecionado.

## Fase ↔ conversa: usar o pacote original

A comparação literal `audio == fase` ou `audio começa com fase + "_"` encontrou somente 14 das 920 fases. É uma heurística insuficiente; ausência desse match não prova ausência de áudio.

O `levels.package` foi lido com o formato já suportado em `scripts/simp_tool.py`:

- Tamanho: 394.537.697 bytes.
- Cabeçalho `simp`, formato Simple_Package v1.
- 2.015 entradas: 974 `.entities`, 974 `.level_manifest`, 66 `.level_set`, 1 `.asset_manifest`.
- As entidades têm cabeçalho `enty`; `parse_entities` retorna `(entity_id, type_name, diff_bytes)`.

Referências concretas encontradas:

| Arquivo/fase | Entidade/referência |
| --- | --- |
| `heroes1_1` | `Guy` aponta a `heroes_mouse`; `Marker` contém `warrior_heroes1_start_end` |
| `heroes1_5_v2` | `Guy` aponta a `heroes1_5` |
| `3d_intro_mirrors` | `Guy` com personagem `trader_alt` aponta a `3d_intro_mirrors` |
| `rotator` | `Guy` aponta a `rotator` |
| `across_the_fence_vtrader_m_p` | `Voice_Log` contém `audiolog_di_across_the_fence_vtrader_m_p` |
| `catching_up_v0` | referências a `audiolog_di_catching_up_v0` e `audiolog_di_catching_up_v0_part_2` |

Campos observados (IDs hexadecimais; interpretar/validar antes de generalizar):

- `Guy`: `0x100E`, já lido como `start_marker` pelo script, contém IDs de diálogo; o leitor também reconhece `0x1011` como `end_marker`.
- `Voice_Log`: `0x1000` contém um ID de audiolog.
- `Marker`: `0x1008` contém um ID de diálogo no exemplo `all_together_now_reassembly_1`.
- `Checkpoint`: `0x1010` contém `hp_endpoint_weapon_mid2` no exemplo inspecionado.
- `Boat`: `0x1000` e `0x1001` contêm `skipping_stones_start` e `skipping_stones_start_repeat`.
- `Overworld_Unlock`: `0x1000` contém `skipping_stones_shrine` no exemplo inspecionado.
- `Judge`: `0x1000` contém `end3_skipping_1` no exemplo inspecionado.

Não usar mera busca de strings como catálogo definitivo. IDs que coincidem com nomes de fase também aparecem em nomes de objetos, materiais e configurações. Exemplo: `Ocean_Map` tem `Ocean_Basic~end3_skipping_1`, que não demonstra uma associação de diálogo. O leitor atual usa heurísticas para pular campos desconhecidos; sua documentação alerta que um byte `0xFD` dentro de dados pode ser confundido com delimitador.

Também foram encontrados marcadores com `bark_conditional` e bases como `skipping_stones_island_west`, enquanto as legendas usam variantes mais específicas. Isso sugere referências construídas dinamicamente; a cobertura não deve depender apenas de IDs literais completos.

## Ordem e timing

Separar três questões:

1. Ordem dos WAVs dentro de uma conversa: normalmente indicada pelos nomes e sequência das legendas.
2. Vários trechos de legenda dentro de um WAV: precisam ser agrupados corretamente.
3. Ordem entre conversas de uma fase: ainda precisa de extração/validação; pode exigir ajustes manuais estáveis.

Exemplos:

- `3d_intro_mirrors`: seis WAVs numerados, personagens alternados, sequência compatível com o bloco de legenda.
- `heroes_warrior_mistrust`: seis WAVs e oito trechos falados; há mudanças de legenda dentro de um mesmo WAV.
- `rotator`: existem WAVs `_1__warrior` e `_3__warrior`; as entradas intermediárias da priestess contêm `...`. Lacunas de numeração não devem ser tratadas automaticamente como arquivos perdidos.
- `skipping_stones` tem início, repetição e variantes de quantidade de tesouros: `return_treasures_0`, `return_treasures_5`, `return_treasures_all`, entre outras. Podem ser alternativas, não uma sequência obrigatória.

Os comandos contêm tempos absolutos, tokens com `+`, valores negativos, durações e referências `!`. Inglês e PT-BR nem sempre usam a mesma forma ou os mesmos tempos. A semântica completa desses tokens não foi decodificada: preservar os dados brutos, comparar com durações reais dos WAVs e validar antes de gerar tempos absolutos ou WebVTT.

A posição de uma entidade no arquivo não foi provada como ordem narrativa. Não usar ordem de serialização, coordenadas ou ordem alfabética como prova automática da sequência entre conversas.

## Problemas das legendas JSON atuais

O conversor `reverse-order/conversores.py`, função `text_asset` (aproximadamente linhas 158–213), agrupa legendas somente quando a linha começa com `:::`. Os TXT preservam os bytes originais e são a fonte mais adequada para um novo parser.

| Idioma | Blocos no TXT (cabeçalhos `:`, `::`, `:::`) | Entradas no JSON atual |
| --- | ---: | ---: |
| Inglês | 587 | 255 |
| PT-BR | 589 | 202 |

Isso faz cabeçalhos e conversas seguintes vazarem para blocos anteriores no JSON. O parser reconhece comandos `=`, mas só remove linhas `++` do campo `text`; comandos como `+ magistrate_disappear 2` permanecem misturados à transcrição.

Distribuição dos cabeçalhos: inglês `:` 52, `::` 280, `:::` 255; PT-BR `:` 356, `::` 31, `:::` 202. Nenhum ID duplicado foi encontrado na enumeração dos cabeçalhos. Preservar o tipo de cabeçalho: seu significado completo ainda não foi investigado.

Entre idiomas:

- 586 IDs compartilhados.
- Somente inglês: `actor_credits`.
- Somente PT-BR: `audiolog_u_collider`, `audiolog_u_unfoldment_is_borrowed`, `paradise_lost_invocation_longer`.
- 85 blocos ingleses começam com `audiolog`.
- Seis blocos compartilhados têm quantidades diferentes de comandos `=`:
  `all_together_now_reassembly_1`, `audiolog_sky_laws_of_form`,
  `promesst2_baby_dragon_end`, `sp_bard_takes_wand`,
  `sp_thief_takes_wand`, `sp_warrior_takes_wand`.
- Não alinhar idiomas cegamente pelo índice da entrada ou assumir que todo bloco tem texto nos dois idiomas.

## Procedimento proposto para conversão limpa

Implementar um script separado/revisável no projeto; não alterar os arquivos extraídos como parte da geração do catálogo.

1. Ler TXT em UTF-8 com tratamento explícito de BOM e quebras de linha.
2. Reconhecer cabeçalhos `:`, `::`, `:::` e preservar ID, forma do cabeçalho e linha de origem.
3. Separar comandos `=`, personagem, timing bruto, duração quando identificável e referência `!`.
4. Separar instruções `++` e comandos de jogo `+` do texto exibível, preservando-os como metadados técnicos.
5. Preservar texto legítimo, acentos, pontuação, reticências e conteúdo entre asteriscos; não remover linhas apenas por começarem com pontuação.
6. Tratar personagem `_` como controle/fim/limpeza de legenda, preservando o cue técnico; não exibir `_` como personagem falante.
7. Gerar saída determinística, com ordenação explícita e sem timestamps variáveis embutidos.
8. Registrar estruturas desconhecidas, referências ausentes, ambiguidades, diferenças entre idiomas e lacunas de cobertura. Não descartar silenciosamente.
9. Separar transcrição limpa de dados de sincronização. Um catálogo com texto estático pode preceder legendas sincronizadas, mas a UX final ainda não foi definida.

Modelo conceitual sugerido: IDs estáveis de fase, conversa e clipe; nomes exibíveis separados dos IDs; posição explícita de cada conversa/clipe; caminhos dos áudios publicados; transcrições por idioma; proveniência para auditar o match; ajustes manuais separados da saída gerada. Os nomes/formato finais ainda são decisões de implementação.

## Artefatos da investigação e limitações

Foi gerado `/tmp/ootss-audio-level-references.json` como artefato exploratório. Contém exemplos de entidades e candidatos por ocorrência literal em tipos selecionados. Pode desaparecer entre sessões e não deve ser tratado como catálogo final.

A última versão desse levantamento encontrou candidatos em 233 arquivos de entidades, incluindo 217 nomes presentes no mapa, e 487 IDs ingleses distintos. Esses números são apenas resultados de uma busca heurística: há falsos positivos possíveis e referências dinâmicas não cobertas. Não equivalem à cobertura confirmada do catálogo.

As inspeções foram executadas por snippets de `python3`, sem criar um script persistente de auditoria. A reconstrução do levantamento deve usar o leitor existente e os critérios documentados acima. Não foi publicado PR nem feito upload de áudios nesta investigação. Um `__pycache__` criado ao importar `simp_tool` foi removido.

## Plano para a próxima sessão

1. Ler este documento, conferir branch/status e instruções locais. Revalidar fontes se mudaram.
2. Construir o parser das legendas TXT com diagnóstico de cobertura, mantendo referências e comandos técnicos fora da transcrição exibível.
3. Construir o vínculo conversa ↔ WAV, incluindo `!`, reutilizações, sufixos especiais e múltiplos cues por WAV.
4. Estender a leitura de entidades para os campos de diálogo/audiolog, usando strings estruturadas em vez de busca literal indiscriminada.
5. Produzir o catálogo fase ↔ conversas e um relatório de casos não resolvidos; investigar as referências dinâmicas.
6. Definir uma ordenação por fase verificável e ajustes manuais para casos não explícitos. Não alegar ordem original onde houver só uma escolha editorial.
7. Definir nomes exibíveis, esquema final e comportamento de variantes; manter a interface simples, sem simular gatilhos.
8. Converter os WAVs para um formato comprimido apropriado ao navegador e ao volume do site; codec/qualidade ainda não foram definidos. Carregar mídia sob demanda.
9. Integrar reprodução e seleção de idioma ao popup/visualização da fase em `index.html`, reutilizando a estrutura existente quando adequado.
10. Validar associações representativas, exceções `!`, segmentação bilíngue, ordem e reprodução no navegador. Não enviar 1,33 GB de WAVs diretamente ao repositório por padrão.

O principal ponto em aberto é a ordem entre conversas. Os arquivos necessários estão acessíveis, há vínculos concretos no pacote e não é necessário reproduzir os gatilhos no site. Ainda não foi comprovado que todas as 920 fases possuem áudio, nem que uma sequência linear única existe para todas elas.

## Piloto implementado posteriormente — alterações locais para revisão

O usuário autorizou implementar o primeiro piloto e, durante o trabalho, pediu explicitamente **não fazer commit ao final**. As alterações do piloto devem permanecer locais na branch `plan/audio-catalog`, sem commit, push ou PR até nova instrução. O documento inicial já havia sido publicado no fork antes dessa instrução.

Recorte confirmado e ordem explícita configurada:

| Fase | Conversas | WAVs |
| --- | --- | ---: |
| `heroes1_1` | `heroes_mouse` → `warrior_heroes1_start_end` | 6 |
| `heroes1_2_v2` | `warrior_heroes1_call` | 1 |
| `heroes1_3` | `heroes_warrior_gate` | 1 |
| `heroes1_4` | `heroes_warrior_mistrust` → `heroes_warrior_where_is_tif` | 7 |

Total: 15 WAVs, 6.744.522 bytes, aproximadamente 70,25 segundos. Foram mantidos em WAV para este teste pequeno; compressão permanece como trabalho futuro.

Arquivos do piloto:

- `scripts/export_audio_catalog.py`: parser dos cabeçalhos/cues e exportação limitada ao piloto. Usa apenas a biblioteca padrão de Python e o leitor de entidades existente.
- `scripts/test_audio_catalog.py`: testes de limites de blocos, referências `!`, limpeza, agrupamento e rejeição de entrada ambígua.
- `data/audio/pilot.json`: ordem dos blocos originais e contagem esperada de clipes. É a entrada mantida manualmente para o piloto; não contém títulos editoriais.
- `data/audio/catalog.json`: índice gerado de fase para arquivo de metadados.
- `data/audio/levels/<fase>.json`: conversas, clipes, transcrições por idioma, duração, proveniência, cues técnicos e hashes das fontes de legendas.
- `audio/levels/*.wav`: cópias dos 15 áudios selecionados, com os nomes originais.
- `js/audio_catalog.js` e `js/audio_catalog.css`: player e layout do popup.
- `index.html`: carrega o índice e integra o painel nas fases presentes nele.

Para regenerar:

```sh
python3 scripts/export_audio_catalog.py \
  --extracted-root '/mnt/c/Users/rhena/OneDrive/Documentos/reverse-order/extraidos' \
  --package '/mnt/c/Program Files (x86)/Steam/steamapps/common/Order of the Sinking Star/data/levels.package'
```

É possível usar `--output-root /tmp/ootss-audio-regenerated` para comparar sem sobrescrever o piloto. `--config` permite escolher uma configuração alternativa. A geração valida referências estruturadas de `Guy` e `Marker`, mídias, contagens e alinhamento entre idiomas antes de gravar saídas. Campos de outros tipos ainda não fazem parte desse exportador.

Limite deliberado do agrupamento: no recorte, uma duração explícita ou referência `!` inicia um clipe; cues seguintes sem duração e com o mesmo personagem continuam nele. Um bloco com tempos absolutos e sem novas fronteiras fica em um clipe. Essa regra foi validada para as seis conversas do piloto, **não foi provada para todas as conversas do jogo**. IDs/personagens divergentes entre idiomas, fronteiras ambíguas e contagens diferentes interrompem a geração.

A ordem entre blocos vem de `pilot.json`, não de uma inferência narrativa automática. Não há títulos editoriais. As transcrições visíveis não usam timing. As instruções de dublagem, comandos e tokens de tempo permanecem na proveniência.

Comportamento da interface:

- Desktop: thumbnail/solução à esquerda; lista de áudios e transcrição à direita.
- Mobile: painéis empilhados.
- Lista única de clipes na ordem; cada linha exibe personagem, início da fala, duração e play/pause. O ID original está no tooltip do nome.
- Selecionar o nome mostra a transcrição sem iniciar reprodução. Trocar a seleção interrompe o clipe anterior.
- Seletor `English`/`Português` troca o texto, mantendo voz inglesa; idioma permanece durante a navegação da sessão.
- Um áudio por vez; botões individuais reproduzem um clipe, e o botão global ao lado do idioma toca a fase em sequência. O botão global pausa/retoma; ao fim da sequência, volta ao estado de play. Selecionar um clipe individual sai do modo de sequência. Fechar o popup interrompe e libera a mídia.
- O primeiro texto aparece ao abrir o popup, sem baixar WAV antecipadamente.
- Arquivos por fase são carregados sob demanda; fases ausentes no catálogo mantêm o popup sem painel de áudio.

Verificações da implementação:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s scripts -p 'test_audio_catalog.py' -v
node --check js/audio_catalog.js
git -c core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol diff --check
python3 -m http.server 8765 --bind 127.0.0.1
```

Os quatro testes Python passaram. A regeneração em diretório separado produziu os mesmos bytes dos 20 arquivos gerados (índice, quatro JSONs de fase e 15 WAVs). `index.html` mantém CRLF, como no arquivo original; a opção `cr-at-eol` evita reportar CRLF como espaço excedente.

O ambiente de teste de navegador foi instalado apenas em `/tmp/ootss-browser-check` (Playwright), com navegador em `~/.cache/ms-playwright`. Não foi adicionado `package.json` nem dependência Node ao projeto. O script temporário de verificação está em `/tmp/ootss-browser-check/check.cjs`; esses arquivos temporários não são garantidos em outra sessão.

A verificação Chromium passou para as quatro fases: contagens de 6/1/1/7 clipes; ausência de downloads WAV antes de play; reprodução, pausa, troca de clipe e seleção de texto; idioma preservado ao mudar de fase; interrupção de todos os objetos Audio ao fechar; painéis empilhados e largura dentro de 390 px no mobile; popup sem áudio para `heroes1_5_v2`; ausência de erros JavaScript. Para reduzir tráfego, o teste interceptou previews de outras fases, preservando as quatro imagens do piloto. Não representa uma nova validação de toda a galeria ou de todos os navegadores.

Capturas temporárias: `/tmp/ootss-audio-desktop.png` e `/tmp/ootss-audio-mobile.png`. O popup usa um nó DOM como conteúdo para que o reposicionamento do Leaflet após a carga assíncrona preserve os botões e seus listeners. A altura e o padding de autopan reservam espaço para os controles do mapa em telas pequenas.

Para revisão local, abrir `http://localhost:8765/` com o servidor acima e selecionar uma das quatro fases (ou usar a busca do mapa). Toda mídia e todo metadado do piloto estão locais no repositório; não houve upload nem alteração na branch remota durante a implementação.

### Ajuste de interface após a revisão do piloto

O usuário pediu reprodução global em sequência e um aumento moderado do popup. O botão global usa o mesmo objeto Audio dos clipes individuais, avança pelo catálogo no evento `ended` e atualiza a transcrição. Uma sequência nova começa no primeiro clipe; pausa global preserva o ponto atual. O popup de áudio passou de 700 para 800 px de largura (limitado à viewport), a coluna da imagem de 360 para 380 px, a lista de 225 para 260 px e o limite da transcrição de 170 para 240 px. Há altura mínima de 440 px no layout desktop; no mobile permanece empilhado e com altura limitada à tela. Mudanças continuam locais, sem commit ou push.

Validação adicional passou em Chromium com `/tmp/ootss-browser-check/check-sequence.cjs`: início global, pausa/retomada, avanço real no evento `ended` pelos sete clipes de `heroes1_4` (com seek ao fim para acelerar), término, reinício no primeiro clipe e saída do modo de sequência ao tocar um clipe individual. As verificações anteriores de idioma, fechamento e layout desktop/mobile também passaram.

### Simplificação: remover títulos editoriais

O usuário pediu remover os cabeçalhos inventados (Mistrust, The mouse etc.) e manter apenas os áudios ordenados, evitando dependências editoriais na geração automática. A interface agora renderiza uma lista única. Os títulos foram removidos da configuração, do exportador e dos manifestos regenerados. Os blocos originais de legenda permanecem internamente para rastrear a fonte e agrupar cues pertencentes ao mesmo WAV; não são grupos editoriais exibidos ao usuário. O extrator geral e a descoberta automática da ordem entre blocos continuam pendentes: o piloto ainda usa a seleção/ordem explícita de `pilot.json`.

## Encerramento e prioridade da próxima sessão

O servidor local da porta 8765 foi parado a pedido do usuário. Não há commit, push ou PR das alterações de implementação. A branch remota contém somente o documento inicial; o piloto e esta documentação atualizada permanecem no workspace local.

Após remover os títulos editoriais, foram regenerados os manifestos e confirmados os mesmos 15 clipes na mesma ordem. A verificação Chromium de reprodução individual, idioma, fechamento e layout desktop/mobile passou novamente. A sequência global havia sido validada na revisão anterior; a remoção dos títulos não altera o playlist.

**Intenção para a próxima sessão:** conseguir atualizar os arquivos extraídos do jogo e executar um procedimento que gere novamente todos os manifestos automaticamente, preservando o comportamento da interface, sem cadastrar títulos ou grupos editoriais.

Trabalho ainda necessário para isso:

1. Conferir o estado local e ler o exportador atual. Ele já regenera o recorte de quatro fases, mas a seleção e a ordem de blocos ainda dependem de `data/audio/pilot.json`.
2. Descobrir automaticamente as referências de áudio/legenda nas entidades de todas as fases do mapa, incluindo `Voice_Log`, checkpoints e outros tipos, com leitura estruturada dos campos. A busca literal exploratória anterior não basta para afirmar cobertura.
3. Tratar referências dinâmicas/variantes e reutilização de WAVs. Diferenciar fase sem áudio, referência não resolvida e fonte incompleta no relatório de geração.
4. Generalizar o agrupamento de cues por WAV, especialmente tempos absolutos, relativos, negativos e diferenças de segmentação entre idiomas. Não reutilizar cegamente a regra limitada do piloto.
5. Resolver a ordem entre blocos por evidência dos dados. Identificar casos sem ordem inequívoca em vez de apresentar ordenação alfabética/serialização como sequência original. Gatilhos não precisam aparecer nem ser simulados na interface.
6. Gerar índice e manifestos estáveis sem nomes editoriais e sem configuração manual por fase como requisito normal. Usar ajustes explícitos somente se houver casos realmente não inferíveis, registrando-os no relatório.
7. Definir regeneração segura: validar antes de publicar as saídas, remover arquivos gerados obsoletos apenas dentro do escopo controlado do gerador, manter entradas/configurações intactas e verificar duas execuções com resultados idênticos.
8. Considerar compressão da mídia antes de ampliar de 15 WAVs para o corpus completo de aproximadamente 1,33 GB. Codec e qualidade ainda não foram escolhidos.

O esquema atual consumido pela interface é `catalog.levels[fase] → JSON da fase`, com `conversations[].clips[]` achatado em uma lista única pelo player. Os blocos internos representam IDs originais das legendas e sua proveniência, não agrupamentos editoriais. É possível gerar esse esquema automaticamente; qualquer mudança no esquema exige atualizar gerador e consumidor juntos.

Para retomar a revisão visual, iniciar novamente `python3 -m http.server 8765 --bind 127.0.0.1` na raiz do projeto. A autorização para fazer commit continua pendente: não commitar nem publicar até o usuário solicitar.


## Atualização de 21/10/2026: posições e audiologs independentes

O projeto original foi integrado por merge. A API atual de `simp_tool.py` devolve
`(id, tipo, diff, versão)` e decodifica `name`/`value` a partir do schema do executável.
O exportador do piloto foi adaptado para usar campos nomeados e versionados
(`initial_bark`, `win_bark`, `string_parameter`, `Voice_Log.name`, `Checkpoint.story`),
sem depender dos antigos números de campo. `--schema` aceita JSON ou executável;
sem essa opção, usa o executável ao lado de `data/`, sem gravar cache na instalação.

A pasta extraída contém legendas/áudio de 13/10; o pacote instalado foi atualizado em
17/10. As associações são validadas contra ambas as fontes; atualizar o jogo não
atualiza automaticamente a pasta `extraidos`.

### Descoberta e posicionamento

Novo comando `scripts/discover_audio_logs.py`, independente de `pilot.json`:

- Encontradas **104 entidades Voice_Log**, referentes a **101 blocos** distintos.
- **71 entidades em overworld.entities** e **33 em arquivos de fases**.
- As coordenadas das 33 entidades locais não podem ser usadas diretamente no mapa
  principal. Não há associação automática à fase mais próxima.
- **68 posições globais** sem pendências de decodificação/grupo foram disponibilizadas.
  Três entidades globais têm `group_id` e aguardam validação da transformação do grupo:
  `psalm_139_part_2`, `audiolog_g_musing_on_fast_travel`, `audiolog_g_substrate`.
- **100 blocos** passaram pela validação das associações inglesas; um permanece
  pendente: `audiolog_sky_play_of_form_1a`, cujo WAV `_3__acting` não existe na pasta
  extraída. Isso pode ser fonte incompleta ou uma regra de segmentação ainda não
  resolvida; não foi substituído por outro arquivo.
- Entre as 68 posições globais exibidas, **67 gravações** foram publicadas e uma
  apresenta o estado de indisponibilidade no popup.

Saídas da descoberta: `data/audio/voice_logs.geojson` (todas as entidades, com espaço
de coordenadas, origem, grupo e flag `mapReady`) e `data/audio/discovery.json`
(resumo, hashes de legendas, clipes validados, candidatos separados, pendências).
Os GeoJSON incluem também as posições locais para investigação; a interface filtra
`mapReady`. A ordem dos IDs no inventário serve somente à estabilidade do arquivo.

### Interface e mídia

A camada **Audio logs** usa o mesmo marcador em forma de pino do mapa, com o ícone
Font Awesome de volume e cor dourada. Usa os popups, fontes, links copiáveis,
busca e controle de camadas existentes. O player do piloto é compartilhado:
reprodução individual/sequencial, pausa, idioma e transcrição; nenhuma galeria ou
preview de fase é criada para audiologs independentes. Os pontos são filtrados
pela altura ao trocar entre overworld/sky/underworld; ocultar a camada remove seus
resultados da busca e fecha o áudio aberto. O fechamento do popup interrompe a mídia.

`catalog.levels` continua atendendo às fases; `catalog.logs` atende às gravações
independentes. Regenerar o piloto preserva a seção `logs`. Arquivos de mídia/JSON
individuais só são solicitados ao abrir/tocar, com `preload=none`.

A publicação de audiologs usa MP3 mono a 96 kbps/44,1 kHz em `audio/logs/`, com
FFmpeg informado explicitamente ao comando. Os WAVs extraídos permanecem intactos.
Os manifestos em `data/audio/logs/` reutilizam `conversations[].clips[]`.
A publicação prepara as conversões em diretório temporário antes de atualizar o
catálogo; arquivos antigos que deixarem de ser referenciados não são apagados.

As traduções são alinhadas por identidade de clipe/personagem, não por número de
cue. Se essa validação falha, a gravação inglesa continua disponível, e a transcrição
PT-BR mostra indisponibilidade. As seis pendências de tradução ficam no relatório:
`actor_credits`, `audiolog_s_magistrate`, `audiolog_sky_laws_of_form`,
`audiolog_sky_play_of_form_3`, `paradise_lost_invocation_2`,
`paradise_lost_invocation_credits`.

### Política de ordem confirmada com os arquivos reais

1. **Dentro de uma conversa:** seguir a sequência de cues das legendas inglesas e
   respeitar referências explícitas `!`. A numeração dos WAVs é conferência auxiliar,
   com comparação numérica (1, 2, 10), sem ordenar lexicalmente nem exigir continuidade.
2. Inserções explícitas como `..._1a__acting` imediatamente após `..._1__acting` não
   avançam o contador dos clipes seguintes no modo Voice_Log. Timelines absolutos
   monotônicos podem ser divididos por mudança de personagem e referências explícitas;
   cada arquivo resultante precisa existir e ser um WAV válido.
3. **Entre conversas de uma fase:** ainda não há prova de ordem narrativa global.
   O piloto mantém a seleção/ordem explícita em `pilot.json`. A posição de um bloco no
   TXT, IDs de entidades e coordenadas não demonstram a ordem de encontro no jogo.
4. `clipOrdering.source=subtitle-cue-order` registra a escolha; `filenameCheck` indica
   concordância, divergência ou nomes não comparáveis. `conversationOrdering` registra
   que a ordem entre blocos do piloto ainda é configurada manualmente.

Exemplo concreto: `audiolog_s_magistrate` toca os clipes com números **4 antes de 3**,
**10 antes de 9** e **12 antes de 11**, devido às chamadas explícitas das legendas.
Ordenar globalmente pelos números produziria uma conversa diferente. Em
`audiolog_sky_play_of_form_3`, a inserção `1a` vem entre `1` e `2`.

### Regeneração

Inspeção sem copiar mídia:

```bash
python3 scripts/discover_audio_logs.py \
  --extracted-root '/mnt/c/Users/rhena/OneDrive/Documentos/reverse-order/extraidos' \
  --package '/mnt/c/Program Files (x86)/Steam/steamapps/common/Order of the Sinking Star/data/levels.package'
```

Para também gerar os manifestos e MP3s dos audiologs globais, acrescentar
`--publish-with-ffmpeg /caminho/para/ffmpeg`. O executável de FFmpeg usado nesta
sessão foi instalado apenas em `/tmp/ootss-browser-check`, junto do Playwright de
verificação; não é dependência adicionada ao repositório e pode desaparecer.
O comando do piloto continua sendo o documentado acima; `--schema` permite reutilizar
um JSON extraído do executável correspondente à versão do pacote.

Validação: 12 testes Python; regeneração do piloto preservando os mesmos 15 clipes,
transcrições, durações e ordem; checagem de sintaxe JS; Chromium com reprodução real,
pausa, idioma, parada ao fechar, popup mobile, busca por altura e camada independente.
A descoberta continua limitada a `Voice_Log`; geração automática de todos os diálogos,
barks dinâmicos e ordem entre conversas das fases permanecem pendentes.

As mudanças desta sessão continuam **sem commit e sem push**.


## Conclusão: catálogo completo autorizado após validar o piloto

O usuário validou o piloto e autorizou ampliar o recurso para todas as fases com
registros de áudio, mantendo a interface existente. A extração incremental foi
atualizada: quatro fontes foram processadas e 6.465 foram reutilizadas. Foram
recuperados o WAV ausente e a versão atual de uma gravação/legenda inglesa.

`export_audio_catalog.py` agora usa o gerador automático `build_audio_catalog.py`
por padrão. O recorte manual permanece disponível somente com `--config` explícito.
A geração usa os campos estruturados de todas as entidades relevantes, namespaces
de história, variantes condicionais e âncoras nomeadas. Os arquivos do piloto foram
migrados para mídia compartilhada, com cópias de segurança em `.git`.

A interface preserva os mesmos controles e estilos. O player passou a distinguir
ocorrências de uma mesma gravação, permitindo sequências com reutilização de WAVs.
Quando a tradução não pode ser alinhada por clipe, mostra o texto da conversa
inteira, identificado no mesmo painel. Nenhuma revisão manual adicional foi pedida.

Cobertura: 920 fases examinadas; 219 fases do mapa com áudio; 235 fontes de níveis
com manifestos; 71 audiologs globais; 69 posições cobertas pelos tiles atuais;
1.412 MP3s (aproximadamente 164 MB); oito trechos de silêncio; uma mídia realmente
ausente na instalação (`coda_5__queen`). Os demais blocos sem associação estruturada
identificada continuam preservados no arquivo completo, sem atribuição inventada.
Detalhes e comandos atualizados: [AUDIO_CATALOG.md](AUDIO_CATALOG.md).

A regeneração incremental reutilizou os 1.412 MP3s sem reconversão. Os testes Python
e a verificação em Chromium cobrem a ampliação e o avanço entre gravações
reutilizadas. O trabalho continua local, sem commit e sem push.
