# WO-004 Session C — Live Acceptance Record

- **Date of live run:** 2026-09-28. Local time is UTC−4. Editor-log timestamps
  are UTC.
- **Operator:** the owner (UEFN). The acceptance harness ran outside UEFN.
- **Base commit:** `17b5afe3f50bfa3ab882ff362a10eef70750c694`.
- **Evidence:** [`evidence/wo004-session-c/`](evidence/wo004-session-c/).
- **Result:** every mandated case passed within its timing and void rules. The
  claims are bounded as stated in sections 7 and 9.

## 1. Scope and authority

Root `WORKORDER.md` authorizes Session C for owner-operated live acceptance only.
This record was written afterwards, under a separate owner authorization for
evidence recording only. That authorization covers this file and the evidence
directory, nothing else.

Recording this evidence does not change:

- `WORKORDER.md`, the issued mandate or the Session A record;
- any implementation, checker or test.

It does not complete WO-004, and it authorizes no commit, push, tag or Release.

The worktree under test held eight uncommitted files:

- the Session B implementation (four files, identified below);
- the Session C authorization transition, including its identity-validation fix
  (`WORKORDER.md`, the mandate, `scripts/drift_check.py`,
  `tests/test_repo_integrity.py`).

Session C changed none of them. At recording time all eight were byte-identical
to the accepted snapshot `wo004-session-c-p1fix-2026-09-28`.

## 2. Implementation identity and deployment

| File | Git blob | SHA-256 of tested bytes |
|---|---|---|
| `.claude/mcp_reference.md` | `75873316c1f0f57037181a4fda2f2cd4365a730d` | `cb55912ec5168d2d46a3631443bc2dcc462f543567142d91b1fdd0b1cb6e5c26` |
| `client.py` | `bfff40e02fa167a0f987a5e066e7bc6f13f8b308` | `c5097f3141b19122b665b0be2a570e13ec642a5d2cc582a6bec717ae25e34850` |
| `mcp_server.py` | `70a88474dc138b5d3915f06a96dffef24c71c993` | `0aa4268491d60f7fbb663da1d3bbcb095997243a51db91357452160b04eed0b3` |
| `tests/test_mcp_security.py` | `34580cb9426f4aeaaa47381cf77d707936e88ffa` | `dd0c2ceaebfb813b371650e10658c98b41958e8d1f5139181ecaf8955cfe6976` |

These equal the mandate's "Session C authorization basis" identities.

**Harness hash check.** Before every subcommand, the harness re-checked the
SHA-256 of both clients against these values. It stops on a mismatch
(`guard_environment`, `harness.py.txt` lines 68–75).

**Deployment**

- **Deploy output.** `deploy.bat` ran from the reviewed worktree into `TOOL_TEST`
  and wrote build stamp `17b5afe+dirty` at 15:58:27 (`deploy_output.redacted.txt`).
- **Preflight** (`cases.redacted.jsonl` record 1, 15:58:34):
  - The deployed `mcp_bridge.py` SHA-256 equals the repository copy:
    `0e5ebc2d6f2d4727d7ca9040573d9854ab7da413e98770832d1336a5c875655c`.
  - The deployed package tree had no mismatched and no missing files.
  - There was no handoff file, and ports 8765–8770 were not listening.
- **Bridge unchanged.** The repository `mcp_bridge.py` is unchanged against `HEAD`
  (blob `bc842fa0ae1689ef2bffe03a86e1233aa6a20289`). This was re-checked at
  recording time.

**Full restart**

- The previous `TOOL_TEST` editor session ran build `52d8929+dirty`. It quit at
  16:00:46, after the deploy.
  - Source: its log, which is private and not excerpted.
- The session under test opened its log at 16:02:00 (excerpt L:1). It loaded the
  new stamp at L:8744.
- The first five `history` entries are the harness's own calls (section 6).

## 3. Build, compatibility and beta state

These fields are recorded separately. They come from
`build-fields.derived.txt` and the excerpt.

