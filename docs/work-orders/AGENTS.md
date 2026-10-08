# Work Order records

Read the repository-root AGENTS.md and every parent AGENTS.md before editing this subtree.

## Purpose

- Proposed, issued, completed, and superseded mandates.

## Ownership

- Owns README.md and the state directories proposed/, issued/, completed/, and superseded/. Root WORKORDER.md remains the sole current-state authority pointer.

## Local Contracts

- Read README.md for state definitions, mandate contents, and owner gates.
- Only root WORKORDER.md may name the current issued Work Order and authorized session.
- Proposed mandates grant no implementation authority; file moves do not themselves authorize state transitions.

## Work Guidance

- Preserve accepted scope, unmet requirements, evidence boundaries, and separate owner gates when revising mandates.

## Verification

- Run relevant tests/test_repo_integrity.py checks and drift check from the repository root.
- Check state-directory, mandate, and root-pointer consistency for any authorized transition.

## Child DOX Index

No child DOX documents. This guide owns the remaining subtree.
