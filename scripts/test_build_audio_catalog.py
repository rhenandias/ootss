"""Checks for automatic associations, media coverage and safe regeneration."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import wave

from export_audio_catalog import parse_subtitles, write_json
from build_audio_catalog import (references_for_entity, expand_story_namespaces,
    resolve_block, world_features, world_triggers, placement_audit, publish, digest, encode_clip, MEDIA_PROFILE)


def entity(kind, fields, identity=1):
    return {'id': identity, 'type': kind, 'fields': fields, 'unknownMembers': 0}


def wav_file(path):
    with wave.open(str(path), 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(8000)
        wav.writeframes(b'\0\0' * 8000)


class AssociationTests(unittest.TestCase):
    def test_movement_requires_bark_volume_and_keeps_conditional_variants(self):
        marker = entity('Marker', {'script_name': 'bark_conditional', 'string_parameter': 'scene',
            'is_point_marker': False, 'box_extents.x': 2, 'box_extents.y': 3, 'box_extents.z': 1,
            'position.x': 80, 'position.y': 79, 'bark_flags': 1}, 12)
        triggers = world_triggers([marker], {'scene_yes': {}, 'scene_no': {}})
        self.assertEqual(triggers[12]['triggerKind'], 'movement')
        self.assertEqual(triggers[12]['blocks'], ['scene_yes', 'scene_no'])
        point = world_features([marker], triggers)[0]
        self.assertEqual(point['geometry']['coordinates'], [80, 79, 0])
        self.assertEqual(point['properties']['type'], 'Audio_Trigger')
        self.assertEqual(point['properties']['barkFlags'], 1)
        marker['fields']['is_point_marker'] = True
        self.assertEqual(world_triggers([marker], {'scene_yes': {}})[12]['triggerKind'], 'scripted')

    def test_named_anchor_does_not_claim_movement_and_respects_group_exclusions(self):
        anchor = entity('Marker', {'entity_name': 'coda', 'group_id': 9}, 13)
        group = entity('Group', {'transform_group': True}, 9)
        triggers = world_triggers([anchor, group], {'coda': {}})
        self.assertEqual(triggers[13]['triggerKind'], 'scripted')
        self.assertFalse(triggers[13]['activationVerifiedInGame'])
        self.assertFalse(world_features([anchor, group], triggers)[0]['properties']['mapReady'])
        self.assertFalse(world_triggers([entity('Settings', {'story_tag': 'coda'})], {'coda': {}}))

    def test_audit_counts_actual_map_access_and_reports_unplaced_sources(self):
        resolved = {name: {'clips': [{'id': name}]} for name in ['mapped', 'trigger', 'offmap', 'unused', 'broad', 'interior']}
        scanned = {'puzzle': {'associations': {'mapped': [{'rule': 'exact-reference'}]}},
                   'interior': {'associations': {'offmap': [{'rule': 'exact-reference'}]}},
                   'overworld': {'associations': {'broad': [{'rule': 'related-story-namespace'}]}}}
        anchor = entity('Marker', {'entity_name': 'trigger'}, 3)
        triggers = world_triggers([anchor], {'trigger': {}})
        interior = world_features([entity('Voice_Log', {'name': 'interior', 'position.z': 89}, 4)])
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / 'extra.wav').touch()
            audit = placement_audit(resolved, scanned, ['puzzle'], interior, world_features([anchor], triggers), Path(folder))
        self.assertEqual(audit['placedBlocks'], 2)
        self.assertEqual({b['block']: b['reason'] for b in audit['unplacedBlocks']}, {
            'offmap': 'only-unmapped-levels', 'unused': 'no-structured-reference',
            'broad': 'namespace-without-spatial-anchor', 'interior': 'outside-current-tiles'})
        self.assertEqual(audit['englishWavsWithoutSubtitleClip'], ['extra'])

    def test_only_dialogue_fields_match_not_mesh_or_sound_level_name(self):
        subtitles = {'scene': {}, 'scene_other': {}}
        guy = entity('Guy', {'initial_bark': 'scene', 'mesh': 'scene_other'})
        self.assertEqual([block for block, _ in references_for_entity(guy, subtitles)], ['scene'])
        settings = entity('Settings', {'sound_level_name': 'scene'})
        self.assertFalse(references_for_entity(settings, subtitles))

    def test_conditional_variants_are_discovered_without_guessing_nearby_levels(self):
        subtitles = {'island_yes': {}, 'island_no': {}, 'other_island': {}}
        marker = entity('Marker', {'script_name': 'bark_conditional', 'string_parameter': 'island'})
        refs = references_for_entity(marker, subtitles)
        self.assertEqual([block for block, _ in refs], ['island_yes', 'island_no'])
        self.assertTrue(all(ref['rule'] == 'dialogue-namespace' for _, ref in refs))

    def test_named_speaker_anchor_is_preserved_alongside_its_initial_bark(self):
        speaker = entity('Guy', {'entity_name': 'actual_b', 'initial_bark': 'start'})
        refs = references_for_entity(speaker, {'actual_b': {}, 'start': {}})
        self.assertEqual({block for block, _ in refs}, {'actual_b', 'start'})
        self.assertEqual(refs[-1][1]['rule'], 'named-dialogue-anchor')

    def test_story_namespace_needs_two_direct_references_and_a_story_tag(self):
        subtitles = {'pals_start': {}, 'pals_end': {}, 'pals_extra': {}}
        refs = {'pals_start': [{'rule': 'exact-reference'}], 'pals_end': [{'rule': 'exact-reference'}]}
        expand_story_namespaces([], refs, subtitles)
        self.assertNotIn('pals_extra', refs)
        expand_story_namespaces([entity('Settings', {'story_tag': 'skipping_pals'})], refs, subtitles)
        self.assertEqual(refs['pals_extra'][0]['supportingBlocks'], ['pals_end', 'pals_start'])

    def test_non_transform_group_keeps_world_coordinates_and_fast_travel_is_off_map(self):
        group = entity('Group', {'position.x': 100, 'is_existence_group': True}, 9)
        voice = entity('Voice_Log', {'name': 'scene', 'group_id': 9, 'position.x': 10}, 10)
        point = world_features([group, voice])[0]
        self.assertTrue(point['properties']['mapReady'])
        self.assertEqual(point['geometry']['coordinates'], [10, 0, 0])
        voice['fields']['position.z'] = 89
        point = world_features([group, voice])[0]
        self.assertEqual(point['properties']['mapExclusion'], 'outside-current-tiles')
        group['fields']['transform_group'] = True
        voice['fields']['position.z'] = 0
        self.assertFalse(world_features([group, voice])[0]['properties']['mapReady'])


class MediaTests(unittest.TestCase):
    def test_silence_does_not_make_a_fake_missing_recording(self):
        blocks = parse_subtitles(':: scene\n= warrior +0 1\nHello\n= priestess +0 1\n...\n')
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            wav_file(root / 'scene_1__warrior.wav')
            result = resolve_block('scene', {'en': blocks, 'pt-br': blocks}, root)
        self.assertEqual(len(result['clips']), 1)
        self.assertFalse(result['missingClips'])
        self.assertEqual(result['silentCues'][0]['id'], 'scene_2__priestess')

    def test_missing_real_media_is_reported_without_dropping_existing_dialogue(self):
        blocks = parse_subtitles(':: scene\n= warrior +0 1\nA\n= magistrate +0 1\nB\n')
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            wav_file(root / 'scene_1__warrior.wav')
            result = resolve_block('scene', {'en': blocks}, root)
        self.assertEqual(len(result['clips']), 1)
        self.assertEqual(result['missingClips'][0]['id'], 'scene_2__magistrate')

    def test_translation_mismatch_never_attaches_text_to_the_wrong_clip(self):
        english = parse_subtitles(':: scene\n= warrior +0 1\nHello\n')
        translated = parse_subtitles(':: scene\n= magistrate +0 1\nWrong speaker\n')
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            wav_file(root / 'scene_1__warrior.wav')
            result = resolve_block('scene', {'en': english, 'pt-br': translated}, root)
        self.assertEqual(result['clips'][0]['transcripts']['pt-br'], [])
        self.assertIn('pt-br', result['translationIssues'])
        self.assertEqual(result['transcripts']['pt-br'], ['Wrong speaker'])

    def test_cache_requires_both_source_and_encoded_content_integrity(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source, output, stage = root / 'sources', root / 'output', root / 'stage'
            source.mkdir()
            wav_file(source / 'scene.wav')
            encoded = output / 'audio/clips/scene.mp3'
            encoded.parent.mkdir(parents=True)
            encoded.write_bytes(b'encoded')
            previous = {'audio/clips/scene.mp3': {
                'sourceSha256': digest(source / 'scene.wav'), 'profile': MEDIA_PROFILE,
                'sha256': digest(encoded), 'bytes': 7}}
            with patch('build_audio_catalog.subprocess.run') as run:
                _, _, changed = encode_clip('scene', source, output, stage, Path('ffmpeg'), previous)
                self.assertFalse(changed)
                run.assert_not_called()
            encoded.write_bytes(b'corrupt')
            with patch('build_audio_catalog.subprocess.run', side_effect=RuntimeError('conversion needed')):
                with self.assertRaisesRegex(RuntimeError, 'conversion needed'):
                    encode_clip('scene', source, output, stage, Path('ffmpeg'), previous)


class RegenerationTests(unittest.TestCase):
    def test_edited_obsolete_output_blocks_publication_and_is_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            file = root / 'audio/clips/old.mp3'
            file.parent.mkdir(parents=True)
            file.write_bytes(b'original')
            previous = {'files': {'audio/clips/old.mp3': {'sha256': digest(file)}}}
            file.write_bytes(b'user change')
            with self.assertRaisesRegex(ValueError, 'edited'):
                publish(root / 'stage', root, {'files': {}}, previous, {})
            self.assertEqual(file.read_bytes(), b'user change')


if __name__ == '__main__':
    unittest.main()
