# UEFN Toolbelt — Agent Guide

> For AI agents working with this codebase. Read this before making any changes.

## What this repo is

Python automation framework for Unreal Editor for Fortnite (UEFN).
362 tools, 55 categories, PySide6 dashboard, and Toolbelt's own custom bridge.
An MCP client can reach that bridge through `mcp_server.py`, configured in a
local, gitignored `.mcp.json` copied from `.mcp.json.template`. MCP-host
integration is untested since the WO-001/WO-004 hardening.
The bridge is Toolbelt's own authenticated, same-user loopback HTTP listener — not
Epic's official UEFN MCP server, which Toolbelt is not reachable through.

## Non-negotiable rules

1. **Never commit without a live UEFN test.** Syntax passing ≠ working in the editor.
2. **Always run `deploy.bat` before testing.** Repo and UEFN project are separate directories. For nonstandard locations use `deploy.bat "C:\path\to\project" /nopause`; unattended mode skips optional dependency installation and preserves existing `init_unreal.py` byte-for-byte. Inspect the startup hook separately; a preserved hook does not prove startup works.
   `install.py` stages package updates before replacement and restores the prior package if replacement fails. It preserves managed startup hooks and an unchanged default loader, and writes a destination build stamp.
   Use `--skip-dependencies` when retaining existing dashboard libraries. External adapter dependencies are declared separately in `requirements-mcp.txt`; editor installs do not consume that file.
3. **Run `python scripts/drift_check.py` before every commit.** Must return PASS.
4. **Bump `__tool_count__` and `__category_count__`** in `Content/Python/UEFN_Toolbelt/__init__.py` when adding tools.
5. **Full UEFN restart required** when adding a new module to `tools/__init__.py`. Nuclear reload crashes. See `docs/UEFN_QUIRKS.md` Quirk #26.
6. **All tool functions must return `{"status": "ok"/"error", ...}`** — never None, never a bare primitive.

7. **Never build an `unreal.*` struct with positional args.** Their order follows
   the C++ field declaration, not the order the docs describe them in.
   Confirmed live on UEFN 42.00:

   ```python
   unreal.Rotator(10, 20, 30)   # roll=10  pitch=20  yaw=30   (NOT pitch,yaw,roll)
   unreal.Color(10, 20, 30)     # r=30     g=20      b=10     (FColor is B,G,R,A)
   ```

   `unreal.Rotator(0, yaw, 0)` sets *pitch* and nothing raises, so props tilt
   instead of turning. `unreal.Color(r, g, b, 255)` swaps red and blue. 31
   Rotator sites and one Color site were wrong this way before it was caught.
   Use keyword args: `unreal.Rotator(roll=0, pitch=0, yaw=yaw)`.
   `tests/test_rotator_argument_order.py` fails the build if this returns.
   See `docs/UEFN_QUIRKS.md` Quirk #41.
8. **Check the registry before building anything** — 362 tools exist. Search first:
   ```bash
   grep -rh 'name="' Content/Python/UEFN_Toolbelt/tools/ --include="*.py" \
     | grep -o 'name="[^"]*"' | sed 's/name="//;s/"//' | sort | grep <keyword>
   ```
9. **Project `.py` files block remote validation.** Before Launch Session, Push
   Changes, or publishing on UEFN 42.00, run `prepare_launch.bat`; after the
   upload completes, run `restore_after_launch.bat`. `.urcignore` does not gate
   Valkyrie staging. See `docs/UEFN_QUIRKS.md` Quirk #42.
10. **Keep owner authorization gates separate.** Implementation, independent
    review, commit, push, tag, GitHub Release, and social publication are
    distinct actions. Authorization for one never implies the next. Leave work
    uncommitted for review unless the owner explicitly authorizes the exact
    commit; never move an existing tag.
