"""Acceptance controls and evidence are testable without simulating native outcomes."""

import importlib
import json
from contextlib import nullcontext
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def suite(monkeypatch, tmp_path):
    module = importlib.import_module("UEFN_Toolbelt.tools.integration_test")
    monkeypatch.setattr(module, "_SAVED", str(tmp_path))
    monkeypatch.setattr(module, "_RESULTS_PATH", str(tmp_path / "results.txt"))
    monkeypatch.setattr(module, "_RESULTS_JSON_PATH", str(tmp_path / "results.json"))
    monkeypatch.setattr(module, "_results", [])
    monkeypatch.setattr(module, "_selected_sections", [])
    monkeypatch.setattr(module, "_integration_running", False)
    project = tmp_path / "ToolbeltAcceptance"
    deployed = project / "Content/Python/UEFN_Toolbelt/tools/integration_test.py"
    deployed.parent.mkdir(parents=True)
    deployed.write_bytes(Path(module.__file__).read_bytes())
    (project / "ToolbeltAcceptance.uefnproject").write_text(json.dumps({
        "plugins": [{"name": "acceptance-uuid", "bIsRoot": True}]}), encoding="utf-8")
    monkeypatch.setattr(module, "__file__", str(deployed))
    monkeypatch.setattr(module.unreal.Paths, "project_dir", lambda: "/Fortnite/FortniteGame/")
    world = SimpleNamespace(get_path_name=lambda: "/acceptance-uuid/Acceptance.Acceptance")
    editor = SimpleNamespace(get_editor_world=lambda: world)
    monkeypatch.setattr(module.unreal, "get_editor_subsystem", lambda _: editor)
    monkeypatch.setattr(module, "undo_transaction", lambda _: nullcontext())
    monkeypatch.setattr(module, "_cleanup_fixtures", MagicMock())
    return module


@pytest.mark.parametrize("project,allow", [("Riftbloom", True), ("ToolbeltAcceptance", False)])
def test_guard_prevents_mutation(suite, monkeypatch, project, allow):
    if project == "Riftbloom":
        monkeypatch.setattr(suite, "__file__", suite.__file__.replace("ToolbeltAcceptance", "Riftbloom"))
    section = MagicMock()
    monkeypatch.setattr(suite, "_test_materials", section)
    result = suite.toolbelt_integration_test(sections=["materials"], allow_mutation=allow)
    assert result["reason"] == "disposable_project_required"
    section.assert_not_called()
    suite._cleanup_fixtures.assert_not_called()


@pytest.mark.parametrize("sections", [[], "materials", ["no_such_section"], ["materials", "materials"], [1]])
def test_invalid_sections_refuse_before_mutation(suite, sections):
    result = suite.toolbelt_integration_test(sections=sections, allow_mutation=True)
    assert result["reason"] == "invalid_sections"
    suite._cleanup_fixtures.assert_not_called()


def test_selected_section_keeps_outcomes_and_execution_separate(suite, monkeypatch):
    def checks():
        suite._record("Fixture", "Actual readback", True, "x=100", verified=True)
        suite._record("Fixture", "Execution only", True, verified=False)
        partial = json.loads(Path(suite._RESULTS_JSON_PATH).read_text(encoding="utf-8"))
        assert partial["completed"] is False
        assert partial["checks"][1]["verified"] is False

    monkeypatch.setattr(suite, "_test_materials", checks)
    other = MagicMock()
    monkeypatch.setattr(suite, "_test_bulk_ops", other)
    result = suite.toolbelt_integration_test(sections=["materials"], allow_mutation=True)
    assert result["status"] == "ok"
    assert result["total"] == 2 and result["verified"] == 1 and result["execution_only"] == 1
    other.assert_not_called()
    final = json.loads(Path(result["json_report"]).read_text(encoding="utf-8"))
    assert final["completed"] is True
    assert final["checks"] == result["checks"]
    assert len(final["harness_sha256"]) == 64


def test_fatal_section_preserves_partial_checks_and_cleanup_error(suite, monkeypatch):
    def fails():
        suite._record("Fixture", "Readback failed", False, "expected x=100")
        raise RuntimeError("native operation failed")

    monkeypatch.setattr(suite, "_test_materials", fails)
    suite._cleanup_fixtures.side_effect = RuntimeError("cleanup failed")
    result = suite.toolbelt_integration_test(sections=["materials"], allow_mutation=True)
    assert result["reason"] == "fatal" and result["completed"] is False
    assert result["checks"][0]["passed"] is False
    partial = json.loads(Path(result["json_report"]).read_text(encoding="utf-8"))
    assert partial["fatal"] == "native operation failed"
    assert partial["cleanup_error"] == "cleanup failed"


def test_bridge_section_default_preserves_listener(suite, monkeypatch):
    package = importlib.import_module("UEFN_Toolbelt")
    run = MagicMock(return_value={"status": "ok", "running": True})
    monkeypatch.setattr(package, "run", run)
    result = suite.toolbelt_integration_test(sections=["bridge_safe"], allow_mutation=True)
    assert result["status"] == "ok"
    run.assert_called_once_with("mcp_status")
    assert result["checks"][0]["verified"] is False


