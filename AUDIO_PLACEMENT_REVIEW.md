# Revisão dos áudios e posições — 21/10/2026

## Resultado no mapa

Foram acrescentados 11 pontos com evidência nos campos do pacote instalado: nove volumes de movimento, um personagem com fala inicial e uma âncora de roteiro. Os 69 pontos de audiologs existentes foram preservados. A camada **Audio logs & triggers** contém agora 80 pontos. As 219 fases com áudio continuam disponíveis, compartilhando as mesmas 1.412 gravações em MP3.

As posições abaixo são as coordenadas globais originais, em X/Y/Z. Pegadas verdes identificam movimento, balão roxo identifica fala de personagem e raio laranja identifica uma âncora de roteiro cuja ativação ainda não foi determinada.

| Diálogo | Entidade | X | Y | Z | Tipo |
| --- | --- | --- | --- | --- | --- |
| `queen_og_ask` | 59773192 | 80.000000 | 71.000000 | 0.000000 | Personagem |
| `queen_og_heroes_entry` | 63036983 | 80.051239 | 79.209145 | 0.887707 | Movimento |
| `queen_og_heroes2` | 63036984 | 78.528191 | 105.525566 | 0.887707 | Movimento |
| `end3_queen_promesst_red` | 63036985 | 27.848291 | 71.380051 | 0.704876 | Movimento |
| `queen_og_wardrobe` | 63036986 | 77.949890 | 95.771530 | 0.564272 | Movimento |
| `queen_og_first_green_beam` | 63036987 | 25.174362 | 107.503151 | 0.027601 | Movimento |
| `queen_og_first_orange_beam` | 63036988 | 11.447787 | 104.549408 | 0.027601 | Movimento |
| `queen_og_first_lily` | 63036989 | 78.986771 | 38.697834 | -0.000095 | Movimento |
| `queen_og_gold_room_first` | 63036991 | 96.051598 | 92.991760 | 0.081274 | Movimento |
| `queen_og_wardrobe_2` | 115527844 | 78.501411 | 99.942352 | 0.564272 | Movimento |
| `coda` | 115609827 | 137.000000 | 133.000000 | -21.000000 | Âncora de roteiro |

Os nove volumes têm `script_name=bark`, `is_point_marker=false`, dimensões positivas em `box_extents` e `string_parameter` que referencia diretamente o diálogo. Dois têm `bark_flags=1`, que o schema identifica como `OPTIONAL`: `queen_og_heroes2` e `queen_og_gold_room_first`. Isso não determina todas as condições narrativas. O exemplo `queen_og_gold_room_first` fica em aproximadamente **(96,05; 92,99; 0,08)** e pode ser encontrado pelo nome na busca do mapa.

A entidade `Guy` 59773192 referencia `queen_og_ask` em `initial_bark`. O marcador 115609827 tem `entity_name=coda`, correspondente ao bloco de legendas, no submundo. Não há volume de movimento nem script de ativação explícito nesse último marcador; por isso ele recebe um raio; a limitação permanece documentada nos metadados. `coda_5__queen` permanece sem WAV/WEM disponível; as demais falas podem ser reproduzidas.

Os gatilhos foram identificados nos dados, sem reprodução de uma sessão de gameplay. O mapa permite ouvir as falas manualmente e não simula as condições de ativação.

## Áudios ainda sem acesso pelo mapa

**53 blocos de diálogo, com 91 gravações**, permanecem sem entrada no mapa. A contagem considera acesso por uma fase presente no mapa, audiolog ou novo ponto de diálogo. Todas as gravações continuam preservadas no arquivo completo (`data/audio/archive.json`).

| Motivo | Blocos |
| --- | ---: |
| Referências em fases que não têm entrada no mapa atual | 28 |
| Sem referência estruturada ao bloco | 20 |
| Associação geral por namespace, sem âncora própria | 3 |
| Posição conhecida fora dos tiles atuais (interior do fast travel) | 2 |

