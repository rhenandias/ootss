"""Compatibility inspection command; export_audio_catalog.py builds the full site.

Without --publish-with-ffmpeg, writes inspection.json only and leaves the current
catalog, media and map points intact. Publication uses the full automatic builder.
"""
import argparse
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from export_audio_catalog import ROOT, write_json
from build_audio_catalog import build


def voice_log_feature(source, entity_id, members):
    fields = {m['name']: m['value'] for m in members if 'name' in m}
    world = Path(source).stem == 'overworld'
    group = fields.get('group_id', 0)
    unknown = [m for m in members if 'name' not in m]
    return {
        'type': 'Feature',
        'geometry': {'type': 'Point', 'coordinates': [
            fields.get('position.' + axis, 0.0) for axis in 'xyz']},
        'properties': {
            'type': 'Voice_Log', 'id': entity_id, 'name': fields.get('name'),
            'source': source, 'sourceLevel': Path(source).stem,
            'coordinateSpace': 'world' if world else 'level-local',
            'mapReady': world and not group and not unknown,
            'groupId': group,
            'designIllustrationsOnly': fields.get('design_illustrations_only', False),
            'author': fields.get('author'), 'unknownMembers': len(unknown),
        },
    }



def discover(extracted_root, package, output_root, schema=None, ffmpeg=None):
    report = build(extracted_root, package, output_root, ROOT / 'data/markers.json',
                   ffmpeg, schema, inspect_only=ffmpeg is None)
    if ffmpeg is None:
        write_json(output_root / 'data/audio/inspection.json', report)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--extracted-root', type=Path, required=True)
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--schema', type=Path)
    parser.add_argument('--output-root', type=Path, default=ROOT)
    parser.add_argument('--publish-with-ffmpeg', type=Path)
    args = parser.parse_args()
    discover(args.extracted_root, args.package, args.output_root, args.schema, args.publish_with_ffmpeg)
