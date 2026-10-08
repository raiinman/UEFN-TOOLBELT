# Claude Code support

Read the repository-root AGENTS.md and every parent AGENTS.md before editing this subtree.

## Purpose

- Scoped rules, specialized-agent definitions, commands, hooks, and reference tables.

## Ownership

- Owns agents/, commands/, hooks/, rules/, settings.local.json, mcp_reference.md, and tool_tables.md. Root CLAUDE.md remains root-owned.

## Local Contracts

- Keep scoped rules aligned with the root agent guide and CONTRIBUTING.md.
- Tool tables describe the registry; mcp_reference.md describes the custom bridge and must preserve SECURITY.md trust and client-outcome boundaries.

## Work Guidance

- Read rules/tool_authoring.md for tool-authoring guidance and rules/verse_authoring.md for Verse work.
- Update only the relevant command, hook, agent definition, or reference; preserve permission scope in settings.

## Verification

- Run python scripts/drift_check.py from the repository root.
- For hook or bridge-reference changes, run the relevant tests/test_push_guard.py or tests/test_mcp_security.py checks.

## Child DOX Index

No child DOX documents. This guide owns the remaining subtree.
