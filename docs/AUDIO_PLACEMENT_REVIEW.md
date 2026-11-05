# Revisão dos áudios e posições — 05/11/2026

A integração de `joric/ootss` em `b4b7d0d` preserva o catálogo do fork e acrescenta os mapas e o formato de marcadores atuais. A `main` anterior está salva em `4632377` e em `backup/main-before-upstream-2026-11-05`. As alterações ficam em `integrate/upstream-maps-audio-2026-11-05`.

## Cobertura

| Medida | Antes | Agora |
| --- | ---: | ---: |
| Fases distintas disponíveis | 920 | 936 |
| Fases com áudio | 219 | 236 |
| Audiologs distintos | 71 | 76 |
| Posições de audiologs | 69 | 79 |
| Gatilhos e âncoras | 11 | 41 |
| Volumes de movimento | 9 | 21 |
| Blocos sem posição identificada | 53 | 23 |
| Gravações em MP3 | 1412 | 1412 |

Há 946 entradas para 936 nomes de fase, pois dez fases têm entradas em mais de um mapa. As 236 fases com áudio correspondem a 246 marcadores. Nenhuma fase anteriormente disponível com áudio foi perdida.

## Mapas e coordenadas

`data/map_config.json` é a fonte comum de limites, alturas e arquivo de entidades para o gerador e a página. Os pontos da introdução e de `skipping_stones` mantêm suas coordenadas locais; não são transportados para o overworld. Os dois audiologs em Z=89 agora são acessíveis em `minimap`. `minimap_high` e `minimap_low` não têm âncoras de áudio próprias no pacote atual.

São 40 posições adicionais: 16 na introdução (oito audiologs e oito gatilhos), 22 gatilhos em stones e dois audiologs no fast travel. Os 80 pontos antigos foram preservados. Os IDs dos gatilhos de novos arquivos são qualificados pelo nome da fonte para evitar colisões.

A busca do original continua abrangendo os mapas e as legendas. A visibilidade dos marcadores é reaplicada após reconstruir o índice de busca, evitando pontos de outros mapas na camada atual. Links com `fonte:id` distinguem a mesma gravação em locais diferentes; links antigos por nome continuam reconhecidos. A camada de áudio reúne audiologs e gatilhos, com reprodução sob demanda, sequência, transcrição e filtros.

## Novas posições acessíveis

X/Y/Z são os valores originais do arquivo de entidades indicado pelo mapa. Os nomes e a proveniência completos estão nos GeoJSONs.

| Mapa | Áudio ou âncora | ID | X / Y / Z |
| --- | --- | ---: | --- |
| intro | `intro_queen_callout_alt` | 62914933 | 45.016 / -5.524 / 0.001 |
| intro | `intro_queen_foreign_script` | 62914934 | 45.041 / 3.942 / 0.001 |
| intro | `intro_queen_am_i_dead` | 62914935 | 45.016 / -16.592 / 0.001 |
| intro | `intro_queen_hosts_1` | 62914936 | 52.367 / 24.948 / 0 |
| intro | `intro_queen_hosts_2` | 62914937 | 57.299 / 26.996 / 0 |
| intro | `intro_queen_teleporter` | 62914938 | 45.004 / 47.041 / 0.499 |
| intro | `intro_1` | 106954775 | 49 / 2 / 0 |
| intro | `intro_before_teleporter` | 106954776 | 45 / 31 / 0 |
| intro | `intro_queen_sign` | 111149186 | 47 / 10 / 0 |
| intro | `paradise_lost_invocation_2` | 115344136 | 45 / 38 / 0 |
| intro | `paradise_lost_invocation_credits` | 115345265 | 59 / 0 / 2 |
| intro | `audiolog_sky_10000_things` | 115345347 | 3 / 26 / 1 |
| intro | `audiolog_sky_laws_of_form` | 115345348 | 6 / 26 / 1 |
| intro | `audiolog_u_computation` | 115345448 | 82 / 26 / 1 |
| intro | `intro_queen_hosts_3` | 115345634 | 47.081 / 30.457 / 0 |
| intro | `actor_credits` | 115345817 | 11 / 2 / 2 |
| minimap | `audiolog_g_musing_on_fast_travel` | 115515423 | 57 / 117 / 89 |
| minimap | `audiolog_g_substrate` | 115515424 | 51 / 113 / 89 |
| stones | `ssnew_interdiction_first` | 1048877 | 48 / 65 / 0 |
| stones | `audio_trigger_1048951` | 1048951 | 26 / 64 / 0 |
| stones | `ssnew_pre_map` | 1048959 | 36 / 64 / 0 |
| stones | `ssnew_traps` | 1049133 | 52 / 60 / 0 |
| stones | `ssnew_what_do_i_do` | 1049981 | 45 / 45 / 0 |
| stones | `ssnew_no_traps` | 1049990 | 68 / 46 / 0 |
| stones | `ssnew_tacking` | 1050680 | 9 / 34 / 0 |
| stones | `ssnew_interdictions_secret_2` | 1050721 | 62 / 33 / 0 |
| stones | `ssnew_good_place` | 1051533 | 44 / 21 / 0 |
| stones | `ssnew_good_place_2` | 1051618 | 53 / 20 / 0 |
| stones | `skipping_stones_shrine` | 58720274 | 22 / 38 / 0 |
| stones | `ssnew_interdictions_secret` | 94371848 | 73 / 36 / 0 |
| stones | `ssnew_built_in_1` | 94371865 | 14 / 34 / 0 |
| stones | `ssnew_weather` | 94371881 | 51 / 31 / 0 |
| stones | `ssnew_built_in_3` | 95420792 | 52 / 14 / 0 |
| stones | `skipping_stones_gold_room_impending` | 115343364 | 39.056 / 30.822 / 0 |
| stones | `skipping_stones_whirlpool` | 115343365 | 21.462 / 17.473 / 0 |
| stones | `skipping_stones_approaching_impeller` | 115343369 | 34 / 2.485 / 0 |
| stones | `skipping_stones_approaching_impeller` | 115343373 | 26 / 1 / 0 |
| stones | `audio_trigger_115343381` | 115343381 | 22.942 / 55.478 / 0 |
| stones | `ssnew_built_in_2` | 115343415 | 7 / 21 / 0 |
| stones | `ssnew_please_disable_interdict` | 135266342 | 27.143 / 10.478 / -0.005 |

