"""Failed local driver scheduling must never leave a mutation callback active."""

import ast
import importlib
from pathlib import Path
from unittest.mock import MagicMock

import pytest

DRIVER = (Path(__file__).resolve().parents[1] / "docs/audits/evidence"
          / "2026-10-09-toolbelt-acceptance/run_native_sections.py")


@pytest.mark.parametrize("unregister_fails", [False, True])
def test_initial_flush_failure_stops_and_unregisters_scheduled_callback(tmp_path, monkeypatch, unregister_fails):
    import unreal

    package = importlib.import_module("UEFN_Toolbelt")
    suite = importlib.import_module("UEFN_Toolbelt.tools.integration_test")
    original_run = MagicMock()
    monkeypatch.setattr(package, "run", original_run)
    monkeypatch.setattr(suite, "_acceptance_identity", lambda: {"mount": "acceptance-uuid"})
    monkeypatch.setattr(suite, "_SECTION_NAMES", ["materials"])
    callbacks = {}
    handle = object()

    def register(callback):
        callbacks[handle] = callback
        return handle

    def unregister(callback_handle):
        if unregister_fails:
            raise RuntimeError("unregister refused")
        del callbacks[callback_handle]

    monkeypatch.setattr(unreal, "register_slate_post_tick_callback", register)
    monkeypatch.setattr(unreal, "unregister_slate_post_tick_callback", unregister)
    original_write = Path.write_text

    def failed_flush(path, *args, **kwargs):
        if path.name == "run.json.tmp":
            raise PermissionError("initial evidence flush failed")
        return original_write(path, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", failed_flush)
    tree = ast.parse(DRIVER.read_text(encoding="utf-8"))
    for statement in tree.body:
        if isinstance(statement, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == "OUTPUT" for target in statement.targets):
            statement.value = ast.Call(func=ast.Name(id="Path", ctx=ast.Load()),
                                       args=[ast.Constant(str(tmp_path / "run"))], keywords=[])
    namespace = {"__file__": str(DRIVER)}
    with pytest.raises(PermissionError, match="initial evidence flush failed"):
        exec(compile(ast.fix_missing_locations(tree), str(DRIVER), "exec"), namespace)
    assert package.run is original_run
    assert namespace["stopped"] is True
    assert namespace["state"]["started_sections"] == []
    if not unregister_fails:
        assert callbacks == {}
        assert namespace["handle"] is None
    # Also prove a callback retained by a refused unregister cannot mutate later.
    namespace["next_tick"] = 0
    namespace["tick"](0.1)
    original_run.assert_not_called()
    assert namespace["state"]["results"] == []
