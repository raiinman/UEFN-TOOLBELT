"""An ordinary actor tag must never be reported as a verified Verse tag."""
from types import SimpleNamespace
from unittest.mock import Mock

from UEFN_Toolbelt.tools import selection_utils


def scene(monkeypatch, actors):
    editor = Mock()
    editor.get_all_level_actors.return_value = actors
    monkeypatch.setattr(selection_utils.unreal, "get_editor_subsystem", lambda cls: editor)
    return editor


def test_verse_lookup_reports_unsupported_without_changing_selection(monkeypatch):
    editor = scene(monkeypatch, [SimpleNamespace(tags=["rb_room_placer"], get_actor_label=lambda: "Ordinary actor tag")])
    result = selection_utils.run_select_by_verse_tag("rb_room_placer")
    assert result["status"] == "error"
    assert result["reason"] == "verse_tags_unavailable"
    assert "count" not in result
    editor.set_selected_level_actors.assert_not_called()


def test_explicit_actor_scope_matches_native_names(monkeypatch):
    class NativeName:
        def __str__(self):
            return "rb_room_placer"

    matched = SimpleNamespace(tags=[NativeName()], get_actor_label=lambda: "Matched")
    other = SimpleNamespace(tags=["other"], get_actor_label=lambda: "Other")
    editor = scene(monkeypatch, [matched, other])
    result = selection_utils.run_select_by_verse_tag("rb_room_placer", tag_scope="actor")
    assert result == {"status": "ok", "tag_scope": "actor", "count": 1, "labels": ["Matched"]}
    editor.set_selected_level_actors.assert_called_once_with([matched])


def test_invalid_scope_rejects_without_editor_contact(monkeypatch):
    editor = scene(monkeypatch, [])
    result = selection_utils.run_select_by_verse_tag("test", tag_scope="anything")
    assert result["status"] == "error"
    editor.get_all_level_actors.assert_not_called()


def test_unreadable_actor_tags_are_unknown_without_partial_selection(monkeypatch):
    class Unreadable:
        @property
        def tags(self):
            raise RuntimeError("unavailable")

    matched = SimpleNamespace(tags=["test"], get_actor_label=lambda: "Matched before failure")
    editor = scene(monkeypatch, [matched, Unreadable()])
    result = selection_utils.run_select_by_verse_tag("test", tag_scope="actor")
    assert result["status"] == "error"
    assert result["reason"] == "actor_tags_unavailable"
    assert "count" not in result
    editor.set_selected_level_actors.assert_not_called()