| Field | Value | Source |
|---|---|---|
| Running editor build | `++Fortnite+Release-42.20-CL-58011042` | Editor log L:1344. Engine `6.0.0-58011042+++Fortnite+Release-42.20` at L:1348 |
| Project `compatibilityVersion` | `42.00` | `TOOL_TEST.uefnproject`. This is a project field and does not identify the editor build |
| UEFN MCP Toolsets beta | ON | `"bEnableToolsetsForProject": true`. Epic's MCP server started for that setting at L:8822 |
| Bridge Python | 3.11.8 (UEFN embedded) | `ping` results |
| Harness Python | 3.13.5, Windows 11 | Preflight record |

**Build labels**

- Probe A keeps its own label, `Release-42.10`, in the Session A record.
- Every observation in this record is bounded to the 42.20 build above.

**Quirk #36** did not occur on this boot:

- the project `init_unreal.py` ran and registered 362 tools (L:8376–L:8747),
  with the beta ON;
- this is one boot. It is not a fix and not a general result.

**Epic release notes.** The mandate asks for a release-notes check for the
running build before the cases. According to the recovered conversation record
of the live session, and the owner's confirmation, the check was **performed
before deployment**:

- a web search, then a fetch of Epic's page
  `https://dev.epicgames.com/documentation/fortnite/42-20-fortnite-ecosystem-updates-and-release-notes?lang=en-US`;
- the fetch returned a summary, which reported no mention of the requested
  topics: Python, Slate or tick, the viewport camera, or MCP.

Limits of that evidence:

- The preserved account is a search and a summarized page fetch. The raw page
  text was not retained. This record therefore does not reproduce the page, and
  it does not show independently that Epic made no relevant change in 42.20.
- No exact timestamp for the search or the fetch is available. The
  conversation's ordering places the check before the deploy; no more precise
  time is claimed.
- The conversation record that supports the check was omitted from the original
  evidence package. It is not published here. This is why the acceptance review
  found the check absent from the evidence (section 11).

The three Epic-side dependencies were exercised live on this build:

- the Python console;
- Slate post-tick queue drain;
- viewport camera get/set.

That is observation, not a release-notes check.

## 4. Cases

Record numbers `C#n` refer to `cases.redacted.jsonl`, and attempt numbers `A#n` to
lines of `attempts.jsonl`. `L:n` refers to editor-log lines, which are kept in the
excerpt.

| Case | Records | Attempts | Observed | Verdict |
|---|---|---|---|---|
| Prerequisite | C#2, C#3 | A#1, A#2 | Authenticated `ping` returned 200 on port 8765 (uptime 31.2 s). The initial camera was read | PASS |
| 1 Positive control | C#4 | A#3 | `client.py` `ping` returned 200 in 0.167 s on port 8765 | PASS |
| 2 Missing handoff | C#5 | none | After `mcp_stop` (L:8947–L:8950), the harness found no handoff and no port 8765–8770 listening. `AuthenticationError` and `ConnectionError`, each "No request was sent" | PASS |
| 3 Rejected before queueing | C#6, C#7 | A#4–A#9 | Restart (L:8955–L:8959): both clients returned 200 on port 8765, uptime 12.1 s. Synthetic dummy-token handoff: `client.py` `AuthenticationError` and `mcp_server.py` `PermissionError`, each "rejected the request before queueing it (HTTP 401)", after 1 attempt. `history` total went from 5 to 6, and the only new entry is that `history` read | PASS |
| 4 Unknown outcome, read-only | C#8 | A#10 | During a stall: `CommandTimeout` with unknown-outcome wording | PASS |
| 5 Unknown outcome, state-changing | C#9, C#10 | A#11–A#15 | During a stall: `set_viewport_camera` raised `CommandTimeout`. Afterwards there was exactly one new `set_viewport_camera` entry, and the camera was at the target | PASS |
| 6 Reported failure | C#11 | A#16 | An unknown command returned 200 with `success: false`. `ToolbeltError`, exact class, with row 9 wording (bridge log L:9076) | PASS |
| 7 `mcp_server.py` path | C#12–C#14 | A#17–A#19 | `ping` 200 on 8765. Unknown command gave `RuntimeError` with row 9 wording (L:9077). During a stall, `TimeoutError` with unknown-outcome wording | PASS |

