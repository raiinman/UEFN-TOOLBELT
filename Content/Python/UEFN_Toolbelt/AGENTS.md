# Editor runtime package

Read the repository-root AGENTS.md and every parent AGENTS.md before editing this subtree.

## Purpose

- The deployable Python runtime: registry, entry points, dashboard, diagnostics, and shared schemas.

## Ownership

- Owns package-level files, including __init__.py, registry.py, dashboard_pyside6.py, menu.py, epic_toolset.py, schema_utils.py, diagnostics.py, smoke_test.py, list_untested.py, and api_dependencies.json. Delegates core/ and tools/ below.

## Local Contracts

- registry.py is the shared tool-registration/execution contract; tools/__init__.py activates registrations.
- Root __init__.py constants are the source of truth for inventory and version. Tool additions update counts; release version changes require their own authorized session.
- Dashboard reachability is explicitly wired; registration alone does not surface a tool in the UI.
- `debug_audit_verse_assets` scans the resolved project mount and reports at most 200 metadata matches. Its name-based candidates do not prove an asset is a usable Verse-generated Blueprint.
- Dashboard and tool windows use normal desktop stacking. Reopening the dashboard restores minimized windows and raises and activates both hidden and visible windows; keep its tool windows accessible without an always-on-top dashboard.

## Work Guidance

- Before Unreal API changes, read docs/UEFN_QUIRKS.md from the repository root.
- Before dashboard or window work, read docs/ui_style_guide.md from the repository root.
- For bridge or official-toolset changes, read SECURITY.md and .claude/mcp_reference.md from the repository root.

## Verification

- From the repository root, run the configured static checks and python scripts/drift_check.py.
- Regenerate api_dependencies.json with python scripts/gen_api_manifest.py when Unreal API calls change.
- Runtime acceptance follows the deploy and live-test workflow in the root guide.

## Child DOX Index

- [core/AGENTS.md](core/AGENTS.md) — Shared utilities, configuration, logging, safety, theme, and window lifecycle.
- [tools/AGENTS.md](tools/AGENTS.md) — Registered editor tools and their domain modules.
