# UI Component Contracts: React Loan Pricing UI

**Branch**: `002-react-pricing-ui` | **Date**: 2026-05-30

These contracts define the props interface and observable behaviour for each
major component. They serve as the acceptance target for component tests.

---

## `<App />`

Top-level component. Owns all `AppState` via `useReducer`. No props.

**Renders**:
- A mode toggle button ("Single Scenario" / "Compare Two Scenarios")
- One `<ScenarioPanel id="a" />` always
- One `<ScenarioPanel id="b" />` when `mode === "comparison"`

**Behaviour**:
- Clicking the mode toggle switches between `"single"` and `"comparison"`
- When switching to comparison, `scenarioB` is initialised with default form values
- When switching back to single, `scenarioB` state is discarded

---

## `<ScenarioPanel>`

Props:

```ts
interface ScenarioPanelProps {
  id: "a" | "b";
  state: ScenarioPanelState;
  onSubmit: (values: ScenarioFormValues) => void;
}
```

**Renders**:
- `<ScenarioForm>` bound to `state.formValues`
- `<ResultsPanel>` when `state.result !== null`
- An error banner when `state.error !== null`
- A loading spinner/overlay when `state.loading === true`

**Behaviour**:
- Calls `onSubmit(values)` when the form passes validation
- Does not call `onSubmit` if any field-level validation error exists
- Disables the submit button while `state.loading === true`

---

## `<ScenarioForm>`

Props:

```ts
interface ScenarioFormProps {
  defaultValues: ScenarioFormValues;
  onSubmit: (values: ScenarioFormValues) => void;
  disabled?: boolean;
}
```

**Renders**:
- Product toggle: "Fixed Rate" | "Adjustable Rate (ARM)"
- Always-visible fields: Home Price, Down Payment, Loan Term (select), Annual Rate /
  Initial Rate
- ARM-only section (visible when `productType === "arm"`): Fixed Period, Adjustment
  Interval, Initial Cap, Periodic Cap, Lifetime Cap
- A "Get Quote" submit button
- Field-level inline error messages below each invalid field

**Validation rules** (enforced before `onSubmit` is called):
- `homePrice`: required, decimal string > 0
- `downPayment`: required, > 0, < homePrice (resolved after converting "%" if needed)
- `termYears`: required, one of "10" | "15" | "20" | "30"
- `annualRate` / `initialRate`: required, decimal 0–30
- ARM only — `periodicCap` ≤ `lifetimeCap`; all cap fields required and > 0

**Behaviour**:
- Switching `productType` hides/shows the ARM fields; shared fields retain values
- `annualRate` / `initialRate` input is reset when `productType` changes
- Errors clear when the corrected field loses focus (on blur)

---

## `<ArmFields>`

Props:

```ts
interface ArmFieldsProps {
  control: Control<ScenarioFormValues>;   // RHF control
  errors: FieldErrors<ScenarioFormValues>;
}
```

Renders the ARM-specific input group. Used inside `<ScenarioForm>` when
`productType === "arm"`.

**Fields rendered**:
- Fixed Period (years): integer input, 1–49
- Adjustment Interval (years): integer input, 1–49
- Initial Cap (%): decimal input, ≥ 0
- Periodic Cap (%): decimal input, > 0
- Lifetime Cap (%): decimal input, > 0

**Cross-field validation**: Periodic Cap ≤ Lifetime Cap is shown as an error on
the Periodic Cap field.

---

## `<ResultsPanel>`

Props:

```ts
interface ResultsPanelProps {
  result: PricingResultDisplay;
}
```

**Renders**:
- Rate-type label (e.g., "Fixed 30-year" or "5/1 ARM 30-year")
- Monthly Payment (formatted with $ and 2 decimal places)
- APR (formatted with % and 3 decimal places)
- Total Interest (formatted with $ and 2 decimal places)
- Loan Amount (formatted with $ and 2 decimal places)

**Behaviour**:
- All values are display-only; no user interaction
- Values are formatted client-side from the string values returned by the backend
- Component re-renders with new values whenever `result` prop changes

---

## `pricingApi` Service

```ts
// src/services/pricingApi.ts

interface PriceFixedRequest {
  home_price: string;
  down_payment: string;
  term_years: number;
  annual_rate: string;
  fee_schedule?: { fees: [] };
}

interface PriceArmRequest {
  home_price: string;
  down_payment: string;
  term_years: number;
  initial_rate: string;
  arm_params: {
    fixed_period_years: number;
    adjustment_period_years: number;
    initial_cap: string;
    periodic_cap: string;
    lifetime_cap: string;
  };
  fee_schedule?: { fees: [] };
}

interface PriceResponse {
  scenario_id: string;
  loan_type: string;
  loan_amount: string;
  monthly_payment: string;
  apr: string;
  total_interest: string;
  rate_type_label: string;
  parameters_summary: Record<string, unknown>;
}

interface CompareRequest {
  scenarios: Array<(PriceFixedRequest & { loan_type: "fixed"; scenario_id?: string })
                 | (PriceArmRequest  & { loan_type: "arm";   scenario_id?: string })>;
}

interface CompareResponse {
  comparison_id: string;
  results: Array<PriceResponse | { scenario_id: string; error: true; code: string; message: string }>;
}

export async function priceFixed(req: PriceFixedRequest): Promise<PriceResponse>
export async function priceArm(req: PriceArmRequest): Promise<PriceResponse>
export async function priceCompare(req: CompareRequest): Promise<CompareResponse>
```

**Error handling**:
- Non-2xx responses → throw `PricingApiError(status, message)` with the first
  detail message from the backend JSON body
- Network failure → throw `PricingApiError(0, "Unable to reach pricing service")`

---

## UI State Machine (per ScenarioPanel)

```
         ┌─────────────────────┐
         │       IDLE          │  result = null, error = null, loading = false
         └──────────┬──────────┘
                    │ user submits valid form
                    ▼
         ┌─────────────────────┐
         │      LOADING        │  loading = true
         └──────┬──────────────┘
                │               │
         success│               │ error
                ▼               ▼
    ┌─────────────────┐  ┌─────────────────┐
    │    SUCCESS      │  │     ERROR       │
    │ result = data   │  │ error = message │
    └────────┬────────┘  └────────┬────────┘
             │                    │
             └────────────────────┘
                      │ user submits again
                      ▼
                   LOADING
```
