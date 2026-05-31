# Data Model: React Loan Pricing UI

**Branch**: `002-react-pricing-ui` | **Date**: 2026-05-30

All financial values are kept as strings in UI state to preserve user-entered
formatting and avoid floating-point representation issues. String → backend
conversion happens only in the API service layer.

---

## UI State Entities

### AppMode

```
"single" | "comparison"
```

Determines whether one or two `ScenarioPanel` instances are rendered.

---

### ProductType

```
"fixed" | "arm"
```

Discriminator that controls which fields are shown in a `ScenarioForm`.

---

### ArmParamsForm

| Field | Type | UI control | Validation |
|-------|------|-----------|------------|
| `fixedPeriodYears` | string | Number input | Required; integer 1–49 |
| `adjustmentPeriodYears` | string | Number input | Required; integer 1–49 |
| `initialCap` | string | Number input | Required; decimal ≥ 0 |
| `periodicCap` | string | Number input | Required; decimal > 0; ≤ lifetimeCap |
| `lifetimeCap` | string | Number input | Required; decimal > 0 |

Cross-field rule: `periodicCap` ≤ `lifetimeCap` (validated before submission).

---

### ScenarioFormValues

| Field | Type | UI control | Validation | Notes |
|-------|------|-----------|------------|-------|
| `productType` | ProductType | Toggle button | Required | Default: "fixed" |
| `homePrice` | string | Currency input | Required; decimal > 0 | |
| `downPayment` | string | Text input | Required; > 0; < homePrice | Accepts "20%" or "80000" |
| `termYears` | string | Select | Required; one of 10/15/20/30 | |
| `annualRate` | string | Decimal input | Required for fixed; 0–30 | Label: "Annual Rate" |
| `initialRate` | string | Decimal input | Required for ARM; 0–30 | Label: "Initial Rate" |
| `armParams` | ArmParamsForm | (group) | Required when productType = "arm" | Hidden for fixed |

---

### ScenarioPanelState

| Field | Type | Notes |
|-------|------|-------|
| `id` | "a" \| "b" | Identifies panel in comparison mode |
| `formValues` | ScenarioFormValues | Current input values |
| `result` | PricingResultDisplay \| null | null until a successful response |
| `error` | string \| null | User-facing error message |
| `loading` | boolean | True while request in flight |
| `fieldErrors` | Record\<string, string\> | Field-level validation errors from RHF |

---

### PricingResultDisplay

Derived from the API response; all values displayed as received (string-formatted
decimals from the backend).

| Field | Type | Display label |
|-------|------|---------------|
| `scenarioId` | string | (internal) |
| `loanType` | string | (used for label) |
| `loanAmount` | string | "Loan Amount" |
| `monthlyPayment` | string | "Monthly Payment" |
| `apr` | string | "APR" |
| `totalInterest` | string | "Total Interest" |
| `rateTypeLabel` | string | "Rate Type" (e.g., "Fixed 30-year") |

---

### AppState

| Field | Type | Notes |
|-------|------|-------|
| `mode` | AppMode | "single" or "comparison" |
| `scenarioA` | ScenarioPanelState | Always present |
| `scenarioB` | ScenarioPanelState \| null | Present only in comparison mode |

---

## State Transitions

```
App starts → mode = "single", scenarioA = default form, result = null

User fills form and submits (single mode):
  scenarioA.loading = true
  → API response OK → scenarioA.result = PricingResultDisplay, loading = false
  → API error       → scenarioA.error = message, loading = false

User toggles comparison mode ON:
  mode = "comparison"
  scenarioB = default form (scenarioA values preserved)

User submits in comparison mode:
  scenarioA.loading = true, scenarioB.loading = true
  → Both results arrive → each panel's result / error updated independently

User toggles comparison mode OFF:
  mode = "single"
  scenarioB = null (state discarded)

User switches productType (fixed ↔ ARM):
  armParams fields appear/disappear
  Shared fields (homePrice, downPayment, termYears) are preserved
  Rate field (annualRate/initialRate) is reset to empty
```

---

## Relationships

```
AppState
  └─ ScenarioPanelState (scenarioA, scenarioB?)
       ├─ ScenarioFormValues
       │    └─ ArmParamsForm (when productType = "arm")
       └─ PricingResultDisplay (when result received)
```
