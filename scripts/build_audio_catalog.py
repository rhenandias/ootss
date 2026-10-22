"""Build the complete dialogue catalog from the game, without per-level configuration.

python3 scripts/build_audio_catalog.py --extracted-root /path/to/extraidos \
    --package /path/to/data/levels.package --ffmpeg /path/to/ffmpeg

The game package associates dialogue with levels. Subtitle cue order determines
clip order; block order is stable presentation order, not a claim about gameplay.
All media is validated before replacing the published catalog. Only owned,
unmodified obsolete outputs are removed; a first migration is backed up.
"""
import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import wave

sys.dont_write_bytecode = True
from export_audio_catalog import (ROOT, SPEAKERS, initialize_schema, package_entries,
                                  parse_subtitles, split_clips, clip_order_evidence, write_json)
from simp_tool import parse_entities, decode_diff

AUDIO_FIELDS = {
    'Guy': {'initial_bark', 'win_bark'},
    'Marker': {'string_parameter', 'script_name'},
    'Voice_Log': {'name'}, 'Checkpoint': {'story'},
    'Sign': {'turn_away_bark', 'look_at_bark'}, 'Wardrobe': {'usage_bark'},
    'Boat': {'initial_talk_name', 'repeat_talk_name'},
    'Overworld_Unlock': {'bark_name'}, 'Judge': {'code'},
    'Settings': {'story_tag', 'intro_cutscene', 'outro_cutscene', 'story_proc_arg_string'},
    'Artifact': {'cutscene_name'},
}
MEDIA_PROFILE = 'mp3-mono-44100-96k-v1'
SAFE_ID = re.compile(r'[A-Za-z0-9_]+$')


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()


def references_for_entity(entity, subtitles):
    """Return (block, provenance) pairs from named dialogue fields, not meshes."""
    fields = entity['fields']
    found = []
    for field in sorted(AUDIO_FIELDS.get(entity['type'], ())):
        value = fields.get(field)
        if not isinstance(value, str) or not value:
            continue
        matches = [value] if value in subtitles else []
        namespace = field == 'story_tag'
        conditional = entity['type'] == 'Marker' and fields.get('script_name') == 'bark_conditional'
        if namespace or conditional:
            matches += [block for block in subtitles if block.startswith(value + '_')]
        for block in dict.fromkeys(matches):
            found.append((block, {'entityId': entity['id'], 'entityType': entity['type'],
                'field': field, 'value': value,
                'rule': 'exact-reference' if block == value else 'dialogue-namespace',
                'coordinates': [fields.get('position.' + axis, 0.0) for axis in 'xyz']}))
    # Named markers and speakers are also engine-driven dialogue anchors.
    anchor = fields.get('entity_name')
    if entity['type'] in {'Marker', 'Guy'} and anchor in subtitles and anchor not in {block for block, _ in found}:
        found.append((anchor, {'entityId': entity['id'], 'entityType': entity['type'],
            'field': 'entity_name', 'value': anchor, 'rule': 'named-dialogue-anchor',
            'coordinates': [fields.get('position.' + axis, 0.0) for axis in 'xyz']}))
    return found


def expand_story_namespaces(entities, associations, subtitles):
    """A story-tagged level can contain several runtime dialogue namespaces.

    Infer additional namespaces only from at least two distinct direct references
    in that level. In skipping_pals this recovers pals_*; in skipping_stones it
    recovers ssnew_*. No proximity or guessed filename-to-level match is used.
    """
    tags = [e for e in entities if e['type'] == 'Settings' and e['fields'].get('story_tag')]
    if not tags:
        return
    direct = {block for block, refs in associations.items()
              if any(ref['rule'] == 'exact-reference' for ref in refs)}
    prefixes = Counter(block.split('_', 1)[0] for block in direct if '_' in block)
    for prefix, count in sorted(prefixes.items()):
        if count < 2:
            continue
        for block in subtitles:
            if block.startswith(prefix + '_') and block not in associations:
                associations.setdefault(block, []).append({'entityId': tags[0]['id'], 'entityType': 'Settings',
                    'field': 'story_tag', 'value': tags[0]['fields']['story_tag'],
                    'rule': 'related-story-namespace', 'namespace': prefix,
                    'supportingBlocks': sorted(b for b in direct if b.startswith(prefix + '_'))})


