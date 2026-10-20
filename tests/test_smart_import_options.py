"""Reject FBX options absent from the current editor API."""
from types import SimpleNamespace

import pytest

from UEFN_Toolbelt.tools import smart_importer as importer


class MeshOptions:
    __slots__ = ("combine_meshes", "build_reversed_index_buffer",
                 "generate_lightmap_u_vs", "auto_generate_collision")


@pytest.mark.parametrize("combined", [False, True])
def test_static_import_uses_current_properties(monkeypatch, combined):
    monkeypatch.setattr(importer.unreal, "AssetImportTask", SimpleNamespace)
    monkeypatch.setattr(importer.unreal, "FbxImportUI", lambda: SimpleNamespace(
        static_mesh_import_data=MeshOptions()))
    task = importer._build_import_task("rock.fbx", "/Island/Kit", "Rock", combined)
    assert task.filename == "rock.fbx"
    assert task.destination_path == "/Island/Kit"
    assert task.automated and not task.save
    data = task.options.static_mesh_import_data
    assert data.combine_meshes is combined
    assert data.generate_lightmap_u_vs is True
    assert data.auto_generate_collision is True
    assert task.options.import_materials is False
