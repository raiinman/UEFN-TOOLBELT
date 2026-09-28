"""Adversarial contract tests for the custom same-user MCP control plane."""

from __future__ import annotations

import ast
import builtins
import http.client
import http.server
import importlib.util
import io
import json
import os
import queue
import socket
import sys
import threading
import time
import types
import urllib.error
import urllib.request
from pathlib import Path

import pytest


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _response(
    port: int,
    *,
    token: str | None,
    body: bytes = b'{"command":"ping","params":{}}',
    path: str = "/",
    content_type: str = "application/json",
    origin: str | None = None,
    host: str | None = None,
    method: str = "POST",
) -> tuple[int, dict, dict[str, str]]:
    headers = {"Content-Type": content_type}
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"
    if origin is not None:
        headers["Origin"] = origin
    request = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        data=body if method == "POST" else None,
        headers=headers,
        method=method,
    )
    if host is not None:
        request.add_unredirected_header("Host", host)
    try:
        with urllib.request.urlopen(request, timeout=2.0) as response:
            payload = json.loads(response.read().decode("utf-8"))
            return response.status, payload, dict(response.headers)
    except urllib.error.HTTPError as exc:
        payload = json.loads(exc.read().decode("utf-8"))
        return exc.code, payload, dict(exc.headers)


def _queued_response(bridge, port: int, token: str, body: bytes | None = None):
    completed: queue.Queue = queue.Queue()

    def request() -> None:
        try:
            completed.put(_response(port, token=token, body=body or b'{"command":"ping"}'))
        except Exception as exc:  # pragma: no cover - assertion reports transport failures
            completed.put(exc)

    thread = threading.Thread(target=request, daemon=True)
    thread.start()
    deadline = time.time() + 2.0
    while bridge._command_queue.empty() and time.time() < deadline:
        time.sleep(0.01)
    assert not bridge._command_queue.empty(), "authenticated request was not queued"
    bridge._tick(0.0)
    thread.join(timeout=2.0)
    assert not thread.is_alive()
    result = completed.get_nowait()
    if isinstance(result, Exception):
        raise result
    return result


@pytest.fixture
def bridge(tmp_path, monkeypatch):
    from UEFN_Toolbelt.tools import mcp_bridge

    mcp_bridge.stop_listener()
    monkeypatch.delenv("UEFN_TOOLBELT_MCP_ALLOW_EXECUTE_PYTHON", raising=False)
    monkeypatch.setenv("UEFN_MCP_TOKEN_FILE", str(tmp_path / "mcp_session.json"))
    monkeypatch.setattr(
        mcp_bridge.unreal,
        "register_slate_post_tick_callback",
        lambda callback: object(),
    )
    monkeypatch.setattr(
        mcp_bridge.unreal,
        "unregister_slate_post_tick_callback",
        lambda handle: None,
    )
    yield mcp_bridge
    mcp_bridge.stop_listener()


def _start(bridge) -> tuple[int, str]:
    port = _free_port()
    bridge.start_listener(port)
    handoff = json.loads(bridge._token_handoff_path().read_text(encoding="utf-8"))
    return port, handoff["token"]


def test_listener_requires_correct_auth_before_dispatch(bridge, monkeypatch):
    port, token = _start(bridge)
    dispatched = []
    original = bridge._execute_command

    def capture(command, params):
        dispatched.append(command)
        return original(command, params)

    monkeypatch.setattr(bridge, "_execute_command", capture)

    missing, _, _ = _response(port, token=None, body=b"not json")
    wrong, _, _ = _response(port, token="wrong" * 10, body=b"not json")
    assert missing == 401
    assert wrong == 401
    assert dispatched == []
    assert bridge._command_queue.empty()

    status, payload, _ = _queued_response(bridge, port, token)
    assert status == 200
    assert payload["success"] is True
    assert dispatched == ["ping"]


def test_repeated_auth_rejections_return_stable_json_without_dispatch(
    bridge, monkeypatch
):
    port, _token = _start(bridge)
    dispatched = []
    monkeypatch.setattr(
        bridge,
        "_execute_command",
        lambda command, params: dispatched.append(command),
    )

    for _ in range(25):
        missing, missing_body, _ = _response(port, token=None)
        wrong, wrong_body, _ = _response(port, token="wrong" * 10)
        assert (missing, missing_body) == (
            401,
            {"success": False, "error": "Authentication required"},
        )
        assert (wrong, wrong_body) == (
            401,
            {"success": False, "error": "Authentication required"},
        )

    assert dispatched == []
    assert bridge._command_queue.empty()


def test_request_validation_is_strict_and_browser_closed(bridge):
    port, token = _start(bridge)

    assert _response(port, token=token, path="/elsewhere")[0] == 404
    assert _response(port, token=token, host="localhost:8765")[0] == 400
    assert _response(port, token=token, origin="https://attacker.invalid")[0] == 403
    assert _response(port, token=token, content_type="text/plain")[0] == 415
    assert _response(port, token=token, body=b"not json")[0] == 400
    assert _response(port, token=None, body=b"not json")[0] == 401
    assert _response(port, token=token, method="GET")[0] == 405

    options, _, headers = _response(port, token=None, method="OPTIONS")
    assert options == 403
    assert not any(name.lower().startswith("access-control-") for name in headers)

    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=2.0)
    connection.putrequest("POST", "/")
    connection.putheader("Content-Type", "application/json")
    connection.putheader("Authorization", f"Bearer {token}")
    connection.putheader("Content-Length", str(bridge.MAX_CONTENT_LENGTH + 1))
    connection.endheaders()
    response = connection.getresponse()
    assert response.status == 413
    response.read()
    connection.close()
    assert bridge._command_queue.empty()

    duplicate = http.client.HTTPConnection("127.0.0.1", port, timeout=2.0)
    duplicate.putrequest("POST", "/")
    duplicate.putheader("Content-Type", "application/json")
    duplicate.putheader("Authorization", f"Bearer {token}")
    duplicate.putheader("Authorization", "Bearer attacker")
    duplicate.putheader("Content-Length", "2")
    duplicate.endheaders(b"{}")
    duplicate_response = duplicate.getresponse()
    assert duplicate_response.status == 401
    duplicate_response.read()
    duplicate.close()
    assert bridge._command_queue.empty()