def scan_package(package, subtitles):
    levels, world_entities, issues, missing_references = {}, [], [], []
    with package.open('rb') as handle:
        entries = package_entries(handle)
        for source, (size, offset) in sorted(entries.items()):
            if not source.endswith('.entities'):
                continue
            level = Path(source).stem
            if level in levels:
                raise ValueError(f'Duplicate entity source for {level}')
            handle.seek(offset)
            entities = []
            for entity_id, entity_type, diff, version in parse_entities(handle.read(size)):
                if entity_type not in AUDIO_FIELDS and entity_type != 'Group':
                    continue
                members = decode_diff(entity_type, diff, version)
                unknown = [m for m in members if 'name' not in m]
                entity = {'id': entity_id, 'type': entity_type,
                          'fields': {m['name']: m['value'] for m in members if 'name' in m},
                          'unknownMembers': len(unknown)}
                entities.append(entity)
                if unknown:
                    issues.append({'source': source, 'entityId': entity_id,
                                   'entityType': entity_type, 'unknownMembers': len(unknown)})
            associations = defaultdict(list)
            for entity in entities:
                entity_refs = references_for_entity(entity, subtitles)
                for block, ref in entity_refs:
                    associations[block].append(ref | {'source': source})
                for field in sorted(AUDIO_FIELDS.get(entity['type'], ())):
                    value = entity['fields'].get(field)
                    if not isinstance(value, str) or not value or value in subtitles:
                        continue
                    if field in {'script_name', 'story_tag', 'intro_cutscene', 'outro_cutscene', 'cutscene_name', 'code'}:
                        continue
                    if entity['type'] == 'Marker' and entity['fields'].get('script_name') not in {'bark', 'bark_on_id'}:
                        continue
                    if not any(ref['field'] == field for _, ref in entity_refs):
                        missing_references.append({'level': level, 'source': source,
                            'entityId': entity['id'], 'entityType': entity['type'],
                            'field': field, 'value': value})
            expand_story_namespaces(entities, associations, subtitles)
            levels[level] = {'source': source, 'associations': dict(associations)}
            if level == 'overworld':
                world_entities = entities
    return levels, world_entities, issues, missing_references


def is_silent_clip(clip):
    text = ' '.join(clip['chunks']).strip()
    return bool(text) and not any(char.isalnum() for char in text)


def resolve_block(block_id, subtitles, audio_root):
    """English defines clip identities; align translations by identity, never cue index."""
    english = split_clips(block_id, subtitles['en'][block_id], voice_log=True)
    translations = {'en': english}
    translation_issues = {}
    for language, blocks in subtitles.items():
        if language == 'en':
            continue
        try:
            translated = split_clips(block_id, blocks[block_id], voice_log=True)
            en_ids = [(c['id'], c['speaker']) for c in english]
            if [(c['id'], c['speaker']) for c in translated] != en_ids:
                raise ValueError('Clip identities differ from English')
            translations[language] = translated
        except (KeyError, ValueError) as error:
            translation_issues[language] = str(error)
    clips, missing, silent = [], [], []
    for index, clip in enumerate(english):
        if not SAFE_ID.fullmatch(clip['id']):
            raise ValueError(f'Unsafe audio ID {clip["id"]}')
        source = audio_root / (clip['id'] + '.wav')
        if not source.exists():
            if is_silent_clip(clip):
                silent.append({'id': clip['id'], 'speaker': clip['speaker'],
                               'chunks': clip['chunks'], 'cueLines': [c['line'] for c in clip['cues']]})
            else:
                missing.append({'id': clip['id'], 'speaker': clip['speaker'], 'chunks': clip['chunks']})
            continue
        with wave.open(str(source)) as wav:
            if not wav.getnframes() or not wav.getframerate():
                raise ValueError(f'Empty audio file {source.name}')
            duration = round(wav.getnframes() / wav.getframerate(), 6)
        clips.append({'id': clip['id'], 'speaker': clip['speaker'],
            'speakerName': SPEAKERS.get(clip['speaker'], clip['speaker']),
            'duration': duration, 'src': f'audio/clips/{clip["id"]}.mp3',
            'transcripts': {lang: translations[lang][index]['chunks'] if lang in translations else []
                            for lang in subtitles},
            'provenance': {'sourceWav': source.name, 'subtitleCueLines': [c['line'] for c in clip['cues']],
                           'explicitAudioReference': clip['cues'][0]['audioOverride']}})
    conversation_transcripts = {language: [' '.join(cue['textLines'])
        for cue in blocks.get(block_id, {}).get('cues', [])
        if cue['speaker'] != '_' and cue['textLines']] for language, blocks in subtitles.items()}
    return {'id': block_id, 'clips': clips, 'clipOrdering': clip_order_evidence(english),
            'transcripts': conversation_transcripts,
            'silentCues': silent, 'missingClips': missing, 'translationIssues': translation_issues}


