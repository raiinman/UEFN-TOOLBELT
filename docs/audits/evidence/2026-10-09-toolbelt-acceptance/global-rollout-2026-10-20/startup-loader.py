"""Start Toolbelt after an authorized UEFN project is mounted."""
import json
import os
import re
import sys
import time
from pathlib import Path

import unreal

_handle = None
_finished = False
_started_at = 0.0


def _normal(path):
    return os.path.normcase(os.path.realpath(path)).rstrip("/\\")


def _installed_project(python_dir):
    """Read one installed native project, without searching beyond its root."""
    try:
        python_dir = Path(python_dir).resolve()
        if python_dir.name.lower() != "python" or python_dir.parent.name.lower() != "content":
            return None
        package = python_dir / "UEFN_Toolbelt" / "__init__.py"
        if not package.is_file() or not package.resolve().is_relative_to(python_dir):
            return None
        root = python_dir.parent.parent
        descriptors = list(root.glob("*.uefnproject"))
        if len(descriptors) != 1 or not descriptors[0].resolve().is_relative_to(root):
            return None
        descriptor = json.loads(descriptors[0].read_text(encoding="utf-8-sig"))
        roots = [p for p in descriptor.get("plugins", [])
                 if isinstance(p, dict) and p.get("bIsRoot") is True]
        if len(roots) != 1:
            return None
        mount = roots[0].get("name")
        if (not isinstance(mount, str) or not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_-]*", mount)
                or mount.lower() in {"temp", "game", "engine", "script"}):
            return None
        return {"mount": mount, "project_file": str(descriptors[0]), "python_dir": str(python_dir)}
    except (OSError, ValueError, TypeError, AttributeError):
        return None


def _project_candidates(projects):
    # sys.path is supplied by the active editor/project hook. The optional old
    # registry contributes bounded fallbacks, never an unrestricted disk scan.
    candidates = {}
    paths = [p for p in sys.path if isinstance(p, str) and p]
    paths.extend(p.get("python_dir") for p in projects if isinstance(p, dict))
    for path in paths:
        if not isinstance(path, str) or not path:
            continue
        project = _installed_project(path)
        if project is not None:
            candidates[_normal(project["python_dir"])] = project
    return list(candidates.values())


def _select_project(projects):
    projects = _project_candidates(projects)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    if world is None:
        return None
    mount = world.get_path_name().lstrip("/").split("/", 1)[0]
    matches = [p for p in projects if p["mount"] == mount]
    if len(matches) == 1:
        return matches[0]
    # An untitled level can still belong to a uniquely mounted project.
    if mount not in ("Temp", "Game"):
        return None
    paths = {_normal(p) for p in sys.path if p}
    matches = [p for p in projects if _normal(p["python_dir"]) in paths]
    return matches[0] if len(matches) == 1 else None


def _stop():
    global _handle, _finished
    _finished = True
    if _handle is not None:
        unreal.unregister_slate_post_tick_callback(_handle)
        _handle = None


def schedule():
    global _handle, _started_at
    if _handle is not None or _finished:
        return
    try:
        projects = json.loads(Path(__file__).with_name("projects.json").read_text(encoding="utf-8"))
        if not isinstance(projects, list):
            projects = []
    except (OSError, ValueError):
        projects = []
    _started_at = time.monotonic()

    def on_tick(_dt):
        elapsed = time.monotonic() - _started_at
        if elapsed < 5:
            return
        if elapsed > 180:
            _stop()
            unreal.log_warning("[CODEX TOOLBELT] No installed native project became ready; listener not started.")
            return
        try:
            project = _select_project(projects)
            if project is None:
                return
            _stop()  # Startup is attempted once; a failure must not replay it each tick.
            python_dir = project["python_dir"]
            if not Path(python_dir, "UEFN_Toolbelt", "__init__.py").is_file():
                raise RuntimeError("The selected project's Toolbelt package is missing.")
            gui_libs = str(Path(__file__).with_name("python-libs"))
            if gui_libs not in sys.path:
                sys.path.insert(0, gui_libs)
            sys.path.insert(0, python_dir)
            import UEFN_Toolbelt as tb
            if _normal(Path(tb.__file__).parent.parent) != _normal(python_dir):
                raise RuntimeError("Toolbelt is already loaded from a different project; restart UEFN.")
            tb.register()
            result = tb.run("mcp_start")
            if not isinstance(result, dict) or result.get("status") != "ok":
                raise RuntimeError("Listener startup did not report success; see the Toolbelt log.")
            unreal.log(f"[CODEX TOOLBELT] Automatic listener startup complete: {project['mount']}")
            dashboard_result = tb.run("launch_qt")
            if not isinstance(dashboard_result, dict) or dashboard_result.get("status") != "ok":
                unreal.log_warning("[CODEX TOOLBELT] Listener is ready, but the dashboard failed to open; see the Toolbelt log.")
        except Exception as exc:
            _stop()
            unreal.log_error(f"[CODEX TOOLBELT] Automatic startup failed: {type(exc).__name__}: {exc}")

    _handle = unreal.register_slate_post_tick_callback(on_tick)
    unreal.log("[CODEX TOOLBELT] Waiting for an installed native UEFN project to finish loading.")