@pytest.mark.parametrize(("header", "first", "second", "expected"), (
    ("Authorization", "Bearer first", "Bearer second", 401),
    ("Host", "127.0.0.1:1", "127.0.0.1:2", 400),
    ("Content-Type", "application/json", "application/json", 415),
    ("Content-Length", "2", "2", 411),
))
def test_duplicate_critical_headers_fail_closed(
    bridge, header, first, second, expected
):
    port, token = _start(bridge)
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=2.0)
    connection.putrequest(
        "POST",
        "/",
        skip_host=header == "Host",
        skip_accept_encoding=True,
    )
    if header != "Content-Type":
        connection.putheader("Content-Type", "application/json")
    if header != "Authorization":
        connection.putheader("Authorization", f"Bearer {token}")
    if header != "Content-Length":
        connection.putheader("Content-Length", "2")
    connection.putheader(header, first)
    connection.putheader(header, second)
    connection.endheaders(b"{}")
    response = connection.getresponse()
    assert response.status == expected
    response.read()
    connection.close()
    assert bridge._command_queue.empty()


def test_repeated_duplicate_content_length_returns_stable_411_and_stays_healthy(
    bridge, monkeypatch
):
    port, token = _start(bridge)
    dispatched = []
    original = bridge._execute_command

    def capture(command, params):
        dispatched.append(command)
        return original(command, params)

    monkeypatch.setattr(bridge, "_execute_command", capture)
    expected = {
        "success": False,
        "error": "A valid Content-Length is required",
    }

    for _ in range(25):
        connection = http.client.HTTPConnection("127.0.0.1", port, timeout=2.0)
        connection.putrequest("POST", "/", skip_accept_encoding=True)
        connection.putheader("Content-Type", "application/json")
        connection.putheader("Authorization", f"Bearer {token}")
        connection.putheader("Content-Length", "2")
        connection.putheader("Content-Length", "2")
        connection.endheaders(b"{}")
        response = connection.getresponse()
        payload = json.loads(response.read().decode("utf-8"))
        connection.close()
        assert (response.status, payload) == (411, expected)

    assert dispatched == []
    assert bridge._command_queue.empty()

    status, payload, _ = _queued_response(bridge, port, token)
    assert status == 200
    assert payload["success"] is True
    assert dispatched == ["ping"]

    for credential in (None, "wrong" * 10):
        status, payload, _ = _response(port, token=credential)
        assert (status, payload) == (
            401,
            {"success": False, "error": "Authentication required"},
        )
    assert dispatched == ["ping"]
    assert bridge.get_status()["running"] is True


def test_signed_content_length_returns_411_without_dispatch_and_stays_healthy(
    bridge, monkeypatch
):
    port, token = _start(bridge)
    dispatched = []
    original = bridge._execute_command

    def capture(command, params):
        dispatched.append(command)
        return original(command, params)

    monkeypatch.setattr(bridge, "_execute_command", capture)
    body = b'{"command":"ping","params":{}}'
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=2.0)
    connection.putrequest("POST", "/", skip_accept_encoding=True)
    connection.putheader("Content-Type", "application/json")
    connection.putheader("Authorization", f"Bearer {token}")
    connection.putheader("Content-Length", f"+{len(body)}")
    connection.endheaders(body)
    response = connection.getresponse()
    payload = json.loads(response.read().decode("utf-8"))
    connection.close()

    assert (response.status, payload) == (
        411,
        {"success": False, "error": "A valid Content-Length is required"},
    )
    assert dispatched == []
    assert bridge._command_queue.empty()

    status, payload, _ = _queued_response(bridge, port, token)
    assert status == 200
    assert payload["success"] is True
    assert dispatched == ["ping"]
    assert bridge.get_status()["running"] is True


def test_listener_executes_only_when_main_thread_tick_drains_queue(bridge, monkeypatch):
    port, token = _start(bridge)
    executed_on = []
    original = bridge._execute_command

    def capture(command, params):
        executed_on.append(threading.get_ident())
        return original(command, params)

    monkeypatch.setattr(bridge, "_execute_command", capture)
    completed: queue.Queue = queue.Queue()
    worker = threading.Thread(
        target=lambda: completed.put(_response(port, token=token)),
        daemon=True,
    )
    worker.start()
    deadline = time.time() + 2.0
    while bridge._command_queue.empty() and time.time() < deadline:
        time.sleep(0.01)
    assert not bridge._command_queue.empty()
    assert executed_on == []
    main_thread = threading.get_ident()
    bridge._tick(0.0)
    worker.join(timeout=2.0)
    assert completed.get_nowait()[0] == 200
    assert executed_on == [main_thread]
    assert bridge._dispatch_mode == "authenticated_queued"


def test_token_rotates_clears_and_never_enters_status_or_logs(bridge):
    first_port, first = _start(bridge)
    first_status = bridge.get_status()
    assert first_status["authenticated"] is True
    assert first_status["transport"] == "authenticated_queued"
    assert first not in json.dumps(first_status)
    assert first not in "\n".join(bridge._log_ring)
    assert first not in json.dumps(bridge.mcp_start(port=first_port))
    assert isinstance(bridge._c_get_log(200)["lines"], list)
    assert first not in json.dumps(bridge._c_get_log(200))

    handoff = bridge._token_handoff_path()
    assert handoff.exists()
    bridge.stop_listener()
    assert not handoff.exists()
    assert bridge._session_secret is None
    assert bridge.get_status()["transport"] == "unavailable"

    second_port = first_port if first_port else _free_port()
    bridge.start_listener(second_port)
    second = json.loads(handoff.read_text(encoding="utf-8"))["token"]
    assert second != first
    assert second not in json.dumps(bridge.get_status())
    assert second not in "\n".join(bridge._log_ring)


def test_active_secret_is_redacted_from_every_server_surface(bridge, monkeypatch):
    port, secret = _start(bridge)

    invalid_body = json.dumps({"command": secret, "params": {}}).encode()
    _status, invalid, _headers = _queued_response(
        bridge, port, secret, invalid_body
    )

    def fail_with_nested_secret(payload):
        raise RuntimeError(f"nested failure: {payload}")

    monkeypatch.setitem(bridge._HANDLERS, "synthetic_failure", fail_with_nested_secret)
    failure_body = json.dumps({
        "command": "synthetic_failure",
        "params": {"payload": {"tuple": [secret, f"prefix-{secret}-suffix"]}},
    }).encode()
    _status, failure, _headers = _queued_response(
        bridge, port, secret, failure_body
    )

    surfaces = {
        "invalid": invalid,
        "failure": failure,
        "logs": bridge._c_get_log(bridge.LOG_RING_SIZE),
        "history": bridge._c_history(bridge.HISTORY_CAP),
    }
    serialized = json.dumps(surfaces)
    assert secret not in serialized
    assert bridge._REDACTED in serialized
    assert secret not in "\n".join(bridge._log_ring)
    assert secret not in json.dumps(list(bridge._history))


