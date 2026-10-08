# Verification suites

Read the repository-root AGENTS.md and every parent AGENTS.md before editing this subtree.

## Purpose

- Off-editor contract/regression tests and the separate live smoke-test entry point.

## Ownership

- Owns conftest.py, test_*.py, and smoke_test.py in this directory.

## Local Contracts

- conftest.py supplies a fake unreal module for off-editor tests; passing those tests establishes no live UEFN behavior.
- pyproject.toml defines test collection; smoke_test.py is a separate live-editor entry point.
- Keep tests isolated from real project state and preserve evidence categories when testing coverage reports.

## Work Guidance

- Add regression coverage for the actual changed contract using existing fixtures and temporary paths.

## Verification

- Run python -m pytest from the repository root; narrow to affected test files during iteration.
- Use .agents/workflows/run_tests.md for authorized live verification.

## Child DOX Index

No child DOX documents. This guide owns the remaining subtree.
