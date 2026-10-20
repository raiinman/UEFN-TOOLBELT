"""Search works without mutating UEFN's immutable ARFilter properties."""
from types import SimpleNamespace

from UEFN_Toolbelt.tools import mcp_bridge as bridge


def test_registry_search_filters_class_on_metadata(monkeypatch):
    material = SimpleNamespace(asset_class_path=SimpleNamespace(asset_name="Material"))
    mesh = SimpleNamespace(asset_class_path=SimpleNamespace(asset_name="StaticMesh"))
    calls = []
    class Registry:
        def get_assets_by_path(self, path, recursive):
            calls.append((path, recursive))
            return [material, mesh]
    monkeypatch.setattr(bridge.unreal, "AssetRegistryHelpers", SimpleNamespace(
        get_asset_registry=lambda: Registry()))
    monkeypatch.setattr(bridge.unreal, "ARFilter", lambda: object())
    monkeypatch.setattr(bridge, "_serialize", lambda asset: str(asset.asset_class_path.asset_name))
    result = bridge._c_search_assets("StaticMesh", "/Island/Kit", True)
    assert result["assets"] == ["StaticMesh"]
    assert result["count"] == 1
    assert calls == [("/Island/Kit", True)]