def test_stop_rejects_pending_work_and_cleans_transport(bridge):
    port, token = _start(bridge)
    completed: queue.Queue = queue.Queue()
    worker = threading.Thread(
        target=lambda: completed.put(_response(port, token=token)),
        daemon=True,
    )
    worker.start()
    deadline = time.time() + 2.0
    while bridge._command_queue.empty() and time.time() < deadline:
        time.sleep(0.01)
    assert not bridge._command_queue.empty()

    handoff = bridge._token_handoff_path()
    bridge.stop_listener()
    worker.join(timeout=2.0)
    assert not worker.is_alive()
    status, payload, _ = completed.get_nowait()
    assert status == 200
    assert payload["success"] is False
    assert "stopped before command dispatch" in payload["error"]
    assert bridge._command_queue.empty()
    assert bridge._responses == {}
    assert bridge._server is None
    assert not handoff.exists()


def test_execute_python_is_unavailable_even_with_former_opt_in(bridge, monkeypatch):
    monkeypatch.setenv("UEFN_TOOLBELT_MCP_ALLOW_EXECUTE_PYTHON", "1")
    port, token = _start(bridge)
    status = bridge.get_status()
    assert status["execute_python_enabled"] is False
    assert "execute_python" not in bridge._public_commands()
    assert "execute_python" not in bridge._HANDLERS
    with pytest.raises(ValueError, match="Unknown command"):
        bridge._dispatch("execute_python", {"code": "result = 1"})

    body = json.dumps({
        "command": "execute_python",
        "params": {"code": "result = 1"},
    }).encode()
    http_status, payload, _ = _queued_response(bridge, port, token, body)
    assert http_status == 200
    assert payload["success"] is False
    assert "Unknown command" in payload["error"]


@pytest.mark.parametrize("tool_name", ("mcp_start", "mcp_stop", "mcp_restart"))
def test_listener_lifecycle_tools_are_local_only(bridge, tool_name):
    with pytest.raises(PermissionError, match="local-only"):
        bridge._c_run_tool(tool_name)


def test_integration_suite_is_local_only(bridge):
    with pytest.raises(PermissionError, match="local-only"):
        bridge._c_run_tool("toolbelt_integration_test")


@pytest.mark.parametrize("operation", ("start", "stop", "restart"))
def test_remote_dispatch_blocks_indirect_lifecycle_and_batch_bypass(
    bridge, monkeypatch, operation
):
    port, token = _start(bridge)

    def indirect_lifecycle():
        if operation == "start":
            bridge.start_listener(port)
        elif operation == "stop":
            bridge.stop_listener()
        else:
            bridge.restart_listener(port)
        return {"unexpected": True}

    command = f"synthetic_indirect_{operation}"
    monkeypatch.setitem(bridge._HANDLERS, command, indirect_lifecycle)

    direct = bridge._execute_command(command, {})
    assert direct["success"] is False
    assert "local-only" in direct["error"]
    assert bridge.get_status()["running"] is True
    assert json.loads(bridge._token_handoff_path().read_text(encoding="utf-8"))[
        "token"
    ] == token

    batched = bridge._execute_command("batch_exec", {"commands": [{
        "command": command,
        "params": {},
    }]})
    assert batched["success"] is True
    nested = batched["result"]["results"][0]
    assert nested["success"] is False
    assert "local-only" in nested["error"]
    assert bridge.get_status()["running"] is True
    assert json.loads(bridge._token_handoff_path().read_text(encoding="utf-8"))[
        "token"
    ] == token


def test_callback_registration_failure_leaves_no_listener_or_direct_mode(
    bridge, monkeypatch
):
    monkeypatch.setattr(
        bridge.unreal,
        "register_slate_post_tick_callback",
        lambda callback: (_ for _ in ()).throw(RuntimeError("Slate unavailable")),
    )
    token_file = bridge._token_handoff_path()
    token_file.write_text("stale credential", encoding="utf-8")
    with pytest.raises(RuntimeError, match="queued Slate dispatch"):
        bridge.start_listener(_free_port())
    assert bridge._server is None
    assert bridge._server_thread is None
    assert bridge._tick_handle is None
    assert bridge._session_secret is None
    assert bridge._dispatch_mode == "unavailable"
    assert not token_file.exists()


class _FakeFastMCP:
    def __init__(self, *args, **kwargs):
        self.tools = {}
        self.instructions = kwargs.get("instructions", "")

    def tool(self):
        def register(function):
            self.tools[function.__name__] = function
            return function
        return register

    def run(self):  # pragma: no cover - entry point is never invoked in tests
        raise AssertionError("FastMCP.run() must not run during unit tests")


