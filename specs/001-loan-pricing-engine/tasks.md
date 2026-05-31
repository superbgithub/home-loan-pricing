---

description: "Task list for Loan Pricing Engine"
---

# Tasks: Loan Pricing Engine

**Input**: Design documents from `specs/001-loan-pricing-engine/`

**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Constitution — Test-First (NON-NEGOTIABLE)**: Per Principle III, every test task
MUST be written and confirmed failing before its corresponding implementation task begins.
The Red-Green-Refactor cycle is enforced throughout.

**Organization**: Tasks are grouped by user story to enable independent implementation
and testing of each story.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no shared dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- All tasks include exact file paths

---

## Phase 1: Setup

**Purpose**: Project initialization, directory structure, and tooling configuration

- [x] T001 Create full source directory tree: `src/engine/`, `src/models/`, `src/validation/`, `src/audit/`, `src/api/routes/` with `__init__.py` in each
- [x] T002 Create `tests/` directory tree: `tests/unit/`, `tests/integration/`, `tests/contract/` with `__init__.py` in each
- [x] T003 [P] Create `requirements.txt` with pinned versions: `fastapi==0.115.x`, `uvicorn[standard]==0.32.x`, `pydantic==2.10.x`
- [x] T004 [P] Create `requirements-dev.txt` with pinned versions: `pytest==8.3.x`, `pytest-asyncio==0.24.x`, `httpx==0.28.x`
- [x] T005 [P] Create `pytest.ini` (or `pyproject.toml` `[tool.pytest.ini_options]`) configuring `asyncio_mode = auto` and `testpaths = tests`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared infrastructure that MUST be complete before any user story begins

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 [P] Create `AuditRecord`, `ErrorDetail` Pydantic output models in `src/models/outputs.py`
- [x] T007 [P] Create `FeeSchedule` and `Fee` Pydantic input models in `src/models/inputs.py`
- [x] T008 Implement JSON audit logger in `src/audit/logger.py` — emits one JSON line per pricing call to stdout with fields: `request_id`, `timestamp`, `loan_type`, `scenario_count`, `inputs_hash`, `outputs_summary`, `duration_ms`, `error`
- [x] T009 Create FastAPI app factory in `src/api/main.py` — registers `/api/v1` prefix, mounts health route, configures exception handlers for 422 validation errors
- [x] T010 [P] Implement `GET /health` route in `src/api/routes/health.py` returning `{"status": "ok"}`

**Checkpoint**: Foundation ready — user story implementation can now begin

---

## Phase 3: User Story 1 — Fixed-Rate Loan Payment (Priority: P1) 🎯 MVP

**Goal**: A user can submit a fixed-rate loan scenario and receive a monthly payment and
APR that are accurate to within $0.01 and Regulation Z tolerance respectively.

**Independent Test**: Submit `{"home_price":"400000.00","down_payment":"80000.00","term_years":30,"annual_rate":"6.50"}` to `POST /price/fixed` and verify `monthly_payment == "2022.65"` and `loan_type == "fixed"`.

### Tests for User Story 1 (Constitution Principle III — write FIRST, confirm FAILING)

- [x] T011 [P] [US1] Write unit tests for the amortisation formula covering: standard case, 15-year term, zero-interest special case, edge inputs — in `tests/unit/test_amortisation.py`. **Must FAIL before T016**
- [x] T012 [P] [US1] Write unit tests for the APR solver covering: no-fee case (APR == rate), with-fees case, Reg Z rounding — in `tests/unit/test_apr.py`. **Must FAIL before T017**
- [x] T013 [P] [US1] Write unit tests for fixed-rate boundary validation: negative rate, zero term, down payment ≥ home price, rate > 30 — in `tests/unit/test_validation.py`. **Must FAIL before T018**
- [x] T014 [P] [US1] Write contract test for `POST /price/fixed`: valid request → 200 with correct fields, invalid rate → 422 with `INVALID_RATE` code — in `tests/contract/test_fixed_api.py`. **Must FAIL before T020**
- [x] T015 [P] [US1] Write integration test for a full fixed-rate pricing pipeline (inputs → engine → audit log emitted) — in `tests/integration/test_fixed_pricing.py`. **Must FAIL before T020**

### Implementation for User Story 1

