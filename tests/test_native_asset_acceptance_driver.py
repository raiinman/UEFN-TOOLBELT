"""Offline checks for the reviewed local asset acceptance script."""
import json
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

BASE = Path(__file__).resolve().parents[1] / 'docs/audits/evidence/2026-10-09-toolbelt-acceptance'
SCRIPT = BASE / 'run_native_assets.py'


def driver_fixture(tmp_path, monkeypatch, failure=None):
    mount = 'fixture-mount'
    project = tmp_path / 'ToolbeltAcceptance'
    texture_file = project / 'Content/AcceptanceFixtures/Textures/T_Acceptance.uasset'
    sound_file = project / 'Content/AcceptanceFixtures/Audio/SW_Acceptance.uasset'
    texture_file.parent.mkdir(parents=True)
    sound_file.parent.mkdir(parents=True)
    texture_file.write_bytes(b'fixture saved texture')
    sound_file.write_bytes(b'fixture saved sound')
    fixture_root = '/' + mount + '/AcceptanceFixtures'

    class Texture:
        def __init__(self):
            self.props = {'srgb':True, 'compression_settings':0, 'lod_group':0, 'mip_gen_settings':0}

        def get_path_name(self): return fixture_root + '/Textures/T_Acceptance.T_Acceptance'
        def get_class(self): return SimpleNamespace(get_name=lambda: 'Texture2D')
        def blueprint_get_size_x(self):
            if failure == 'dimensions_unavailable': raise RuntimeError('fixture getter unavailable')
            return 32
        def blueprint_get_size_y(self):
            if failure == 'dimensions_unavailable': raise RuntimeError('fixture getter unavailable')
            return 32
        def get_editor_property(self, name): return self.props[name]

    class Sound:
        def get_path_name(self): return fixture_root + '/Audio/SW_Acceptance.SW_Acceptance'
        def get_editor_property(self, name):
            return {'duration':0.1, 'num_channels':1, 'sample_rate':22050,
                    'sample_rate_override':22050, 'sound_class_object':None}[name]

    texture = Texture()
    sound = Sound()
    unreal = ModuleType('unreal')
    unreal.Texture2D = Texture
    unreal.SoundWave = Sound
    unreal.TextureCompressionSettings = SimpleNamespace(TC_DEFAULT=0, TC_MASKS=1, TC_EDITOR_ICON=2,
                                                        TC_NORMALMAP=3, TC_HDR=4, TC_GRAYSCALE=5)
    unreal.TextureGroup = SimpleNamespace(TEXTUREGROUP_WORLD=0, TEXTUREGROUP_UI=1, TEXTUREGROUP_WORLD_NORMAL_MAP=2)
    unreal.TextureMipGenSettings = SimpleNamespace(TMGS_FROM_TEXTURE_GROUP=0, TMGS_NO_MIPMAPS=1)
    unreal.EditorAssetLibrary = SimpleNamespace(load_asset=lambda path: sound if '/Audio/' in path else texture,
                                                does_asset_exist=lambda _: False)
    unreal.SystemLibrary = SimpleNamespace(get_engine_version=lambda: 'fixture-engine')
    unreal.log = lambda *_: None
    tb = ModuleType('UEFN_Toolbelt')
    tb.__tool_count__ = 362
    tb.registry = SimpleNamespace(list_tools=lambda: [None] * 362)
    tools = ModuleType('UEFN_Toolbelt.tools')
    core = ModuleType('UEFN_Toolbelt.core')
    core.native_project_dir = lambda: str(project)
    suite = ModuleType('UEFN_Toolbelt.tools.integration_test')
    identity = {'mount':mount, 'project_dir':str(project), 'world_path':'/' + mount + '/Map.Map'}
    suite._acceptance_identity = lambda: dict(identity)
    suite._integration_running = False
    tb.core = core
    tb.tools = tools
    tools.integration_test = suite
    texture_module = ModuleType('UEFN_Toolbelt.tools.texture_tools')
    sound_module = ModuleType('UEFN_Toolbelt.tools.sound_asset_tools')
    tools.texture_tools = texture_module
    tools.sound_asset_tools = sound_module
    for module in (tb, core, suite, texture_module, sound_module):
        module.__file__ = str(tmp_path / (module.__name__ + '.py'))
        Path(module.__file__).write_text('# fixture source', encoding='utf-8')
    for name, module in [('unreal', unreal), ('UEFN_Toolbelt', tb), ('UEFN_Toolbelt.core', core),
                         ('UEFN_Toolbelt.tools', tools), ('UEFN_Toolbelt.tools.integration_test', suite),
                         ('UEFN_Toolbelt.tools.texture_tools', texture_module),
                         ('UEFN_Toolbelt.tools.sound_asset_tools', sound_module)]:
        monkeypatch.setitem(sys.modules, name, module)
    driver = {'__name__':'reviewed_local_driver'}
    exec(compile(SCRIPT.read_text(encoding='utf-8'), str(SCRIPT), 'exec'), driver)
    script_copy = tmp_path / 'run_native_assets.py'
    script_copy.write_bytes(SCRIPT.read_bytes())
    driver['SCRIPT_PATH'] = script_copy
    driver['OUTPUT'] = tmp_path / 'native-assets-r2'
    plan = json.loads((BASE / 'safe-additional-calls.json').read_text())
    original_mount = plan['target']['mount']
    plan = json.loads(json.dumps(plan).replace(original_mount, mount))
    (tmp_path / 'safe-additional-calls.json').write_text(json.dumps(plan))
    calls = []

    def run(tool, **kwargs):
        calls.append((tool, kwargs))
        if tool == 'anim_create_montage': return {'status':'error', 'reason':'invalid_fixture'}
        if tool == 'sound_asset_list': return {'status':'ok', 'sounds':[{'name':'SW_Acceptance'}], 'count':1}
        if tool == 'sound_asset_audit': return {'status':'ok', 'total':1, 'clean':0, 'unknown':0,
                                              'issue_list':[{'issues':['No SoundClass assigned']}]}
        if tool in ['texture_set_srgb', 'texture_set_compression', 'texture_set_group', 'texture_apply_preset']:
            before = dict(texture.props)
            target = dict(before)
            if tool == 'texture_set_srgb': target['srgb'] = kwargs['srgb']
            if tool == 'texture_set_compression':
                target['compression_settings'] = getattr(unreal.TextureCompressionSettings,
                                                          'TC_EDITOR_ICON' if kwargs['compression']=='TC_UI' else kwargs['compression'])
            if tool == 'texture_set_group':
                target['lod_group'] = getattr(unreal.TextureGroup, 'TEXTUREGROUP_' + kwargs['group'].upper())
            if tool == 'texture_apply_preset':
                comp, group, srgb, mip = driver['PRESETS'][kwargs['preset']]
                target.update(compression_settings=getattr(unreal.TextureCompressionSettings, comp),
                              lod_group=getattr(unreal.TextureGroup, group), srgb=srgb,
                              mip_gen_settings=getattr(unreal.TextureMipGenSettings, mip))
            requested = {prop for prop in target if target[prop] != before[prop]}
            if tool == 'texture_set_compression' and kwargs['compression'] == 'TC_MASKS' and target['compression_settings'] != before['compression_settings']:
                target['srgb'] = False
            if not kwargs['dry_run'] and failure != 'false_success':
                texture.props = target
                texture_file.write_text(json.dumps(target))
            if failure == 'identity_switch': identity['mount'] = 'another-project'
            actual_after = texture.props
            implicit = [{'name':'T_Acceptance', 'property':prop,
                         'from':before[prop] if isinstance(before[prop], bool) else str(before[prop]),
                         'to':actual_after[prop] if isinstance(actual_after[prop], bool) else str(actual_after[prop])}
                        for prop in before if prop not in requested and before[prop] != actual_after[prop]]
            return {'status':'ok', 'errors':[], 'changed':int(before != target),
                    'implicit_changes': [] if failure == 'omit_implicit' else implicit, 'unknown_reads':[]}
        return {'status':'ok', 'count':0}

    tb.run = run
    return driver, calls, texture


