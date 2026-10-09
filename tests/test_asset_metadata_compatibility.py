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