- [x] T016 [P] [US1] Implement `calculate_monthly_payment(principal, annual_rate, term_years)` in `src/engine/amortisation.py` using `decimal.Decimal`; handle zero-rate case; ROUND_HALF_UP only on returned value
- [x] T017 [P] [US1] Implement `calculate_apr(loan_amount, monthly_payment, term_months, fees)` in `src/engine/apr.py` using Newton-Raphson iteration in `decimal.Decimal`; raise `APRConvergenceError` if solver fails to converge
- [x] T018 [P] [US1] Create `FixedScenario` Pydantic model in `src/models/inputs.py`; implement `validate_fixed_scenario(scenario)` in `src/validation/rules.py` raising typed `ValidationError` for each rule in FR-005
- [x] T019 [US1] Implement `PricingResult` Pydantic output model in `src/models/outputs.py` with all fields from data-model.md (`scenario_id`, `loan_type`, `loan_amount`, `monthly_payment`, `apr`, `total_interest`, `rate_type_label`, `parameters_summary`)
- [x] T020 [US1] Implement `POST /price/fixed` route in `src/api/routes/fixed.py`: validate → price → emit audit log → return `PricingResult`; mount route in `src/api/main.py`

**Checkpoint**: User Story 1 fully functional — run `pytest tests/ -k "fixed"` and validate with quickstart.md step 4

---

## Phase 4: User Story 2 — Variable-Rate (ARM) Loan Payment (Priority: P2)

**Goal**: A user can submit a 5/1 ARM scenario and receive a correct initial monthly
payment and APR for the initial-rate-held-constant disclosure period.

**Independent Test**: Submit a 5/1 ARM with `initial_rate:"5.75"`, 2/2/5 caps, 30-year term to `POST /price/arm` and verify `rate_type_label == "5/1 ARM 30-year"` and `loan_type == "arm"`.

### Tests for User Story 2 (Constitution Principle III — write FIRST, confirm FAILING)

- [x] T021 [P] [US2] Write unit tests for ARM initial payment and APR calculations: standard 5/1 ARM, 7/1 ARM, caps boundary — in `tests/unit/test_arm.py`. **Must FAIL before T025**
- [x] T022 [P] [US2] Write unit tests for ARM validation rules: periodic_cap > lifetime_cap, fixed_period ≥ term, max_rate > 30 ceiling — in `tests/unit/test_validation.py` (append to existing file). **Must FAIL before T026**
- [x] T023 [P] [US2] Write contract test for `POST /price/arm`: valid ARM → 200, inconsistent caps → 422 with `PERIODIC_CAP_EXCEEDS_LIFETIME` — in `tests/contract/test_arm_api.py`. **Must FAIL before T028**
- [x] T024 [P] [US2] Write integration test for a full ARM pricing pipeline including audit record — in `tests/integration/test_arm_pricing.py`. **Must FAIL before T028**

### Implementation for User Story 2

- [x] T025 [P] [US2] Create `ArmParameters` and `ArmScenario` Pydantic models in `src/models/inputs.py`
- [x] T026 [US2] Implement `calculate_arm_initial_payment` and `calculate_arm_apr` in `src/engine/arm.py`; reuse `amortisation.calculate_monthly_payment` for initial period; APR uses initial-rate-held-constant assumption per Regulation Z
- [x] T027 [US2] Implement ARM-specific validation rules in `src/validation/rules.py`: `validate_arm_scenario(scenario)` enforcing all ARM cap constraints from data-model.md
- [x] T028 [US2] Implement `POST /price/arm` route in `src/api/routes/arm.py`: validate → price → emit audit log → return `PricingResult`; mount route in `src/api/main.py`

**Checkpoint**: User Story 2 fully functional — run `pytest tests/ -k "arm"` and validate with quickstart.md step 5

---

## Phase 5: User Story 3 — Compare Multiple Loan Scenarios (Priority: P3)

**Goal**: A user can submit up to 5 loan scenarios and receive individual pricing results
for each, with partial success (valid results + error details for invalid inputs) returned in a single response.

**Independent Test**: Submit two fixed-rate scenarios (30-year and 15-year) to `POST /price/compare`; verify response contains two `results` entries each with `scenario_id`, `monthly_payment`, and `total_interest`.

### Tests for User Story 3 (Constitution Principle III — write FIRST, confirm FAILING)

