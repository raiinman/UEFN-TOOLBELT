# Registered editor tools

Read the repository-root AGENTS.md and every parent AGENTS.md before editing this subtree.

## Purpose

- Feature-domain modules registered through tools/__init__.py.

## Ownership

- Owns registered tool implementations, the integration suite, and the custom bridge in this directory. Root-level tools/ is a separate utility directory.

## Local Contracts

- Read .claude/rules/tool_authoring.md and CONTRIBUTING.md from the repository root for tool contracts and registration changes.
- Search the registry for overlapping behavior before adding tools.
- AssetData reads use `asset_class_path.asset_name` and object paths built from `package_name.asset_name`; removed `asset_class` and `object_path` attributes must not return.
- Preserve structured results, editor-main-thread execution, undo transactions for mutations, bounded asset scans, and keyword Unreal struct arguments.
- FBX imports use current static-mesh properties, generated collision and `generate_lightmap_u_vs`; do not restore the removed adjacency option.
- Bridge asset searches use path metadata and class-name filtering without mutable ARFilter properties; return at most 200 assets and report total count/truncation.
- Bridge transforms use EditorActorSubsystem.set_actor_transform in an undo transaction. A refused move raises an error; omitted transform parts stay unchanged.
- Publish audit recognizes native player spawner devices and legitimate system actors, scans redirectors only in the user mount, and shares the build service's editor-log selection and latest-build scan. Unavailable checks remain unknown rather than passing.
- `verse_build_status` counts unique diagnostics in the latest completed compile, accepts current range and legacy locations, and clears earlier errors after a successful build. Preserve duplicate suppression and consecutive-failure boundaries.
- `select_by_verse_tag` defaults to an explicit unsupported VerseTagMarkup result; ordinary Actor.tags require tag_scope='actor'. Never treat ordinary actor metadata or an unreadable tag scan as a verified Verse-tag match/absence. Preserve selection on unsupported/unreadable scans.
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
