"""Reviewed local-console asset acceptance. Requires native disposable PNG/WAV imports.

Run only after the section driver has finished. This script has no Slate callback,
remote command, network action, world mutation, asset deletion or automatic retry.
"""
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import unreal

import UEFN_Toolbelt as tb
from UEFN_Toolbelt.tools import integration_test as suite

SCRIPT_PATH = Path('C:/Users/mikea/Documents/MCP/UEFN-TOOLBELT/docs/audits/evidence/2026-10-09-toolbelt-acceptance/run_native_assets.py')
OUTPUT = SCRIPT_PATH.parent / 'native-assets-r2'
PROPERTIES = ('srgb', 'compression_settings', 'lod_group', 'mip_gen_settings')
PRESETS = {
    'game': ('TC_DEFAULT', 'TEXTUREGROUP_WORLD', True, 'TMGS_FROM_TEXTURE_GROUP'),
    'ui': ('TC_EDITOR_ICON', 'TEXTUREGROUP_UI', True, 'TMGS_NO_MIPMAPS'),
    'normal': ('TC_NORMALMAP', 'TEXTUREGROUP_WORLD_NORMAL_MAP', False, 'TMGS_FROM_TEXTURE_GROUP'),
    'mask': ('TC_MASKS', 'TEXTUREGROUP_WORLD', False, 'TMGS_FROM_TEXTURE_GROUP'),
    'hdr': ('TC_HDR', 'TEXTUREGROUP_WORLD', False, 'TMGS_FROM_TEXTURE_GROUP'),
    'icon': ('TC_EDITOR_ICON', 'TEXTUREGROUP_UI', True, 'TMGS_NO_MIPMAPS'),
    'grayscale': ('TC_GRAYSCALE', 'TEXTUREGROUP_WORLD', False, 'TMGS_FROM_TEXTURE_GROUP'),
}


