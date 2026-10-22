# Audio comparison samples

Open http://localhost:8765/audio-comparison/ while the project server is running.
From the project root, the server command is `python3 -m http.server 8765 --bind 127.0.0.1`.

Seven complete dialogue excerpts are provided at 96, 64, 48 and 32 kbps (28 MP3s).
The current 96 kbps MP3s are copied byte for byte from the map catalog. Lower bitrates
are converted directly from the extracted English WAVs using FFmpeg/libmp3lame,
mono, 44.1 kHz, constant bitrate, with no additional volume processing.

Choose a sample and start playback. Use **Compare here** on another bitrate of the
same sample to continue at the current position. Players are mutually exclusive.
Headphones and a steady listening volume make comparisons easier. Dialogue may
contain spoilers. Native controls allow replaying each sample from the beginning.

`manifest.json` records source WAV names and hashes, transcripts, exact MP3 sizes
and hashes. Every `sample-NN/` directory contains the four bitrate variants.
These are local comparison assets; the map catalog and its 96 kbps audio are unchanged.