def world_features(entities, triggers=None):
    """Entity positions are world coordinates; group membership is not an offset."""
    lookup = {entity['id']: entity for entity in entities}
    features = []
    for entity in entities:
        trigger = (triggers or {}).get(entity['id'])
        if entity['type'] != 'Voice_Log' and not trigger:
            continue
        fields = entity['fields']
        group_id = fields.get('group_id', 0)
        chain, seen, unsupported = [], set(), False
        current = group_id
        while current:
            if current in seen or current not in lookup:
                unsupported = True
                break
            seen.add(current)
            group = lookup[current]
            chain.append(current)
            if group['fields'].get('transform_group') or group['unknownMembers']:
                unsupported = True
            current = group['fields'].get('group_id', 0)
        position = [fields.get('position.' + axis, 0.0) for axis in 'xyz']
        # The existing tiles cover these three realms, not the fast-travel interior.
        covered = -57 <= position[2] <= 75
        name = trigger['name'] if trigger else fields.get('name')
        features.append({'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': position},
            'properties': {'type': 'Audio_Trigger' if trigger else 'Voice_Log', 'id': entity['id'], 'name': name,
                'source': 'data-common/overworld.entities', 'sourceLevel': 'overworld',
                'coordinateSpace': 'world', 'groupId': group_id, 'groupChain': chain,
                'mapReady': bool(name) and covered and not unsupported and not entity['unknownMembers'],
                'mapExclusion': 'outside-current-tiles' if not covered else
                                'unresolved-group-transform' if unsupported else
                                'unknown-entity-members' if entity['unknownMembers'] else None,
                **(trigger or {})}})
    return sorted(features, key=lambda f: f['properties']['id'])


def world_triggers(entities, subtitles):
    """Locate explicit world dialogue anchors without guessing a runtime condition.

    Only a non-point bark marker with positive box extents is labelled movement.
    Named engine anchors remain scripted events: their activation is not known.
    """
    result = {}
    for entity in entities:
        if entity['type'] in {'Voice_Log', 'Settings', 'Group'}:
            continue
        refs = references_for_entity(entity, subtitles)
        if not refs:
            continue
        fields = entity['fields']
        script = fields.get('script_name')
        extents = [fields.get('box_extents.' + axis, 0) for axis in 'xyz']
        if (entity['type'] == 'Marker' and script in {'bark', 'bark_conditional', 'bark_on_id'}
                and fields.get('is_point_marker') is False and all(v > 0 for v in extents)):
            kind = 'movement'
        else:
            kind = {'Guy': 'character', 'Sign': 'sign', 'Wardrobe': 'object',
                    'Boat': 'boat', 'Checkpoint': 'checkpoint',
                    'Overworld_Unlock': 'unlock', 'Artifact': 'object'}.get(entity['type'], 'scripted')
        blocks = list(dict.fromkeys(block for block, _ in refs))
        result[entity['id']] = {
            'name': blocks[0] if len(blocks) == 1 else f'audio_trigger_{entity["id"]}',
            'audioKey': str(entity['id']), 'triggerKind': kind, 'blocks': blocks,
            'scriptName': script, 'boxExtents': extents if kind == 'movement' else None,
            'barkFlags': fields.get('bark_flags', 0),
            'activationVerifiedInGame': False,
            'provenance': [ref for _, ref in refs]}
    return result


