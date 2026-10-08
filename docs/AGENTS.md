# Project documentation

Read the repository-root AGENTS.md and every parent AGENTS.md before editing this subtree.

## Purpose

- Operational guides, schemas, visuals, and evidence-oriented reference material.

## Ownership

- Owns documentation, schemas, curated stubs, images, changelog, and DOX_LICENSE.txt directly in docs/. Delegates audits/ and work-orders/ below. Root project documents remain root-owned.

## Local Contracts

- Preserve the distinction between source inspection, mock/static checks, recorded live evidence, and unverified behavior.
- Use TOOL_STATUS.md and scripts/coverage_evidence.json as the coverage sources; generated schema/stub material remains reference evidence.
- DOX instructions were adapted from raiinman/dox; retain DOX_LICENSE.txt with distributed copies.

## Work Guidance

- Update the guide that owns the changed behavior; keep links and evidence claims grounded in current files.
- Preserve UEFN quirks, UI standards, plugin contracts, and pipeline boundaries when updating their guides.

## Verification

- Check changed local links and run python scripts/drift_check.py from the repository root.
- For coverage references, use python scripts/coverage_report.py --check.

## Child DOX Index

- [audits/AGENTS.md](audits/AGENTS.md) — Accepted audits, feasibility findings, and preserved run evidence.
- [work-orders/AGENTS.md](work-orders/AGENTS.md) — Mandates and state records subject to the root authority pointer.
