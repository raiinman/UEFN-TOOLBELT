# Toolbelt native acceptance

## Authorized scope

The owner requested completion of the maintenance report's evidence gaps and
authorized subagent review, repairs and native test work. This fork maintenance
is separate from upstream WO-008's pinned Claude run. The initial maintenance
revision was `47ff89a912257e0bc6f0269db16c3d8b58b7df4a` on
`codex/toolbelt-reliability-update`; later working-tree repairs and native runs
have their own recorded source hashes. This audit does not attest an untested
merge, a future deployment or a release.

The initial maintenance revision passed GitHub
[CI run 38002672318](https://github.com/raiinman/UEFN-TOOLBELT/actions/runs/38002672318):
Linux 3,265 passed/18 skipped, Windows 3,272 passed/11 skipped. Those results
remain specific to that revision.

## Native target and preserved history

`C:/Users/mikea/Documents/MCP/ToolbeltTests/ToolbeltAcceptance` was created through
the native Blank template. Its descriptor root is
`001485b2-9178-47cf-a1a5-e66b92a43825`. Native mutation procedures check both the
deployed descriptor and active world. The acceptance fixtures belong in this
disposable project, not Riftbloom. Managed deferred startup opened its listener
and dashboard after Python Editor Scripting was enabled.

The initial smoke result was 88/89 because deployment supplied a non-Git
Verse-reference snapshot. The original
[failed smoke](evidence/2026-10-09-toolbelt-acceptance/smoke-before-reference-fix.txt)
and subsequent
[smoke artifact](evidence/2026-10-09-toolbelt-acceptance/smoke-after-reference-fix.txt)
remain separate. Smoke checks establish environment/registration observations,
not functional execution of all tools.

The first local section driver reentered Slate while a material tool pumped
events. That interrupted attempt was stopped without saving the disposable
editor. Its [redacted log](evidence/2026-10-09-toolbelt-acceptance/native-driver-reentry.log)
and [redaction provenance](evidence/2026-10-09-toolbelt-acceptance/native-driver-reentry.redaction.json)
preserve the negative result. Authentication/account content was removed; the
original bytes are retained privately outside the repository. The corrected
driver prevents nested dispatch and repeated sections, records the in-flight
section before calls, and preserves a fresh output directory.

## Recorded native runs, updated 2026-10-20

| Artifact | Recorded procedure | Result and scope |
|---|---|---|
| [Section baseline r2](evidence/2026-10-09-toolbelt-acceptance/native-sections-r2/run.json) | 52 sections, 223 inner calls on the initial disposable editor boot | 189/189 authored checks passed, with 161 authored `verified` flags and 28 execution-only flags. Later review found hidden unsupported operations; these flags are not universal per-tool acceptance. |
| [Asset r1](evidence/2026-10-09-toolbelt-acceptance/native-assets-r1/run.json) | 49 calls, UEFN 42.30, engine `6.0.0-58813929` | 23/24 checks passed. Requested mask compression also changed sRGB from true to false. The original driver assumed other properties stayed unchanged. The failed check and [matching reviewed driver](evidence/2026-10-09-toolbelt-acceptance/native-assets-r1/driver-reviewed.py) are preserved. |
| [Maintenance r1](evidence/2026-10-09-toolbelt-acceptance/native-maintenance-r1/run.json) | 20 calls after a cold restart on 2026-10-20 | 13/15 top-level checks passed. Two section checks failed honestly: visibility included two unsupported lock operations; lighting lacked a DirectionalLight fixture. Completion means the procedure finished, not that every check passed. |
| [Asset r2](evidence/2026-10-09-toolbelt-acceptance/native-assets-r2/run.json) | 50 calls on 2026-10-20, UEFN 42.40, engine `6.0.0-59247843` | 25/25 scoped checks passed. Native properties and reported implicit changes agreed for the named texture fixture. Advanced-class empty lists and negative montage calls remain boundaries. |

The maintenance artifact's 15 checks include the results of three integration
section calls. Their failures are nested observations, not additional independent
failed runs to add to the top-level total. The two failing sections contain two
lock/unlock failures and one missing-light failure. The bulk alignment section
passed its single check.

## Outcomes actually checked

The real PNG fixture is a native 32x32 Texture2D. Asset r2 independently reads
sRGB, compression, group and mip settings after each setter and each of the
seven presets. It compares expected changes with reported counts, checks a
no-op and previews, and verifies exact loaded class/path and contained saved
`.uasset` bytes/hashes. For mask compression it deliberately reproduces the
native sRGB adjustment and checks that `implicit_changes` reports the actual
delta. Requested properties are checked after saving as well as after setting.

Maintenance r1 independently confirms that the earlier asset r1 final PNG
properties and dimensions survived the later cold boot. This is scoped
persistence evidence for that saved state. It does not prove a separate
post-asset-r2 restart of every preset, nor image quality or platform rendering.

The real WAV fixture loads as a native SoundWave with duration approximately
0.10000000149 seconds, one channel and native sample rate 48,000 Hz. The list
includes the named fixture. Direct SoundClass inspection returns None, and the
audit reports that known issue with zero clean assets. The unavailable
`sample_rate_override` property remains explicit in the observations. These
checks do not validate audio playback, MetaSounds, SoundCues or advanced audio
class fixtures.

Maintenance r1 additionally checks:

- Memory reporting reads the known PNG's 32x32 dimensions and records the exact
  project mount, scan scope and enumeration-completeness facts. A partial report
  remains unknown in publish audit. A full current-island report agrees with the
  independently inspected estimate. This rough VRAM estimate is not Fortnite's
  in-session memory calculation or a publishing acceptance.
- Two distinct project-local ZIP backups preserve the exact saved PNG/WAV
  `.uasset` bytes and retain the first archive. This does not establish complete
  project-file coverage, successful restoration or a native traversal-error
  injection.
- Lock/unlock now return explicit errors for the selected FortStaticMeshActor
  whose movement-lock properties are absent or protected. The earlier
  `status=ok`/`failed=1` result is no longer treated as operational success.
  This proves the refusal boundary, not successful movement locking.

## All-tool evidence disposition

The [final combined ledger](evidence/2026-10-09-toolbelt-acceptance/runtime-tool-ledger-final.json)
binds all four raw run artifacts by SHA256. It enumerates all 362 registered
tools and references exact calls and manually reviewed check locations.
The four artifacts contain 342 recorded calls. Including the section harness
itself, 223 distinct registered tools were invoked; 139 were not attempted in
these captured procedures. Neither total is a functional PASS count.

| Conservative disposition | Tools |
|---|---:|
| Returned result only | 165 |
| Scoped native state or output checked | 21 |
| Known audio issue checked | 1 |
| Diagnostic memory subcheck checked | 1 |
| Empty or no-findings boundary | 24 |
| Native capability unavailable | 6 |
| Negative-input refusal boundary | 1 |
| Missing fixture refusal | 1 |
| Empty LOD fixture no-op | 2 |
| Harness with mixed authored assertions | 1 |
| Not attempted in these runs | 139 |
| Total | 362 |

The scoped categories retain narrow limits. Original report existence checks,
material counters, registry membership and authored `verified` flags alone do
not become independent outcome evidence. Empty LOD scans do not validate LOD
generation. Exposed animation factories and refusal of a Texture2D or missing
sequence do not validate montage creation, animation playback or skeleton
compatibility. The baseline and snapshot ledgers remain unchanged as historical
records; the combined ledger does not promote canonical source coverage in
`TOOL_STATUS.md` or `scripts/coverage_evidence.json`.

## Remaining limits and closeout

### Use in any prepared UEFN project

The owner clarified that Toolbelt must work across UEFN projects. Named native
acceptance targets are test isolation, not a restriction on ordinary tools.
The maintained package uses each project's own descriptor and mount.

The [global rollout record](evidence/2026-10-09-toolbelt-acceptance/global-rollout-2026-10-20/rollout.json)
records deployment to AquaShiftGunGame, AquaShiftAnimSource, MyProject, FNSoT,
Scrapline and DeadSignalUndertow, in addition to the already updated Riftbloom
and ToolbeltAcceptance. All eight installed packages match all 94 maintained
Python files, 752 file comparisons in total. The six additional deployments
followed SHA-verified backups of 656 existing files. Five existing startup hooks,
including Scrapline's custom hook, and sibling tools were preserved. Python was
enabled only where missing, in AquaShiftAnimSource and MyProject; other descriptor
fields and bindings were preserved. MyProject received the managed deferred hook.

The local shared [startup loader](evidence/2026-10-09-toolbelt-acceptance/global-rollout-2026-10-20/startup-loader.py)
now discovers installed Content/Python paths with strict native descriptor and
world matching. Its optional legacy registry no longer restricts eligible
projects. MyProject was found without a registry entry. Nineteen standalone
checks passed: 18 simulated discovery, ambiguity, missing-registry and callback
cases, plus filesystem metadata checks for the eight actual installed projects.
The preserved self-check is machine-specific evidence, not a portable CI suite.

The additional six editors were not opened, and the new discovery loader has
not received a fresh native cold-start test. Existing two-project startup
evidence remains specific to the earlier loader. Preparing a future project
still requires its package, Python enablement and startup hook; it needs no
hard-coded project-name entry. The user preference and global Toolbelt skill
now make that preparation part of project setup.

### Current startup and deployment, 2026-10-20

After deployment and a full UEFN restart, ToolbeltAcceptance started its
authenticated listener and dashboard automatically. Its five setup checks were
green and its [health report](evidence/2026-10-09-toolbelt-acceptance/smoke-2026-10-20.txt)
passed 89/89. The [current byte manifest](evidence/2026-10-09-toolbelt-acceptance/deployed-python-2026-10-20.json)
matches all 94 deployed Python files against maintained source. A Git stash
round-trip changed line endings in six source files; restoring their previously
deployed byte form recovered exact equality without a behavior change.

The package was then deployed to Riftbloom with the editor closed. Its normal
project load started the listener and dashboard without console recovery.
[Native level readback](evidence/2026-10-09-toolbelt-acceptance/riftbloom-level-2026-10-20.json)
retained the Riftbloom world with 122 actors. Its dashboard showed five passing
setup checks, PySide6 6.12.0, 362 registrations, 23 Verse chapters and a config
path in Riftbloom's own Saved directory. Its
[health report](evidence/2026-10-09-toolbelt-acceptance/riftbloom-smoke-2026-10-20.txt)
passed 89/89. The [deployment/startup record](evidence/2026-10-09-toolbelt-acceptance/riftbloom-startup-2026-10-20.json)
contains matching source/deployed hashes for all 94 Python files and records
the limits of these derived UI observations. No acceptance fixtures were run
in Riftbloom.

The installer reported preserving Riftbloom's startup hook byte-for-byte.
An extra pre-deployment package-backup script failed on a nested baseline path,
but deployment was erroneously issued after that failure. That separate backup
was never created; the successful install removed its temporary prior-package
copy. Prior maintained source remains in Git, but no exact snapshot of the
previous deployed package is claimed. This was disclosed during the work;
startup guidance now explicitly requires stopping dependent deployment when
backup preparation fails.

Before loading Riftbloom, the nine shared Saved files captured immediately
before this resumed acceptance were restored to their exact pre-test hashes.
Post-test versions were retained outside the repository. The
[restoration manifest](evidence/2026-10-09-toolbelt-acceptance/shared-state-restoration-2026-10-20.json)
records both identities. The listener credential was excluded. These are the
October 20 baseline bytes, preserving intervening user history; the older
October 9 backups were not substituted.

### Functional and platform boundaries

The scoped evidence folders use Git `-text` attributes so captured Windows
line endings survive checkout unchanged. The initial maintenance folder's three
checksummed artifacts match their original recorded digests. Earlier commits
could normalize those text artifacts; their CI did not include the new optional
artifact-byte checks. The current evidence binding requires exact bytes on
Windows and Linux rather than relying on platform newline conversion.

- Positive compatible animation, skeletal, advanced audio, Blueprint and other
  class fixtures remain absent or unverified. Their empty queries, missing APIs
  and invalid-input controls stay separately classified. No 362-tool functional
  acceptance is claimed.
- Native evidence covers one Windows PC and the recorded disposable project
  boots/builds. It does not prove Linux editor execution, PS5 behavior,
  multiplayer gameplay, Fortnite upload or remote publishing validation.
- The integration harness remains local-only through the UEFN console/dashboard.
  The bridge rejected its invocation before execution. Its cleanup does not
  restore every asset, file or persistent setting.
- Recorded runtime source hashes and manifests describe their captured revisions.
  The older [manifest](evidence/2026-10-09-toolbelt-acceptance/deployed-python-final.json)
  is preserved separately. A later runtime change requires fresh deployment
  attribution and relevant acceptance.
- Final merged-tree verification passed 4,142 tests with 22 skips across four
  workers in 1,130.43 seconds. The [JUnit report](evidence/2026-10-09-toolbelt-acceptance/offline-final-2026-10-20.xml)
  and [summary](evidence/2026-10-09-toolbelt-acceptance/offline-final-2026-10-20.json)
  preserve the result. Ruff, Mypy (13 files), drift, coverage, API manifest
  (172 symbols) and dependency checks passed. Interrupted serial runs are not
  counted as complete passes.
- Fork main `568eca67c5000d28ffd010dc80f8d3dc237c2e0d` was integrated with
  its artwork and formal work-order records preserved. Scoped same-model
  reviews accepted the maintenance, integration, evidence-byte protection and
  four-worker CI setup. Author rechecks are not independent review; no
  cross-model review or completed WO-008 client acceptance is claimed.

The source-derived [tool plan](evidence/2026-10-09-toolbelt-acceptance/tool-plan.json)
and [safe call plan](evidence/2026-10-09-toolbelt-acceptance/safe-additional-calls.json)
remain preparation where no matching native observation exists. The fixture
generator establishes original source media only; import and property claims
above come from the corresponding native evidence.

DOX closeout: runtime, core, tool, script, CI and test guides document the changed
contracts. The evidence guide now requires preserving exact captured bytes;
the scoped Git attributes retain original whitespace as evidence. Runtime Python
still passes its normal lint checks. The audit and documentation parent scopes
and child indexes remain unchanged because their ownership already covers these
artifacts. Project startup guidance was refreshed separately with the observed
project-local config paths and the requirement to stop deployment when a
prerequisite backup fails.
