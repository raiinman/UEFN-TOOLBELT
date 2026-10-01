# WO-006 — Official MCP Versus Toolbelt Benchmark

STATUS: ISSUED

AUTHORIZATION: ISSUED — SESSION B AUTHORIZED FOR OWNER-OPERATED LIVE MEASUREMENT ONLY

OWNER: Ocean Bennett

PRIORITY: P2

BASELINE: `f9354feaf4ab072c9941ab4d6ec8337395ce18a0`

ISSUANCE_COMMIT: `0c0bf26191ee953c7a27237109b4a91a4db97275`

ISSUANCE_CI_WORKFLOW: `36743995194`

ISSUANCE_CI_JOB: `109985389182` — Lint, types, tests

SESSION_A_AUTHORIZATION_COMMIT: `d46a30ed9de54ec01536d132e1032fcf762fa3c7`

SESSION_A_AUTHORIZATION_CI_WORKFLOW: `36756889729`

SESSION_A_AUTHORIZATION_CI_JOB: `110029304446` — Lint, types, tests

SESSION_B_AUTHORIZATION_COMMIT: `8667b0e0ef78d504586d710984ef1a1fef7263b2`

SESSION_B_AUTHORIZATION_CI_WORKFLOW: `36801338578`

SESSION_B_AUTHORIZATION_CI_JOB: `110176132684` — Lint, types, tests

## Issuance basis

