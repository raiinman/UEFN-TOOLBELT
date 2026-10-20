"""Local acceptance-controller flow checks; fake results prove no native outcomes."""

import importlib
import json
import runpy
import zipfile
from pathlib import Path
from types import SimpleNamespace

import pytest

DRIVER = (Path(__file__).resolve().parents[1] / "docs/audits/evidence"
          / "2026-10-09-toolbelt-acceptance/run_native_maintenance.py")


@pytest.fixture
def controller(tmp_path, monkeypatch):
    namespace = runpy.run_path(str(DRIVER), run_name="controller_fixture")
    main = namespace["main"]
    scope = main.__globals__
    project = tmp_path / "ToolbeltAcceptance"
    identity = {"project_dir": str(project), "mount": "fixture-uuid",
                "descriptor": str(project / "ToolbeltAcceptance.uefnproject"),
                "world_path": "/fixture-uuid/Acceptance.Acceptance"}
    mount = "/fixture-uuid"
    fixtures = mount + "/AcceptanceFixtures"
    texture_path = fixtures + "/Textures/T_Acceptance"
    sound_path = fixtures + "/Audio/SW_Acceptance"
    properties = {"srgb": False, "compression_settings": "<TextureCompressionSettings.TC_GRAYSCALE: 3>",
                  "lod_group": "<TextureGroup.TEXTUREGROUP_WORLD: 0>",
                  "mip_gen_settings": "<TextureMipGenSettings.TMGS_FROM_TEXTURE_GROUP: 0>"}
    texture_file = project / "Content/AcceptanceFixtures/Textures/T_Acceptance.uasset"
    sound_file = project / "Content/AcceptanceFixtures/Audio/SW_Acceptance.uasset"
    for file, content in ((texture_file, b"saved imported texture bytes"),
                          (sound_file, b"saved imported sound bytes")):
        file.parent.mkdir(parents=True)
        file.write_bytes(content)
    prior = tmp_path / "prior.json"
    prior.write_text(json.dumps({"identity": identity, "native_readbacks": [{
        "object_path": texture_path + ".T_Acceptance", "properties": properties}]}), encoding="utf-8")
    scope["SCRIPT_PATH"] = DRIVER
    scope["OUTPUT"] = tmp_path / "evidence"
    scope["PRIOR"] = prior
    package = scope["tb"]
    control = SimpleNamespace(changed_identity=False, change_after_memory=False, incomplete=False,
                              calls=[], sections=[], backup_count=0, missing_memory_check=False)
    monkeypatch.setattr(scope["suite"], "_integration_running", False)
    monkeypatch.setattr(scope["suite"], "_acceptance_identity", lambda: (
        dict(identity, mount="different-uuid") if control.changed_identity else dict(identity)))
    monkeypatch.setattr(scope["core"], "native_project_dir", lambda: str(project))
    monkeypatch.setattr(package, "registry", SimpleNamespace(list_tools=lambda: list(range(362))))
    for module in (package, scope["core"], scope["suite"], scope["actor_visibility"],
                   scope["memory_profiler"], scope["project_admin"], scope["publish_audit"],
                   scope["sound_asset_tools"], scope["texture_tools"]):
        file = project / "Content/Python" / (module.__name__.replace(".", "/") + ".py")
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text("# fake controller runtime fixture\n", encoding="utf-8")
        monkeypatch.setattr(module, "__file__", str(file))

    class Texture:
        def get_path_name(self):
            return texture_path + ".T_Acceptance"

        def get_editor_property(self, name):
            return properties[name]

        def blueprint_get_size_x(self):
            return 32

        def blueprint_get_size_y(self):
            return 32

    class Sound:
        def get_path_name(self):
            return sound_path + ".SW_Acceptance"

        def get_editor_property(self, name):
            return 0.1

    monkeypatch.setattr(scope["unreal"], "Texture2D", Texture)
    monkeypatch.setattr(scope["unreal"], "SoundWave", Sound)
    monkeypatch.setattr(scope["unreal"], "TextureCompressionSettings", SimpleNamespace(
        TC_GRAYSCALE=properties["compression_settings"]))
    monkeypatch.setattr(scope["unreal"], "TextureGroup", SimpleNamespace(
        TEXTUREGROUP_WORLD=properties["lod_group"]))
    monkeypatch.setattr(scope["unreal"], "TextureMipGenSettings", SimpleNamespace(
        TMGS_FROM_TEXTURE_GROUP=properties["mip_gen_settings"]))
    monkeypatch.setattr(scope["unreal"].EditorAssetLibrary, "load_asset",
                        lambda path: Texture() if path == texture_path else Sound())
    memory_path = project / "Saved/UEFN_Toolbelt/memory_report.json"

    def original_run(tool, **kwargs):
        control.calls.append((tool, kwargs))
        if tool == "memory_scan":
            full = kwargs["scan_path"] == mount
            report = {"project_mount": identity["mount"], "scan_path": kwargs["scan_path"],
                      "full_project_scan": full, "registry_enumeration_complete": True,
                      "textures": [{"path": texture_path + ".T_Acceptance", "width": 32,
                                    "height": 32, "inspection_complete": True}],
                      "summary": {"unknown_assets": 0, "unknown_textures": 0, "unknown_meshes": 0,
                                  "unknown_sounds": 0, "estimate_complete": True, "estimated_vram_mb": 0}}
            memory_path.parent.mkdir(parents=True, exist_ok=True)
            memory_path.write_text(json.dumps(report), encoding="utf-8")
            if control.change_after_memory:
                control.changed_identity = True
            return {"status": "ok", "path": str(memory_path)}
        if tool == "publish_audit":
            if control.missing_memory_check:
                return {"status": "error", "message": "Audit did not produce any checks"}
            report = json.loads(memory_path.read_text())
            return {"checks": {"memory": {"pass": True if report["full_project_scan"] else None}}}
        if tool == "system_backup_project":
            control.backup_count += 1
            path = project / "Saved/UEFN_Toolbelt/backups" / f"fixture_{control.backup_count}.zip"
            path.parent.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(path, "x") as archive:
                for file in (texture_file, sound_file):
                    archive.write(file, file.relative_to(project).as_posix())
            return {"status": "ok", "path": str(path)}
        if tool == "toolbelt_integration_test":
            section = kwargs["sections"][0]
            control.sections.append(section)
            package.run("actor_lock")  # Exercise recording of a nested tool call.
            text = tmp_path / "native-section.txt"
            data = tmp_path / "native-section.json"
            text.write_text("known unsupported check\n", encoding="utf-8")
            data.write_text(json.dumps({"section": section}), encoding="utf-8")
            return {"status": "error", "completed": not control.incomplete, "passed": 0,
                    "failed": 1, "total": 1, "report": str(text), "json_report": str(data)}
        if tool == "actor_lock":
            return {"status": "error", "reason": "actor_lock_unavailable"}
        pytest.fail("Unexpected tool call: " + tool)

    monkeypatch.setattr(package, "run", original_run)
    return SimpleNamespace(main=main, scope=scope, control=control, package=package,
                           original_run=original_run, output=scope["OUTPUT"])


