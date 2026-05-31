---

description: "Task list for React Loan Pricing UI"
---

# Tasks: React Loan Pricing UI

**Input**: Design documents from `specs/002-react-pricing-ui/`

**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Constitution — Test-First (NON-NEGOTIABLE)**: Per Principle III, tests MUST be
written and confirmed failing before corresponding component implementation begins.
Vitest + React Testing Library; msw for API mocking.

**Constitution — No Frontend Arithmetic**: Per Principle I, no monetary calculations
on the frontend. All values come from the backend as pre-formatted strings.

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no blocking dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- All tasks include exact file paths

---

## Phase 1: Setup

**Purpose**: Project scaffolding, dependencies, build configuration

- [x] T001 Create `frontend/` directory and initialise Vite + React + TypeScript project: `npm create vite@latest frontend -- --template react-ts`
- [x] T002 Pin all dependency versions in `frontend/package.json` to exact versions (remove `^` and `~` prefixes per Constitution Technology Constraints)
- [x] T003 [P] Configure Vite dev proxy in `frontend/vite.config.ts`: forward `/api/*` → `http://localhost:8000`
- [x] T004 [P] Install dev dependencies: `vitest`, `@vitest/ui`, `@testing-library/react`, `@testing-library/user-event`, `@testing-library/jest-dom`, `msw`, `jsdom` — add to `devDependencies` in `frontend/package.json`
- [x] T005 [P] Install production dependencies: `react-hook-form` — add to `dependencies` in `frontend/package.json`
- [x] T006 [P] Configure Vitest in `frontend/vite.config.ts`: set `test.environment = "jsdom"`, `test.setupFiles = ["src/__tests__/setup.ts"]`, `test.globals = true`
- [x] T007 Create `frontend/src/__tests__/setup.ts`: import `@testing-library/jest-dom/vitest` and configure msw server lifecycle (`beforeAll` / `afterEach` / `afterAll`)
- [x] T008 [P] Delete Vite scaffold boilerplate: remove `src/App.css`, clear `src/index.css`, remove `src/assets/react.svg`, reset `src/App.tsx` to an empty shell

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared TypeScript types and the API service layer — required by all user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T009 [P] Create shared TypeScript interfaces in `frontend/src/types/pricing.ts`: `ScenarioFormValues`, `ArmParamsForm`, `PricingResultDisplay`, `ScenarioPanelState`, `AppState`, `AppMode`, `ProductType`
- [x] T010 Write tests for `pricingApi` service in `frontend/src/__tests__/pricingApi.test.ts`: test `priceFixed`, `priceArm`, and `priceCompare` happy paths using msw handlers; test network error → `PricingApiError(0, …)`; test non-2xx → `PricingApiError(status, …)`. **Must FAIL before T011**
- [x] T011 Implement `frontend/src/services/pricingApi.ts`: typed `fetch` wrapper with `priceFixed()`, `priceArm()`, `priceCompare()`, and `PricingApiError` class; base path `/api/v1`

**Checkpoint**: Foundation ready — all user story work can now begin

---

## Phase 3: User Story 1 — Price a Fixed-Rate Loan (Priority: P1) 🎯 MVP

**Goal**: A user fills in a fixed-rate form (home price, down payment, term, rate),
submits, and sees monthly payment, APR, and total interest in a results panel.

**Independent Test**: Enter $400,000 home, $80,000 down, 30 years, 6.5% rate →
results panel shows "Monthly Payment", "APR", and "Fixed 30-year" label.

### Tests for User Story 1 (write FIRST — confirm FAILING before implementation)

- [x] T012 [P] [US1] Write `frontend/src/__tests__/ResultsPanel.test.tsx`: renders monthly payment with `$` prefix and 2dp; renders APR with `%` suffix and 3dp; renders rate-type label. **Must FAIL before T016**
- [x] T013 [P] [US1] Write `frontend/src/__tests__/ScenarioForm.test.tsx` (fixed-rate subset): renders all fixed-rate fields; submit with valid data calls `onSubmit`; submit with blank Home Price shows inline error and does not call `onSubmit`; submit with rate > 30 shows inline error. **Must FAIL before T017**
- [x] T014 [P] [US1] Write `frontend/src/__tests__/ScenarioPanel.test.tsx` (single-mode fixed): shows loading spinner while request in flight; shows results panel after successful API response (msw); shows error banner on API failure. **Must FAIL before T018**
- [x] T015 [P] [US1] Write `frontend/src/__tests__/App.test.tsx` (single fixed-rate flow): user fills fixed form and submits → results appear; re-submit updates results without page reload. **Must FAIL before T019**

