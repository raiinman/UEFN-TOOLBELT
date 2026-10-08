# Community plugin examples

Read the repository-root AGENTS.md and every parent AGENTS.md before editing this subtree.

## Purpose

- Reference custom plugins loaded through the Toolbelt plugin system.

## Ownership

- Owns example plugin Python files; the Plugin Hub index registry.json stays root-owned.

## Local Contracts

- Follow docs/plugin_dev_guide.md and CONTRIBUTING.md from the repository root for plugin discovery, registration, scanner limits, and distribution.
- Community plugins do not change the core release version or core tool counts.
- Registered plugin functions follow the same structured result contract as core tools.

## Work Guidance

- Use the existing examples and plugin-development guide when extending a plugin; keep any authorized registry.json listing consistent with the plugin.

## Verification

- Run relevant repository integrity/contract checks and drift check.
- Live plugin acceptance uses the deploy/load/test workflow in the root guide.

## Child DOX Index

No child DOX documents. This guide owns the remaining subtree.