## Fases acrescentadas à cobertura de áudio

`across_the_fence_old`, `catching_up_v0`, `end2_mirror1`, `end2_mirror_4_islands_v2`, `height_chooser`, `heroes1_7`, `lily_wearing_intro`, `make_shoreline`, `push_down_a_lot`, `quad_torch_v1`, `sender`, `sender_simplified`, `strategic_stack`, `torcher`, `worlds_collide_heroes_and_promesst`, `worlds_collide_heroes_and_promesst_v2`, `worlds_collide_heroes_and_promesst_v3`.

## Extração atualizada

A primeira rodada incremental reutilizou 6.475 fontes e processou 23: 22 concluídas e uma legenda pendente. A gravação `audiolog_sky_play_of_form_3_1__acting.wem` mudou e seu MP3 foi reconvertido; os outros 1.411 MP3s foram validados e reutilizados. As revisões anteriores ficam em `reverse-order/extraidos/revisoes/`.

A pendência era o chinês simplificado, cujo arquivo usa cabeçalhos com um dois-pontos. O conversor antigo só reconhecia três. Corrigi `reverse-order/conversores.py` para aceitar os três formatos, incrementei a versão do conversor e reextraí todos os idiomas. Os 11 concluíram sem pendências. A validação comparou todos os blocos com o parser do catálogo e confirmou preservação byte a byte dos TXT. O backup é `reverse-order/conversores.py.before-upstream-2026-11-05.bak`.

O site usa as legendas originais da instalação via `--subtitles-dir`, com 588 blocos ingleses. A cópia antiga de `audiolog_sky_play_of_form_3_1a__acting.wav` continua preservada na extração e não é usada pelo catálogo atual.

## Limitações das fontes

Restam 23 blocos, com 61 gravações, sem posição identificável: 20 não têm referência estruturada e três só têm associação geral por namespace. Estão preservados em `archive.json`. Não há evidência de posição para movê-los a uma fase ou ponto específico.

| Bloco | Motivo |
| --- | --- |
| `heroes2_wizard_priestess_mid` | Sem referência estruturada |
| `heroes3_warrior_and_druid_transmutation` | Sem referência estruturada |
| `mirror_3` | Sem referência estruturada |
| `mirror_4` | Sem referência estruturada |
| `mirror_after_clones_first` | Sem referência estruturada |
| `mirror_icy_start` | Sem referência estruturada |
| `hw_thief_wizard` | Sem referência estruturada |
| `sp_warrior_shunt` | Sem referência estruturada |
| `sp_help_drop` | Sem referência estruturada |
| `sp_wizard_open_beam` | Sem referência estruturada |
| `hp_wizard_be_aggro` | Sem referência estruturada |
| `vs_warrior_dragons` | Sem referência estruturada |
| `moment_alone` | Sem referência estruturada |
| `more_than_mirror_guy` | Sem referência estruturada |
| `vm_warrior_mirror_guy_2_end` | Sem referência estruturada |
| `vm_warrior_mirror_guy_3` | Sem referência estruturada |
| `end1_dimension_1` | Sem referência estruturada |
| `end1_dimension_2` | Sem referência estruturada |
| `end1_dimension_3` | Sem referência estruturada |
| `end1_dimension_4` | Sem referência estruturada |
| `audiolog_sky_play_of_form_2_surprise` | Namespace sem âncora própria |
| `queen_og_mirror_isles` | Namespace sem âncora própria |
| `end3_mirror_isles_first` | Namespace sem âncora própria |

`coda_5__queen` continua sem WAV/WEM na instalação atual. As oito falas de reticências da Priestess são silêncio. Os gatilhos são identificados nos dados; suas condições de ativação não foram reproduzidas em gameplay.

## Validação

- 29 testes Python passaram, incluindo separação dos espaços de coordenadas e cobertura dos minimapas.
- Sintaxe do player e do JavaScript da página verificada com Node.
- Todos os 1.772 arquivos gerados tiveram seus hashes conferidos, incluindo 1.412 MP3s; manifestos conferidos nos 11 idiomas.
- As coordenadas das âncoras presentes no arquivo de marcadores coincidem exatamente com o original.
- Chromium: reprodução na introdução, stones, minimapa e overworld; legendas PT-BR; sequência em uma fase; parada ao fechar e trocar de mapa; filtro 246/946 entradas; links para fonte e entidade; popup a 390 pixels. Sem erros JavaScript ou HTTP de áudio.

Os hashes das fontes, os novos pontos, a mídia alterada e o resumo da extração ficam em [data/audio/upstream_update.json](../data/audio/upstream_update.json). O histórico da extração de outubro continua em [data/audio/extraction_update.json](../data/audio/extraction_update.json).

A integração foi preparada localmente; não houve push nem publicação do site.
