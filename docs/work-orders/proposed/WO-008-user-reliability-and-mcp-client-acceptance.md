# WO-008 User reliability and MCP client acceptance

STATUS: PROPOSED
AUTHORIZATION: NOT AUTHORIZED
Owner: Ocean Bennett
Priority: user-facing reliability and missing integration evidence
Draft date: 2026-10-04
Revision: r2
Planning baseline: `9879d39fbdb58083a0f7229a9c9c90c7d6fb375f`

This is a registered following-train proposal, not an issued Work Order.
The owner adopted r2 as a planning basis only. The repository's
`WORKORDER.md` continues to say NONE/NONE. Nothing here authorizes
implementation, editor contact, configuration changes, a commit, a push,
or publication.

## Purpose and evidence

Establish that one actual MCP client can use Toolbelt's authenticated bridge to
read, change, and restore one actor in the owner's installed UEFN build. Then
repair the bounded disconnect-handling issue and misleading setup/UI wording,
and verify the changed package through that same client. A useful result is a
repeatable user workflow with explicit limits, not more tools or a benchmark.

The baseline's repository CI succeeded: workflow `37227518827`, job
`111510144686`, with 2666 passed and 14 skipped on Ubuntu 24.04 / Python 3.11.16.
That is carried evidence from the verified push handoff, not a run for this
draft or live MCP-host evidence. The skip reasons were not printed.

The released `v2.5.0` tag remains on
`eabce22518d07725e05173aa707909023166a799`. Runtime, `client.py`, `mcp_server.py`,
and `.mcp.json.template` have no diff between that tag and the planning baseline.
Accepted records do not demonstrate the hardened package through an actual
MCP host, or establish compatibility with UEFN 42.30. Record the installed
build at execution; do not assume it from chat or advertise an untested build.

The [WO-004 Session C record](../../audits/2026-09-28-wo004-session-c-live-acceptance.md)
observed `ConnectionAbortedError` during response writes. Later requests still
succeeded; this is not evidence that the listener crashed. The
[composition explainer](../../OFFICIAL_MCP_AND_TOOLBELT.md) and
2.5.0 notes disclose missing host integration and unsupported dashboard/menu
wording. WO-006 remains superseded, with no accepted benchmark.

## Admission and issuance prerequisites

At the planning baseline, the checker admitted only the remaining frozen
WO-001 through WO-007 proposals, then an empty set. Canonical placement
depends on a separately reviewed and owner-authorized proposal-admission
amendment. That amendment recognizes this exact following-train proposal
only; it does not add WO-008 to the frozen train. Its scope is this
proposal, the affected checker and tests, and proposed-directory guidance.
Frozen-train missing, duplicate, and misplaced-order protections remain
in force. Admission is not a general state-machine rewrite and permits
no unknown issued order.

Proposal-only admission retains NONE/NONE; it does not make issuance or any
session valid. A separate, scoped, independently reviewed and owner-authorized
issuance/session-enforcement transition remains outstanding. The checker now
accepts only frozen-train issued identities, defaults to broader Session A
implementation wording, and permits Session C only for WO-004. That later
transition must support WO-008's exact identity and closed, offline-preparation,
and live-start boundaries, resolving its exact markers and conditional prose
without blanket scanner exemptions. It must preserve publication/history and
frozen-train protections when a new issued order replaces NONE: distinguish
historical bases/records from the new pointer shape instead of simply reusing
the NONE-state helper unchanged. Do not append WO-008 to the old frozen train
or waive unknown-order checks. Its precise file/test plan is a later deliverable,
not authority given by this draft.

Both amendment plans require targeted positive and damage probes for proposal
admission with NONE/NONE retained, unknown/duplicate/misplaced orders, missing
historical documents or publication history, unauthorized sessions, and each
intended later state. Issuance and each session still require their separate
owner gates in `WORKORDER.md`. Neither amendment is implemented or authorized
by this proposal.

## Session A Real client baseline

The owner selected **Claude Code** as the first MCP client. This selects a test
target only; it grants no setup or live authority and establishes no compatibility.
Session A, if separately authorized, changes no product code. Use Claude Code
and an owner-approved disposable project, not a production project or recovery
of the old WO-006 fixture. Prepare and review the exact call sequence offline
before a separate owner instruction starts live contact. No launcher rehearsal
or timing harness is required.

