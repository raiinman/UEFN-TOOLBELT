# Offline tooling and hooks

Read the repository-root AGENTS.md and every parent AGENTS.md before editing this subtree.

## Purpose

- Consistency checks, registry-derived coverage, API manifests, editor-session staging, and agent hooks.

## Ownership

- Owns script files and coverage_evidence.json; root batch wrappers and tool configuration remain root-owned.

## Local Contracts

- coverage_report.py owns offline registry enumeration used by drift_check.py; preserve the shared source of truth.
- Coverage mappings distinguish source coverage from observed run evidence.
- session_python.ps1 owns the prepare/restore manifest workflow; preserve exact restoration and the root wrapper contracts.

## Work Guidance

- Read each script entry point and existing targeted tests before changing its behavior.
- Generated coverage and API artifacts must remain reproducible from their named sources.

## Verification

- Run the configured lint/type checks and the relevant tests/test_coverage_report.py, tests/test_api_manifest.py, tests/test_push_guard.py, or tests/test_session_python_workflow.py checks.
- Run python scripts/drift_check.py and python scripts/coverage_report.py --check from the repository root.

## Child DOX Index

No child DOX documents. This guide owns the remaining subtree.
