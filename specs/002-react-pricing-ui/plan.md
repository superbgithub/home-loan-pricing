# Implementation Plan: React Loan Pricing UI

**Branch**: `002-react-pricing-ui` | **Date**: 2026-05-30 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-react-pricing-ui/spec.md`

## Summary

Build a React 18 + TypeScript single-page application that wraps the existing loan
pricing API. Users fill out a form (fixed or ARM product), submit, and see monthly
payment, APR, and total interest rendered in a results panel. A comparison mode
renders two independent scenario panels side by side. All pricing arithmetic stays
server-side; the frontend only formats and displays the values the backend returns.

## Technical Context

**Language/Version**: TypeScript 5.x + Node.js 20+

**Primary Dependencies**: React 18, Vite 6, React Hook Form v7, Vitest, React Testing
Library, msw (Mock Service Worker)

**Storage**: None — stateless UI; no localStorage, no cookies, no session persistence
between page loads.

**Testing**: Vitest + React Testing Library + jsdom; msw for API mocking in tests

**Target Platform**: Browser (desktop ≥ 1024px, tablet ≥ 768px); served from
`frontend/dist/` as static files

**Project Type**: Single-page web application (no SSR, no routing library needed for v1)

**Performance Goals**: First Contentful Paint < 1.5s on a local dev connection;
results appear within 2s of submission (dominated by API latency, not UI rendering)

**Constraints**: No monetary arithmetic on the frontend — all figures come from the
backend as pre-formatted decimal strings. No floating-point math in the UI layer.

**Scale/Scope**: Single-user, single-session; no concurrency concerns at UI level.
Maximum 2 concurrent in-flight API requests (one per comparison scenario).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate | Status |
|-----------|------|--------|
| I. Financial Precision | No monetary arithmetic on frontend; all values displayed as received from backend (pre-rounded Decimal strings) | ✅ PASS |
| II. Regulatory Compliance | All pricing calculations and Reg Z rounding stay in the Python engine; frontend is display-only | ✅ PASS |
| III. Test-First | Tests written before component implementation; RTL tests match spec acceptance scenarios | ✅ PASS (enforced in tasks) |
| IV. Auditability | Each form submission triggers a backend API call which emits an audit record server-side; no additional frontend audit needed | ✅ PASS |
| V. Simplicity & YAGNI | No state manager, no UI library, no router, no auth — only what the spec requires | ✅ PASS |

**Post-Phase-1 re-check**: All gates pass. No complexity violations.

## Project Structure

### Documentation (this feature)

```text
specs/002-react-pricing-ui/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── ui-components.md # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code (repository root)

```text
frontend/
├── index.html
├── vite.config.ts           # Vite + proxy config (/api → localhost:8000)
├── tsconfig.json
├── package.json             # Pinned exact versions
├── package-lock.json
├── src/
│   ├── main.tsx             # React root mount
│   ├── App.tsx              # AppState (useReducer) + layout
│   ├── App.module.css
│   ├── types/
│   │   └── pricing.ts       # Shared TS interfaces
│   ├── services/
│   │   └── pricingApi.ts    # fetch wrapper for /price/fixed, /price/arm, /price/compare
│   └── components/
│       ├── ScenarioPanel/
│       │   ├── ScenarioPanel.tsx
│       │   └── ScenarioPanel.module.css
│       ├── ScenarioForm/
│       │   ├── ScenarioForm.tsx
│       │   ├── ScenarioForm.module.css
│       │   └── ArmFields.tsx
│       └── ResultsPanel/
│           ├── ResultsPanel.tsx
│           └── ResultsPanel.module.css
└── src/__tests__/
    ├── setup.ts             # RTL + msw global setup
    ├── pricingApi.test.ts   # Service layer tests
    ├── ScenarioForm.test.tsx
    ├── ArmFields.test.tsx
    ├── ResultsPanel.test.tsx
    ├── ScenarioPanel.test.tsx
    └── App.test.tsx         # Integration: single-mode and comparison-mode flows
```

**Structure Decision**: Frontend lives in `frontend/` at repo root, isolated from the
Python `src/` directory. The two projects share only the API contract documented in
`specs/001-loan-pricing-engine/contracts/pricing-api.md`.

## Complexity Tracking

> No violations. All Constitution Check gates pass without exception.