### Implementation for User Story 1

- [x] T016 [P] [US1] Implement `frontend/src/components/ResultsPanel/ResultsPanel.tsx` and `ResultsPanel.module.css`: display `loanAmount`, `monthlyPayment`, `apr`, `totalInterest`, `rateTypeLabel` formatted with currency/percent helpers; no arithmetic — display received strings only
- [x] T017 [US1] Implement `frontend/src/components/ScenarioForm/ScenarioForm.tsx` and `ScenarioForm.module.css`: register all fixed-rate fields with React Hook Form; inline validation rules per data-model.md; product toggle (Fixed / ARM) — ARM fields hidden in this story; "Get Quote" submit button disabled while loading
- [x] T018 [US1] Implement `frontend/src/components/ScenarioPanel/ScenarioPanel.tsx` and `ScenarioPanel.module.css`: renders `ScenarioForm` + `ResultsPanel`; manages loading/error/result display states; calls `pricingApi.priceFixed()` on submit
- [x] T019 [US1] Implement `frontend/src/App.tsx` and `frontend/src/App.module.css`: `useReducer` with `AppState`; render single `ScenarioPanel`; wire up mode toggle button (renders "Compare Two Scenarios" label, no-op for now); update `frontend/src/main.tsx` to mount `<App />`
- [x] T020 [US1] Create `frontend/index.html` with correct `<title>Home Loan Pricing</title>` and mount point `<div id="root">`; ensure `npm run dev` serves the app on `http://localhost:5173`

**Checkpoint**: US1 done — `npm run dev`, fill fixed form, see results. `npm run test` green for US1 tests.

---

## Phase 4: User Story 2 — Price a Variable-Rate (ARM) Loan (Priority: P2)

**Goal**: Toggling to "Adjustable Rate (ARM)" reveals ARM-specific fields; submitting
shows initial payment, APR, and a rate-type label like "5/1 ARM 30-year".

**Independent Test**: Toggle to ARM → enter 5.75% initial rate, fixed period 5, interval
1, caps 2/2/5 → submit → results show "5/1 ARM 30-year" label and valid payment/APR.

### Tests for User Story 2 (write FIRST — confirm FAILING before implementation)

- [x] T021 [P] [US2] Write `frontend/src/__tests__/ArmFields.test.tsx`: ARM fields group renders all 5 cap inputs; cross-field error shows on Periodic Cap when periodicCap > lifetimeCap; fields are hidden when productType is "fixed". **Must FAIL before T023**
- [x] T022 [P] [US2] Extend `frontend/src/__tests__/ScenarioForm.test.tsx` (ARM subset): toggling to ARM shows ARM fields and hides annual-rate label; shared fields (homePrice, downPayment, termYears) retain values after toggle; switching back to fixed hides ARM fields. **Must FAIL before T024**
- [x] T023 [P] [US2] Extend `frontend/src/__tests__/ScenarioPanel.test.tsx` (ARM flow): selecting ARM + valid ARM inputs + submit calls `pricingApi.priceArm()`; inconsistent caps show inline error, no API call made. **Must FAIL before T025**

### Implementation for User Story 2

- [x] T024 [P] [US2] Implement `frontend/src/components/ScenarioForm/ArmFields.tsx`: render fixed-period, adjustment-interval, and three cap inputs; register with RHF `control`; cross-field `periodicCap ≤ lifetimeCap` validation via RHF `validate`
- [x] T025 [US2] Extend `frontend/src/components/ScenarioForm/ScenarioForm.tsx`: wire product toggle to show/hide `<ArmFields />`; switch rate field label between "Annual Rate" and "Initial Rate"; reset rate field value on product-type change; preserve shared field values across toggle
- [x] T026 [US2] Extend `frontend/src/components/ScenarioPanel/ScenarioPanel.tsx`: detect `productType` in submitted values and call `pricingApi.priceFixed()` or `pricingApi.priceArm()` accordingly

**Checkpoint**: US2 done — toggle to ARM, fill form, see "5/1 ARM 30-year" result. `npm run test` green for US1+US2.

---

## Phase 5: User Story 3 — Compare Two Scenarios Side by Side (Priority: P3)

**Goal**: Clicking "Compare Two Scenarios" renders a second independent scenario panel;
both panels submit and display results side by side.

**Independent Test**: Activate comparison mode → Panel A: 30yr fixed 6.5% → Panel B:
15yr fixed 6.0% → submit both → two result cards visible simultaneously, each labelled.

### Tests for User Story 3 (write FIRST — confirm FAILING before implementation)

