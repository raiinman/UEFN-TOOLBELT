"""Native Content backups stay project-local and never replace prior archives."""

import datetime
import zipfile
from pathlib import Path
from types import SimpleNamespace

import pytest

from UEFN_Toolbelt.tools import project_admin


@pytest.fixture
def native_content(tmp_path, monkeypatch):
    content = tmp_path / "Native Island/Content"
    content.mkdir(parents=True)
    (content / "prop.uasset").write_bytes(b"original asset")
    monkeypatch.setattr(project_admin, "project_content_dir", lambda: str(content))
    monkeypatch.setattr(project_admin.unreal.Paths, "project_saved_dir",
                        lambda: pytest.fail("Engine-shared Saved must not be used"))
    real_datetime = datetime.datetime

    class FixedDateTime:
        @staticmethod
        def now():
            return real_datetime(2026, 10, 9, 12, 0, 0)

    monkeypatch.setattr(project_admin.datetime, "datetime", FixedDateTime)
    return content


def test_repeated_same_second_backups_preserve_prior_bytes(native_content):
    first = project_admin.run_system_backup_project()
    assert first["status"] == "ok"
    first_path = Path(first["path"])
    original_archive = first_path.read_bytes()
    (native_content / "prop.uasset").write_bytes(b"updated asset")
    second = project_admin.run_system_backup_project()
    assert second["status"] == "ok"
    assert first["path"] != second["path"]
    assert first_path.parent == native_content.parent / "Saved/UEFN_Toolbelt/backups"
    assert first_path.read_bytes() == original_archive
    assert second["source_content"] == str(native_content)
    with zipfile.ZipFile(first["path"]) as archive:
        assert archive.read("Content/prop.uasset") == b"original asset"
    with zipfile.ZipFile(second["path"]) as archive:
        assert archive.read("Content/prop.uasset") == b"updated asset"


def test_project_switch_keeps_backups_with_their_native_source(native_content, monkeypatch, tmp_path):
    first = project_admin.run_system_backup_project()
    other = tmp_path / "Other Island/Content"
    other.mkdir(parents=True)
    (other / "other.verse").write_bytes(b"other project source")
    monkeypatch.setattr(project_admin, "project_content_dir", lambda: str(other))
    second = project_admin.run_system_backup_project()
    assert second["status"] == "ok"
    assert Path(second["path"]).parent == other.parent / "Saved/UEFN_Toolbelt/backups"
    assert Path(first["path"]).exists()
    with zipfile.ZipFile(second["path"]) as archive:
        assert archive.namelist() == ["Content/other.verse"]
        assert archive.read("Content/other.verse") == b"other project source"


def test_failed_backup_preserves_prior_archive(native_content, monkeypatch):
    first = project_admin.run_system_backup_project()
    first_path = Path(first["path"])
    original_archive = first_path.read_bytes()

    def refuse_write(*args, **kwargs):
        raise OSError("source file locked")

    monkeypatch.setattr(project_admin.zipfile.ZipFile, "write", refuse_write)
    failed = project_admin.run_system_backup_project()
    assert failed["status"] == "error"
    assert first_path.read_bytes() == original_archive
    assert list(first_path.parent.glob("*.zip")) == [first_path]


def test_exclusive_creation_never_overwrites_even_with_name_collision(native_content, monkeypatch):
    monkeypatch.setattr(project_admin.uuid, "uuid4", lambda: SimpleNamespace(hex="fixed-collision"))
    first = project_admin.run_system_backup_project()
    first_path = Path(first["path"])
    original_archive = first_path.read_bytes()
    (native_content / "prop.uasset").write_bytes(b"different asset")
    collision = project_admin.run_system_backup_project()
    assert collision["status"] == "error"
    assert collision["incomplete_path"] == ""
    assert first_path.read_bytes() == original_archive


def test_directory_enumeration_failure_refuses_partial_archive_and_keeps_prior(native_content, monkeypatch):
    first = project_admin.run_system_backup_project()
    first_path = Path(first['path'])
    original_archive = first_path.read_bytes()

    def partially_readable_walk(path, onerror=None):
        assert path == str(native_content)
        # One file was already archived before another directory became unreadable.
        yield str(native_content), ['Unreadable'], ['prop.uasset']
        error = PermissionError('fixture directory enumeration denied')
        if onerror is not None:
            onerror(error)
        # This models os.walk's default behavior: silently skip an unreadable subtree.

    monkeypatch.setattr(project_admin.os, 'walk', partially_readable_walk)
    failed = project_admin.run_system_backup_project()
    assert failed['status'] == 'error'
    assert 'directory enumeration denied' in failed['message']
    assert failed['incomplete_path'] == ''
    assert first_path.read_bytes() == original_archive
    assert list(first_path.parent.glob('*.zip')) == [first_path]
