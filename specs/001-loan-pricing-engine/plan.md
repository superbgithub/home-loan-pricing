# Implementation Plan: Loan Pricing Engine

**Branch**: `001-loan-pricing-engine` | **Date**: 2026-05-30 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-loan-pricing-engine/spec.md`

## Summary

Build a Python library that calculates monthly mortgage payments and APR for fixed-rate
and adjustable-rate (ARM) home loans, exposed via a FastAPI HTTP service. All monetary
arithmetic uses `decimal.Decimal` (never float). APR follows the Regulation Z actuarial
method. Every pricing request produces an immutable JSON audit log entry.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: fastapi, pydantic v2, uvicorn, pytest, pytest-asyncio, httpx

**Storage**: N/A — stateless calculation engine; audit records emitted to stdout as
structured JSON (no database).

**Testing**: pytest + pytest-asyncio + httpx (contract tests against live FastAPI app)

**Target Platform**: Linux server; Docker-friendly (12-factor, stdout logging)

**Project Type**: Library (core engine) + FastAPI web service (thin HTTP layer)

**Performance Goals**: Single pricing request < 50ms wall-clock (CPU-bound Decimal math)

**Constraints**: All monetary arithmetic in `decimal.Decimal`; Regulation Z half-up
rounding at display boundaries only; no float anywhere in the pricing pipeline.

**Scale/Scope**: v1 single-instance; batch comparison limited to 5 scenarios per request.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate | Status |
|-----------|------|--------|
| I. Financial Precision | All monetary values use `decimal.Decimal`; ROUND_HALF_UP only at display | ✅ PASS |
| II. Regulatory Compliance | APR uses Reg Z Appendix J actuarial method; ARM APR uses initial-rate assumption | ✅ PASS |
| III. Test-First | Tests written and confirmed failing before any implementation task begins | ✅ PASS (enforced in tasks) |
| IV. Auditability | Every pricing call emits one JSON audit line to stdout; no silent failures | ✅ PASS |
| V. Simplicity & YAGNI | Single project; no ORM, no database, no PMI (out of scope); library-first | ✅ PASS |

**Post-Phase-1 re-check**: All gates still pass. No complexity violations; no
Complexity Tracking entries required.

## Project Structure

### Documentation (this feature)

```text
specs/001-loan-pricing-engine/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── pricing-api.md   # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit-tasks — NOT created here)
```

### Source Code (repository root)

```text
src/
├── engine/
│   ├── __init__.py
│   ├── amortisation.py      # Monthly payment formula (Decimal math)
│   ├── apr.py               # Regulation Z APR solver (Newton-Raphson)
│   └── arm.py               # ARM-specific calculations
├── models/
│   ├── __init__.py
│   ├── inputs.py            # Pydantic input models (FixedScenario, ArmScenario, etc.)
│   └── outputs.py           # Pydantic output models (PricingResult, ComparisonResult)
├── validation/
│   ├── __init__.py
│   └── rules.py             # Boundary validation logic (FR-005)
├── audit/
│   ├── __init__.py
│   └── logger.py            # JSON audit line emitter
└── api/
    ├── __init__.py
    ├── main.py              # FastAPI app factory
    └── routes/
        ├── fixed.py         # POST /price/fixed
        ├── arm.py           # POST /price/arm
        ├── compare.py       # POST /price/compare
        └── health.py        # GET /health

tests/
├── contract/
│   ├── test_fixed_api.py    # HTTP-level contract tests (httpx)
│   ├── test_arm_api.py
│   └── test_compare_api.py
├── integration/
│   ├── test_fixed_pricing.py   # End-to-end fixed-rate scenario tests
│   └── test_arm_pricing.py     # End-to-end ARM scenario tests
└── unit/
    ├── test_amortisation.py    # Formula accuracy tests (reference values)
    ├── test_apr.py             # APR solver tests (Reg Z reference values)
    ├── test_arm.py             # ARM calculation tests
    ├── test_validation.py      # Boundary validation tests
    └── test_audit.py           # Audit log output tests

requirements.txt             # Pinned production dependencies
requirements-dev.txt         # Pinned dev/test dependencies
```

**Structure Decision**: Single Python project (Option 1). Library core in `src/engine/`
is imported by `src/api/` routes. Tests mirror source structure. No monorepo complexity
needed for v1.

## Complexity Tracking

> No violations. All Constitution Check gates pass without exception.
