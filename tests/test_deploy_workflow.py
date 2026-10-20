"""Execute the Windows deploy wrapper against disposable project directories."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


@pytest.mark.skipif(shutil.which("cmd") is None, reason="Windows batch is unavailable")
@pytest.mark.parametrize("existing_hook", [False, True])
@pytest.mark.parametrize("with_reference", [False, True])
def test_explicit_project_deploy_preserves_startup_and_stamps(tmp_path, existing_hook, with_reference):
    source = tmp_path / "source repo"
    source.mkdir()
    shutil.copy2(REPO / "deploy.bat", source / "deploy.bat")
    shutil.copy2(REPO / "install.py", source / "install.py")
    package = source / "Content" / "Python" / "UEFN_Toolbelt"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("# deployed package\n", encoding="utf-8")
    (source / "init_unreal.py").write_text("# default loader\n", encoding="utf-8")
    if with_reference:
        reference = source / "verse-book"
        (reference / "docs").mkdir(parents=True)
        (reference / "docs" / "chapter.md").write_text("# Verse reference\n", encoding="utf-8")
        (reference / "setup.py").write_text("# exclude Python helper\n", encoding="utf-8")
        subprocess.run(["git", "init", str(reference)], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(reference), "add", "."], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(reference), "-c", "user.name=Test Fixture",
                        "-c", "user.email=fixture@example.invalid", "commit", "-m", "fixture"],
                       check=True, capture_output=True)
    project = tmp_path / "custom projects" / "Test Island"
    project.mkdir(parents=True)
    (project / "Test Island.uefnproject").write_text("{}", encoding="utf-8")
    hook = project / "Content" / "Python" / "init_unreal.py"
    old_package = hook.parent / "UEFN_Toolbelt"
    old_package.mkdir(parents=True)
    (old_package / "removed_module.py").write_text("# no longer in source\n", encoding="utf-8")
    if existing_hook:
        hook.write_bytes(b"# existing deferred hook\r\n")
    result = subprocess.run(
        ["cmd", "/d", "/c", "deploy.bat", str(project), "/nopause"],
        cwd=source, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert not result.stderr, result.stderr
    assert (hook.parent / "UEFN_Toolbelt" / "__init__.py").read_text() == "# deployed package\n"
    assert not (old_package / "removed_module.py").exists()
    assert hook.read_bytes() == (
        b"# existing deferred hook\r\n" if existing_hook else b"# default loader\r\n"
    )
    stamp = json.loads((hook.parent / "UEFN_Toolbelt" / "_build_stamp.json").read_text())
    assert stamp["project"] == "Test Island"
    assert stamp["deployed_at"] != "unknown"
    assert "sys.modules.pop" not in result.stdout
    assert "full UEFN restart" in result.stdout
    if with_reference:
        deployed_reference = project / "verse-book"
        assert (deployed_reference / ".git").is_dir()
        assert (deployed_reference / "docs" / "chapter.md").read_text() == "# Verse reference\n"
        assert not list(deployed_reference.rglob("*.py"))
        origin = subprocess.run(["git", "-C", str(deployed_reference), "remote", "get-url", "origin"],
                                check=True, capture_output=True, text=True).stdout.strip()
        assert origin == "https://github.com/verselang/book.git"
        status = subprocess.run(["git", "-C", str(deployed_reference), "status", "--porcelain"],
                                check=True, capture_output=True, text=True).stdout.strip()
        assert status == ""


@pytest.mark.skipif(shutil.which("cmd") is None, reason="Windows batch is unavailable")
def test_explicit_non_project_is_rejected_without_copying(tmp_path):
    result = subprocess.run(
        ["cmd", "/d", "/c", "deploy.bat", str(tmp_path), "/nopause"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode != 0
    assert not (tmp_path / "Content").exists()
