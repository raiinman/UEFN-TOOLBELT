"""Uninspected asset metrics cannot become zero-cost or clean memory evidence."""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from UEFN_Toolbelt.tools import memory_profiler as memory


def unavailable(*args, **kwargs):
    raise AttributeError("native inspection unavailable")


def test_unreadable_texture_dimensions_have_no_memory_estimate():
    result = memory._texture_info(SimpleNamespace(get_editor_property=unavailable))
    assert result["severity"] == "unknown"
    assert result["width"] is result["height"] is result["estimated_vram_kb"] is None
    assert result["inspection_complete"] is False


def test_valid_source_art_fallback_retains_observed_dimensions():
    result = memory._texture_info(SimpleNamespace(
        get_editor_property=unavailable, source_art_width=256, source_art_height=512))
    assert result["width"] == 256 and result["height"] == 512
    assert result["estimated_vram_kb"] == 512
    assert result["inspection_complete"] is True


def test_documented_texture_methods_work_without_legacy_properties():
    asset = SimpleNamespace(blueprint_get_size_x=lambda: 32, blueprint_get_size_y=lambda: 64,
                            get_editor_property=lambda _: pytest.fail("Legacy property was consulted"))
    result = memory._texture_info(asset)
    assert result["width"] == 32 and result["height"] == 64
    assert result["estimated_vram_kb"] == 8
    assert result["inspection_complete"] is True


@pytest.mark.parametrize("failure", ["raises", "zero", "invalid"])
def test_failed_texture_methods_can_use_checked_legacy_properties(failure):
    def method():
        if failure == "raises":
            raise AttributeError("method unavailable")
        return 0 if failure == "zero" else "32"

    asset = SimpleNamespace(blueprint_get_size_x=method, blueprint_get_size_y=method,
                            get_editor_property=lambda name: 32 if name == "blueprint_width" else 64)
    result = memory._texture_info(asset)
    assert result["width"] == 32 and result["height"] == 64
    assert result["inspection_complete"] is True


def test_unavailable_texture_methods_and_properties_remain_unknown():
    asset = SimpleNamespace(blueprint_get_size_x=unavailable, blueprint_get_size_y=unavailable,
                            get_editor_property=unavailable)
    result = memory._texture_info(asset)
    assert result["inspection_complete"] is False
    assert result["width"] is result["height"] is None


@pytest.mark.parametrize("value", [None, 0, -1, True, "2048", float("nan"), float("inf")])
def test_invalid_texture_measurement_is_unknown(value):
    result = memory._texture_info(SimpleNamespace(get_editor_property=lambda _: value))
    assert result["severity"] == "unknown"
    assert result["estimated_vram_kb"] is None


def test_unreadable_mesh_lods_are_not_reported_missing(monkeypatch):
    monkeypatch.setattr(memory.unreal, "get_editor_subsystem", lambda _: SimpleNamespace(
        get_lod_count=unavailable, get_number_verts=unavailable))
    result = memory._mesh_info(object())
    assert result["lod_count"] is result["missing_lods"] is result["approx_verts"] is None
    assert result["severity"] == "unknown"


def test_known_critical_mesh_survives_other_unavailable_metrics(monkeypatch):
    monkeypatch.setattr(memory.unreal, "get_editor_subsystem", lambda _: SimpleNamespace(
        get_lod_count=unavailable, get_number_verts=lambda *args: 300_000))
    result = memory._mesh_info(object())
    assert result["severity"] == "critical"
    assert result["inspection_complete"] is False
    assert result["missing_lods"] is None


@pytest.mark.parametrize("value", [None, -1, True, "10", float("nan"), float("inf")])
def test_invalid_sound_duration_is_unknown(value):
    result = memory._sound_info(SimpleNamespace(get_editor_property=lambda _: value))
    assert result["duration_secs"] is None
    assert result["severity"] == "unknown"


def test_zero_sound_duration_is_an_actual_observation():
    result = memory._sound_info(SimpleNamespace(get_editor_property=lambda _: 0.0))
    assert result["duration_secs"] == 0
    assert result["severity"] == "ok"
    assert result["inspection_complete"] is True


@pytest.fixture
def unknown_inventory(monkeypatch):
    asset = SimpleNamespace(get_editor_property=unavailable)
    monkeypatch.setattr(memory, "resolve_scan_path", lambda _: "/Island")
    monkeypatch.setattr(memory, "detect_project_mount", lambda: "Island")
    monkeypatch.setattr(memory, "_list_assets_of_class", lambda path, kind: [(f"/Island/{kind}", asset)])
    monkeypatch.setattr(memory.unreal, "get_editor_subsystem", lambda _: SimpleNamespace(
        get_lod_count=unavailable, get_number_verts=unavailable))
    reports = []
    messages = []
    monkeypatch.setattr(memory, "_write_report", lambda report: reports.append(report) or "report.json")
    monkeypatch.setattr(memory, "log_info", messages.append)
    return reports, messages


