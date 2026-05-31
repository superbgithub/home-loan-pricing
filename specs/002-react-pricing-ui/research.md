# Research: React Loan Pricing UI

**Branch**: `002-react-pricing-ui` | **Date**: 2026-05-30

---

## Decision 1: JavaScript Framework

**Decision**: React 18 + TypeScript

**Rationale**: React is the dominant choice for interactive single-page apps with
a product-toggle + live-results pattern. TypeScript catches mis-shaped API responses
at compile time — critical when displaying financial figures (Constitution Principle I:
any display bug must be obviously wrong, not silently off). The project's backend is
already Python-typed; TypeScript mirrors that discipline on the frontend.

**Alternatives considered**:
- **Vue 3**: Excellent DX, but smaller ecosystem and fewer typed component libraries
  relevant to form-heavy financial UIs.
- **Svelte**: Very lean, but team familiarity and ecosystem breadth favour React for
  a financial product where reliability outweighs bundle size.
- **Plain HTML + JS**: Eliminates build tooling complexity, but makes the reactive
  form state (toggle, conditional ARM fields, live validation) significantly harder
  to maintain correctly.

---

## Decision 2: Build Tool

**Decision**: Vite 6 with `@vitejs/plugin-react`

**Rationale**: Vite's native-ESM dev server starts in < 500ms regardless of project
size, and its built-in proxy feature (`server.proxy`) forwards `/api/*` requests to
the backend at `http://localhost:8000` with zero extra configuration — eliminating
CORS issues during development without a custom server.

**Alternatives considered**:
- **Create React App (CRA)**: Deprecated upstream; Webpack-based cold starts are slow.
- **Next.js**: Adds SSR complexity that brings no benefit for a stateless pricing tool
  with no SEO requirements and no server-side auth.

---

## Decision 3: Form Handling & Validation

**Decision**: React Hook Form (RHF) v7 with inline validation rules

**Rationale**: RHF registers inputs with minimal re-renders and provides field-level
error reporting out of the box, satisfying FR-004 (inline validation before submission)
and SC-003 (zero invalid requests reach the backend). The `trigger()` API allows
per-field validation on blur, which matches the UX pattern of a financial input form
where users tab between fields.

**Alternatives considered**:
- **Formik**: Larger bundle, more re-renders per keystroke; less suited to a
  performance-sensitive form with many conditionally visible fields.
- **Native HTML5 validation**: No programmatic control over error message placement
  or cross-field validation (e.g., periodic cap ≤ lifetime cap on ARM form).

---

## Decision 4: Styling

**Decision**: CSS Modules (`.module.css`)

**Rationale**: Zero runtime overhead, co-located with components, no class-name
collisions. Keeps the dependency list minimal (Constitution Principle V: Simplicity).
A financial tool has modest styling needs; a full CSS-in-JS solution or Tailwind adds
complexity without proportional benefit for this scope.

**Alternatives considered**:
- **Tailwind CSS**: Good for rapid prototyping but adds a PostCSS pipeline and
  produces verbose JSX; rejected in favour of readability.
- **Styled-components**: Runtime CSS injection; unnecessary overhead for a mostly
  static layout.

---

## Decision 5: HTTP Client

**Decision**: Native browser `fetch` wrapped in a typed service module (`src/services/pricingApi.ts`)

**Rationale**: `fetch` is available in all supported browsers, has no bundle cost, and
with TypeScript generics produces fully typed response objects. A thin wrapper handles
JSON serialisation, error mapping, and base URL configuration in one place. This
satisfies Constitution Principle V (no unnecessary dependencies) and keeps the service
layer independently testable via `vi.stubGlobal('fetch', ...)`.

**Alternatives considered**:
- **Axios**: Adds ~13 KB gzipped; no meaningful ergonomic advantage over `fetch` with
  a typed wrapper for this use case.

---

## Decision 6: Testing

**Decision**: Vitest + React Testing Library (RTL) + jsdom

**Rationale**: Vitest is the native test runner for Vite projects (shared config,
instant HMR-style reruns). RTL tests components from the user's perspective (fill
form, click submit, assert result text) — matching the acceptance scenarios in the
spec exactly. `msw` (Mock Service Worker) provides realistic API mocking without
patching `fetch` directly, enabling tests that exercise the full fetch-to-render
pipeline.

**Alternatives considered**:
- **Jest + Babel**: Requires a separate transformer; slower startup than Vitest for
  an ESM project.
- **Playwright / Cypress (E2E only)**: Valuable for integration, but RTL unit tests
  are faster and catch more granular component regressions.

---

## Decision 7: State Management

**Decision**: React built-in state (`useState`, `useReducer`) — no external store

**Rationale**: The app has two scenarios maximum, no cross-page navigation, and no
shared auth state. A `useReducer` at the `App` level holds all UI state (mode,
per-scenario form data, results, loading, error) and is passed down via props. This
is sufficient and avoids the indirection of Redux or Zustand (Constitution Principle V).

---

## Decision 8: API Integration Pattern

**Decision**: Vite dev proxy + relative URL paths in production

During development, Vite proxies `/api/v1/*` → `http://localhost:8000/api/v1/*`.
In a production build, the frontend is served from the same origin as the API
(or a reverse proxy handles routing), so relative URLs work without environment
variables for the base URL.

The service module uses `/api/v1/price/fixed`, `/api/v1/price/arm`, and
`/api/v1/price/compare` — exactly the paths defined in the backend contract.

---

## Resolution Summary

| Item | Decision |
|------|----------|
| Language | TypeScript 5.x |
| Framework | React 18 |
| Build tool | Vite 6 |
| Form library | React Hook Form v7 |
| Styling | CSS Modules |
| HTTP client | Native fetch (typed wrapper) |
| Testing | Vitest + RTL + msw |
| State management | React useState / useReducer |
| API proxy | Vite `server.proxy` |
| Target platform | Desktop (≥ 1024px), tablet (≥ 768px) |