def main():
    if OUTPUT.exists():
        raise ValueError('Preserve previous asset evidence and choose a fresh output directory.')
    identity = suite._acceptance_identity()
    if getattr(suite, '_integration_running', False):
        raise ValueError('Wait for the integration section driver to finish.')
    mount = '/' + identity['mount']
    fixtures = mount + '/AcceptanceFixtures'
    texture_path = fixtures + '/Textures/T_Acceptance'
    sound_path = fixtures + '/Audio/SW_Acceptance'
    from UEFN_Toolbelt import core
    project = Path(core.native_project_dir()).resolve()
    output_state = {'schema_version': 1, 'identity': identity,
                    'started_at_utc': datetime.now(UTC).isoformat(),
                    'script_sha256': hashlib.sha256(SCRIPT_PATH.read_bytes()).hexdigest(),
                    'runtime_sources': {}, 'declared_tools': tb.__tool_count__,
                    'registered_tools': len(tb.registry.list_tools()),
                    'calls': [], 'checks': [], 'native_readbacks': [],
                    'availability': {}, 'completed': False, 'fatal': '',
                    'limitation': 'Exact calls and scoped independent reads only. Empty lists and native-unavailable refusals are boundaries. load_asset may return cached objects; this script does not prove post-restart persistence or animation playback.'}
    OUTPUT.mkdir(parents=True)

    def flush():
        temporary = OUTPUT / 'run.json.tmp'
        temporary.write_text(json.dumps(output_state, indent=2, default=str), encoding='utf-8')
        temporary.replace(OUTPUT / 'run.json')

    def guard():
        if suite._acceptance_identity() != identity or Path(core.native_project_dir()).resolve() != project:
            raise ValueError('Native disposable project identity changed; stop without retry.')
        if getattr(suite, '_integration_running', False):
            raise ValueError('Integration harness is active; stop without retry.')

    def check(name, passed, detail):
        output_state['checks'].append({'name': name, 'passed': bool(passed), 'detail': detail})
        flush()

    def call(tool, **kwargs):
        guard()
        entry = {'tool': tool, 'kwargs': kwargs}
        output_state['current_call'] = entry
        flush()
        try:
            entry['result'] = tb.run(tool, **kwargs)
            return entry['result']
        except Exception as exc:
            entry['raised'] = str(exc)
            raise
        finally:
            output_state['calls'].append(entry)
            output_state['current_call'] = None
            flush()

    def enum(enum_type, member):
        return getattr(getattr(unreal, enum_type, None), member, None)

    def texture_state():
        guard()
        asset = unreal.EditorAssetLibrary.load_asset(texture_path)
        if not isinstance(asset, unreal.Texture2D):
            raise ValueError('Named PNG fixture is not a readable native Texture2D.')
        if asset.get_path_name() != texture_path + '.T_Acceptance':
            raise ValueError('Loaded texture does not match the exact fixture object path.')
        values = {prop: asset.get_editor_property(prop) for prop in PROPERTIES}
        file = project / 'Content/AcceptanceFixtures/Textures/T_Acceptance.uasset'
        if not file.resolve().is_relative_to(project) or not file.is_file():
            raise ValueError('Named texture has no contained native saved .uasset file.')
        observed = {'object_path': asset.get_path_name(), 'class': asset.get_class().get_name(),
                    'properties': {key: value if isinstance(value, bool) else str(value)
                                   for key, value in values.items()},
                    'saved_file': str(file), 'saved_file_sha256': hashlib.sha256(file.read_bytes()).hexdigest(),
                    'saved_file_bytes': file.stat().st_size}
        output_state['native_readbacks'].append(observed)
        flush()
        return values

    def mutate(tool, expected, unavailable=(), implicit_expected=None, **kwargs):
        before = texture_state()
        result = call(tool, scan_path=fixtures + '/Textures', dry_run=False, **kwargs)
        after = texture_state()
        if unavailable:
            check(tool + ' unavailable preflight', isinstance(result, dict) and result.get('status') == 'error'
                  and result.get('changed') == 0 and before == after,
                  {'missing': list(unavailable), 'state_unchanged': before == after})
            return
        expected_after = dict(before, **expected)
        expected_changes = int(any(before[prop] != value for prop, value in expected.items()))
        if implicit_expected and expected_changes:
            expected_after.update(implicit_expected)
        actual_implicit = {prop: (before[prop] if isinstance(before[prop], bool) else str(before[prop]),
                                  after[prop] if isinstance(after[prop], bool) else str(after[prop]))
                           for prop in PROPERTIES if prop not in expected and before[prop] != after[prop]}
        reported_implicit = {item.get('property'): (item.get('from'), item.get('to'))
                             for item in result.get('implicit_changes', [])} if isinstance(result, dict) else {}
        implicit_matches = (isinstance(result, dict) and 'implicit_changes' in result
                            and reported_implicit == actual_implicit and result.get('unknown_reads') == [])
        passed = (isinstance(result, dict) and result.get('status') == 'ok'
                  and result.get('errors') == [] and result.get('changed') == expected_changes
                  and after == expected_after and implicit_matches)
        check(tool + ' native property readback', passed,
              {'requested': {k: v if isinstance(v, bool) else str(v) for k, v in expected.items()},
               'expected_changed': expected_changes, 'reported_changed': result.get('changed') if isinstance(result, dict) else None,
               'properties_match': after == expected_after, 'implicit_changes_match': implicit_matches,
               'actual_implicit_changes': actual_implicit, 'reported_implicit_changes': reported_implicit,
               'kind': 'no_op_verified' if not expected_changes else 'state_delta_verified'})

    try:
        guard()
        for module in (tb, core, suite):
            path = Path(module.__file__)
            output_state['runtime_sources'][module.__name__] = hashlib.sha256(path.read_bytes()).hexdigest()
        from UEFN_Toolbelt.tools import sound_asset_tools, texture_tools
        for module in (sound_asset_tools, texture_tools):
            output_state['runtime_sources'][module.__name__] = hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()
        output_state['availability'] = {name: getattr(unreal, name, None) is not None
                                        for name in ('Texture2D', 'SoundWave', 'AnimSequence', 'Skeleton',
                                                     'AnimMontage', 'AnimMontageFactory', 'InputActionFactory')}
        try:
            output_state['engine_version'] = unreal.SystemLibrary.get_engine_version()
        except Exception as exc:
            output_state['engine_version_unavailable'] = str(exc)
        flush()
        original = texture_state()
        texture_fixture = unreal.EditorAssetLibrary.load_asset(texture_path)
        dimensions = {"class": texture_fixture.get_class().get_name(),
                      "object_path": texture_fixture.get_path_name(), "expected": [32, 32],
                      "values": {}, "unknown": {}}
        for axis in ("x", "y"):
            method_name = "blueprint_get_size_" + axis
            getter = getattr(texture_fixture, method_name, None)
            try:
                if not callable(getter):
                    raise ValueError("Documented dimension getter is unavailable")
                dimensions["values"][axis] = getter()
            except Exception as exc:
                dimensions["unknown"][axis] = str(exc)
        output_state["texture_dimensions"] = dimensions
        if not dimensions["unknown"]:
            check("Texture2D imported dimensions", dimensions["values"] == {"x": 32, "y": 32}, dimensions)
        else:
            output_state["observations"] = [{"name": "Texture2D imported dimensions",
                                               "disposition": "unknown", "detail": dimensions}]
            flush()
        # Both supplied imports must exist before any fixture property mutation.
        sound_fixture = unreal.EditorAssetLibrary.load_asset(sound_path)
        sound_saved = project / 'Content/AcceptanceFixtures/Audio/SW_Acceptance.uasset'
        if (not isinstance(sound_fixture, unreal.SoundWave)
                or sound_fixture.get_path_name() != sound_path + '.SW_Acceptance'
                or not sound_saved.resolve().is_relative_to(project) or not sound_saved.is_file()):
            raise ValueError('Named WAV fixture must be imported and saved before texture mutations.')
        mutate('texture_set_srgb', {'srgb': not original['srgb']}, srgb=not original['srgb'])
        mutate('texture_set_srgb', {'srgb': original['srgb']}, srgb=original['srgb'])
        mutate('texture_set_srgb', {'srgb': original['srgb']}, srgb=original['srgb'])
        for tool, enum_type, member, prop, args in (
            ('texture_set_compression', 'TextureCompressionSettings', 'TC_MASKS', 'compression_settings', {'compression': 'TC_MASKS', 'max_assets': 5}),
            ('texture_set_compression', 'TextureCompressionSettings', 'TC_EDITOR_ICON', 'compression_settings', {'compression': 'TC_UI', 'max_assets': 5}),
            ('texture_set_group', 'TextureGroup', 'TEXTUREGROUP_UI', 'lod_group', {'group': 'ui'}),
            ('texture_set_group', 'TextureGroup', 'TEXTUREGROUP_WORLD', 'lod_group', {'group': 'world'}),
        ):
            value = enum(enum_type, member)
            side_effect = None
            if tool == 'texture_set_compression' and member == 'TC_MASKS' and value is not None:
                # Narrow expected native42.30 observation preserved in r1: masks disable sRGB.
                # Make the observed transition reproducible, rather than accepting any changed field.
                mutate('texture_set_srgb', {'srgb': True}, srgb=True)
                side_effect = {'srgb': False}
            mutate(tool, {prop: value}, unavailable=() if value is not None else (enum_type + '.' + member,),
                   implicit_expected=side_effect, **args)
        for preset, (comp, group, srgb, mip) in PRESETS.items():
            targets = {'compression_settings': enum('TextureCompressionSettings', comp),
                       'lod_group': enum('TextureGroup', group), 'srgb': srgb,
                       'mip_gen_settings': enum('TextureMipGenSettings', mip)}
            missing = [name for name, value in targets.items() if value is None]
            mutate('texture_apply_preset', targets, unavailable=missing, preset=preset)

        guard()
        sound = unreal.EditorAssetLibrary.load_asset(sound_path)
        if not isinstance(sound, unreal.SoundWave) or sound.get_path_name() != sound_path + '.SW_Acceptance':
            raise ValueError('Named WAV fixture is not an exact readable native SoundWave.')
        sound_read = {'object_path': sound.get_path_name(), 'properties': {}, 'unknown': {}}
        for prop in ('duration', 'num_channels', 'sample_rate', 'sample_rate_override', 'sound_class_object'):
            try:
                value = sound.get_editor_property(prop)
                sound_read['properties'][prop] = (value if value is None or isinstance(value, (str, float, int, bool))
                                                   else value.get_path_name())
            except Exception as exc:
                sound_read['unknown'][prop] = str(exc)
        sound_file = project / 'Content/AcceptanceFixtures/Audio/SW_Acceptance.uasset'
        sound_read['saved_file_exists'] = sound_file.is_file() and sound_file.resolve().is_relative_to(project)
        output_state['sound_readback'] = sound_read
        duration = sound_read['properties'].get('duration')
        check('SoundWave duration', isinstance(duration, (int, float)) and abs(duration - 0.1) < 0.01,
              {'duration': duration, 'expected_seconds': 0.1, 'unknown': sound_read['unknown']})
        listed = call('sound_asset_list', scan_path=fixtures + '/Audio', sound_type='wave', max_results=5)
        check('SoundWave named list fixture', isinstance(listed, dict) and any(
              item.get('name') == 'SW_Acceptance' for item in listed.get('sounds', [])),
              'Known fixture required; empty list is not positive acceptance.')
        audit = call('sound_asset_audit', scan_path=fixtures + '/Audio', warn_duration_sec=1.0, max_results=5)
        properties = sound_read['properties']
        if 'sound_class_object' in properties and properties['sound_class_object'] is None:
            check('SoundWave missing SoundClass issue', isinstance(audit, dict) and audit.get('total') == 1
                  and audit.get('clean') == 0 and any('No SoundClass assigned' in issue
                  for item in audit.get('issue_list', []) for issue in item.get('issues', [])),
                  'A native None SoundClass is a legitimate known issue, not a failed duration read.')
        if 'sound_class_object' not in properties:
            check('SoundWave unreadable SoundClass remains unknown', isinstance(audit, dict)
                  and audit.get('unknown', 0) > 0 and audit.get('clean') == 0,
                  'Unavailable native inspection must not count as clean.')

        for sequence, name in ((texture_path, 'AM_InvalidTexture'),
                               (fixtures + '/Animations/AS_Missing', 'AM_MissingSequence')):
            guard()
            destination = fixtures + '/Animations'
            absent_before = not unreal.EditorAssetLibrary.does_asset_exist(destination + '/' + name)
            result = call('anim_create_montage', sequence_path=sequence, destination=destination, name=name)
            absent_after = not unreal.EditorAssetLibrary.does_asset_exist(destination + '/' + name)
            check('Montage negative preflight ' + name, isinstance(result, dict) and result.get('status') == 'error'
                  and absent_before and absent_after,
                  'Invalid-class/missing-sequence or API-unavailable boundary only; no valid animation fixture/playback proof.')

        plan_path = SCRIPT_PATH.parent / 'safe-additional-calls.json'
        plan_bytes = plan_path.read_bytes()
        output_state['additional_plan_sha256'] = hashlib.sha256(plan_bytes).hexdigest()
        plan = json.loads(plan_bytes)
        allowed = {entry['tool'] for entry in plan['calls']}
        fixed_allowed = {'api_search', 'api_inspect', 'anim_list_skeletons', 'anim_list_sequences', 'anim_list_montages',
                         'anim_list_blend_spaces', 'audio_list_metasounds', 'audio_list_sound_classes', 'audio_list_sound_cues',
                         'audio_list_sound_mixes', 'audio_list_synesthesia', 'texture_audit', 'texture_set_compression',
                         'texture_set_group', 'texture_set_srgb', 'texture_apply_preset', 'sound_asset_list', 'sound_asset_audit',
                         'sound_attenuation_list', 'sound_class_list', 'blueprint_list', 'blueprint_audit', 'blueprint_inspect',
                         'curve_list', 'datatable_list', 'skel_list', 'skel_audit', 'input_list_actions', 'input_list_contexts',
                         'world_partition_status', 'data_layer_list'}
        if len(plan['calls']) != 31 or not allowed.issubset(fixed_allowed) or plan['target']['mount'] != identity['mount']:
            raise ValueError('Additional query plan changed its reviewed tool set or target.')
        for entry in plan['calls']:
            args = entry['kwargs']
            for key in ('scan_path', 'search_path', 'asset_path'):
                path = args.get(key)
                if path is not None and not (path == fixtures or path.startswith(fixtures + '/')):
                    raise ValueError('Additional query path left the reviewed fixture subtree.')
            if entry['tool'].startswith('texture_') and entry['tool'] != 'texture_audit' and args.get('dry_run') is not True:
                raise ValueError('Additional texture queries must remain previews.')
            before = texture_state() if args.get('dry_run') is True and entry['tool'].startswith('texture_') else None
            result = call(entry['tool'], **args)
            output_state['calls'][-1]['disposition'] = 'returned_only; interpret fixture prerequisite and independent readback separately'
            if before is not None:
                check(entry['tool'] + ' preview preserves state', texture_state() == before,
                      'Preview alone does not establish a persisted texture mutation.')
            flush()
        output_state['completed'] = True
        output_state['finished_at_utc'] = datetime.now(UTC).isoformat()
    except Exception as exc:
        output_state['fatal'] = str(exc)
        output_state['completed'] = False
    finally:
        flush()
    unreal.log('[ACCEPTANCE] Asset evidence written; completed=' + str(output_state['completed']))
    return output_state


if __name__ == '__main__':
    main()