- [x] T027 [P] [US3] Extend `frontend/src/__tests__/App.test.tsx` (comparison flow): clicking comparison toggle renders second panel; Panel A and Panel B are independently configurable; submitting both shows two result cards; deactivating comparison removes Panel B. **Must FAIL before T028**

### Implementation for User Story 3

- [x] T028 [US3] Extend `frontend/src/App.tsx`: comparison mode toggle updates `AppState.mode`; when `mode === "comparison"` render two `<ScenarioPanel>` instances (id="a" and id="b") side by side; deactivate discards `scenarioB` state; add comparison layout styles to `frontend/src/App.module.css`

**Checkpoint**: US3 done — activate comparison mode, fill both panels, see two result cards. `npm run test` all green.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Accessibility, responsive layout, production build, final validation

- [x] T029 [P] Add `aria-label` attributes to all form inputs, the product toggle, the comparison mode toggle, the loading spinner, and the error banner in all components
- [x] T030 [P] Add responsive CSS breakpoints in all `.module.css` files: desktop layout (≥ 1024px) side-by-side columns in comparison; tablet layout (≥ 768px) stacked single column; ensure no horizontal scroll at 768px viewport
- [x] T031 [P] Add msw request handlers in `frontend/src/__tests__/setup.ts` for all three endpoints (`/api/v1/price/fixed`, `/api/v1/price/arm`, `/api/v1/price/compare`) with realistic response fixtures matching the backend contract
- [x] T032 Run `npm run build` in `frontend/` and confirm `frontend/dist/` is populated with no TypeScript errors and no Vite build errors
- [x] T033 [P] Execute quickstart.md steps 1–8 against a running backend; confirm all expected values appear and audit logs emit on the backend stdout

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — **blocks all user stories**
- **US1 (Phase 3)**: Depends on Phase 2; independent of US2, US3
- **US2 (Phase 4)**: Depends on Phase 2 + US1 (extends ScenarioForm and ScenarioPanel)
- **US3 (Phase 5)**: Depends on US1 + US2 (App renders ScenarioPanels for both product types)
- **Polish (Phase 6)**: Depends on all user story phases complete

### Within Each User Story

1. Tests MUST be written and confirmed **failing** before implementation begins
2. Type definitions (pricing.ts) before service layer
3. Service layer (pricingApi.ts) before components that call it
4. Leaf components (ResultsPanel, ArmFields) before container components (ScenarioForm, ScenarioPanel)
5. ScenarioPanel before App

### Parallel Opportunities

- T003, T004, T005, T006 (Setup config) — all parallel after T001, T002
- T009, T010 (Foundational) — parallel (different files)
- T012, T013, T014, T015 (US1 tests) — all parallel
- T016, T017 (US1 leaf implementations) — parallel (different components)
- T021, T022, T023 (US2 tests) — all parallel
- T024, T025 (US2 ARM fields + form extend) — parallel (different files)
- T029, T030, T031 (Polish) — all parallel

---

## Parallel Execution Examples

### US1 — Test Writing (all parallel)

```
Task T012: src/__tests__/ResultsPanel.test.tsx
Task T013: src/__tests__/ScenarioForm.test.tsx (fixed subset)
Task T014: src/__tests__/ScenarioPanel.test.tsx (single fixed)
Task T015: src/__tests__/App.test.tsx (single fixed flow)
```

### US1 — Implementation (parallel leaf components)

```
Task T016: src/components/ResultsPanel/ResultsPanel.tsx + .module.css
Task T017: src/components/ScenarioForm/ScenarioForm.tsx + .module.css
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001–T008)
2. Complete Phase 2: Foundational (T009–T011)
3. Write US1 tests (T012–T015) → confirm all **FAIL**
4. Implement US1 components (T016–T020) → confirm all tests **PASS**
5. **STOP and VALIDATE**: `npm run test` green + quickstart.md step 3
6. Demo: fixed-rate form → results panel working end-to-end

### Incremental Delivery

1. Setup + Foundational → project compiles and tests run
2. US1 → Fixed-rate pricing UI live (MVP)
3. US2 → ARM toggle and ARM results live
4. US3 → Comparison mode live
5. Polish → Production build passes, accessibility complete

---

## Notes

- `[P]` = different files, no blocking dependencies within the parallel group
- `[US?]` maps task to user story for traceability
- Constitution Principle I: never perform currency math in the UI — display backend strings as-is
- Constitution Principle III: tests red before implementation green — enforced every phase
- Pin all npm packages to exact versions (no `^` or `~`) per Constitution Technology Constraints
- Run `npm run test` after each checkpoint before proceeding to the next phase
