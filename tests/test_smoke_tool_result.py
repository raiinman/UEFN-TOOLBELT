"""The registered smoke API returns structured failures without breaking the boolean API."""

import os

import pytest
import unreal

import UEFN_Toolbelt as tb


@pytest.mark.parametrize("passed,status", [(True, "ok"), (False, "error")])
def test_registered_smoke_result_preserves_pass_and_report(monkeypatch, tmp_path, passed, status):
    monkeypatch.setattr(tb, "smoke_test", lambda **_: passed)
    monkeypatch.setattr(unreal.Paths, "project_saved_dir", lambda: str(tmp_path))
    result = tb.registry.execute_strict("toolbelt_smoke_test")
    assert result["status"] == status
    assert result["passed"] is passed
    assert result["report"] == os.path.join(str(tmp_path), "UEFN_Toolbelt", "smoke_test_results.txt")
    assert "Environment health" in result["limitation"]


def test_registered_smoke_exception_is_an_explicit_failure(monkeypatch):
    def fails(**kwargs):
        raise OSError("report unavailable")

    monkeypatch.setattr(tb, "smoke_test", fails)
    result = tb.registry.execute_strict("toolbelt_smoke_test")
    assert result["status"] == "error"
    assert result["passed"] is False
    assert result["reason"] == "smoke_test_failed"
    assert result["message"] == "report unavailable"


@pytest.mark.parametrize("passed", [True, False])
def test_public_smoke_api_keeps_boolean_result(monkeypatch, passed):
    import importlib
    import importlib.util
    from types import SimpleNamespace

    # Other suites import the same-named submodule, replacing the package attribute.
    # Reload the public entry point before substituting its dynamically loaded runner.
    importlib.reload(tb)
    module = SimpleNamespace(run_smoke_test=lambda: passed)
    spec = SimpleNamespace(loader=SimpleNamespace(exec_module=lambda _: None))
    monkeypatch.setattr(importlib.util, "spec_from_file_location", lambda *_: spec)
    monkeypatch.setattr(importlib.util, "module_from_spec", lambda _: module)
    assert tb.smoke_test() is passed
