# Shared runtime utilities

Read the repository-root AGENTS.md and every parent AGENTS.md before editing this subtree.

## Purpose

- Utilities used by editor tools and the dashboard.

## Ownership

- Owns this directory: shared helpers, persistent configuration, activity logging, safety gates, theme, and base window.

## Local Contracts

- core/ provides helpers rather than tool registrations.
- Use the existing project-mount helper for asset paths and theme.py for shared UI colors.
- Mount detection reads the native descriptor's root plugin before falling back to the containing folder. UUID mounts must retain their identity.
- Default scan and destination resolution refuse unknown/reserved project mounts instead of falling back to Fortnite's `/Game` content. Explicit read paths retain their identity.
- Tool windows inherit ToolbeltWindow; persistent Qt/Slate state affects restart requirements.

## Work Guidance

- Read docs/ui_style_guide.md from the repository root before changing base_window.py or theme.py.
- Preserve existing configuration and logging contracts; caller-visible changes must be reflected in owning docs.

## Verification

- Run relevant tests/test_config.py and tests/test_dashboard_liveness.py checks, the configured type check, and drift check.
- For runtime acceptance, deploy first and follow the root guide; Qt/window lifecycle changes need a full restart.

## Child DOX Index

No child DOX documents. This guide owns the remaining subtree.