Before live contact, record the client name/version, external Python and MCP
package versions, UEFN About build, source/deployment identities, deployed
extras, and the disposable project's file baseline. The owner performs deploy,
full editor restart, fixture checks, and local bridge lifecycle steps. Use the
selected client's normal MCP launch mechanism in an isolated configuration;
do not read or overwrite the owner's existing `.mcp.json`, install dependencies,
or change shared agent permissions without separate approval.

Use a movable, unlocked test actor approved by the owner. Before the baseline,
the owner prepares it with non-default rotation and scale: at least one component
of each must differ from its default by more than its agreed comparison
tolerance. Resetting to zero rotation or unit scale must therefore fail the
preservation check. Record its exact path, class, full transform, and an explicit
small location-only target.
The target must differ from the recorded baseline on at least one coordinate
by more than the agreed location-comparison tolerance; an unchanged actor must
fail the target check. Preserve rotation and scale. Resolve any unsupported
fixture check before starting; there is no implied exception to a required
check. The owner observes UEFN without unrelated editing during the short call
sequence. These fixture requirements add no endpoint calls.

The **actual client**, not a direct `client.py` harness or unit stub, must:

1. Initialize the MCP connection to `mcp_server.py` over its normal stdio path
   and enumerate its tools. This is Toolbelt's server, not Epic's official MCP.
2. Call `ping`, `list_toolbelt_tools`,
   `describe_toolbelt_tool("mcp_status")`, and
   `run_toolbelt_tool("mcp_status")`. Confirm authenticated queued transport
   and `execute_python_enabled: false`; do not infer authentication from a
   successful unauthenticated request or merely from tool registration.
3. Call `get_all_actors` and identify exactly one actor by its recorded path.
   Save the returned location, rotation, and scale as the baseline.
4. Call `set_actor_transform` once with that exact path and approved location.
   A separate `get_all_actors` call must confirm the target and unchanged
   rotation/scale; the owner also checks the actor in the editor.
5. Restore the original location once and independently re-read all transform
   fields. Compare numeric values with any representation tolerance explicitly
   agreed before the run, not by claiming JSON is byte-identical.

No additional tool execution, save command, generic batch, arbitrary Python,
Launch Session, Push Changes, or publishing is in scope. Record calls and
outcomes, but never bearer values, authorization headers, session identifiers,
or unredacted personal paths. Normal code may consume the handoff; agents must
not print its contents. Record credential discovery and rotation only through
redacted observations or existing tests.

On a timeout, UNKNOWN, disconnect, unexpected mutation, or ambiguous actor
identity, stop automatic calls. Do not retry or automatically restore a possibly
still-running mutation. The owner decides state inspection and recovery under
a separately bounded instruction. A failed or incomplete run is evidence,
not permission to repair code or repeat the run live.

Cleanup stops the local bridge, closes the client connection, and verifies
listener shutdown and handoff removal. Preserve the disposable project for
inspection; deleting it is not implicit. Record saves separately from in-memory
transform restoration, and do not claim persistent project rollback.

Acceptance requires independent review of each stage as MET, NOT MET, or NOT
TESTED, with the exact host/build/package identities. A negative result may be
accepted as a diagnostic result, but cannot support a compatibility claim.

## Session B Bounded reliability corrections

Session B requires accepted Session A evidence and a separate owner-authorized
file/test plan. An unexpected integration defect needs its own bounded amendment;
the words "fix integration" do not authorize an open-ended transport rewrite.

Proposed corrections are:

- Handle `ConnectionAbortedError` narrowly alongside the existing broken-pipe
  and reset cases during response-body writes/flushes. Test write and flush
  failures and a healthy response. Unrelated exceptions must still surface.
  A lost reply must remain UNKNOWN; this changes neither retry policy nor
  execution guarantees.
- Correct the complete dashboard/menu claims about any MCP-compatible agent,
  auto-connection, and running all registered tools. Describe configured access
  and local-only lifecycle exclusions; name a tested host/build only after
  accepted live evidence. Do not change layout or add capabilities.