def placement_audit(resolved, scanned, map_levels, features, trigger_features, audio_root):
    """Account for every subtitle block against actual visible map entry points."""
    locations = defaultdict(list)
    for level in map_levels:
        for block in scanned[level]['associations']:
            locations[block].append({'kind': 'level', 'level': level})
    excluded = []
    for feature in features + trigger_features:
        props = feature['properties']
        blocks = props.get('blocks', [props['name']])
        for block in blocks:
            if props['mapReady']:
                locations[block].append({'kind': props['type'], 'entityId': props['id'],
                    'coordinates': feature['geometry']['coordinates']})
            else:
                excluded.append({'block': block, 'entityId': props['id'],
                    'reason': props['mapExclusion'], 'coordinates': feature['geometry']['coordinates']})
    unplaced = []
    for block, value in resolved.items():
        if value['clips'] and not locations[block]:
            sources = [level for level, data in scanned.items() if block in data['associations']]
            direct_sources = [level for level in sources if any(
                ref['rule'] != 'related-story-namespace' for ref in scanned[level]['associations'][block])]
            exclusion = next((e['reason'] for e in excluded if e['block'] == block), None)
            reason = (exclusion or ('only-unmapped-levels' if direct_sources else
                      'namespace-without-spatial-anchor' if sources else 'no-structured-reference'))
            unplaced.append({'block': block, 'recordings': len(value['clips']), 'sourceLevels': sources,
                'directSourceLevels': direct_sources, 'reason': reason})
    used_ids = {clip['id'] for value in resolved.values() for clip in value['clips']}
    return {'schemaVersion': 1, 'placedBlocks': sum(bool(v) for v in locations.values()),
        'unplacedBlocks': unplaced, 'excludedWorldAnchors': excluded,
        'locations': {k: v for k, v in sorted(locations.items()) if v},
        'englishWavsWithoutSubtitleClip': sorted(p.stem for p in audio_root.glob('*.wav') if p.stem not in used_ids)}


def encode_clip(clip_id, audio_root, output_root, stage, ffmpeg, previous_media):
    source = audio_root / (clip_id + '.wav')
    source_hash = digest(source)
    relative = f'audio/clips/{clip_id}.mp3'
    published = output_root / relative
    old = previous_media.get(relative, {})
    if (old.get('sourceSha256') == source_hash and old.get('profile') == MEDIA_PROFILE
            and published.exists() and digest(published) == old.get('sha256')):
        return relative, old, False
    destination = stage / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([str(ffmpeg), '-nostdin', '-v', 'error', '-y', '-i', str(source),
                    '-map_metadata', '-1', '-ac', '1', '-ar', '44100', '-c:a', 'libmp3lame',
                    '-b:a', '96k', str(destination)], check=True, capture_output=True)
    return relative, {'sourceSha256': source_hash, 'profile': MEDIA_PROFILE,
                      'sha256': digest(destination), 'bytes': destination.stat().st_size}, True


def catalog_files(output_root, catalog):
    """Identify only explicitly referenced, generated manifests and media."""
    files = set()
    for section in ('levels', 'logs', 'triggers'):
        for relative in catalog.get(section, {}).values():
            if not relative.startswith(f'data/audio/{section}/') or '..' in Path(relative).parts:
                continue
            files.add(relative)
            path = output_root / relative
            if path.is_file():
                document = json.loads(path.read_text(encoding='utf-8'))
                for group in document.get('conversations', []):
                    for clip in group.get('clips', []):
                        source = clip.get('src', '')
                        if source.startswith(('audio/levels/', 'audio/logs/', 'audio/clips/')) and '..' not in Path(source).parts:
                            files.add(source)
    return files


def publish(stage, output_root, generated, previous, previous_catalog):
    old_files = previous.get('files', {})
    legacy = catalog_files(output_root, previous_catalog) if not previous else set()
    obsolete = (set(old_files) | legacy) - set(generated['files'])
    backup = output_root / '.git/audio-catalog-backups'
    for relative in sorted(obsolete):
        path = output_root / relative
        if not path.is_file():
            continue
        if relative in old_files and digest(path) != old_files[relative]['sha256']:
            raise ValueError(f'Obsolete generated output was edited; preserved: {relative}')
        # Keep migration originals recoverable outside the published site.
        destination = backup / digest(path) / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not destination.exists():
            shutil.copyfile(path, destination)
    for path in sorted(stage.rglob('*')):
        if not path.is_file() or path.name in ('catalog.json', 'generated.json'):
            continue
        target = output_root / path.relative_to(stage)
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_name(target.name + '.tmp')
        shutil.copyfile(path, temporary)
        os.replace(temporary, target)
    for relative in ['data/audio/catalog.json', 'data/audio/generated.json']:
        target = output_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_name(target.name + '.tmp')
        shutil.copyfile(stage / relative, temporary)
        os.replace(temporary, target)
    for relative in sorted(obsolete):
        (output_root / relative).unlink(missing_ok=True)


