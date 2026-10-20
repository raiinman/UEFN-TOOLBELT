# Shared runtime utilities

Read the repository-root AGENTS.md and every parent AGENTS.md before editing this subtree.

## Purpose

- Utilities used by editor tools and the dashboard.

## Ownership

- Owns this directory: shared helpers, persistent configuration, activity logging, safety gates, theme, and base window.

## Local Contracts

- core/ provides helpers rather than tool registrations.
- Use the existing project-mount helper for asset paths and theme.py for shared UI colors.
- Mount detection reads the unique native descriptor's root plugin even after a project folder rename. Existing ambiguous, unreadable or root-less descriptors must refuse guessed destinations. A descriptor-free legacy folder may use its name. UUID mounts retain their identity.
- Default scan and destination resolution refuse unknown/reserved project mounts instead of falling back to Fortnite's `/Game` content. Explicit read paths retain their identity.
- Tool windows inherit ToolbeltWindow; persistent Qt/Slate state affects restart requirements.

- native_project_dir() and project_content_dir() require the deployed package and a unique native descriptor; never substitute FortniteGame paths for native filesystem reads or writes.
- Persistent configuration is per native project under Saved/UEFN_Toolbelt/config.json. Legacy shared config stays intact; migration admits ordinary preferences and paths belonging to the current project, never another island's Verse/import destination. Unknown identity gives defaults-only nonwritable configuration.
- Configuration saves replace files atomically and roll back cached values on failure. Unreadable or malformed existing files refuse writes. Public tb.config resolves the current project configuration on access.

## Work Guidance

- Read docs/ui_style_guide.md from the repository root before changing base_window.py or theme.py.
- Preserve existing configuration and logging contracts; caller-visible changes must be reflected in owning docs.

## Verification

- Run relevant tests/test_config.py and tests/test_dashboard_liveness.py checks, the configured type check, and drift check.
- For runtime acceptance, deploy first and follow the root guide; Qt/window lifecycle changes need a full restart.

## Child DOX Index

No child DOX documents. This guide owns the remaining subtree.
