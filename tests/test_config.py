"""
Tests for the persistent config store (core/config.py).
==============================================================================
Config survives install.py updates and backs every `config_*` tool, so its
defaults-vs-overrides precedence and its on-disk round-trip are worth pinning.
"""

from __future__ import annotations

import json

import pytest

from UEFN_Toolbelt.core.config import DEFAULTS, Config


@pytest.fixture
def cfg(tmp_path):
    """A Config bound to a throwaway file — never touches the real Saved/ dir."""
    return Config(str(tmp_path / "UEFN_Toolbelt" / "config.json"))


# ── Precedence: user value → DEFAULTS → fallback ──────────────────────────────

def test_get_returns_default_when_unset(cfg):
    assert cfg.get("scatter.default_folder") == DEFAULTS["scatter.default_folder"]


def test_get_returns_fallback_for_unknown_key(cfg):
    assert cfg.get("no.such.key", fallback="sentinel") == "sentinel"


def test_get_returns_none_for_unknown_key_without_fallback(cfg):
    assert cfg.get("no.such.key") is None


def test_user_value_overrides_default(cfg):
    cfg.set("scatter.default_folder", "MyScatter")
    assert cfg.get("scatter.default_folder") == "MyScatter"


# ── Persistence ───────────────────────────────────────────────────────────────

def test_set_persists_to_disk(cfg, tmp_path):
    cfg.set("scatter.default_count", 123)
    written = json.loads((tmp_path / "UEFN_Toolbelt" / "config.json").read_text(encoding="utf-8"))
    assert written["scatter.default_count"] == 123


def test_value_survives_a_new_instance(cfg, tmp_path):
    cfg.set("text.default_color", "#ABCDEF")
    reopened = Config(str(tmp_path / "UEFN_Toolbelt" / "config.json"))
    assert reopened.get("text.default_color") == "#ABCDEF"


def test_corrupt_config_file_does_not_raise(tmp_path):
    """A hand-edited/truncated config must degrade to defaults, not crash the editor."""
    path = tmp_path / "UEFN_Toolbelt" / "config.json"
    path.parent.mkdir(parents=True)
    path.write_text("{ this is not json", encoding="utf-8")

    cfg = Config(str(path))
    assert cfg.get("scatter.default_folder") == DEFAULTS["scatter.default_folder"]


# ── reset / is_default / all ──────────────────────────────────────────────────

def test_reset_restores_the_default(cfg):
    cfg.set("scatter.default_radius", 9999.0)
    assert cfg.reset("scatter.default_radius") is True
    assert cfg.get("scatter.default_radius") == DEFAULTS["scatter.default_radius"]


def test_reset_returns_false_when_key_was_never_set(cfg):
    assert cfg.reset("scatter.default_radius") is False


def test_is_default_tracks_customisation(cfg):
    assert cfg.is_default("text.default_size") is True
    cfg.set("text.default_size", 250.0)
    assert cfg.is_default("text.default_size") is False
    cfg.reset("text.default_size")
    assert cfg.is_default("text.default_size") is True


def test_all_merges_defaults_with_overrides(cfg):
    cfg.set("scatter.default_count", 7)
    merged = cfg.all()
    assert merged["scatter.default_count"] == 7                      # override wins
    assert merged["arena.fallback_mesh"] == DEFAULTS["arena.fallback_mesh"]
    assert set(DEFAULTS).issubset(merged)                            # nothing dropped


def test_all_returns_a_copy_not_the_live_dict(cfg):
    snapshot = cfg.all()
    snapshot["scatter.default_count"] = -1
    assert cfg.get("scatter.default_count") == DEFAULTS["scatter.default_count"]


def _native_fixture(tmp_path, monkeypatch, name='Island'):
    from UEFN_Toolbelt import core
    from UEFN_Toolbelt.core import config
    root = tmp_path / name
    package = root / 'Content/Python/UEFN_Toolbelt/core'
    package.mkdir(parents=True)
    (root / f'{name}.uefnproject').write_text(json.dumps({
        'plugins': [{'name': f'uuid-{name}', 'bIsRoot': True}]}), encoding='utf-8')
    monkeypatch.setattr(core, '__file__', str(package / '__init__.py'))
    monkeypatch.setattr(config, '_config_instance', None)
    return root, config


def test_project_config_migrates_settings_but_not_other_islands_paths(tmp_path, monkeypatch):
    import unreal
    root, config = _native_fixture(tmp_path, monkeypatch)
    legacy_saved = tmp_path / 'SharedSaved'
    legacy_file = legacy_saved / 'UEFN_Toolbelt/config.json'
    legacy_file.parent.mkdir(parents=True)
    other = tmp_path / 'Riftbloom/Content'
    other.mkdir(parents=True)
    original = {'ui.theme':'custom_theme', 'scatter.default_count':7,
                'verse.project_path':str(other), 'import.default_dir':'/uuid-Riftbloom/Textures'}
    legacy_file.write_text(json.dumps(original), encoding='utf-8')
    original_bytes = legacy_file.read_bytes()
    monkeypatch.setattr(unreal.Paths, 'project_saved_dir', lambda: str(legacy_saved))
    cfg = config.get_config()
    assert cfg.get('ui.theme') == 'custom_theme'
    assert cfg.get('scatter.default_count') == 7
    assert cfg.get('verse.project_path') == ''
    assert cfg.get('import.default_dir') == ''
    assert cfg._path == str(root / 'Saved/UEFN_Toolbelt/config.json')
    assert legacy_file.read_bytes() == original_bytes
    cfg.set('scatter.default_count', 8)
    assert legacy_file.read_bytes() == original_bytes
    with pytest.raises(ValueError, match='current native project'):
        cfg.set('verse.project_path', str(other))