Every unknown-outcome message:

- names the command;
- says no reply confirmed the outcome;
- names no cause.

The exact texts are in the records and in the case 4, 5 and 7 console files.

**Stall timing.** The stall command is `wo004_stall_console_command.py.txt`, a
75 s `time.sleep`. All times below come from the stall prints, the attempt
record and the client's raise time.

| | Case 4 | Case 5 | Case 7 |
|---|---|---|---|
| Stall lines | L:8967–L:9009 | L:9029–L:9071 | L:9080–L:9122 |
| Stall length | 75.002 s | 75.001 s | 75.001 s |
| Stall start → attempt start | 23.8 ms | 40.4 ms | 22.8 ms |
| Attempt start → client raise | 30.012 s | 30.008 s | 30.011 s |
| Client raise → stall end | 44.97 s | 44.95 s | 44.97 s |
| Attempt result | `TimeoutError`, no HTTP status, `reason` null | same | same |
| Client class | `CommandTimeout` | `CommandTimeout` | `TimeoutError` |

All three stalls meet the void rule:

- the stall began before the attempt;
- the client raised before the stall ended;
- no `200` arrived for the attempt.

**Clock basis.** Each of the six stall print values exceeds its log stamp by 0.16
to 0.63 ms. This is consistent with the log truncating the same wall clock to
milliseconds.

**Case 5 camera**