def test_real_property_oracles_and_negative_boundaries_are_recorded(tmp_path, monkeypatch):
    driver, calls, _ = driver_fixture(tmp_path, monkeypatch)
    result = driver['main']()
    assert result['completed'] is True
    assert result['fatal'] == ''
    assert all(check['passed'] for check in result['checks'])
    assert len(calls) == 50
    assert len(result['calls']) == 50
    assert len([call for call in calls if call[0]=='anim_create_montage']) == 2
    assert result['texture_dimensions']['values'] == {'x':32, 'y':32}
    assert result['texture_dimensions']['class'] == 'Texture2D'
    assert result['sound_readback']['properties']['duration'] == 0.1
    assert any(check['detail'].get('kind') == 'no_op_verified'
               for check in result['checks'] if isinstance(check['detail'], dict))
    assert len([call for call in calls if call[0]=='texture_apply_preset' and not call[1]['dry_run']]) == 7
    persisted = json.loads((driver['OUTPUT'] / 'run.json').read_text())
    assert persisted['script_sha256'] and persisted['runtime_sources']


def test_reported_success_without_property_change_never_passes_oracle(tmp_path, monkeypatch):
    driver, _, _ = driver_fixture(tmp_path, monkeypatch, failure='false_success')
    result = driver['main']()
    # Completion records that the script reached the end; it does not mean checks passed.
    assert result['completed'] is True
    assert any(not check['passed'] for check in result['checks'])
    assert any(check['name']=='texture_set_srgb native property readback' and not check['passed']
               for check in result['checks'])


