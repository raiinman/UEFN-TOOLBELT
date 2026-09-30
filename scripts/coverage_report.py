"""
Registry-derived coverage report (WO-005 Session A).
==============================================================================
Three separate things are reported and never merged:

  * the registry - every @register_tool site in the package, found offline;
  * source coverage - what the repository's test code is written to check,
    derived only from explicit entries in scripts/coverage_evidence.json;
  * run evidence - what was observed in recorded runs, taken only from the
    records in that same file.

Source coverage describes test code, never a run. A tool reaches a category
above `registration-only` only through a mapping entry that names it, and only
if the mapped check obeys the promotion rules checked here. Anything else stays
`registration-only` with its reason. Low coverage is never an error.

    py -3 scripts/coverage_report.py              summary
    py -3 scripts/coverage_report.py --list       summary plus one line per tool
    py -3 scripts/coverage_report.py --json       the same data, machine-readable
    py -3 scripts/coverage_report.py --markdown   the TOOL_STATUS.md block
    py -3 scripts/coverage_report.py --check      validate without the report

Exit codes: 0 consistent; 1 a mapping names a missing check or tool, breaks a
promotion rule, or the TOOL_STATUS.md block is stale; 2 a registry defect (an
unparseable file, a duplicate name, or a non-constant name).

drift_check._registered_tools() delegates to enumerate_registrations(), so the
drift gate and this report read the same registry.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Any, NamedTuple

PACKAGE_REL = "Content/Python/UEFN_Toolbelt"
EVIDENCE_REL = "scripts/coverage_evidence.json"
STATUS_REL = "TOOL_STATUS.md"
# The check sources, read as source text only. tests/smoke_test.py is a stale
# copy and is deliberately not among them.
CHECK_SOURCES = {
    "integration": PACKAGE_REL + "/tools/integration_test.py",
    "smoke": PACKAGE_REL + "/smoke_test.py",
}
INPUTS = (PACKAGE_REL, EVIDENCE_REL, STATUS_REL, *CHECK_SOURCES.values())

BLOCK_BEGIN = "<!-- coverage:begin -->"
BLOCK_END = "<!-- coverage:end -->"

OUTCOME = "defined-outcome"
EXECUTION = "defined-execution"
REGISTRATION_ONLY = "registration-only"
CATEGORIES = (OUTCOME, EXECUTION, REGISTRATION_ONLY)
REASONS = ("unmapped", "ambiguous", "no-check")
RUN_SCOPES = ("integration", "smoke", "other")


class RegistryDefect(Exception):
    """The registry cannot be enumerated honestly. Every site is named."""

    def __init__(self, problems: list[str]) -> None:
        super().__init__("; ".join(problems))
        self.problems = problems


class Registration(NamedTuple):
    name: str
    category: str
    file: str
    line: int


class Check(NamedTuple):
    source: str
    section: str
    label: str
    line: int
    function: str
    invoked: frozenset[str]
    passed_literal: bool
    verified_false: bool
    in_handler: bool
    in_failure_branch: bool
    function_text: str

    @property
    def check_id(self) -> str:
        return f"{self.source}:{self.section}:{self.label}:{self.line}"


# ─── Registry ────────────────────────────────────────────────────────────────

def _is_register_call(node: ast.expr) -> bool:
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    return ((isinstance(func, ast.Name) and func.id == "register_tool")
            or (isinstance(func, ast.Attribute) and func.attr == "register_tool"))


def enumerate_registrations(package_root: Path) -> list[Registration]:
    """Every @register_tool site under `package_root`, in file order.

    A missing package is empty. A file that fails to parse, a duplicate name,
    or a non-constant name raises RegistryDefect naming each site involved,
    never a silent skip or overwrite.
    """
    package_root = Path(package_root)
    if not package_root.is_dir():
        return []
    problems: list[str] = []
    sites: list[Registration] = []
    for path in sorted(package_root.rglob("*.py")):
        rel = path.relative_to(package_root.parent).as_posix()
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError, ValueError) as exc:
            problems.append(f"{rel}: cannot be parsed ({exc})")
            continue
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for dec in node.decorator_list:
                if not _is_register_call(dec):
                    continue
                assert isinstance(dec, ast.Call)
                keywords = {k.arg: k.value for k in dec.keywords}
                name = keywords.get("name")
                if not (isinstance(name, ast.Constant)
                        and isinstance(name.value, str)):
                    problems.append(
                        f"{rel}:{dec.lineno}: register_tool name is not a "
                        "constant string")
                    continue
                cat = keywords.get("category")
                category = (cat.value if isinstance(cat, ast.Constant)
                            and isinstance(cat.value, str) else "?")
                sites.append(Registration(name.value, category, rel,
                                          dec.lineno))
    by_name: dict[str, list[Registration]] = {}
    for site in sites:
        by_name.setdefault(site.name, []).append(site)
    for tool_name, group in sorted(by_name.items()):
        if len(group) > 1:
            where = ", ".join(f"{s.file}:{s.line}" for s in group)
            problems.append(f"duplicate tool name {tool_name!r} at {where}")
    if problems:
        raise RegistryDefect(problems)
    return sites


# ─── Checks, read as source text ─────────────────────────────────────────────

def _is_run_call(node: ast.AST) -> str | None:
    """The tool name of a `run("x")` or `tb.run("x")` call, else None."""
    if not (isinstance(node, ast.Call) and node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)):
        return None
    func = node.func
    if isinstance(func, ast.Name) and func.id == "run":
        return node.args[0].value
    if (isinstance(func, ast.Attribute) and func.attr == "run"
            and isinstance(func.value, ast.Name) and func.value.id == "tb"):
        return node.args[0].value
    return None


def _ends_in_return(block: list[ast.stmt]) -> bool:
    return bool(block) and isinstance(block[-1], ast.Return)


def collect_checks(source: str, path: Path) -> list[Check]:
    """Every `_record(section, label, passed, ...)` call in one source file.

    A failure branch is an `if` block that records and then returns early.
    Records with a non-constant section or label cannot be referenced by a
    mapping and are skipped.
    """
    path = Path(path)
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    lines = text.splitlines()
    parents: dict[ast.AST, ast.AST] = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node
    checks: list[Check] = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "_record"):
            continue
        args = node.args
        if len(args) < 2 or not all(
                isinstance(a, ast.Constant) and isinstance(a.value, str)
                for a in args[:2]):
            continue
        passed = (args[2] if len(args) > 2 else
                  next((k.value for k in node.keywords if k.arg == "passed"),
                       None))
        verified = next((k.value for k in node.keywords
                         if k.arg == "verified"), None)
        in_handler = in_failure_branch = False
        function: ast.FunctionDef | ast.AsyncFunctionDef | None = None
        current: ast.AST = node
        while current in parents:
            parent = parents[current]
            if isinstance(parent, ast.ExceptHandler):
                in_handler = True
            if isinstance(parent, ast.If):
                branch = (parent.body if current in parent.body
                          else parent.orelse if current in parent.orelse
                          else [])
                if _ends_in_return(branch):
                    in_failure_branch = True
            if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef)):
                function = parent
                break
            current = parent
        invoked: set[str] = set()
        function_text = ""
        if function is not None:
            invoked = {name for sub in ast.walk(function)
                       if (name := _is_run_call(sub)) is not None}
            end = function.end_lineno or function.lineno
            function_text = "\n".join(lines[function.lineno - 1:end])
        section, label = args[0], args[1]
        assert isinstance(section, ast.Constant)
        assert isinstance(label, ast.Constant)
        checks.append(Check(
            source=source, section=str(section.value), label=str(label.value),
            line=node.lineno,
            function=function.name if function is not None else "",
            invoked=frozenset(invoked),
            passed_literal=passed is None or isinstance(passed, ast.Constant),
            verified_false=(isinstance(verified, ast.Constant)
                            and verified.value is False),
            in_handler=in_handler, in_failure_branch=in_failure_branch,
            function_text=function_text,
        ))
    return sorted(checks, key=lambda c: c.line)


# ─── Evidence and classification ─────────────────────────────────────────────

def _normalized(text: str) -> str:
    return " ".join(text.split())


def _entry_problems(entry: dict[str, Any], checks: dict[tuple, Check],
                    names: set[str]) -> tuple[list[str], Check | None]:
    """Why one mapping entry cannot promote, or [] when it may."""
    problems: list[str] = []
    key = (entry.get("source"), entry.get("section"), entry.get("label"),
           entry.get("line"))
    where = ":".join(str(part) for part in key)
    check = checks.get(key)
    if check is None:
        problems.append(f"mapping {where}: names a missing check")
    tools = entry.get("tools")
    if not isinstance(tools, list) or not tools:
        problems.append(f"mapping {where}: lists no tools")
        tools = []
    for tool in tools:
        if tool not in names:
            problems.append(f"mapping {where}: names a missing tool {tool!r}")
    category = entry.get("category")
    if category not in (OUTCOME, EXECUTION):
        problems.append(f"mapping {where}: claims category {category!r}")
    assertion = entry.get("assertion")
    if not isinstance(assertion, str) or not assertion.strip():
        problems.append(f"mapping {where}: names no assertion")
    if check is None:
        return problems, None
    if isinstance(assertion, str) and assertion.strip() and (
            _normalized(assertion) not in _normalized(check.function_text)):
        problems.append(f"mapping {where}: its assertion is not in the "
                        "check's function")
    # Rule 2: the check's function invokes every tool the entry lists.
    for tool in tools:
        if tool in names and tool not in check.invoked:
            problems.append(f"mapping {where}: the check's function never "
                            f"invokes {tool!r} (rule 2)")
    # Rule 3: an outcome needs a computed, verified, non-failure record.
    if category == OUTCOME:
        for broken, why in (
            (check.passed_literal, "its passed value is a literal"),
            (check.verified_false, "it is recorded with verified=False"),
            (check.in_handler, "it is recorded in an exception handler"),
            (check.in_failure_branch, "it is recorded in a failure branch"),
        ):
            if broken:
                problems.append(f"mapping {where}: {why} (rule 3)")
    return problems, check


def build_report(root: Path) -> dict[str, Any]:
    """The whole report for the repository at `root`.

    Raises RegistryDefect for a registry that cannot be enumerated honestly.
    Mapping problems are collected in `errors`; an invalid entry promotes
    nothing.
    """
    root = Path(root)
    registrations = enumerate_registrations(root / PACKAGE_REL)
    names = {r.name for r in registrations}
    evidence_path = root / EVIDENCE_REL
    evidence = (json.loads(evidence_path.read_text(encoding="utf-8"))
                if evidence_path.is_file() else {})
    checks: dict[tuple, Check] = {}
    for source, rel in CHECK_SOURCES.items():
        for check in collect_checks(source, root / rel):
            checks[(check.source, check.section, check.label,
                    check.line)] = check
    invoked_anywhere = set().union(*(c.invoked for c in checks.values()))

    errors: list[str] = []
    promoted: dict[str, dict[str, set[str]]] = {
        name: {OUTCOME: set(), EXECUTION: set()} for name in names}
    for entry in evidence.get("mappings", []):
        problems, mapped = _entry_problems(entry, checks, names)
        if problems or mapped is None:
            errors.extend(problems)
            continue
        for tool in entry["tools"]:
            promoted[tool][entry["category"]].add(mapped.check_id)

    decided: dict[str, dict[str, Any]] = {}
    for item in evidence.get("registration_only", []):
        tool, reason = item.get("tool"), item.get("reason")
        if tool not in names:
            errors.append(f"registration-only decision names a missing tool "
                          f"{tool!r}")
        elif reason not in REASONS:
            errors.append(f"registration-only decision for {tool!r} has "
                          f"reason {reason!r}")
        elif tool in decided:
            errors.append(f"registration-only decision for {tool!r} is "
                          "repeated")
        else:
            decided[tool] = item

    flags: dict[str, dict[str, Any]] = {}
    for flag in evidence.get("flags", []):
        tool = flag.get("tool")
        missing = [k for k in ("flag", "reason", "sources", "enforcement")
                   if not flag.get(k)]
        if tool not in names:
            errors.append(f"availability flag names a missing tool {tool!r}")
        elif missing:
            errors.append(f"availability flag for {tool!r} lacks "
                          + ", ".join(missing))
        else:
            flags[tool] = flag

    tools = []
    for site in sorted(registrations, key=lambda r: r.name):
        found = promoted[site.name]
        if found[OUTCOME]:
            category, reason = OUTCOME, ""
        elif found[EXECUTION]:
            category, reason = EXECUTION, ""
        else:
            category = REGISTRATION_ONLY
            if site.name in decided:
                reason = decided[site.name]["reason"]
            elif site.name not in invoked_anywhere:
                reason = "no-check"
            else:
                reason = "unmapped"
        if site.name in decided and category != REGISTRATION_ONLY:
            errors.append(f"registration-only decision for {site.name!r} "
                          f"contradicts its {category} mapping")
        flag = flags.get(site.name)
        tools.append({
            "name": site.name, "category": category, "reason": reason,
            "flag": flag["flag"] if flag else "",
            "checks": sorted(found[OUTCOME] | found[EXECUTION]),
            "note": decided.get(site.name, {}).get("note", ""),
            "file": site.file, "line": site.line,
        })

    runs = []
    for record in evidence.get("run_evidence", []):
        missing = [k for k in ("scope", "build", "date", "result", "source",
                               "limitation") if not record.get(k)]
        if missing or record.get("scope") not in RUN_SCOPES:
            errors.append(f"run-evidence record {record!r} is incomplete")
            continue
        runs.append(record)

    counts = {category: sum(1 for t in tools if t["category"] == category)
              for category in CATEGORIES}
    reasons = {reason: sum(1 for t in tools if t["reason"] == reason)
               for reason in REASONS}
    return {
        "registry": {"total": len(tools)},
        "source_coverage": {"counts": counts, "registration_only_reasons":
                            reasons},
        "tools": tools,
        "flags": [flags[name] for name in sorted(flags)],
        "run_evidence": runs,
        "run_scopes_without_records": [
            scope for scope in RUN_SCOPES
            if not any(r["scope"] == scope for r in runs)],
        "errors": errors,
    }


# ─── Outputs ─────────────────────────────────────────────────────────────────

def _names(tools: list[dict[str, Any]]) -> str:
    return ", ".join(f"`{t['name']}`" for t in tools) or "none"


def render_markdown(report: dict[str, Any]) -> str:
    """The generated TOOL_STATUS.md block, markers included."""
    counts = report["source_coverage"]["counts"]
    reasons = report["source_coverage"]["registration_only_reasons"]
    tools = report["tools"]
    out = [
        BLOCK_BEGIN,
        "<!-- Generated by `py -3 scripts/coverage_report.py --markdown`; "
        "do not edit by hand. -->",
        "",
        "**Source coverage** says what the test code is written to check. It "
        "is derived offline from explicit entries in "
        "`scripts/coverage_evidence.json` and claims nothing about any run. "
        "**Run evidence** is listed separately below.",
        "",
        "| Measure | Value |",
        "|---|---:|",
        f"| Registered (runtime registry, offline) | {report['registry']['total']} |",
        f"| `{OUTCOME}` | {counts[OUTCOME]} |",
        f"| `{EXECUTION}` | {counts[EXECUTION]} |",
        f"| `{REGISTRATION_ONLY}` | {counts[REGISTRATION_ONLY]} |",
    ]
    for reason in REASONS:
        out.append(f"| `{REGISTRATION_ONLY}`, reason `{reason}` | "
                   f"{reasons[reason]} |")
    out += ["", "**Availability flags.** A flag leaves the tool registered "
            "and its source category unchanged. Coverage is never permission "
            "to run a flagged tool.", "",
            "| Tool | Flag | Reason | Enforcement | Sources |",
            "|---|---|---|---|---|"]
    for flag in report["flags"]:
        out.append(f"| `{flag['tool']}` | `{flag['flag']}` | {flag['reason']} "
                   f"| {flag['enforcement']} | "
                   + "; ".join(flag["sources"]) + " |")
    out += ["", "**Run evidence.** Recorded observations only; none is "
            "converted into per-tool source coverage.", "",
            "| Scope | Build | Date | Result | Source | Limitation |",
            "|---|---|---|---|---|---|"]
    for run in report["run_evidence"]:
        out.append(f"| {run['scope']} | {run['build']} | {run['date']} | "
                   f"{run['result']} | {run['source']} | {run['limitation']} |")
    for scope in report["run_scopes_without_records"]:
        out.append(f"| {scope} | — | — | No preserved run record | — | — |")
    out += ["", f"**`{OUTCOME}`:** "
            + _names([t for t in tools if t["category"] == OUTCOME]), "",
            f"**`{EXECUTION}`:** "
            + _names([t for t in tools if t["category"] == EXECUTION])]
    for reason in REASONS:
        group = [t for t in tools if t["reason"] == reason]
        out += ["", f"<details><summary><code>{REGISTRATION_ONLY}</code>, "
                f"reason <code>{reason}</code> ({len(group)})</summary>", "",
                _names(group), "", "</details>"]
    out.append(BLOCK_END)
    return "\n".join(out) + "\n"


def current_block(status_text: str) -> str | None:
    """The block as it stands in TOOL_STATUS.md, or None when absent."""
    start = status_text.find(BLOCK_BEGIN)
    end = status_text.find(BLOCK_END)
    if start < 0 or end < start or status_text.count(BLOCK_BEGIN) != 1:
        return None
    return status_text[start:end + len(BLOCK_END)] + "\n"


def block_is_current(root: Path, report: dict[str, Any]) -> bool:
    path = Path(root) / STATUS_REL
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return current_block(text) == render_markdown(report)


def render_summary(report: dict[str, Any], listing: bool) -> str:
    counts = report["source_coverage"]["counts"]
    reasons = report["source_coverage"]["registration_only_reasons"]
    out = [
        "UEFN Toolbelt - registry-derived coverage report",
        f"  Registered: {report['registry']['total']}",
        "  Source coverage (what test code is written to check; not a run):",
    ]
    for category in CATEGORIES:
        out.append(f"    {category}: {counts[category]}")
    for reason in REASONS:
        out.append(f"      {REGISTRATION_ONLY} ({reason}): {reasons[reason]}")
    out.append("  Availability flags:")
    for flag in report["flags"]:
        out.append(f"    {flag['tool']}: {flag['flag']} - {flag['reason']}; "
                   f"enforcement: {flag['enforcement']}; sources: "
                   + "; ".join(flag["sources"]))
    out.append("  Run evidence (recorded observations, by scope and build):")
    for run in report["run_evidence"]:
        out.append(f"    [{run['scope']}] {run['build']} ({run['date']}): "
                   f"{run['result']} - source: {run['source']}; "
                   f"limitation: {run['limitation']}")
    for scope in report["run_scopes_without_records"]:
        out.append(f"    [{scope}] no preserved run record")
    if listing:
        out.append("  Tools:")
        for tool in report["tools"]:
            out.append(
                f"    {tool['name']}  {tool['category']}"
                + (f" ({tool['reason']})" if tool["reason"] else "")
                + (f"  flag={tool['flag']}" if tool["flag"] else "")
                + ("  checks=" + ",".join(tool["checks"])
                   if tool["checks"] else ""))
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--list", action="store_true")
    mode.add_argument("--json", action="store_true")
    mode.add_argument("--markdown", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]),
                        help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    # The block and the report carry non-ASCII text; a Windows console
    # default encoding would corrupt --markdown output written to a file.
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")
    root = Path(args.root)
    try:
        report = build_report(root)
    except RegistryDefect as defect:
        for problem in defect.problems:
            print("registry defect: " + problem, file=sys.stderr)
        return 2
    errors = list(report["errors"])
    # --markdown produces the block, so it cannot also require the block to
    # be current already.
    if not args.markdown and not block_is_current(root, report):
        errors.append(STATUS_REL + ": the generated coverage block is stale "
                      "or missing; regenerate it with --markdown")
    if args.markdown:
        sys.stdout.write(render_markdown(report))
    elif args.json:
        sys.stdout.write(json.dumps(report, indent=2) + "\n")
    elif not args.check:
        sys.stdout.write(render_summary(report, args.list))
    for error in errors:
        print("coverage error: " + error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
