"""New UEFN UUID plugin mounts must not become display-name asset paths."""
import json

import pytest

from UEFN_Toolbelt import core


@pytest.mark.parametrize("mount", ["96af6cef-b385-4bf5-a7ec-1ea0c19944c5", "Riftbloom"])
def test_descriptor_root_plugin_owns_mount(tmp_path, monkeypatch, mount):
    root = tmp_path / "Riftbloom"
    package = root / "Content" / "Python" / "UEFN_Toolbelt" / "core"
    package.mkdir(parents=True)
    (root / "Riftbloom.uefnproject").write_text(json.dumps({
        "plugins": [{"name": "Dependency", "bIsRoot": False},
                    {"name": mount, "bIsRoot": True}]}))
    monkeypatch.setattr(core, "__file__", str(package / "__init__.py"))
    assert core.detect_project_mount() == mount


def test_legacy_folder_fallback_without_descriptor(tmp_path, monkeypatch):
    package = tmp_path / "Legacy" / "Content" / "Python" / "UEFN_Toolbelt" / "core"
    package.mkdir(parents=True)
    monkeypatch.setattr(core, "__file__", str(package / "__init__.py"))
    assert core.detect_project_mount() == "Legacy"


def test_renamed_project_directory_uses_single_descriptor_identity(tmp_path, monkeypatch):
    root = tmp_path / "Renamed Folder"
    package = root / "Content/Python/UEFN_Toolbelt/core"
    package.mkdir(parents=True)
    (root / "OriginalName.uefnproject").write_text(json.dumps({
        "plugins": [{"name": "uuid-project-mount", "bIsRoot": True}]}))
    monkeypatch.setattr(core, "__file__", str(package / "__init__.py"))
    assert core.resolve_content_path("/Game/NewAsset") == "/uuid-project-mount/NewAsset"


@pytest.mark.parametrize("descriptors", [
    {"One.uefnproject": "{}", "Two.uefnproject": "{}"},
    {"One.uefnproject": "{invalid"},
    {"One.uefnproject": "{}"},
])
def test_ambiguous_or_invalid_descriptor_never_guesses_folder_mount(tmp_path, monkeypatch, descriptors):
    root = tmp_path / "Renamed Folder"
    package = root / "Content/Python/UEFN_Toolbelt/core"
    package.mkdir(parents=True)
    for name, content in descriptors.items():
        (root / name).write_text(content)
    monkeypatch.setattr(core, "__file__", str(package / "__init__.py"))
    with pytest.raises(ValueError, match="mount is unavailable"):
        core.resolve_content_path("/Game/NewAsset")


def test_native_content_path_uses_descriptor_even_when_engine_paths_are_wrong(tmp_path, monkeypatch):
    root = tmp_path / 'Island'
    package = root / 'Content/Python/UEFN_Toolbelt/core'
    package.mkdir(parents=True)
    (root / 'Renamed.uefnproject').write_text(json.dumps({
        'plugins':[{'name':'uuid-island','bIsRoot':True}]}), encoding='utf-8')
    monkeypatch.setattr(core, '__file__', str(package / '__init__.py'))
    monkeypatch.setattr(core.unreal.Paths, 'project_dir', lambda: '/Engine/FortniteGame/')
    assert core.native_project_dir() == str(root)
    assert core.project_content_dir() == str(root / 'Content')


@pytest.mark.parametrize('descriptor', ['{}', '{invalid', '{"plugins":[{"name":"Game","bIsRoot":true}]}'])
def test_native_filesystem_path_refuses_unconfirmed_descriptor(tmp_path, monkeypatch, descriptor):
    root = tmp_path / 'Island'
    package = root / 'Content/Python/UEFN_Toolbelt/core'
    package.mkdir(parents=True)
    (root / 'Island.uefnproject').write_text(descriptor, encoding='utf-8')
    monkeypatch.setattr(core, '__file__', str(package / '__init__.py'))
    with pytest.raises(ValueError, match='Native project'):
        core.project_content_dir()


def test_native_filesystem_path_refuses_multiple_even_when_one_matches_folder(tmp_path, monkeypatch):
    root = tmp_path / 'Island'
    package = root / 'Content/Python/UEFN_Toolbelt/core'
    package.mkdir(parents=True)
    for name in ['Island', 'Other']:
        (root / f'{name}.uefnproject').write_text(json.dumps({
            'plugins':[{'name':f'uuid-{name}','bIsRoot':True}]}), encoding='utf-8')
    monkeypatch.setattr(core, '__file__', str(package / '__init__.py'))
    with pytest.raises(ValueError, match='unique .uefnproject'):
        core.native_project_dir()


