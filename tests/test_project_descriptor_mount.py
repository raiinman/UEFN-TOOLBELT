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
