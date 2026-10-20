"""Actor locking counts only independently observed requested property states."""

from contextlib import nullcontext
from types import SimpleNamespace

import pytest

from UEFN_Toolbelt.tools import actor_visibility as visibility


class Actor:
    def __init__(self, state=False, property_name="lock_location", mode="normal"):
        self.state = state
        self.property_name = property_name
        self.mode = mode
        self.writes = []

    def get_actor_label(self):
        return "Fixture"

    def get_editor_property(self, name):
        if name != self.property_name:
            raise AttributeError("property unavailable")
        if self.writes and self.mode == "readback_error":
            raise AttributeError("readback unavailable")
        return self.state

    def set_editor_property(self, name, value):
        self.writes.append((name, value))
        if self.mode == "setter_error":
            raise RuntimeError("native setter refused")
        if self.mode != "noop":
            self.state = value


@pytest.fixture
def selected(monkeypatch):
    monkeypatch.setattr(visibility.unreal, "ScopedEditorTransaction", lambda _: nullcontext())

    def configure(*actors):
        monkeypatch.setattr(visibility, "_sub", lambda: SimpleNamespace(
            get_selected_level_actors=lambda: list(actors)))

    return configure


@pytest.mark.parametrize("desired", [True, False])
@pytest.mark.parametrize("property_name", ["lock_location", "bLockLocation", "bLocked"])
def test_verified_lock_and_unlock_transition(selected, desired, property_name):
    actor = Actor(state=not desired, property_name=property_name)
    selected(actor)
    run = visibility.run_actor_lock if desired else visibility.run_actor_unlock
    result = run()
    assert result["status"] == "ok"
    assert result["locked" if desired else "unlocked"] == 1
    assert result["changed"] == 1 and result["failed"] == 0
    assert result["actors"][0]["before"] is not desired
    assert result["actors"][0]["after"] is desired
    assert actor.writes == [(property_name, desired)]


def test_no_readable_lock_property_refuses_without_any_write(selected):
    actor = Actor(property_name="unavailable")
    selected(actor)
    result = visibility.run_actor_lock()
    assert result["status"] == "error"
    assert result["reason"] == "actor_lock_unavailable"
    assert result["locked"] == 0 and result["failed"] == 1
    assert actor.writes == []


@pytest.mark.parametrize("mode,reason", [
    ("setter_error", "actor_lock_set_failed"),
    ("noop", "actor_lock_readback_failed"),
    ("readback_error", "actor_lock_readback_failed"),
])
def test_setter_or_unverified_readback_never_counts_as_locked(selected, mode, reason):
    actor = Actor(mode=mode)
    selected(actor)
    result = visibility.run_actor_lock()
    assert result["status"] == "error"
    assert result["locked"] == 0 and result["failed"] == 1
    assert result["actors"][0]["reason"] == reason
    assert result["possible_partial_changes"] is True


def test_mixed_selection_preserves_success_and_failed_actor_detail(selected):
    good = Actor()
    unsupported = Actor(property_name="unavailable")
    selected(good, unsupported)
    result = visibility.run_actor_lock()
    assert result["status"] == "error"
    assert result["locked"] == result["failed"] == result["changed"] == 1
    assert result["possible_partial_changes"] is True
    assert good.state is True
    assert unsupported.writes == []


def test_already_requested_state_is_observed_without_claiming_a_change(selected):
    actor = Actor(state=True)
    selected(actor)
    result = visibility.run_actor_lock()
    assert result["status"] == "ok"
    assert result["locked"] == 1 and result["changed"] == 0
    assert result["actors"][0]["already_in_state"] is True
    assert actor.writes == []
