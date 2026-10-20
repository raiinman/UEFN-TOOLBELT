"""
UEFN TOOLBELT — Actor Visibility & Lock Tools
==============================================
Hide, isolate, reveal, and lock actors from Python.
Built for fast-moving teams working in crowded shared levels.

Use cases:
  • Isolate your section while teammates work elsewhere
  • Fold away Zones/Signs/Devices while placing props
  • Lock final assets so they can't be dragged out of place
  • One command to restore everything when done
"""

from __future__ import annotations

import unreal

from ..core import log_error, log_info
from ..registry import register_tool


def _sub():
    return unreal.get_editor_subsystem(unreal.EditorActorSubsystem)


# ── Visibility ─────────────────────────────────────────────────────────────────

@register_tool(
    name="actor_hide",
    category="Visibility",
    description=(
        "Hide selected actors in the editor viewport without deleting them. "
        "Reversible — use actor_show or actor_show_all to restore."
    ),
    tags=["visibility", "hide", "actor", "selection", "editor"],
)
def run_actor_hide(**kwargs) -> dict:
    """Hide all currently selected actors in the editor viewport."""
    try:
        sub = _sub()
        actors = sub.get_selected_level_actors()
        if not actors:
            return {"status": "error", "error": "No actors selected."}
        with unreal.ScopedEditorTransaction("Hide Actors"):
            for a in actors:
                a.set_is_temporarily_hidden_in_editor(True)
        log_info(f"actor_hide: hid {len(actors)} actor(s)")
        return {
            "status": "ok",
            "hidden": len(actors),
            "labels": [a.get_actor_label() for a in actors],
            "tip": "Run actor_show_all to restore all hidden actors at once.",
        }
    except Exception as e:
        log_error(f"actor_hide failed: {e}")
        return {"status": "error", "error": str(e)}


@register_tool(
    name="actor_show",
    category="Visibility",
    description=(
        "Unhide currently selected actors. "
        "Use actor_show_all to restore every hidden actor in the level at once."
    ),
    tags=["visibility", "show", "unhide", "actor", "selection"],
)
def run_actor_show(**kwargs) -> dict:
    """Make the currently selected hidden actors visible again."""
    try:
        sub = _sub()
        actors = sub.get_selected_level_actors()
        if not actors:
            return {"status": "error", "error": "No actors selected."}
        with unreal.ScopedEditorTransaction("Show Actors"):
            for a in actors:
                a.set_is_temporarily_hidden_in_editor(False)
        log_info(f"actor_show: showed {len(actors)} actor(s)")
        return {"status": "ok", "shown": len(actors), "labels": [a.get_actor_label() for a in actors]}
    except Exception as e:
        log_error(f"actor_show failed: {e}")
        return {"status": "error", "error": str(e)}


@register_tool(
    name="actor_isolate",
    category="Visibility",
    description=(
        "Hide every actor in the level EXCEPT the current selection. "
        "Focus on exactly your section. Run actor_show_all when done."
    ),
    tags=["visibility", "isolate", "hide", "section", "focus"],
)
def run_actor_isolate(**kwargs) -> dict:
    """
    Hide all level actors except those currently selected.
    Workflow: select what you want to see → actor_isolate → work → actor_show_all.
    """
    try:
        sub = _sub()
        selected = sub.get_selected_level_actors()
        if not selected:
            return {
                "status": "error",
                "error": "No actors selected. Select what you want to KEEP visible, then run this.",
            }
        keep = {id(a) for a in selected}
        all_actors = sub.get_all_level_actors()
        to_hide = [a for a in all_actors if id(a) not in keep]
        with unreal.ScopedEditorTransaction("Isolate Selection"):
            for a in to_hide:
                a.set_is_temporarily_hidden_in_editor(True)
        log_info(f"actor_isolate: {len(selected)} visible, {len(to_hide)} hidden")
        return {
            "status": "ok",
            "visible": len(selected),
            "hidden": len(to_hide),
            "tip": "Run actor_show_all to restore full level visibility.",
        }
    except Exception as e:
        log_error(f"actor_isolate failed: {e}")
        return {"status": "error", "error": str(e)}


