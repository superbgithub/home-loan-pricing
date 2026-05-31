<!--
## Sync Impact Report
- Version change: (none) → 1.0.0
- Added sections: Core Principles (I–V), Technology Constraints, Development Workflow, Governance
- Removed sections: N/A (initial creation from template)
- Templates requiring updates:
  - .specify/templates/plan-template.md ✅ aligned (Constitution Check section present)
  - .specify/templates/spec-template.md ✅ aligned (no constitution-specific sections required)
  - .specify/templates/tasks-template.md ✅ aligned (phase structure consistent with principles)
- Deferred TODOs: None
-->

# Home Loan Pricing Constitution

## Core Principles

### I. Financial Precision
All monetary calculations MUST use fixed-point or decimal arithmetic (never IEEE 754
floating point) to prevent rounding errors in loan amounts, interest rates, and payments.
Currency values MUST be stored and transmitted in the smallest representable unit (e.g.,
cents for USD). Rounding rules MUST follow applicable regulatory standards (e.g.,
Regulation Z half-up rounding for APR disclosures).

### II. Regulatory Compliance
Loan pricing logic MUST comply with applicable federal and state lending laws, including
TILA (Truth in Lending Act), RESPA, ECOA, and state usury caps. Any pricing rule with a
legal basis MUST reference the specific regulation it implements as a code comment or
linked document. Compliance checks MUST execute before any rate or fee is surfaced to
an end user.

### III. Test-First (NON-NEGOTIABLE)
TDD is mandatory for all pricing logic, rate calculations, and compliance rules. Tests
MUST be written and confirmed to fail before any implementation begins. The
Red-Green-Refactor cycle is strictly enforced. No implementation task is considered
started until its corresponding test exists and is red.

### IV. Auditability
Every pricing decision, rate change, or fee adjustment MUST be logged with a timestamp,
actor identity, inputs, and outputs. Audit logs MUST be immutable and retained per
applicable regulatory retention requirements. Pricing engine outputs MUST be reproducible
from stored inputs alone; no hidden mutable state is permitted in the pricing pipeline.

### V. Simplicity & YAGNI
Features are added only when there is a confirmed, documented requirement. Abstractions
are introduced only when at least three concrete use cases exist. Complexity MUST be
justified in writing in the implementation plan (Complexity Tracking table) before any
implementation begins.

## Technology Constraints

- Monetary values MUST be represented using a `Decimal` type or language-equivalent
  (not `float` / `double`).
- All external inputs (rates, loan amounts, borrower data) MUST be validated at system
  boundaries before processing; trust no upstream caller.
- No personally identifiable information (PII) may be written to logs in plain text;
  structured logging MUST mask or omit sensitive fields.
- Dependencies MUST be pinned to exact versions in lockfiles; open version ranges are
  not permitted in production manifests.

## Development Workflow

- All features begin with `/speckit-specify` → `/speckit-plan` → `/speckit-tasks`
  before any code is written.
- A Constitution Check (per plan-template.md) MUST pass before Phase 0 research and
  again after Phase 1 design.
- Pull requests require at least one peer review and all CI checks green before merge.
- No feature flag or backwards-compatibility shim may be introduced without explicit
  justification recorded in the implementation plan.

## Governance

This constitution supersedes all other development practices. Amendments require:

1. A written proposal describing the change and its rationale.
2. Explicit approval by the project lead.
3. A migration plan for any existing code that would violate the updated principle.
4. A version bump following the policy below.

**Versioning policy**:
- MAJOR: Principle removals, redefinitions, or backward-incompatible governance changes.
- MINOR: New principle or section added, or materially expanded guidance.
- PATCH: Clarifications, wording fixes, or non-semantic refinements.

All PRs and code reviews MUST verify compliance with this constitution. Violations MUST
be documented in the plan's Complexity Tracking table before implementation begins.

**Version**: 1.0.0 | **Ratified**: 2026-05-30 | **Last Amended**: 2026-05-30
