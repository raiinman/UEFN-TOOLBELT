"""
WO-005 Session A acceptance tests for scripts/coverage_report.py.
==============================================================================
Every test here is offline. Source coverage describes test code; nothing in
this file is live evidence of any tool's behaviour in the editor.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "coverage_report", REPO / "scripts" / "coverage_report.py")
assert SPEC is not None and SPEC.loader is not None
cr = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cr)

PACKAGE = cr.PACKAGE_REL
INTEGRATION = cr.CHECK_SOURCES["integration"]


# ─── Synthetic repositories ──────────────────────────────────────────────────

TOOLS = ("alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta",
         "theta", "iota", "kappa", "lambda_", "mu")

SUITE = textwrap.dedent('''
    def _test_outcome():
        try:
            r = tb.run("alpha")
            ok = r.get("count") == 3
            _record("S", "alpha outcome", ok)
        except Exception as e:
            _record("S", "alpha failed", False, str(e))

    def _test_unverified():
        r = tb.run("beta")
        _record("S", "beta unverified", r is not None, verified=False)

    def _test_literal():
        tb.run("gamma")
        _record("S", "gamma literal", True)

    def _test_membership():
        names = [t["name"] for t in tb.registry.list_tools()]
        _record("S", "delta membership", "delta" in names)

    def _test_mention():
        label = "delta"
        _record("S", "delta mention", label == "delta")

    def _test_import():
        from . import delta_module
        _record("S", "delta import", delta_module is not None)

    def _test_other_tool():
        r = run("epsilon")
        _record("S", "never calls delta", r.get("ok") == 1)

    def _test_handler():
        try:
            tb.run("zeta")
        except Exception as e:
            _record("S", "zeta handler", str(e) != "")

    def _test_failure_branch():
        r = tb.run("eta")
        if not r:
            _record("S", "eta failure", r is None)
            return
        _record("S", "eta ok", r.get("x") == 1)

    def _test_repeat():
        r = tb.run("theta")
        _record("S", "theta one", r.get("a") == 1)
        r2 = tb.run("theta")
        _record("S", "theta two", r2.get("b") == 2)

    def _test_pair():
        a = tb.run("iota")
        b = tb.run("kappa")
        _record("S", "iota and kappa", a.get("n") == 1 and b.get("n") == 1)

    def _test_invoked_unmapped():
        r = tb.run("lambda_")
        _record("S", "lambda ok", r.get("n") == 1)
''')


def _line(text, label):
    """Source line of the `_record` call carrying `label`."""
    needle = f'"{label}"'
    for number, line in enumerate(text.splitlines(), start=1):
        if "_record(" in line and needle in line:
            return number
    raise AssertionError("no record " + label)


def _entry(label, tools, category, assertion, suite=SUITE):
    return {"source": "integration", "section": "S", "label": label,
            "line": _line(suite, label), "tools": list(tools),
            "category": category, "assertion": assertion}


def _repo(tmp_path, mappings=(), registration_only=(), flags=(),
          runs=(), suite=SUITE, extra=None, block=True):
    """A synthetic repository: one registration per tool, one suite, and a
    current TOOL_STATUS.md block unless `block` is False."""
    root = tmp_path / "repo"
    tools_dir = root / PACKAGE / "tools"
    tools_dir.mkdir(parents=True)
    (tools_dir / "registered.py").write_text("".join(
        f'@register_tool(name="{name}", category="Synthetic")\n'
        f"def run_{name}():\n    return {{}}\n\n" for name in TOOLS),
        encoding="utf-8")
    (root / INTEGRATION).write_text(suite, encoding="utf-8")
    for rel, text in (extra or {}).items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    (root / "scripts").mkdir()
    (root / cr.EVIDENCE_REL).write_text(json.dumps({
        "mappings": list(mappings), "registration_only": list(registration_only),
        "flags": list(flags), "run_evidence": list(runs)}), encoding="utf-8")
    status = "# Status\n\n"
    if block:
        status += cr.render_markdown(cr.build_report(root))
    (root / cr.STATUS_REL).write_text(status, encoding="utf-8")
    return root


def _categories(root):
    return {t["name"]: (t["category"], t["reason"])
            for t in cr.build_report(root)["tools"]}


def _cli(root, *args):
    result = subprocess.run(
        [sys.executable, "-B", str(REPO / "scripts" / "coverage_report.py"),
         "--root", str(root), *args],
        capture_output=True, text=True, encoding="utf-8")
    return result.returncode, result.stdout, result.stderr


# ─── 1. The runtime registry equals the source set ───────────────────────────

def test_runtime_registry_equals_the_enumerated_source_set():
    import UEFN_Toolbelt as tb
    from UEFN_Toolbelt.registry import get_registry

    tb.register_all_tools()
    runtime = {t["name"] for t in get_registry().list_tools()}
    source = [r.name for r in cr.enumerate_registrations(REPO / PACKAGE)]
    assert runtime == set(source)
    assert len(source) == len(set(source)) == tb.__tool_count__


# ─── 2. Registrations outside tools/ are counted ─────────────────────────────

def test_a_registration_outside_tools_is_counted(tmp_path):
    root = _repo(tmp_path, extra={
        PACKAGE + "/helper.py":
            '@register_tool(name="outside", category="X")\ndef f():\n    pass\n',
        PACKAGE + "/core/deep.py":
            '@register_tool(name="deeper", category="X")\ndef g():\n    pass\n',
    })
    names = {r.name: r.file for r in cr.enumerate_registrations(root / PACKAGE)}
    assert names["outside"] == "UEFN_Toolbelt/helper.py"
    assert names["deeper"] == "UEFN_Toolbelt/core/deep.py"
    assert len(names) == len(TOOLS) + 2


# ─── 3. Registry defects fail loudly, naming the sites ───────────────────────

@pytest.mark.parametrize(("name", "extra", "needles"), (
    ("syntax-error", {PACKAGE + "/broken.py": "def (:\n"},
     ("UEFN_Toolbelt/broken.py", "cannot be parsed")),
    ("duplicate", {PACKAGE + "/again.py":
                   '@register_tool(name="alpha", category="X")\n'
                   "def again():\n    pass\n"},
     ("duplicate tool name 'alpha'", "UEFN_Toolbelt/tools/registered.py:1",
      "UEFN_Toolbelt/again.py:1")),
    ("non-constant", {PACKAGE + "/dynamic.py":
                      'N = "x"\n@register_tool(name=N, category="X")\n'
                      "def dyn():\n    pass\n"},
     ("UEFN_Toolbelt/dynamic.py:2", "not a constant string")),
), ids=("syntax-error", "duplicate", "non-constant"))
def test_a_registry_defect_exits_2_naming_the_sites(tmp_path, name, extra,
                                                    needles):
    root = _repo(tmp_path, block=False)
    for rel, text in extra.items():
        (root / rel).write_text(text, encoding="utf-8")
    with pytest.raises(cr.RegistryDefect):
        cr.enumerate_registrations(root / PACKAGE)
    for mode in ((), ("--check",), ("--json",), ("--markdown",)):
        code, _out, err = _cli(root, *mode)
        assert code == 2, (mode, err)
        for needle in needles:
            assert needle in err, (needle, err)


# ─── 4. Positive controls ────────────────────────────────────────────────────

def test_mapped_checks_that_invoke_their_tool_are_promoted(tmp_path):
    root = _repo(tmp_path, mappings=[
        _entry("alpha outcome", ["alpha"], cr.OUTCOME,
               'ok = r.get("count") == 3'),
        _entry("beta unverified", ["beta"], cr.EXECUTION, "r is not None"),
        _entry("gamma literal", ["gamma"], cr.EXECUTION, "True"),
        _entry("eta ok", ["eta"], cr.OUTCOME, 'r.get("x") == 1'),
    ])
    report = cr.build_report(root)
    assert report["errors"] == []
    found = _categories(root)
    assert found["alpha"] == (cr.OUTCOME, "")
    assert found["beta"] == (cr.EXECUTION, "")
    assert found["gamma"] == (cr.EXECUTION, "")
    assert found["eta"] == (cr.OUTCOME, "")
    # Two tools promoted by separate checks count as two.
    assert report["source_coverage"]["counts"][cr.OUTCOME] == 2
    assert report["source_coverage"]["counts"][cr.EXECUTION] == 2
    assert _cli(root, "--check")[0] == 0


# ─── 5. Rejections, for both promoted categories ─────────────────────────────

@pytest.mark.parametrize(("label", "tool", "assertion"), (
    ("delta membership", "delta", '"delta" in names'),
    ("delta mention", "delta", 'label == "delta"'),
    ("delta import", "delta", "delta_module is not None"),
    ("never calls delta", "delta", 'r.get("ok") == 1'),
), ids=("registry-membership", "string-mention", "import", "never-calls"))
@pytest.mark.parametrize("category", (cr.OUTCOME, cr.EXECUTION))
def test_a_check_that_does_not_invoke_the_tool_promotes_nothing(
        tmp_path, label, tool, assertion, category):
    root = _repo(tmp_path, mappings=[_entry(label, [tool], category,
                                            assertion)])
    report = cr.build_report(root)
    assert _categories(root)[tool][0] == cr.REGISTRATION_ONLY
    assert any("rule 2" in e for e in report["errors"]), report["errors"]
    assert _cli(root, "--check")[0] == 1


@pytest.mark.parametrize(("label", "tool", "assertion", "why"), (
    ("gamma literal", "gamma", "True", "literal"),
    ("beta unverified", "beta", "r is not None", "verified=False"),
    ("eta failure", "eta", "r is None", "failure branch"),
    ("zeta handler", "zeta", 'str(e) != ""', "exception handler"),
), ids=("literal-true", "verified-false", "failure-branch", "handler"))
def test_an_unqualified_check_does_not_produce_defined_outcome(
        tmp_path, label, tool, assertion, why):
    root = _repo(tmp_path, mappings=[_entry(label, [tool], cr.OUTCOME,
                                            assertion)])
    report = cr.build_report(root)
    assert _categories(root)[tool][0] != cr.OUTCOME
    assert any(why in e and "rule 3" in e for e in report["errors"]), (
        report["errors"])
    assert _cli(root, "--check")[0] == 1


@pytest.mark.parametrize(("entry", "needle"), (
    ({"label": "alpha outcome", "line": 999}, "missing check"),
    ({"tools": ["nope"]}, "missing tool"),
    ({"assertion": "this text is not in the function"}, "assertion"),
    ({"category": "verified-live"}, "claims category"),
), ids=("missing-check", "missing-tool", "foreign-assertion", "bad-category"))
def test_an_invalid_mapping_exits_1(tmp_path, entry, needle):
    base = _entry("alpha outcome", ["alpha"], cr.OUTCOME,
                  'ok = r.get("count") == 3')
    base.update(entry)
    root = _repo(tmp_path, mappings=[base])
    code, _out, err = _cli(root, "--check")
    assert code == 1 and needle in err, err
    assert _categories(root)["alpha"][0] == cr.REGISTRATION_ONLY


# ─── 6. Unique tools; no promotion beyond the entry ──────────────────────────

def test_repeated_checks_count_once_and_promote_only_listed_tools(tmp_path):
    root = _repo(tmp_path, mappings=[
        _entry("theta one", ["theta"], cr.OUTCOME, 'r.get("a") == 1'),
        _entry("theta two", ["theta"], cr.OUTCOME, 'r2.get("b") == 2'),
        _entry("iota and kappa", ["iota"], cr.OUTCOME,
               'a.get("n") == 1 and b.get("n") == 1'),
    ])
    report = cr.build_report(root)
    assert report["errors"] == []
    tools = {t["name"]: t for t in report["tools"]}
    assert tools["theta"]["category"] == cr.OUTCOME
    assert len(tools["theta"]["checks"]) == 2
    assert tools["iota"]["category"] == cr.OUTCOME
    assert tools["kappa"]["category"] == cr.REGISTRATION_ONLY
    assert report["source_coverage"]["counts"][cr.OUTCOME] == 2


# ─── 7. Availability flags ───────────────────────────────────────────────────

FLAGGED = ("lod_auto_generate_selection", "lod_auto_generate_folder",
           "memory_autofix_lods")


def test_the_three_stubbed_tools_carry_their_flag_everywhere():
    report = cr.build_report(REPO)
    tools = {t["name"]: t for t in report["tools"]}
    flags = {f["tool"]: f for f in report["flags"]}
    assert set(flags) == set(FLAGGED)
    summary = cr.render_summary(report, listing=True)
    markdown = cr.render_markdown(report)
    as_json = json.loads(json.dumps(report))
    for name in FLAGGED:
        flag = flags[name]
        assert tools[name]["flag"] == "stubbed-operation"
        assert flag["reason"] and flag["sources"] and flag["enforcement"]
        assert "set_lods_with_notification" in flag["enforcement"]
        assert "registry-level" in flag["enforcement"]
        for output in (summary, markdown):
            assert name in output and flag["reason"] in output
            assert flag["enforcement"] in output
            assert all(source in output for source in flag["sources"])
        assert any(f["tool"] == name for f in as_json["flags"])
    # A mapping that names a flagged tool keeps the flag: the wrapper is
    # mapped, and still flagged.
    assert tools["memory_autofix_lods"]["checks"]
    assert tools["memory_autofix_lods"]["flag"] == "stubbed-operation"


def test_a_flag_keeps_the_tool_and_its_source_category(tmp_path):
    flag = {"tool": "alpha", "flag": "stubbed-operation", "reason": "r",
            "sources": ["s"], "enforcement": "e"}
    mapped = [_entry("alpha outcome", ["alpha"], cr.OUTCOME,
                     'ok = r.get("count") == 3')]
    with_flag = _categories(_repo(tmp_path / "a", mappings=mapped,
                                  flags=[flag]))
    without = _categories(_repo(tmp_path / "b", mappings=mapped))
    assert with_flag == without
    assert with_flag["alpha"] == (cr.OUTCOME, "")


# ─── 8. Unmapped and other registration-only reasons ─────────────────────────

def test_registration_only_tools_carry_their_reason(tmp_path):
    root = _repo(tmp_path, registration_only=[
        {"tool": "epsilon", "reason": "ambiguous", "note": "n"}])
    found = _categories(root)
    assert found["lambda_"] == (cr.REGISTRATION_ONLY, "unmapped")
    assert found["mu"] == (cr.REGISTRATION_ONLY, "no-check")
    assert found["epsilon"] == (cr.REGISTRATION_ONLY, "ambiguous")
    listing = _cli(root, "--list")[1]
    assert "lambda_  registration-only (unmapped)" in listing


# ─── 9. Run evidence stays separate from source coverage ─────────────────────

def test_run_evidence_matches_the_mandate_and_promotes_nothing(tmp_path):
    evidence = json.loads((REPO / cr.EVIDENCE_REL).read_text(encoding="utf-8"))
    runs = {r["scope"]: r for r in evidence["run_evidence"]}
    assert set(runs) == {"integration", "other"}
    integration = runs["integration"]
    assert integration["date"] == "2026-08-23"
    assert "112671c" in integration["build"]
    assert "190/190" in integration["result"]
    assert "163" in integration["result"] and "27" in integration["result"]
    assert "not preserved" in integration["limitation"]
    assert "never converted into per-tool" in integration["limitation"]
    other = runs["other"]
    assert other["build"] == "++Fortnite+Release-42.20-CL-58011042"
    assert other["date"] == "2026-09-28"
    assert other["source"] == (
        "docs/audits/2026-09-28-wo004-session-c-live-acceptance.md")
    assert "One machine and one boot" in other["limitation"]
    assert "never promoted" in other["limitation"]
    report = cr.build_report(REPO)
    assert report["run_scopes_without_records"] == ["smoke"]
    # No source fact is run evidence.
    for run in evidence["run_evidence"]:
        assert run["source"] not in cr.CHECK_SOURCES.values()
        assert not any(c in json.dumps(run) for c in cr.CATEGORIES)
    # The run records contribute to no source category: removing them
    # changes no tool's category.
    root = tmp_path / "copy"
    for rel in (PACKAGE,):
        _copy_tree(REPO / rel, root / rel)
    (root / "scripts").mkdir()
    stripped = dict(evidence, run_evidence=[])
    (root / cr.EVIDENCE_REL).write_text(json.dumps(stripped), encoding="utf-8")
    before = {t["name"]: t["category"] for t in report["tools"]}
    after = {t["name"]: t["category"]
             for t in cr.build_report(root)["tools"]}
    assert before == after


def _copy_tree(src, dst):
    for path in src.rglob("*.py"):
        target = dst / path.relative_to(src)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())


# ─── 10. The generated block, and the report's inputs ────────────────────────

def test_the_tool_status_block_equals_the_markdown_output():
    report = cr.build_report(REPO)
    text = (REPO / cr.STATUS_REL).read_text(encoding="utf-8")
    assert cr.current_block(text) == cr.render_markdown(report)
    assert cr.block_is_current(REPO, report)
    code, out, err = _cli(REPO, "--markdown")
    assert code == 0, err
    assert out.replace("\r\n", "\n") == cr.render_markdown(report)
    assert _cli(REPO, "--check") == (0, "", "")


def test_a_stale_block_exits_1(tmp_path):
    root = _repo(tmp_path, block=False)
    code, _out, err = _cli(root, "--check")
    assert code == 1 and "stale" in err
    status = root / cr.STATUS_REL
    status.write_text(cr.render_markdown(cr.build_report(root))
                      .replace("| 12 |", "| 13 |"), encoding="utf-8")
    assert _cli(root, "--check")[0] == 1


def test_the_stale_smoke_copy_is_not_an_input(tmp_path):
    assert "tests/smoke_test.py" not in cr.INPUTS
    assert all("tests/" not in rel for rel in cr.CHECK_SOURCES.values())
    clean = _categories(_repo(tmp_path / "a"))
    noisy = _categories(_repo(tmp_path / "b", extra={
        "tests/smoke_test.py": 'tb.run("mu")\n_record("S", "mu", True)\n'}))
    assert clean == noisy


def test_the_block_states_counts_as_labelled_values():
    markdown = cr.render_markdown(cr.build_report(REPO))
    import re
    assert not re.search(r"\b\d{2,4}\s+(?:[A-Za-z][\w-]*\s+){0,2}tools?\b",
                         markdown)
    assert not re.search(r"\b\d+\s+categories\b", markdown)


# ─── 11. The migration shim ──────────────────────────────────────────────────

SHIM = REPO / PACKAGE / "list_untested.py"


def test_the_shim_exits_3_and_names_the_replacement(tmp_path):
    copy = tmp_path / "elsewhere" / "list_untested.py"
    copy.parent.mkdir()
    copy.write_bytes(SHIM.read_bytes())
    result = subprocess.run([sys.executable, "-B", str(copy)],
                            capture_output=True, text=True, cwd=tmp_path)
    assert result.returncode == 3
    assert "py -3 scripts/coverage_report.py" in result.stdout
    assert "reports no coverage" in result.stdout
    assert "3" in ast.get_docstring(ast.parse(SHIM.read_text("utf-8")))


def test_the_shim_opens_no_file_and_imports_nothing_from_scripts():
    tree = ast.parse(SHIM.read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {alias.name for alias in node.names}
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")
    assert imported == {"sys"}
    called = {getattr(node.func, "id", getattr(node.func, "attr", ""))
              for node in ast.walk(tree) if isinstance(node, ast.Call)}
    assert not called & {"open", "read_text", "read_bytes", "listdir",
                         "walk", "rglob", "glob", "Path", "exec_module"}
    assert "register_tool" not in SHIM.read_text(encoding="utf-8")


# ─── drift_check delegates to the same enumerator ────────────────────────────

def _drift_check(root):
    spec = importlib.util.spec_from_file_location(
        "drift_for_coverage", REPO / "scripts" / "drift_check.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = str(root)
    return module


def test_drift_check_reads_the_same_registry(tmp_path):
    dc = _drift_check(REPO)
    expected = {r.name: r.category
                for r in cr.enumerate_registrations(REPO / PACKAGE)}
    assert dc._registered_tools() == expected
    root = _repo(tmp_path, block=False)
    (root / PACKAGE / "broken.py").write_text("def (:\n", encoding="utf-8")
    dc.ROOT = str(root)
    with pytest.raises(Exception) as caught:
        dc._registered_tools()
    assert "UEFN_Toolbelt/broken.py" in str(caught.value)
    dc.ROOT = str(tmp_path / "no-package-here")
    assert dc._registered_tools() == {}


# ─── The CLI modes ───────────────────────────────────────────────────────────

def test_the_cli_modes_report_the_same_data():
    code, out, err = _cli(REPO)
    assert code == 0, err
    for needle in ("Registered: 362", "Source coverage", "Availability flags",
                   "Run evidence", "[smoke] no preserved run record"):
        assert needle in out
    code, out, _err = _cli(REPO, "--json")
    data = json.loads(out)
    assert code == 0 and data["registry"]["total"] == len(data["tools"])
    assert sum(data["source_coverage"]["counts"].values()) == len(data["tools"])
    code, out, _err = _cli(REPO, "--list")
    assert code == 0
    assert sum(1 for line in out.splitlines()
               if line.startswith("    ") and "  " in line.strip()) >= 362