@register_tool(
    name="actor_show_all",
    category="Visibility",
    description=(
        "Restore visibility for every hidden actor in the level. "
        "The universal undo for actor_hide, actor_isolate, and folder_hide."
    ),
    tags=["visibility", "show", "restore", "unhide", "all", "reset"],
)
def run_actor_show_all(**kwargs) -> dict:
    """Un-hide every actor in the level — the global 'get everything back' command."""
    try:
        sub = _sub()
        restored = 0
        with unreal.ScopedEditorTransaction("Show All Actors"):
            for a in sub.get_all_level_actors():
                try:
                    if a.is_temporarily_hidden_in_editor():
                        a.set_is_temporarily_hidden_in_editor(False)
                        restored += 1
                except Exception:
                    continue
        log_info(f"actor_show_all: restored {restored} actor(s)")
        return {"status": "ok", "restored": restored}
    except Exception as e:
        log_error(f"actor_show_all failed: {e}")
        return {"status": "error", "error": str(e)}


# ── Folder visibility ──────────────────────────────────────────────────────────

@register_tool(
    name="folder_hide",
    category="Visibility",
    description=(
        "Hide all actors in a named World Outliner folder. "
        "Pair with folder_show or actor_show_all to restore."
    ),
    tags=["visibility", "hide", "folder", "outliner", "section"],
)
def run_folder_hide(folder_name: str = "", **kwargs) -> dict:
    """
    Hide all actors whose World Outliner folder path starts with folder_name.

    Args:
        folder_name: Folder path, e.g. 'Zones', 'Props/Trees', 'Devices'
    """
    if not folder_name:
        return {"status": "error", "error": "folder_name is required. Example: 'Zones' or 'Props/Trees'"}
    try:
        sub = _sub()
        target = folder_name.strip("/").lower()
        hidden = 0
        with unreal.ScopedEditorTransaction(f"Hide Folder: {folder_name}"):
            for a in sub.get_all_level_actors():
                try:
                    fp = str(a.get_folder_path()).strip("/").lower()
                    if fp == target or fp.startswith(target + "/"):
                        a.set_is_temporarily_hidden_in_editor(True)
                        hidden += 1
                except Exception:
                    continue
        log_info(f"folder_hide: hid {hidden} actor(s) in '{folder_name}'")
        return {"status": "ok", "hidden": hidden, "folder": folder_name}
    except Exception as e:
        log_error(f"folder_hide failed: {e}")
        return {"status": "error", "error": str(e)}


@register_tool(
    name="folder_show",
    category="Visibility",
    description="Restore visibility for all actors in a named World Outliner folder.",
    tags=["visibility", "show", "folder", "outliner", "restore"],
)
def run_folder_show(folder_name: str = "", **kwargs) -> dict:
    """
    Un-hide all actors whose World Outliner folder path starts with folder_name.

    Args:
        folder_name: Folder path, e.g. 'Zones', 'Props/Trees', 'Devices'
    """
    if not folder_name:
        return {"status": "error", "error": "folder_name is required."}
    try:
        sub = _sub()
        target = folder_name.strip("/").lower()
        shown = 0
        with unreal.ScopedEditorTransaction(f"Show Folder: {folder_name}"):
            for a in sub.get_all_level_actors():
                try:
                    fp = str(a.get_folder_path()).strip("/").lower()
                    if fp == target or fp.startswith(target + "/"):
                        a.set_is_temporarily_hidden_in_editor(False)
                        shown += 1
                except Exception:
                    continue
        log_info(f"folder_show: showed {shown} actor(s) in '{folder_name}'")
        return {"status": "ok", "shown": shown, "folder": folder_name}
    except Exception as e:
        log_error(f"folder_show failed: {e}")
        return {"status": "error", "error": str(e)}


# ── Actor locking ──────────────────────────────────────────────────────────────

_LOCK_PROPERTIES = ("lock_location", "bLockLocation", "bLocked")