- [x] T029 [P] [US3] Write contract tests for `POST /price/compare`: two valid scenarios → 200 with two results; one valid + one invalid → 200 with mixed results; >5 scenarios → 422 with `SCENARIO_LIMIT_EXCEEDED` — in `tests/contract/test_compare_api.py`. **Must FAIL before T032**

### Implementation for User Story 3

- [x] T030 [P] [US3] Create `ComparisonRequest`, `ComparisonResult`, and `PricingResultOrError` Pydantic models in `src/models/inputs.py` and `src/models/outputs.py`; enforce 1–5 scenario limit at model level
- [x] T031 [US3] Implement `POST /price/compare` route in `src/api/routes/compare.py`: iterate scenarios, delegate to fixed/arm pricing functions, collect results and errors, emit single audit record with `scenario_count = N`, return `ComparisonResult`; mount route in `src/api/main.py`

**Checkpoint**: All user stories functional — run `pytest tests/` and validate with quickstart.md step 6

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Quality, completeness, and end-to-end validation across all stories

- [x] T032 [P] Write unit tests for audit logger: verify JSON structure, `inputs_hash` reproducibility, `duration_ms` present, `error` null on success — in `tests/unit/test_audit.py`
- [x] T033 [P] Verify all dependency versions are pinned exactly (no `>=`, `~=`, or `*`) in `requirements.txt` and `requirements-dev.txt`
- [x] T034 Run full `pytest tests/ -v` — all tests must pass; address any failures before marking complete
- [x] T035 [P] Execute quickstart.md validation steps 1–8 manually; confirm each curl command returns expected output and every request produces a JSON audit line on stdout

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion — **blocks all user stories**
- **US1 (Phase 3)**: Depends on Phase 2; no dependency on US2 or US3
- **US2 (Phase 4)**: Depends on Phase 2; no dependency on US1 (reuses engine helpers but doesn't depend on US1 routes)
- **US3 (Phase 5)**: Depends on Phase 2, US1, and US2 (delegates to fixed/arm pricing functions)
- **Polish (Phase 6)**: Depends on all user story phases complete

### User Story Dependencies

- **User Story 1 (P1)**: Independent after Foundational
- **User Story 2 (P2)**: Independent after Foundational; reuses `amortisation.py` but does not depend on US1 route completion
- **User Story 3 (P3)**: Depends on US1 and US2 pricing functions being implemented

### Within Each User Story

1. All test tasks MUST be written and confirmed **failing** before implementation begins
2. Models before services (Pydantic model → engine function → route)
3. Engine functions before routes
4. Route implemented before registered in `main.py`

### Parallel Opportunities

- T003, T004, T005 (Setup) — run together after T001, T002
- T006, T007 (Foundational models) — run together after Phase 1
- T011, T012, T013, T014, T015 (US1 tests) — all parallel
- T016, T017, T018 (US1 engine + model) — all parallel
- T021, T022, T023, T024 (US2 tests) — all parallel
- US1 and US2 phases can overlap once Foundational is done (different files)

---

## Parallel Execution Examples

### User Story 1 — Test Writing (all parallel)

```
Task T011: tests/unit/test_amortisation.py
Task T012: tests/unit/test_apr.py
Task T013: tests/unit/test_validation.py (fixed rules)
Task T014: tests/contract/test_fixed_api.py
Task T015: tests/integration/test_fixed_pricing.py
```

### User Story 1 — Implementation (parallel group)

```
Task T016: src/engine/amortisation.py
Task T017: src/engine/apr.py
Task T018: src/models/inputs.py (FixedScenario) + src/validation/rules.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (**CRITICAL** — blocks all stories)
3. Write all US1 tests (T011–T015) → confirm all **FAIL**
4. Complete US1 implementation (T016–T020) → confirm all tests **PASS**
5. **STOP and VALIDATE**: `pytest tests/ -k "fixed"` green + quickstart.md step 4
6. Demo: fixed-rate loan returns correct payment and APR

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. US1 → Fixed-rate pricing live (MVP)
3. US2 → ARM pricing live
4. US3 → Comparison live
5. Polish → Production-quality

---

## Notes

- `[P]` = different files, no blocking inter-task dependencies within the same parallel group
- `[US?]` maps each task to its user story for traceability
- Constitution Principle III is non-negotiable: tests red before implementation green
- Constitution Principle I is non-negotiable: `float` is forbidden in all engine code
- Commit after each checkpoint (end of each user story phase)
