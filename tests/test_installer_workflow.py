"""Installer updates preserve project hooks and a recoverable package."""

import importlib.util
import json
import subprocess
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


def test_installer_stamps_actual_clean_and_dirty_deployed_build(installer, tmp_path):
    source = Path(installer.REPO_ROOT)
    subprocess.run(["git", "init", str(source)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(source), "add", "."], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(source), "-c", "user.name=Test Fixture",
                    "-c", "user.email=fixture@example.invalid", "commit", "-m", "fixture"],
                   check=True, capture_output=True)
    commit = subprocess.run(["git", "-C", str(source), "rev-parse", "--short", "HEAD"],
                            check=True, capture_output=True, text=True).stdout.strip()
    project = tmp_path / "stamped island"
    package = project / "Content/Python/UEFN_Toolbelt"
    installer._install_toolbelt(str(project))
    clean = json.loads((package / "_build_stamp.json").read_text())
    assert clean["commit"] == commit
    assert clean["project"] == project.name
    assert (package / "__init__.py").read_bytes() == (Path(installer.TOOLBELT_SRC) / "__init__.py").read_bytes()
    (Path(installer.TOOLBELT_SRC) / "__init__.py").write_text("# changed package\n")
    installer._install_toolbelt(str(project))
    dirty = json.loads((package / "_build_stamp.json").read_text())
    assert dirty["commit"] == commit + "+dirty"
    assert dirty["deployed_at"] != "unknown"
    assert (package / "__init__.py").read_text() == "# changed package\n"


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


def test_failed_rollback_retains_recoverable_previous_package(installer, tmp_path, monkeypatch, capsys):
    project = tmp_path / "island"
    package = project / "Content" / "Python" / "UEFN_Toolbelt"
    package.mkdir(parents=True)
    (package / "user_file.py").write_bytes(b"# preserve even if rollback is blocked\n")
    replace = installer.os.replace

    def refuse_install_and_rollback(source, target):
        if Path(source).name in ("package", "previous"):
            raise OSError("destination locked")
        return replace(source, target)

    monkeypatch.setattr(installer.os, "replace", refuse_install_and_rollback)
    with pytest.raises(SystemExit):
        installer._install_toolbelt(str(project))
    backups = list(package.parent.glob(".toolbelt-install-*/previous"))
    assert len(backups) == 1
    assert (backups[0] / "user_file.py").read_bytes() == b"# preserve even if rollback is blocked\n"
    assert str(backups[0]) in capsys.readouterr().out


def test_preserve_startup_keeps_arbitrary_hook_byte_for_byte(installer, tmp_path):
    project = tmp_path / "island"
    hook = project / "Content" / "Python" / "init_unreal.py"
    hook.parent.mkdir(parents=True)
    hook.write_bytes(b"# custom startup\r\nprint('leave unchanged')\r\n")
    original = hook.read_bytes()
    installer._install_toolbelt(str(project), preserve_startup=True)
    assert hook.read_bytes() == original


def test_cli_can_update_package_without_changing_dependencies(installer, tmp_path, monkeypatch):
    project = tmp_path / "island"
    project.mkdir()
    (project / "island.uefnproject").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(installer.sys, "argv", ["install.py", "--project", str(project), "--skip-dependencies"])
    monkeypatch.setattr(installer, "_ensure_pyside6", lambda: pytest.fail("Dependency setup ran"))
    installer.main()
    assert (project / "Content/Python/UEFN_Toolbelt/_build_stamp.json").exists()


