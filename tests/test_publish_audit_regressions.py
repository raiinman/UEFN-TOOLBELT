"""Publish checks must reflect the active UEFN island, not engine defaults."""
import os
from types import SimpleNamespace

import pytest

from UEFN_Toolbelt import core
from UEFN_Toolbelt.tools import publish_audit as audit


def actor(class_name):
    return SimpleNamespace(
        get_class=lambda: SimpleNamespace(get_name=lambda: class_name),
        get_actor_label=lambda: class_name,
        get_actor_location=lambda: SimpleNamespace(x=0, y=0, z=0),
        get_actor_scale3d=lambda: SimpleNamespace(x=1, y=1, z=1),
    )


def test_default_spawn_pad_requirement_accepts_real_device():
    result = audit._check_required_devices(
        ["SpawnPadDevice"], [actor("BP_Creative_Player_Spawner_Prop_C")])
    assert result["pass"] is True
    assert result["missing"] == []


def test_engine_player_start_does_not_satisfy_spawn_pad_requirement():
    result = audit._check_required_devices(
        ["SpawnPadDevice"], [actor("FortPlayerStartCreative")])
    assert result["pass"] is False
    assert result["missing"] == ["SpawnPadDevice"]


@pytest.mark.parametrize("class_name", [
    "WaterZone", "LevelBounds", "Device_ExperienceSettings_V2_UEFN_C",
])
def test_engine_managed_actor_at_origin_is_legitimate(class_name):
    result = audit._check_rogue_actors([actor(class_name)])
    assert result["pass"] is True
    assert result["rogues"] == []


def test_user_mesh_at_origin_still_warns():
    result = audit._check_rogue_actors([actor("StaticMeshActor")])
    assert result["pass"] is False
    assert result["rogues"][0]["issues"] == ["at origin"]


def test_verse_log_is_under_saved_logs(tmp_path):
    saved = tmp_path / "Saved"
    logs = saved / "Logs"
    logs.mkdir(parents=True)
    (logs / "Riftbloom.log").write_text("VerseBuild SUCCESS\n", encoding="utf-8")
    result = audit._check_verse_build(str(saved))
    assert result["status"] == "SUCCESS"
    assert result["pass"] is True


def test_publish_check_prefers_editor_log_over_newer_revision_control_log(tmp_path):
    saved = tmp_path / "Saved"
    logs = saved / "Logs"
    logs.mkdir(parents=True)
    editor = logs / "UnrealEditorFortnite.log"
    editor.write_text("VerseBuild ERROR\n", encoding="utf-8")
    unrelated = logs / "UnrealRevisionControl.log"
    unrelated.write_text("revision control is connected\n", encoding="utf-8")
    os.utime(editor, (1, 1))
    os.utime(unrelated, (2, 2))
    result = audit._check_verse_build(str(saved))
    assert result["status"] == "FAILED"
    assert result["pass"] is False


@pytest.mark.parametrize("markers,status,passed", [
    ("VerseBuild SUCCESS\nVerseBuild ERROR\n", "FAILED", False),
    ("VerseBuild ERROR\nVerseBuild SUCCESS\n", "SUCCESS", True),
    ("LogSolLoadCompiler finished SUCCESS\nLogSolLoadCompiler finished FAIL\n",
     "FAILED", False),
])
def test_last_build_marker_controls_status(tmp_path, markers, status, passed):
    saved = tmp_path / "Saved"
    # Both locations isolate marker ordering from the separate path regression.
    for logs in (saved / "Logs", tmp_path / "Logs"):
        logs.mkdir(parents=True)
        (logs / "Riftbloom.log").write_text(markers, encoding="utf-8")
    result = audit._check_verse_build(str(saved))
    assert result["status"] == status
    assert result["pass"] is passed


def set_mount(monkeypatch, mount):
    monkeypatch.setattr(core, "detect_project_mount", lambda: mount)
    monkeypatch.setattr(audit, "detect_project_mount", lambda: mount, raising=False)


def test_redirectors_scan_confirmed_user_uuid_mount(monkeypatch):
    mount = "96af6cef-b385-4bf5-a7ec-1ea0c19944c5"
    set_mount(monkeypatch, mount)
    scanned = []
    redirector = SimpleNamespace(
        asset_class="ObjectRedirector",
        asset_class_path=SimpleNamespace(asset_name="ObjectRedirector"),
    )

    def scan(path, **kwargs):
        scanned.append(str(path))
        return [redirector] if str(path) == f"/{mount}" else []

    registry = SimpleNamespace(
        get_assets=lambda asset_filter: scan(asset_filter.package_paths[0]),
        get_assets_by_path=scan,
    )
    monkeypatch.setattr(audit.unreal, "ARFilter", lambda **kwargs: SimpleNamespace(**kwargs))
    monkeypatch.setattr(audit.unreal, "AssetRegistryHelpers", SimpleNamespace(
        get_asset_registry=lambda: registry))
    result = audit._check_redirectors()
    assert scanned == [f"/{mount}"]
    assert result["pass"] is False
    assert result["count"] == 1


@pytest.mark.parametrize("mount", ["Game", "96af6cef-b385-4bf5-a7ec-1ea0c19944c5"])
def test_unknown_mount_or_registry_error_never_passes(monkeypatch, mount):
    set_mount(monkeypatch, mount)

    def unavailable():
        if mount == "Game":
            return SimpleNamespace(get_assets=lambda _: [], get_assets_by_path=lambda *a, **k: [])
        raise RuntimeError("Asset Registry unavailable")

    monkeypatch.setattr(audit.unreal, "AssetRegistryHelpers", SimpleNamespace(
        get_asset_registry=unavailable))
    result = audit._check_redirectors()
    assert result["pass"] is None
    assert result["severity"] == "warn"
