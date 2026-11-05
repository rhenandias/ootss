# Catálogo de áudio

O mapa oferece falas nas fases e audiologs independentes, com reprodução individual,
sequência, pausa e transcrições nos 11 idiomas disponíveis no jogo: inglês,
português brasileiro, alemão, espanhol, francês, italiano, japonês, coreano,
russo, chinês simplificado e chinês tradicional. Os controles, marcadores,
popups, busca e filtros seguem a interface existente. A mídia só é carregada ao tocar.

## Cobertura

A geração atual examina 936 fases distintas (946 entradas) e disponibiliza áudio
em 236 delas (246 marcadores). Exporta 76 audiologs distintos, 79 posições de
audiologs e 41 gatilhos/âncoras, com 1.412 gravações compartilhadas em aproximadamente
164 MB de MP3 mono a 96 kbps. Os oito mapas são overworld, sky, underworld, intro,
minimap, minimap_high, minimap_low e stones. Nem todo mapa contém um audiolog;
os dois minimapas adicionais não têm âncoras de áudio próprias nas fontes atuais.

A configuração em `data/map_config.json` é compartilhada pela página e pelo gerador.
Cada ponto conserva o arquivo de entidades de origem, suas coordenadas e os mapas
compatíveis. Assim, a introdução e `skipping_stones` usam seus próprios espaços
locais, e os dois audiologs em Z=89 aparecem no minimapa de fast travel.
Os manifestos também incluem níveis que não estão expostos pelo mapa.

As fontes são o `levels.package`, o schema do executável correspondente, os WAVs
extraídos e os TXT originais de legendas. A seleção de fases é automática e não
requer editar `pilot.json`, cadastrar nomes de fases ou inventar títulos de conversas.

## Gerar e atualizar

Requisitos de geração: Python 3 e FFmpeg com `libmp3lame`. O site continua estático,
sem dependências de Python, Node ou FFmpeg para o visitante.

Primeiro atualize a extração a partir da instalação do jogo. Neste workspace, o
extrator incremental existente preserva as versões anteriores em `revisoes/`:

```sh
python3 ../reverse-order/extrair.py --tipos audio legendas textos --idiomas todos
```

Depois regenere o catálogo:

```sh
python3 scripts/export_audio_catalog.py \
  --extracted-root '/mnt/c/Users/rhena/OneDrive/Documentos/reverse-order/extraidos' \
  --package '/mnt/c/Program Files (x86)/Steam/steamapps/common/Order of the Sinking Star/data/levels.package' \
  --subtitles-dir '/mnt/c/Program Files (x86)/Steam/steamapps/common/Order of the Sinking Star/data/strings/subtitles' \
  --ffmpeg /caminho/para/ffmpeg
```

FFmpeg pode estar no `PATH`; nesse caso, omita `--ffmpeg`. Por padrão, o schema é
lido do `sinking_star.exe` ao lado da pasta `data`, sem escrever na instalação.
`--schema /caminho/schema.json` reutiliza um schema previamente extraído para a
mesma versão do jogo. `--output-root` seleciona outro destino e `--workers` controla
as conversões simultâneas (padrão: 4).

`--subtitles-dir` lê diretamente os arquivos `.subtitles` em UTF-8 da instalação,
sem conversão prévia nem escrita na pasta do jogo. Todos os idiomas encontrados
são incluídos automaticamente no catálogo e no seletor. Sem essa opção, são
descobertos os idiomas disponíveis nos `.subtitles.txt` da extração; extrações
antigas podem conter somente inglês e português. O inglês é obrigatório porque
define os identificadores das gravações. Os códigos originais `s-cn` e `t-cn`
são preservados nos dados e apresentados como 简体中文 e 繁體中文 no seletor.

Para conferir as fontes e a cobertura sem alterar o site ou converter mídia:

```sh
python3 scripts/build_audio_catalog.py \
  --extracted-root /caminho/extraidos \
  --package /caminho/data/levels.package \
  --inspect-only
```

`build_audio_catalog.py` é o gerador usado pelo comando principal. O comando antigo
`discover_audio_logs.py` continua disponível: sem publicação, grava apenas
`data/audio/inspection.json`; com `--publish-with-ffmpeg`, chama o gerador completo.