@pytest.mark.parametrize("explicit", [True, False])
def test_cli_rejects_non_project_before_dependency_or_package_changes(installer, tmp_path, monkeypatch, explicit):
    project = tmp_path / "ordinary directory"
    existing = project / "Content/Python/UEFN_Toolbelt/user.py"
    existing.parent.mkdir(parents=True)
    existing.write_bytes(b"# original user file\n")
    args = ["install.py", "--project", str(project)] if explicit else ["install.py"]
    monkeypatch.setattr(installer.sys, "argv", args)
    monkeypatch.setattr(installer, "_find_uefn_projects", list)
    monkeypatch.setattr("builtins.input", lambda _: str(project))
    monkeypatch.setattr(installer, "_ensure_pyside6", lambda: pytest.fail("Dependency setup ran before validation"))
    with pytest.raises(SystemExit):
        installer.main()
    assert existing.read_bytes() == b"# original user file\n"
    assert not (existing.parent / "__init__.py").exists()


def test_project_validation_accepts_descriptor_in_renamed_directory(installer, tmp_path):
    project = tmp_path / "renamed directory"
    project.mkdir()
    (project / "OriginalName.uefnproject").write_text("{}", encoding="utf-8")
    assert installer._pick_project(str(project)) == str(project.resolve())


@pytest.fixture
def reference_source(installer):
    reference = Path(installer.REPO_ROOT) / "verse-book"
    (reference / "docs").mkdir(parents=True)
    (reference / "docs/chapter.md").write_text("# current reference\n", encoding="utf-8")
    (reference / "setup.py").write_text("# exclude Python helper\n", encoding="utf-8")
    subprocess.run(["git", "init", str(reference)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(reference), "add", "."], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(reference), "-c", "user.name=Test Fixture",
                    "-c", "user.email=fixture@example.invalid", "commit", "-m", "fixture"],
                   check=True, capture_output=True)
    return reference


def test_reference_snapshot_upgrade_preserves_custom_files(installer, reference_source, tmp_path):
    project = tmp_path / "island"
    snapshot = project / "verse-book/custom.txt"
    snapshot.parent.mkdir(parents=True)
    snapshot.write_bytes(b"keep my custom notes\r\n")
    installer._install_reference(str(project))
    assert (project / "verse-book/.git").is_dir()
    assert (project / "verse-book/docs/chapter.md").read_text() == "# current reference\n"
    assert not list((project / "verse-book").rglob("*.py"))
    backups = list(project.glob(".verse-book-backup-*/verse-book/custom.txt"))
    assert len(backups) == 1
    assert backups[0].read_bytes() == b"keep my custom notes\r\n"


@pytest.mark.parametrize("rollback_blocked", [False, True])
def test_reference_replacement_failure_preserves_snapshot(installer, reference_source, tmp_path, monkeypatch, rollback_blocked):
    project = tmp_path / "island"
    snapshot = project / "verse-book/custom.txt"
    snapshot.parent.mkdir(parents=True)
    snapshot.write_bytes(b"keep my custom notes\r\n")
    replace = installer.os.replace

    def refuse_replacement(source, destination):
        if Path(source).name == "reference" or (rollback_blocked and Path(source).name == "verse-book"):
            # Permit moving the original snapshot into its backup.
            if Path(source).parent == project:
                return replace(source, destination)
            raise OSError("destination locked")
        return replace(source, destination)

    monkeypatch.setattr(installer.os, "replace", refuse_replacement)
    with pytest.raises(OSError, match="destination locked"):
        installer._install_reference(str(project))
    if rollback_blocked:
        backups = list(project.glob(".verse-book-backup-*/verse-book/custom.txt"))
        assert len(backups) == 1
        assert backups[0].read_bytes() == b"keep my custom notes\r\n"
    else:
        assert snapshot.read_bytes() == b"keep my custom notes\r\n"
        assert not (snapshot.parent / ".git").exists()


def test_existing_reference_clone_and_local_notes_remain_untouched(installer, reference_source, tmp_path):
    project = tmp_path / "island"
    project.mkdir()
    installer._install_reference(str(project))
    chapter = project / "verse-book/docs/chapter.md"
    chapter.write_bytes(b"local documentation notes\n")
    installer._install_reference(str(project))
    assert chapter.read_bytes() == b"local documentation notes\n"