def test_empty_section_is_not_a_positive_acceptance_result(suite, monkeypatch):
    monkeypatch.setattr(suite, "_test_materials", lambda: None)
    result = suite.toolbelt_integration_test(sections=["materials"], allow_mutation=True)
    assert result["status"] == "error" and result["total"] == 0


@pytest.mark.parametrize("bad_identity", ["world", "ambiguous", "missing_root", "invalid_mount"])
def test_native_identity_mismatch_refuses_before_mutation(suite, monkeypatch, bad_identity):
    project = Path(suite.__file__).parents[4]
    descriptor = project / "ToolbeltAcceptance.uefnproject"
    if bad_identity == "world":
        world = SimpleNamespace(get_path_name=lambda: "/riftbloom-uuid/Riftbloom.Riftbloom")
        monkeypatch.setattr(suite.unreal, "get_editor_subsystem",
                            lambda _: SimpleNamespace(get_editor_world=lambda: world))
    elif bad_identity == "ambiguous":
        (project / "Other.uefnproject").write_text("{}", encoding="utf-8")
    elif bad_identity == "missing_root":
        descriptor.write_text("{}", encoding="utf-8")
    else:
        descriptor.write_text(json.dumps({"plugins": [{"name": "Game", "bIsRoot": True}]}), encoding="utf-8")
    section = MagicMock()
    monkeypatch.setattr(suite, "_test_materials", section)
    result = suite.toolbelt_integration_test(sections=["materials"], allow_mutation=True)
    assert result["reason"] == "disposable_project_required"
    section.assert_not_called()


def test_evidence_separates_native_identity_from_engine_paths(suite, monkeypatch):
    monkeypatch.setattr(suite, "_test_materials", lambda: suite._record("Fixture", "Readback", True))
    result = suite.toolbelt_integration_test(sections=["materials"], allow_mutation=True)
    evidence = json.loads(Path(result["json_report"]).read_text(encoding="utf-8"))
    assert evidence["project"]["mount"] == "acceptance-uuid"
    assert evidence["project"]["project_dir"].endswith("ToolbeltAcceptance")
    assert evidence["project"]["descriptor"].endswith(".uefnproject")
    assert evidence["project"]["world_path"].startswith("/acceptance-uuid/")
    assert evidence["engine_saved_dir"] != evidence["project"]["project_dir"]



def test_initial_evidence_failure_refuses_before_mutation(suite, monkeypatch):
    def fail_write(**kwargs):
        raise PermissionError("report unavailable")

    monkeypatch.setattr(suite, "_write_json_report", fail_write)
    section = MagicMock()
    monkeypatch.setattr(suite, "_test_materials", section)
    result = suite.toolbelt_integration_test(sections=["materials"], allow_mutation=True)
    assert result["reason"] == "evidence_unavailable"
    assert result["completed"] is False
    section.assert_not_called()
    suite._cleanup_fixtures.assert_not_called()


def test_final_evidence_failure_is_structured(suite, monkeypatch):
    original = suite._write_json_report
    calls = 0

    def fail_after_initial(**kwargs):
        nonlocal calls
        calls += 1
        if calls > 1:
            raise PermissionError("report became unavailable")
        original(**kwargs)

    monkeypatch.setattr(suite, "_write_json_report", fail_after_initial)
    monkeypatch.setattr(suite, "_test_materials", lambda: suite._record("Fixture", "Readback", True))
    result = suite.toolbelt_integration_test(sections=["materials"], allow_mutation=True)
    assert result["status"] == "error" and result["completed"] is False
    assert result["evidence_error"] == "report became unavailable"



@pytest.mark.parametrize("destroy_result", [True, False])
def test_cleanup_preserves_survivors_even_when_destroy_claims_success(monkeypatch, destroy_result):
    module = importlib.import_module("UEFN_Toolbelt.tools.integration_test")
    actor = object()
    subsystem = SimpleNamespace(get_all_level_actors=lambda: [actor],
                                destroy_actor=lambda _: destroy_result)
    monkeypatch.setattr(module.unreal, "get_editor_subsystem", lambda _: subsystem)
    monkeypatch.setattr(module, "_spawn_fixtures", [actor])
    with pytest.raises(RuntimeError, match="Cleanup left 1 tracked fixtures"):
        module._cleanup_fixtures()
    assert module._spawn_fixtures == [actor]


def test_cleanup_requires_absence_readback_before_forgetting_fixture(monkeypatch):
    module = importlib.import_module("UEFN_Toolbelt.tools.integration_test")
    actor = object()
    live = [actor]

    def destroy(target):
        live.remove(target)
        return True

    subsystem = SimpleNamespace(get_all_level_actors=lambda: list(live), destroy_actor=destroy)
    monkeypatch.setattr(module.unreal, "get_editor_subsystem", lambda _: subsystem)
    monkeypatch.setattr(module, "_spawn_fixtures", [actor])
    module._cleanup_fixtures()
    assert module._spawn_fixtures == []
    assert live == []