def test_backup_reads_native_content_not_engine_content(tmp_path, monkeypatch):
    import zipfile

    from UEFN_Toolbelt.tools import project_admin
    root = tmp_path / 'Island'
    package = root / 'Content/Python/UEFN_Toolbelt/core'
    package.mkdir(parents=True)
    (root / 'Island.uefnproject').write_text(json.dumps({
        'plugins':[{'name':'uuid-island','bIsRoot':True}]}), encoding='utf-8')
    asset = root / 'Content/SM_Fixture.uasset'
    asset.write_bytes(b'known-native-asset')
    monkeypatch.setattr(core, '__file__', str(package / '__init__.py'))
    monkeypatch.setattr(core.unreal.Paths, 'project_content_dir', lambda: pytest.fail('unsafe engine content call'))
    monkeypatch.setattr(core.unreal.Paths, 'project_saved_dir', lambda: str(tmp_path / 'EngineSaved'))
    result = project_admin.run_system_backup_project()
    assert result['status'] == 'ok'
    with zipfile.ZipFile(result['path']) as backup:
        assert backup.namelist() == ['Content/SM_Fixture.uasset']
        assert backup.read('Content/SM_Fixture.uasset') == b'known-native-asset'


def test_prefab_export_uses_confirmed_project_source(tmp_path, monkeypatch):
    from UEFN_Toolbelt.tools import prefab_migrator
    root = tmp_path / 'Island'
    package = root / 'Content/Python/UEFN_Toolbelt/core'
    package.mkdir(parents=True)
    (root / 'Island.uefnproject').write_text(json.dumps({
        'plugins':[{'name':'uuid-island','bIsRoot':True}]}), encoding='utf-8')
    monkeypatch.setattr(core, '__file__', str(package / '__init__.py'))
    monkeypatch.setattr(core.unreal.Paths, 'project_content_dir', lambda: pytest.fail('unsafe engine content call'))
    calls = []
    def export(*args):
        calls.append(args)
        return {'ok':['fixture'], 'skip':[], 'missing':[], 'error':[]}
    monkeypatch.setattr(prefab_migrator, '_export_to_disk', export)
    result = prefab_migrator.prefab_export_to_disk(packages=['/uuid-island/Fixture'], dst_content=str(tmp_path / 'Export'))
    assert result['status'] == 'ok'
    assert calls[0][1] == str(root / 'Content')


def test_filesystem_writers_refuse_before_touching_unknown_project(tmp_path, monkeypatch):
    from UEFN_Toolbelt.tools import prefab_migrator, project_admin
    package = tmp_path / 'Unknown/Content/Python/UEFN_Toolbelt/core'
    package.mkdir(parents=True)
    monkeypatch.setattr(core, '__file__', str(package / '__init__.py'))
    monkeypatch.setattr(core.unreal.Paths, 'project_saved_dir', lambda: pytest.fail('created backup output before identity'))
    monkeypatch.setattr(prefab_migrator, '_export_to_disk', lambda *_: pytest.fail('export before identity'))
    assert project_admin.run_system_backup_project()['status'] == 'error'
    assert prefab_migrator.prefab_export_to_disk(packages=['/Unknown/Fixture'], dst_content=str(tmp_path / 'Export'))['status'] == 'error'


def test_schema_sync_writes_only_current_native_docs(tmp_path, monkeypatch):
    from UEFN_Toolbelt import schema_utils
    from UEFN_Toolbelt.tools import api_capability_crawler
    root = tmp_path / 'Island'
    package = root / 'Content/Python/UEFN_Toolbelt/core'
    package.mkdir(parents=True)
    (root / 'Island.uefnproject').write_text(json.dumps({
        'plugins':[{'name':'uuid-island','bIsRoot':True}]}), encoding='utf-8')
    monkeypatch.setattr(core, '__file__', str(package / '__init__.py'))
    monkeypatch.setattr(core.unreal.Paths, 'project_dir', lambda: pytest.fail('unsafe engine docs call'))
    source = tmp_path / 'source.json'
    source.write_text('{"fixture":true}', encoding='utf-8')
    destination = api_capability_crawler._sync_to_repo(str(source), 'uefn_reference_schema.json')
    assert destination == str(root / 'docs/uefn_reference_schema.json')
    assert schema_utils.get_schema_path() == destination
    assert (root / 'docs/uefn_reference_schema.json').read_bytes() == source.read_bytes()
