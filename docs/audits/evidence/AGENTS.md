# Preserved audit evidence

Read the repository-root AGENTS.md and every parent AGENTS.md before editing this subtree.

## Purpose

- Source artifacts supporting the parent audit records.

## Ownership

- Owns evidence files and run-specific directories beneath this path.

## Local Contracts

- Keep raw artifacts, derived artifacts, provenance, and redactions distinguishable.
- Recorded files establish only the observations documented by their provenance and accepted scope.

## Work Guidance

- Preserve original evidence and its checksums; document authorized corrections in the owning audit record.
- Apply the project security/redaction contract to any new captured artifact.

## Verification

- Check SHA256SUMS.txt where present and run relevant tests/test_session_b_evidence.py or tests/test_manifest_attribution.py checks.

## Child DOX Index

No child DOX documents. This guide owns the remaining subtree.
