# Registered editor tools

Read the repository-root AGENTS.md and every parent AGENTS.md before editing this subtree.

## Purpose

- Feature-domain modules registered through tools/__init__.py.

## Ownership

- Owns registered tool implementations, the integration suite, and the custom bridge in this directory. Root-level tools/ is a separate utility directory.

## Local Contracts

- Read .claude/rules/tool_authoring.md and CONTRIBUTING.md from the repository root for tool contracts and registration changes.
- Search the registry for overlapping behavior before adding tools.
- Preserve structured results, editor-main-thread execution, undo transactions for mutations, bounded asset scans, and keyword Unreal struct arguments.
- mcp_bridge.py follows SECURITY.md; Toolbelt custom MCP and Epic official MCP remain distinct surfaces.

## Work Guidance

- Read docs/UEFN_QUIRKS.md before Unreal API edits and docs/ui_style_guide.md before window edits.
- Read .claude/rules/verse_authoring.md before Verse-generation work.
- When adding tools, update the package counts, explicit dashboard wiring, relevant inventories, and API manifest as applicable.

## Verification

- Run applicable off-editor tests and python scripts/drift_check.py from the repository root.
- New modules and persistent-window changes need a full UEFN restart after deploy; follow the root live-test workflow.
- The integration suite mutates editor state; use its documented live procedure and authorization.

## Child DOX Index

No child DOX documents. This guide owns the remaining subtree.
