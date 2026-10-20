"""Asset tools must work with current metadata, without removed legacy fields."""

import ast
import importlib
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

TOOLS = Path(__file__).resolve().parents[1] / "Content/Python/UEFN_Toolbelt/tools"
MODULES = (
    "animation_tools", "audio_design_tools", "blueprint_tools", "curve_tools",
    "datatable_tools", "enhanced_input_tools", "sound_asset_tools", "texture_tools",
)


@pytest.mark.parametrize("module_name,function_name,loads_asset", [
    ("animation_tools", "run_anim_list_blend_spaces", False),
    ("animation_tools", "run_anim_list_sequences", True),
    ("audio_design_tools", "run_audio_list_metasounds", True),
    ("audio_design_tools", "run_audio_list_synesthesia", False),
    ("curve_tools", "run_curve_list", False),
    ("sound_asset_tools", "run_sound_asset_list", False),
])
def test_current_metadata_is_listed(module_name, function_name, loads_asset, monkeypatch):
    module = importlib.import_module(f"UEFN_Toolbelt.tools.{module_name}")
    registry = MagicMock()
    registry.get_assets.return_value = [SimpleNamespace(
        asset_name="Example", package_name="/Island/Example",
        asset_class_path=SimpleNamespace(asset_name="ExampleClass"),
        get_tag_value=lambda _: None,
    )]
    monkeypatch.setattr(module, "resolve_scan_path", lambda _: "/Island")
    monkeypatch.setattr(module.unreal.AssetRegistryHelpers, "get_asset_registry", lambda: registry)
    load_asset = MagicMock(return_value=None)
    monkeypatch.setattr(module.unreal.EditorAssetLibrary, "load_asset", load_asset)
    result = getattr(module, function_name)()
    assert result["status"] == "ok", result
    assert result["count"] == 1
    if loads_asset:
        load_asset.assert_called_once_with("/Island/Example.Example")


@pytest.mark.parametrize("module_name", MODULES)
def test_asset_tools_do_not_read_removed_metadata_fields(module_name):
    tree = ast.parse((TOOLS / f"{module_name}.py").read_text(encoding="utf-8"))
    legacy_reads = [node.lineno for node in ast.walk(tree)
                    if isinstance(node, ast.Attribute) and node.attr in {"object_path", "asset_class"}]
    assert not legacy_reads, f"Legacy AssetData fields at {module_name}:{legacy_reads}"


def test_blueprint_with_unreadable_compile_status_is_not_reported_clean(monkeypatch):
    module = importlib.import_module("UEFN_Toolbelt.tools.blueprint_tools")

    class Blueprint:
        def get_editor_property(self, name):
            raise AttributeError("compile status unavailable")

    registry = MagicMock()
    registry.get_assets.return_value = [SimpleNamespace(asset_name="Example", package_name="/Island/Example")]
    monkeypatch.setattr(module, "resolve_scan_path", lambda _: "/Island")
    monkeypatch.setattr(module.unreal.AssetRegistryHelpers, "get_asset_registry", lambda: registry)
    monkeypatch.setattr(module.unreal, "Blueprint", Blueprint)
    monkeypatch.setattr(module.unreal.EditorAssetLibrary, "load_asset", lambda _: Blueprint())
    result = module.run_blueprint_audit()
    assert result["clean"] == 0
    assert result["issues"] == 1
    assert "unavailable" in result["issue_list"][0]["issue"]


@pytest.mark.parametrize("compile_status,clean", [
    ("BlueprintStatus.BS_UP_TO_DATE", 1),
    ("BS_UP_TO_DATE", 1),
    ("<BlueprintStatus.BS_UP_TO_DATE: 0>", 1),
    ("BlueprintStatus.BS_UP_TO_DATE_WITH_WARNINGS", 0),
    ("BlueprintStatus.BS_DIRTY", 0),
    ("BlueprintStatus.BS_UNKNOWN", 0),
    ("BlueprintStatus.BS_BEING_CREATED", 0),
    ("BlueprintStatus.BS_ERROR", 0),
    ("unexpected", 0),
    ("<BlueprintStatus.BS_DIRTY: 1>", 0),
    ("<BlueprintStatus.BS_UNKNOWN: 0>", 0),
    ("<BlueprintStatus.BS_UP_TO_DATE_WITH_WARNINGS: 5>", 0),
    ("garbage BlueprintStatus.BS_UP_TO_DATE", 0),
])
def test_blueprint_clean_requires_known_up_to_date_state(monkeypatch, compile_status, clean):
    module = importlib.import_module("UEFN_Toolbelt.tools.blueprint_tools")
    monkeypatch.setattr(module.unreal, "BlueprintStatus", None)

    class Blueprint:
        def get_editor_property(self, name):
            return compile_status

    registry = MagicMock()
    registry.get_assets.return_value = [SimpleNamespace(asset_name="Example", package_name="/Island/Example")]
    monkeypatch.setattr(module, "resolve_scan_path", lambda _: "/Island")
    monkeypatch.setattr(module.unreal.AssetRegistryHelpers, "get_asset_registry", lambda: registry)
    monkeypatch.setattr(module.unreal, "Blueprint", Blueprint)
    monkeypatch.setattr(module.unreal.EditorAssetLibrary, "load_asset", lambda _: Blueprint())
    result = module.run_blueprint_audit()
    assert result["clean"] == clean
    assert result["issues"] == 1 - clean


def test_blueprint_native_enum_equality_is_used_without_string_parsing(monkeypatch):
    module = importlib.import_module("UEFN_Toolbelt.tools.blueprint_tools")

    class NativeEnumValue:
        def __str__(self):
            raise AssertionError("Native enum success must use equality")

    up_to_date = NativeEnumValue()
    monkeypatch.setattr(module.unreal, "BlueprintStatus", SimpleNamespace(BS_UP_TO_DATE=up_to_date))
    assert module._is_blueprint_up_to_date(up_to_date) is True
    assert module._is_blueprint_up_to_date(NativeEnumValue()) is False
    assert module._is_blueprint_up_to_date("BS_UP_TO_DATE") is False

    class Blueprint:
        def get_editor_property(self, name):
            return up_to_date

    registry = MagicMock()
    registry.get_assets.return_value = [SimpleNamespace(asset_name="Example", package_name="/Island/Example")]
    monkeypatch.setattr(module, "resolve_scan_path", lambda _: "/Island")
    monkeypatch.setattr(module.unreal.AssetRegistryHelpers, "get_asset_registry", lambda: registry)
    monkeypatch.setattr(module.unreal, "Blueprint", Blueprint)
    monkeypatch.setattr(module.unreal.EditorAssetLibrary, "load_asset", lambda _: Blueprint())
    result = module.run_blueprint_audit()
    assert result["clean"] == 1
    assert result["issues"] == 0
