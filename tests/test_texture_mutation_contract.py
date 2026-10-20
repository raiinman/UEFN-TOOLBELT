"""Texture mutation refuses partial presets and proves property/save outcomes offline."""
from contextlib import nullcontext
from enum import Enum
from types import SimpleNamespace

import pytest

from UEFN_Toolbelt.tools import texture_tools as mod


class Compression(Enum):
    TC_DEFAULT = 0
    TC_MASKS = 1
    TC_EDITOR_ICON = 2


class Group(Enum):
    TEXTUREGROUP_WORLD = 0
    TEXTUREGROUP_UI = 1


class Mips(Enum):
    TMGS_FROM_TEXTURE_GROUP = 0
    TMGS_NO_MIPMAPS = 1


class Texture:
    def __init__(self):
        self.props = {'compression_settings': Compression.TC_DEFAULT,
                          'lod_group': Group.TEXTUREGROUP_WORLD, 'srgb': True,
                          'mip_gen_settings': Mips.TMGS_FROM_TEXTURE_GROUP}
        self.writes = []
        self.refuse = False
        self.raise_setter = False

    def get_editor_property(self, prop):
        return self.props[prop]

    def set_editor_property(self, prop, value):
        self.writes.append((prop, value))
        if self.raise_setter:
            raise RuntimeError('read-only texture')
        if not self.refuse:
            self.props[prop] = value


@pytest.fixture
def texture(monkeypatch):
    tex = Texture()
    asset = SimpleNamespace(asset_name='T_Test', package_name='/Fixture/T_Test')
    monkeypatch.setattr(mod.unreal, 'Texture2D', Texture)
    monkeypatch.setattr(mod.unreal, 'TextureCompressionSettings', Compression)
    monkeypatch.setattr(mod.unreal, 'TextureGroup', Group)
    monkeypatch.setattr(mod.unreal, 'TextureMipGenSettings', Mips)
    monkeypatch.setattr(mod.unreal.EditorAssetLibrary, 'load_asset', lambda _: tex)
    monkeypatch.setattr(mod, '_load_textures_in_folder', lambda _: [asset])
    monkeypatch.setattr(mod, 'resolve_scan_path', lambda _: '/Fixture')
    monkeypatch.setattr(mod, 'undo_transaction', lambda _: nullcontext())
    monkeypatch.setattr(mod, 'save_loaded_asset', lambda *_: True)
    return tex


@pytest.mark.parametrize('function,args,prop,value', [
    (mod.run_texture_set_compression, {'compression':'TC_UI'}, 'compression_settings', Compression.TC_EDITOR_ICON),
    (mod.run_texture_set_group, {'group':'ui'}, 'lod_group', Group.TEXTUREGROUP_UI),
    (mod.run_texture_set_srgb, {'srgb':False}, 'srgb', False),
])
def test_setter_uses_actual_enum_and_reads_back(texture, function, args, prop, value):
    result = function(dry_run=False, **args)
    assert result['status'] == 'ok'
    assert result['changed'] == 1
    assert result['errors'] == []
    assert texture.props[prop] == value
    again = function(dry_run=False, **args)
    assert again['changed'] == 0
    assert again['skipped'] == 1


def test_complete_ui_preset_and_noop(texture):
    result = mod.run_texture_apply_preset(preset='ui', dry_run=False)
    assert result['status'] == 'ok'
    assert result['changed'] == 1
    assert texture.props == {'compression_settings': Compression.TC_EDITOR_ICON,
                                'lod_group': Group.TEXTUREGROUP_UI, 'srgb': True,
                                'mip_gen_settings': Mips.TMGS_NO_MIPMAPS}
    assert mod.run_texture_apply_preset(preset='ui', dry_run=False)['skipped'] == 1


@pytest.mark.parametrize('dry_run', [True, False])
def test_missing_preset_enum_refuses_before_any_property_write(texture, monkeypatch, dry_run):
    monkeypatch.setattr(mod.unreal, 'TextureMipGenSettings', SimpleNamespace())
    result = mod.run_texture_apply_preset(preset='ui', dry_run=dry_run)
    assert result['status'] == 'error'
    assert result['changed'] == 0
    assert 'TMGS_NO_MIPMAPS' in result['message']
    assert texture.writes == []