A presença de um prefixo em comum não fornece uma posição. Em particular, não associei `audiolog_sky_play_of_form_2_surprise`, `queen_og_mirror_isles` nem `end3_mirror_isles_first` a marcadores vizinhos ou de nome parecido. O pacote só permite a associação geral desses três ao overworld pelo namespace.

As 28 referências em fases ausentes correspondem à introdução e a versões de fases de design illustrations. Coordenadas locais dessas fases não são coordenadas globais. Os dois audiologs excluídos ficam em Z=89: `audiolog_g_musing_on_fast_travel` em (57,117,89) e `audiolog_g_substrate` em (51,113,89).

### Relação completa

| Bloco | Situação | Fontes com referência específica ou namespace do próprio nível |
| --- | --- | --- |
| `heroes2_wizard_priestess_mid` | Sem referência estruturada | — |
| `heroes3_warrior_and_druid_transmutation` | Sem referência estruturada | — |
| `intro_1` | Fase ausente do mapa | `intro` |
| `intro_before_teleporter` | Fase ausente do mapa | `intro` |
| `audiolog_g_musing_on_fast_travel` | Fora dos tiles | `overworld` |
| `audiolog_g_substrate` | Fora dos tiles | `overworld` |
| `mirror_3` | Sem referência estruturada | — |
| `mirror_4` | Sem referência estruturada | — |
| `mirror_after_clones_first` | Sem referência estruturada | — |
| `mirror_icy_start` | Sem referência estruturada | — |
| `intro_queen_am_i_dead` | Fase ausente do mapa | `intro` |
| `intro_queen_callout_alt` | Fase ausente do mapa | `intro` |
| `intro_queen_foreign_script` | Fase ausente do mapa | `intro` |
| `intro_queen_sign` | Fase ausente do mapa | `intro` |
| `intro_queen_hosts_1` | Fase ausente do mapa | `intro` |
| `intro_queen_hosts_2` | Fase ausente do mapa | `intro` |
| `intro_queen_hosts_3` | Fase ausente do mapa | `intro` |
| `intro_queen_teleporter` | Fase ausente do mapa | `intro` |
| `hw_thief_wizard` | Sem referência estruturada | — |
| `sp_warrior_shunt` | Sem referência estruturada | — |
| `sp_help_drop` | Sem referência estruturada | — |
| `sp_wizard_open_beam` | Sem referência estruturada | — |
| `hp_wizard_be_aggro` | Sem referência estruturada | — |
| `vs_warrior_dragons` | Sem referência estruturada | — |
| `moment_alone` | Sem referência estruturada | — |
| `more_than_mirror_guy` | Sem referência estruturada | — |
| `vm_warrior_mirror_guy_2_end` | Sem referência estruturada | — |
| `vm_warrior_mirror_guy_3` | Sem referência estruturada | — |
| `end1_dimension_1` | Sem referência estruturada | — |
| `end1_dimension_2` | Sem referência estruturada | — |
| `end1_dimension_3` | Sem referência estruturada | — |
| `end1_dimension_4` | Sem referência estruturada | — |
| `audiolog_sky_play_of_form_2_surprise` | Namespace geral, sem âncora | — |
| `queen_og_mirror_isles` | Namespace geral, sem âncora | — |
| `audiolog_di_catching_up_v0` | Fase ausente do mapa | `catching_up_v0` |
| `audiolog_di_catching_up_v0_part_2` | Fase ausente do mapa | `catching_up_v0` |
| `audiolog_di_heroes_1_7` | Fase ausente do mapa | `heroes1_7` |
| `audiolog_di_strategic_stack` | Fase ausente do mapa | `strategic_stack` |
| `audiolog_di_torcher` | Fase ausente do mapa | `torcher` |
| `audiolog_di_quad_torch_v1` | Fase ausente do mapa | `quad_torch_v1` |
| `audiolog_di_height_chooser` | Fase ausente do mapa | `height_chooser` |
| `audiolog_di_push_down_a_lot` | Fase ausente do mapa | `push_down_a_lot` |
| `audiolog_di_across_the_fence_old` | Fase ausente do mapa | `across_the_fence_old` |
| `audiolog_di_sender` | Fase ausente do mapa | `sender` |
| `audiolog_di_sender_simplified` | Fase ausente do mapa | `sender_simplified` |
| `audiolog_di_worlds_collide_heroes_and_promesst` | Fase ausente do mapa | `worlds_collide_heroes_and_promesst` |
| `audiolog_di_worlds_collide_heroes_and_promesst_v2` | Fase ausente do mapa | `worlds_collide_heroes_and_promesst_v2` |
| `audiolog_di_worlds_collide_heroes_and_promesst_v3` | Fase ausente do mapa | `worlds_collide_heroes_and_promesst_v3` |
| `audiolog_di_lily_wearing_intro` | Fase ausente do mapa | `lily_wearing_intro` |
| `paradise_lost_invocation_credits` | Fase ausente do mapa | `intro` |
| `end3_mirror_isles_first` | Namespace geral, sem âncora | — |
| `paradise_lost_invocation_2` | Fase ausente do mapa | `intro` |
| `actor_credits` | Fase ausente do mapa | `intro` |

