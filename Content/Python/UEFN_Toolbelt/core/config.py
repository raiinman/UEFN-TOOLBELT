"""
UEFN TOOLBELT — Persistent Config
==================================
A thin JSON-backed key/value store that survives install.py updates.

Lives at: <native project>/Saved/UEFN_Toolbelt/config.json
            ↑ outside the package directory, never overwritten on update

Usage (from any tool):
    from ..core import get_config
    cfg = get_config()

    mesh = cfg.get("arena.fallback_mesh")           # returns default if not set
    cfg.set("scatter.default_folder", "MyScatter")  # persists immediately
    cfg.reset("scatter.default_folder")             # back to default

Keys use dot-notation namespaced by tool family:
    arena.*      scatter.*     text.*
    screenshot.* snapshot.*    lod.*

DEFAULTS act as the fallback for any key not present in config.json.
To add a new configurable value: add it to DEFAULTS below.
Tools read via cfg.get("key") — they never need to know if the user
customised the value or if the default is being used.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

# ── Defaults — the canonical fallback for every configurable value ─────────────
# These are the values tools get when the user hasn't customised anything.
# Never read these directly in tool code — always go through cfg.get().

DEFAULTS: dict[str, Any] = {
    # Arena Generator
    "arena.fallback_mesh":      "/Engine/BasicShapes/Cube",

    # Scatter / Foliage
    "scatter.default_folder":   "Scatter",
    "scatter.default_radius":   2000.0,
    "scatter.default_count":    50,

    # Text Painter
    "text.default_folder":      "ToolbeltText",
    "text.default_color":       "#FFFFFF",
    "text.default_size":        100.0,

    # Screenshots
    "screenshot.default_width":  1920,
    "screenshot.default_height": 1080,
    "screenshot.default_name":   "shot",

    # Snapshots
    "snapshot.default_scope":   "all",

    # Verse Device Graph
    "verse.project_path":       "",

    # Image Import (import_image_from_clipboard / import_image_from_url)
    # Empty string = auto-detect project mount at call time → /{mount}/UEFN_Toolbelt/Textures
    "import.default_dir":       "",

    # UI Theme
    "ui.theme":                 "toolbelt_dark",
}


class Config:
    """
    Lazy-loading JSON config store.
    Loads from disk on first access, auto-saves on every set().
    Thread-safety is not required — UEFN Python is single-threaded.
    """

    def __init__(self, path: str, project_root: str | None = None) -> None:
        self._project_root = Path(project_root).resolve() if project_root else None
        self._path = path
        self._load_error: str | None = None
        self._data: dict[str, Any] | None = None  # None = not loaded yet

    # ── Private ────────────────────────────────────────────────────────────────

    def _load(self) -> None:
        try:
            with open(self._path, encoding="utf-8") as stream:
                loaded = json.load(stream)
            if not isinstance(loaded, dict):
                raise ValueError("Configuration must be a JSON object")
            self._data = loaded
        except FileNotFoundError:
            self._data = {}
        except (OSError, ValueError, TypeError):
            self._data = {}
            self._load_error = "Existing configuration is unreadable or invalid; writes refused"

    def _require_writable(self) -> None:
        if self._load_error:
            raise ValueError(self._load_error)

    def _ensure_loaded(self) -> dict[str, Any]:
        """Load on first use and return the (now non-None) data dict."""
        if self._data is None:
            self._load()
        assert self._data is not None  # _load() always assigns a dict
        return self._data

    def _save(self) -> None:
        self._require_writable()
        directory = os.path.dirname(os.path.abspath(self._path))
        os.makedirs(directory, exist_ok=True)
        temporary = ""
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=directory,
                                             prefix=".config.", suffix=".tmp", delete=False) as stream:
                temporary = stream.name
                json.dump(self._data, stream, indent=2, sort_keys=True)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self._path)
        finally:
            if temporary and os.path.exists(temporary):
                os.remove(temporary)

    def _safe_verse_path(self, value: Any) -> bool:
        if not value:
            return True
        if self._project_root is None:
            return True  # Explicit standalone Config retains its existing contract.
        if not isinstance(value, str):
            return False
        path = Path(value)
        return path.is_absolute() and path.resolve().is_relative_to(self._project_root)

    # ── Public API ─────────────────────────────────────────────────────────────

    def get(self, key: str, fallback: Any = None) -> Any:
        """
        Return the value for key.
        Priority: user config → DEFAULTS → fallback argument.
        """
        data = self._ensure_loaded()
        if key in data:
            if key == "verse.project_path" and not self._safe_verse_path(data[key]):
                return DEFAULTS[key]  # Stale cross-project override cannot direct writes.
            return data[key]
        if key in DEFAULTS:
            return DEFAULTS[key]
        return fallback

    def set(self, key: str, value: Any) -> None:
        """Set a value and immediately persist it to disk."""
        if key == "verse.project_path" and not self._safe_verse_path(value):
            raise ValueError("Verse project path must stay inside the current native project")
        data = self._ensure_loaded()
        self._require_writable()
        previous = dict(data)
        data[key] = value
        try:
            self._save()
        except Exception:
            self._data = previous
            raise

    def reset(self, key: str) -> bool:
        """
        Remove a user-set value, restoring the default.
        Returns True if the key existed, False if it wasn't set.
        """
        data = self._ensure_loaded()
        self._require_writable()
        if key in data:
            previous = dict(data)
            del data[key]
            try:
                self._save()
            except Exception:
                self._data = previous
                raise
            return True
        return False

    def all(self) -> dict[str, Any]:
        """
        Return a snapshot of all values — merging defaults with user overrides.
        User-set values take priority. Keys with defaults that haven't been
        customised show the default value with an 'is_default' marker in
        config_list output (not in this dict — this is the clean merged view).
        """
        data = self._ensure_loaded()
        merged = dict(DEFAULTS)
        merged.update(data)
        if not self._safe_verse_path(merged["verse.project_path"]):
            merged["verse.project_path"] = DEFAULTS["verse.project_path"]
        return merged

    def is_default(self, key: str) -> bool:
        """True if the user has not customised this key."""
        return key not in self._ensure_loaded()


class _UnresolvedConfig(Config):
    """Defaults remain importable; unconfirmed projects cannot persist settings."""
    def __init__(self) -> None:
        super().__init__("")
        self._data = {}

    def set(self, key: str, value: Any) -> None:
        raise ValueError("Configuration writes require a confirmed native project")

    def reset(self, key: str) -> bool:
        raise ValueError("Configuration writes require a confirmed native project")


# ── Singleton ──────────────────────────────────────────────────────────────────

_config_instance: Config | None = None


def _native_project_identity() -> tuple[Path, str]:
    from . import detect_project_mount, native_project_dir
    return Path(native_project_dir()), detect_project_mount()


def _migrate_legacy_config(destination: Path, legacy: Path, project: Path, mount: str) -> None:
    """Copy settings once; keep the legacy file and reject other-project paths."""
    if destination.exists() or not legacy.is_file():
        return
    with legacy.open(encoding="utf-8") as stream:
        data = json.load(stream)
    if not isinstance(data, dict):
        return
    scoped = Config(str(destination), str(project))
    safe = dict(data)
    if not scoped._safe_verse_path(safe.get("verse.project_path", "")):
        safe.pop("verse.project_path", None)
    import_dir = safe.get("import.default_dir", "")
    if import_dir and (not isinstance(import_dir, str)
                       or not (import_dir == f"/{mount}" or import_dir.startswith(f"/{mount}/"))):
        safe.pop("import.default_dir", None)
    scoped._data = safe
    scoped._save()


def get_config() -> Config:
    """Return project-local config; migrate shared legacy settings without path leaks."""
    global _config_instance
    import unreal
    try:
        project, mount = _native_project_identity()
    except (OSError, ValueError, TypeError):
        if not isinstance(_config_instance, _UnresolvedConfig):
            _config_instance = _UnresolvedConfig()
        return _config_instance
    path = project / "Saved" / "UEFN_Toolbelt" / "config.json"
    if not path.resolve().is_relative_to(project):
        raise ValueError("Native project configuration resolves outside its project")
    if _config_instance is None or Path(_config_instance._path).resolve() != path.resolve():
        legacy = Path(unreal.Paths.project_saved_dir()) / "UEFN_Toolbelt" / "config.json"
        try:
            _migrate_legacy_config(path, legacy, project, mount)
        except (OSError, ValueError, TypeError):
            pass  # Invalid legacy state leaves current project defaults intact.
        _config_instance = Config(str(path), str(project))
    return _config_instance
