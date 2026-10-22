"""Export all level dialogue and world audio logs from the game.

python3 scripts/export_audio_catalog.py --extracted-root /path/to/extraidos \
    --package /path/to/data/levels.package --ffmpeg /path/to/ffmpeg

The automatic builder is the default. --config data/audio/pilot.json explicitly
selects the original pilot for regression work only; it is not needed to export.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import sys
import wave

sys.dont_write_bytecode = True
from simp_tool import parse_entities, decode_diff, build_tables, load_schema, extract_schema

HEADER = re.compile(r"^(:{1,3})\s+(\S+)\s*$")
NUMBER = re.compile(r"[+-]?\d+(?:\.\d+)?$")
ROOT = Path(__file__).resolve().parents[1]
SPEAKERS = {"warrior": "Valens", "magistrate": "Magistrate Reynard", "ratleigh": "Ratleigh"}
REFERENCE_FIELDS = {"Guy": {"initial_bark", "win_bark"}, "Marker": {"string_parameter"},
                    "Voice_Log": {"name"}, "Checkpoint": {"story"}}


def initialize_schema(package, schema=None):
    """Decode against named, versioned fields from the matching game executable."""
    source = schema or package.parent.parent / "sinking_star.exe"
    build_tables(extract_schema(str(source)) if source.suffix.lower() == ".exe"
                 else load_schema(str(source)))


def parse_subtitles(text):
    blocks, block, cue = {}, None, None
    for line_number, line in enumerate(text.lstrip("\ufeff").splitlines(), 1):
        header = HEADER.fullmatch(line)
        if header:
            block_id = header[2]
            if block_id in blocks:
                raise ValueError(f"Duplicate subtitle ID {block_id} at line {line_number}")
            block = {"header": header[1], "line": line_number, "cues": []}
            blocks[block_id] = block
            cue = None
        elif line.startswith(":"):
            raise ValueError(f"Unknown subtitle header at line {line_number}: {line}")
        elif line.startswith("="):
            if block is None:
                raise ValueError(f"Cue outside a block at line {line_number}")
            tokens = line[1:].split()
            if len(tokens) < 2 or not NUMBER.fullmatch(tokens[1]):
                raise ValueError(f"Unknown cue at line {line_number}: {line}")
            override = None
            if "!" in tokens:
                pos = tokens.index("!")
                if pos != len(tokens) - 2:
                    raise ValueError(f"Invalid audio reference at line {line_number}")
                override = tokens[pos + 1]
                tokens = tokens[:pos]
            if len(tokens) > 3 or (len(tokens) == 3 and not NUMBER.fullmatch(tokens[2])):
                raise ValueError(f"Unknown timing at line {line_number}: {line}")
            cue = {"speaker": tokens[0], "timing": tokens[1:], "audioOverride": override,
                   "line": line_number, "textLines": [], "notes": [], "commands": []}
            block["cues"].append(cue)
        elif cue is not None:
            if line.startswith("++"):
                cue["notes"].append(line[2:].strip())
            elif line.startswith("+"):
                cue["commands"].append(line[1:].strip())
            elif line.strip():
                cue["textLines"].append(line.strip())
        elif line.strip() and line.strip() != "[1]":
            raise ValueError(f"Content outside a cue at line {line_number}: {line}")
    return blocks


def split_clips(block_id, block, *, voice_log=False):
    clips = []
    sequence = 0
    absolute_timeline = voice_log and all(
        len(cue['timing']) == 1 and not cue['timing'][0].startswith(('+', '-'))
        for cue in block['cues'])
    if absolute_timeline:
        times = [float(cue['timing'][0]) for cue in block['cues']]
        if times != sorted(times):
            raise ValueError(f'Non-monotonic absolute timeline in {block_id}')
    for cue in block["cues"]:
        if cue["speaker"] == "_":
            if cue["textLines"]:
                raise ValueError(f"Unexpected spoken text in control cue {block_id}")
            continue
        starts_clip = (not clips or len(cue["timing"]) == 2 or cue["audioOverride"]
                       or (absolute_timeline and cue['speaker'] != clips[-1]['speaker']))
        if starts_clip:
            override = cue['audioOverride']
            variant = re.fullmatch(re.escape(block_id) + r'_(\d+)[a-z]__(\w+)', override or '')
            inserted_variant = (voice_log and variant and clips
                and clips[-1]['id'] == f'{block_id}_{variant[1]}__{variant[2]}')
            if not inserted_variant:
                sequence += 1
            clip_id = override or f"{block_id}_{sequence}__{cue['speaker']}"
            if not re.fullmatch(r"[A-Za-z0-9_]+", clip_id):
                raise ValueError(f"Unsafe audio ID: {clip_id}")
            clips.append({"id": clip_id, "speaker": cue["speaker"], "chunks": [], "cues": []})
        elif cue["speaker"] != clips[-1]["speaker"]:
            raise ValueError(f"Ambiguous clip boundary in {block_id} at line {cue['line']}")
        text = " ".join(cue["textLines"])
        if not text and not voice_log:
            raise ValueError(f"Empty spoken cue in {block_id} at line {cue['line']}")
        if text:
            clips[-1]["chunks"].append(text)
        clips[-1]["cues"].append({k: v for k, v in cue.items() if k != "textLines"})
    if any(not clip['chunks'] for clip in clips):
        raise ValueError(f'Clip has no transcript in {block_id}')
    return clips


def clip_order_evidence(clips):
    """Describe filename agreement without overriding the subtitle cue sequence.

    Numbering belongs to a dialogue block, not a level. Explicit ! references
    can reuse numbers or insert variants; gaps are allowed and do not prove loss.
    """
    numbers = []
    for clip in clips:
        match = re.search(r"_(\d+)([a-z]?)__(\w+)$", clip["id"])
        if not match:
            return {"source": "subtitle-cue-order", "filenameCheck": "not-comparable"}
        numbers.append((int(match[1]), match[2]))
    agrees = len(set(numbers)) == len(numbers) and numbers == sorted(numbers)
    return {"source": "subtitle-cue-order",
            "filenameCheck": "agrees" if agrees else "needs-review"}


def package_entries(handle):
    if handle.read(4) != b"simp":
        raise ValueError("Invalid Simple_Package header")
    handle.seek(16)
    toc = struct.unpack("<Q", handle.read(8))[0]
    handle.seek(toc + 8)
    count = struct.unpack("<Q", handle.read(8))[0]
    handle.seek(toc + 64)
    entries = {}
    for _ in range(count):
        length = struct.unpack("<I", handle.read(4))[0]
        name = handle.read(length).decode("utf-8")
        handle.read(1)
        entries[name.replace("\\", "/")] = struct.unpack("<QQ", handle.read(16))
    return entries


def level_references(handle, entries, level):
    candidates = [key for key in entries if Path(key).name == level + ".entities"]
    if len(candidates) != 1:
        raise ValueError(f"Expected one entity file for {level}, got {len(candidates)}")
    size, offset = entries[candidates[0]]
    handle.seek(offset)
    references = {}
    for entity_id, entity_type, diff, version in parse_entities(handle.read(size)):
        members = decode_diff(entity_type, diff, version)
        position = {axis: 0.0 for axis in "xyz"}
        for member in members:
            if member.get("name") in {"position.x", "position.y", "position.z"}:
                position[member["name"][-1]] = member["value"]
        for member in members:
            if member.get("name") not in REFERENCE_FIELDS.get(entity_type, set()):
                continue
            value = member["value"]
            if not isinstance(value, str) or not value:
                continue
            references.setdefault(value, []).append({"entityId": entity_id, "entityType": entity_type,
                "member": hex(member["member"]), "field": member["name"],
                "source": candidates[0], "coordinateSpace": "level-local",
                "coordinates": [position[axis] for axis in "xyz"]})
    return references


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def export(extracted_root, package, config_path, output_root, schema=None):
    initialize_schema(package, schema)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    sources, subtitles = {}, {}
    for language in config["languages"]:
        path = extracted_root / "legendas/data/strings/subtitles" / f"{language}.subtitles.txt"
        source = path.read_bytes()
        sources[language] = hashlib.sha256(source).hexdigest()
        subtitles[language] = parse_subtitles(source.decode("utf-8-sig"))
    audio_root = extracted_root / "audio/data/sound/GeneratedSoundBanks/Windows/ExternalSources/English"
    catalog = {"schemaVersion": 1, "languages": config["languages"], "levels": {}}
    existing_catalog = output_root / 'data/audio/catalog.json'
    if existing_catalog.exists():
        existing = json.loads(existing_catalog.read_text(encoding='utf-8'))
        if 'logs' in existing:
            catalog['logs'] = existing['logs']
    documents, files = {}, {}
    with package.open("rb") as handle:
        entries = package_entries(handle)
        for level, groups in config["levels"].items():
            references = level_references(handle, entries, level)
            conversations = []
            for group in groups:
                block_id = group["id"]
                if block_id not in references:
                    raise ValueError(f"No structured entity reference for {level}/{block_id}")
                translations = {lang: split_clips(block_id, subtitles[lang][block_id])
                                for lang in config["languages"]}
                english = translations["en"]
                if len(english) != group["expectedClips"]:
                    raise ValueError(f"Unexpected clip count for {block_id}")
                for lang, clips in translations.items():
                    if [(c["id"], c["speaker"]) for c in clips] != [(c["id"], c["speaker"]) for c in english]:
                        raise ValueError(f"Translation alignment differs for {block_id}/{lang}")
                published = []
                for i, clip in enumerate(english):
                    source = audio_root / (clip["id"] + ".wav")
                    with wave.open(str(source)) as wav:
                        duration = round(wav.getnframes() / wav.getframerate(), 6)
                    relative = "audio/levels/" + source.name
                    files[relative] = source
                    published.append({"id": clip["id"], "speaker": clip["speaker"],
                                      "speakerName": SPEAKERS.get(clip["speaker"], clip["speaker"]),
                                      "src": relative, "duration": duration,
                                      "transcripts": {lang: clips[i]["chunks"] for lang, clips in translations.items()}})
                conversations.append({"id": block_id, "clips": published,
                                      "clipOrdering": clip_order_evidence(english),
                                      "provenance": {"entities": references[block_id],
                                          "subtitles": {lang: {"line": subtitles[lang][block_id]["line"],
                                              "header": subtitles[lang][block_id]["header"],
                                              "clips": clips} for lang, clips in translations.items()}}})
            documents[level] = {"schemaVersion": 1, "level": level, "orderSource": "pilot.json",
                                "conversationOrdering": {"source": "pilot.json", "automatic": False},
                                "subtitleSha256": sources, "conversations": conversations}
            catalog["levels"][level] = f"data/audio/levels/{level}.json"
    # Validate all input and associations before writing any output.
    for level, document in documents.items():
        write_json(output_root / catalog["levels"][level], document)
    for relative, source in files.items():
        destination = output_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.resolve() != destination.resolve():
            shutil.copyfile(source, destination)
    write_json(output_root / "data/audio/catalog.json", catalog)
    print(f"Exported {len(documents)} levels, {len(files)} WAVs; languages: {', '.join(config['languages'])}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extracted-root", type=Path, required=True)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--config", type=Path, help="Optional legacy pilot configuration; omit for the full automatic catalog")
    parser.add_argument("--output-root", type=Path, default=ROOT)
    parser.add_argument("--schema", type=Path, help="Matching schema JSON or game executable; defaults to the executable next to data/")
    parser.add_argument('--ffmpeg', type=Path, default=shutil.which('ffmpeg'))
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    if args.config:
        export(args.extracted_root, args.package, args.config, args.output_root, args.schema)
    else:
        from build_audio_catalog import build
        if not args.ffmpeg or not args.ffmpeg.is_file():
            parser.error('FFmpeg is required; provide --ffmpeg /path/to/ffmpeg')
        if not 1 <= args.workers <= 16:
            parser.error('--workers must be between 1 and 16')
        build(args.extracted_root, args.package, args.output_root, ROOT / 'data/markers.json',
              args.ffmpeg, args.schema, args.workers)