def test_completed_failed_checks_continue_and_inner_calls_are_recorded(controller):
    state = controller.main()
    assert state["completed"] is True and state["fatal"] == ""
    assert controller.control.sections == ["visibility_tools", "lighting_extended", "bulk_ops"]
    assert controller.package.run is controller.original_run
    assert sum(call["depth"] == 1 and call["tool"] == "actor_lock" for call in state["calls"]) == 3
    assert sum(check["passed"] is False for check in state["checks"]) == 3
    assert state["active_calls"] == []
    assert (controller.output / "01_visibility_tools.json").is_file()
    assert (controller.output / "partial-memory.json").is_file()
    assert (controller.output / "full-memory.json").is_file()
    assert (controller.output / "driver.py").read_bytes() == DRIVER.read_bytes()


def test_identity_change_stops_before_any_followup_or_retry(controller):
    controller.control.change_after_memory = True
    state = controller.main()
    assert state["completed"] is False
    assert "identity changed" in state["fatal"]
    assert [call[0] for call in controller.control.calls] == ["memory_scan"]
    assert controller.package.run is controller.original_run


def test_incomplete_section_stops_and_restores_public_run(controller):
    controller.control.incomplete = True
    state = controller.main()
    assert state["completed"] is False
    assert "Incomplete integration section" in state["fatal"]
    assert controller.control.sections == ["visibility_tools"]
    assert controller.package.run is controller.original_run
    assert (controller.output / "01_visibility_tools.json").is_file()


def test_existing_evidence_is_exclusive_and_never_overwritten(controller):
    state = controller.main()
    assert state["completed"] is True
    original = (controller.output / "run.json").read_bytes()
    prior_calls = list(controller.control.calls)
    with pytest.raises(ValueError, match="Preserve prior evidence"):
        controller.main()
    assert (controller.output / "run.json").read_bytes() == original
    assert controller.control.calls == prior_calls


def test_missing_publish_memory_check_is_not_accepted_as_unknown(controller):
    controller.control.missing_memory_check = True
    state = controller.main()
    memory_checks = [check for check in state["checks"] if "publish memory" in check["name"]]
    assert len(memory_checks) == 2
    assert all(check["passed"] is False for check in memory_checks)
    assert all(check["detail"]["memory_check_present"] is False for check in memory_checks)
    assert controller.package.run is controller.original_run