- Align setup documentation with the tested client configuration and remaining
  evidence limits. Close the deferred `.MCP.json` case-variant test gap, preserving
  missing-Git and parent-repository protections. Make historical security tag
  wording range-specific and soften the remaining universal README claims.

Proposed maximum product scope is
`Content/Python/UEFN_Toolbelt/tools/mcp_bridge.py`,
`Content/Python/UEFN_Toolbelt/dashboard_pyside6.py`,
`Content/Python/UEFN_Toolbelt/menu.py`, `tests/test_mcp_security.py`,
`tests/test_repo_integrity.py`, `README.md`, `SECURITY.md`,
`.claude/mcp_reference.md`, `docs/OFFICIAL_MCP_AND_TOOLBELT.md`, and a new
unreleased entry in `docs/CHANGELOG.md`. The owner-approved Session B plan must
narrow this list to files actually needed. Do not edit historical records or
the released 2.5.0 notes. No version change is proposed.

Run affected tests and static gates on final uncommitted content. Damage probes
must show the new tests catch the intended defects. Leave all work uncommitted
for independent review; apply only authorized corrections before Session C.

## Session C Live acceptance of the corrections

Before the Session C gate, determine whether the changed menu and its tooltip
can be observed on the actual build and resolve the acceptance plan with the
owner. The README records the menu as non-rendering; do not assume it is visible
on a later build. If unavailable, record its live wording inspection as NOT
TESTED, not a pass. Any alternate acceptance method requires an explicitly
owner-approved plan; this observation authorizes neither menu repair nor a
live-verification exemption.

After independent acceptance of Session B and separate owner authorization,
deploy exactly the reviewed content and fully restart UEFN. Repeat the short
Session A workflow through Claude Code, re-recording actual versions and file
identities. Inspect all changed dashboard wording and any visible changed menu
wording in the editor, preserving the unavailable-menu limit above.

Offline tests may force the disconnect exception; a healthy live request after
a disconnect is only live recovery evidence if that disconnect actually
occurred. Do not manufacture an editor stall or claim the exception branch was
tested live when only a unit test exercised it.

Run one complete offline suite on final product/test content, plus the required
static gates. Use actual Git checkout coverage for tracked-file tests; disclose
skips and platform differences. CI belongs to the exact commit it tested, not
future content. Any `Content/Python` commit follows the repository's accepted
live-verification rule and records its actual limits; this proposal grants no
exemption.

Deliver a concise redacted evidence ledger, raw evidence needed to support it,
and one checksum manifest. Separate offline checks, owner observations, actual
MCP-host calls, and CI. An accepted public summary may state only the tested
host/build, calls, and outcomes. It proves neither all 362 tools nor exactly-once
execution, and makes no Epic-versus-Toolbelt comparison.

## Process discipline and exclusions

Record setup time, owner interruptions, failed attempts, and test durations as
ordinary notes so the next process-improvement proposal has real bottlenecks.
Do not build another benchmark or expand this order into a checker/test-system
redesign. Reuse unchanged evidence only when its inputs are bound to the current
content; rerun the checks affected by an edit. Do not repeat full suites for
prose-only corrections without a concrete reason or stricter repository rule.

Keep one implementer and an independent reviewer per deliverable. Use the
existing mandatory gates, not extra rehearsal/review loops without a specific
risk they test. This is a proposed working discipline, not an adopted policy
amendment and not authority to omit existing gates.

Other tools, performance rankings, official-MCP integration, WO-006 resumption,
project recovery, modal detection, heartbeat, timeout redesign, automatic retries,
trust-boundary weakening, broad type-checking work, dependency upgrades, version
selection, tag/Release changes, metadata, social posting, and scratch cleanup
are excluded. A future process-speed pilot and broader tool coverage work need
separate proposals.

## Decision locks and next gate

The owner reserves proposal adoption and admission, issuance, session starts,
the client/project/fixture/target choices, live start, any unexpected repair,
recovery, exact commits, pushes, completion, and any later release decision.
Review acceptance never substitutes for these decisions.

NEXT GATE: independent review of the proposal-admission deliverable.
Issuance/session enforcement requires its own file/test plan, independent
review, and separate owner authorization. No session is authorized, and
this proposal grants no review, implementation, commit, or push authority.
