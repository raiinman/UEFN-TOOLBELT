# Toolbelt repository maintenance — 9 October 2026

## Scope and baseline

The user requested a repository-wide audit and repairs after the deployment/startup
repair. The target is the local `raiinman/UEFN-TOOLBELT` fork; upstream is
`undergroundrap/UEFN-TOOLBELT`. This maintenance is authorized by the user's chat,
separately from upstream WO-008's pinned, one-attempt acceptance run. Preserve
that work order's records without attempting its live run or claiming completion.
Commits, pushes, releases and repository settings remain separate owner actions.

- Local/fork head: `2a22aefce53db281b1f613429aee8441801e7e27`.
- Upstream head: `ce04d17ab5fd548adaddb95775e23b97f418829f`.
- Upstream's additional commit changes five governance/integrity paths, with no
  runtime changes. Retain the fork's additional DOX hierarchy and local repairs.
- GitHub observations: fork issues and discussions disabled, Actions enabled but
  no runs, PRs or releases returned. Upstream has three closed issues, no PRs,
  a v2.5.0 release and a successful CI run for its current head.

## Ordered repair checklist

1. [x] Establish the full offline baseline: Ruff, configured Mypy, all pytest
   tests, drift, generated coverage and API-manifest checks. Preserve failures
   and distinguish tests skipped on this platform from passing checks.
2. [x] Incorporate the five upstream paths without resetting the local worktree
   or deleting DOX files. Verify upstream path equality and integrity checks.
3. [x] Repair installer/deployment gaps and active restart instructions. Verify
   managed-hook preservation, new installs, upgrade failures and build stamps
   against temporary directories; retain prior local compatibility fixes.
4. [x] Review CI's platform coverage and public entry points. Add coverage for
   the Windows deployment/session workflow and verify relevant CI commands.
5. [x] Inspect remaining runtime compatibility and client/bridge boundaries.
   Repair confirmed failures; keep source suspicions, empty scans, unavailable
   APIs and positive native operations separately labeled.
6. [x] Deploy executable changes, fully restart UEFN, verify automatic startup,
   dashboard and selected normal/read-only tool interactions. Do not run the
   mutating integration harness in Riftbloom.
7. [x] Recheck modified behavior, complete the DOX pass and record remaining
   limitations. Leave a concrete uncommitted change set for owner review.

## Evidence limits

Offline checks do not prove all 362 tools work in current UEFN. Public GitHub
records do not establish private runtime behavior. Broader tool acceptance needs
appropriate source assets and a disposable native project; use project-specific
acceptance evidence rather than converting registry counts into functional claims.

## Results

### Repaired findings

- Installer: stage complete package copies before replacement; restore the old
  package if replacement fails; preserve managed hooks and unchanged default
  loaders; stamp installs; support retaining existing PySide6 dependencies;
  avoid undefined cleanup variables when the appended loader finds no packages.
- AssetData: replace removed `object_path`/`asset_class` reads in eight modules
  with package/object names and current class metadata. Native Blueprint audit
  reproduced the old `object_path` failure and then loaded the same prop cleanly.
  An unreadable Blueprint compile status no longer counts as clean.
- Project paths: default reads/destinations refuse unknown or reserved mounts.
  Explicit read paths keep their identity; UUID project paths still resolve.
- Diagnostics: Verse/device candidates use the active project mount and bounded
  metadata results instead of `/TOOL_TEST`. Publish audit shares the build
  service's editor-log selection and latest-compile scan.
- Workflow guides: current instructions use guarded reloads or full restarts.
  Historical crash records remain intact. Reference schemas are snapshots to
  verify against the installed editor, not proof of current API availability.
- CI: Linux and Windows matrix, read-only token permissions, manual dispatch,
  generated drift/coverage/API gates and a real MCP SDK import check. Reviewed
  official action releases are pinned: checkout v7.0.1 and setup-python v7.0.0.
  External SDK dependencies are declared in `requirements-mcp.txt`; the local
  adapter successfully imported with SDK 1.30.0.

### Verification so far

- Fresh focused repair checks: **59 passed**. Full Ruff, configured Mypy (13
  source files), coverage regeneration check and API-manifest check passed.
  The manifest remains current at 171 Unreal symbols. CI YAML parsed and the
  Windows/Linux matrix and permissions were checked; GitHub execution awaits a
  published change.
- Real deploy and installer CLI updates preserved Riftbloom's startup-hook hash.
  Following full UEFN restart, the listener/dashboard started automatically on
  the UUID mount. Native readback retained Riftbloom with 122 actors; all five
  dashboard badges passed with 362 tools, PySide6 6.12.0 and 23 Verse chapters.
- Native health check: **89/89** on UEFN 42.30, UE 6.0.0-58813929 and Python
  3.11.8. The raw result is preserved in
  [native-smoke.txt](evidence/2026-10-09-toolbelt-maintenance/native-smoke.txt).
- Blueprint audit: one prop failed to load before repair; the same prop was
  clean with zero issues after repair. Verse asset audit changed from no matches
  in the hard-coded test mount to 30 candidates in Riftbloom's mount. After a
  normal Compile Verse click, both build status and publish audit reported
  SUCCESS; build status reported zero errors. See the derived
  [native observations](evidence/2026-10-09-toolbelt-maintenance/native-observations.json).
- [Deployed Python manifest](evidence/2026-10-09-toolbelt-maintenance/deployed-python.json)
  records matching source/deployed hashes for the observed runtime. Checksums
  accompany the artifacts. No Fortnite upload or mutating integration harness
  was run. These observations do not complete WO-008's separate acceptance run.

### Remaining checks and limits

The full initial offline suite completed with exit code 0, with platform-specific
skips. Because that interpreter started before repairs, current executable fixes
were additionally checked in a fresh process: 59 focused checks passed. The
updated coverage tests passed 35 checks. Upstream's WO-008 checks passed 525
checks in an isolated checkout, then 525 again on the combined fork. All five
incorporated paths match upstream `ce04d17` exactly. Full Ruff, configured Mypy,
drift, coverage and API-manifest checks passed on the combined tree.

The coverage ledger now includes the preserved 89/89 environment-health run.
Its source classifications remain 80 tools with defined outcome checks, 73 with
execution checks and 209 registration-only tools; the new record promotes no
per-tool evidence level. Existing local compatibility/window fixes were retained
and exercised by the baseline, their focused checks and native startup. The
source authoring fields and installed runtime remain v2.5.0, 362 tools and 55
categories; no release-version claim was added.

DOX closeout: root deployment/dependency guidance, runtime package, core, tools
and CI contracts were updated where behavior changed. Workflow guides and current
reference tables now use the safe reload procedure. Documentation, audit,
evidence, work-order and test parent scopes/indexes remain unchanged because
their ownership and structure already cover these artifacts. Upstream governance
records were incorporated without executing their separately gated live run.

Class-specific animation/audio/texture mutation acceptance still needs native
assets and a disposable project. The installed editor's unavailable APIs and
stubbed LOD operations remain explicitly limited. No cross-model independent
review is claimed; the available Claude CLI is signed out. Commit, push and
release actions have not occurred.