def test_cleanup_readback_failure_keeps_tracking(monkeypatch):
    module = importlib.import_module("UEFN_Toolbelt.tools.integration_test")
    actor = object()
    reads = 0

    def read():
        nonlocal reads
        reads += 1
        if reads > 1:
            raise RuntimeError("actor readback unavailable")
        return [actor]

    subsystem = SimpleNamespace(get_all_level_actors=read, destroy_actor=lambda _: True)
    monkeypatch.setattr(module.unreal, "get_editor_subsystem", lambda _: subsystem)
    monkeypatch.setattr(module, "_spawn_fixtures", [actor])
    with pytest.raises(RuntimeError, match="readback unavailable"):
        module._cleanup_fixtures()
    assert module._spawn_fixtures == [actor]


def test_nested_invocation_preserves_outer_results_fixtures_and_identity(suite, monkeypatch):
    nested_results = []
    fixture = object()
    monkeypatch.setattr(suite, "_spawn_fixtures", [fixture])

    def section():
        suite._record("Fixture", "Before event pumping", True)
        outer_results = suite._results
        outer_context = suite._project_context
        outer_started = suite._start_time
        outer_sections = suite._selected_sections
        nested = suite.toolbelt_integration_test(sections=["bridge_safe"], allow_mutation=True)
        nested_results.append(nested)
        assert nested["status"] == "error"
        assert nested["reason"] == "integration_already_running"
        assert nested["completed"] is False
        assert suite._results is outer_results
        assert suite._project_context is outer_context
        assert suite._start_time == outer_started
        assert suite._selected_sections is outer_sections
        assert suite._spawn_fixtures == [fixture]
        suite._record("Fixture", "After event pumping", True)

    monkeypatch.setattr(suite, "_test_materials", section)
    result = suite.toolbelt_integration_test(sections=["materials"], allow_mutation=True)
    assert result["status"] == "ok"
    assert result["total"] == 2
    assert len(nested_results) == 1
    assert suite._integration_running is False
    suite._cleanup_fixtures.assert_called_once()


def test_guard_releases_on_uncaught_exception_and_allows_next_run(suite, monkeypatch):
    def failed_validation(sections):
        raise RuntimeError("validation unexpectedly failed")

    original = suite._validate_sections
    monkeypatch.setattr(suite, "_validate_sections", failed_validation)
    with pytest.raises(RuntimeError, match="validation unexpectedly failed"):
        suite.toolbelt_integration_test(sections=["materials"], allow_mutation=True)
    assert suite._integration_running is False
    monkeypatch.setattr(suite, "_validate_sections", original)
    monkeypatch.setattr(suite, "_test_materials", lambda: suite._record("Fixture", "Readback", True))
    result = suite.toolbelt_integration_test(sections=["materials"], allow_mutation=True)
    assert result["status"] == "ok"
    assert suite._integration_running is False



@pytest.mark.parametrize("expected", [True, False])
def test_lock_operator_status_ok_with_zero_changed_and_failed_actor_never_passes(suite, expected):
    actor = SimpleNamespace(get_editor_property=lambda _: expected)
    field = "locked" if expected else "unlocked"
    passed, detail, verified = suite._lock_check(actor, {"status": "ok", field: 0, "failed": 1}, expected)
    assert passed is False
    assert verified is True
    assert "failed" in detail


@pytest.mark.parametrize("count,unchanged", [(1, 0), (0, 1)])
@pytest.mark.parametrize("expected", [True, False])
def test_lock_requires_actual_desired_readback_for_change_or_noop(suite, expected, count, unchanged):
    actor = SimpleNamespace(get_editor_property=lambda _: expected)
    field = "locked" if expected else "unlocked"
    result = {"status": "ok", field: count, "unchanged": unchanged, "failed": 0}
    assert suite._lock_check(actor, result, expected)[0] is True
    refused = SimpleNamespace(get_editor_property=lambda _: not expected)
    assert suite._lock_check(refused, result, expected)[0] is False


def test_unavailable_lock_is_explicit_failed_operator_boundary(suite):
    def unavailable(_):
        raise AttributeError("lock unavailable")

    actor = SimpleNamespace(get_editor_property=unavailable)
    result = {"status": "error", "reason": "actor_lock_unavailable", "locked": 0, "failed": 1}
    passed, detail, verified = suite._lock_check(actor, result, True)
    assert passed is False and verified is False
    assert "operator not accepted" in detail


def test_sky_missing_fixture_error_is_not_accepted_as_success(suite, monkeypatch):
    package = importlib.import_module("UEFN_Toolbelt")
    subsystem = SimpleNamespace(get_all_level_actors=list)
    monkeypatch.setattr(suite.unreal, "get_editor_subsystem", lambda _: subsystem)
    monkeypatch.setattr(package, "run", lambda tool, **_: (
        {"status": "error", "message": "No DirectionalLight in level."}
        if tool == "sky_set_time" else {"status": "ok"}))
    suite._test_lighting_extended()
    sky = next(check for check in suite._results if check["name"] == "sky_set_time")
    assert sky["passed"] is False
    assert sky["verified"] is False
    assert "No DirectionalLight" in sky["detail"]