The independently accepted revision of this mandate was committed as
`0c0bf26191ee953c7a27237109b4a91a4db97275`; [CI workflow
`36743995194`](https://github.com/undergroundrap/UEFN-TOOLBELT/actions/runs/36743995194)
completed successfully, including required job
[`109985389182` — Lint, types, tests](https://github.com/undergroundrap/UEFN-TOOLBELT/actions/runs/36743995194/job/109985389182).
Those identify the accepted proposal, not the later commit that records this
issuance. The planning baseline above is preserved unchanged.

Issuance alone grants no implementation authority. A session becomes
implementable only when the owner names it in root `WORKORDER.md`. Four
optional clarifications from the delta review of revision 3 are left to the
review of Session A's `plan.md`, and issuance does not change the accepted
benchmark design.
The four items for that review are the triggering pair's outcome after a
failed barrier, classification of unsupported protocol versions or
capabilities, timeouts for notifications/initialized and session DELETE, and
matching command responses among other SSE messages.

## Session A authorization basis

Session A is authorized for the offline design and harness only under the
current root `WORKORDER.md` gate alone. The recorded basis is commit
`d46a30ed9de54ec01536d132e1032fcf762fa3c7`; [CI workflow
`36756889729`](https://github.com/undergroundrap/UEFN-TOOLBELT/actions/runs/36756889729)
completed successfully, including required job
[`110029304446` — Lint, types, tests](https://github.com/undergroundrap/UEFN-TOOLBELT/actions/runs/36756889729/job/110029304446).
That commit and its CI are evidence for this issued mandate; they establish no
harness implementation and no test result.

This gate covers exactly the scope in "Proposed Session A — offline design and
harness" below, unchanged: `harness.py` and the data-only `config.json`,
`analysis.py` and `plan.md`, the synthetic results and summary, and testing
against local stubs, with the artifacts and their SHA-256 hashes kept in the
owner's private evidence folder. Session A changes no repository file. The
four clarifications recorded under "Issuance basis" remain questions for
`plan.md` to settle and for its review to examine; this gate decides none of
them. Session A ends with its artifacts held for independent review. It opens
no deploy, editor launch, bridge startup, MCP call, connection to a real
editor endpoint, live measurement, commit, or push, and Session B stays
closed. The planning baseline and the issuance evidence above are preserved
unchanged, and neither is the Session A basis.

## Session A acceptance record

The owner accepted Session A's private offline artifacts after independent
review, as offline preparation only and not as proof of live compatibility.
The accepted harness package is identified by its `SHA256SUMS` digest
`f17a44a477b2fb2d3d347a75232c7076516ce110308aeb25c0efefad90dff3f8`, and its
preserved independent review by the `SHA256SUMS` digest
`a856bdfff88565831905b0e1fcd77862e408b0eb704774ac1631da9225ac94c1`; both are
kept in the owner's private evidence folder. The first review required fixes,
the second revision made them, and the review of that revision accepted it
with its limitations disclosed. `plan.md` settles the four clarifications
recorded under "Issuance basis", and the first review examined them.

The harness and its stub tests ran offline on the owner's Windows machine
only. They have never run in GitHub CI, and no repository commit or CI run
attests to them. Session A changed no repository file, made no live contact,
and took no measurement. Session A is closed, and its authorization basis
above is kept verbatim as the record of that gate.

## Session B authorization basis

Session B is authorized for owner-operated live measurement only under the
current root `WORKORDER.md` gate alone. The recorded basis is commit
`8667b0e0ef78d504586d710984ef1a1fef7263b2`; [CI workflow
`36801338578`](https://github.com/undergroundrap/UEFN-TOOLBELT/actions/runs/36801338578)
completed successfully, including required job
[`110176132684` — Lint, types, tests](https://github.com/undergroundrap/UEFN-TOOLBELT/actions/runs/36801338578/job/110176132684).
That CI tested the repository's checker and tests at that commit. It did not
run the private harness, and it establishes no live result.

This gate covers exactly the scope in "Proposed Session B — owner-operated
live measurement" below, unchanged, together with the operator procedure in
the accepted `plan.md`. The owner operates UEFN and performs every owner check
and attestation. The harness runs only after the owner's separate, explicit
instruction to begin the live run, invoked by the owner or by the agent under
the owner's direct supervision.

The run uses the accepted harness files unchanged, each verified against the
accepted package's `SHA256SUMS` before use, and `client.py` unchanged from the
repository at the base commit above. The data-only configuration is filled
from live `describe_toolset` output in a separate live copy, recorded with its
SHA-256; the accepted package's stub configuration and every other file stay
unchanged. The run uses the verified Python 3.13.5 interpreter.

Actual response classes and measured wall times are preserved. An actual
Toolbelt timeout remains UNKNOWN and follows the abort and barrier rules. The
Toolbelt client applies its 10-second timeout to each socket operation, not to
the whole call, so a confirmed response can take longer than 10 seconds. Any
such response keeps its response class, is flagged explicitly wherever the
results are reported, and is never presented as meeting a hard 10-second
whole-call deadline. The official client enforces a whole-call deadline with a
watchdog whose overhead falls inside the official timing window only. Both
asymmetries are disclosed with the results, and no estimated constant is
subtracted.

The owner accepted the harness's recorded limitations for this run, with no
further harness revision. A timed-out call is not cancelled and may still act.
SSE resumption, server-initiated requests, and unsupported protocol versions
are not implemented and end their pair HARNESS-LIMITED. Discovery matches tool
names by substring, and the confirmation calls back it up. Toolbelt
exclusivity rests on the owner's attestation, because a caller in lockstep
with the harness cannot be detected. A harness programming defect stops the
run, and its record can then show the in-flight slot as NOT ATTEMPTED or, late
in the run, lack the closing footer; a harness `ValueError` inside the official
exchange reads conservatively as UNKNOWN. The stub tests ran on Windows only,
against stubs that are not Epic's server.

Session B ends with its private artifacts held for independent review. It
opens no code change, fallback, emulation, policy change, live repair, commit,
or push. A runtime defect, or any apparent need to change bridge, client,
transport, harness, or policy code, stops the session for a new owner
decision. The evidence-recording transition, WO-006 completion, and WO-007
remain closed. The planning baseline, the issuance evidence, and the Session A
authorization evidence above are preserved unchanged, and none of them is the
Session B basis.

## Revision provenance

First proposed as a sketch at planning baseline
`6b8ffb2b2d672812f8699af2c22f92c19708f29b` and preserved in commit
`318c28fa08bfef032280bad9b76eab7cd81f626d`, kept here as historical
provenance. Revision 1 was prepared at
`f9354feaf4ab072c9941ab4d6ec8337395ce18a0` after the 2026-09-30 pre-issuance
review, revision 2 at the same commit after the focused re-review of
revision 1, and revision 3 at the same commit after the delta review of
revision 2. They record the owner's planning choices and decisions of that
date and the corrections those reviews required. Repository facts below were
read at that commit; facts read from Epic's installed plugin source are marked
as such.

## Problem

An agent can reach the editor through two loopback surfaces: Epic's official
UEFN MCP server, with its own toolsets, and Toolbelt's custom bridge. Their
per-call cost has never been compared on an operation both can perform, under
controlled conditions. The timings observed during the 2026-08-24 audit mixed
launch, modal, compile, and warm-state effects and are not a benchmark.

Two different things are kept apart:

- **Epic's own tools.** The official server lists its own toolsets, including
  the `editor_toolset` actor, scene, and asset tools (2026-08-24 audit,
  "Official MCP inventory"). Their names and descriptions are preserved; their
  live signatures were never captured.
- **Toolbelt's toolset through Epic's server.** WO-002 recorded that external
  exposure as `failed`, bounded by `UE::ValkyrieToolset::ToolsetPolicy`. That
  result says nothing about comparing Epic's own tools with Toolbelt's bridge,
  and this work order does not reopen it.

The one question this benchmark answers: for one read-only operation and one
reversible mutation that both surfaces genuinely support, is the
client-observed per-call round trip materially different on this machine and
this editor build?

## Owner planning choices (2026-09-30)

1. The comparison is the smallest useful one: asset existence, and a
   reversible transform on one pre-placed `TOOL_TEST` fixture actor.
2. "Toolbelt" means `client.py` direct HTTP to the custom bridge. Results
   describe that client path only; they do not measure MCP-host or stdio
   integration through `mcp_server.py`.
3. Excluded: session launch, Verse push, create/delete loops, p95, automated
   frame-stall or modal metrics, and first-connection measurements.
4. Live measurement is a separate, later owner decision.

## Current transport — decision lock

- Toolbelt's bridge has one dispatch mode, `authenticated_queued`: an
  authenticated same-user loopback POST is queued and executed on the editor
  thread from a Slate tick. If queued dispatch cannot register, the listener
  fails closed and its mode is `unavailable` (`mcp_bridge.py` lines 92-108 and
  1065-1142). There is no direct or unqueued fallback, and remote Python was
  removed under WO-001.
- The benchmark uses that mode as it is. It adds, re-enables, and uses no
  fallback, unqueued path, raw-Python path, or console or CVar emulation, and
  makes no change to Epic's `ToolsetPolicy`.
- No bridge, client, transport, test, or Epic-policy code changes under this
  work order. The accepted WO-001 security controls, and the WO-004 client
  outcome semantics, direct loopback transport, and no-automatic-retry
  guidance, apply unchanged.
- The official surface is reached as WO-002 Session B reached it: JSON-RPC over
  streamable HTTP at the official loopback endpoint, through the top-level
  `call_tool(tool_name, toolset_name, arguments)`.

## Official client protocol — decision lock

The harness's official client follows the MCP streamable-HTTP lifecycle, with
no change to either measured transport:

- an `initialize` request, then the `notifications/initialized` notification;
  both are untimed;
- the negotiated protocol version sent as `MCP-Protocol-Version` on every later
  request, and the `Mcp-Session-Id` returned by `initialize`, when one is
  issued, sent on every later request;
- `Accept: application/json, text/event-stream`, with the response parsed as
  either a JSON body or an SSE stream, and the JSON-RPC response matched to its
  request `id`;
- a direct loopback opener that ignores proxy settings, follows no redirect,
  and makes one attempt per call;
- the endpoint discovered from the running editor at the time of the run and
  recorded. `http://127.0.0.1:8000/mcp` (WO-002 Session B evidence) is
  historical only;
- at the end, the official session closed with an HTTP `DELETE` carrying its
  session id, when one was issued;
- every `tools/call` response validated and correlated under JSON-RPC 2.0
  rules: `jsonrpc` is `"2.0"`, the `id` equals the request's, and exactly one
  of `result` or `error` is present.

Lifecycle messages are not command calls. `initialize`, the
`notifications/initialized` notification, and the closing `DELETE` are
recorded with the role `lifecycle`, their HTTP status, and whether they did
what the lifecycle requires; the command response classes below are never
applied to them. A notification's legitimate acknowledgment is `202 Accepted`
with no body, and a `DELETE` may be answered with any 2xx, or with `405` when
the server does not let clients end sessions; both are recorded as they are. A
failed `initialize` or initialized notification ends the run before any
confirmation, and each pair is then recorded ABORTED with that reason. The
closing `DELETE` affects cleanup only, never a pair outcome.

WO-002 Session B evidence records the requested protocol `2025-03-26` and the
negotiated `2025-11-25`, and no response headers or SSE use, so the stubs in
Session A exercise both response modes.

## Candidate pairs — unconfirmed

These pairs are named from source, not from live evidence. Each official
signature below was read from Epic's installed `editor_toolset` plugin source on
this machine
(`Engine/Plugins/Experimental/Toolsets/EditorToolset/Content/Python/editor_toolset/toolsets/`).
Installed source is not the exposed surface: the installed package holds
modules that the live 42.00 `list_toolsets` did not expose.

| Pair | Official (installed source) | Toolbelt bridge |
|---|---|---|
| Asset existence, read-only | `AssetTools.exists(path)` in `asset.py` | `does_asset_exist(asset_path)`, `mcp_bridge.py` line 606 |
| Transform, then restore | `ActorTools.set_actor_transform(actor, xform, worldspace)` in `actor.py`; re-read with `ActorTools.get_actor_transform(actor)` | `set_actor_transform(actor_path, location, rotation, scale)`, `mcp_bridge.py` line 490; re-read with `get_all_actors(class_filter)`, line 394, which returns each actor's location, rotation, and scale |

Only `does_asset_exist` lacks a public `ToolbeltClient` method, so the harness
calls the client's unchanged `_send(command, params, timeout)` path for it. The
set uses the public `set_actor_transform` method and the re-read the public
`get_all_actors(class_filter)` method (`client.py` line 459). Both public
methods return a default when a key is missing (`.get("actor", {})`,
`.get("actors", [])`), so a result without the expected fields, or a re-read
without exactly one entry for the fixture, is an unexpected shape.

### Mutation target — decision lock

Each set, on both surfaces, confirmation and warm-up included, applies one
explicit world-space target, recorded before any call and identical for both
surfaces: the recorded original location plus (100, 0, 0) cm, with the
recorded original rotation and scale. Every set passes the full transform —
location, rotation, and scale — never a partial one. The target is fixed before
any live call and never changed after data is seen, and every set is followed
by the restoration and verification below. This planning choice permits no
live action.

### Fixture — decision lock

One disposable `TOOL_TEST` level with exactly one fixture: an unparented,
uniquely labelled, unlocked, non-Blueprint `StaticMeshActor` with physics
simulation disabled. Physics simulation is an owner check in the editor's
Details panel, recorded as such: UEFN sandboxes reads of the simulate-physics
flag from Python (`docs/UEFN_QUIRKS.md` Quirk #34), so no Python read of it is
claimed. Its label, path, and original transform are recorded before any
call. The asset existence pair uses `/Engine/BasicShapes/Cube`.
These constraints keep both setters on the plain world-space path: the
official setter compiles Blueprint actors, treats parented actors relative to
their parent, and refuses non-editable ones, and the bridge takes the first
actor whose path or label matches.

### Observed differences, and what disqualifies a pair

Recorded as observations, never normalized, and not disqualifying unless they
change the agreed postcondition:

- the official setter calls `root.modify()` on the root component; whether an
  undo entry results depends on its registry wrapper and is not verified;
- the official setter sets one transform with teleport enabled; the bridge
  sets location, rotation, and scale separately with sweep and teleport
  disabled;
- the official `exists` may also report folders; the bridge reports assets
  only. The pair uses an asset path, where both answer the same question;
- the bridge finds its actor by a linear scan; the official tool takes an actor
  reference.

Disqualifying: a different postcondition for the same input, any asset save,
compile, or other asset write, and any dialog raised by the call.

### Confirmation, before any timing

Each pair is confirmed on the running build:

- `describe_toolset` returns the official tool with a name, parameters, and
  identifier form the data-only configuration below can express;
- one untimed call per surface produces the same postcondition: the same
  existence answer for the same asset, or the recorded mutation target, re-read
  from the fixture within the tolerances below before its restore;
- a mismatch, absence, or policy refusal makes the pair NOT COMPARABLE. It is
  never bridged by emulation, a proxy, or a policy change.

## Harness boundary — decision lock

Session A builds the harness against local stubs, before live signatures are
known. The harness takes a data-only configuration file that Session B may
fill from the live `describe_toolset` output and record as evidence: official
toolset and tool names, parameter names, the actor-identifier encoding, and
the transform and rotation shapes for each surface. Session B changes no code.
If a surface needs anything the configuration cannot express, the pair ends
HARNESS-LIMITED, a limitation of this harness and not a finding about either
surface, and any code change returns to Session A under a new owner gate.

## Outcomes — decision lock

### Response classes

Every command call the harness makes, whatever its role, has exactly one
response class: SUCCESS, REJECTED, REPORTED FAILURE, or UNKNOWN. Lifecycle
messages are recorded separately (see "Official client protocol"). Each
surface's rules are applied in the order listed, and the first that matches
decides the class, so the branches are mutually exclusive.

Toolbelt, in this order. The client's exception hierarchy makes the order
matter: `OutcomeUnknown` subclasses `ToolbeltError`, and `CommandTimeout`
subclasses `OutcomeUnknown`.

1. `OutcomeUnknown`, including `CommandTimeout` → UNKNOWN.
2. `AuthenticationError` or `NotConnected` → REJECTED, the two cases where
   the client establishes that no request was dispatched.
3. Any remaining `ToolbeltError` → REPORTED FAILURE. This includes the
   bridge's non-401 pre-queue rejections, which the client does not
   distinguish, so they are treated conservatively as reported failures.
4. Any other exception → UNKNOWN.
5. A returned result without the expected fields and types → UNKNOWN.
6. A well-formed result whose value contradicts the confirmed postcondition →
   REPORTED FAILURE.
7. Otherwise → SUCCESS.

Official, for each `tools/call` command request, in this order:

1. The connection was refused, or no request was sent → REJECTED.
2. A timeout, a reset or lost connection, or a truncated or unparseable JSON
   or SSE body → UNKNOWN.
3. Any HTTP status other than `200` → UNKNOWN, regardless of its body.
4. An envelope that fails JSON-RPC validation or correlation (see "Official
   client protocol"), or any other malformed or unexpected envelope → UNKNOWN.
5. A valid JSON-RPC `error` with code `-32700`, `-32600`, `-32601`, or
   `-32602` → REPORTED FAILURE; any other code → UNKNOWN.
6. A `result` with `isError: true` → REPORTED FAILURE.
7. A `result` whose tool payload does not decode to the expected shape →
   UNKNOWN.
8. A well-formed payload whose value contradicts the confirmed postcondition →
   REPORTED FAILURE.
9. Otherwise → SUCCESS. A JSON-RPC `result` alone is never SUCCESS.

No response class claims that nothing executed, except REJECTED, which rests
on evidence that no request was dispatched. A REPORTED FAILURE, on either
surface and from any error code, does not show the absence of side effects.

### Call records

Every call is recorded with a global sequence number, its role (lifecycle,
discovery, confirmation, warm-up, measured, barrier, restore, or re-read),
surface, operation, round, response class (or, for a lifecycle message, its
lifecycle result), and, for warm-up and measured calls, its disposition and
wall time. Nothing attempted is left out of the record.

### Warm-up and measured dispositions

Every scheduled warm-up and measured slot has exactly one disposition, decided
in this order:

1. **NOT ATTEMPTED:** a scheduled slot left after the pair's timing ended.
2. **VOID:** operator-observed interference, such as a dialog, a focus change,
   or a visible stall, noted against that attempt. An annotation, not modal
   diagnosis. VOID takes precedence over the response class for disposition
   counts.
3. **UNKNOWN:** response class UNKNOWN.
4. **FAILED:** response class REJECTED or REPORTED FAILURE.
5. **VALID:** response class SUCCESS; the only retained samples.

The response class is recorded separately and is never replaced by the
disposition: a VOID attempt whose class is UNKNOWN still triggers every
UNKNOWN, barrier, and abort rule below. Warm-up dispositions are counted but
never retained. No slot is retried, replaced, or padded.

### Pair outcomes

Each pair ends in exactly one outcome, taken in this order of precedence:

1. **ABORTED.** An UNKNOWN on any mutating call, a restoration that cannot be
   verified, or quiescence that cannot be established (see "Unknown mutation
   outcomes"). Pairs the run never reached are also ABORTED, with that reason.
2. **HARNESS-LIMITED.** See "Harness boundary".
3. **NOT COMPARABLE.** Confirmation failed.
4. **MEASURED.** Both surfaces' cells hold 30 VALID measured attempts out of 30
   scheduled, and every mutation was restored and verified.
5. **INCOMPLETE.** Confirmation succeeded and nothing above applies, but at
   least one cell has fewer than 30 VALID attempts.

If the owner declines the live run, WO-006 records **NOT RUN** with that
decision. NOT RUN claims no technical incompatibility.

## Unknown mutation outcomes — decision lock

An UNKNOWN on any mutating call, whether confirmation, warm-up, measured, or
restore, ends all benchmarking in that live run. Reconciliation afterwards is
cleanup only; it never permits further timed samples. An immediate state read
does not prove that a delayed execution has finished.

- **Toolbelt.** Every accepted request is queued before its handler waits
  (`mcp_bridge.py` lines 930-945), and one tick consumer runs queued commands to
  completion in FIFO order (lines 1001-1016). Stopping the listener drains the
  queue unexecuted (line 1148). A later Toolbelt request that
  returns SUCCESS therefore shows that every earlier-enqueued command has run,
  provided three assumptions hold and are recorded: the same listener
  instance, with no `mcp_stop` or `mcp_restart` between the two requests;
  enqueue order following send order; and the harness as the only caller. The
  evidence that will support those assumptions is defined in Session A's
  `plan.md` (see "Proposed Session A"); none is claimed here. The barrier is an
  untimed `ping` sent after the UNKNOWN through the client's unchanged
  `_send("ping", None, 45.0)`, because the public `ping()` method takes no
  timeout. The listener serves one request at a time and may still be waiting
  out the earlier request's 30-second deadline, so the barrier's timeout is 45
  seconds. After a successful barrier, the fixture is re-read, restored to its
  recorded original, and re-read to verify.
- **Official.** No equivalent barrier is known, and none is assumed. The
  harness makes no further mutation. The run records OWNER RECOVERY REQUIRED:
  the owner inspects and restores the fixture, and the record says so.

If the Toolbelt assumptions cannot be verified, or its barrier does not
return SUCCESS, the same rule applies: no further mutation, and OWNER RECOVERY
REQUIRED. Restoration is never claimed without a verifying re-read.

A Toolbelt UNKNOWN on a read-only call ends that pair's timing (see
"Measurement") and does not by itself end the run. It still leaves a command
possibly queued, so the same untimed barrier runs before another pair is
scheduled. The barrier is a separate synchronization call, never a retry of the
UNKNOWN call and never a replacement sample. If the barrier cannot establish
quiescence, because it does not return SUCCESS or its assumptions cannot be
supported, the run stops, the pairs not yet reached are ABORTED with that
reason, and the record says OWNER RECOVERY REQUIRED.

## Restoration — decision lock

- Every mutating call, confirmation and warm-up included, is followed by an
  untimed restore to the recorded original transform and an untimed re-read,
  both on the surface that made the set. The verified re-read is the
  precondition for the next set.
- A REPORTED FAILURE on a set is still followed by a restore and a re-read,
  because a reported failure does not show that nothing executed.
- A restore or re-read that does not verify ends the run as ABORTED, with
  OWNER RECOVERY REQUIRED.
- At the end, both surfaces re-read the fixture, and both must match the
  recorded original.
- Tolerances, fixed before any live call and never changed after data is
  seen: location within 0.01 cm on each axis; scale within 0.0001 on each axis;
  rotation compared as unit quaternions, converted from each surface's recorded
  representation, within 0.01 degrees. The proposed angular metric is
  2·acos(|q1·q2|). The conversion convention for each surface and the metric
  are verified in Session A's `plan.md` before any live gate; neither is
  claimed verified here.
- A restored transform is not a clean package and not unchanged undo history:
  both setters leave the level dirty. Nothing is saved at any point, and the
  save prompt is declined when the disposable project is closed. The record
  says the level was left dirty and unsaved.

## Measurement — decision lock

- **Timing window.** `time.perf_counter()` around the single client call, and
  nothing else. For Toolbelt, the window includes the client's per-call read
  of the session handoff file, its request, and its reply parsing and
  classification; it also contains the bridge's fixed transport artefacts, a
  20 ms reply poll (`POLL_INTERVAL_SEC`), tick-gated draining
  (`TICK_BATCH_LIMIT`), and a new connection per request. For the official
  side, the window includes encoding, the request, and JSON or SSE parsing and
  classification. Record writing, restores, re-reads, and barrier calls are
  outside every window.
- **Timeout.** Every confirmation, warm-up, measured, restore, and re-read
  call uses an explicit 10-second client timeout on both surfaces, well under
  the bridge's 30-second deadline (`HTTP_TIMEOUT_SEC`). On the Toolbelt side
  that is `ToolbeltClient(timeout=10.0)`, which the public methods and the
  `does_asset_exist` `_send` call inherit; no timeout parameter is passed to a
  public method that has none. Only the Toolbelt barrier uses 45 seconds, as
  `_send("ping", None, 45.0)`. On the official side, `initialize`,
  `list_toolsets`, and `describe_toolset` are untimed and use a 30-second
  timeout; `tools/call` uses 10 seconds. A call that reaches its timeout is
  UNKNOWN. No automatic retry on either surface.
- **Server timing.** Toolbelt's `history` carries a handler `elapsed_ms` with
  no request identity; the official side exposes no known equivalent. No
  handler-only comparison is claimed, and the asymmetry is recorded.
- **Cells.** One cell per operation and surface: five scheduled warm-up
  attempts, then 30 scheduled measured attempts.
- **Order.** The asset existence pair first, then the transform pair; each
  pair's confirmation comes before its warm-ups. Warm-ups and measured
  attempts run in rounds, one call per surface per round, sequential and never
  concurrent, because the bridge serves one request at a time. The surface
  that goes first alternates by round: official first in even rounds, Toolbelt
  first in odd rounds, counted from round 0 for warm-ups and again for measured
  rounds. In the transform pair, each set is followed by its own restore and
  re-read before the other surface's call.
- **Warm-ups.** Warm-ups never count toward n. A warm-up that fails is recorded
  and not replaced, and the measured rounds still follow. An UNKNOWN on a
  mutating warm-up ends the run as ABORTED. An UNKNOWN on a read-only warm-up
  ends that pair's timing.
- **Early end.** An UNKNOWN on a read-only warm-up or measured attempt ends
  that pair's timing: every remaining warm-up and measured slot of both cells
  is NOT ATTEMPTED, and the pair is INCOMPLETE unless something above takes
  precedence. A Toolbelt UNKNOWN is followed by the barrier in "Unknown
  mutation outcomes" before another pair is scheduled.
- **Report.** Every attempted call, raw. Per cell, for warm-ups and measured
  slots separately: scheduled, attempted, NOT ATTEMPTED, VALID, FAILED,
  UNKNOWN, and VOID counts, where scheduled equals attempted plus NOT
  ATTEMPTED, and attempted equals VALID plus FAILED plus UNKNOWN plus VOID;
  with it, the count of attempted slots by response class. Latency is
  summarized over VALID measured attempts only: n, minimum, median (p50), and
  maximum. The median's 95%
  interval is the distribution-free order-statistic interval, the 10th and 21st
  of 30 ordered values (about 95.7% coverage), reported only when n is 30. It
  assumes independent, identically distributed observations within a cell;
  alternation reduces but does not remove time drift, so the interval is
  descriptive. INCOMPLETE cells keep their raw results and, when there are
  VALID attempts, descriptive statistics without an interval. No p95, no pooled
  or cross-operation averages, and no claim that either surface is better in
  general. Every result is scoped to these client paths, these operations, this
  machine, and this build.

## Conditions held constant and recorded

- One editor session on one machine, for both surfaces and every cell.
- The editor in the foreground and focused: an unfocused editor throttles
  ticks (WO-004 Session A record, Probe A). The background-CPU setting is
  recorded and not changed during the run.
- The running build, read from the editor log at the time of the run.
  `++Fortnite+Release-42.20-CL-58011042` (WO-004 Session C, 2026-09-28) is
  historical evidence only.
- The same fixture state for both surfaces, and no other client connected to
  either surface.
- Direct loopback with no proxy, for both clients.

## Use of WO-005

WO-005 source categories describe registry tools, not bridge commands such as
`set_actor_transform` or `does_asset_exist`, and they establish no live
verification. They are used only to keep flagged tools out: the three
`stubbed-operation` tools are never candidates.

## Proposed Session A — offline design and harness

No live contact: no deploy, editor launch, bridge startup, MCP call, or
connection to the official endpoint. No repository file changes.

| Artifact | Content |
|---|---|
| `harness.py` | Standard library only. The Toolbelt side through `client.py` `ToolbeltClient`; the official side through the client protocol above. Sequential, no retry |
| `config.json` | The data-only configuration, with stub values |
| `analysis.py` | Derives the per-cell counts and summary from the raw JSONL |
| `plan.md` | The confirmation procedure, fixture, ordering, tolerances, stop rules, and record schema |
| `synthetic-results.jsonl`, `synthetic-summary.md` | The analysis run on synthetic data |

The artifacts are kept in the owner's private evidence folder with SHA-256
hashes.

Acceptance, each able to fail:

- the harness runs offline against local stub loopback servers for each
  surface, and classifies every response class, including a JSON-RPC `result`
  with `isError: true`, a mismatched id, an unparseable body, and a timeout;
- stub tests show the Toolbelt order: `CommandTimeout` and `OutcomeUnknown`
  classify as UNKNOWN, not REPORTED FAILURE; `AuthenticationError` and
  `NotConnected` as REJECTED; a plain `ToolbeltError` as REPORTED FAILURE; a
  non-Toolbelt exception and an unexpected result shape as UNKNOWN; and a
  `CommandTimeout` on a mutating call ends the run as ABORTED. No client code
  is changed to make them pass;
- stub tests show the official order: a non-200 status carrying a
  well-formed JSON-RPC body is UNKNOWN; each of `-32700`, `-32600`, `-32601`,
  and `-32602` is REPORTED FAILURE and another code is UNKNOWN; a malformed or
  uncorrelated envelope is UNKNOWN; a well-formed payload with the wrong value
  is REPORTED FAILURE; and a `202` acknowledgment of the initialized
  notification is recorded as a lifecycle result, not classified as a command;
- a stubbed Toolbelt UNKNOWN on a read-only call is followed by the barrier
  before another pair is scheduled, and a failing barrier stops the run with
  OWNER RECOVERY REQUIRED;
- a VOID attempt whose response class is UNKNOWN is counted VOID and still
  triggers the UNKNOWN rules;
- the official stub answers in both JSON and SSE modes, issues a session id,
  and checks that the negotiated protocol and session headers arrive on later
  requests;
- every call is recorded with its sequence number and role, and the per-cell
  counts account for every scheduled warm-up and measured slot;
- a stubbed UNKNOWN on a mutating call ends the run as ABORTED, and a stubbed
  UNKNOWN on a read-only call ends that pair's timing as INCOMPLETE;
- the analysis reproduces the synthetic summary from the synthetic JSONL,
  including the interval at n = 30 and its absence below 30;
- the plan names every condition above, and no step retries, emulates, or
  touches bridge, client, or policy code;
- the plan states the evidence that will support the Toolbelt barrier's
  assumptions, listener continuity and the harness as the only caller, and how
  the run records it;
- the plan states each surface's rotation-to-quaternion conversion convention
  and the angular metric, and shows them correct on known cases offline;
- the plan states the concrete official protocol details: the protocol version
  requested, the client capabilities sent, how SSE streams are handled,
  including notifications and server-initiated requests on them, and how the
  endpoint is discovered from the running editor.

These last three remain unsettled questions for Session A's `plan.md`.
Nothing in this proposal claims they are settled; they are settled, and
reviewed, before the owner's Session B decision.

Session A ends with its artifacts held for independent review. Commit, push,
and Session B each need a separate owner gate.

## Proposed Session B — owner-operated live measurement

Not authorized by issuance or by Session A; it needs its own owner gate. The
owner operates UEFN.

Prerequisites:

- the disposable `TOOL_TEST` level and fixture above, with the fixture's label,
  path, original transform, and mutation target recorded, physics simulation
  confirmed disabled by the owner in the Details panel, and
  `/Engine/BasicShapes/Cube` present;
- `deploy.bat`, a deployed runtime hash that matches source, and a full editor
  restart;
- the UEFN MCP Toolsets beta flag on, with the Quirk #36 recovery if Toolbelt
  did not load;
- the Toolbelt listener run locally by the owner with `mcp_start`;
- the official endpoint and the running build, read from the editor and
  recorded;
- the data-only configuration filled from live `describe_toolset` output and
  recorded.

Artifacts, kept privately with SHA-256 hashes: the raw JSONL of every call,
the per-cell summary, the configuration, the confirmation calls, the
restoration re-reads, and a redacted run log, with `SHA256SUMS` and
`PROVENANCE` files. Redaction removes user-home paths, bearer and handoff
material, and MCP session identifiers.

Acceptance: each pair ends in exactly one outcome with its evidence; every
mutation is restored and verified, or the record says OWNER RECOVERY REQUIRED;
at the end both surfaces' re-reads match the fixture's recorded original, and
the level is otherwise unchanged apart from being dirty and unsaved.

Cleanup: the official session closed, the harness process confirmed exited,
the Toolbelt listener stopped, the disposable project closed with the save
prompt declined, and the session handoff file absent.

Stop: any runtime defect, or any apparent need to change bridge, client,
transport, or policy code, stops the session for a new owner decision.

## Recording and publication

A later record transition, which needs its own owner gate, adds a sanitized
audit record under `docs/audits/` and its evidence under
`docs/audits/evidence/wo006/`, with the harness preserved as `harness.py.txt`,
following the WO-004 Session C precedent. The record states every result as
scoped to these client paths, these operations, this build, and this machine.

## Exclusions and deferred work

- No performance optimization, and no change to any measured path.
- No comparative or marketing conclusion before independent review.
- No session launch, Verse push, create/delete loops, p95, automated
  frame-stall or modal metrics, or first-connection measurements.
- No measurement of MCP-host or stdio integration.
- Other operations, other builds, and repeated runs are deferred.

WO-007 remains proposed and unauthorized.

## Acceptance criteria

- Each candidate pair ends in exactly one outcome, by the stated precedence,
  with its evidence.
- Every call is recorded with its role and response class; every scheduled
  measured slot has a disposition; nothing is retried, replaced, or padded.
- Every mutation is restored and verified by re-reading state, or the record
  says OWNER RECOVERY REQUIRED.
- The report gives every raw call, the per-cell counts, and the latency summary
  over VALID attempts, with the interval only at n = 30, and no general
  conclusion.
- No bridge, client, transport, test, or Epic-policy code changes.

## Stop boundaries

Owner decisions, each separate, none implying the next: issuing WO-006,
opening Session A, opening Session B, the evidence-recording transition, each
commit, each push, and WO-006 completion. Independent review of each session
comes before its commit decision, and CI runs after each push; neither is an
owner decision, and neither stands in for one. Tagging, GitHub Release
creation, repository metadata changes, branch-protection changes, and social
publication are outside WO-006 and remain unauthorized.

NEXT GATE: owner-operated execution of the accepted Session B scope, after the
owner's separate instruction to begin the live run, ending with its private
artifacts held for independent review. The evidence-recording transition,
commit, push, WO-006 completion, and WO-007 remain closed.