11. **Cold-start from `WORKORDER.md`.** It is the sole pointer allowed to name
    the current issued Work Order and authorized session. Files under
    `docs/work-orders/proposed/` are planning only and never grant implementation
    authority. If either current field says `NONE`, stop at the corresponding
    owner gate.

## Key files for agents

| File | What to read for |
|---|---|
| `WORKORDER.md` | Current issued Work Order, authorized session, base, and exact gate; `NONE` means stop |
| `CLAUDE.md` | Full project context, mandatory rules, all tool tables |
| `SECURITY.md` | Current trust boundary and fixed security issues; the custom bridge remains experimental after WO-001's hardening |
| `docs/audits/2026-08-24-uefn-42-official-mcp-audit.md` | Accepted official-MCP, coexistence, security, and repository-truth evidence |
| `docs/work-orders/README.md` | Work Order states, required contents, and gate sequence |
| `docs/UEFN_QUIRKS.md` | Non-obvious UEFN Python behaviors — read before touching any API |
| `docs/PIPELINE.md` | 6-phase autonomous game-building pipeline |
| `docs/ui_style_guide.md` | Mandatory for any PySide6 window work |
| `TOOL_STATUS.md` | Per-tool test coverage — check before assuming a tool is tested |
| `ARCHITECTURE.md` | System design, directory map, data flow |
| `scripts/drift_check.py` | Run this — validates version/count consistency across docs and agent context |
| `.agents/workflows/` | Step-by-step workflows: `add_new_tool.md`, `run_tests.md` |

## Specialized agents in this repo

See `.claude/agents/` for focused agent definitions:
- **`verse-deployer`** — Verse codegen + error fix loop (Phases 5–7 of the pipeline)
- **`tool-developer`** — Builds new tools: registry audit → write → drift check → test instructions

## Quick orientation

```bash
# See every registered tool name
grep -rh 'name="' Content/Python/UEFN_Toolbelt/tools/ --include="*.py" \
  | grep -o 'name="[^"]*"' | sed 's/name="//;s/"//' | sort

# Validate codebase consistency
python scripts/drift_check.py

# Syntax check a tool file
python -c "import ast; ast.parse(open('Content/Python/UEFN_Toolbelt/tools/your_tool.py').read()); print('OK')"
```

## Deploy + test workflow

```
deploy.bat                          → sync repo → UEFN project
[full restart for startup/window changes; tb.hard_reload() otherwise] → reload safely
tb.run("tool_name")                 → test live
[user confirms output]              → leave the complete change uncommitted
[independent review accepts]         → owner may authorize the exact commit
[owner separately authorizes push]  → push and monitor CI to completion
```

For Launch Session / Push Changes validation:

```
prepare_launch.bat                  → verify zero project .py files
[Launch Session or Push Changes]    → wait for remote validation
restore_after_launch.bat            → restore the manifest exactly
```

---

# DOX framework

- DOX is the AGENTS.md hierarchy installed here
- Agent must follow DOX instructions across any edits

## Core Contract

- AGENTS.md files are binding work contracts for their subtrees
- Work products, source materials, instructions, records, assets, and durable docs must stay understandable from the nearest applicable AGENTS.md plus every parent AGENTS.md above it

## Read Before Editing

1. Read the root AGENTS.md
2. Identify every file or folder you expect to touch
3. Walk from the repository root to each target path
4. Read every AGENTS.md found along each route
5. If a parent AGENTS.md lists a child AGENTS.md whose scope contains the path, read that child and continue from there
6. Use the nearest AGENTS.md as the local contract and parent docs for repo-wide rules
7. If docs conflict, the closer doc controls local work details, but no child doc may weaken DOX

Do not rely on memory. Re-read the applicable DOX chain in the current session before editing.

## Update After Editing

Every meaningful change requires a DOX pass before the task is done.

Update the closest owning AGENTS.md when a change affects:

