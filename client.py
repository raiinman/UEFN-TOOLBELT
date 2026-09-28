"""
UEFN Toolbelt — External Python Client
=========================================
Stdlib-only HTTP client for the UEFN Toolbelt MCP bridge.
No MCP, no SDK, no dependencies — works from any Python 3.8+ script,
or trusted same-user local automation.

Usage:
    from client import ToolbeltClient, ToolbeltError

    ue = ToolbeltClient()                  # loads the current local session handoff
    ue.ping()
    ue.run_tool("material_apply_preset", preset="chrome")
    actors = ue.get_all_actors()

Requirements:
    - UEFN is running with the Toolbelt loaded
    - MCP listener is started: tb.run("mcp_start")

Author: Ocean Bennett · License: AGPL-3.0
"""

from __future__ import annotations

import json
import os
import socket
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


def _redact_secret(value: Any, secret: str) -> Any:
    """Defensively remove the current handoff credential from client output."""
    if isinstance(value, str):
        return value.replace(secret, "[REDACTED]")
    if isinstance(value, dict):
        return {
            _redact_secret(key, secret): _redact_secret(item, secret)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_redact_secret(item, secret) for item in value]
    if isinstance(value, tuple):
        return tuple(_redact_secret(item, secret) for item in value)
    return value


# ─── Bridge outcome contract ─────────────────────────────────────────────────
#
# WO-004 Session B. Every (status, error) pair the bridge writes before it
# queues a command (mcp_bridge.py, its _reject and _error call sites). Only one
# of these exact two-key bodies, received directly from the validated loopback
# endpoint, shows that the request was rejected before queueing. Anything else
# is an unknown outcome: a status code alone does not identify its producer.
_BRIDGE_REJECTIONS = frozenset({
    (400, "Invalid Host header"),
    (400, "Transfer-Encoding is not supported"),
    (400, "Malformed JSON request"),
    (400, "JSON body must be an object"),
    (400, "Missing 'command'"),
    (400, "'params' must be an object"),
    (401, "Authentication required"),
    (403, "Browser-originated requests are not accepted"),
    (403, "Browser preflight is not accepted"),
    (404, "Unknown path"),
    (405, "Only authenticated POST requests are accepted"),
    (411, "A valid Content-Length is required"),
    (413, "Request body is too large"),
    (415, "Content-Type must be application/json"),
})
# The bridge's own 504 body, followed by the command that was sent.
_DEADLINE_ERROR_PREFIX = "Command timed out: "
# The body stop_listener returns for a command drained before dispatch.
_STOP_DRAIN_ERROR = "MCP listener stopped before command dispatch"


class _RefuseRedirects(urllib.request.HTTPRedirectHandler):
    """Never follow a redirect: it would carry the bearer to an unvalidated URL."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _direct_opener() -> urllib.request.OpenerDirector:
    """A per-request opener for the bridge: no HTTP proxy and no redirect.

    ProxyHandler({}) ignores environment and system proxy settings for these
    requests only. No global opener is installed and no environment variable
    is changed.
    """
    return urllib.request.build_opener(
        urllib.request.ProxyHandler({}), _RefuseRedirects()
    )


def _is_timeout(error: object) -> bool:
    """True for a timeout on every supported Python.

    socket.timeout is an alias of TimeoutError from Python 3.10, and a
    separate OSError subclass before it, so both are named here.
    """
    return isinstance(error, (TimeoutError, socket.timeout))


def _bridge_error_body(raw: bytes | None) -> dict | None:
    """The bridge's exact two-key error envelope, or None for anything else."""
    if raw is None:
        return None
    try:
        body = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return None
    if (
        isinstance(body, dict)
        and set(body) == {"success", "error"}
        and body["success"] is False
        and isinstance(body["error"], str)
    ):
        return body
    return None


def _unknown_outcome(safe_command: str, detail: str) -> str:
    """Wording for every outcome no reply confirmed. It names no cause."""
    return (
        f"No reply confirmed the outcome of command '{safe_command}' ({detail}).\n"
        "  The command may not have run, may still be queued or running, or may "
        "have completed.\n"
        "  Do not send a command that changes editor or project state again "
        "until that state has been checked. A check sent while the editor is "
        "not processing the bridge queue can also go unanswered.\n"
        "  Toolbelt cannot determine why no reply arrived; look at the UEFN editor."
    )


