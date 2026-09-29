# WO-005 — Registry-Derived Coverage Source of Truth

STATUS: ISSUED

AUTHORIZATION: ISSUED — SESSION A AUTHORIZED FOR OFFLINE COVERAGE MODEL ONLY

OWNER: Ocean Bennett

PRIORITY: P2

BASELINE: `1925ba8a09c3696d25de7ffc3f23caf970362c4d`

ISSUANCE_COMMIT: `528f1962c0c45c0631bab3637f3fd40db6317027`

ISSUANCE_CI_WORKFLOW: `36529997892`

ISSUANCE_CI_JOB: `109281301869` — Lint, types, tests

SESSION_A_AUTHORIZATION_COMMIT: `867074f8a520450ef6073b4c922079a897a83886`

SESSION_A_AUTHORIZATION_CI_WORKFLOW: `36596756689`

SESSION_A_AUTHORIZATION_CI_JOB: `109503539592` — Lint, types, tests

## Issuance basis

The independently accepted revision of this mandate was committed as
`528f1962c0c45c0631bab3637f3fd40db6317027`; [CI workflow
`36529997892`](https://github.com/undergroundrap/UEFN-TOOLBELT/actions/runs/36529997892)
completed successfully, including required job
[`109281301869` — Lint, types, tests](https://github.com/undergroundrap/UEFN-TOOLBELT/actions/runs/36529997892/job/109281301869).
Those identify the accepted proposal, not the later commit that records this
issuance. The planning baseline above is preserved unchanged.

Issuance alone grants no implementation authority. A session becomes
implementable only when the owner names it in root `WORKORDER.md`. The
live-verification exemption proposed for Session A was not accepted by
issuance; at that gate it remained a separate owner decision.

## Session A authorization basis

Session A is authorized for the offline coverage model only under the current
root `WORKORDER.md` gate alone. The recorded basis is commit
`867074f8a520450ef6073b4c922079a897a83886`; [CI workflow
`36596756689`](https://github.com/undergroundrap/UEFN-TOOLBELT/actions/runs/36596756689)
completed successfully, including required job
[`109503539592` — Lint, types, tests](https://github.com/undergroundrap/UEFN-TOOLBELT/actions/runs/36596756689/job/109503539592).

This gate covers exactly the scope in "Proposed Session A — offline coverage
model" below: its six-path file scope, the migration shim, the acceptance
tests, the static gates, the cleanup duties, and the exclusions, unchanged.
Session A ends with its worktree uncommitted for independent review. It opens
no deploy, editor launch, bridge startup, MCP call, commit, or push. The
planning baseline and the issuance evidence above are preserved unchanged, and
neither is the Session A basis.

## Session A live-verification exemption

The owner accepted the live-verification exemption proposed for Session A
under "Live verification" below, on these terms only:

- It applies only to the offline Session A scope accepted above.
- Session A changes no tool, registry, startup, bridge, dashboard, or editor
  behaviour.
- The only `Content/Python/` change permitted during implementation is the
  standalone `list_untested.py` migration shim specified under "Migration
  shim" below.
- Offline tests and source mappings are not live execution evidence.
- Any editor or runtime impact discovered during implementation stops
  Session A for a new owner decision; it does not silently widen this
  exemption.
- The eventual implementation commit must explain this exemption truthfully
  through the existing `Live-Verification: not-required — <reason>` trailer.
- This exemption grants no commit, push, deployment, or live-run permission.

## Revision provenance

First proposed as a sketch at planning baseline
`6b8ffb2b2d672812f8699af2c22f92c19708f29b`, kept here as historical provenance.
This revision was prepared at `1925ba8a09c3696d25de7ffc3f23caf970362c4d` after
the 2026-09-29 pre-issuance review, and it records the owner's planning
direction of the same date and the corrections that review required. Every
source fact below was read at that commit. Its CI workflow `36513524464` and
required job `109230682321` (Lint, types, tests) concluded successfully on that
exact commit.

## Problem, as found at the revision baseline

- **Registry universe.** The package has 362 `@register_tool` sites with 362
  distinct constant names and no duplicates. Six are outside `tools/`:
  `toolbelt_smoke_test` (package `__init__.py`), `launch_qt` and
  `toolbelt_update` (`dashboard_pyside6.py`), `debug_dump_verse_actor` and
  `debug_audit_verse_assets` (`diagnostics.py`), and `core_safety_audit`
  (`core/safety_gate.py`).
- **Existing enumerator.** `scripts/drift_check.py::_registered_tools()` walks
  the whole package with `ast`, but it silently skips a file that fails to
  parse, and it keys by name, so a duplicate registration overwrites the first.
  `tests/test_ui_coverage.py` pins only its length to `__tool_count__`. No test
  compares the offline runtime registry with the source set.
- **Old report.** `Content/Python/UEFN_Toolbelt/list_untested.py` regex-scans
  `tools/*.py` only (356 names), and counts any string literal that equals a
  tool name as coverage (191 names).
- **Wrong smoke source.** It reads `tests/smoke_test.py` (463 lines), a stale
  copy. The smoke test that `toolbelt_smoke_test` loads is
  `Content/Python/UEFN_Toolbelt/smoke_test.py` (618 lines). Its Layer 3 tool
  checks are a minimum registry count (`MIN_TOOL_COUNT = 179`, checked with
  `>=` at `smoke_test.py:350` and `:398`; no exact-total assertion) and
  registry membership of six named tools (`verse_gen_custom`, `snapshot_save`,
  `material_apply_preset`, `mcp_start`, `scatter_hism`, and `tag_add`, at
  `smoke_test.py:416-422`). It runs no registered tool.
- **Unattributed checks.** `Content/Python/UEFN_Toolbelt/tools/integration_test.py`
  records checks as `_record(section, name, passed, detail, verified=True)`.
  `name` is a human label, so no check says which tool it evaluates.
- **Reporting surface.** `TOOL_STATUS.md` holds the 2026-08-24 reconciliation
  table (362 / 356 / 191 / 187 / 190) as prose. The counts below are
  reproducible at the revision baseline:
  - 142 registered names never appear inside a backtick span in the file; 141
    have no whole-word match anywhere (`geometry_boolean_union` appears once
    without backticks).
  - The "Layer 7" section (lines 261-312) contains 13 backticked tokens that
    match `[a-z][a-z0-9_]+` and are not registered names: `align`, `arc`,
    `circle`, `distribute`, `grid`, `line`, `randomize`, `reset`, `snap`,
    `spiral`, `stack`, `undo_transaction`, and `wave`.
  - Several paragraphs say the smoke test executes tools, and the Disabled Tools
    table overstates how the LOD tools are disabled. Both are listed under
    Session A.

## Definitions — decision lock

Coverage has two independent axes. They are stored, reported, and counted
separately and are never merged.

**Source coverage** describes what the repository's test code is written to
check. It is derived offline and claims nothing about any run. Each registered
tool has exactly one source category:

| Category | Meaning |
|---|---|
| `defined-outcome` | At least one mapped check that invokes the named tool and whose `passed` value is computed from an assertion about that tool's returned data or observable effect |
| `defined-execution` | Mapped checks invoke the named tool, but none asserts an outcome of it: `verified=False`, a literal `True`, or a result that only shows the call returned |
| `registration-only` | Registered, with no qualifying mapped check. The reason is recorded: `unmapped`, `ambiguous`, or `no-check` |

**Availability flag.** Separate from the category. A flag records the tool,
its reason, its attributable sources, and the enforcement that actually
exists. The flag keeps the tool in the inventory, leaves its source category
unchanged, and is listed prominently in every report. Coverage in any category
is never permission to run a flagged tool, and a mapping never clears a flag.
At the revision baseline three tools carry one flag, `stubbed-operation`:

| Tool | Where the stub acts | Sources |
|---|---|---|
| `lod_auto_generate_selection` | Calls `_apply_lods` directly | Code `tools/lod_tools.py:141-163, 166-217`; `TOOL_STATUS.md:76-82`; `docs/UEFN_QUIRKS.md` #18 |
| `lod_auto_generate_folder` | Calls `_apply_lods` directly | Code `tools/lod_tools.py:141-163, 220-273`; `TOOL_STATUS.md:76-82`; `docs/UEFN_QUIRKS.md` #18 |
| `memory_autofix_lods` | Wrapper: calls `lod_auto_generate_folder` | Code `tools/memory_profiler.py:465-493`; `docs/UEFN_QUIRKS.md` #18. Not in the `TOOL_STATUS.md` table |

What is enforced, from the code: `_apply_lods` never calls the crashing
reduction API (`set_lods_with_notification`); it logs an error and reports the
mesh as failed. There is no registry-level disabling. All three tools stay
registered, callable, and reachable from the dashboard, and the folder tools
return `status: "ok"` with the meshes counted as failed. The documentation says
more than that: `TOOL_STATUS.md:77` calls them "intentionally disabled at
runtime", and Quirk #18 says they "return a clear error message". This work
order records the code-level enforcement only. It claims no new live safety
verification and changes no runtime behaviour.

**Run evidence** describes what was observed. Each record names its scope,
editor build label, date, result, and source: a preserved results file
identified by SHA-256, or a named repository record with its limitation stated.
A tool call in source, `verified=True`, and an offline fake-`unreal` import are
never run evidence. At the revision baseline the records available to this
report are:

- **Integration.** One record: a reported 190/190 checks (163 with `verified`
  true, 27 execution-only) on UEFN 42.00, dated 2026-08-23, on the "publishing
  hardening build based on 112671c" (`TOOL_STATUS.md:58-60`). It is narrative
  only; its results file is not preserved in the repository, and the exact
  harness source that run used is not identified. It stays a check-level
  result and is never converted into per-tool verification.
- **Smoke.** No smoke-test run record is preserved in the repository.
- **Other live records.** The WO-004 Session C record
  (`docs/audits/2026-09-28-wo004-session-c-live-acceptance.md`) documents build
  `++Fortnite+Release-42.20-CL-58011042` on 2026-09-28. After a deploy and full
  restart, the editor log reports 362 tools registered, and the registered
  tools `mcp_start` and `mcp_stop` were run from the console. That record
  limits the registration observation to one machine and one boot, not a
  general result. It is not an integration or smoke run, and it is never
  promoted into integration coverage or per-tool outcome verification.

This work order imports no new evidence and authorizes no live run.

**Promotion rules** for source coverage:

1. Only an explicit mapping entry that names the tool can raise it above
   `registration-only`. Inference alone never promotes.
2. For either `defined-execution` or `defined-outcome`, the mapped check's
   enclosing function must invoke the named tool, as a call to `run` or
   `tb.run` with that tool's constant name. A registry-membership test, an
   import, or a string mention without a call is not an invocation.
3. A mapped check supports `defined-outcome` only if, in addition, its
   `passed` argument is an expression, not a literal; `verified` is not
   `False`; and it is not recorded in an exception handler or a failure branch.
   The mapping entry names the assertion it relies on, and the independent
   review judges that the assertion concerns that tool.
4. Being the only tool in a section is not sufficient by itself.
5. Counts are over unique tools. Several checks for one tool count once, and a
   check promotes only the tools its entry lists.
6. Anything unmapped, ambiguous, or unsupported stays `registration-only` with
   its reason shown in the report. Nothing is promoted silently.

## Evidence sources — decision lock

- Definitions of checks: `Content/Python/UEFN_Toolbelt/tools/integration_test.py`
  and `Content/Python/UEFN_Toolbelt/smoke_test.py`, read as source text only.
- The live smoke test's current Layer 3 tool checks are the minimum registry
  count and six registry-membership checks, with no invocation, so under rule 2
  they cannot raise any tool above `registration-only`.
- `tests/smoke_test.py` is excluded from every current coverage claim and left
  in place; its retirement is separate work.
- Run evidence comes only from the run-evidence records defined above.

## Owner decisions for this revision (2026-09-29)

1. `list_untested.py` stays as a minimal migration shim.
2. Session A is offline only. The live-verification exemption below was sent
   to independent review and owner acceptance; this revision did not grant it.
3. The optional live integration run is deferred and is not required to close
   WO-005.
4. One hardened enumerator is shared with `drift_check._registered_tools()`,
   keeping that function's interface and caller-root behaviour. No
   authorization scanner or other governance check changes.

## Proposed Session A — offline coverage model

Offline only: no deploy, editor, bridge, or MCP work. If any runtime impact is
discovered, Session A stops and the scope is reconsidered with the owner.

**Exact file scope**

| Path | Change |
|---|---|
| `scripts/coverage_report.py` | New. The hardened enumerator, the mapping validator, the classifier, and the CLI |
| `scripts/coverage_evidence.json` | New. The explicit check-to-tool mapping, the availability flags with reason, sources, and enforcement, and the run-evidence records |
| `scripts/drift_check.py` | `_registered_tools()` delegates to the hardened enumerator. No other change |
| `tests/test_coverage_report.py` | New. The acceptance tests below |
| `TOOL_STATUS.md` | The generated block and the named corrections below. No other prose changes |
| `Content/Python/UEFN_Toolbelt/list_untested.py` | Replaced by a minimal migration shim (see below) |

**`TOOL_STATUS.md` changes, exactly**

- The reconciliation table and the "Layer 7" list become one generated block
  between `<!-- coverage:begin -->` and `<!-- coverage:end -->`, using
  registered names only.
- The claim that the smoke test executes tools is corrected where it appears:
  the heading "Layer 3 Execution Verified (Safe Tools)" (line 86), that
  section's introduction (line 87) and closing note (line 108), the coverage
  sentence at line 114, the "Safe tools execute end-to-end" bullet at line 318,
  and the contributor step at line 412. The corrected heading and text say
  what the smoke test actually checks, and nothing more:
  - a minimum registry count (`MIN_TOOL_COUNT`, 179 at this baseline), not an
    exact total;
  - registry membership of six named tools, listed under "Problem" above;
  - no execution of any registered tool.

  The section's list of eighteen tools stays, reframed as tools that need no
  selection or open level. It no longer says they are executed or verified,
  and it does not claim the smoke test checks them individually: none of them
  is among the six membership names.
- The Disabled Tools paragraph and table (lines 76-82) are qualified to match
  the availability flags above: registered and callable, the reduction call
  stubbed in code, `memory_autofix_lods` added, and the module named
  `lod_tools.py`.

Everything else in `TOOL_STATUS.md`, including its historical figures and
module notes, is left as it is.

**Enumerator.** It returns every registration site with its name, category,
file, and line. It takes the package root as an argument. A file that fails to
parse, a duplicate name, or a non-constant name is an error that names each
site involved, never a silent skip or overwrite.

`drift_check._registered_tools()` keeps its signature and its name-to-category
mapping, and still resolves the package from `drift_check.ROOT`. It loads
`coverage_report.py` by file path, from the same directory as `drift_check.py`,
with `importlib.util.spec_from_file_location`. This matches how the existing
tests load `drift_check.py` itself, and does not rely on `scripts/` being on
`sys.path`.

**CLI**

- `py -3 scripts/coverage_report.py` prints the registry total, the source
  category counts with their reasons, the flagged tools with flag, reason,
  sources and enforcement, and the run-evidence records by scope and build.
- `--list` adds one line per tool: name, category, reason, flag, and check ids.
- `--json` emits the same data, machine-readable.
- `--markdown` emits the `TOOL_STATUS.md` block.
- `--check` validates without printing the report.

Exit codes: 0 when consistent; 1 when a mapping names a missing check or tool,
breaks a promotion rule, or the `TOOL_STATUS.md` block is stale; 2 for a
registry defect. Low coverage is never an error: there is no threshold.

The generated block states each count as a labelled value, for example
"`defined-outcome`: 12", and never as a number followed by the word "tools".
The same wording rule applies to the corrected `TOOL_STATUS.md` paragraphs:
a figure such as the smoke test's minimum appears as a labelled value or in
code formatting (`MIN_TOOL_COUNT`, 179), never as a number within two words
before "tools", and no number is placed directly before "categories". The
drift check's tool-count rule (`drift_check.py:4435-4438`) flags any number
other than the registry total placed before "tools", and its category rule
(`drift_check.py:4441-4444`) does the same before "categories". Both rules stay
unchanged.

**Mapping.** Each entry has a check id (section, label, and source line), the
tool or tools it covers, the claimed category, and the assertion it relies on.
Session A may leave a tool `registration-only (unmapped)` rather than guess.
No coverage percentage is an acceptance target.

**Migration shim.** `Content/Python/UEFN_Toolbelt/list_untested.py` keeps its
path and does only this:

- It prints that the coverage report now runs from a repository checkout, with
  the command `py -3 scripts/coverage_report.py` from the repository root.
- It prints that it reports no coverage itself.
- It exits with status 3, a value the old script never used, so no caller can
  read it as "all covered" (0) or "gaps found" (1). Its docstring documents
  that code.

It reads no repository file, imports nothing from `scripts/`, and does not
assume `scripts/` exists, since deployed projects receive the package without
it. It registers no tool and changes no editor startup behaviour.

**Acceptance tests** (`tests/test_coverage_report.py`), each able to fail:

1. With the offline fake `unreal`, the runtime registry after
   `register_all_tools()` has exactly the enumerator's names, and the count
   equals `__tool_count__`.
2. A synthetic registration outside `tools/` is counted.
3. A synthetic file with a syntax error, and a synthetic duplicate name, each
   produce exit 2 naming the sites, rather than a smaller total.
4. Positive controls, so a classifier that leaves everything
   `registration-only` fails:
   - a mapped check that invokes its tool, with a non-literal `passed` and
     `verified` true, reaches `defined-outcome`;
   - a mapped check that invokes its tool with `verified=False`, or with a
     literal `True`, reaches `defined-execution`;
   - two tools promoted by separate checks count as two.
5. Rejection cases, for both promoted categories: a registry-membership test,
   a string-literal mention, an import, and a function that never calls the
   mapped tool each leave the tool `registration-only`; and a literal `True`,
   `verified=False`, a failure branch, and an exception handler each fail to
   produce `defined-outcome`.
6. Repeated checks for one tool count once, and a check does not promote a
   tool its entry does not list.
7. A flagged tool keeps its inventory entry and its source category, carries
   its flag with reason, sources and enforcement in every output, and keeps the
   flag when a mapping names it. The three tools above carry the flag.
8. An unmapped tool is reported `registration-only` with its reason.
9. No source fact appears as run evidence; the integration, smoke, and other
   records match the lists above, labels and limitations included; the 42.20
   record contributes to no source category.
10. The `TOOL_STATUS.md` generated block equals `--markdown` output, and
    `tests/smoke_test.py` is not among the report's inputs.
11. The shim exits with status 3, prints the replacement command, and neither
    opens a repository file nor imports from `scripts/`.

**Static gates**: `python -m ruff check .`, `python -m mypy` (the new script is
in the typed `scripts/` island), `python -m pytest`,
`python scripts/drift_check.py`, `python scripts/gen_api_manifest.py --check`,
and `git diff --check`. CI is verified only after a separately gated commit and
push.

**Live verification.** `CLAUDE.md` requires a live UEFN test before a commit,
and a commit touching `Content/Python/` must carry `Verified-Live:` or
`Live-Verification: not-required — <reason>`. Session A changes no tool,
registry, bridge, UI, or editor behaviour. The only `Content/Python/` change is
the shim, which nothing in the runtime imports: `register_all_tools()` and the
startup script never load `list_untested.py`, and its current docstring says
"Run from any Python (outside UEFN is fine)". On that basis a narrowly reasoned
`not-required` exemption was proposed, for independent review and owner
acceptance; the proposal did not grant it. The owner later accepted it, bounded
as recorded under "Session A live-verification exemption" above.

**Cleanup duties.** Session A creates synthetic test fixtures only under
pytest's `tmp_path`, and leaves no cache, report output, or scratch file in the
worktree. It removes only files it created during the session. It deletes no
preserved evidence, snapshot, or other existing repository file; the old
`list_untested.py` content is replaced as scoped above.

**Exclusions.** No change to any tool, `registry.py`, `integration_test.py`,
either smoke test, the dashboard or UI, tool counts, the version, or
`docs/UEFN_QUIRKS.md`. No CI coverage threshold. No general semantic analysis
of test code. No change to authorization scanners or other governance
machinery.

**Stop.** Session A ends with its worktree uncommitted for independent review.
Commit, push, and WO-005 completion each need a separate owner gate.

## Deferred — optional owner-operated integration run

Not part of WO-005 and not required for its closure. A later, separately gated
run on the current editor build could add one integration run-evidence record,
with its results file preserved privately and identified by SHA-256.

## Acceptance criteria

- Every registered tool appears exactly once, with one source category and
  its availability flag where one applies. The enumerator fails loudly on
  unparseable files and duplicate names.
- The runtime registry and the source set are proven equal offline.
- No tool is promoted without an explicit mapping whose check invokes it, and
  no tool reaches `defined-outcome` without meeting every promotion rule.
- Source coverage and run evidence are reported separately; every run record
  keeps its scope, build, date, and limitation.
- The generated `TOOL_STATUS.md` block shows only generated figures and
  registered names, the named paragraphs are corrected, and all other prose is
  unchanged.
- No runtime behaviour changes.

## Stop boundaries

Owner decisions, each separate, none implying the next: issuing WO-005,
opening Session A, the exact commit, the push, and WO-005 completion.
Independent review of Session A comes before the commit decision, and CI runs
after the push; neither is an owner decision, and neither stands in for one.
Tagging, GitHub Release creation, repository metadata changes,
branch-protection changes, and social publication are outside WO-005 and
remain unauthorized. The deferred integration run needs its own owner
decision.

## Issuance requirements carried from WO-004

The issuance transition that names WO-005 in the root pointer must also reword
two history sentences in `WORKORDER.md`, at lines 114 and 155 of the revision
baseline. The issued-order activation scan would otherwise misread them. The
test fixture `_make_wo005_owner_case` in `tests/test_repo_integrity.py` shows
both rewordings. Those edits belong to that governance transition, not to
Session A.

WO-006 and WO-007 remain proposed and unauthorized.

NEXT GATE: fresh independent review of the complete uncommitted Session A
implementation, which is limited to the offline coverage model, followed by
separate owner gates for its commit and its push. Deploy, live runs, the
deferred integration run, and WO-005 completion remain closed.