def _set_selected_lock_state(desired: bool) -> dict:
    count_key = "locked" if desired else "unlocked"
    outcomes = []
    try:
        actors = _sub().get_selected_level_actors()
        if not actors:
            return {"status": "error", "error": "No actors selected.", count_key: 0,
                    "attempted": 0, "changed": 0, "failed": 0}
        with unreal.ScopedEditorTransaction("Lock Actors" if desired else "Unlock Actors"):
            for index, actor in enumerate(actors):
                try:
                    label = actor.get_actor_label()
                except Exception:
                    label = f"Selected actor {index + 1}"
                outcome = {"label": label, "status": "error", "changed": False,
                           "property": None, "before": None, "after": None,
                           "may_have_changed": False}
                probes = []
                for prop in _LOCK_PROPERTIES:
                    try:
                        before = actor.get_editor_property(prop)
                        if not isinstance(before, bool):
                            raise ValueError("Lock property did not return a boolean")
                    except Exception as exc:
                        probes.append({"property": prop, "message": str(exc)})
                        continue
                    outcome.update(property=prop, before=before)
                    break
                else:
                    outcome.update(reason="actor_lock_unavailable", probes=probes,
                                   message="No supported boolean movement-lock property is readable in this build.")
                    outcomes.append(outcome)
                    continue
                if before is desired:
                    outcome.update(status="ok", after=before, already_in_state=True)
                    outcomes.append(outcome)
                    continue
                outcome["may_have_changed"] = True
                try:
                    actor.set_editor_property(prop, desired)
                except Exception as exc:
                    outcome.update(reason="actor_lock_set_failed", message=str(exc))
                    outcomes.append(outcome)
                    continue
                try:
                    after = actor.get_editor_property(prop)
                    outcome["after"] = after if isinstance(after, bool) else None
                    if after is not desired:
                        raise ValueError("Movement-lock readback did not match the requested state")
                except Exception as exc:
                    outcome.update(reason="actor_lock_readback_failed", message=str(exc))
                    outcomes.append(outcome)
                    continue
                outcome.update(status="ok", changed=True, may_have_changed=False)
                outcomes.append(outcome)
    except Exception as exc:
        return {"status": "error", "reason": "actor_lock_failed", "error": str(exc),
                count_key: sum(item["status"] == "ok" for item in outcomes),
                "changed": sum(item["changed"] for item in outcomes), "actors": outcomes,
                "possible_partial_changes": bool(outcomes)}
    errors = [item for item in outcomes if item["status"] == "error"]
    unavailable = sum(item.get("reason") == "actor_lock_unavailable" for item in errors)
    result = {"status": "error" if errors else "ok", count_key: len(outcomes) - len(errors),
              "attempted": len(outcomes), "changed": sum(item["changed"] for item in outcomes),
              "failed": len(errors), "unavailable": unavailable,
              "labels": [item["label"] for item in outcomes], "actors": outcomes,
              "errors": errors,
              "possible_partial_changes": bool(errors) and any(
                  item["changed"] or item["may_have_changed"] for item in outcomes)}
    if errors:
        result["reason"] = ("actor_lock_unavailable" if unavailable == len(outcomes)
                            else "actor_lock_failed")
    log_info(f"actor_{'lock' if desired else 'unlock'}: verified={result[count_key]}, failed={len(errors)}")
    return result


@register_tool(
    name="actor_lock",
    category="Visibility",
    description="Set the exposed movement-lock property on selected actors and verify readback; unsupported actors return errors.",
    tags=["lock", "freeze", "protect", "actor", "placement"],
)
def run_actor_lock(**kwargs) -> dict:
    """Verify the requested lock state; property readback does not prove viewport behavior."""
    return _set_selected_lock_state(True)


@register_tool(
    name="actor_unlock",
    category="Visibility",
    description="Clear the exposed movement-lock property on selected actors and verify readback; unsupported actors return errors.",
    tags=["lock", "unlock", "actor", "selection", "transform"],
)
def run_actor_unlock(**kwargs) -> dict:
    """Verify the requested unlocked state without guessing property availability."""
    return _set_selected_lock_state(False)