def test_identity_switch_stops_before_next_operation_without_retry(tmp_path, monkeypatch):
    driver, calls, _ = driver_fixture(tmp_path, monkeypatch, failure='identity_switch')
    result = driver['main']()
    assert result['completed'] is False
    assert 'identity changed' in result['fatal']
    assert len(calls) == 1
    assert len(result['calls']) == 1


def test_existing_output_is_preserved_without_any_native_call(tmp_path, monkeypatch):
    driver, calls, _ = driver_fixture(tmp_path, monkeypatch)
    driver['OUTPUT'].mkdir()
    preserved = driver['OUTPUT'] / 'run.json'
    preserved.write_bytes(b'existing raw evidence')
    with pytest.raises(ValueError, match='Preserve previous asset evidence'):
        driver['main']()
    assert preserved.read_bytes() == b'existing raw evidence'
    assert calls == []


def test_unavailable_dimension_getters_remain_unknown_without_aborting_mutations(tmp_path, monkeypatch):
    driver, calls, _ = driver_fixture(tmp_path, monkeypatch, failure='dimensions_unavailable')
    result = driver['main']()
    assert result['completed'] is True
    assert len(calls) == 50
    assert result['texture_dimensions']['values'] == {}
    assert set(result['texture_dimensions']['unknown']) == {'x', 'y'}
    assert result['observations'][0]['disposition'] == 'unknown'
    assert not any(check['name']=='Texture2D imported dimensions' for check in result['checks'])


def test_unreported_native_side_effect_fails_even_when_requested_properties_match(tmp_path, monkeypatch):
    driver, _, _ = driver_fixture(tmp_path, monkeypatch, failure='omit_implicit')
    result = driver['main']()
    assert result['completed'] is True
    assert any(check['name']=='texture_set_compression native property readback' and not check['passed']
               and check['detail']['properties_match'] is True
               and check['detail']['implicit_changes_match'] is False for check in result['checks'])
