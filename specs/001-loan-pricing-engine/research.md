# Research: Loan Pricing Engine

**Branch**: `001-loan-pricing-engine` | **Date**: 2026-05-30

---

## Decision 1: Programming Language

**Decision**: Python 3.11+

**Rationale**: Python ships a native `decimal.Decimal` type that satisfies Constitution
Principle I (Financial Precision) with no third-party dependency. The `decimal` module
supports configurable precision and half-up rounding (ROUND_HALF_UP), which maps
directly to Regulation Z requirements. Python's ecosystem has mature testing tooling
(pytest) and a standard web framework (FastAPI) that minimises accidental complexity.

**Alternatives considered**:
- **Java/Kotlin**: `BigDecimal` is equally precise, but JVM startup adds friction for a
  v1 service; would revisit if throughput demands JVM warm-path performance.
- **Go**: `shopspring/decimal` library exists but is not stdlib; adds a dependency for
  the most critical guarantee in the system.
- **JavaScript/TypeScript**: No native decimal type; `big.js` is third-party. Rejected
  to honour Principle I without external risk.

---

## Decision 2: Project Type

**Decision**: Python library with a thin FastAPI web-service layer

**Rationale**: The core pricing engine is pure calculation — no I/O, no state — so it
should be a standalone importable library first. A FastAPI layer wraps it so the engine
is also accessible as an HTTP service. This keeps the calculation logic testable without
a running server (Principle III: Test-First).

**Alternatives considered**:
- **CLI only**: Would not support programmatic integration or the batch comparison
  user story (US3).
- **Web service only**: Entangles HTTP concerns with calculation logic; makes unit
  tests heavier than necessary.

---

## Decision 3: Monthly Payment Formula

**Decision**: Standard amortisation formula

```
M = P × [r(1+r)^n] / [(1+r)^n − 1]
```

where P = principal (loan amount), r = monthly interest rate (annual rate / 12),
n = total number of monthly payments (term_years × 12).

All arithmetic performed with `decimal.Decimal` and `ROUND_HALF_UP` at the final
display step only (intermediate values carried at full precision).

**Special case — zero interest rate**: M = P / n (avoids division-by-zero in the
standard formula).

**Rationale**: This is the universally accepted mortgage amortisation formula. Using
it verbatim ensures results match any reference amortisation table.

---

## Decision 4: APR Calculation Method

**Decision**: Regulation Z actuarial method (12 CFR Part 1026, Appendix J)

The APR is the annual interest rate that equates the present value of all scheduled
payments to the amount financed (loan amount minus prepaid finance charges / fees).
Solved iteratively (Newton-Raphson or bisection) using `decimal.Decimal` arithmetic.

For ARM products, APR is disclosed based on the initial-rate-period assumption
(i.e., the initial rate is held constant for the full term), which is the standard
regulatory approach for ARM APR disclosure under Regulation Z.

**Rationale**: Appendix J is the legally required method for U.S. mortgage APR
disclosure. Any other method would violate Principle II (Regulatory Compliance).

---

## Decision 5: Audit Log Strategy

**Decision**: Structured JSON log to stdout (12-factor app style) for v1

Every pricing call emits one JSON line to stdout containing: `request_id` (UUID),
`timestamp` (ISO-8601 UTC), `inputs` (sanitised), `outputs`, and `duration_ms`.
No PII fields (borrower name, SSN) are accepted as inputs by the engine in v1, so
masking is N/A at this stage.

**Rationale**: Satisfies Principle IV (Auditability) with zero infrastructure
dependency. stdout is captured by any container/process supervisor and forwarded to
log aggregation in production. Switching to a structured log sink (e.g., Cloud
Logging, Datadog) is a config change, not a code change.

---

## Decision 6: ARM Cap Validation Rules

**Decision**: Enforce the following at input boundary:
- `periodic_cap` MUST be ≤ `lifetime_cap`
- `initial_cap` MUST be ≥ 0 (can be 0 for "no initial adjustment limit" products,
  but must be explicitly provided)
- `lifetime_cap` MUST be > 0
- Maximum rate = initial_rate + lifetime_cap MUST be ≤ 30% (sanity ceiling; not a
  legal requirement but protects against data entry errors)

**Rationale**: These are structural consistency constraints derivable from FNMA/FHLMC
ARM guidelines and standard lender practice. Catching them at boundary validation
(Principle II, FR-005) prevents silent mis-pricing.

---

## Decision 7: Dependency List (minimal)

| Package | Purpose | Justification |
|---------|---------|---------------|
| `fastapi` | HTTP routing | Thin web layer over library core |
| `uvicorn` | ASGI server | Standard FastAPI runtime |
| `pydantic` v2 | Input validation | Boundary validation per FR-005 |
| `pytest` | Test runner | TDD support per Principle III |
| `pytest-asyncio` | Async test support | FastAPI route testing |
| `httpx` | Test HTTP client | Contract test HTTP calls |

No ORM, no database driver. All dependencies pinned to exact versions in
`requirements.txt` and `requirements-dev.txt` per Technology Constraints.

---

## Resolution Summary

| Item | Was | Now |
|------|-----|-----|
| Language/Version | NEEDS CLARIFICATION | Python 3.11+ |
| Primary Dependencies | NEEDS CLARIFICATION | fastapi, pydantic v2, uvicorn |
| Storage | Unknown | N/A (stateless calculation; audit to stdout) |
| Testing | NEEDS CLARIFICATION | pytest + pytest-asyncio + httpx |
| Target Platform | NEEDS CLARIFICATION | Linux server (Docker-friendly) |
| Project Type | NEEDS CLARIFICATION | Library + FastAPI web service |
| Performance Goals | Unknown | Single request < 50ms (CPU-bound Decimal math) |
| Constraints | Unknown | Decimal arithmetic only; no float; Reg Z rounding |
| Scale/Scope | Unknown | v1: single-instance; batch up to 5 scenarios |