def _load_external_client(repo_root, tmp_path, monkeypatch, token: str):
    fastmcp = types.ModuleType("mcp.server.fastmcp")
    fastmcp.FastMCP = _FakeFastMCP
    server = types.ModuleType("mcp.server")
    mcp_package = types.ModuleType("mcp")
    monkeypatch.setitem(sys.modules, "mcp", mcp_package)
    monkeypatch.setitem(sys.modules, "mcp.server", server)
    monkeypatch.setitem(sys.modules, "mcp.server.fastmcp", fastmcp)
    handoff = tmp_path / "external_session.json"
    handoff.write_text(
        json.dumps({
            "version": 1,
            "host": "127.0.0.1",
            "port": 8765,
            "token": token,
        }),
        encoding="utf-8",
    )
    monkeypatch.setenv("UEFN_MCP_TOKEN_FILE", str(handoff))
    spec = importlib.util.spec_from_file_location(
        "mcp_server_security_case",
        repo_root / "mcp_server.py",
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, handoff


def test_external_client_authenticates_without_exposing_token(
    repo_root, tmp_path, monkeypatch
):
    token = "s" * 43
    monkeypatch.setenv("UEFN_TOOLBELT_MCP_ALLOW_EXECUTE_PYTHON", "1")
    client, handoff = _load_external_client(repo_root, tmp_path, monkeypatch, token)
    captured = {}

    class Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return b'{"success":true,"result":{"status":"ok"}}'

    def success(request, timeout):
        captured["authorization"] = request.get_header("Authorization")
        return Response()

    # The transport seam is the per-request direct opener (WO-004 Session B).
    monkeypatch.setattr(client, "_direct_opener", lambda: _Opener(success))
    assert client._send("ping") == {"status": "ok"}
    assert captured["authorization"] == f"Bearer {token}"
    assert "execute_python" not in client.mcp.tools

    rotated = "r" * 43
    handoff.write_text(
        json.dumps({
            "version": 1,
            "host": "127.0.0.1",
            "port": 8765,
            "token": rotated,
        }),
        encoding="utf-8",
    )
    assert client._send("ping") == {"status": "ok"}
    assert captured["authorization"] == f"Bearer {rotated}"

    def unauthorized(request, timeout):
        # The bridge's own 401 carries its exact rejection body; a bodiless
        # 401 is an unknown outcome under Session B, not a rejection.
        raise urllib.error.HTTPError(
            request.full_url, 401, "Unauthorized", {},
            io.BytesIO(_BRIDGE_401_BODY),
        )

    monkeypatch.setattr(client, "_direct_opener", lambda: _Opener(unauthorized))
    with pytest.raises(PermissionError) as exc_info:
        client._send("ping")
    for secret in (token, rotated):
        assert secret not in str(exc_info.value)
        assert secret not in repr(exc_info.value)

    class ReflectedFailure(Response):
        def read(self):
            return json.dumps({
                "success": False,
                "error": f"failure {rotated}",
                "traceback": {"nested": [rotated]},
            }).encode()

    monkeypatch.setattr(
        client,
        "_direct_opener",
        lambda: _Opener(lambda request, timeout: ReflectedFailure()),
    )
    with pytest.raises(RuntimeError) as reflected:
        client._send(rotated)
    assert rotated not in str(reflected.value)
    assert "[REDACTED]" in str(reflected.value)


def test_stdlib_client_uses_handoff_and_keeps_execute_python_off(
    repo_root, tmp_path, monkeypatch
):
    spec = importlib.util.spec_from_file_location(
        "toolbelt_stdlib_client_security_case",
        repo_root / "client.py",
    )
    assert spec is not None and spec.loader is not None
    client_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(client_module)

    token = "t" * 43
    handoff = tmp_path / "client_session.json"
    handoff.write_text(
        json.dumps({
            "version": 1,
            "host": "127.0.0.1",
            "port": 8765,
            "token": token,
        }),
        encoding="utf-8",
    )
    client = client_module.ToolbeltClient(token_file=handoff)
    captured = {}

    class Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return b'{"success":true,"result":{"status":"ok"}}'

    def success(request, timeout):
        captured["authorization"] = request.get_header("Authorization")
        return Response()

    # The transport seam is the per-request direct opener (WO-004 Session B).
    monkeypatch.setattr(client_module, "_direct_opener", lambda: _Opener(success))
    assert client.ping() == {"status": "ok"}
    assert captured["authorization"] == f"Bearer {token}"

    monkeypatch.setenv("UEFN_TOOLBELT_MCP_ALLOW_EXECUTE_PYTHON", "1")
    with pytest.raises(client_module.ToolbeltError, match="unavailable"):
        client.execute_python("result = 1")

    class ReflectedFailure(Response):
        def read(self):
            return json.dumps({
                "success": False,
                "error": token,
                "traceback": {"nested": [f"prefix-{token}"]},
            }).encode()

    monkeypatch.setattr(
        client_module,
        "_direct_opener",
        lambda: _Opener(lambda request, timeout: ReflectedFailure()),
    )
    with pytest.raises(client_module.ToolbeltError) as reflected:
        client._send(token)
    assert token not in str(reflected.value)
    assert "[REDACTED]" in str(reflected.value)

    def unauthorized(request, timeout):
        # The bridge's own 401 carries its exact rejection body; a bodiless
        # 401 is an unknown outcome under Session B, not a rejection.
        raise urllib.error.HTTPError(
            request.full_url, 401, "Unauthorized", {},
            io.BytesIO(_BRIDGE_401_BODY),
        )

    monkeypatch.setattr(client_module, "_direct_opener", lambda: _Opener(unauthorized))
    with pytest.raises(client_module.AuthenticationError) as exc_info:
        client.ping()
    assert token not in str(exc_info.value)
    assert token not in repr(exc_info.value)


# --- WO-004 Session B: client outcome semantics -----------------------------
#
# The static verification the issued WO-004 mandate prescribes for both
# clients. Every test uses a dummy token and a synthetic handoff, and drives
# either the per-request opener seam or isolated fake servers on ephemeral
# loopback ports. None reads a live handoff, uses a live token, or reaches a
# real proxy. Proving what a running editor produces is Session C's job.

_DUMMY_TOKEN = "dummy-session-token-for-outcome-tests-" + "x" * 10
_BRIDGE_401_BODY = b'{"success": false, "error": "Authentication required"}'
_BRIDGE_SOURCE = (
    Path(__file__).resolve().parents[1] / "Content" / "Python"
    / "UEFN_Toolbelt" / "tools" / "mcp_bridge.py"
)
_STOP_DRAIN = "MCP listener stopped before command dispatch"
_COMMAND = "set_viewport_camera"
# The command carries the dummy token, so every row also proves redaction.
_SENT = _COMMAND + "-" + _DUMMY_TOKEN
_UNKNOWN_PHRASES = (
    "may not have run",
    "may still be queued or running",
    "may have completed",
    "until that state has been checked",
    "can also go unanswered",
    "cannot determine why no reply arrived",
    "UEFN editor",
)
_FORBIDDEN_IN_UNKNOWN = (
    "modal", "dialog", "blocked", "heavy operation", "shorter operation",
    "retry", "rejected", "refused", "not running",
)


class _Opener:
    """Stands in for the per-request direct opener and records each attempt."""

    def __init__(self, respond):
        self.respond = respond
        self.attempts: list = []

    def open(self, request, timeout=None):
        self.attempts.append(request)
        return self.respond(request, timeout)


class _Reply:
    """A 2xx response as urllib returns it: status, then a readable body."""

    def __init__(self, status: int, body):
        self.status = status
        self._body = body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        if isinstance(self._body, BaseException):
            raise self._body
        return self._body


def _respond_with(factory):
    def respond(request, timeout):
        outcome = factory()
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome
    return respond


def _http_error(code: int, body: bytes | None) -> urllib.error.HTTPError:
    fp = None if body is None else io.BytesIO(body)
    return urllib.error.HTTPError("http://127.0.0.1:8765/", code, "status", {}, fp)


def _envelope(error: str, **extra) -> bytes:
    return json.dumps({"success": False, "error": error, **extra}).encode()


def _bridge_rejection_pairs() -> set[tuple[int, str]]:
    """Every literal (status, error) the bridge passes to _reject or _error."""
    tree = ast.parse(_BRIDGE_SOURCE.read_text(encoding="utf-8"))
    pairs = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr in ("_reject", "_error")
            and len(node.args) >= 2
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, int)
            and isinstance(node.args[1], ast.Constant)
            and isinstance(node.args[1].value, str)
        ):
            pairs.add((node.args[0].value, node.args[1].value))
    return pairs


