# Catálogo de áudio

O mapa oferece falas nas fases e audiologs independentes, com reprodução individual,
sequência, pausa e transcrições em inglês e português. Os controles, marcadores,
popups, busca e filtros seguem a interface existente. A mídia só é carregada ao tocar.

## Cobertura

A geração atual examina as 920 fases do mapa e disponibiliza áudio em 219 delas.
Também exporta 71 audiologs do mundo e 1.412 gravações distintas, em aproximadamente
164 MB de MP3 mono a 96 kbps. Arquivos reutilizados entre fases são compartilhados.
Há 69 posições de audiologs nas três camadas do mapa; duas gravações ficam no
interior de fast travel, fora dos tiles atuais, e permanecem no catálogo e no arquivo
completo. Além disso, 11 pontos de diálogo do overworld agora aparecem no mapa:
nove volumes de movimento, um personagem e uma âncora de roteiro no submundo. Os manifestos também incluem níveis que não estão expostos pelo mapa.

As fontes são o `levels.package`, o schema do executável correspondente, os WAVs
extraídos e os TXT originais de legendas. A seleção de fases é automática e não
requer editar `pilot.json`, cadastrar nomes de fases ou inventar títulos de conversas.

## Gerar e atualizar

Requisitos de geração: Python 3 e FFmpeg com `libmp3lame`. O site continua estático,
sem dependências de Python, Node ou FFmpeg para o visitante.

Primeiro atualize a extração a partir da instalação do jogo. Neste workspace, o
extrator incremental existente preserva as versões anteriores em `revisoes/`:

```sh
python3 ../reverse-order/extrair.py --tipos audio legendas textos
```

Depois regenere o catálogo:

```sh
python3 scripts/export_audio_catalog.py \
  --extracted-root '/mnt/c/Users/rhena/OneDrive/Documentos/reverse-order/extraidos' \
  --package '/mnt/c/Program Files (x86)/Steam/steamapps/common/Order of the Sinking Star/data/levels.package' \
  --ffmpeg /caminho/para/ffmpeg
```

FFmpeg pode estar no `PATH`; nesse caso, omita `--ffmpeg`. Por padrão, o schema é
lido do `sinking_star.exe` ao lado da pasta `data`, sem escrever na instalação.
`--schema /caminho/schema.json` reutiliza um schema previamente extraído para a
mesma versão do jogo. `--output-root` seleciona outro destino e `--workers` controla
as conversões simultâneas (padrão: 4).

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
| `data/audio/voice_logs.geojson` | Posições globais, grupos e cobertura dos tiles |
| `data/audio/audio_triggers.geojson` | Gatilhos e âncoras globais com posição, tipo e evidência |
| `data/audio/triggers/*.json` | Conversas reproduzíveis por gatilho |
| `data/audio/placement_audit.json` | Acesso pelo mapa por bloco, exclusões e áudios sem posição |
| `audio/clips/*.mp3` | Mídia compartilhada por identificador original |
| `data/audio/archive.json` | Todos os 587 blocos de legenda, incluindo os sem associação estruturada identificada |
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

## Gatilhos e revisão de posições

A camada **Audio logs & triggers** reúne os audiologs dourados e os novos pontos:
pegadas verdes para movimento, balão roxo para fala de personagem e raio laranja
para âncora de roteiro. Todos têm reprodução e transcrições nos popups, busca,
links diretos e filtro de altura. A reprodução começa por ação do visitante.

Um volume de movimento exige `Marker.script_name` igual a `bark`,
`bark_conditional` ou `bark_on_id`, `is_point_marker=false` e três dimensões
positivas em `box_extents`. O ponto usa a posição original do volume. Referências
condicionais podem disponibilizar mais de uma conversa no mesmo popup; não
simulamos as condições do jogo. `bark_flags`, script, dimensões, referência original
e IDs das entidades ficam no GeoJSON. A identificação decorre dos dados do jogo;
os gatilhos não foram reproduzidos durante uma sessão de gameplay.

A âncora `coda` tem referência nominal e coordenadas globais verificadas, mas sua
condição de ativação não foi determinada. Essa limitação permanece documentada nos metadados. Ela não
recebe ícone de movimento. Uma das suas falas continua sem mídia (`coda_5__queen`).

O relatório `placement_audit.json` considera um bloco posicionado quando existe
acesso a ele por uma fase presente no mapa ou por uma âncora global exibível.
Coordenadas locais de fases não são usadas como coordenadas globais. Blocos que
existem apenas em fases ausentes do mapa, nos interiores de fast travel ou sem
referência estruturada permanecem listados com a razão e as fontes disponíveis.
O relatório também lista WAVs ingleses não consumidos pelas legendas, para revisão.
A revisão da extração e a relação dos pontos estão em [AUDIO_PLACEMENT_REVIEW.md](AUDIO_PLACEMENT_REVIEW.md).

## Filtrar fases com diálogo

No controle de camadas, **Only levels with dialogue (219)** restringe os
marcadores e a busca às fases com áudio registrado. A escolha permanece salva
no navegador. Desativar o filtro restaura as demais fases; as camadas de
regiões, audiologs e gatilhos mantêm seus controles independentes. As contagens
das camadas acompanham o filtro. Um pequeno balão no canto do marcador
identifica fases com diálogo, preservando a cor e o símbolo principal.
