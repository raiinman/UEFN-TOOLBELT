# GitHub automation

Read the repository-root AGENTS.md and every parent AGENTS.md before editing this subtree.

## Purpose

- Repository CI workflows.

## Ownership

- Owns workflows/; release and publication authority remain in the root policy.

## Local Contracts

- CI uses the off-editor checks and Python version declared in workflows/ci.yml and pyproject.toml.
- CI results establish static/mock coverage only; preserve the distinction from live UEFN verification.

## Work Guidance

- Keep workflow commands consistent with requirements-dev.txt and the tooling configuration.

## Verification

- Run the applicable CI commands locally; after an authorized push, inspect the actual required CI jobs through completion.

## Child DOX Index

No child DOX documents. This guide owns the remaining subtree.