def _bridge_deadline_prefixes() -> list[str]:
    """The literal prefix of every 504 body the bridge formats."""
    tree = ast.parse(_BRIDGE_SOURCE.read_text(encoding="utf-8"))
    prefixes = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "_error"
            and len(node.args) >= 2
            and isinstance(node.args[0], ast.Constant)
            and node.args[0].value == 504
            and isinstance(node.args[1], ast.JoinedStr)
            and isinstance(node.args[1].values[0], ast.Constant)
        ):
            prefixes.append(node.args[1].values[0].value)
    return prefixes


def _stdlib_client_module(repo_root):
    spec = importlib.util.spec_from_file_location(
        "toolbelt_client_outcome_case", repo_root / "client.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_handoff(path, port: int = 8765, token: str = _DUMMY_TOKEN):
    path.write_text(json.dumps({
        "version": 1, "host": "127.0.0.1", "port": port, "token": token,
    }), encoding="utf-8")
    return path


def _sender(kind, repo_root, tmp_path, monkeypatch, *, port: int = 8765,
            handoff: str = "valid"):
    """(module, send) for one client, wired to a synthetic handoff.

    `handoff` is "valid", "missing", or "invalid" (a too-short token).
    """
    token = _DUMMY_TOKEN if handoff != "invalid" else "short"
    if kind == "client":
        module = _stdlib_client_module(repo_root)
        path = tmp_path / "client_outcome_handoff.json"
        if handoff != "missing":
            _write_handoff(path, port, token)
        return module, module.ToolbeltClient(token_file=path)._send
    module, path = _load_external_client(
        repo_root, tmp_path, monkeypatch, _DUMMY_TOKEN
    )
    if handoff == "missing":
        path.unlink()
    else:
        _write_handoff(path, port, token)
    return module, module._send


def _expected(kind, module, name):
    return getattr(module, name) if kind == "client" else getattr(builtins, name)


_KINDS = ("client", "server")

# (id, outcome factory, client.py class, mcp_server.py class, message group)
_OUTCOME_ROWS = [
    ("refused",
     lambda: urllib.error.URLError(ConnectionRefusedError(10061, "refused")),
     "NotConnected", "ConnectionError", "refused"),
    ("timeout-direct", lambda: TimeoutError("timed out"),
     "CommandTimeout", "TimeoutError", "unknown"),
    ("timeout-wrapped",
     lambda: urllib.error.URLError(TimeoutError("timed out")),
     "CommandTimeout", "TimeoutError", "unknown"),
    ("504-bridge-deadline",
     lambda: _http_error(504, _envelope("Command timed out: " + _SENT)),
     "CommandTimeout", "TimeoutError", "unknown"),
    ("504-other-command",
     lambda: _http_error(504, _envelope("Command timed out: ping")),
     "OutcomeUnknown", "RuntimeError", "unknown"),
    ("504-without-body", lambda: _http_error(504, None),
     "OutcomeUnknown", "RuntimeError", "unknown"),
    ("401-without-body", lambda: _http_error(401, None),
     "OutcomeUnknown", "RuntimeError", "unknown"),
    ("401-extra-key",
     lambda: _http_error(401, _envelope("Authentication required",
                                        traceback="")),
     "OutcomeUnknown", "RuntimeError", "unknown"),
    ("301", lambda: _http_error(301, b"moved"),
     "OutcomeUnknown", "RuntimeError", "unknown"),
    ("302", lambda: _http_error(302, b"found"),
     "OutcomeUnknown", "RuntimeError", "unknown"),
    ("303", lambda: _http_error(303, b"see other"),
     "OutcomeUnknown", "RuntimeError", "unknown"),
    ("502", lambda: _http_error(502, b"<html>bad gateway</html>"),
     "OutcomeUnknown", "RuntimeError", "unknown"),
    ("203-success", lambda: _Reply(203, b'{"success": true, "result": 1}'),
     "OutcomeUnknown", "RuntimeError", "unknown"),
    ("remote-disconnected", lambda: http.client.RemoteDisconnected("closed"),
     "OutcomeUnknown", "RuntimeError", "unknown"),
    ("connection-reset", lambda: ConnectionResetError(10054, "reset"),
     "OutcomeUnknown", "RuntimeError", "unknown"),
    ("connection-reset-wrapped",
     lambda: urllib.error.URLError(ConnectionResetError(10054, "reset")),
     "OutcomeUnknown", "ConnectionError", "unknown"),
    ("other-url-error", lambda: urllib.error.URLError(OSError("unreachable")),
     "OutcomeUnknown", "ConnectionError", "unknown"),
    # A refusal is recognized by the reason's type only, never by its text.
    ("url-error-text-mentions-refusal",
     lambda: urllib.error.URLError(OSError(
         "No connection could be made because the target machine actively"
         " refused it")),
     "OutcomeUnknown", "ConnectionError", "unknown"),
    ("200-truncated",
     lambda: _Reply(200, http.client.IncompleteRead(b'{"succ', 20)),
     "OutcomeUnknown", "RuntimeError", "unknown"),
    ("200-non-json", lambda: _Reply(200, b"<html>ok</html>"),
     "OutcomeUnknown", "RuntimeError", "unknown"),
    ("200-non-object", lambda: _Reply(200, b"[1, 2, 3]"),
     "OutcomeUnknown", "RuntimeError", "unknown"),
    ("200-truthy-non-boolean",
     lambda: _Reply(200, b'{"success": "yes", "result": 1}'),
     "OutcomeUnknown", "RuntimeError", "unknown"),
    ("200-stop-drain", lambda: _Reply(200, _envelope(_STOP_DRAIN)),
     "ToolbeltError", "RuntimeError", "drained"),
    ("200-stop-drain-with-traceback",
     lambda: _Reply(200, _envelope(_STOP_DRAIN, traceback="Traceback ...")),
     "ToolbeltError", "RuntimeError", "failure"),
    ("200-reported-failure",
     lambda: _Reply(200, _envelope("failure " + _DUMMY_TOKEN,
                                   traceback="tb " + _DUMMY_TOKEN)),
     "ToolbeltError", "RuntimeError", "failure"),
]
for _code, _error in sorted(_bridge_rejection_pairs()):
    _OUTCOME_ROWS.append((
        "rejected-" + str(_code) + "-" + _error,
        (lambda code=_code, error=_error: _http_error(code, _envelope(error))),
        "AuthenticationError" if _code == 401 else "ToolbeltError",
        "PermissionError" if _code == 401 else "RuntimeError",
        "rejected",
    ))
for _code in sorted({code for code, _error in _bridge_rejection_pairs()}):
    _OUTCOME_ROWS.append((
        "status-" + str(_code) + "-other-body",
        (lambda code=_code: _http_error(code, _envelope("some other error"))),
        "OutcomeUnknown", "RuntimeError", "unknown",
    ))


@pytest.mark.parametrize("kind", _KINDS)
@pytest.mark.parametrize(("name", "factory", "client_cls", "server_cls", "group"),
                         _OUTCOME_ROWS, ids=[row[0] for row in _OUTCOME_ROWS])
def test_outcome_classification_follows_the_mandate(
    repo_root, tmp_path, monkeypatch, kind, name, factory, client_cls,
    server_cls, group
):
    """Each response raises its class after exactly one attempt, redacted.

    Static verification items 1, 3, 7, and 9 of the issued WO-004 mandate.
    """
    module, send = _sender(kind, repo_root, tmp_path, monkeypatch)
    opener = _Opener(_respond_with(factory))
    monkeypatch.setattr(module, "_direct_opener", lambda: opener)
    expected = _expected(kind, module, client_cls if kind == "client"
                         else server_cls)

    with pytest.raises(expected) as exc_info:
        send(_SENT)

    error = exc_info.value
    assert type(error) is expected, name + ": raised " + type(error).__name__
    assert len(opener.attempts) == 1, name + ": attempts " + str(len(opener.attempts))
    message = str(error)
    assert _DUMMY_TOKEN not in message
    assert _DUMMY_TOKEN not in repr(error)
    lowered = message.lower()
    if group == "unknown":
        assert _COMMAND in message
        for phrase in _UNKNOWN_PHRASES:
            assert phrase in message, name + ": missing " + repr(phrase)
        for word in _FORBIDDEN_IN_UNKNOWN:
            assert word not in lowered, name + ": names " + repr(word)
    else:
        assert "may not have run" not in message
    if group == "refused":
        assert "no request reached" in message
    if group == "rejected":
        assert "rejected the request before queueing it" in message
    else:
        assert "reject" not in lowered, name + ": rejection wording"
    if group == "drained":
        assert "stopped before it dispatched" in message
    if group == "failure":
        assert "may have failed before running or partway through" in message
        for claim in ("did not run", "was not executed", "was executed",
                      "has run"):
            assert claim not in lowered


@pytest.mark.parametrize("kind", _KINDS)
def test_a_bridge_result_is_returned_after_one_attempt(
    repo_root, tmp_path, monkeypatch, kind
):
    """Row 7: a 200 whose body is an object with success true."""
    module, send = _sender(kind, repo_root, tmp_path, monkeypatch)
    opener = _Opener(_respond_with(
        lambda: _Reply(200, b'{"success": true, "result": {"ok": 1}}')))
    monkeypatch.setattr(module, "_direct_opener", lambda: opener)
    assert send("ping") == {"ok": 1}
    assert len(opener.attempts) == 1


@pytest.mark.parametrize("kind", _KINDS)
@pytest.mark.parametrize("handoff", ("missing", "invalid"))
def test_no_request_is_attempted_without_a_valid_handoff(
    repo_root, tmp_path, monkeypatch, kind, handoff
):
    """Row 1: zero attempts, and the message says no request was sent."""
    module, send = _sender(kind, repo_root, tmp_path, monkeypatch,
                           handoff=handoff)
    opener = _Opener(_respond_with(lambda: AssertionError("no attempt")))
    monkeypatch.setattr(module, "_direct_opener", lambda: opener)
    expected = _expected(kind, module, "AuthenticationError" if kind == "client"
                         else "ConnectionError")

    with pytest.raises(expected) as exc_info:
        send(_COMMAND)

    assert type(exc_info.value) is expected
    assert opener.attempts == []
    assert "No request was sent" in str(exc_info.value)
    assert "may not have run" not in str(exc_info.value)


class _PreThreeTenTimeout(OSError):
    """socket.timeout as it was before Python 3.10: an OSError, not TimeoutError."""


@pytest.mark.parametrize("kind", _KINDS)
@pytest.mark.parametrize("wrapped", (False, True), ids=("direct", "wrapped"))
def test_a_distinct_socket_timeout_type_is_still_a_timeout(
    repo_root, tmp_path, monkeypatch, kind, wrapped
):
    """Row 3 holds where socket.timeout is not TimeoutError (Python < 3.10).

    This simulates that relationship on the running interpreter; it does not
    prove execution on an untested Python version.
    """
    assert not issubclass(_PreThreeTenTimeout, TimeoutError)
    monkeypatch.setattr(socket, "timeout", _PreThreeTenTimeout)
    module, send = _sender(kind, repo_root, tmp_path, monkeypatch)

    def factory():
        error = _PreThreeTenTimeout("timed out")
        return urllib.error.URLError(error) if wrapped else error

    opener = _Opener(_respond_with(factory))
    monkeypatch.setattr(module, "_direct_opener", lambda: opener)
    expected = _expected(kind, module, "CommandTimeout" if kind == "client"
                         else "TimeoutError")

    with pytest.raises(expected) as exc_info:
        send(_COMMAND)

    assert type(exc_info.value) is expected
    assert len(opener.attempts) == 1


@pytest.mark.parametrize("kind", _KINDS)
def test_known_bridge_responses_match_the_bridge_source(
    repo_root, tmp_path, monkeypatch, kind
):
    """Static verification item 2: a bridge message change fails here.

    The clients' enumerated rejections equal the bridge's literal _reject and
    _error pairs; the 504 deadline prefix and the stop-drain error match the
    bridge's own text.
    """
    module, _send = _sender(kind, repo_root, tmp_path, monkeypatch)
    bridge_pairs = _bridge_rejection_pairs()
    assert len(bridge_pairs) >= 14
    assert bridge_pairs == module._BRIDGE_REJECTIONS
    assert _bridge_deadline_prefixes() == [module._DEADLINE_ERROR_PREFIX]
    assert (
        '"error": "' + module._STOP_DRAIN_ERROR + '"'
        in _BRIDGE_SOURCE.read_text(encoding="utf-8")
    )


def _counting_real_opener(module, monkeypatch):
    """Wrap the production opener so each real attempt is recorded."""
    real = module._direct_opener
    attempts: list = []

    def counting():
        opener = real()
        original = opener.open

        def open_(request, *args, **kwargs):
            attempts.append(request.full_url)
            return original(request, *args, **kwargs)

        opener.open = open_
        return opener

    monkeypatch.setattr(module, "_direct_opener", counting)
    return attempts


def _fake_server(status: int, body: bytes, headers: dict | None = None):
    """A loopback HTTP server that records every request it receives."""
    seen: list = []

    class Handler(http.server.BaseHTTPRequestHandler):
        def _handle(self):
            length = int(self.headers.get("Content-Length") or 0)
            payload = self.rfile.read(length) if length else b""
            seen.append({
                "line": self.requestline,
                "authorization": self.headers.get("Authorization"),
                "body": payload,
            })
            self.send_response(status)
            for key, value in (headers or {}).items():
                self.send_header(key, value)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        do_GET = do_POST = _handle

        def log_message(self, *args):
            pass

    server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, seen


class _RawListener:
    """A loopback TCP listener that records any connection and any bytes."""

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(("127.0.0.1", 0))
        self.sock.listen(5)
        self.sock.settimeout(0.1)
        self.port = int(self.sock.getsockname()[1])
        self.accepted = 0
        self.received = b""
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        while not self._stop.is_set():
            try:
                connection, _address = self.sock.accept()
            except OSError:
                continue
            self.accepted += 1
            connection.settimeout(0.5)
            try:
                self.received += connection.recv(65536)
            except OSError:
                pass
            connection.close()

    def close(self):
        self._stop.set()
        self._thread.join(timeout=2.0)
        self.sock.close()


@pytest.mark.parametrize("kind", _KINDS)
def test_a_refused_connection_delivers_nothing(
    repo_root, tmp_path, monkeypatch, kind
):
    """Static verification item 4, on the real opener and a closed port."""
    module, send = _sender(kind, repo_root, tmp_path, monkeypatch,
                           port=_free_port())
    attempts = _counting_real_opener(module, monkeypatch)
    expected = _expected(kind, module, "NotConnected" if kind == "client"
                         else "ConnectionError")

    with pytest.raises(expected) as exc_info:
        send(_COMMAND)

    assert type(exc_info.value) is expected
    assert len(attempts) == 1
    assert "no request reached" in str(exc_info.value)
    assert "may not have run" not in str(exc_info.value)


@pytest.mark.parametrize("kind", _KINDS)
def test_environment_proxies_are_bypassed(
    repo_root, tmp_path, monkeypatch, kind
):
    """Static verification item 5: the fake proxy sees no connection."""
    endpoint, seen = _fake_server(
        200, b'{"success": true, "result": {"via": "endpoint"}}')
    proxy = _RawListener()
    try:
        module, send = _sender(kind, repo_root, tmp_path, monkeypatch,
                               port=endpoint.server_address[1])
        proxy_url = "http://127.0.0.1:" + str(proxy.port)
        for name in ("HTTP_PROXY", "http_proxy", "ALL_PROXY"):
            monkeypatch.setenv(name, proxy_url)
        for name in ("NO_PROXY", "no_proxy"):
            monkeypatch.delenv(name, raising=False)
        # Non-vacuous: urllib's default handling would route through it.
        assert urllib.request.getproxies().get("http") == proxy_url
        environment = dict(os.environ)
        global_opener = urllib.request._opener

        assert send("ping") == {"via": "endpoint"}

        assert dict(os.environ) == environment
        assert urllib.request._opener is global_opener
        assert len(seen) == 1
        assert seen[0]["authorization"] == "Bearer " + _DUMMY_TOKEN
        assert proxy.accepted == 0
        assert _DUMMY_TOKEN.encode() not in proxy.received
    finally:
        proxy.close()
        endpoint.shutdown()
        endpoint.server_close()


@pytest.mark.parametrize("kind", _KINDS)
def test_a_redirect_is_not_followed(repo_root, tmp_path, monkeypatch, kind):
    """Static verification item 6: one attempt, and the target sees nothing."""
    target, target_seen = _fake_server(
        200, b'{"success": true, "result": {"via": "redirect"}}')
    first, first_seen = _fake_server(302, b"", {
        "Location": "http://127.0.0.1:" + str(target.server_address[1])
                    + "/elsewhere",
    })
    try:
        module, send = _sender(kind, repo_root, tmp_path, monkeypatch,
                               port=first.server_address[1])
        attempts = _counting_real_opener(module, monkeypatch)
        expected = _expected(kind, module, "OutcomeUnknown" if kind == "client"
                             else "RuntimeError")

        with pytest.raises(expected) as exc_info:
            send(_COMMAND)

        assert type(exc_info.value) is expected
        assert len(attempts) == 1
        assert len(first_seen) == 1
        assert target_seen == []
        assert "may not have run" in str(exc_info.value)
    finally:
        for server in (first, target):
            server.shutdown()
            server.server_close()


@pytest.mark.parametrize("kind", _KINDS)
def test_the_production_opener_is_direct_and_per_request(
    repo_root, tmp_path, monkeypatch, kind
):
    """No proxy handler at all, and no redirect handler that follows.

    ProxyHandler({}) registers no protocol method, so the opener does not
    keep it; passing it only stops build_opener adding the default handler
    that reads environment and system proxies.
    """
    module, _send = _sender(kind, repo_root, tmp_path, monkeypatch)
    monkeypatch.setenv("HTTP_PROXY", "http://127.0.0.1:9")
    opener = module._direct_opener()
    assert opener is not module._direct_opener()
    assert not [handler for handler in opener.handlers
                if isinstance(handler, urllib.request.ProxyHandler)]
    default = urllib.request.build_opener()
    assert [handler for handler in default.handlers
            if isinstance(handler, urllib.request.ProxyHandler)], (
        "control: with a proxy configured, urllib's default opener keeps one"
    )
    redirects = [handler for handler in opener.handlers
                 if isinstance(handler, urllib.request.HTTPRedirectHandler)]
    assert len(redirects) == 1
    assert type(redirects[0]) is module._RefuseRedirects


def test_connect_sends_a_single_ping(repo_root, tmp_path, monkeypatch):
    module = _stdlib_client_module(repo_root)
    monkeypatch.setenv("UEFN_MCP_TOKEN_FILE",
                       str(_write_handoff(tmp_path / "connect_handoff.json")))
    opener = _Opener(_respond_with(
        lambda: _Reply(200, b'{"success": true, "result": {"status": "ok"}}')))
    monkeypatch.setattr(module, "_direct_opener", lambda: opener)
    module.connect()
    assert len(opener.attempts) == 1


def test_outcome_unknown_sits_inside_the_existing_hierarchy(repo_root):
    module = _stdlib_client_module(repo_root)
    assert issubclass(module.OutcomeUnknown, module.ToolbeltError)
    assert issubclass(module.CommandTimeout, module.OutcomeUnknown)
    assert not issubclass(module.NotConnected, module.OutcomeUnknown)
    assert not issubclass(module.AuthenticationError, module.OutcomeUnknown)


def test_agent_instructions_explain_unknown_outcomes(
    repo_root, tmp_path, monkeypatch
):
    """Static verification item 8."""
    module, _handoff = _load_external_client(
        repo_root, tmp_path, monkeypatch, _DUMMY_TOKEN)
    instructions = module.mcp.instructions
    for phrase in (
        "a timeout, a lost connection, or an unexpected response",
        "Do not automatically send a state-changing tool call again",
        "inspect state with read tools before deciding",
        "get_history entries carry a command name, an elapsed time, and a "
        "success flag",
        "cannot identify a specific call or show how many times it ran",
    ):
        assert phrase in instructions, phrase
    lowered = instructions.lower()
    assert "modal" not in lowered
    assert "dialog" not in lowered


# --- Session B review follow-ups: three discriminating regression families --


class _StallingBody:
    """An HTTP error body whose read times out, as a stalled socket would."""

    def read(self, *args):
        raise TimeoutError("timed out")

    def readline(self, *args):
        raise TimeoutError("timed out")

    def close(self):
        pass


@pytest.mark.parametrize("kind", _KINDS)
@pytest.mark.parametrize("code", (504, 401, 502))
def test_a_timeout_reading_an_error_body_is_a_timeout(
    repo_root, tmp_path, monkeypatch, kind, code
):
    """Row 3 still precedes rows 4 to 6 when the error body's read times out."""
    module, send = _sender(kind, repo_root, tmp_path, monkeypatch)
    opener = _Opener(_respond_with(lambda: urllib.error.HTTPError(
        "http://127.0.0.1:8765/", code, "status", {}, _StallingBody())))
    monkeypatch.setattr(module, "_direct_opener", lambda: opener)
    expected = _expected(kind, module, "CommandTimeout" if kind == "client"
                         else "TimeoutError")

    with pytest.raises(expected) as exc_info:
        send(_SENT)

    error = exc_info.value
    assert type(error) is expected
    assert len(opener.attempts) == 1
    assert error.__suppress_context__ is True
    message = str(error)
    for phrase in _UNKNOWN_PHRASES:
        assert phrase in message
    assert _DUMMY_TOKEN not in message
    assert _DUMMY_TOKEN not in repr(error)


# A known rejection or deadline body requires success to be exactly the
# boolean false. A numeric 0 compares equal to False but is not the bridge's
# envelope, so the reply stays an unknown outcome.
_NUMERIC_FALSE_BODIES = (
    ("401-success-zero", 401, {"success": 0, "error": "Authentication required"}),
    ("400-success-zero", 400, {"success": 0, "error": "Malformed JSON request"}),
    ("504-success-zero", 504, {"success": 0, "error": "Command timed out: " + _SENT}),
)


@pytest.mark.parametrize("kind", _KINDS)
@pytest.mark.parametrize(("name", "code", "body"), _NUMERIC_FALSE_BODIES,
                         ids=[row[0] for row in _NUMERIC_FALSE_BODIES])
def test_numeric_false_is_not_the_bridge_envelope(
    repo_root, tmp_path, monkeypatch, kind, name, code, body
):
    module, send = _sender(kind, repo_root, tmp_path, monkeypatch)
    opener = _Opener(_respond_with(
        lambda: _http_error(code, json.dumps(body).encode())))
    monkeypatch.setattr(module, "_direct_opener", lambda: opener)
    expected = _expected(kind, module, "OutcomeUnknown" if kind == "client"
                         else "RuntimeError")

    with pytest.raises(expected) as exc_info:
        send(_SENT)

    assert type(exc_info.value) is expected, (
        name + ": " + type(exc_info.value).__name__)
    assert len(opener.attempts) == 1
    assert "may not have run" in str(exc_info.value)
    assert "reject" not in str(exc_info.value).lower()


# Unknown outcomes raised while a transport exception is being handled
# suppress that exception's context, so its text - which can repeat request
# details - never travels with the client's error.
_CONTEXT_ROW_IDS = (
    "timeout-direct", "timeout-wrapped", "504-bridge-deadline",
    "504-without-body", "401-without-body", "502", "remote-disconnected",
    "connection-reset", "connection-reset-wrapped", "other-url-error",
    "url-error-text-mentions-refusal",
)
_CONTEXT_ROWS = [row for row in _OUTCOME_ROWS if row[0] in _CONTEXT_ROW_IDS]
assert len(_CONTEXT_ROWS) == len(_CONTEXT_ROW_IDS)


@pytest.mark.parametrize("kind", _KINDS)
@pytest.mark.parametrize(("name", "factory", "client_cls", "server_cls", "group"),
                         _CONTEXT_ROWS, ids=[row[0] for row in _CONTEXT_ROWS])
def test_unknown_outcomes_suppress_the_transport_exception_context(
    repo_root, tmp_path, monkeypatch, kind, name, factory, client_cls,
    server_cls, group
):
    module, send = _sender(kind, repo_root, tmp_path, monkeypatch)
    monkeypatch.setattr(module, "_direct_opener",
                        lambda: _Opener(_respond_with(factory)))
    expected = _expected(kind, module, client_cls if kind == "client"
                         else server_cls)

    with pytest.raises(expected) as exc_info:
        send(_SENT)

    error = exc_info.value
    assert "may not have run" in str(error)
    assert error.__cause__ is None
    assert error.__suppress_context__ is True, (
        name + ": the transport exception's context is not suppressed")