def test_valid_same_project_verse_override_migrates_and_existing_local_wins(tmp_path, monkeypatch):
    import unreal
    root, config = _native_fixture(tmp_path, monkeypatch)
    saved = tmp_path / 'SharedSaved'
    legacy = saved / 'UEFN_Toolbelt/config.json'
    legacy.parent.mkdir(parents=True)
    original = {'verse.project_path':str(root / 'Content'),
                'import.default_dir':'/uuid-Island/Textures', 'ui.theme':'legacy_theme'}
    legacy.write_text(json.dumps(original), encoding='utf-8')
    monkeypatch.setattr(unreal.Paths, 'project_saved_dir', lambda: str(saved))
    cfg = config.get_config()
    assert cfg.get('verse.project_path') == str(root / 'Content')
    assert cfg.get('import.default_dir') == '/uuid-Island/Textures'
    cfg.set('ui.theme', 'island_theme')
    monkeypatch.setattr(config, '_config_instance', None)
    assert config.get_config().get('ui.theme') == 'island_theme'


def test_singleton_changes_when_native_project_changes(tmp_path, monkeypatch):
    import unreal

    from UEFN_Toolbelt import core
    root, config = _native_fixture(tmp_path, monkeypatch)
    monkeypatch.setattr(unreal.Paths, 'project_saved_dir', lambda: str(tmp_path / 'SharedSaved'))
    first = config.get_config()
    first.set('scatter.default_count', 9)
    second_root = tmp_path / 'OtherIsland'
    package = second_root / 'Content/Python/UEFN_Toolbelt/core'
    package.mkdir(parents=True)
    (second_root / 'OtherIsland.uefnproject').write_text(json.dumps({
        'plugins':[{'name':'uuid-other','bIsRoot':True}]}), encoding='utf-8')
    monkeypatch.setattr(core, '__file__', str(package / '__init__.py'))
    second = config.get_config()
    assert second is not first
    assert second.get('scatter.default_count') == DEFAULTS['scatter.default_count']
    assert second._path.startswith(str(second_root))
    assert first._path.startswith(str(root))


def test_cross_project_override_in_existing_local_file_is_not_readable_as_target(tmp_path):
    root = tmp_path / 'Island'
    root.mkdir()
    path = root / 'config.json'
    path.write_text(json.dumps({'verse.project_path':str(tmp_path / 'OtherIsland')}), encoding='utf-8')
    cfg = Config(str(path), str(root))
    assert cfg.get('verse.project_path') == ''
    assert cfg.all()['verse.project_path'] == ''


def test_no_descriptor_does_not_fall_back_to_shared_writable_config(tmp_path, monkeypatch):
    from UEFN_Toolbelt import core
    from UEFN_Toolbelt.core import config
    package = tmp_path / 'NoDescriptor/Content/Python/UEFN_Toolbelt/core'
    package.mkdir(parents=True)
    monkeypatch.setattr(core, '__file__', str(package / '__init__.py'))
    monkeypatch.setattr(config, '_config_instance', None)
    unresolved = config.get_config()
    assert unresolved.get('verse.project_path') == ''
    with pytest.raises(ValueError, match='confirmed native project'):
        unresolved.set('scatter.default_count', 4)


@pytest.mark.parametrize('value', ['[]', 'null', '1'])
def test_non_object_config_falls_back_to_defaults(tmp_path, value):
    path = tmp_path / 'config.json'
    path.write_text(value, encoding='utf-8')
    assert Config(str(path)).get('scatter.default_count') == DEFAULTS['scatter.default_count']


@pytest.mark.parametrize('raw', [b'{broken', b'[]', b'null', b'4'])
def test_invalid_existing_config_reads_defaults_but_preserves_bytes_on_writes(tmp_path, raw):
    path = tmp_path / 'config.json'
    path.write_bytes(raw)
    cfg = Config(str(path))
    assert cfg.get('scatter.default_count') == DEFAULTS['scatter.default_count']
    with pytest.raises(ValueError, match='unreadable or invalid; writes refused'):
        cfg.set('scatter.default_count', 5)
    with pytest.raises(ValueError, match='writes refused'):
        cfg.reset('scatter.default_count')
    assert path.read_bytes() == raw
    assert cfg.get('scatter.default_count') == DEFAULTS['scatter.default_count']