def build(extracted_root, package, output_root, markers, ffmpeg, schema=None, workers=4, inspect_only=False):
    initialize_schema(package, schema)
    subtitles, subtitle_hashes = {}, {}
    for language in ('en', 'pt-br'):
        path = extracted_root / f'legendas/data/strings/subtitles/{language}.subtitles.txt'
        subtitles[language] = parse_subtitles(path.read_text(encoding='utf-8-sig'))
        subtitle_hashes[language] = digest(path)
    english = subtitles['en']
    audio_root = extracted_root / 'audio/data/sound/GeneratedSoundBanks/Windows/ExternalSources/English'
    scanned, world, decode_issues, missing_references = scan_package(package, english)
    map_levels = sorted({f['properties']['name'] for f in json.loads(markers.read_text())['features']
                         if f['properties']['type'] == 'Level_Entry'})
    missing_sources = set(map_levels) - set(scanned)
    if missing_sources:
        raise ValueError(f'Missing entity sources: {sorted(missing_sources)}')
    triggers = world_triggers(world, english)
    all_features = world_features(world, triggers)
    features = [f for f in all_features if f['properties']['type'] == 'Voice_Log']
    trigger_features = [f for f in all_features if f['properties']['type'] == 'Audio_Trigger']
    log_names = sorted({e['fields']['name'] for e in world if e['type'] == 'Voice_Log' and e['fields'].get('name')})
    referenced = {block for level in scanned.values() for block in level['associations']}
    resolved = {name: resolve_block(name, subtitles, audio_root) for name in english}
    previous_path = output_root / 'data/audio/generated.json'
    previous = json.loads(previous_path.read_text()) if previous_path.exists() else {}
    catalog_path = output_root / 'data/audio/catalog.json'
    previous_catalog = json.loads(catalog_path.read_text()) if catalog_path.exists() else {}
    catalog = {'schemaVersion': 1, 'languages': list(subtitles), 'levels': {}, 'logs': {}, 'triggers': {}}
    report_levels = {}
    documents = {}
    used_blocks = set()
    for level in sorted(scanned):
        refs = scanned[level]['associations']
        groups = []
        for block in sorted(refs, key=lambda name: english[name]['line']):
            value = resolved[block]
            if not value['clips']:
                continue
            groups.append(value | {'provenance': {'entities': refs[block],
                'subtitleLine': english[block]['line'], 'subtitleHeader': english[block]['header']}})
            used_blocks.add(block)
        report_levels[level] = {'onMap': level in map_levels, 'references': len(refs),
            'blocks': [g['id'] for g in groups], 'clips': sum(len(g['clips']) for g in groups),
            'status': 'audio' if groups else 'no-audio-references' if not refs else 'no-available-media'}
        if groups:
            relative = f'data/audio/levels/{level}.json'
            documents[relative] = {'schemaVersion': 1, 'level': level,
                'conversationOrdering': {'source': 'subtitle-block-order', 'narrativeOrderVerified': False},
                'subtitleSha256': subtitle_hashes, 'conversations': groups}
            catalog['levels'][level] = relative
    for name in log_names:
        if name not in resolved:
            raise ValueError(f'World Voice_Log has no English subtitle block: {name}')
        used_blocks.add(name)
        value = resolved[name]
        if value['clips']:
            relative = f'data/audio/logs/{name}.json'
            documents[relative] = {'schemaVersion': 1, 'audioLog': name,
                'subtitleSha256': subtitle_hashes, 'conversations': [value]}
            catalog['logs'][name] = relative
    for identity, trigger in sorted(triggers.items()):
        groups = [resolved[name] for name in sorted(trigger['blocks'], key=lambda name: english[name]['line'])
                  if resolved[name]['clips']]
        if groups:
            relative = f'data/audio/triggers/{identity}.json'
            documents[relative] = {'schemaVersion': 1, 'trigger': trigger,
                'subtitleSha256': subtitle_hashes, 'conversations': groups}
            catalog['triggers'][str(identity)] = relative
    placement = placement_audit(resolved, scanned, map_levels, features, trigger_features, audio_root)
    # Keep every available source recording exportable, including dialogue not
    # referenced by this version of the level package. These are not guessed onto levels.
    clip_ids = {clip['id'] for block in resolved.values() for clip in block['clips']}
    summary = {'mapLevels': len(map_levels),
        'mapLevelsWithAudio': sum(report_levels[level]['status'] == 'audio' for level in map_levels),
        'levelsWithAudio': len(catalog['levels']), 'worldAudioLogs': len(catalog['logs']),
        'worldMarkers': sum(f['properties']['mapReady'] for f in features),
        'worldTriggerMarkers': sum(f['properties']['mapReady'] for f in trigger_features),
        'movementTriggerMarkers': sum(f['properties']['mapReady'] and f['properties']['triggerKind'] == 'movement'
                                     for f in trigger_features),
        'unplacedAudioBlocks': len(placement['unplacedBlocks']),
        'subtitleBlocks': len(english), 'referencedBlocks': len(referenced),
        'unreferencedBlocks': len(set(english) - referenced), 'uniqueRecordings': len(clip_ids),
        'silentCues': sum(len(value['silentCues']) for value in resolved.values()),
        'missingRecordings': sum(len(value['missingClips']) for value in resolved.values()),
        'referencesWithoutSubtitles': len(missing_references),
        'decodeIssues': len(decode_issues)}
    schema_source = schema or package.parent.parent / 'sinking_star.exe'
    report = {'schemaVersion': 1, 'summary': summary, 'subtitleSha256': subtitle_hashes,
        'sources': {'packageSha256': digest(package), 'schemaSourceSha256': digest(schema_source)},
        'ordering': 'Clips follow English subtitle cues; blocks follow subtitle file order. Conditional variants are listed, not simulated.',
        'levels': report_levels, 'decodeIssues': decode_issues,
        'referencesWithoutSubtitles': missing_references,
        'missingRecordings': {name: value['missingClips'] for name, value in resolved.items() if value['missingClips']},
        'silentCues': {name: value['silentCues'] for name, value in resolved.items() if value['silentCues']},
        'translationIssues': {name: value['translationIssues'] for name, value in resolved.items() if value['translationIssues']},
        'unreferencedBlocks': sorted(set(english) - referenced)}
    print(json.dumps(summary, indent=2), flush=True)
    if inspect_only:
        return report
    with tempfile.TemporaryDirectory(prefix='ootss-full-audio-') as temporary:
        stage = Path(temporary)
        media, converted = {}, 0
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(encode_clip, name, audio_root, output_root, stage,
                                   ffmpeg, previous.get('media', {})): name for name in sorted(clip_ids)}
            for count, future in enumerate(as_completed(futures), 1):
                relative, entry, changed = future.result()
                media[relative] = entry
                converted += changed
                if count % 100 == 0 or count == len(clip_ids):
                    print(f'Media {count}/{len(clip_ids)}; converted {converted}; reused {count-converted}', flush=True)
        # Archive preserves all source subtitle blocks without assigning unused dialogue to a level.
        archive = {'schemaVersion': 1, 'subtitleSha256': subtitle_hashes,
                   'conversations': [resolved[name] for name in english]}
        documents['data/audio/archive.json'] = archive
        documents['data/audio/report.json'] = report
        documents['data/audio/placement_audit.json'] = placement
        documents['data/audio/voice_logs.geojson'] = {'type': 'FeatureCollection', 'features': features}
        documents['data/audio/audio_triggers.geojson'] = {'type': 'FeatureCollection', 'features': trigger_features}
        for relative, value in sorted(documents.items()):
            write_json(stage / relative, value)
        write_json(stage / 'data/audio/catalog.json', catalog)
        files = {relative: {'sha256': entry['sha256']} for relative, entry in sorted(media.items())}
        for relative in sorted(documents):
            files[relative] = {'sha256': digest(stage / relative)}
        generated = {'schemaVersion': 1, 'profile': MEDIA_PROFILE, 'files': files,
                     'media': dict(sorted(media.items()))}
        write_json(stage / 'data/audio/generated.json', generated)
        publish(stage, output_root, generated, previous, previous_catalog)
    print(f'Published {summary["mapLevelsWithAudio"]} map levels, {len(catalog["logs"])} world logs, '
          f'{len(clip_ids)} MP3s ({sum(v["bytes"] for v in media.values())/1_000_000:.1f} MB).', flush=True)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--extracted-root', type=Path, required=True)
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--schema', type=Path)
    parser.add_argument('--markers', type=Path, default=ROOT / 'data/markers.json')
    parser.add_argument('--output-root', type=Path, default=ROOT)
    parser.add_argument('--ffmpeg', type=Path, default=shutil.which('ffmpeg'))
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--inspect-only', action='store_true', help='Validate sources and print coverage without changing the site')
    args = parser.parse_args()
    if not args.inspect_only and (not args.ffmpeg or not args.ffmpeg.is_file()):
        parser.error('FFmpeg is required; provide --ffmpeg /path/to/ffmpeg')
    if not 1 <= args.workers <= 16:
        parser.error('--workers must be between 1 and 16')
    build(args.extracted_root, args.package, args.output_root, args.markers,
          args.ffmpeg, args.schema, args.workers, args.inspect_only)
