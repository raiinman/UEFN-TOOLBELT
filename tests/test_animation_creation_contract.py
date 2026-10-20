"""Montage creation refuses unsupported APIs and preserves honest partial state."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from UEFN_Toolbelt.tools import animation_tools as animation


@pytest.fixture
def montage_api(monkeypatch):
    skeleton = SimpleNamespace(get_name=lambda: "Skeleton")

    class AnimSequence:
        def get_editor_property(self, name):
            return skeleton

        def get_name(self):
            return "Sequence"

    class AnimMontage:
        def get_editor_property(self, name):
            return skeleton

    class AnimMontageFactory:
        def set_editor_property(self, name, value):
            self.target_skeleton = value

    create = MagicMock(return_value=AnimMontage())
    load = MagicMock(side_effect=[AnimSequence(), AnimMontage()])
    save = MagicMock(return_value=True)
    monkeypatch.setattr(animation.unreal, "AnimSequence", AnimSequence)
    monkeypatch.setattr(animation.unreal, "AnimMontage", AnimMontage)
    monkeypatch.setattr(animation.unreal, "AnimMontageFactory", AnimMontageFactory)
    monkeypatch.setattr(animation.unreal, "AssetTools", SimpleNamespace(create_asset=create))
    monkeypatch.setattr(animation.unreal.AssetToolsHelpers, "get_asset_tools",
                        lambda: SimpleNamespace(create_asset=create))
    monkeypatch.setattr(animation.unreal.EditorAssetLibrary, "load_asset", load)
    monkeypatch.setattr(animation, "save_asset", save)
    monkeypatch.setattr(animation, "resolve_content_path", lambda *args: "/Island/Animations")
    return SimpleNamespace(create=create, load=load, save=save, sequence=AnimSequence,
                           montage=AnimMontage, skeleton=skeleton)


@pytest.mark.parametrize("api", ["AnimSequence", "AnimMontage", "AnimMontageFactory", "AssetTools"])
def test_missing_native_api_refuses_before_any_asset_operation(montage_api, monkeypatch, api):
    monkeypatch.setattr(animation.unreal, api, None)
    result = animation.run_anim_create_montage(sequence_path="/Island/Sequence")
    assert result["status"] == "error"
    assert result["reason"] == "engine_api_unavailable"
    montage_api.load.assert_not_called()
    montage_api.create.assert_not_called()


def test_wrong_source_class_is_rejected_before_creation(montage_api):
    montage_api.load.side_effect = [object()]
    result = animation.run_anim_create_montage(sequence_path="/Island/Sequence")
    assert result["status"] == "error"
    assert "not an AnimSequence" in result["message"]
    montage_api.create.assert_not_called()


def test_save_failure_retains_created_asset_information(montage_api):
    montage_api.save.return_value = False
    result = animation.run_anim_create_montage(sequence_path="/Island/Sequence")
    assert result["status"] == "error"
    assert result["reason"] == "asset_save_failed"
    assert result["created"] is True
    assert result["saved"] is False
    assert result["readback_verified"] is False
    assert result["path"] == "/Island/Animations/AM_Sequence"
    montage_api.load.assert_called_once_with("/Island/Sequence")


def test_saved_asset_without_readback_is_error(montage_api):
    montage_api.load.side_effect = [montage_api.sequence(), None]
    result = animation.run_anim_create_montage(sequence_path="/Island/Sequence")
    assert result["status"] == "error"
    assert result["reason"] == "asset_readback_failed"
    assert result["created"] is result["saved"] is True
    assert result["readback_verified"] is False


def test_readback_exception_retains_saved_state(montage_api):
    montage_api.load.side_effect = [montage_api.sequence(), RuntimeError("readback failed")]
    result = animation.run_anim_create_montage(sequence_path="/Island/Sequence")
    assert result["status"] == "error"
    assert result["created"] is result["saved"] is True
    assert result["path"] == "/Island/Animations/AM_Sequence"


def test_created_saved_montage_and_skeleton_are_verified(montage_api):
    result = animation.run_anim_create_montage(sequence_path="/Island/Sequence")
    assert result["status"] == "ok"
    assert result["created"] is result["saved"] is result["readback_verified"] is True
    assert montage_api.create.call_args.args[3].target_skeleton is montage_api.skeleton
    assert montage_api.load.call_args_list[1].args == (result["path"],)