## Nova extração

A extração incremental de áudio, bancos, legendas e textos terminou com sucesso em aproximadamente 9min26s. Foram reutilizadas **6.474 fontes** e reprocessado **um banco alterado**, sem erros ou conversões parciais nesta rodada. A comparação usa o manifesto existente no início deste trabalho.

- Nenhuma fonte nova e nenhuma fala nova ou alterada nesta rodada. As 1.412 gravações publicadas foram verificadas e reutilizadas.
- `Music_and_ambience.bnk` mudou de 33.231.234 para 33.231.339 bytes. Os blocos BKHD e HIRC mudaram; os blocos DIDX e DATA permaneceram idênticos. As **7.380 saídas** (WEM, WAV e sequências Wwise MIDI) mantiveram os mesmos nomes e hashes. Portanto, a alteração do banco não trouxe mídia nova para converter. O processamento concluiu 3.194 decodificações WAV e preservou 496 sequências Wwise MIDI.
- A fonte `audiolog_sky_play_of_form_3_1a__acting.wem` não existe mais na instalação, mas sua cópia antiga permanece na extração por política de preservação. É o único WAV inglês sem clipe correspondente nas legendas atuais; não foi acrescentado ao mapa.
- As pendências de texturas e meshes do manifesto são anteriores e ficam fora do escopo desta extração de áudio.

Contagens, hashes anteriores/atuais e diferenças das saídas estão em [data/audio/extraction_update.json](data/audio/extraction_update.json). As versões anteriores do banco foram preservadas em `reverse-order/extraidos/revisoes/`.

## Fontes e validação

Foram revisados `AUDIO_CATALOG_PLAN.md`, os geradores existentes, `data/markers.json`, os manifestos do catálogo, o schema extraído do executável instalado e `data/levels.package`. A associação aos pontos usa campos nomeados e versionados do jogo.

- [Gatilhos e evidências](data/audio/audio_triggers.geojson).
- [Inventário de posições e pendências](data/audio/placement_audit.json).
- [Cobertura e hashes das fontes](data/audio/report.json).

Validação: 25 testes Python passaram; JavaScript do player e scripts inline passaram pela verificação de sintaxe. Em Chromium, os três tipos de ponto reproduziram áudio, exibiram transcrição PT-BR e pararam ao fechar. Busca respeitou altura e camada oculta; layout mobile ficou dentro da tela. A regressão cobriu cinco fases, sequência com gravações repetidas e audiologs existentes, sem erro JavaScript ou resposta 404 de áudio.

Não houve commit nem publicação remota.