| Read | Location |
|---|---|
| Baseline | (339.186416, 339.18649, 402.501074), pitch −40, yaw 225, roll 0 |
| Target | (739.2, 739.2, 602.5) |
| Verify read (A#15) | (739.2, 739.2, 602.5) |

- The first verify read, A#14, started 5.0 s after the stall ended.
- No attempt of any kind was made between A#13 and A#14.

## 5. Bridge side: 504 generation versus what the clients observed

In all three stalls, the bridge's deadline loop reached
`self._error(504, f"Command timed out: {command}")` during the stall. The traceback
frames are at L:8994, L:9056 and L:9107. Writing that response then failed:
`_respond` raised `ConnectionAbortedError: [WinError 10053]` at
`self.wfile.write(body)` (L:9005, L:9067, L:9118).

`end_headers()` runs before that `try` and raised nothing. `_respond` catches
only `BrokenPipeError` and `ConnectionResetError`, so this exception went
unhandled and was logged.

**What the clients saw.** No client observed a 504. Each recorded a socket
`TimeoutError` with no HTTP status. The bridge-side 504 generation is therefore
observed only in the editor log. **The live client path for a received bridge
504, row 5, was not exercised.**

**Ordering.** The timestamps establish only this: each client raised before the
bridge's first error log line for that request. The gaps were within 3.2–4.2 ms,
6.5–7.5 ms and 9.6–10.6 ms. The window is 1 ms wide because log stamps are
truncated to milliseconds. The log line is written after the failed write, so
these figures do not measure a margin between the client closing the socket and
the bridge's write. `WinError 10053` is consistent with the connection having
been closed first on the client side, but that is inference from the error type.

An "about 3 ms" margin stated in the session's working report is unsupported. It
is not part of this record.

After each stall the listener kept answering: A#11, A#14 and A#20 returned 200.
This applies only to these GIL-releasing console stalls.

**Deferred, not repaired.** The unhandled `ConnectionAbortedError` in `_respond`
is recorded as an observation. `mcp_bridge.py` is out of WO-004's scope, and
nothing was changed.

## 6. Reconciliation

**Attempts**

- `attempts.jsonl` holds 21 records.
- `cases.redacted.jsonl` holds 23 client calls:
  - 21 made exactly one attempt;
  - the 2 case-2 calls made none.
- Every attempt is referenced by exactly one call, is identical field for field
  to the copy embedded in that call, and falls inside the call's time window.
- No attempt is unreferenced or referenced twice.

| Attempts | Client | Command | Result | Case |
|---|---|---|---|---|
| A#1, A#2 | `client.py` | `ping`, `get_viewport_camera` | 200 | Prerequisite |
| A#3 | `client.py` | `ping` | 200 | 1 |
| A#4, A#5 | `client.py`, `mcp_server.py` | `ping` | 200 | 3, restart |
| A#6, A#9 | `client.py` | `history` | 200 | 3, before and after |
| A#7, A#8 | `client.py`, `mcp_server.py` | `ping` (synthetic handoff) | 401 in 0.001 s and 0.021 s | 3 |
| A#10 | `client.py` | `ping` | socket timeout, 30.012 s | 4 |
| A#11, A#12 | `client.py` | `get_viewport_camera`, `history` | 200 | 5, baseline |
| A#13 | `client.py` | `set_viewport_camera` | socket timeout, 30.008 s | 5 |
| A#14, A#15 | `client.py` | `history`, `get_viewport_camera` | 200 | 5, verify |
| A#16 | `client.py` | unknown command | 200, `success: false` | 6 |
| A#17, A#18 | `mcp_server.py` | `ping`, unknown command | 200 | 7 |
| A#19 | `mcp_server.py` | `ping` | socket timeout, 30.011 s | 7 |
| A#20, A#21 | `client.py` | `set_viewport_camera`, `get_viewport_camera` | 200 | Cleanup restore |

**Case 5 history.** The verify read (A#14) returned a total of 11 entries against
a baseline of 9. Both totals are below 500.

| Entry | Command | Consistent with |
|---|---|---|
| 1–5 | `ping`, `get_viewport_camera`, `ping`, `ping`, `ping` | A#1–A#5 |
| 6 | `history` | A#6 |
| 7 | `history` | A#9 |
| 8 | `ping`, `elapsed_ms` 1.0 | A#10, dispatched after its stall ended |
| 9 | `get_viewport_camera` | A#11 |
| 10 | `history` | A#12 |
| 11 | `set_viewport_camera` | A#13 |

**Reading the history**

- The 401 attempts A#7 and A#8 have no entries: they were rejected before
  queueing.
- The window since the baseline is `[history, set_viewport_camera]`, so there is
  exactly one new `set_viewport_camera`.
- History entries carry no request identifier, parameters or time. The mapping
  above is consistent, but no entry can be attributed to a particular attempt.
- Entry 8 is consistent with the case-4 `ping` running after its client had
  already reported an unknown outcome. That is the behaviour the unknown-outcome
  wording describes.

**Exactly-once is not claimed.** Camera placement is idempotent, and history
cannot show how many times a call ran.

**Reproducing this section.** Every figure in sections 4–6 can be recomputed from
three files: `attempts.jsonl`, `cases.redacted.jsonl`, and
`editor-log-excerpts.redacted.txt`, which keeps each line's original `L:n`.

The same analysis script was run on the private originals and on these published
files, and it produced identical output.

## 7. Harness, and what was not integration-tested

**What the harness did**

- It imported both clients from the reviewed worktree.
- It replaced each module's `_direct_opener` with a recorder:
  - The recorder calls the real factory, a proxy-free and redirect-refusing
    opener.
  - It passes `timeout` through and re-raises the original exception.
  - It records neither request headers nor tokens.

**Not MCP-host or stdio integration.** `mcp.server.fastmcp` was replaced by a
stand-in whose `tool()` returns each function unchanged. The harness then called
the `mcp_server.py` functions directly, in its own process. There was:

- no FastMCP server;
- no stdio transport;
- no MCP host or Claude Code connection.

That leaves these untested:

- FastMCP registration and schemas;
- how exceptions become tool-error results, and the text an agent sees;
- delivery of the `instructions` text;
- `mcp` package compatibility;
- the `.mcp.json` launch path, including `UEFN_MCP_PORT`.

At recording time the `mcp` package was not importable on Python 3.13.5 or
3.12.10 here.

**Harness version**

- `harness.py.txt` is the executed file, with one line redacted (section 10).
- Its private original and the private bytecode cache both record source mtime
  16:03:58 and size 25428, before the first attempt at 16:04:12.
- The preflight, at 15:58:34, ran under an earlier harness version, which was
  not preserved.

## 8. Cleanup

- **Camera restored.** C#15 (A#20, A#21) returned exactly the initial location
  and rotation.
- **Editor shutdown**, all from the log:
  - `mcp_stop` at L:9128–L:9131 (16:13:01);
  - `QUIT_EDITOR` at L:9141;
  - "Editor shut down" at L:9231;
  - log closed at L:9396 (16:13:09).
- **Final check** (C#16, 16:13:35):
  - the handoff was absent and no port 8765–8770 was listening;
  - the editor was not running;
  - the synthetic handoff was absent. It was deleted by this check
    (`synthetic_removed_now`: true).
- **No saves.** The full private log contains no package-save or dirty-package
  line: 0 matches for `LogSavePackage|SavePackage|Saving package|dirty package`.
  The acceptance review separately reported no project file changed after the
  deploy except `TOOL_TEST.code-workspace` (16:02:44, during boot). This record
  did not re-check that.

## 9. Deviations and coverage limits

**Deviations from the mandate's procedure**

1. **Stall trigger.** The harness fired each stall request when the stall-start
   line appeared in the editor log, not after an owner report. `stall_began_before_attempt`
   holds in every stall case.
2. **Release-notes check evidence.** The check was performed before deployment,
   but its supporting conversation record was omitted from the original
   evidence package. The page text was not retained, and no exact time is
   recorded (section 3).
3. **Console text** is preserved only for the three stall cases. The other cases
   survive as structured records.
4. **Beta state** was captured as raw lines and is labeled here after the fact.
5. **Synthetic handoff** was deleted at the final cleanup check, not immediately
   after case 3. It held only a dummy token.
6. **Preflight harness** ran under an earlier version that was not preserved.

**Coverage limits**

- **Outcome rows exercised live:**
  - row 1;
  - row 3 (a direct socket timeout only, not one wrapped in `URLError`);
  - row 4 (the `401` pair only);
  - row 7;
  - row 9.
- **Not exercised live:**
  - row 2 (refusal);
  - row 5 (a client-received bridge 504);
  - rows 6, 8 and 10;
  - the other 13 enumerated rejections;
  - proxy bypass and redirect refusal.

  These rely on the static tests only.
- **No MCP-host, stdio or FastMCP integration** (section 7).
- **Scope:**
  - one machine and one boot: Windows 11, build `Release-42.20-CL-58011042`,
    project `compatibilityVersion` 42.00, Toolsets beta ON;
  - bridge on Python 3.11.8, harness on 3.13.5;
  - client Python 3.8–3.12, Linux and macOS were not live-tested.
- **Stall type.** The stalls were GIL-releasing console `time.sleep` calls, not
  dialogs. **No modal or dialog diagnosis is claimed.**
- **Single caller.** No other caller was shown:
  - all 11 history entries read at case 5 map to harness attempts;
  - the `mcp` package was absent, so `mcp_server.py` could not have run as an MCP
    server.

  An idle connected process, another reader of the handoff, or foreign requests
  rejected before queueing cannot be excluded.
- **Exactly-once execution is not claimed** (section 6).
- **Enforcement.** This record and its evidence directory are not declared
  drift-check scan targets, and no test pins their hashes. `SHA256SUMS.txt` and
  `PROVENANCE.txt` allow a manual check.

## 10. Evidence, redaction and provenance

The published evidence is in `evidence/wo004-session-c/`, 14 files:

- `.gitattributes` sets `* binary`, so Git stores and checks out exact bytes and
  the hashes hold regardless of `core.autocrlf`.
- `SHA256SUMS.txt` covers every other file.
- `PROVENANCE.txt` maps each published file to:
  - its private original, by path inside the owner's preservation package;
  - both SHA-256 values;
  - its transformation.

| File | Kind |
|---|---|
| `attempts.jsonl`, `state.json`, `case4_console.txt`, `case5_console.txt`, `case7_console.txt` | Byte-exact |
| `cases.redacted.jsonl` | **Redacted.** The user-profile path segment in the bridge tracebacks of C#11 and C#13 is replaced with `<user>` (4 occurrences). Nothing else changed |
| `harness.py.txt` | **Redacted, non-executing.** Line 25's repository path is replaced with `"<repo>"`. The dummy token at line 33 is a labeled literal, not a credential |
| `wo004_stall_console_command.py.txt` | **Extracted.** The console command as logged at L:8966, L:9028 and L:9079, which are identical |
| `editor-log-excerpts.redacted.txt` | **Redacted excerpt.** 182 of 9,396 log lines in 21 windows, each prefixed `L:n` and keeping its original bytes, CRLF included. The user-profile segment is replaced with `<user>` on 12 lines |
| `deploy_output.redacted.txt` | **Redacted.** 8 other project names are replaced with `<other-project>`, with numbering kept. The user-profile segment is replaced with `<user>` |
| `build-fields.derived.txt` | **Derived.** The three fields of section 3, each quoting its source line |

**What the excerpt leaves out**

- account, authentication and presence lines (`LogEOSSDK`, `LogOnlineAccount`);
- the machine identifier;
- hardware and network lines;
- an outstanding-request URL carrying a session token fragment.

The three private stall segments equal the log's L:8966–L:9010, L:9028–L:9072
and L:9079–L:9123 with CR removed, and those lines lie inside the excerpt.

**Kept private, outside the repository**, in the owner's verified preservation
package (59 files, each hash-checked):

- the full editor logs;
- the reviewer transcripts and reports;
- the project file, which holds project identifiers and an account-derived Verse
  path;
- the raw build capture;
- `list_projects.cmd`, whose output lists private project names;
- the harness bytecode;
- the source map.

**Private data scan.** Every published file and this record were scanned for:

- account and owner names, email addresses and profile paths;
- scratch paths and session identifiers;
- the machine ID, EOS user IDs and JWT fragments;
- bearer and authorization values, 43-character token-shaped strings;
- project GUIDs, other project names and non-loopback IP addresses.

There were no findings.

## 11. Independent review

The offline acceptance review concluded **VERDICT: ACCEPT**. It rebuilt every
PASS and timing determination from the raw records and found no P0 or P1
issues. Its report is kept privately (SHA-256
`accf1d2929e62671d89931de63169291145600856f11a51469ae395c497dcfad`).

The report says the stall segments are "verbatim contiguous slices of the log".
This record states the precise relation: they match after CR removal (section
10).

| P2 finding | Disposition in this record |
|---|---|
| The "about 3 ms" margin is unmeasured | Withdrawn. Only the bounds in section 5 are stated |
| The release-notes check is absent from the evidence | Corrected. It was performed before deployment, according to the recovered conversation record and owner confirmation. That record was omitted from the original package, the raw page text was not retained, and no exact time is available (section 3) |
| The originals exist only in temporary storage | Preserved in the private verified package |
| The bytecode is missing from the pre-review hash list | Preserved privately. Not published |
| Procedure deviations | Recorded in section 9 |
| Bridge `ConnectionAbortedError`, a stale `TOOL_TEST` `core.py`, and harness style findings | The first is deferred (section 5). The second is noted here from the review and was not re-checked. The third does not apply, because the harness is published as `.txt` |

The earlier static reviews of the Session C authorization transition returned
ACCEPT WITH REQUIRED FIX, and the fix re-review returned ACCEPT.

## 12. Gate status

Session B remains uncommitted, and this record is uncommitted.

`WORKORDER.md` and the issued mandate are unchanged. Each of these needs its own
owner gate:

- independent review of this record;
- commit;
- push;
- CI;
- WO-004 completion.

WO-005 through WO-007 remain proposed.
