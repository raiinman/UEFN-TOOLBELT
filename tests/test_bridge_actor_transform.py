"""Static cooked props need the editor transform API; refusal is not success."""
from types import SimpleNamespace

import pytest

from UEFN_Toolbelt.tools import mcp_bridge as bridge


class Vector:
    def __init__(self, *, x=0.0, y=0.0, z=0.0):
        self.x, self.y, self.z = x, y, z


class Rotator:
    def __init__(self, *, pitch=0.0, yaw=0.0, roll=0.0):
        self.pitch, self.yaw, self.roll = pitch, yaw, roll

    def quaternion(self):
        return self

    def rotator(self):
        return self


class Transform:
    def __init__(self, *, translation=None, rotation=None, scale3d=None):
        self.translation = translation if translation is not None else Vector()
        self.rotation = rotation if rotation is not None else Rotator()
        self.scale3d = scale3d if scale3d is not None else Vector(x=1, y=1, z=1)


class StaticCookedActor:
    def __init__(self):
        self.transform = Transform(
            translation=Vector(x=11, y=22, z=33),
            rotation=Rotator(pitch=4, yaw=5, roll=6),
            scale3d=Vector(x=2, y=3, z=4),
        )

    def get_path_name(self):
        return "/Riftbloom/Map.PlayerSpawner"

    def get_actor_label(self):
        return "PlayerSpawner"

    def get_actor_transform(self):
        return self.transform

    def get_actor_location(self):
        return self.transform.translation

    def get_actor_rotation(self):
        return self.transform.rotation

    def get_actor_scale3d(self):
        return self.transform.scale3d

    def set_actor_location(self, *args):
        return False

    def set_actor_rotation(self, *args):
        return False

    def set_actor_scale3d(self, *args):
        pass


def snapshot(actor):
    location = actor.get_actor_location()
    rotation = actor.get_actor_rotation()
    scale = actor.get_actor_scale3d()
    return {
        "location": [location.x, location.y, location.z],
        "rotation": [rotation.pitch, rotation.yaw, rotation.roll],
        "scale": [scale.x, scale.y, scale.z],
    }


@pytest.fixture
def editor(monkeypatch):
    actor = StaticCookedActor()
    serialized = []

    class EditorSubsystem:
        move_allowed = True

        def get_all_level_actors(self):
            return [actor]

        def set_actor_transform(self, target, world_transform):
            assert target is actor
            if self.move_allowed:
                actor.transform = world_transform
            return self.move_allowed

    subsystem = EditorSubsystem()

    def serialize_actor(target):
        serialized.append(target)
        return snapshot(target)

    monkeypatch.setattr(bridge.unreal, "Vector", Vector)
    monkeypatch.setattr(bridge.unreal, "Rotator", Rotator)
    monkeypatch.setattr(bridge.unreal, "Transform", Transform)
    monkeypatch.setattr(bridge.unreal, "get_editor_subsystem", lambda cls: subsystem)
    monkeypatch.setattr(bridge, "_serialize_actor", serialize_actor)
    return SimpleNamespace(actor=actor, subsystem=subsystem, serialized=serialized)


@pytest.mark.parametrize("changes", [
    {"location": [100, 200, 300], "rotation": [10, 20, 30], "scale": [5, 6, 7]},
    {"location": [100, 200, 300]},
    {"rotation": [10, 20, 30]},
    {"scale": [5, 6, 7]},
])
def test_editor_transform_moves_static_actor_and_preserves_omitted_parts(editor, changes):
    expected = snapshot(editor.actor) | changes

    result = bridge._c_set_actor_transform(editor.actor.get_path_name(), **changes)

    assert snapshot(editor.actor) == expected
    assert result["actor"] == expected


def test_refused_editor_transform_reports_error_without_serializing_success(editor):
    editor.subsystem.move_allowed = False
    before = snapshot(editor.actor)

    try:
        result = bridge._c_set_actor_transform("PlayerSpawner", rotation=[10, 20, 30])
    except RuntimeError as error:
        assert str(error)
    else:
        assert result.get("error"), "A refused transform must not return an actor as success"

    assert editor.serialized == []
    assert snapshot(editor.actor) == before