def _reported_failure(safe_command: str, error: object) -> str:
    """Wording for a reported failure. It claims neither execution nor its absence."""
    return (
        f"UEFN reported a failure for command '{safe_command}': {error}\n"
        "  It may have failed before running or partway through, leaving some "
        "changes applied. Check the editor's state before continuing."
    )


# ─── Exceptions ───────────────────────────────────────────────────────────────

class ToolbeltError(Exception):
    """A toolbelt command failed on the UEFN side."""
    def __init__(self, message: str, traceback_text: str = ""):
        super().__init__(message)
        self.traceback_text = traceback_text

    def __str__(self) -> str:
        if self.traceback_text:
            return f"{super().__str__()}\n{self.traceback_text}"
        return super().__str__()


class NotConnected(ToolbeltError):
    """The connection was refused, so no request reached a listener."""


class OutcomeUnknown(ToolbeltError):
    """No reply confirmed whether the command ran.

    The command may not have run, may still be queued or running, or may have
    completed. Check editor state before sending a state-changing command again.
    """


class CommandTimeout(OutcomeUnknown):
    """No reply arrived before a deadline. The outcome is unknown."""


class AuthenticationError(ToolbeltError):
    """The local session credential is missing, stale, or rejected."""


_INVALID_HANDOFF = (
    "No request was sent: the UEFN MCP session handoff is invalid.\n"
    "  Restart the listener in UEFN: import UEFN_Toolbelt as tb; tb.run('mcp_restart')"
)


def _http_status_error(code: int, raw: bytes | None, command: str,
                       safe_command: str, token: str) -> ToolbeltError:
    """Classify an HTTP error status. Only the bridge's exact bodies count."""
    body = _bridge_error_body(raw)
    if body is not None:
        error = body["error"]
        if (code, error) in _BRIDGE_REJECTIONS:
            if code == 401:
                return AuthenticationError(
                    "UEFN MCP authentication failed: the listener rejected the "
                    "request before queueing it (HTTP 401).\n"
                    "  Restart the listener to refresh the session."
                )
            return ToolbeltError(
                "The UEFN Toolbelt listener rejected the request before queueing "
                f"it (HTTP {code}: {_redact_secret(error, token)})."
            )
        if code == 504 and error == _DEADLINE_ERROR_PREFIX + command:
            return CommandTimeout(_unknown_outcome(
                safe_command, "the bridge's reply deadline elapsed (HTTP 504)"
            ))
    return OutcomeUnknown(_unknown_outcome(
        safe_command, f"an unexpected HTTP {code} response"
    ))


# ─── Client ───────────────────────────────────────────────────────────────────

