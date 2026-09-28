# WO-004 — Modal Observability and Human-Safe Blocking

STATUS: ISSUED

AUTHORIZATION: ISSUED — SESSION C AUTHORIZED FOR LIVE ACCEPTANCE ONLY

OWNER: Ocean Bennett

PRIORITY: P1

BASELINE: `0d513f1639cf197707132205f4074d0fe3a750cc`

ISSUANCE_COMMIT: `8444faf340afe47765c43d943200db712880817b`

ISSUANCE_CI_WORKFLOW: `34441169191`

ISSUANCE_CI_JOB: `102756337393` — Lint, types, tests

SESSION_A_AUTHORIZATION_COMMIT: `f9fc7268d63dad92f5dd009bbf20e11477b8f926`

SESSION_A_AUTHORIZATION_CI_WORKFLOW: `34509193110`

SESSION_A_AUTHORIZATION_CI_JOB: `102978793893` — Lint, types, tests

SESSION_A_ACCEPTANCE_COMMIT: `c4c21caa0960c430a4bcfb90cd65ef1edfc1a790`

SESSION_A_ACCEPTANCE_CI_WORKFLOW: `34735715115`

SESSION_A_ACCEPTANCE_CI_JOB: `103666661855` — Lint, types, tests

SESSION_B_AUTHORIZATION_COMMIT: `da846ec36773d673ca9dcab3025ac36555579d0f`

SESSION_B_AUTHORIZATION_CI_WORKFLOW: `36375370541`

SESSION_B_AUTHORIZATION_CI_JOB: `108780005124` — Lint, types, tests

SESSION_C_AUTHORIZATION_COMMIT: `17b5afe3f50bfa3ab882ff362a10eef70750c694`

SESSION_C_AUTHORIZATION_CI_WORKFLOW: `36385787242`

SESSION_C_AUTHORIZATION_CI_JOB: `108810759914` — Lint, types, tests

## Issuance basis