def test_unreadable_existing_config_cannot_be_overwritten(tmp_path, monkeypatch):
    import builtins
    path = tmp_path / 'config.json'
    original = b'{"scatter.default_count":9}'
    path.write_bytes(original)
    real_open = builtins.open

    def unreadable(file, mode='r', *args, **kwargs):
        if str(file) == str(path) and mode == 'r':
            raise PermissionError('fixture refuses config reads')
        return real_open(file, mode, *args, **kwargs)

    monkeypatch.setattr(builtins, 'open', unreadable)
    cfg = Config(str(path))
    assert cfg.get('scatter.default_count') == DEFAULTS['scatter.default_count']
    with pytest.raises(ValueError, match='writes refused'):
        cfg.set('scatter.default_count', 5)
    assert path.read_bytes() == original


def test_failed_serialization_preserves_file_and_cached_value(cfg, tmp_path):
    cfg.set('scatter.default_count', 7)
    path = tmp_path / 'UEFN_Toolbelt/config.json'
    original = path.read_bytes()
    with pytest.raises(TypeError):
        cfg.set('scatter.default_count', object())
    assert path.read_bytes() == original
    assert cfg.get('scatter.default_count') == 7
    assert list(path.parent.glob('.config.*.tmp')) == []


@pytest.mark.parametrize('operation', ['set', 'reset'])
@pytest.mark.parametrize('failure', ['write', 'replace'])
def test_failed_atomic_save_preserves_file_and_rolls_back_cache(cfg, tmp_path, monkeypatch, operation, failure):
    from UEFN_Toolbelt.core import config
    cfg.set('scatter.default_count', 7)
    path = tmp_path / 'UEFN_Toolbelt/config.json'
    original = path.read_bytes()

    def refused(*args, **kwargs):
        raise PermissionError('fixture atomic save refused')

    if failure == 'write':
        monkeypatch.setattr(config.tempfile, 'NamedTemporaryFile', refused)
    else:
        monkeypatch.setattr(config.os, 'replace', refused)
    with pytest.raises(PermissionError, match='atomic save refused'):
        if operation == 'set':
            cfg.set('scatter.default_count', 8)
        else:
            cfg.reset('scatter.default_count')
    assert path.read_bytes() == original
    assert cfg.get('scatter.default_count') == 7
    assert not cfg.is_default('scatter.default_count')
    assert list(path.parent.glob('.config.*.tmp')) == []


def test_public_config_follows_native_project_switch_without_cross_contamination(tmp_path, monkeypatch):
    import unreal

    import UEFN_Toolbelt as tb
    from UEFN_Toolbelt import core
    root, _ = _native_fixture(tmp_path, monkeypatch)
    monkeypatch.setattr(unreal.Paths, 'project_saved_dir', lambda: str(tmp_path / 'SharedSaved'))
    tb.config.set('scatter.default_count', 7)
    first_bytes = (root / 'Saved/UEFN_Toolbelt/config.json').read_bytes()
    other = tmp_path / 'OtherIsland'
    package = other / 'Content/Python/UEFN_Toolbelt/core'
    package.mkdir(parents=True)
    (other / 'OtherIsland.uefnproject').write_text(json.dumps({
        'plugins':[{'name':'uuid-other','bIsRoot':True}]}), encoding='utf-8')
    monkeypatch.setattr(core, '__file__', str(package / '__init__.py'))
    assert tb.config.get('scatter.default_count') == DEFAULTS['scatter.default_count']
    tb.config.set('scatter.default_count', 8)
    assert (root / 'Saved/UEFN_Toolbelt/config.json').read_bytes() == first_bytes
    assert json.loads((other / 'Saved/UEFN_Toolbelt/config.json').read_text())['scatter.default_count'] == 8
    monkeypatch.setattr(core, '__file__', str(root / 'Content/Python/UEFN_Toolbelt/core/__init__.py'))
    assert tb.config.get('scatter.default_count') == 7


def test_public_config_recovers_from_early_unresolved_identity(tmp_path, monkeypatch):
    import unreal

    import UEFN_Toolbelt as tb
    from UEFN_Toolbelt import core
    from UEFN_Toolbelt.core import config
    unknown = tmp_path / 'Unknown/Content/Python/UEFN_Toolbelt/core'
    unknown.mkdir(parents=True)
    monkeypatch.setattr(core, '__file__', str(unknown / '__init__.py'))
    monkeypatch.setattr(config, '_config_instance', None)
    assert tb.config.get('verse.project_path') == ''
    with pytest.raises(ValueError, match='confirmed native project'):
        tb.config.set('scatter.default_count', 1)
    root, _ = _native_fixture(tmp_path, monkeypatch)
    monkeypatch.setattr(unreal.Paths, 'project_saved_dir', lambda: str(tmp_path / 'SharedSaved'))
    tb.config.set('scatter.default_count', 9)
    assert tb.config.get('scatter.default_count') == 9
    assert (root / 'Saved/UEFN_Toolbelt/config.json').is_file()
    assert not (unknown.parents[3] / 'Saved/UEFN_Toolbelt/config.json').exists()