- purpose, scope, ownership, or responsibilities
- durable structure, contracts, workflows, or operating rules
- required inputs, outputs, permissions, constraints, side effects, or artifacts
- user preferences about behavior, communication, process, organization, or quality
- AGENTS.md creation, deletion, move, rename, or index contents

Update parent docs when parent-level structure, ownership, workflow, or child index changes. Update child docs when parent changes alter local rules. Remove stale or contradictory text immediately. Small edits that do not change behavior or contracts may leave docs unchanged, but the DOX pass still must happen.

## Hierarchy

- Root AGENTS.md is the DOX rail: project-wide instructions, global preferences, durable workflow rules, and the top-level Child DOX Index
- Child AGENTS.md files own domain-specific instructions and their own Child DOX Index
- Each parent explains what its direct children cover and what stays owned by the parent
- The closer a doc is to the work, the more specific and practical it must be

## Child Doc Shape

- Create a child AGENTS.md when a folder becomes a durable boundary with its own purpose, rules, responsibilities, workflow, materials, or quality standards
- Work Guidance must reflect the current standards of the project or user instructions; if there are no specific standards or instructions yet, leave it empty
- Verification must reflect an existing check; if no verification framework exists yet, leave it empty and update it when one exists

Default section order:
- Purpose
- Ownership
- Local Contracts
- Work Guidance
- Verification
- Child DOX Index

## Style

- Keep docs concise, current, and operational
- Document stable contracts, not diary entries
- Put broad rules in parent docs and concrete details in child docs
- Prefer direct bullets with explicit names
- Do not duplicate rules across many files unless each scope needs a local version
- Delete stale notes instead of explaining history
- Trim obvious statements, repeated rules, misplaced detail, and warnings for risks that no longer exist

## Closeout

1. Re-check changed paths against the DOX chain
2. Update nearest owning docs and any affected parents or children
3. Refresh every affected Child DOX Index
4. Remove stale or contradictory text
5. Run existing verification when relevant
6. Report any docs intentionally left unchanged and why

## User Preferences

When the user requests a durable behavior change, record it here or in the relevant child AGENTS.md.

## Project Ownership

The root owns repository-wide policy, root files, deployment/install and launch wrappers,
external clients, root inventories/configuration, and paths not delegated below.
DOX traversal and documentation maintenance preserve the existing review, live-test,
and owner authorization gates.

Adapted from [raiinman/dox](https://github.com/raiinman/dox/blob/b88194c34ace1a2a3dc01831d36b8a65986a41f5/AGENTS.md).
Copyright (c) 2026 Agent Zero; [MIT license](docs/DOX_LICENSE.txt).
Only the reusable framework is installed; DOX's own file inventory and README
presentation instructions do not apply to this project.

## Child DOX Index

- [.agents/AGENTS.md](.agents/AGENTS.md) — Step-by-step contributor and live-test workflows.
- [.claude/AGENTS.md](.claude/AGENTS.md) — Scoped rules, specialized-agent definitions, commands, hooks, and reference tables.
- [.github/AGENTS.md](.github/AGENTS.md) — Repository CI workflows.
- [Content/Python/UEFN_Toolbelt/AGENTS.md](Content/Python/UEFN_Toolbelt/AGENTS.md) — The deployable Python runtime: registry, entry points, dashboard, diagnostics, and shared schemas.
- [community_plugins/AGENTS.md](community_plugins/AGENTS.md) — Reference custom plugins loaded through the Toolbelt plugin system.
- [docs/AGENTS.md](docs/AGENTS.md) — Operational guides, schemas, visuals, and evidence-oriented reference material.
- [scripts/AGENTS.md](scripts/AGENTS.md) — Consistency checks, registry-derived coverage, API manifests, editor-session staging, and agent hooks.
- [tests/AGENTS.md](tests/AGENTS.md) — Off-editor contract/regression tests and the separate live smoke-test entry point.
- [tools/AGENTS.md](tools/AGENTS.md) — Auxiliary inspection scripts outside the registered Toolbelt tool package.