def test_full_report_marks_unknowns_and_never_claims_publish_readiness(unknown_inventory):
    reports, messages = unknown_inventory
    result = memory.run_memory_scan()
    summary = result["summary"]
    assert summary["unknown_assets"] == 3
    assert summary["unknown_textures"] == summary["unknown_meshes"] == summary["unknown_sounds"] == 1
    assert summary["estimate_complete"] is False
    assert summary["estimated_vram_mb"] is None
    assert summary["meshes_missing_lods"] == 0
    assert reports[0]["textures"][0]["estimated_vram_kb"] is None
    assert reports[0]["project_mount"] == "Island"
    assert reports[0]["full_project_scan"] is True
    assert reports[0]["registry_enumeration_complete"] is True
    assert "Good to publish" not in "\n".join(messages)


def test_texture_scan_reports_unknown_without_claiming_all_small(unknown_inventory):
    _, messages = unknown_inventory
    result = memory.run_memory_scan_textures()
    assert result["count"] == 0
    assert len(result["unknown"]) == 1
    assert "All textures are" not in "\n".join(messages)


def test_mesh_scan_reports_unavailable_lods_without_autofix_advice(unknown_inventory):
    _, messages = unknown_inventory
    result = memory.run_memory_scan_meshes()
    assert result["count"] == 1
    assert result["unknown_count"] == 1
    assert result["offenders"][0]["missing_lods"] is None
    assert "memory_autofix_lods" not in "\n".join(messages)


def test_ranked_report_handles_unknown_metrics_without_formatting_failure(unknown_inventory):
    result = memory.run_memory_top_offenders()
    assert len(result["unknown_textures"]) == 1
    assert len(result["unknown_meshes"]) == 1
    assert result["textures"] == []
    assert result["meshes"] == []


def test_metadata_inventory_retains_failed_texture_load(monkeypatch):
    metadata = SimpleNamespace(asset_name="Texture", package_name="/Island/Texture",
                               asset_class_path=SimpleNamespace(asset_name="Texture2D"))
    registry = SimpleNamespace(get_assets_by_path=lambda *args, **kwargs: [metadata])
    monkeypatch.setattr(memory.unreal.AssetRegistryHelpers, "get_asset_registry", lambda: registry)
    monkeypatch.setattr(memory, "load_asset", lambda _: None)
    monkeypatch.setattr(memory, "resolve_scan_path", lambda _: "/Island")
    monkeypatch.setattr(memory, "detect_project_mount", lambda: "Island")
    reports = []
    monkeypatch.setattr(memory, "_write_report", lambda report: reports.append(report) or "report.json")
    result = memory.run_memory_scan()
    assert result["summary"]["total_textures"] == 1
    assert result["summary"]["unknown_textures"] == 1
    assert result["summary"]["estimated_vram_mb"] is None
    assert result["summary"]["estimate_complete"] is False
    assert reports[0]["textures"][0]["load_failed"] is True
    assert reports[0]["textures"][0]["path"] == "/Island/Texture.Texture"


@pytest.mark.parametrize("metadata", [None, [SimpleNamespace()]])
def test_unavailable_or_unreadable_registry_never_writes_complete_report(monkeypatch, metadata):
    registry = SimpleNamespace(get_assets_by_path=lambda *args, **kwargs: metadata)
    monkeypatch.setattr(memory.unreal.AssetRegistryHelpers, "get_asset_registry", lambda: registry)
    monkeypatch.setattr(memory, "resolve_scan_path", lambda _: "/Island")
    monkeypatch.setattr(memory, "_write_report", lambda _: pytest.fail("Incomplete inventory was persisted"))
    result = memory.run_memory_scan()
    assert result["status"] == "error"
    assert result["reason"] == "asset_registry_unavailable"


def test_subfolder_scan_cannot_become_full_project_evidence(unknown_inventory, monkeypatch):
    reports, _ = unknown_inventory
    monkeypatch.setattr(memory, "resolve_scan_path", lambda _: "/Island/SmallFolder")
    memory.run_memory_scan()
    assert reports[0]["full_project_scan"] is False


def test_report_written_to_native_project_saved_not_shared_engine_saved(tmp_path, monkeypatch):
    project = tmp_path / "Island"
    monkeypatch.setattr(memory, "native_project_dir", lambda: str(project))
    monkeypatch.setattr(memory.unreal.Paths, "project_saved_dir", lambda: pytest.fail("Shared path used"))
    report = {"project_mount": "Island", "scan_path": "/Island"}
    path = Path(memory._write_report(report))
    assert path == project / "Saved/UEFN_Toolbelt/memory_report.json"
    assert json.loads(path.read_text()) == report


def test_failed_atomic_report_write_preserves_prior_bytes(tmp_path, monkeypatch):
    monkeypatch.setattr(memory, "native_project_dir", lambda: str(tmp_path))
    path = Path(memory._write_report({"old": True}))
    original = path.read_bytes()

    def refuse(*args, **kwargs):
        raise PermissionError("replacement refused")

    monkeypatch.setattr(memory.os, "replace", refuse)
    with pytest.raises(PermissionError):
        memory._write_report({"new": True})
    assert path.read_bytes() == original
    assert list(path.parent.glob(".memory.*.tmp")) == []