def test_dry_run_reads_existing_values_without_writes_or_save(texture, monkeypatch):
    monkeypatch.setattr(mod, 'save_loaded_asset', lambda *_: pytest.fail('dry run saved'))
    result = mod.run_texture_apply_preset(preset='ui', dry_run=True)
    assert result['status'] == 'ok'
    assert result['changed'] == 1
    assert texture.writes == []


@pytest.mark.parametrize('failure', ['setter', 'readback', 'save'])
@pytest.mark.parametrize('function,args', [
    (mod.run_texture_set_srgb, {'srgb':False}),
    (mod.run_texture_apply_preset, {'preset':'ui'}),
])
def test_failures_are_errors_and_not_changes(texture, monkeypatch, failure, function, args):
    if failure == 'setter': texture.raise_setter = True
    if failure == 'readback': texture.refuse = True
    if failure == 'save': monkeypatch.setattr(mod, 'save_loaded_asset', lambda *_: False)
    result = function(dry_run=False, **args)
    assert result['status'] == 'error'
    assert result['changed'] == 0
    assert len(result['errors']) == 1
    assert result['errors'][0]['may_have_changed'] is True


def test_unloaded_asset_is_an_error(texture, monkeypatch):
    monkeypatch.setattr(mod.unreal.EditorAssetLibrary, 'load_asset', lambda _: None)
    result = mod.run_texture_set_srgb(srgb=False, dry_run=False)
    assert result['status'] == 'error'
    assert result['changed'] == 0
    assert result['errors']


def test_native_compression_side_effect_is_reported_without_hiding_requested_delta(texture, monkeypatch):
    original_setter = texture.set_editor_property

    def native_setter(prop, value):
        original_setter(prop, value)
        if prop == 'compression_settings' and value == Compression.TC_MASKS:
            texture.props['srgb'] = False  # Native42.30 observed automatic adjustment.

    monkeypatch.setattr(texture, 'set_editor_property', native_setter)
    result = mod.run_texture_set_compression(compression='TC_MASKS', dry_run=False)
    assert result['status'] == 'ok'
    assert result['changed'] == 1
    assert result['changes'][0]['from'] == str(Compression.TC_DEFAULT)
    assert result['changes'][0]['to'] == str(Compression.TC_MASKS)
    assert result['implicit_changes'] == [{'name':'T_Test', 'property':'srgb', 'from':True, 'to':False}]
    assert result['property_observations'][0]['before']['srgb'] is True
    assert result['property_observations'][0]['after']['srgb'] is False
    assert result['unknown_reads'] == []


def test_save_coercion_of_requested_property_is_an_error(texture, monkeypatch):
    def coerce_on_save(*_):
        texture.props['compression_settings'] = Compression.TC_DEFAULT
        return True

    monkeypatch.setattr(mod, 'save_loaded_asset', coerce_on_save)
    result = mod.run_texture_set_compression(compression='TC_MASKS', dry_run=False)
    assert result['status'] == 'error'
    assert result['changed'] == 0
    assert result['errors'][0]['may_have_changed'] is True
    assert 'after saving' in result['errors'][0]['error']
    assert result['property_observations'][0]['after']['compression_settings'] == str(Compression.TC_DEFAULT)


def test_unrequested_unreadable_properties_remain_explicit_unknowns(texture, monkeypatch):
    original_getter = texture.get_editor_property

    def limited_getter(prop):
        if prop == 'lod_group': raise AttributeError('fixture lod_group unavailable')
        return original_getter(prop)

    monkeypatch.setattr(texture, 'get_editor_property', limited_getter)
    result = mod.run_texture_set_srgb(srgb=False, dry_run=False)
    assert result['status'] == 'ok'
    assert result['changed'] == 1
    assert [(item['stage'], item['property']) for item in result['unknown_reads']] == [
        ('before', 'lod_group'), ('after_attempt', 'lod_group')]
    assert 'lod_group' not in result['property_observations'][0]['before']
    assert 'lod_group' not in result['property_observations'][0]['after']
