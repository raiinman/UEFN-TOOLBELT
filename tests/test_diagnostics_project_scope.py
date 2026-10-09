"""The Verse diagnostic scans the active island, not a historical test project."""

from types import SimpleNamespace
from unittest.mock import MagicMock

from UEFN_Toolbelt import diagnostics


def test_verse_asset_audit_uses_current_project_and_returns_bounded_matches(monkeypatch):
    registry = MagicMock()
    registry.get_assets_by_path.return_value = [
        SimpleNamespace(asset_name=f"verse_device_{i}", package_name=f"/Island/device_{i}",
                        asset_class_path=SimpleNamespace(asset_name="Blueprint"))
        for i in range(205)
    ]
    monkeypatch.setattr(diagnostics.unreal.AssetRegistryHelpers, "get_asset_registry", lambda: registry)
    monkeypatch.setattr(diagnostics, "resolve_scan_path", lambda _: "/Island", raising=False)
    result = diagnostics.audit_verse_assets()
    registry.get_assets_by_path.assert_called_once_with("/Island", recursive=True)
    assert result["status"] == "ok"
    assert result["found"] is True
    assert result["count"] == 205
    assert len(result["assets"]) == 200
    assert result["truncated"] is True
