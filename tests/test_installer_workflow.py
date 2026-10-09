"""Installer updates preserve project hooks and a recoverable package."""

import importlib.util
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


@pytest.fixture
def installer(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location("toolbelt_install", REPO / "install.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    source = tmp_path / "source"
    source.mkdir()
    package = source / "package"
    package.mkdir()
    (package / "__init__.py").write_text("# current package\n", encoding="utf-8")
    loader = source / "init_unreal.py"
    loader.write_text("# default loader\n", encoding="utf-8")
    monkeypatch.setattr(module, "REPO_ROOT", str(source))
    monkeypatch.setattr(module, "TOOLBELT_SRC", str(package))
    monkeypatch.setattr(module, "INIT_SRC", str(loader))
    return module


def test_managed_hook_is_preserved_byte_for_byte(installer, tmp_path):
    project = tmp_path / "island"
    hook = project / "Content" / "Python" / "init_unreal.py"
    hook.parent.mkdir(parents=True)
    original = b"# [CODEX_TOOLBELT_AUTOSTART]\r\n# user hook\r\n# [/CODEX_TOOLBELT_AUTOSTART]\r\n"
    hook.write_bytes(original)
    installer._install_toolbelt(str(project))
    assert hook.read_bytes() == original
    assert (hook.parent / "UEFN_Toolbelt" / "__init__.py").exists()


def test_new_install_is_idempotent_and_stamped(installer, tmp_path):
    project = tmp_path / "island"
    installer._install_toolbelt(str(project))
    hook = project / "Content" / "Python" / "init_unreal.py"
    original = hook.read_bytes()
    installer._install_toolbelt(str(project))
    assert hook.read_bytes() == original
    stamp = json.loads((hook.parent / "UEFN_Toolbelt" / "_build_stamp.json").read_text())
    assert stamp["project"] == "island"
    assert stamp["deployed_at"] != "unknown"


def test_failed_update_keeps_existing_package(installer, tmp_path, monkeypatch):
    project = tmp_path / "island"
    package = project / "Content" / "Python" / "UEFN_Toolbelt"
    package.mkdir(parents=True)
    original = package / "__init__.py"
    original.write_text("# old package\n", encoding="utf-8")

    def refuse_copy(*args, **kwargs):
        raise OSError("copy unavailable")

    monkeypatch.setattr(installer.shutil, "copytree", refuse_copy)
    with pytest.raises(SystemExit):
        installer._install_toolbelt(str(project))
    assert original.read_text(encoding="utf-8") == "# old package\n"


def test_replacement_failure_restores_previous_package(installer, tmp_path, monkeypatch):
    project = tmp_path / "island"
    package = project / "Content" / "Python" / "UEFN_Toolbelt"
    package.mkdir(parents=True)
    original = package / "__init__.py"
    original.write_text("# old package\n", encoding="utf-8")
    replace = installer.os.replace

    def refuse_install(source, target):
        if Path(source).name == "package":
            raise OSError("replacement unavailable")
        return replace(source, target)

    monkeypatch.setattr(installer.os, "replace", refuse_install)
    with pytest.raises(SystemExit):
        installer._install_toolbelt(str(project))
    assert original.read_text(encoding="utf-8") == "# old package\n"


def test_appended_loader_runs_with_no_packages(installer, tmp_path, monkeypatch):
    script = tmp_path / "init_unreal.py"
    script.write_text("# custom hook\n", encoding="utf-8")
    monkeypatch.syspath_prepend(str(tmp_path))
    exec(installer._LOADER_BLOCK, {"__file__": str(script)})


def test_cli_can_update_package_without_changing_dependencies(installer, tmp_path, monkeypatch):
    project = tmp_path / "island"
    project.mkdir()
    monkeypatch.setattr(installer.sys, "argv", ["install.py", "--project", str(project), "--skip-dependencies"])
    monkeypatch.setattr(installer, "_ensure_pyside6", lambda: pytest.fail("Dependency setup ran"))
    installer.main()
    assert (project / "Content/Python/UEFN_Toolbelt/_build_stamp.json").exists()
