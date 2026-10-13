# Catálogo de áudios por fase — continuidade temporária

Documento de passagem para uma nova sessão do Codex. Data: 2026-10-13.
Este arquivo é temporário: pode ser substituído por documentação definitiva após a implementação.

## Estado e escopo autorizado

- Fork: https://github.com/rhenandias/ootss (`origin`).
- Projeto original: https://github.com/joric/ootss (`upstream`).
- Branch desta passagem: `plan/audio-catalog`.
- Base local ao criar a branch: `f70500c` (`main`).
- O PR anterior de previews de fases já foi aprovado/mesclado: o histórico local inclui `eff37fe`, merge do PR #10, e `25fba2b`, adição de imagens.
- Nesta sessão foram feitas inspeções e análises; nenhum player, conversor ou catálogo definitivo foi implementado.
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