## Associação e ordem

O leitor usa os nomes e versões dos campos do jogo, incluindo falas iniciais e de
vitória, checkpoints, placas, barcos, gatilhos, cutscenes e `Voice_Log`. Marcadores e
personagens nomeados também podem servir como âncoras de diálogo. Namespaces de
história e variantes condicionais são registrados com a evidência da associação.
Não são usadas distâncias para atribuir um audiolog a uma fase.

Dentro de uma conversa, a sequência segue as legendas inglesas e respeita chamadas
explícitas `! arquivo`. Os números dos WAVs são uma conferência auxiliar: há
reinícios, lacunas e inserções como `1a`, e referências explícitas podem chamar `4`
antes de `3`. Variantes inseridas não deslocam os números dos arquivos seguintes.

Entre conversas, a lista segue a posição dos blocos no TXT original. Essa é uma
ordem estável de apresentação; as condições de encontro e ramificações do jogo
não são simuladas. Os IDs originais e a proveniência permanecem nos manifestos.

Quando idiomas têm segmentações diferentes, não se associa a fala pelo índice de
um cue. Se não for possível alinhar os clipes, o painel apresenta a transcrição da
conversa inteira com o título **Conversation transcript**. Sem tradução na fonte,
o painel informa a indisponibilidade do texto; a reprodução inglesa continua normal.

## Saídas

| Arquivo ou pasta | Conteúdo |
| --- | --- |
| `data/audio/catalog.json` | Índices `levels`, `logs` e `triggers` usados pela interface |
| `data/audio/levels/*.json` | Conversas, clipes e proveniência de cada nível |
| `data/audio/logs/*.json` | Gravações independentes do mundo |
| `data/audio/voice_logs.geojson` | Posições por arquivo de entidades, grupos e mapas compatíveis |
| `data/audio/audio_triggers.geojson` | Gatilhos e âncoras por mapa com posição, tipo e evidência |
| `data/audio/triggers/*.json` | Conversas reproduzíveis por gatilho |
| `data/audio/placement_audit.json` | Acesso pelo mapa por bloco, exclusões e áudios sem posição |
| `audio/clips/*.mp3` | Mídia compartilhada por identificador original |
| `data/audio/archive.json` | Todos os 588 blocos de legenda, incluindo os sem associação estruturada identificada |
| `data/audio/report.json` | Cobertura, fontes sem legenda, silêncio, mídia ausente e diferenças entre traduções |
| `data/audio/generated.json` | Propriedade e hashes dos arquivos gerados; cache das conversões |

Oito trechos da Priestess são reticências sem arquivo de voz. Permanecem nos
metadados como silêncio e não geram botões de reprodução com links quebrados.
Uma fala do epílogo, `coda_5__queen`, não tem WAV extraído nem WEM na instalação
atual; o relatório a identifica e preserva as demais falas dessa conversa. Referências
antigas do jogo sem legenda ou gravação correspondente também ficam no relatório.

A geração valida as fontes e prepara as conversões antes de atualizar o catálogo.
Hashes do WAV de origem e do MP3 publicado permitem reutilizar gravações intactas.
Arquivos obsoletos são removidos somente dentro do conjunto de saídas registradas;
um arquivo obsoleto editado interrompe a publicação para preservar a alteração.
A migração dos WAVs e MP3s do piloto mantém cópias recuperáveis em
`.git/audio-catalog-backups/`. Os arquivos extraídos do jogo permanecem intactos.

`data/audio/pilot.json` continua como configuração de regressão. Usar
`--config data/audio/pilot.json` seleciona explicitamente o recorte antigo, substituindo
apenas o índice de fases por esse recorte; a geração normal deve omitir `--config`.