class ToolbeltClient:
    """
    HTTP client for the UEFN Toolbelt MCP bridge.

    Start the listener in UEFN first:
        import UEFN_Toolbelt as tb; tb.run("mcp_start")

    Then connect from any external script:
        ue = ToolbeltClient()
        ue.run_tool("arena_generate", size="large", apply_team_colors=True)
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int | None = None,
        timeout: float = 30.0,
        token_file: str | os.PathLike[str] | None = None,
    ):
        if host != "127.0.0.1":
            raise ValueError("The Toolbelt client only accepts the loopback host")
        self._port_override = port
        self.timeout = timeout
        self._token_file = Path(token_file) if token_file else self._default_token_file()

    @staticmethod
    def _default_token_file() -> Path:
        override = os.environ.get("UEFN_MCP_TOKEN_FILE", "").strip()
        if override:
            return Path(override).expanduser()
        local_app_data = os.environ.get("LOCALAPPDATA", "").strip()
        if not local_app_data:
            raise AuthenticationError(
                "No request can be sent: LOCALAPPDATA is unset, so the UEFN MCP "
                "session handoff cannot be located"
            )
        return (
            Path(local_app_data)
            / "UnrealEditorFortnite"
            / "Saved"
            / "UEFN_Toolbelt"
            / "mcp_session.json"
        )

    def _session(self) -> tuple[str, str]:
        try:
            payload = json.loads(self._token_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise AuthenticationError(
                "No request was sent: the UEFN MCP session handoff is missing or "
                "unreadable.\n"
                "  Start or restart the listener in UEFN: "
                "import UEFN_Toolbelt as tb; tb.run('mcp_start')"
            ) from exc
        if not isinstance(payload, dict):
            raise AuthenticationError(_INVALID_HANDOFF)
        host = payload.get("host")
        port = self._port_override if self._port_override is not None else payload.get("port")
        token = payload.get("token")
        if (
            payload.get("version") != 1
            or host != "127.0.0.1"
            or not isinstance(port, int)
            or not (1 <= port <= 65535)
            or not isinstance(token, str)
            or len(token) < 32
        ):
            raise AuthenticationError(_INVALID_HANDOFF)
        return f"http://127.0.0.1:{port}", token

    # ── Core transport ────────────────────────────────────────────────────────

    def _send(self, command: str, params: dict | None = None,
              timeout: float | None = None) -> Any:
        """
        Send one command to UEFN and return the result.

        Exactly one connection attempt is made, directly to the validated
        loopback endpoint, and none when the session handoff is missing or
        invalid. Nothing is retried. Raises:

          AuthenticationError - no request was sent (missing or invalid
                                handoff), or the bridge's own 401 rejection
          NotConnected        - the connection was refused; nothing delivered
          CommandTimeout      - no reply before a deadline; outcome unknown
          OutcomeUnknown      - no reply confirmed the outcome
          ToolbeltError       - the bridge rejected the request before queueing
                                it, stopped before dispatching it, or reported
                                a failure
        """
        url, token = self._session()
        payload = json.dumps({"command": command, "params": params or {}}).encode()
        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        t = timeout if timeout is not None else self.timeout
        safe_command = _redact_secret(command, token)
        try:
            with _direct_opener().open(req, timeout=t) as resp:
                status = resp.status
                raw = resp.read()
        except urllib.error.HTTPError as exc:
            try:
                error_raw: bytes | None = exc.read()
            except Exception as read_error:
                if _is_timeout(read_error):
                    raise CommandTimeout(
                        _unknown_outcome(safe_command, f"no reply within {t}s")
                    ) from None
                error_raw = None
            raise _http_status_error(
                exc.code, error_raw, command, safe_command, token
            ) from None
        except Exception as exc:
            reason = exc.reason if isinstance(exc, urllib.error.URLError) else None
            # A timeout is a timeout whether or not urllib wrapped it, so it is
            # decided before a refusal or any other transport error.
            if _is_timeout(exc) or _is_timeout(reason):
                raise CommandTimeout(
                    _unknown_outcome(safe_command, f"no reply within {t}s")
                ) from None
            if isinstance(reason, ConnectionRefusedError):
                raise NotConnected(
                    "The connection was refused, so no request reached a UEFN "
                    "Toolbelt listener.\n"
                    "  Start it in UEFN: import UEFN_Toolbelt as tb; tb.run('mcp_start')"
                ) from None
            raise OutcomeUnknown(_unknown_outcome(
                safe_command,
                "the connection failed or closed before a complete reply",
            )) from None

        if status != 200:
            # urllib raises only outside 200-299, so a 2xx other than 200
            # arrives here as an ordinary response. It is not the bridge's.
            raise OutcomeUnknown(_unknown_outcome(
                safe_command, f"an unexpected HTTP {status} response"
            ))
        try:
            body = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, ValueError):
            body = None
        if not isinstance(body, dict) or not isinstance(body.get("success"), bool):
            raise OutcomeUnknown(_unknown_outcome(
                safe_command, "a reply that is not the bridge's result format"
            ))
        if body == {"success": False, "error": _STOP_DRAIN_ERROR}:
            raise ToolbeltError(
                "The UEFN Toolbelt listener stopped before it dispatched "
                f"command '{safe_command}'."
            )

        body = _redact_secret(body, token)

        if not body["success"]:
            raise ToolbeltError(
                _reported_failure(safe_command, body.get("error", "Unknown error")),
                body.get("traceback", ""),
            )
        return body.get("result")

    def batch(self, commands: list[dict], timeout: float = 60.0) -> list[dict]:
        """
        Execute multiple commands in a single UEFN editor tick.
        Each entry: {"command": "name", "params": {...}}

        Faster than sending commands one-by-one for multi-step sequences.

        Example:
            ue.batch([
                {"command": "run_tool",
                 "params": {"tool_name": "snapshot_save"}},
                {"command": "run_tool",
                 "params": {"tool_name": "scatter_hism",
                            "kwargs": {"count": 200, "radius": 3000}}},
                {"command": "save_current_level", "params": {}},
            ])
        """
        result = self._send("batch_exec", {"commands": commands}, timeout=timeout)
        return result.get("results", [])

    # ── System ────────────────────────────────────────────────────────────────

    def ping(self) -> dict:
        """Check if the listener is alive. Returns port, commands, python version."""
        return self._send("ping")

    def get_log(self, last_n: int = 50) -> list[str]:
        """Get last N lines from the MCP listener log ring."""
        return self._send("get_log", {"last_n": last_n}).get("lines", [])

    def history(self, tail: int = 30) -> list[dict]:
        """Get recent command history with per-command timing."""
        return self._send("history", {"tail": tail}).get("entries", [])

    def undo(self) -> dict:
        """Undo the last editor action."""
        return self._send("undo")

    def redo(self) -> dict:
        """Redo the last undone action."""
        return self._send("redo")

    # ── Toolbelt bridge ───────────────────────────────────────────────────────

    def run_tool(self, tool_name: str, timeout: float = 120.0, **kwargs) -> dict:
        """
        Run any registered UEFN Toolbelt tool by name.
        This is the main interface — 362 tools available.

        Examples:
            ue.run_tool("material_apply_preset", preset="chrome")
            ue.run_tool("arena_generate", size="large", apply_team_colors=True)
            ue.run_tool("scatter_hism", count=300, radius=5000.0)
            ue.run_tool("snapshot_save", name="before_cleanup")
            ue.run_tool("tag_add", key="biome", value="desert")
            ue.run_tool("screenshot_focus_selection", width=1920, height=1080)
            ue.run_tool("ref_full_report", scan_path="")
        """
        return self._send(
            "run_tool",
            {"tool_name": tool_name, "kwargs": kwargs},
            timeout=timeout,
        )

    def list_tools(self, category: str = "") -> list[dict]:
        """List all registered toolbelt tools, optionally filtered by category."""
        return self._send("list_tools", {"category": category}).get("tools", [])

    def execute_python(self, code: str, timeout: float = 60.0) -> dict:
        """Reject arbitrary remote Python; use the local UEFN console instead."""
        raise ToolbeltError(
            "execute_python is unavailable on the Toolbelt MCP bridge; "
            "use the local UEFN Python console"
        )

    # ── Actors ────────────────────────────────────────────────────────────────

    def get_all_actors(self, class_filter: str = "") -> list[dict]:
        """List all actors in the current level."""
        return self._send("get_all_actors",
                          {"class_filter": class_filter}).get("actors", [])

    def get_selected_actors(self) -> list[dict]:
        """Get actors currently selected in the UEFN viewport."""
        return self._send("get_selected_actors").get("actors", [])

    def spawn_actor(
        self,
        asset_path: str = "",
        actor_class: str = "",
        location: list[float] | None = None,
        rotation: list[float] | None = None,
        label: str = "",
    ) -> dict:
        """Spawn an actor. Provide asset_path OR actor_class."""
        params: dict[str, Any] = {}
        if asset_path:  params["asset_path"]  = asset_path
        if actor_class: params["actor_class"] = actor_class
        if location:    params["location"]    = location
        if rotation:    params["rotation"]    = rotation
        if label:       params["label"]       = label
        return self._send("spawn_actor", params).get("actor", {})

    def set_actor_property(self, actor_path: str, property_name: str, value) -> dict:
        """Set a single editor property on an actor by path or label."""
        return self._send("set_actor_property", {
            "actor_path": actor_path, "property_name": property_name, "value": value,
        })

    def delete_actors(self, actor_paths: list[str]) -> dict:
        """Delete actors by path name or label."""
        return self._send("delete_actors", {"actor_paths": actor_paths})

    def set_actor_transform(
        self,
        actor_path: str,
        location: list[float] | None = None,
        rotation: list[float] | None = None,
        scale:    list[float] | None = None,
    ) -> dict:
        """Set location, rotation and/or scale on an actor."""
        params: dict[str, Any] = {"actor_path": actor_path}
        if location: params["location"] = location
        if rotation: params["rotation"] = rotation
        if scale:    params["scale"]    = scale
        return self._send("set_actor_transform", params).get("actor", {})

    # ── Assets ────────────────────────────────────────────────────────────────

    def list_assets(self, directory: str = "/Game/",
                    recursive: bool = True, class_filter: str = "") -> list[str]:
        """List asset paths in a Content Browser directory."""
        return self._send("list_assets", {
            "directory": directory,
            "recursive": recursive,
            "class_filter": class_filter,
        }).get("assets", [])

    def get_asset_info(self, asset_path: str) -> dict:
        """Get metadata for an asset."""
        return self._send("get_asset_info", {"asset_path": asset_path}).get("asset", {})

    def import_asset(
        self,
        source_file: str,
        destination_path: str,
        replace_existing: bool = True,
        save: bool = True,
    ) -> dict:
        """Import an external file into the Content Browser."""
        return self._send("import_asset", {
            "source_file":      source_file,
            "destination_path": destination_path,
            "replace_existing": replace_existing,
            "save":             save,
        })

    def save_asset(self, asset_path: str) -> bool:
        """Save a modified asset."""
        return self._send("save_asset", {"asset_path": asset_path}).get("success", False)

    def rename_asset(self, old_path: str, new_path: str) -> bool:
        """Rename or move an asset."""
        return self._send("rename_asset", {
            "old_path": old_path, "new_path": new_path
        }).get("success", False)

    def duplicate_asset(self, source_path: str, dest_path: str) -> bool:
        """Duplicate an asset."""
        return self._send("duplicate_asset", {
            "source_path": source_path, "dest_path": dest_path
        }).get("success", False)

    def delete_asset(self, asset_path: str) -> bool:
        """Delete an asset."""
        return self._send("delete_asset", {"asset_path": asset_path}).get("success", False)

    def create_material_instance(
        self,
        parent_path: str,
        instance_name: str,
        destination: str = "/Game/Materials",
        scalar_params: dict[str, float] | None = None,
        vector_params: dict[str, list[float]] | None = None,
        texture_params: dict[str, str] | None = None,
    ) -> str:
        """
        Create a new MaterialInstanceConstant from a parent material.
        Returns the path of the created MI.

        Example:
            path = ue.create_material_instance(
                parent_path="/Game/Materials/M_Master",
                instance_name="MI_Red",
                destination="/Game/Materials/Instances",
                scalar_params={"Roughness": 0.2, "Metallic": 0.8},
                vector_params={"BaseColor": [1.0, 0.1, 0.1, 1.0]},
            )
        """
        return self._send("create_material_instance", {
            "parent_path":    parent_path,
            "instance_name":  instance_name,
            "destination":    destination,
            "scalar_params":  scalar_params or {},
            "vector_params":  vector_params or {},
            "texture_params": texture_params or {},
        }).get("path", "")

    # ── Level & viewport ──────────────────────────────────────────────────────

    def save_level(self) -> bool:
        """Save the current level."""
        return self._send("save_current_level").get("success", False)

    def get_level_info(self) -> dict:
        """Get world name and actor count."""
        return self._send("get_level_info")

    def get_camera(self) -> dict:
        """Get viewport camera location and rotation."""
        return self._send("get_viewport_camera")

    def set_camera(
        self,
        location: list[float] | None = None,
        rotation: list[float] | None = None,
    ) -> dict:
        """Move the viewport camera."""
        params: dict[str, Any] = {}
        if location: params["location"] = location
        if rotation: params["rotation"] = rotation
        return self._send("set_viewport_camera", params)


# ─── Quick connect helper ─────────────────────────────────────────────────────

def connect(port: int | None = None, timeout: float = 30.0) -> ToolbeltClient:
    """Create a client and verify the connection with a single ping."""
    client = ToolbeltClient(port=port, timeout=timeout)
    client.ping()   # raises NotConnected if the connection is refused
    return client
