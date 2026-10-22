"""Focused tests for subtitle boundaries and the pilot's clip segmentation."""
import unittest
from io import BytesIO
from unittest.mock import patch
from export_audio_catalog import parse_subtitles, split_clips, clip_order_evidence, level_references
from discover_audio_logs import voice_log_feature


class SubtitleTests(unittest.TestCase):
    def test_header_variants_do_not_leak_into_previous_block(self):
        blocks = parse_subtitles("[1]\n::: a\n= warrior 0\nA\n:: b\n= warrior 0\nB\n: c\n= warrior 0\nC\n")
        self.assertEqual(list(blocks), ["a", "b", "c"])
        self.assertEqual(blocks["a"]["cues"][0]["textLines"], ["A"])

    def test_notes_commands_controls_and_audio_override(self):
        blocks = parse_subtitles("::: scene\n= warrior +0.0 5 ! reused_1__warrior\n++ quietly\n+ victory 2\n...Hello *there*.\n= warrior +2\nSecond line.\n= _ +0.0\n")
        clips = split_clips("scene", blocks["scene"])
        self.assertEqual(len(clips), 1)
        self.assertEqual(clips[0]["id"], "reused_1__warrior")
        self.assertEqual(clips[0]["chunks"], ["...Hello *there*.", "Second line."])
        self.assertEqual(clips[0]["cues"][0]["commands"], ["victory 2"])
        self.assertEqual(clips[0]["cues"][0]["notes"], ["quietly"])

    def test_duration_starts_another_clip_including_negative_offset(self):
        blocks = parse_subtitles("::: scene\n= warrior +0.0 5\nOne\n= magistrate -0.35 1\nTwo\n")
        clips = split_clips("scene", blocks["scene"])
        self.assertEqual([c["id"] for c in clips], ["scene_1__warrior", "scene_2__magistrate"])

    def test_unknown_and_ambiguous_input_is_rejected(self):
        for text in ["::: a\n::: a\n", ":::: a\n", "::: a\n= warrior unknown\n", "::: a\n= warrior 0 weird\n"]:
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_subtitles(text)
        blocks = parse_subtitles("::: scene\n= warrior 0\nOne\n= magistrate 2\nTwo\n")
        with self.assertRaisesRegex(ValueError, "Ambiguous"):
            split_clips("scene", blocks["scene"])


class ExtractionTests(unittest.TestCase):
    def test_absolute_voice_log_groups_speaker_runs(self):
        block = parse_subtitles(':: scene\n= warrior 0\nA\n= warrior 2\nB\n'
                                '= magistrate 4\nC\n= warrior 6\nD\n')['scene']
        clips = split_clips('scene', block, voice_log=True)
        self.assertEqual([c['id'] for c in clips],
                         ['scene_1__warrior', 'scene_2__magistrate', 'scene_3__warrior'])
        self.assertEqual(clips[0]['chunks'], ['A', 'B'])

    def test_inserted_voice_log_variant_does_not_shift_following_number(self):
        block = parse_subtitles(':: scene\n= warrior 0\nA\n'
                                '= warrior 2 ! scene_1a__warrior\nB\n'
                                '= magistrate 4\nC\n')['scene']
        clips = split_clips('scene', block, voice_log=True)
        self.assertEqual([c['id'] for c in clips],
                         ['scene_1__warrior', 'scene_1a__warrior', 'scene_2__magistrate'])

    def test_voice_log_can_start_with_unsubtitled_audio(self):
        block = parse_subtitles(':: scene\n= misc +0 4 ! credits\n= misc +1\nHello\n')['scene']
        self.assertEqual(split_clips('scene', block, voice_log=True)[0]['chunks'], ['Hello'])

    def test_decreasing_absolute_timestamps_are_not_guessed(self):
        block = parse_subtitles(':: scene\n= warrior 3\nA\n= magistrate 1\nB\n')['scene']
        with self.assertRaisesRegex(ValueError, 'Non-monotonic'):
            split_clips('scene', block, voice_log=True)

    def test_versioned_named_references_and_positions(self):
        members = [{'name': 'initial_bark', 'value': 'scene', 'member': 0x100E},
                   {'name': 'position.x', 'value': 12},
                   {'name': 'mesh', 'value': 'not_dialogue', 'member': 31}]
        with patch('export_audio_catalog.parse_entities', return_value=[(7, 'Guy', b'x', 34)]), \
             patch('export_audio_catalog.decode_diff', return_value=members) as decode:
            refs = level_references(BytesIO(b'x'), {'data-common/level.entities': (1, 0)}, 'level')
        decode.assert_called_once_with('Guy', b'x', 34)
        self.assertEqual(list(refs), ['scene'])
        self.assertEqual(refs['scene'][0]['coordinates'], [12, 0, 0])

    def test_local_positions_never_become_world_markers(self):
        members = [{'name': 'name', 'value': 'audiolog_test'},
                   {'name': 'position.x', 'value': 10}]
        local = voice_log_feature('data-common/test.entities', 1, members)
        world = voice_log_feature('data-common/overworld.entities', 1, members)
        grouped = voice_log_feature('data-common/overworld.entities', 1,
                                    members + [{'name': 'group_id', 'value': 5}])
        self.assertFalse(local['properties']['mapReady'])
        self.assertTrue(world['properties']['mapReady'])
        self.assertFalse(grouped['properties']['mapReady'])

    def test_numeric_check_uses_numbers_and_allows_gaps(self):
        clips = [{'id': f'scene_{i}__warrior'} for i in [1, 3, 10]]
        self.assertEqual(clip_order_evidence(clips)['filenameCheck'], 'agrees')

    def test_explicit_references_keep_subtitle_order_even_with_reset_numbers(self):
        block = parse_subtitles('::: scene\n= warrior 0 2 ! reused_3__warrior\nA\n'
                                '= magistrate 0 2 ! reused_1__magistrate\nB\n')['scene']
        clips = split_clips('scene', block)
        self.assertEqual([c['id'] for c in clips], ['reused_3__warrior', 'reused_1__magistrate'])
        self.assertEqual(clip_order_evidence(clips)['filenameCheck'], 'needs-review')


if __name__ == "__main__":
    unittest.main()