## Verificação

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s scripts -p 'test_*audio_catalog.py'
node --check js/audio_catalog.js
python3 -m http.server 8765 --bind 127.0.0.1
```

Os testes cobrem referências estruturadas, variantes, timelines, silêncio,
traduções, integridade do cache e preservação de saídas alteradas. A verificação
funcional em Chromium também cobriu fases de diferentes regiões, listas longas,
reutilização de uma mesma gravação na sequência, parada ao fechar o popup,
carregamento sob demanda e o audiolog recuperado após atualizar a extração.
Na ampliação dos idiomas, também foram verificadas em Chromium as 11 opções
e seus textos em uma fase, um audiolog e um gatilho, incluindo a troca de idioma
durante a reprodução sem interromper o áudio. A validação dos manifestos confere
os idiomas em todas as conversas e clipes e preserva os textos ingleses e portugueses.

## Gatilhos e revisão de posições

A camada **Audio logs & triggers** reúne os audiologs dourados e os novos pontos:
pegadas verdes para movimento, balão roxo para fala de personagem e raio laranja
para âncora de roteiro. Todos têm reprodução e transcrições nos popups, busca,
links diretos e filtro de altura. A reprodução começa por ação do visitante.

Um volume de movimento exige `Marker.script_name` igual a `bark`,
`bark_conditional` ou `bark_on_id`, `is_point_marker=false` e três dimensões
positivas em `box_extents`. O ponto usa a posição original do volume no mapa do seu arquivo de entidades. Referências
condicionais podem disponibilizar mais de uma conversa no mesmo popup; não
simulamos as condições do jogo. `bark_flags`, script, dimensões, referência original
e IDs das entidades ficam no GeoJSON. A identificação decorre dos dados do jogo;
os gatilhos não foram reproduzidos durante uma sessão de gameplay.

A âncora `coda` tem referência nominal e coordenadas globais verificadas, mas sua
condição de ativação não foi determinada. Essa limitação permanece documentada nos metadados. Ela não
recebe ícone de movimento. Uma das suas falas continua sem mídia (`coda_5__queen`).

O relatório `placement_audit.json` considera um bloco posicionado quando existe
acesso a ele por uma fase presente no mapa ou por uma âncora global exibível.
Coordenadas locais são exibidas somente em mapas que usam o mesmo arquivo de
entidades. Restam 23 blocos sem posição identificável nos dados: 20 sem referência
estruturada e três com associação geral por namespace, sem âncora própria.
O relatório também lista WAVs ingleses não consumidos pelas legendas, para revisão.
A revisão da extração e a relação dos pontos estão em [AUDIO_PLACEMENT_REVIEW.md](AUDIO_PLACEMENT_REVIEW.md).

## Filtrar fases com diálogo

No controle de camadas, **Only levels with dialogue (246)** restringe os
marcadores e a busca às fases com áudio registrado (236 nomes distintos). A escolha permanece salva
no navegador. Desativar o filtro restaura as demais fases; as camadas de
regiões, audiologs e gatilhos mantêm seus controles independentes. As contagens
das camadas acompanham o filtro. Um pequeno balão no canto do marcador
identifica fases com diálogo, preservando a cor e o símbolo principal.

## Integração do original em 05/11/2026

A branch `integrate/upstream-maps-audio-2026-11-05` incorpora `upstream/main`
em `b4b7d0d`. A `main` foi salva com as alterações locais em `4632377` e também
preservada em `backup/main-before-upstream-2026-11-05`.
O histórico reescrito do original é ligado por um commit de integração com os dois
pais; as atualizações foram comparadas com a versão anteriormente integrada.
O player, os 11 idiomas, filtros, controles de fases e busca nas legendas foram
mantidos. Os tiles e as imagens usam o repositório `joric/ootss_tileset`, como no
original atualizado; a mídia de áudio continua neste projeto.

A extração atualizou uma gravação, reconvertida em MP3; as outras 1.411 foram
verificadas e reutilizadas. O conversor de legendas de `reverse-order` foi corrigido
para os cabeçalhos de um, dois e três dois-pontos e validado nos 11 idiomas.
O backup do conversor foi mantido no mesmo diretório.

A revisão detalhada, os novos pontos e as limitações estão em
[AUDIO_PLACEMENT_REVIEW.md](AUDIO_PLACEMENT_REVIEW.md) e no registro
[data/audio/upstream_update.json](data/audio/upstream_update.json).
