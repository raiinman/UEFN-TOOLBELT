# WO-007 — Public MCP Composition Explainer

STATUS: ISSUED

AUTHORIZATION: ISSUED — SESSION NOT AUTHORIZED

OWNER: Ocean Bennett

PRIORITY: P2

BASELINE: `5d88a4ee56309df43537d289514a150615dfeba6`

ISSUANCE_COMMIT: `c04e4a794f1e7d0c607c7ad712cbd28e86a55914`

ISSUANCE_CI_WORKFLOW: `37050236355`

ISSUANCE_CI_JOB: `110981533635` — Lint, types, tests

## Issuance basis

The independently accepted revision of this mandate was committed as
`c04e4a794f1e7d0c607c7ad712cbd28e86a55914`; [CI workflow
`37050236355`](https://github.com/undergroundrap/UEFN-TOOLBELT/actions/runs/37050236355)
completed successfully, including required job
[`110981533635` — Lint, types, tests](https://github.com/undergroundrap/UEFN-TOOLBELT/actions/runs/37050236355/job/110981533635).
Those identify the accepted proposal, not the later commit that records this
issuance, and they establish nothing about any Session A output. The planning
baseline above and the revision basis below are preserved unchanged; the train
state the revision basis describes is the state before this issuance.

Issuance alone grants no implementation authority. Session A, the repository
explainer and draft variants, needs its own separate owner gate recorded in
root `WORKORDER.md`, and its proposed live-verification exemption remains
pending the owner's decision.

## Revision basis

This pre-issuance revision replaces the original sketch, first proposed at
planning baseline `6b8ffb2b2d672812f8699af2c22f92c19708f29b`; the earlier
text remains in the repository history. The new baseline is the commit that
closed WO-006 as superseded. [CI workflow
`37037329967`](https://github.com/undergroundrap/UEFN-TOOLBELT/actions/runs/37037329967)
completed successfully on that commit, including required job
[`110938646551` — Lint, types, tests](https://github.com/undergroundrap/UEFN-TOOLBELT/actions/runs/37037329967/job/110938646551).
That run is CI on the WO-006 closure transition commit (distinct from the
closure basis CI `36817435116` recorded in the WO-006 mandate) and evidence for
this baseline only. It tested the repository's checker and tests; it
establishes nothing about any WO-007 output, which does not exist yet.

Train state at this baseline: WO-001 through WO-005 are completed. WO-006 is
superseded without an accepted comparative measurement and is resolved for
the frozen train, not completed. WO-007 remains proposed and unauthorized,
and this revision changes that state in no way.

## Problem

Creators need a factual explanation of what Epic's official UEFN MCP does, what
Toolbelt still adds, how the two coexist, when manual Toolbelt recovery is
needed, and where a custom MCP client fits.

## Evidence sources — decision lock

Every public claim must trace to one of these records, read at the baseline
above, and to nothing else:

- `docs/audits/2026-08-24-uefn-42-official-mcp-audit.md`: the official-MCP
  inventory, the launch boundary, coexistence, and the official-MCP findings it
  records (its P1 items 4 and 5 and P2 item 4), as observed on UEFN 42.00;
- the completed WO-001 mandate: the authenticated, same-user loopback bridge
  and its fail-closed control plane;
- the completed WO-002 mandate and
  `docs/audits/evidence/2026-08-27-wo002-session-b-official-mcp.json`: Toolbelt
  is not reachable through Epic's official MCP server, an accepted terminal
  negative result bounded by `UE::ValkyrieToolset::ToolsetPolicy`;
- the completed WO-003 mandate: the converged official-MCP documentation;
- the completed WO-004 mandate and
  `docs/audits/2026-09-28-wo004-session-c-live-acceptance.md`: client outcome
  semantics, direct loopback transport, and no automatic retry, as accepted at
  WO-004's completion. The Session C record bounds what ran live: only the
  outcome rows its section 9 lists, on the one build and boot recorded there.
  Proxy bypass and redirect refusal rest on static tests only, and no MCP-host,
  stdio, or FastMCP integration and no exactly-once execution are claimed. Its
  section 3 records that Quirk #36 did not occur on that one 42.20 boot, which
  is not a fix;
- the completed WO-005 mandate and `TOOL_STATUS.md`: registry-derived coverage
  categories, which describe what test code checks and establish no live
  verification;
- the superseded WO-006 mandate: its closure record, for the benchmark
  disclosure only;
- `SECURITY.md`, `docs/UEFN_QUIRKS.md` (Quirk #36 recovery and the
  project-Python upload rule), `CLAUDE.md`, and `.claude/mcp_reference.md`, as
  they stand at the baseline.

Precedence: the audit, the completed mandates, their evidence records, and
`TOOL_STATUS.md` govern, and a later accepted record governs an earlier one
where they differ (WO-001 and WO-002 supersede the audit's pre-hardening bridge
findings and its capability-direction rows). `SECURITY.md`,
`docs/UEFN_QUIRKS.md`, `CLAUDE.md`, and `.claude/mcp_reference.md` support a
claim only where they agree with those records; they never extend a claim,
drop its build, or present static or source-defined behaviour as live.

Three distinctions hold throughout. Epic's official MCP server and its own
toolsets are kept apart from Toolbelt's custom bridge and `client.py`.
Source-defined coverage categories and static tests are kept apart from live
verification. Findings observed on a named UEFN build are stated as historical
and build-specific, never as current or universal claims.

## Benchmark disclosure — decision lock

The explainer and the Release-note draft carry this public disclosure
verbatim. Markdown line wrapping is allowed; no wording change is:

A controlled comparison was planned. The only live attempt was rejected:
logged cadence did not establish the required foreground condition, and the
project was saved during the session. No accepted comparison, performance
ranking, compatibility finding or bridge-replacement conclusion exists.

The X draft cannot hold that text within 280 characters, so it carries exactly
this owner-fixed short form (166 characters) instead:

A controlled comparison's only live attempt was rejected; no accepted
comparison, performance ranking, compatibility finding, or bridge-replacement
conclusion exists.

No other or improvised disclosure wording is used. Drafting rule, not public
text: publish no rejected timing figures. No WO-006 timing figure, no
performance or quality comparison between Epic's official MCP and the bridge
(such as faster, slower, or more reliable), and no suggestion that the bridge
is obsolete, replaceable, or deprecated appears in any output. Evidence-backed
capability descriptions remain allowed.

## Proposed Session A — repository explainer and draft variants

Proposed output paths. The owner chose to propose the two list entries
alongside the explainer; this revision implements none of them:

- `docs/OFFICIAL_MCP_AND_TOOLBELT.md`: the one repository explainer;
- `scripts/drift_check.py`: one `SCAN_FILES` entry for that path, so its tool
  and category counts are drift-checked like other documentation surfaces;
- `tests/test_repo_integrity.py`: the matching required scan-target entry;
- private, outside the repository, in
  `C:\Users\ocean\UEFN-Toolbelt-Evidence\WO-007\session-a\`: a Release-note
  draft and an X draft, each kept as public copy separate from private
  claim-to-source notes.

The explainer contains:

- a capability matrix with one column for Epic's official MCP toolsets and one
  for Toolbelt's bridge;
- the launch-boundary sequence for Verse compilation and play sessions, which
  Epic's official server provides and Toolbelt's in-editor Python does not;
- the recovery guidance for Quirk #36 when the MCP Toolsets beta suppresses
  `init_unreal.py`, stated in its UEFN 42.00 context with the one 42.20 boot on
  which it did not occur (not a demonstrated fix), and the project-Python rule
  before Launch Session, Push Changes, or publishing;
- the security boundary: the bridge's experimental status; authenticated
  same-user loopback; no browser origins; no arbitrary remote Python; the
  handoff file as privileged local material; and its stated non-defences, that
  loopback plus a bearer token is not a sandbox and there is no defence against
  a compromised same-user account;
- known official-MCP quirks, sourced from the audit's P1 items 4 and 5 and P2
  item 4 and labelled as observed on UEFN 42.00;
- an evidence-gaps section: the benchmark disclosure above; modal detection
  deferred by WO-004; the WO-004 limits named in the evidence sources above
  (the one build and boot, outcome rows not exercised live, static-only proxy
  and redirect protections, no MCP-host, stdio, or FastMCP integration, and no
  exactly-once claim); and the difference between coverage categories and live
  verification.

Acceptance criteria:

- each explainer section and each capability-matrix row links its repository
  evidence source and the relevant section, with the observed build where one
  applies; a claim without one is removed rather than softened;
- no sentence presents Toolbelt as reachable through Epic's official MCP
  server, or presents a coverage category or static test as live verification;
- the explainer and the Release-note draft contain the verbatim disclosure, the
  X draft contains the short form exactly, and no WO-006 timing figure appears;
- Release-note public copy: at most 400 words, including the disclosure;
- X public copy: ASCII only, no URL, at most 280 characters, counted with
  Python `len()` over the exact text excluding only its single final newline,
  with internal newlines counted;
- each draft records its public-copy word or character count and SHA-256
  separately from the draft text, and keeps private claim-to-source notes
  outside its public-copy count;
- both draft variants agree with the explainer and carry no claim the
  explainer lacks;
- `scripts/drift_check.py` scans the new path and passes, with tool and
  category counts matching the registry;
- the work-order contract raises nothing, and `ruff`, `mypy`, and the tests
  affected by the scan-target change pass.

Exclusions: no runtime, bridge, client, or Epic-policy code change; no new
tool; no benchmark, rehearsal, or live measurement; no change to the WO-006
record; no new governance mechanism; and no checker logic beyond the one
scan-target entry.

Deferred: any external publication of the explainer or drafts, and any new
benchmark.

Cleanup duties: private drafts and review material stay outside the
repository; no UEFN project file, editor session, or listener is involved; the
worktree ends with exactly the three proposed repository paths changed,
unstaged, for independent review.

Proportional checks: `drift_check`, `ruff`, `mypy`, whitespace checks, and the
affected repository-integrity tests. A full-suite run is needed only if the
owner asks for it. Any push needs its own owner gate, and its CI must reach a
successful terminal conclusion before status evidence is recorded.

Proposed live-verification exemption, offered for the owner's decision and
not accepted by this proposal: Session A's whole scope is the explainer, one
`SCAN_FILES` entry in `scripts/drift_check.py`, the matching scan-target entry
in `tests/test_repo_integrity.py`, and the two private drafts outside the
repository. It runs nothing in UEFN and touches no runtime path, so its
verification would be offline only. The owner may accept it, narrow it, or
require a live check at the Session A gate.

## WO-007 issuance constraints

Issuing WO-007 must:

- keep the root pointer's "Release-train amendment (owner decision)"
  paragraph visible and unchanged in substance: the frozen train stays WO-001
  through WO-007; WO-006 stays resolved as superseded, never relabelled
  completed, with its unmet requirements recorded in its mandate; the train is
  complete only when WO-001 through WO-005 and WO-007 are completed and WO-006
  remains superseded; and the amendment opens no session and grants nothing.
  Only its WO-007 status clause changes, to WO-007's issued state with every
  session still unauthorized;
- keep the release gate closed: the final integration/repository-truth audit
  and a separate owner release decision remain required;
- leave the superseded WO-006 record and its checks unchanged.

This revision makes no checker change and edits neither `WORKORDER.md` nor the
WO-006 record. Any checker update for WO-007's issuance belongs to that later,
separately reviewed transition.

## Authority boundaries

Independent pre-issuance review, issuance, Session A, each commit, each push,
and any publication are separate owner gates; none implies the next. The
release version stays undecided. Tags, GitHub Releases, repository-description
and other repository-metadata edits, branch-protection edits, and social posts
all remain unauthorized.

Decision lock: drafting grants no authority to publish, change the repository
description, create a Release, or post socially. Every external action requires
its own owner gate.

NEXT GATE: separate owner decision on Session A authorization, recorded in root
`WORKORDER.md`, together with the owner's decision on its proposed
live-verification exemption. Issuance authorizes no session, and this mandate
grants no review, commit, push, or session authority.