The independently accepted revision of this mandate was committed as
`8444faf340afe47765c43d943200db712880817b`; [CI workflow
`34441169191`](https://github.com/undergroundrap/UEFN-TOOLBELT/actions/runs/34441169191)
completed successfully, including required job
[`102756337393` — Lint, types, tests](https://github.com/undergroundrap/UEFN-TOOLBELT/actions/runs/34441169191/job/102756337393).

Issuance alone grants no implementation authority. A session becomes
implementable only when the owner names it in root `WORKORDER.md`. The
planning baseline above is preserved unchanged; it records the state this
mandate was planned against, not the issuance point.

## Session A authorization basis

Session A is authorized for read-only feasibility planning under the
current root `WORKORDER.md` gate alone. The recorded basis is commit
`f9fc7268d63dad92f5dd009bbf20e11477b8f926`; [CI workflow
`34509193110`](https://github.com/undergroundrap/UEFN-TOOLBELT/actions/runs/34509193110)
completed successfully, including required job
[`102978793893` — Lint, types, tests](https://github.com/undergroundrap/UEFN-TOOLBELT/actions/runs/34509193110/job/102978793893).

This gate covers source and documentation inspection and the drafting of
proposed probes. It opens no live UEFN work: no editor launch, no bridge
start, no official-MCP call, and no level mutation. Every probe this
session specifies needs its own separate owner gate before anyone runs
it. The issuance evidence above is preserved unchanged; the planning
baseline records the state this mandate was planned against, and neither
is the Session A basis.

Session A records its result in [the 2026-09-10 modal-feasibility
record](../../audits/2026-09-10-wo004-session-a-modal-feasibility.md). It is a
declared scan target, and its conclusion is content-pinned in
`tests/test_repo_integrity.py`, so the record can be neither deleted nor
emptied silently.

## Session A decision record

This record is the owner's written Session A decision. It amends the forward
scope of this mandate and leaves its issued history in place: the issuance
basis, the Session A authorization basis, the planning basis, the problem
statement, the transport boundaries, the Session A plan, and the issuance
enforcement record are unchanged.

**Accepted evidence.** The Session A record, including its live Probe A
observations and their evidence directory, was independently accepted,
committed, and pushed as `c4c21caa0960c430a4bcfb90cd65ef1edfc1a790`; [CI
workflow
`34735715115`](https://github.com/undergroundrap/UEFN-TOOLBELT/actions/runs/34735715115)
completed successfully, including required job
[`103666661855` — Lint, types, tests](https://github.com/undergroundrap/UEFN-TOOLBELT/actions/runs/34735715115/job/103666661855).

**Live Probe A provenance.** The Session A authorization basis above opened no
live UEFN work. Live Probe A ran later under a separate owner authorization, in
`TOOL_TEST`, and is recorded in Section 6 of [the Session A
record](../../audits/2026-09-10-wo004-session-a-modal-feasibility.md), with
preserved evidence under `docs/audits/evidence/wo004-probe-a/`. Probes B and C
were not run.

**Accepted findings, bounded.** Python post-tick callback silence was observed
under the recorded conditions. Its cause, any modal diagnosis, and the
operational reliability of a tick heartbeat remain unproven. No bridge command
is served from the HTTP thread, and `_tick_health` is written but never read.

**Decision.** The owner accepts Session A's bounded findings. WO-004's
remaining work is narrowed to client timeout and error semantics, to guidance
that keeps automatic retry absent, and to one narrow client transport
correction: both clients connect directly to their validated loopback endpoint,
bypassing environment and system HTTP proxies for these requests only. The
owner made that transport decision after independent review reproduced proxy
exposure with dummy credentials; it changes neither the bridge nor its
authentication protocol. Modal detection, heartbeat and status endpoints, and
further feasibility probes are deferred.

**What this amends.** "Candidate paths and responsibilities" and "Status
semantics" each gain an amendment note. The Session B and Session C sections
are replaced by their amended versions below. "Inclusions", "Exclusions and
deferred work", "Configurations and fixtures", "Acceptance criteria", "Stop
boundaries", and the next gate are amended to match. The text before this
amendment is preserved in the repository history at
`c4c21caa0960c430a4bcfb90cd65ef1edfc1a790`.

Session A is accepted and complete. At the Session A acceptance gate, Session B
implementation and Session C live testing were not authorized; each required a
separate owner gate recorded in root `WORKORDER.md`.

## Session B authorization basis

At the Session B authorization gate, Session B was authorized for client
outcome semantics only under the root `WORKORDER.md` gate. The recorded basis
is commit `da846ec36773d673ca9dcab3025ac36555579d0f`; [CI workflow
`36375370541`](https://github.com/undergroundrap/UEFN-TOOLBELT/actions/runs/36375370541)
completed successfully, including required job
[`108780005124` — Lint, types, tests](https://github.com/undergroundrap/UEFN-TOOLBELT/actions/runs/36375370541/job/108780005124).

That gate covered exactly the amended scope in "Session B — client outcome
semantics (amended)" below: its candidate file inventory, required contract,
exclusions, and static verification, unchanged. Session B ended with its
worktree uncommitted for independent review. That gate opened no live UEFN
work: no deploy, no editor launch, no bridge start, no MCP call, and no level
mutation. Session C live testing was not authorized at that gate. The
issuance, Session A authorization, and Session A acceptance evidence above are
preserved unchanged, and none of them is the Session B basis.

## Session C authorization basis

Session C is authorized for owner-operated live acceptance only under the
current root `WORKORDER.md` gate alone. The recorded basis is commit
`17b5afe3f50bfa3ab882ff362a10eef70750c694`; [CI workflow
`36385787242`](https://github.com/undergroundrap/UEFN-TOOLBELT/actions/runs/36385787242)
completed successfully, including required job
[`108810759914` — Lint, types, tests](https://github.com/undergroundrap/UEFN-TOOLBELT/actions/runs/36385787242/job/108810759914).

That CI ran on the base commit, which does not contain the Session B
implementation. The implementation is uncommitted, and its evidence is local
checks and independent static review, not CI. On Windows 11 with Python
3.13.5, the full suite gave 1443 passed and 10 skipped; the security tests gave
175 passed on Python 3.13.5 and on Python 3.12.10; and ruff, the drift check,
and the API manifest check were clean. The configured mypy files include
neither client. Two independent static reviews accepted the implementation:
the implementation review and the review of its test and documentation
cleanup. Linux, macOS, Python 3.8 to 3.11, and all live behaviour are untested,
and static acceptance is not live acceptance.

Session C tests exactly this reviewed implementation, identified by its files
in the reviewed snapshot `wo004-session-b-cleanup-2026-09-28`:

- `.claude/mcp_reference.md`: Git blob `75873316c1f0f57037181a4fda2f2cd4365a730d`, SHA-256 `cb55912ec5168d2d46a3631443bc2dcc462f543567142d91b1fdd0b1cb6e5c26`
- `client.py`: Git blob `bfff40e02fa167a0f987a5e066e7bc6f13f8b308`, SHA-256 `c5097f3141b19122b665b0be2a570e13ec642a5d2cc582a6bec717ae25e34850`
- `mcp_server.py`: Git blob `70a88474dc138b5d3915f06a96dffef24c71c993`, SHA-256 `0aa4268491d60f7fbb663da1d3bbcb095997243a51db91357452160b04eed0b3`
- `tests/test_mcp_security.py`: Git blob `34580cb9426f4aeaaa47381cf77d707936e88ffa`, SHA-256 `dd0c2ceaebfb813b371650e10658c98b41958e8d1f5139181ecaf8955cfe6976`

Each Git blob is the line-ending-normalized identity Git would commit; each
SHA-256 is of the reviewed worktree bytes.

This gate covers the owner-operated procedure in "Session C — live acceptance,
owner-operated (amended)" below, unchanged, including its runtime prerequisites
and the updated-editor prerequisite. The owner operates UEFN. Session C changes
no implementation file: a defect found live stops the session and is reported
for a separate owner decision. It opens no commit, push, or WO-004 completion.

## Planning basis

This revision was prepared at `0d513f1639cf197707132205f4074d0fe3a750cc`, on
which CI workflow
[`34434992222`](https://github.com/undergroundrap/UEFN-TOOLBELT/actions/runs/34434992222)
completed successfully, including required job
[`102738086806` — Lint, types, tests](https://github.com/undergroundrap/UEFN-TOOLBELT/actions/runs/34434992222/job/102738086806).

That is planning evidence only. The issuance basis is separate: issuance records
its own commit, workflow, and required job in the root pointer at that gate.

## Problem and accepted evidence

**Observed**, recorded as P1 finding 4 of the
[2026-08-24 UEFN 42.00 audit](../../audits/2026-08-24-uefn-42-official-mcp-audit.md)
(`:274`, with the owner action at `:68`): a Save Content modal blocked an
official queued call for approximately four minutes, and the call resumed
immediately after the owner closed the dialog. The audit states in the same
finding that agentic automation lacks modal observability.

**Inferred, not observed**: that a modal is the general cause of long-pending
operations. One correlated incident establishes that a modal *can* block a
queued call. It does not establish that pending calls are usually
modal-blocked, nor that any modal state is reachable from third-party Python.

**Evidence gap**: the audit records the incident narratively. No log excerpt,
timestamp range, or screenshot is preserved as a citable artifact for that
specific four-minute block. This Work Order does not manufacture one. Session A
records whatever primary evidence still exists, or records its absence.

## Transport boundaries — read before scoping anything

Three distinct surfaces are involved. Conflating them is the main way this Work
Order could produce work that cannot address the recorded incident.

| Surface | What it is | Relationship to the incident |
|---|---|---|
| Epic's official UEFN MCP | Epic's own server and toolsets, `127.0.0.1:8000/mcp` | **The blocked call was here.** Not Toolbelt code. Toolbelt cannot instrument it |
| Toolbelt's custom bridge | `Content/Python/UEFN_Toolbelt/tools/mcp_bridge.py`, in-editor authenticated same-user loopback listener | A *separate* transport. WO-002 recorded Toolbelt is not reachable through Epic's MCP, bounded by `UE::ValkyrieToolset::ToolsetPolicy` |
| Toolbelt client side | `mcp_server.py`, `client.py` | Callers of Toolbelt's bridge only. They observe Toolbelt commands, never official-MCP ones |

**Consequence for scope.** Improving Toolbelt's bridge or client does not
observe, classify, or recover the official-MCP call described in the incident.
Any claim that it does must be rejected in review. What Toolbelt can honestly
offer is (a) better status semantics for *its own* operations, and (b) if and
only if Session A proves it, a read-only editor-state signal the owner or an
agent can consult while *any* surface appears stalled.

## Candidate paths and responsibilities

Identified by source inspection at the baseline. Session B confirms or revises.

| Path | Current responsibility | Candidate change |
|---|---|---|
| `mcp_server.py` (`:190`, `:211`, `:232-236`, `:327`, `:646`) | External bridge client; raises one undifferentiated `TimeoutError` — *"timed out after Ns. The UEFN editor may be blocked. Try a shorter operation."* | Evidence-based status result instead of that single guess |
| `client.py` (`:50-71`, `:145-186`, `:241`, `:265`) | Stdlib client. It **already** separates `NotConnected`, `CommandTimeout`, and `AuthenticationError` (`:171-186`). What is absent is a `queued` or `modal_blocked` outcome and a shared structured result rather than exceptions | Extend to the shared status result; do not rebuild the split that exists |
| `Content/Python/UEFN_Toolbelt/tools/mcp_bridge.py` (`:114`, `:1006-1015`, `:1072`) | In-editor listener; `queue.Queue` handoff drained by `register_slate_post_tick_callback` | Possible read-only status endpoint — subject to the main-thread constraint below |
| `tests/` | Static suites, fake `unreal` via `conftest.py` | Simulated status/regression tests |

**Amendment (Session A decision).** The table above is the planning-time
identification. Session B's inventory is now the exact list in "Session B —
client outcome semantics (amended)": the bridge is unchanged, and no in-editor
status surface or shared status result is in scope.

**Main-thread constraint.** Toolbelt drains its command queue on the Slate
post-tick callback — the same main thread every `unreal.*` call requires. A
modal that blocks the main thread therefore blocks Toolbelt's own sensing on
that thread. Any design that senses modal state from the tick callback is
self-defeating for the exact case it targets. Session A must confront this
directly. A design that cannot report while blocked is not a solution.

## Session A — feasibility, read-only

No implementation. Feasibility settles first, because every later session
depends on its result.

1. Identify candidate supported APIs for editor, window, or modal state by
   read-only source and documentation inspection.
2. Determine whether any candidate is readable **while the main thread is
   blocked**, or whether all sensing shares that thread.
3. Record whatever primary evidence remains for the 2026-08-24 incident, or
   record its absence.
4. Specify the exact owner-operated TOOL_TEST probes the questions above
   require, including any `api_search` or `api_inspect` run against the live
   runtime. Those probes need their own owner gate. This document does not open
   it, and no live UEFN operation happens during Session A planning.

**`unavailable` and `unknown` are valid, complete results.** WO-002 established
that a recorded negative result is an acceptable outcome. If no supported API
exists, or none is readable while blocked, Session A ends with that finding and
the remaining sessions are re-scoped or dropped.

**Explicit decision required.** After Session A the owner decides in writing
whether the next session is re-scoped, dropped, or opened. Every dependent
session stays closed until that decision is recorded, and each one needs its own
owner gate.

**Stop.** Session A ends with its finding recorded. Nothing further follows from
it without a separate owner gate.

## Status semantics — evidence required per outcome

An elapsed timeout is the absence of a reply. It is not evidence of a modal, of
failure, or of anything else. It cannot on its own distinguish a blocked editor
from a slow operation, a crashed editor, or a dropped connection.

| Status | Evidence required |
|---|---|
| `queued` | Bridge acknowledged receipt and the operation is present in its queue |
| `disconnected` | Transport-level failure: connection refused, socket closed, listener absent |
| `failed` | The operation returned an error, or the bridge reported it terminal |
| `modal_blocked` | A supported editor-state signal, proven in Session A, positively reports a blocking dialog |
| `unknown` / `pending` | **Default.** No reply and no positive evidence for any of the above |

`unknown` must remain reachable and must be reported as such. Collapsing it into
`modal_blocked` would restate the guess the current message already makes.

**No automatic retry of a possibly executed mutating command.** A timeout does
not prove the command did not run. Retrying a spawn, delete, save, or property
write risks duplicating or compounding an applied change. Retry may be offered
only for operations the transport can prove idempotent or unexecuted, and
otherwise must be an explicit owner decision.

**Operation identity and recovery** may be specified only where the actual
transport supports them. The bridge is synchronous and its internal request id
is never returned to a caller, so correlation of a late reply to a specific
in-flight operation is unproven. Session B must confirm what the transport can
actually do before any resume, cancel, or reattach behaviour is designed.
Official MCP operations are out of reach on both counts.

**Amendment (Session A decision).** The evidence rules above still govern.
Session A proved no signal for `queued` or `modal_blocked`, so no Toolbelt code
produces either. The remaining outcomes are carried by the clients' existing
exception contracts, defined in "Session B — client outcome semantics
(amended)", and an unknown outcome is the default wherever delivery or
completion is unproven.

## Session B — client outcome semantics (amended)

Session B changes how Toolbelt's two external clients connect to the bridge,
classify the outcome of a bridge call, and word that outcome, and it documents
that contract. It changes no bridge behaviour.

### Existing behaviour, inspected at `c4c21caa0960c430a4bcfb90cd65ef1edfc1a790`

Neither client retries today. Once the session handoff loads, each `_send`
makes exactly one `urlopen` call (`client.py:163`, `mcp_server.py:211`). Both
calls use urllib's default opener, which applies environment and system HTTP
proxy settings and follows redirects.

**Bridge response producers**, in
`Content/Python/UEFN_Toolbelt/tools/mcp_bridge.py`:

| Producer | Location | Queued? | What it establishes |
|---|---|---|---|
| Wrong path, `Host`, browser `Origin`, content type, framing, size, or bearer: `404`, `400`, `403`, `415`, `411`, `413`, `401` | `do_POST` `:880-909` | No | Rejected before queueing |
| Malformed JSON, non-object body, missing `command`, non-object `params`: `400` | `:911-928` | No | Rejected before queueing |
| Any other method: `405`, or `403` for `OPTIONS` | `do_GET` and its aliases, `do_OPTIONS` | No | Rejected before queueing |
| Deadline elapsed: `504` | `:934-943` | **Yes** | Nothing about the command. It stays queued or running, `_tick` still dispatches it, and its unread result is pruned after `STALE_CLEANUP_SEC` (`:1018-1024`) |
| Listener stopped while the command was still queued: `200`, `success: false`, `MCP listener stopped before command dispatch` | `stop_listener` `:1145-1157` | Drained | Not dispatched |
| Dispatch raised: `200`, `success: false`, with error and traceback | `_execute_command` `:982-988` | Dispatched | A failure, not whether anything changed. `_dispatch` raises before any handler for an unknown command (`:240-245`); a handler raises before its body on bad parameters or on the local-only lifecycle guard (`:288-294`); or it raises part-way through, after changes were applied |
| Dispatch returned: `200`, `success: true` | `_execute_command` `:980-981` | Dispatched | The handler returned. That does not show the requested operation succeeded: `run_tool` carries the tool's own `status`, and `batch_exec` reports success per item (`:350-359`) |

Every error response the handler's own methods write is JSON of the form
`{"success": false, "error": message}` (`_error`, `:950-951`). The inherited
`BaseHTTPRequestHandler.send_error`, which the bridge does not override, still
writes HTML for what it rejects itself, such as a malformed request line, an
over-long header block, or an unknown method. Those responses match no
enumerated pair. A request whose handler raises after `:932`,
for example while its response is written, is closed without a response and
leaves the command queued or dispatched. The listener is a single-threaded
`HTTPServer` (`:1069`), so a request waits behind any request still inside its
deadline loop.

These producers describe the bridge. A client sees only what reaches it, and a
status code alone does not identify which server produced it or whether a
command ran.

**Client mapping at that commit:**

| Transport result | `client.py` | `mcp_server.py` |
|---|---|---|
| Handoff missing, unreadable, or invalid | `AuthenticationError`, no request (`:119-140`) | `ConnectionError`, no request (`:163-186`) |
| `401` | `AuthenticationError` (`:166-169`) | `PermissionError` (`:214-217`) |
| Any other HTTP status, `504` included | `ToolbeltError`, "rejected with HTTP N" (`:170`) | `RuntimeError`, "rejected with HTTP N" (`:218-220`) |
| `URLError` whose text contains "refused" or "no connection" | `NotConnected`, "listener is not running" (`:171-177`) | `ConnectionError`, "listener is not running" (`:221-228`) |
| Any other `URLError` | `NotConnected`, "could not be reached" (`:178`) | `ConnectionError`, "could not be reached" (`:229`) |
| Other exception whose text contains "timed out" | `CommandTimeout`, "UEFN may be processing a heavy operation" (`:179-185`) | `TimeoutError`, "The UEFN editor may be blocked. Try a shorter operation." (`:230-236`) |
| Any other exception, such as a dropped connection or an unreadable body | `ToolbeltError` with the exception text (`:186`) | `RuntimeError` with the exception text (`:237`) |
| `200` with `success: false` | `ToolbeltError` with the bridge's error and traceback (`:190-194`) | `RuntimeError`, "UEFN error for …" (`:241-245`) |

CPython's `urllib.request.AbstractHTTPHandler.do_open`, checked on 3.13.5,
wraps an `OSError` raised while connecting or sending in `URLError`, so a
timeout while connecting or sending arrives as a `URLError` whose reason is a
`TimeoutError`. An error while reading the response, such as
`http.client.RemoteDisconnected` (a `ConnectionResetError`), propagates
unwrapped. The standard library does not report how much of a request reached
the listener, so only a refused connection shows that no request was delivered.

### Transport exposures reproduced for this amendment

Both were reproduced on Python 3.13.5 in isolated processes, with dummy
credentials, a synthetic handoff file, and fake HTTP servers on ephemeral
loopback ports. No live handoff or token, no UEFN, no bridge, and no real proxy
was involved. They show what these clients do under those conditions. They are
not evidence that any credential reached a proxy or another server on the
owner's machine.

- **Proxy.** With `HTTP_PROXY` naming a fake proxy, `client.py`'s `ping` sent its
  request, dummy bearer included, to the fake proxy. The fake endpoint named in
  the handoff received nothing, and the client reported the proxy's `502` as
  "rejected with HTTP 502". `urllib.request.proxy_bypass("127.0.0.1")` returned
  `False`. First reported by independent review and reproduced here;
  `mcp_server.py` opens requests through the same default opener.
- **Redirect.** A fake endpoint that answered the `POST` with `302` to a second
  loopback URL caused `client.py` to send a `GET`, dummy bearer included, to that
  URL and to return the second server's JSON as a successful result.

A per-request opener built with `urllib.request.ProxyHandler({})` sent the same
request to the fake endpoint and nothing to the fake proxy.

### Required contract

Session B keeps each existing exception class where the evidence supports it,
and changes a class only where the old one asserts more than is known.

**Direct loopback transport.** Both clients open every bridge
request directly to the endpoint validated from the session handoff -
`127.0.0.1` and its integer port - through a per-request opener that ignores
environment and system HTTP proxy settings (`urllib.request.ProxyHandler({})`)
and follows no redirect. This covers these requests only. It installs no global
opener, changes no process environment or system proxy setting, leaves handoff
and endpoint validation exactly as strict, and changes nothing in the bridge or
its bearer protocol.

The proxy bypass is the owner's decision, recorded in "Session A decision
record". Refusing redirects is not a separate grant: it follows from connecting
only to the validated endpoint and from the one-attempt rule below, because a
redirect sends a second request, bearer included, to an endpoint that was never
validated. The Session B gate restates both.

**Terms.** A *connection attempt* is one call into that opener for one client
call. A *delivered request* is an HTTP request a server received. A refused
connection is an attempt with no delivered request, and a client can observe
attempts but never delivery.

**Classification.** The first matching row applies.

| # | Condition | What it establishes | `client.py` | `mcp_server.py` |
|---|---|---|---|---|
| 1 | The session handoff is missing, unreadable, or invalid | No connection attempted and no request sent | `AuthenticationError` (unchanged) | `ConnectionError` (unchanged) |
| 2 | The connection attempt raised a `URLError` whose reason is a `ConnectionRefusedError` | An attempt, with no request delivered | `NotConnected` (unchanged) | `ConnectionError` (unchanged) |
| 3 | A timeout - `TimeoutError` or `socket.timeout` - raised directly or as the reason of a `URLError` | Unknown outcome | `CommandTimeout` (unchanged when direct; was `NotConnected` when wrapped) | `TimeoutError` (unchanged when direct; was `ConnectionError` when wrapped) |
| 4 | An HTTP error status whose body parses to exactly `{"success": false, "error": M}` for an enumerated pair below | Rejected by the bridge before queueing | `AuthenticationError` for `401`, otherwise `ToolbeltError` (unchanged) | `PermissionError` for `401`, otherwise `RuntimeError` (unchanged) |
| 5 | `504` whose body parses to exactly `{"success": false, "error": "Command timed out: C"}`, where C is the command sent | The bridge's deadline elapsed; unknown outcome | **`CommandTimeout`** (was `ToolbeltError`) | **`TimeoutError`** (was `RuntimeError`) |
| 6 | Any status other than `200` that rows 4 and 5 did not match - including any 2xx other than `200`, any redirect, a `401` or `504` without the bridge body, and any status a proxy or another server could produce | Unknown outcome | **`OutcomeUnknown`** (was `ToolbeltError`, or `AuthenticationError` for an unmatched `401`. Today a `301`, `302`, or `303` reply is not raised: it is followed with a `GET`, bearer included, and the redirect target's reply is classified instead. Today a 2xx other than `200` is returned as a result when its body carries a truthy `success`, and raises `AttributeError` when its JSON is not an object) | `RuntimeError` (unchanged, except that an unmatched `401` was `PermissionError`; the same redirect and 2xx behaviour applies today) |
| 7 | `200` with a JSON object whose `success` is `true` | The handler returned | the result (unchanged) | the result (unchanged) |
| 8 | `200` whose body parses to exactly `{"success": false, "error": "MCP listener stopped before command dispatch"}` - those two keys and no others | Drained before dispatch | `ToolbeltError` (unchanged) | `RuntimeError` (unchanged) |
| 9 | `200` with a JSON object whose `success` is `false` that row 8 did not match | A reported failure; neither execution nor non-execution | `ToolbeltError` (unchanged) | `RuntimeError` (unchanged) |
| 10 | Any other transport error - a `URLError` with another reason, or a connection closed, reset, or aborted while awaiting or reading the response, including a truncated body (`http.client.IncompleteRead`) - or a `200` body that is not a JSON object with a boolean `success` | Unknown outcome | **`OutcomeUnknown`** (was `NotConnected` for a `URLError`, otherwise `ToolbeltError`; a `200` whose JSON is not an object currently raises `AttributeError`, and a truthy non-boolean `success` is currently returned as a result) | `ConnectionError` for a `URLError`, otherwise `RuntimeError` (classes unchanged; the same `AttributeError` and truthy-`success` behaviour applies today) |

Row 3 precedes rows 2 and 10, so a timeout is always a timeout, whether or not
`urllib` wrapped it. A refusal is recognized only by the reason's type; the
existing text match does not survive.

Row 8 is bound to the envelope `stop_listener` writes (`:1154-1157`), which the
HTTP thread returns unchanged through `_respond(200, result)` (`:945`). A
dispatched command that raises the same message produces a body that also
carries `traceback` (`_execute_command`, `:984-988`), so it is row 9, not row 8.

Rows 7 to 9, and row 10's response-body clause, apply only to status `200`.
Row 10's transport-error clause has no status condition: it covers an error
raised before any status line arrives and an error raised while a `200` body is
read, such as a reset mid-body or a truncated body (`IncompleteRead`). `urllib`'s `HTTPErrorProcessor`
raises `HTTPError` only outside 200-299, so a 2xx other than `200` arrives as an
ordinary response: each client checks the status itself and sends anything other
than `200` to row 6.

**Enumerated bridge rejections for row 4**, each with its literal call site:

| Status | `error` | Call site |
|---|---|---|
| `404` | `Unknown path` | `:881` |
| `400` | `Invalid Host header` | `:884` |
| `403` | `Browser-originated requests are not accepted` | `:887` |
| `415` | `Content-Type must be application/json` | `:891` |
| `400` | `Transfer-Encoding is not supported` | `:894` |
| `411` | `A valid Content-Length is required` | `:898`, `:902` |
| `413` | `Request body is too large` | `:905` |
| `401` | `Authentication required` | `:908` |
| `400` | `Malformed JSON request` | `:915` |
| `400` | `JSON body must be an object` | `:918` |
| `400` | `Missing 'command'` | `:924` |
| `400` | `'params' must be an object` | `:927` |
| `405` | `Only authenticated POST requests are accepted` | `:869` |
| `403` | `Browser preflight is not accepted` | `:948` |

Each pair is produced before `_command_queue.put` at `:932`. Row 4 relies on the
request having gone directly to the validated endpoint, with no proxy and no
redirect, and on the body being one of these exact bridge bodies. Another
same-user process listening on that port could imitate one. `SECURITY.md`
already states that loopback plus a bearer token is not a sandbox, and this
contract claims nothing beyond that boundary.

**Supported Python versions.** `client.py` declares Python 3.8 and later
(`:5`); `mcp_server.py` declares no floor of its own and inherits its `mcp`
dependency's. CI runs Python 3.11 only, and the probes behind this plan ran on
3.13.5. Before 3.10, `socket.timeout` is a separate `OSError` subclass rather
than an alias of `TimeoutError`, so rows 3 and 10 are decided with
`isinstance(error, (TimeoutError, socket.timeout))`, never with `TimeoutError`
alone and never by message text. Session B does not change either file's
declared support and installs no interpreter; every version it did not run,
3.8 to 3.10 at least, is recorded as untested.

`OutcomeUnknown` is one new subclass inside the existing hierarchy, not a new
result schema: `class OutcomeUnknown(ToolbeltError)`, with `CommandTimeout`
re-parented beneath it, so every `CommandTimeout` stays a `ToolbeltError`. It is
needed because `NotConnected` asserts that the listener is not running, which a
lost connection does not show, and a bare `ToolbeltError` cannot be told apart
from a reported failure. `mcp_server.py` keeps its built-in classes except for
rows 3, 5, and 6; its agent-facing contract is the message text.

**Message requirements.**

- *Row 1:* says no request was sent because the session handoff is missing or
  invalid, and how to restart the listener.
- *Row 2:* says the connection was refused, so no request reached a listener. It
  claims nothing about delivery beyond that.
- *Row 4:* says the listener rejected the request before queueing it, with its
  status. No unknown-outcome wording.
- *Rows 3, 5, 6, and 10 - unknown outcome:* names the command, with the session
  token redacted. It says no reply confirmed the outcome: the command may not
  have run, may still be queued or running, or may have completed. It says not to
  send a command that changes editor or project state again until that state has
  been checked, and that a check sent while the editor is not processing the
  bridge queue can also go unanswered. It says Toolbelt cannot determine why no
  reply arrived, and directs the owner to the UEFN editor. It names no cause - no
  modal, dialog, blocked editor, or heavy operation - and suggests neither a
  shorter operation nor a retry.
- *Row 8:* says the listener stopped before dispatching the command.
- *Row 9:* says the bridge reported a failure, which can be a rejection before
  dispatch or a failure during execution that left partial changes. It claims
  neither.

**No automatic retry.** Every client call makes at most one connection attempt:
one once the handoff loads, and none when row 1 applies. No outcome triggers a
retry, backoff, redirect, reconnect-and-resend, or fallback request, and
`connect()` sends one `ping`.

**Agent instructions.** The FastMCP `instructions` in `mcp_server.py` gain one
short paragraph: a timeout, a lost connection, or an unexpected response is an
unknown outcome; do not automatically send a state-changing tool call again; once
the editor answers, inspect state with read tools before deciding; `get_history`
entries carry a command name, an elapsed time, and a success flag, but no request
identifier, parameters, time, or caller, so they cannot identify a specific call
or show how many times it ran. It names no cause of a missing reply.

### Compatibility consequences

1. `504` with the bridge body: `client.py` `ToolbeltError` becomes
   `CommandTimeout`, and `mcp_server.py` `RuntimeError` becomes `TimeoutError`.
   `except ToolbeltError` still catches the `client.py` case, and code catching
   `RuntimeError` from `mcp_server.py` no longer does.
2. A timeout wrapped in `URLError`: `client.py` `NotConnected` becomes
   `CommandTimeout`, and `mcp_server.py` `ConnectionError` becomes `TimeoutError`.
3. Any other `URLError` that is not a refusal: `client.py` `NotConnected` becomes
   `OutcomeUnknown`; `mcp_server.py` keeps `ConnectionError`. A `URLError` whose
   text mentions a refusal but whose reason is not a `ConnectionRefusedError` is
   no longer treated as a refusal.
4. Response-phase connection errors, unreadable bodies, and error statuses without
   an exact bridge body: `client.py` `ToolbeltError` becomes `OutcomeUnknown`. An
   unmatched `401` becomes `OutcomeUnknown` in `client.py` (was
   `AuthenticationError`) and `RuntimeError` in `mcp_server.py` (was
   `PermissionError`). Two response bodies change from behaviour neither client
   documents today, for a `200` and for any other 2xx alike: a body that is not
   a JSON object raises `AttributeError` at `client.py:190` and
   `mcp_server.py:241`, and a truthy non-boolean `success` is returned as a
   result. Both become unknown outcomes. A 2xx other than `200` whose body
   carries any truthy `success`, `true` included, is also returned as a result
   today, by both clients, and becomes an unknown outcome. The bridge produces
   none of these: it answers only with `200` or an `_error` status. Today such a
   response can reach either client from a proxy, from the target of a followed
   redirect, or from another server on the port; after the direct-transport
   change, only another server on the port remains. In either case the status
   alone does not identify which server produced the response.
5. Proxies and redirects: bridge requests no longer use environment or system
   HTTP proxies and no longer follow redirects. Today a `301`, `302`, or `303`
   reply to the bridge `POST` is followed with a `GET` that carries the bearer to
   the redirect target, and a `307` or `308` reply already raises. Any setup that
   reached the bridge only through a proxy stops working.
6. Existing tests: the fixtures in `tests/test_mcp_security.py` patch
   `urllib.request.urlopen` and fake a `401` with no body. The transport seam
   moves to the direct opener, and a bodiless `401` becomes an unknown outcome, so
   those fixtures move to the new seam and carry the bridge's real `401` body.
   Their class and redaction assertions keep their meaning; none is weakened or
   removed.
7. Every other class is unchanged. Message text changes for timeouts, lost
   connections, rejected requests, and reported failures. No test pins the
   current messages.
8. The Probe C expectation table in the Session A record describes the mapping at
   `c4c21caa0960c430a4bcfb90cd65ef1edfc1a790` and stays as history.

### Limitations of the existing bridge deadline, recorded and not changed

- `HTTP_TIMEOUT_SEC = 30.0` (`:93`) bounds the bridge's wait. `client.py` waits
  30 s by default, 60 s for `batch`, and 120 s for `run_tool`; `mcp_server.py`
  waits 120 s for `run_toolbelt_tool` and `batch_exec`. Whenever the deadline
  loop runs, an operation longer than 30 s is reported as an unknown outcome
  even if it later succeeds, and the longer client timeouts are never reached.
- The 30 s default in `client.py` equals the bridge deadline, so either the
  `504` or the client's socket timeout may arrive first.
- Whether the deadline loop completes while the editor is not servicing ticks is
  unproven, because Probe C was not run. Both paths therefore map to the same
  unknown outcome.
- A `504` neither removes nor cancels the queued command, and its late result is
  discarded.
- The single-threaded listener serializes requests, so a follow-up check can
  wait behind a request that is still pending.
- No request identifier reaches the client, so a late execution cannot be
  matched to the call that submitted it.

### Exact candidate file inventory

Session B may modify only these four files:

- `client.py`
- `mcp_server.py`
- `.claude/mcp_reference.md` - its "External HTTP Client (no MCP required)"
  section documents the direct loopback transport, the outcome contract, and the
  compatibility consequences.
- `tests/test_mcp_security.py` - the existing home of both clients' transport
  tests and of `_load_external_client`.

Nothing else changes: not `Content/Python/**` or `mcp_bridge.py`, `deploy.bat`,
`README.md`, `SECURITY.md`, `docs/CHANGELOG.md` (release notes belong to a
separately gated release session), the governance files, the Session A record,
or its evidence directory.

### Exclusions

Any change to the bridge, including its deadline, queue, endpoints, status or
heartbeat readers, `_tick_health`, and its bearer or handoff protocol.
Authentication and the WO-001 control plane. Weakening handoff or endpoint
validation. Global proxy configuration, `install_opener`, or process
environment changes. Epic's official MCP. Operation identifiers, correlation,
cancellation, and reattachment. Retry of any kind. Detecting, classifying, or
handling modals or dialogs. Version or count bumps.

### Static verification

In `tests/test_mcp_security.py`, for both clients. Every test uses dummy
credentials and synthetic handoff files, and none reads a live handoff, uses a
live token, or contacts a real proxy.

1. **Classification.** Each row of the classification table raises its class,
   driven through the transport seam: a missing and an invalid handoff; a
   `URLError` wrapping `ConnectionRefusedError`; a direct `TimeoutError`; a
   `URLError` wrapping `TimeoutError`; every enumerated rejection with its exact
   body; the same statuses with a non-matching body, including a bodiless `401`;
   a `504` with and without the bridge body; a `301`, a `302`, and a `303`; a
   `502`; a `203` carrying `{"success": true, ...}`; `RemoteDisconnected`;
   `ConnectionResetError`; a `200` whose body is truncated, raising
   `IncompleteRead`; a non-JSON `200`; a `200` whose JSON is not an object; a
   `200` whose `success` is a truthy non-boolean; `success: true`; the exact
   stop-drain body; and another `success: false`.
   Two near-match cases are required as well. The stop-drain error carrying an
   extra `traceback` key is row 9, not row 8. And a timeout type that is distinct
   from `TimeoutError` - simulated by temporarily replacing `socket.timeout` with
   a separate `OSError` subclass, as it is before Python 3.10 - is row 3, both
   raised directly and as a `URLError` reason.
2. **Enumeration drift.** The clients' enumerated rejection pairs equal the
   literal `(status, error)` arguments passed to `_reject` and `_error` in
   `mcp_bridge.py`, plus the `504` deadline form, so a bridge message change fails
   a test instead of silently moving a response between rows.
3. **Attempts.** Exactly one connection attempt for rows 2 to 10, and none for
   row 1.
4. **Refusal, isolated.** A synthetic handoff naming a loopback port with no
   listener raises the row 2 class after one attempt, and its message claims no
   delivery.
5. **Proxy bypass, isolated.** A fake proxy and a fake endpoint listen on
   ephemeral loopback ports, and the synthetic handoff names the endpoint. With
   `HTTP_PROXY`, `http_proxy`, and `ALL_PROXY` naming the fake proxy and
   `NO_PROXY` cleared, the fake proxy accepts no connection and receives no token
   bytes; the fake endpoint receives exactly one request, carrying the dummy
   bearer. Afterwards the process environment and urllib's global opener are as
   they were.
6. **Redirect, isolated.** A fake endpoint that answers `302` to a second fake
   server raises an unknown outcome after one attempt, and the second server
   receives nothing.
7. **Messages.** Unknown-outcome messages name the command and carry the guidance
   above, and contain none of "modal", "dialog", "blocked", "heavy operation",
   "shorter operation", "retry", "rejected", "refused", or "not running". Row 1
   and row 2 messages claim no delivery and carry no unknown-outcome wording.
   Rejection wording appears only for row 4, and row 9 claims neither execution
   nor non-execution.
8. **Instructions.** The FastMCP `instructions` contain the unknown-outcome
   paragraph and name no modal or dialog.
9. **Redaction.** No raised exception's `str` or `repr` contains the session
   token, on any row.
10. **Existing behaviour.** The existing authentication, redaction, and
    `execute_python` assertions keep their meaning after the fixture changes in
    compatibility item 6.
11. **Local gates.** `python -m ruff check .`, `python -m mypy`,
    `python -m pytest`, `python scripts/drift_check.py`,
    `python scripts/gen_api_manifest.py --check`, and `git diff --check` pass.

The CI required job is verified only after the separately gated commit and
push, as "Stop boundaries" orders.

**Stop.** Session B ends with its worktree uncommitted for independent review.
Session C, commit, and push each need their own owner gate.

## Session C — live acceptance, owner-operated (amended)

Static tests cannot show what a running editor produces. Session C checks the
Session B mappings against `TOOL_TEST` before Session B is committed, because
`CLAUDE.md` requires live verification before code is committed. It does not
test modal behaviour, classify any dialog, or exercise proxies or redirects,
which static verification covers with fake servers.

### Runtime prerequisites

- **Reviewed worktree.** The client files come from the independently reviewed,
  uncommitted Session B worktree, and their hashes match that review's snapshot.
- **What deployment reaches.** `client.py` and `mcp_server.py` run from the
  repository checkout, outside UEFN. `deploy.bat` copies only
  `Content/Python/UEFN_Toolbelt`, `init_unreal.py`, and `verse-book`, so client
  edits never reach the editor, and Session B leaves the in-editor bridge
  unchanged.
- **Repository policy still applies.** `CLAUDE.md` requires `deploy.bat` before
  any live test of a code change, so run it from the reviewed worktree. Its
  `_build_stamp.json` then names the base commit marked `+dirty`, because the
  client edits are uncommitted, so the stamp alone does not identify the
  deployed bridge: the deployed `mcp_bridge.py` SHA-256 must also equal the
  repository copy. A mismatch stops the session.
- **Fresh editor.** A full UEFN restart, so the bridge's in-memory `_history`
  holds no entries. Record as separate fields the running editor build from the
  editor log, the project's `compatibilityVersion`, and the UEFN MCP Toolsets
  beta state. Run `tb.run("mcp_start")`, with the Quirk #36 recovery if needed,
  then an authenticated external `ping`.
- **Editor build after an update.** UEFN was updated after Probe A. Before any
  live session, record the running editor build from the editor log and the
  project's `compatibilityVersion` as separate fields. Check Epic's release
  notes for that build against the Epic-side dependencies these cases use - the
  in-editor Python console, the Slate post-tick callback that drains the bridge
  queue, and the viewport-camera API behind `get_viewport_camera` and
  `set_viewport_camera` - and verify them before running the cases. Earlier
  evidence keeps its original build label (`Release-42.10` for Probe A). Report
  a concrete incompatibility before expanding scope; an update alone does not
  reopen the investigation. This prerequisite authorizes no live work.
- **One caller.** The acceptance harness is the bridge's only caller: no MCP
  host is connected to `mcp_server.py`, and no other script holds the session
  handoff. The harness imports both clients from the reviewed worktree and calls
  the `mcp_server.py` functions directly. No proxy variable is set.
- **Attempt record.** In its own process, the harness wraps the clients'
  transport seam to record every connection attempt with its command and its
  start and end times. An attempt is not a delivered request; delivery and
  dispatch are read only from the bridge's `history`.
- **No credential copies.** The harness never copies the live handoff or keeps
  its bearer token. Any synthetic handoff it writes carries a dummy token and is
  deleted at cleanup.

### Cases

Each case records the harness's attempt record, the exception class and
message, and the elapsed time. A case whose precondition did not occur is void,
not passed.

A **stall** is produced without a dialog. The owner enters this in the UEFN
Python console:

```python
import time; print("WO-004 stall start", time.time()); time.sleep(75); print("WO-004 stall end", time.time())
```

It changes no content. Windows may mark the editor as not responding; the owner
does not close it. The two printed values bound the stall on the same clock the
harness uses. After the owner reports that the stall has begun, the harness
sends the case's request and records the attempt's start and the moment the
client raised. Cases 4 and 5 count only when all of the following hold:

- the stall began before the attempt started;
- the client raised a row 3 or row 5 outcome before the stall ended, so the
  request's own deadline - 30 s for the calls used here, in both clients -
  expired while the stall was still running;
- no `200` response arrived for that attempt.

If any of these cannot be shown from the printed values and the attempt record,
the case is void: neither passed nor failed. The 75 s stall leaves room to send
the request after the stall starts and still reach its 30 s deadline before the
stall ends.

1. **Positive control.** `ping` returns promptly after one attempt. Record the
   port it reports.
2. **Stopped listener: missing handoff.** After `mcp_stop`, confirm that the
   handoff file is absent and ports 8765–8770 are closed. `ping` through each
   client then raises the row 1 class (`AuthenticationError` or
   `ConnectionError`) with no connection attempt recorded, and its message says
   no request was sent. Connection refusal is not tested live; static test 4
   covers it.
3. **Rejected before queueing.** Restart the listener with `tb.run("mcp_start")`.
   Send one `ping` through each client, confirm that it succeeds, and record the
   port it reports. That newly observed port replaces case 1's for this and
   every later case, because a restarted listener may bind a different port and
   always rotates its session secret. Then read `history`, and send a `ping`
   through a synthetic handoff naming the new port with a dummy token. That handoff is valid in every other respect - `version`
   1, host `127.0.0.1`, and a token of at least 32 characters - so the call
   reaches row 4 rather than row 1. Run it through `client.py` and again through
   `mcp_server.py`. Each raises `AuthenticationError` or `PermissionError` with
   row 4 wording after one attempt, and a second `history` read shows no new
   `ping` entry.
4. **Unknown outcome, read-only.** During a stall, `ping` with the default
   timeout raises `CommandTimeout` or `TimeoutError` with unknown-outcome
   wording, after exactly one attempt. Record whether a `504` or a socket timeout
   arrived. The stall timing rule above decides whether the case counts.
5. **Unknown outcome, state-changing.** Before the owner starts the stall, record
   the viewport camera, choose a different target location, and read `history`
   as the baseline. During the stall, send one `set_viewport_camera` to the
   target. Pass requires all of:
   - exactly one connection attempt for that call, and no further attempt until
     the verification reads below;
   - an unknown-outcome exception;
   - after the stall, `history` shows exactly one new `set_viewport_camera`
     entry since the baseline, with its `total` below 500 at both reads;
   - `get_viewport_camera` reports the target location.

   The stall timing rule above decides whether the case counts; a void case 5
   is repeated only under a new stall, with a new baseline.
6. **Reported failure.** `_send` with a command name the bridge does not have
   raises `ToolbeltError` or `RuntimeError` with row 9 wording, after one attempt.
7. **MCP server path.** Cases 1, 4, and 6 are repeated through `mcp_server.py`:
   its `ping` function for cases 1 and 4, and its `_send` with an unknown
   command name for case 6.

**What case 5 establishes, and no more.** The client made one connection
attempt, the bridge dispatched a command of that name once in a window with no
other caller, and the camera reached the target. Each `history` entry records a
command name, an elapsed time, and a success flag - no request identifier,
parameters, time, or caller - so it cannot attribute an entry to a particular
attempt or prove how many times a call ran. Its
`total` stops growing at 500 entries (`HISTORY_CAP`), and the history persists
across `mcp_stop` and `mcp_start` until the module reloads. Camera placement is
idempotent, so the final camera cannot distinguish one execution from two.
Session C does not claim exactly-once execution.

**Evidence.** The harness output, the attempt record, the editor build fields,
the deployed hashes, and the cleanup checks are recorded for independent
acceptance review. The synthetic handoff from case 3 is deleted.

**Stop.** Session C ends with its evidence recorded and Session B still
uncommitted. Commit, push, and WO-004 completion each need their own owner
gate.

## Safety — non-negotiable

Toolbelt must never auto-confirm, dismiss, accept, decline, or manipulate any
dialog: destructive, save, validation, overwrite, missing-class, or otherwise
ambiguous. No blind keystrokes, no forced window closure, no automatic save, no
synthetic confirmation.

The only supported resolution is the owner reading the dialog and acting. The
deliverable's job is to tell the owner **that** something appears blocked and
**what** to look at — never to act for them.

## Inclusions

Client outcome classification and wording in `client.py` and `mcp_server.py`;
direct loopback transport for bridge requests, with no proxy and no redirect;
the no-automatic-retry guarantee and its agent instructions; the client
contract in `.claude/mcp_reference.md`; simulated regression tests in
`tests/test_mcp_security.py`; owner-operated live acceptance of those mappings.
Amended by the Session A decision: as issued, this list also named read-only
feasibility work, now complete, and a shared client status result, now out of
scope.

## Exclusions and deferred work

- **Deferred by the Session A decision:** modal or dialog detection and
  classification; heartbeat, status, and tick-health readers and endpoints; any
  change to `mcp_bridge.py`, including its deadline and queue; operation
  identifiers, correlation, cancellation, and reattachment; and Probes B and C
  or any further feasibility probe. Taking any of them up needs a new proposal
  or a separately gated amendment.
- No general computer control, window manipulation, or input synthesis.
- No WO-001 custom-bridge security change or expansion.
- No instrumentation of Epic's official MCP server.
- **Repository metadata is out of scope** — the GitHub description, the
  homepage, the topics, and the visibility all stay as they are.
- **Branch-protection settings are out of scope.**
- **No tag. No GitHub Release. Social publication is out of scope.**
- Four non-blocking observations recorded during the review of commit
  `0d513f1639cf197707132205f4074d0fe3a750cc` remain deferred and out of scope:
  a claim carried on both the root pointer and an issued mandate is reported
  against only one of them; a redundant conjunct in the WO-007 identity test;
  an unreachable `ValueError` guarding an internal `surface` argument; and a
  redundant proposal-set branch in `scripts/drift_check.py`.
- Reducing the size of the governance-enforcement surface added by that same
  commit — 1024 insertions against 113 deletions across
  `scripts/drift_check.py` and `tests/test_repo_integrity.py` — belongs to a
  separate mandate. This one leaves that surface alone.

## Configurations and fixtures

`TOOL_TEST` as the disposable level; Toolbelt's bridge started manually. Record
per run, as separate fields: the running editor build from the editor log
(Probe A ran on `Release-42.10`); the project's `compatibilityVersion` (`42.00`
during Probe A, a project field that does not identify the editor build); and
Epic's UEFN MCP Toolsets beta state, since Quirk #36 suppresses the project
startup script when it is enabled. As issued, this section named UEFN 42.00 as
the fixture.

## Cleanup

Stop the listener, close the editor, confirm the handoff file is absent and
ports 8765–8770 are closed. Leave TOOL_TEST unsaved and unmutated.

## Acceptance criteria

Amended by the Session A decision.

- Each client outcome is raised only from its specified evidence, and an unknown
  outcome is the default wherever delivery or completion is unproven.
- No client call makes more than one connection attempt, on any outcome, and
  no bridge request uses a proxy or follows a redirect.
- No client message or agent instruction names a modal, dialog, or blocked
  editor as a cause.
- `.claude/mcp_reference.md` documents the contract and each compatibility
  consequence.
- Session A's result is recorded before dependent work is planned; the Session A
  decision record satisfies this.
- Static gates pass before independent review, and the CI required job passes
  after the separately gated commit and push.
- Session C evidence is recorded with its claims limited as stated there, or the
  deliverable is reduced to what was shown, with the reduction stated.

## Stop boundaries

Each is a separate owner gate and none implies the next.

Completed: proposal revision → independent pre-issuance review → issuance →
Session A gate → Session A decision → independent review of the decision and
amendment → commit → push → CI → Session B gate → Session B implementation,
left uncommitted → independent review → Session C gate.

Remaining: live acceptance against that uncommitted change → independent
acceptance review → commit → push → CI → WO-004 completion gate.

As issued, this chain placed commit and push before Session C. It is reordered
because `CLAUDE.md` requires live verification before code is committed.

Live UEFN probes are owner-operated and separately gated. This document opens
nothing.

## Issuance enforcement

Issuance acceptance had to protect three surfaces that were unenforced at the
planning baseline. Driving the real `check_work_order_contract()` against a
temporary issued-state fixture at
`0d513f1639cf197707132205f4074d0fe3a750cc` produced zero findings for all of
the following, which is why each is named here:

1. **The root pointer's `- Base commit:`** — a zeroed, garbage, or simply wrong
   value raised nothing once a later order owned the pointer. It is now pinned
   to the issuance commit while this mandate is issued and no session is open.
2. **The root pointer's issuance evidence** — the `- Issuance commit:`,
   `- Issuance CI workflow:`, and `- Issuance CI job:` bullets could be deleted
   with no finding. They are now an exact, contiguous, terminal slice of the
   pointer's canonical bullet block.
3. **This mandate's own `BASELINE:` marker** — it could be zeroed with no
   finding. Exactly one canonical marker must now be present in this document,
   carrying the expected value, opening the canonical metadata slice.

Enforcement uses the existing structural validators in
`scripts/drift_check.py` and carries mutation coverage in
`tests/test_repo_integrity.py`, driving the real checker over temporary copies.
The mutation set covers, for each of the three surfaces: a changed value,
a removed field, a duplicated field, and a decoy — a correct value placed
somewhere else in the file, which does not satisfy the check.

All three surfaces are enforced as of this issuance, against the values
declared in the canonical metadata block above and in the root pointer's
canonical bullet block. The planning basis and the issuance basis are
distinct records and must not be conflated.

NEXT GATE: owner-operated Session C live acceptance of the reviewed uncommitted
Session B implementation, followed by fresh independent review of the recorded
evidence. Any change to the implementation, commit, push, and WO-004 completion
remain closed.
